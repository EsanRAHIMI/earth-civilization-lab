"""Cross-domain scientific release verdict tied to real immutable experiment artifacts.

There is no right to certify a connected climate/water/food digital twin from
independent single-domain metrics alone. Acceptance requires evidence of actual
water-storage target plus basin budget, independent crop-yield skill across
unseen regions, compatible shared forcing, and a blind future data vintage.
"""
import datetime,hashlib,json,pathlib,statistics

REQUIRED=("hadcrut5_independent_climate_test.json",
          "climate_joint_temperature_ocean_hindcast.json",
          "country_wheat_no_future_weather_audit.json")

def evaluate(root="."):
    root=pathlib.Path(root)
    docs={}
    digests={}
    for name in REQUIRED:
        p=root/"evidence"/name
        if not p.is_file():raise FileNotFoundError("Missing primary independent test report: "+str(p))
        original=p.read_bytes()
        digests[name]=hashlib.sha256(original).hexdigest()
        docs[name]=json.loads(original)
    external=docs["hadcrut5_independent_climate_test.json"]
    joint=docs["climate_joint_temperature_ocean_hindcast.json"]
    crop=docs["country_wheat_no_future_weather_audit.json"]
    if external.get("status")!="independent_institution_HadCRUT5_source_evaluation":
        raise ValueError("Met Office evaluation provenance not verified")
    if joint.get("status")!="joint_NOAA_0_2000m_NASA_surface_training_only_hindcast":
        raise ValueError("Joint temperature/ocean experiment provenance not verified")
    if crop.get("status")!="exploratory_country_AND_time_disjoint_crop_audit":
        raise ValueError("Crop blocked evaluation provenance not verified")
    if crop.get("issued_at")!="January 1 of target harvest year":
        raise ValueError("Pre-issue crop forecast information barrier missing")
    if len(crop.get("folds",[]))<3 or not all(
        f.get("country_disjoint") and f.get("train_before_test")
        for f in crop["folds"]
    ):raise ValueError("Geographical or temporal holdout violated")
    climate=external["metrics"]
    climate_m=climate["joint_physics"]["mae_c"]
    climate_baseline=min(climate[k]["mae_c"] for k in
                         ("frozen_train_last","train_only_linear_trend"))
    temperature_skill=climate_m<climate_baseline
    crop_wins=sum(f.get("beats_persistence",False) for f in crop["folds"])
    crop_sustained=(crop_wins==len(crop["folds"]))
    grace_file=root/"evidence/nasa_grace_mascon_observation_manifest.json"
    grace_report=json.loads(grace_file.read_text()) if grace_file.exists() else None
    actual_water_calibrated=bool(grace_report and
      grace_report.get("land_water_storage_model_calibrated") is True
      and grace_report.get("spatial_leakage_correction_validated") is True
      and grace_report.get("observational_error_covariance_validated") is True)
    # Future unknown label period from an independent prospective evaluation
    # must have been verified by external audit. No such evaluation exists here.
    prospective_independent_holdout=False
    joint_energy_water_food_validation=False
    ready=(temperature_skill and crop_sustained and actual_water_calibrated and
           prospective_independent_holdout and joint_energy_water_food_validation)
    result={
     "status":"operational_release_blocked" if not ready else "eligible_for_external_review",
     "generated_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
     "evidence_sha256":digests,
     "regional_units":{"climate":"MAE Celsius 2015-2024",
                       "wheat":"MAE metric tonnes per harvested hectare 2019-2023",
                       "water":"NO credible independent basin-level TWS storage skill yet"},
     "tests":{
      "met_office_climate_beats_strongest_baseline":temperature_skill,
      "climate_MAE_C":climate_m,
      "strongest_climate_baseline_MAE_C":climate_baseline,
      "cropland_country_out_of_time_positive_folds":crop_wins,
      "cropland_country_test_fold_count":len(crop["folds"]),
      "crop_beats_baseline_in_all_geographies":crop_sustained,
      "actual_GRACE_storage_model_independently_calibrated":actual_water_calibrated,
      "unknown_future_prospective_blind_holdout_verified":prospective_independent_holdout,
      "physical_climate_water_food_coupling_validated":joint_energy_water_food_validation
     },
     "observational_research_interface_allowed":True,
     "scientific_scenario_forecast_enabled":False,
     "operational_global_decisions_authorized":False,
     "accepted_physical_global_digital_twin":False,
     "critical_note":"Three observation sources are not a calibrated coupled dynamical model; observational and causal validation are separate.",
     "sources_not_prospective":"All historical evaluation intervals have been examined during previous research; only a genuinely new frozen future data vintage can be confirmatory."
    }
    output=root/"reports";output.mkdir(parents=True,exist_ok=True)
    (output/"coupled_operational_verdict.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({"status":result["status"],"tests":result["tests"],
                      "scenario_enabled":False},indent=2))
    return result

if __name__=="__main__":evaluate()
