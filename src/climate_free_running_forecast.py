"""True out-of-sample decadal CO2-only energy-balance hindcast (research, not forecast skill certificate).

Unlike earlier conditional hindcasts, NO measured CO2 or temperature from
2015-2024 enters model forcing, parameter fitting or forecast initialisation.
Two-layer energy balance + train-only logarithmic CO2 extrapolation, with honest
trend and persistence baselines. Missing non-CO2 forcing prevents physical
climate validation. Deterministic sensitivity is not probabilistic uncertainty.
"""
import csv
import hashlib
import json
import math
import pathlib
import statistics
from src.climate_multisource_readiness import annual_records

START, TRAIN_END, TEST_END = 1980, 2014, 2024
CO2_REFERENCE_PPM = 278.
SOLAR_FORCING_COEFFICIENT = 5.35
HEAT_CAPACITY_SURFACE = 8.0
HEAT_CAPACITY_DEEP = 100.0

def annual_co2_extrapolation(annual_co2, training_end, forecast_end):
    """Forecast future CO2 in ppm using only training-era measured concentrations."""
    years = sorted(y for y in annual_co2 if START <= y <= training_end)
    if not years or years[-1] != training_end or years != list(range(START, training_end+1)):
        raise ValueError("Missing or non-consecutive training CO2 years")
    if forecast_end < training_end:
        raise ValueError("Invalid forecast end")
    # Regress log CO2 on calendar year to preserve positivity.
    xm = statistics.mean(years)
    ys = [math.log(annual_co2[y]) for y in years]
    ym = statistics.mean(ys)
    denominator = sum((y-xm)**2 for y in years)
    slope = sum((y-xm)*(v-ym) for y,v in zip(years,ys))/denominator
    intercept = ym - slope*xm
    result = {y:annual_co2[y] for y in years}
    for y in range(training_end+1,forecast_end+1):
        result[y] = math.exp(intercept+slope*y)
    return result, {"train_only_log_co2_slope_per_year":slope,
                    "future_co2_assumption":"extrapolated from <=2014 only; not measured",
                    "extrapolated_co2_ppm_end":result[forecast_end]}

def integrate(co2, years, feedback, deep_exchange):
    """Implicit-Euler 2-layer EBM with time-invariant parameters.

    C in W*yr/(m2*K), lambda/gamma W/(m2*K), forcing W/m2.
    Annual timestep is exactly one year; CO2 series is the only forcing.
    """
    if feedback<=0 or deep_exchange<=0:
        raise ValueError("Positive physical coefficients required")
    surface=0.
    deep=0.
    series={}
    for year in years:
        forcing=SOLAR_FORCING_COEFFICIENT*math.log(co2[year]/CO2_REFERENCE_PPM)
        aa=1+(feedback+deep_exchange)/HEAT_CAPACITY_SURFACE
        bb=-deep_exchange/HEAT_CAPACITY_SURFACE
        cc=-deep_exchange/HEAT_CAPACITY_DEEP
        dd=1+deep_exchange/HEAT_CAPACITY_DEEP
        determinant=aa*dd-bb*cc
        updated_surface=(dd*(surface+forcing/HEAT_CAPACITY_SURFACE)-bb*deep)/determinant
        updated_deep=(-cc*(surface+forcing/HEAT_CAPACITY_SURFACE)+aa*deep)/determinant
        surface,deep=updated_surface,updated_deep
        series[year]=surface
    return series

def calibrate_physical(train_co2, train_temp):
    years=sorted(train_temp)
    if years!=list(range(START,TRAIN_END+1)) or any(y not in train_co2 for y in years):
        raise ValueError("Training year or forcing gaps")
    selected=None
    for feedback in (0.6, 0.9, 1.2, 1.5, 1.8, 2.2, 2.6, 3.0):
        for exchange in (0.05, 0.1, 0.2, 0.4, 0.7, 1., 1.5):
            modeled=integrate(train_co2,years,feedback,exchange)
            offset=statistics.mean(train_temp[y]-modeled[y] for y in years)
            loss=statistics.mean((train_temp[y]-modeled[y]-offset)**2 for y in years)
            candidate=(loss,feedback,exchange,offset)
            if selected is None or candidate<selected:
                selected=candidate
    return {"train_mse_c2":selected[0],"feedback_W_m2_K":selected[1],
            "deep_exchange_W_m2_K":selected[2],
            "baseline_temperature_offset_c":selected[3]}

