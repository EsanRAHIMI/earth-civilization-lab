"""Joint global surface temperature and NOAA 0–2000 m ocean-heat benchmark.

Research-grade *diagnostic*, not full Earth-system calibration. NASA surface
temperature and NOAA 0–2000m OHC have distinct physical support. Model heat
storage is converted to an *effective ocean-equivalent* anomaly with one
train-only inferred scale, explicitly showing the identifiability limitation.

Training ends 2014; 2015–2024 NOAA/NASA outcomes never enter fitting, forcing
projection or model state. Uses existing pinned IGCC v2025.06.11 forcing. Post-
2014 retrospective source revision means this is NOT a prospective blind test.
"""
import csv,hashlib,json,math,pathlib,statistics
from src.climate_igcc_full_forcing import decode_igcc,projected_components
from src.climate_multisource_readiness import annual_records

TRAIN_END=2014
TEST_END=2024
START=1980
OCEAN_AREA_M2=3.61e14
JOULES_PER_WATT_YEAR=365.25*86400
ZJ_CONVERSION=OCEAN_AREA_M2*JOULES_PER_WATT_YEAR/1e21

def measured_ohc(path):
    result={}
    with pathlib.Path(path).open(newline="") as handle:
        reader=csv.DictReader(handle)
        fields={"year","heat_0_2000_zj","heat_0_2000_se_zj"}
        if not reader.fieldnames or not fields.issubset(reader.fieldnames):
            raise ValueError("Ocean heat input columns/units not recognized")
        for row in reader:
            year=int(row["year"])
            level=float(row["heat_0_2000_zj"])
            sigma=float(row["heat_0_2000_se_zj"])
            if year in result or not math.isfinite(level) or not math.isfinite(sigma) or sigma<=0:
                raise ValueError("Duplicate/nonphysical ocean heat value")
            result[year]=(level,sigma)
    if not set(range(2005,2025)).issubset(result):
        raise ValueError("Missing NOAA OHC annual holdout or training measurements")
    return result

def two_layer(forcing, years, feedback, exchange, cap_s=8., cap_d=100.):
    if min(feedback,exchange,cap_s,cap_d)<=0:
        raise ValueError("Nonpositive physical parameters")
    surface=deep=0.
    state={}
    for year in years:
        if year not in forcing or not math.isfinite(forcing[year]):
            raise ValueError("Missing finite annual net forcing")
        aa=1+(feedback+exchange)/cap_s
        bb=-exchange/cap_s
        cc=-exchange/cap_d
        dd=1+exchange/cap_d
        det=aa*dd-bb*cc
        surface,deep=(
            (dd*(surface+forcing[year]/cap_s)-bb*deep)/det,
            (-cc*(surface+forcing[year]/cap_s)+aa*deep)/det
        )
        state[year]=(surface,deep)
    return state

def heat_equivalent_zj(state,baseline_year,year,cap_s,cap_d):
    """Full model heat change expressed as ocean-area-equivalent ZJ.

    NOT automatically the measured 0-2000m ocean inventory. Ocean fraction
    and depth support are unknown and must be stated.
    """
    surf,deep=state[year]
    s0,d0=state[baseline_year]
    return ZJ_CONVERSION*(cap_s*(surf-s0)+cap_d*(deep-d0))

def score(pred, truth, years):
    differences=[pred[y]-truth[y] for y in years]
    return {"n":len(differences),
            "mae":statistics.mean(abs(x) for x in differences),
            "rmse":math.sqrt(statistics.mean(x*x for x in differences)),
            "bias":statistics.mean(differences)}

