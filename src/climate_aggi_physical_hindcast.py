"""NOAA AGGI all-long-lived-GHG forcing driven EBM, full decadal hindcast.

This reduces the deliberate CO2-only omission in the preceding EBM, but NO
test-era AGGI/NASA values are consumed by fitting or forecast integrations.
IMPORTANT: AGGI is not net anthropogenic forcing: aerosols, solar and volcanic
perturbations are absent. Not a validated climate model.
"""
import csv
import hashlib
import io
import json
import math
import pathlib
import statistics
import urllib.request
from src.climate_free_running_forecast import (
    START, TRAIN_END, TEST_END, HEAT_CAPACITY_SURFACE, HEAT_CAPACITY_DEEP
)
from src.climate_multisource_readiness import annual_records

SOURCE="https://gml.noaa.gov/aggi/AGGI_Table.csv"

def parse_noaa_aggi(raw):
    """NOAA published AGGI table: 8th column is total GHG ERF in W/m2.

    Do not blindly infer columns: the 2014 and 2024 reference values must
    match NASA/NOAA published fixed-known quality control checks.
    """
    lines=io.StringIO(raw.decode("utf-8-sig"))
    annual={}
    for row in csv.reader(lines):
        if not row:
            continue
        first=row[0].strip().strip('"')
        if not(first.isdigit() and len(first)==4):
            continue
        year=int(first)
        if not 1979<=year<=2100:
            continue
        if len(row)<10:
            raise ValueError("NOAA AGGI data record missing forcing columns")
        # NOAA table: Year, CO2, CH4, N2O, CFC*, HCFC, HFC*, Total, CO2eq, AGGI, %.
        try:
            components=[float(row[i]) for i in range(1,8)]
        except ValueError as e:
            raise ValueError("NOAA AGGI numeric record corrupt") from e
        if any(not math.isfinite(x) or x<0 for x in components):
            raise ValueError("Unphysical AGGI forcing")
        if abs(sum(components[:6])-components[6])>.025:
            raise ValueError("AGGI total does not reconcile forcing components")
        if year in annual:
            raise ValueError("Repeated NOAA AGGI year")
        annual[year]=components[6]
    if not all(y in annual for y in range(START, TEST_END+1)):
        raise ValueError("NOAA AGGI annual period incomplete; no imputation")
    if abs(annual[2014]-3.110)>.04 or abs(annual[2024]-3.539)>.04:
        raise ValueError("NOAA AGGI forcing differs from cited 2024 table; review product vintage")
    return annual

def download(root,fetcher=None):
    root=pathlib.Path(root)
    if fetcher is None:
        def fetcher(url):
            req=urllib.request.Request(url,headers={"User-Agent":"EarthCivilizationLab/1.0 research-data"})
            with urllib.request.urlopen(req,timeout=90) as response:return response.read()
    raw=fetcher(SOURCE)
    forcing=parse_noaa_aggi(raw)
    folder=root/"data/independent_raw"
    folder.mkdir(parents=True,exist_ok=True)
    (folder/"noaa_aggi_annual_ghg_forcing.csv").write_bytes(raw)
    return forcing,hashlib.sha256(raw).hexdigest()

def extrapolate_forcing(train,forecast_end):
    years=list(range(START,TRAIN_END+1))
    if sorted(train)!=years:
        raise ValueError("Train forcing must cover 1980-2014 exactly")
    xbar=statistics.mean(years)
    ybar=statistics.mean(train[y] for y in years)
    slope=sum((y-xbar)*(train[y]-ybar) for y in years)/sum((y-xbar)**2 for y in years)
    result=dict(train)
    for year in range(TRAIN_END+1,forecast_end+1):
        result[year]=max(0.,ybar+slope*(year-xbar))
    return result,{"training_linear_forcing_slope_wm2_per_year":slope,
                    "future_forcing":"training-only linear extrapolation; not measured greenhouse gases"}

def integrate_forcing(forcing,years,feedback,exchange):
    if not (math.isfinite(feedback) and math.isfinite(exchange) and feedback>0 and exchange>0):
        raise ValueError("Unphysical EBM feedback/transport")
    surf=deep=0.
    model={}
    for year in years:
        aa=1+(feedback+exchange)/HEAT_CAPACITY_SURFACE
        bb=-exchange/HEAT_CAPACITY_SURFACE
        cc=-exchange/HEAT_CAPACITY_DEEP
        dd=1+exchange/HEAT_CAPACITY_DEEP
        determinant=aa*dd-bb*cc
        next_s=(dd*(surf+forcing[year]/HEAT_CAPACITY_SURFACE)-bb*deep)/determinant
        next_d=(-cc*(surf+forcing[year]/HEAT_CAPACITY_SURFACE)+aa*deep)/determinant
        surf,deep=next_s,next_d
        model[year]=surf
    return model