def run(root="."):
    root=pathlib.Path(root)
    raw=root/"data/independent_raw"
    nasa=raw/"nasa_gistemp_global.csv"
    noaa=raw/"noaa_global_annual_co2.csv"
    temp=annual_records(nasa,"Year","J-D")
    co2=annual_records(noaa,"year","mean")
    years=list(range(START,TEST_END+1))
    if any(y not in temp or y not in co2 for y in years):
        raise ValueError("Missing verified NASA/NOAA observations; no imputation allowed")
    train_temp={y:temp[y] for y in years if y<=TRAIN_END}
    train_co2={y:co2[y] for y in years if y<=TRAIN_END}
    future_co2,forcing_meta=annual_co2_extrapolation(train_co2,TRAIN_END,TEST_END)
    physical=calibrate_physical(train_co2,train_temp)
    modeled=integrate(future_co2,years,physical["feedback_W_m2_K"],
                      physical["deep_exchange_W_m2_K"])
    selected={y:modeled[y]+physical["baseline_temperature_offset_c"] for y in years if y>TRAIN_END}
    historical_baseline=temp[TRAIN_END]
    train_years=list(train_temp)
    ymean=statistics.mean(train_temp.values())
    xmean=statistics.mean(train_years)
    slope=sum((y-xmean)*(train_temp[y]-ymean) for y in train_years)/sum((y-xmean)**2 for y in train_years)
    baselines={
        "frozen_2014_temperature":{y:historical_baseline for y in selected},
        "training_only_linear_trend":{y:ymean+slope*(y-xmean) for y in selected},
    }
    def measure(pred):
        errors=[pred[y]-temp[y] for y in sorted(pred)]
        return {"mae_c":statistics.mean(map(abs,errors)),
                "rmse_c":math.sqrt(statistics.mean(e*e for e in errors)),
                "bias_c":statistics.mean(errors)}
    errors={name:measure(data) for name,data in {"ebm_co2_only":selected,**baselines}.items()}
    report={
        "status":"true_free_running_out_of_sample_CO2_only_EBM_research_hindcast",
        "training_years":[START,TRAIN_END],
        "blind_forecast_years":[TRAIN_END+1,TEST_END],
        "temperature_source":"NASA GISTEMP v4, global J-D temperature anomaly",
        "co2_source":"NOAA GML global mean annual concentration",
        "n_forecast_years":len(selected),
        "future_test_year_co2_consumed_by_model":False,
        "future_test_year_temperature_consumed_by_model":False,
        "physics":{"co2_reference_ppm":CO2_REFERENCE_PPM,
            "forcing_formula":"5.35*ln(CO2/278) W/m2",
            "surface_capacity_W_year_m2_K":HEAT_CAPACITY_SURFACE,
            "deep_capacity_W_year_m2_K":HEAT_CAPACITY_DEEP,
            **physical},
        "future_co2":forcing_meta,
        "metrics":errors,
        "beats_frozen_last_observation":errors["ebm_co2_only"]["mae_c"] < errors["frozen_2014_temperature"]["mae_c"],
        "beats_training_linear_trend":errors["ebm_co2_only"]["mae_c"] < errors["training_only_linear_trend"]["mae_c"],
        "input_sha256":{"nasa":hashlib.sha256(nasa.read_bytes()).hexdigest(),
                        "noaa":hashlib.sha256(noaa.read_bytes()).hexdigest()},
        "yearly_forecasts":[{"year":year,"observed_temp_anomaly_c":temp[year],
            "ebm_forecast_c":selected[year],
            "frozen_2014_forecast_c":historical_baseline,
            "trend_forecast_c":baselines["training_only_linear_trend"][year],
            "co2_projection_ppm":future_co2[year]} for year in sorted(selected)],
        "valid_global_earth_model":False,
        "scenario_ready":False,
        "critical_limitations":[
            "Only CO2 forcing; aerosols, methane, nitrous oxide, volcanoes, solar and land feedbacks omitted",
            "Forecast future CO2 uses crude log-linear extrapolation, not carbon-cycle dynamics",
            "Even 2015-2024 historical holdout may have been inspected during wider project development",
            "Training CO2 values are historical observations; 2015-2024 CO2 and temperature never fed into predictions",
            "Single world aggregate, no regions, no 90% uncertainty intervals, fixed arbitrary heat capacities",
            "Years 2015-2024 evaluated once as a contiguous free-running 10-year trajectory, not ten independent forecasts"
        ]
    }
    folder=root/"reports"
    folder.mkdir(exist_ok=True)
    (folder/"climate_free_running_decadal_hindcast.json").write_text(json.dumps(report,indent=2))
    print(json.dumps({"status":report["status"],"metrics":errors,"future_CO2_leakage":False,
                      "beats_frozen":report["beats_frozen_last_observation"],
                      "beats_trend":report["beats_training_linear_trend"]},indent=2))
    return report

if __name__=="__main__":
    run()
