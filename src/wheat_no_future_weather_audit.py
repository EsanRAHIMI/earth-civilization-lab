"""Leakage-safe country+future-year audit of observational crop coupling.

Strict availability: target y_t cannot use annual precipitation of year t
when prediction is issued at 1 January t. This audit uses *previous-year*
observed rainfall, previous-year yield, and physically comparable units.

Countries are blocked entirely out of training; year 2019+ is blocked out of
training and model selection. This is EXPLORATORY, since history is public and
country-level rainfall is not a wheat growing-area forcing. No crop physics
or GRACE terrestrial water-storage target is trained.
"""
import hashlib,json,math,pathlib,statistics
import numpy as np
from src.country_aligned_wheat_rain_benchmark import benchmark as retrospective_benchmark

TRAIN_END=2016
VALID_END=2018
TEST_START=2019
TEST_END=2023
COUNTRIES=("India","Pakistan","United States of America")

def form_rows(observed):
    rows=[]
    for country,records in observed.items():
        years={int(x["year"]):x for x in records}
        for year in range(2006,2024):
            if year not in years or year-1 not in years:continue
            previous=years[year-1];target=years[year]
            if any(key not in previous for key in ("yield_t_ha","national_precipitation_mm")):
                continue
            observed_target=float(target["yield_t_ha"])
            last_yield=float(previous["yield_t_ha"])
            rain=float(previous["national_precipitation_mm"])
            if not all(math.isfinite(v) and v>0 for v in (observed_target,last_yield,rain)):
                raise ValueError("Nonphysical crop observation")
            rows.append((country,year,last_yield,rain,observed_target))
    return rows

def fit_ridge(rows,with_rain,alpha):
    if len(rows)<8:raise ValueError("Too few physically joined calibration rows")
    rainavg=statistics.mean(row[3] for row in rows)
    rainstd=statistics.pstdev(row[3] for row in rows) or 1.
    def design(row):
        values=[1.,row[2]]
        if with_rain:values.append((row[3]-rainavg)/rainstd)
        return values
    X=np.array([design(r) for r in rows],dtype=float)
    y=np.array([r[4] for r in rows],dtype=float)
    penalty=np.eye(X.shape[1])*alpha
    penalty[0,0]=0.
    beta=np.linalg.solve(X.T@X+penalty,X.T@y)
    return lambda row:max(0.,float(np.dot(design(row),beta)))

def mae(rows,predict):
    return statistics.mean(abs(r[4]-predict(r)) for r in rows)

def study(rows):
    folds=[]
    for withheld in COUNTRIES:
        develop=[r for r in rows if r[0]!=withheld and r[1]<=TRAIN_END]
        validation=[r for r in rows if r[0]!=withheld and TRAIN_END<r[1]<=VALID_END]
        test=[r for r in rows if r[0]==withheld and TEST_START<=r[1]<=TEST_END]
        fold={"held_country":withheld,"n_train":len(develop),
              "n_val":len(validation),"n_test":len(test),
              "train_before_test":all(r[1]<TEST_START for r in develop+validation),
              "country_disjoint":all(r[0]!=withheld for r in develop+validation)}
        if min(len(develop)/12,len(validation)/3,len(test)/4)<1:
            fold.update(status="insufficient_data",accepted=False)
            folds.append(fold);continue
        candidates=[("persistence",0.,False,None)]
        for rain in (False,True):
            for alpha in (1.,10.,100.):
                candidates.append(("rain" if rain else "yield",alpha,rain,None))
        scores=[]
        for name,alpha,rain,_ in candidates:
            predictor=(lambda row:row[2]) if name=="persistence" else fit_ridge(develop,rain,alpha)
            scores.append((mae(validation,predictor),name,alpha,rain))
        best=min(scores,key=lambda x:(x[0],x[1],x[2]))
        final=(lambda row:row[2]) if best[1]=="persistence" else fit_ridge(develop+validation,best[3],best[2])
        baseline=lambda row:row[2]
        selected=mae(test,final)
        persistent=mae(test,baseline)
        fold.update({"status":"exploratory_geographic_temporal_holdout",
                    "predictor":best[1],"regularization":best[2],
                    "test_mae_t_ha":selected,"persistence_mae_t_ha":persistent,
                    "improvement_t_ha":persistent-selected,
                    "beats_persistence":selected<persistent-1e-8,
                    "accepted":False,
                    "limitations":"One held nation and five historical harvest years; not independent prospective trial"})
        folds.append(fold)
    return folds

def run(root="."):
    root=pathlib.Path(root)
    evidence_file=root/"reports/country_aligned_wheat_rain_benchmark.json"
    if not evidence_file.is_file():raise FileNotFoundError("Authoritative paired rain/yield report required")
    evidence=json.loads(evidence_file.read_text())
    # The old report intentionally contains only metadata, NOT full national
    # annual rainfall panels, so reconstruct from saved NetCDF + polygons.
    from src.country_aligned_wheat_rain_benchmark import COUNTRY_ISO,fetch_geometry,pixel_area_weights,annual_country_rainfall
    import netCDF4
    observations=json.loads((root/"reports/faostat_wheat_country_observations.json").read_text())["countries"]
    raw=root/"data/independent_raw"
    polygons,geo=fetch_geometry()
    with netCDF4.Dataset(raw/"noaa_gpcp_v23_monthly.nc") as nc:
        for country,iso in COUNTRY_ISO.items():
            annual=annual_country_rainfall(nc,pixel_area_weights(nc,polygons[iso]))
            for record in observations[country]:
                if record["year"] in annual:record["national_precipitation_mm"]=annual[record["year"]]
    rows=form_rows(observations)
    folds=study(rows)
    wins=sum(f.get("beats_persistence",False) for f in folds)
    report={"status":"exploratory_country_AND_time_disjoint_crop_audit",
            "issued_at":"January 1 of target harvest year",
            "asof_feature_rule":"rainfall(t-1) and wheat_yield(t-1) only; NEVER rainfall(t)",
            "source_products":"NOAA GPCP v2.3 + FAOSTAT wheat 15, geographic clipping to Natural Earth 110m",
            "eligible_country_years":len(rows),
            "folds":folds,"positive_skill_folds":wins,
            "eligible_for_confirmatory_release":False,
            "coupled_hydrology_crop_validation":False,
            "note":"The predictor only joins observed climate with crop statistics. GRACE storage is absent; there is no physically validated coupled system.",
            "source_report_sha256":hashlib.sha256(evidence_file.read_bytes()).hexdigest()}
    out=root/"reports";out.mkdir(exist_ok=True)
    (out/"country_wheat_no_future_weather_audit.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"eligible_rows":len(rows),
                      "folds":folds,"validated":False},indent=2))
    return report

if __name__=="__main__":run()