def fit(train_forcing,train_temp):
    years=list(range(START,TRAIN_END+1))
    best=None
    for feedback in (.6,.9,1.2,1.5,1.8,2.2,2.6,3.):
        for exchange in (.05,.1,.2,.4,.7,1.,1.5):
            computed=integrate_forcing(train_forcing,years,feedback,exchange)
            offset=statistics.mean(train_temp[y]-computed[y] for y in years)
            loss=statistics.mean((train_temp[y]-computed[y]-offset)**2 for y in years)
            candidate=(loss,feedback,exchange,offset)
            if best is None or candidate<best:best=candidate
    return best

def run(root="."):
    root=pathlib.Path(root)
    source,source_sha=download(root)
    nasa_path=root/"data/independent_raw/nasa_gistemp_global.csv"
    observed=annual_records(nasa_path,"Year","J-D")
    years=list(range(START,TEST_END+1))
    if any(y not in observed for y in years):
        raise ValueError("NASA annual temperatures missing")
    # Explicit slicing ensures future gas observations are unavailable to the integrator.
    historical={y:source[y] for y in range(START,TRAIN_END+1)}
    projection,meta=extrapolate_forcing(historical,TEST_END)
    calibration=fit(historical,observed)
    _,feedback,exchange,offset=calibration
    integrated=integrate_forcing(projection,years,feedback,exchange)
    future={y:integrated[y]+offset for y in range(TRAIN_END+1,TEST_END+1)}
    train_years=list(range(START,TRAIN_END+1))
    mean_y=statistics.mean(observed[y] for y in train_years)
    mean_x=statistics.mean(train_years)
    slope=sum((y-mean_x)*(observed[y]-mean_y) for y in train_years)/sum((y-mean_x)**2 for y in train_years)
    baseline_constant={y:observed[TRAIN_END] for y in future}
    baseline_trend={y:mean_y+slope*(y-mean_x) for y in future}
    def metrics(p):
        diffs=[p[y]-observed[y] for y in sorted(p)]
        return {"mae_c":statistics.mean(abs(e) for e in diffs),
                "rmse_c":math.sqrt(statistics.mean(e*e for e in diffs)),
                "bias_c":statistics.mean(diffs)}
    performance={"aggi_all_long_lived_ghg_ebm":metrics(future),
                 "frozen_last_observation":metrics(baseline_constant),
                 "training_linear_trend":metrics(baseline_trend)}
    report={"status":"free_running_2015_2024_noaa_aggi_ebm_hindcast",
        "forcing":"NOAA AGGI total long-lived greenhouse gas effective radiative forcing vs preindustrial (W/m2)",
        "forcing_source_url":SOURCE,
        "forcing_sha256":source_sha,
        "nasa_temperature_sha256":hashlib.sha256(nasa_path.read_bytes()).hexdigest(),
        "training_years":[START,TRAIN_END],"holdout_years":[TRAIN_END+1,TEST_END],
        "forecast_uses_future_measured_greenhouse_gas_forcing":False,
        "forecast_uses_future_measured_temperature":False,
        "forecast_forcing_generated_by_train_only_trend":True,
        "calibration":{"train_mse_c2":calibration[0],"feedback_W_m2_K":feedback,
                       "deep_exchange_W_m2_K":exchange,
                       "NASA_training_temperature_offset_c":offset,
                       "heat_capacity_surface_W_year_m2_K":HEAT_CAPACITY_SURFACE,
                       "heat_capacity_deep_W_year_m2_K":HEAT_CAPACITY_DEEP},
        "future_forcing":meta,"metrics":performance,
        "improves_over_frozen":performance["aggi_all_long_lived_ghg_ebm"]["mae_c"]<performance["frozen_last_observation"]["mae_c"],
        "improves_over_training_trend":performance["aggi_all_long_lived_ghg_ebm"]["mae_c"]<performance["training_linear_trend"]["mae_c"],
        "yearly_forecasts":[{"year":y,"predicted_temp_c":future[y],"observed_temp_c":observed[y],
                              "projected_aggi_wm2":projection[y]} for y in sorted(future)],
        "validation_accepted":False,"scenario_ready":False,
        "limitations":[
         "NOAA AGGI includes long-lived greenhouse gases only; no aerosols, land-use, solar or volcanic forcing",
         "A revised 2024 NOAA AGGI vintage has been used for historical training; no time-stamped 2014 frozen source release",
         "Future forcing projected from historical trend; this is not carbon-chemistry or emissions scenario dynamics",
         "Fit and selection confined to <=2014 but historical holdout was seen in earlier experiments",
         "Heat capacities are assumed, and ocean heat has not been jointly calibrated",
         "World aggregate only; cannot validate basin food or regional climate decisions"] }
    folder=root/"reports";folder.mkdir(exist_ok=True)
    (folder/"climate_aggi_decadal_hindcast.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"metrics":performance,"forcing_sha256":source_sha,
                      "validation_accepted":False},indent=2))
    return report

if __name__=="__main__":run()