def run(root="."):
    root=pathlib.Path(root)
    raw=root/"data/independent_raw"
    forcing_file=raw/"igcc_2024_annual_erf_best.csv"
    nasa_file=raw/"nasa_gistemp_global.csv"
    ocean_file=raw/"ocean_heat_content_annual.csv"
    for path in (forcing_file,nasa_file,ocean_file):
        if not path.is_file():raise FileNotFoundError(str(path))
    true_forcing=decode_igcc(forcing_file.read_bytes())
    nasa=annual_records(nasa_file,"Year","J-D")
    ohc=measured_ohc(ocean_file)
    years=list(range(START,TEST_END+1))
    if any(year not in nasa for year in years):
        raise ValueError("NASA global annual temperature incomplete")
    # Strict train-only forcing: NO future observed forcing can enter prediction.
    forcing,forcing_projection=projected_components(
        {y:true_forcing[y] for y in range(START,TRAIN_END+1)},TEST_END)
    train_years=list(range(START,TRAIN_END+1))
    ohc_train=list(range(2005,TRAIN_END+1))
    temp_variance=statistics.pvariance([nasa[y] for y in train_years])
    ohc_variance=statistics.pvariance([ohc[y][0]-ohc[2005][0] for y in ohc_train])
    if min(temp_variance,ohc_variance)<=0:raise ValueError("Training targets have zero variation")
    # Coarse, intentionally bounded parameter study. Fraction represents an
    # unidentifiable effective 0–2000m contribution of total EBM heat.
    candidate_best=None
    for lam in (.6,.9,1.2,1.5,1.8,2.2,2.6,3.):
        for gamma in (.05,.1,.2,.4,.7,1.,1.5):
            for cap_d in (50.,100.,180.):
                state=two_layer(forcing,years,lam,gamma,8.,cap_d)
                offset=statistics.mean(nasa[y]-state[y][0] for y in train_years)
                temperature_mse=statistics.mean((state[y][0]+offset-nasa[y])**2
                                                for y in train_years)
                q={y:heat_equivalent_zj(state,2005,y,8.,cap_d) for y in ohc_train}
                observed_delta={y:ohc[y][0]-ohc[2005][0] for y in ohc_train}
                # Train a bounded, nonnegative effective 0–2000m scaling
                # using OHC observations through 2014, with NO test-year OHC.
                denominator=sum(q[y]**2 for y in ohc_train)
                if denominator<=1e-12:continue
                factor=max(0.,min(1.,sum(q[y]*observed_delta[y]
                                           for y in ohc_train)/denominator))
                ohc_mse=statistics.mean((factor*q[y]-observed_delta[y])**2
                                        for y in ohc_train)
                objective=.5*temperature_mse/temp_variance+.5*ohc_mse/ohc_variance
                candidate=(objective,lam,gamma,cap_d,factor,offset,
                           temperature_mse,ohc_mse)
                if candidate_best is None or candidate<candidate_best:
                    candidate_best=candidate
    if candidate_best is None:raise RuntimeError("No feasible joint model candidate")
    _,lam,gamma,cap_d,factor,offset,t_train_loss,h_train_loss=candidate_best
    state=two_layer(forcing,years,lam,gamma,8.,cap_d)
    test=list(range(2015,TEST_END+1))
    pred_t={y:state[y][0]+offset for y in test}
    pred_h={y:ohc[2005][0]+factor*heat_equivalent_zj(state,2005,y,8.,cap_d) for y in test}
    # True frozen, no 2015-24 observations in either baseline.
    baseline_t={y:nasa[TRAIN_END] for y in test}
    baseline_h={y:ohc[TRAIN_END][0] for y in test}
    avg_year=statistics.mean(train_years)
    mean_t=statistics.mean(nasa[y] for y in train_years)
    t_slope=sum((y-avg_year)*(nasa[y]-mean_t) for y in train_years)/sum(
        (y-avg_year)**2 for y in train_years)
    avg_ohc_year=statistics.mean(ohc_train)
    mean_h=statistics.mean(ohc[y][0] for y in ohc_train)
    h_slope=sum((y-avg_ohc_year)*(ohc[y][0]-mean_h) for y in ohc_train)/sum(
        (y-avg_ohc_year)**2 for y in ohc_train)
    trend_t={y:mean_t+t_slope*(y-avg_year) for y in test}
    trend_h={y:mean_h+h_slope*(y-avg_ohc_year) for y in test}
    actual_t={y:nasa[y] for y in test}
    actual_h={y:ohc[y][0] for y in test}
    temperature={
        "joint_physics":score(pred_t,actual_t,test),
        "frozen_2014":score(baseline_t,actual_t,test),
        "train_only_trend":score(trend_t,actual_t,test)}
    ocean={
        "joint_physics":score(pred_h,actual_h,test),
        "frozen_2014":score(baseline_h,actual_h,test),
        "train_only_trend":score(trend_h,actual_h,test)}
    accept=(temperature["joint_physics"]["mae"]<min(
            temperature["frozen_2014"]["mae"],temperature["train_only_trend"]["mae"])
            and ocean["joint_physics"]["mae"]<min(
            ocean["frozen_2014"]["mae"],ocean["train_only_trend"]["mae"]))
    # Even a favorable post-hoc result is not prospective acceptance.
    report={
        "status":"joint_NOAA_0_2000m_NASA_surface_training_only_hindcast",
        "forecast_period":[2015,2024],"training_end_year":TRAIN_END,
        "training_temperature_years":[1980,2014],
        "training_ocean_heat_years":[2005,2014],
        "future_temperature_used_in_fit":False,"future_ocean_heat_used_in_fit":False,
        "future_IGCC_forcing_used_in_fit_or_forecast":False,
        "forcing_projection":forcing_projection,
        "model_parameters":{"feedback_W_m2_K":lam,"exchange_W_m2_K":gamma,
            "surface_capacity_W_year_m2_K":8.,"deep_capacity_W_year_m2_K":cap_d,
            "ocean_effective_fraction_of_model_storage":factor,
            "temperature_anomaly_offset_c":offset,
            "ocean_area_assumption_m2":OCEAN_AREA_M2,
            "storage_depth_supported_m":2000},
        "training_losses":{"temperature_mse_c2":t_train_loss,
                           "ocean_mse_zj2":h_train_loss,
                           "normalized_joint_score":candidate_best[0]},
        "holdout_temperature_c":temperature,"holdout_ocean_heat_zj":ocean,
        "beats_both_baselines_in_both":accept,
        "source_sha256":{"IGCC":hashlib.sha256(forcing_file.read_bytes()).hexdigest(),
            "NASA":hashlib.sha256(nasa_file.read_bytes()).hexdigest(),
            "NOAA_OHC_annual":hashlib.sha256(ocean_file.read_bytes()).hexdigest()},
        "series":[{"year":y,"NASA_temperature_c":nasa[y],
                   "predicted_temperature_c":pred_t[y],
                   "NOAA_OHC_0_2000m_zj":ohc[y][0],
                   "predicted_ocean_heat_zj":pred_h[y]} for y in test],
        "confirmatory_validation_accepted":False,
        "operational_or_long_range_use_authorized":False,
        "limits":[
            "Physical EBM heat capacity covers an effective reservoir, not only the observed 0-2000m water column",
            "Effective ocean fraction fitted from ten NOAA annual values; cannot identify vertical uptake physics",
            "NOAA 0-2000m anomalies are not full-depth ocean heat or independent energy-budget closure",
            "NOAA published snapshot fallback possible; inspect provenance report",
            "The forcing archive was revised after 2014; strict as-of-2014 prospective hindcast is impossible",
            "No independent region-level skill, external peer replication or distributional uncertainty",
            "Historical test decades are visible during ongoing model development",
            "Free-running future forcing uses a historical trend, not credible future emissions"
        ]
    }
    out=root/"reports";out.mkdir(exist_ok=True)
    (out/"climate_joint_temperature_ocean_hindcast.json").write_text(
        json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"temperature":temperature,
                      "ocean_heat":ocean,"accepted":False},indent=2))
    return report

if __name__=="__main__":run()
