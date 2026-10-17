"""Publish one inspectable and fail-closed scientific dashboard evidence index.

Pipeline success, observation freshness, model skill and scenario clearance are
separate facts. Missing report means UNAVAILABLE; it never becomes PASS.
"""
import datetime,hashlib,json,pathlib
REPORTS={
 "world_bank":{"file":"data-lineage.json","kind":"historical_country_statistics"},
 "climate":{"file":"climate-external.json","kind":"historical_external_temperature_validation"},
 "ocean":{"file":"climate-ocean.json","kind":"historical_thermal_state_research"},
 "satellite_rain":{"file":"gpcp-rainfall.json","kind":"historical_noaa_satellite_gauge"},
 "agriculture":{"file":"faostat-wheat.json","kind":"historical_fao_wheat_statistics"},
 "crop_hindcast":{"file":"wheat-issue-audit.json","kind":"retrospective_preissue_country_holdout"},
 "joint_verdict":{"file":"coupled-verdict.json","kind":"scientific_release_decision"},
 "grace":{"file":"nasa-grace.json","kind":"protected_terrestrial_storage_observation"},
}
PIPELINES=("six_sector","climate_physics","spatial_crop","coupled_review","grace")
def compose(folder):
 folder=pathlib.Path(folder)
 runs=json.loads((folder/"pipeline-runs.json").read_text())
 models={}
 for key,spec in REPORTS.items():
  path=folder/spec["file"]
  if not path.is_file():
   models[key]={"state":"UNAVAILABLE","kind":spec["kind"],"reason":"No successfully published and versioned authoritative artifact"}
   continue
  raw=path.read_bytes();value=json.loads(raw)
  if not isinstance(value,dict) or "status" not in value:
   raise ValueError("Malformed evidence artifact: "+spec["file"])
  models[key]={"state":"RESEARCH_ONLY","kind":spec["kind"],
              "status":value["status"],"file":spec["file"],
              "bytes":len(raw),"sha256":hashlib.sha256(raw).hexdigest(),
              "scientific_model_accepted":False}
 operational=models.get("joint_verdict")
 if operational["state"]=="RESEARCH_ONLY":
  verdict=json.loads((folder/"coupled-verdict.json").read_text())
  if verdict.get("scientific_scenario_forecast_enabled") is not False or verdict.get("operational_global_decisions_authorized") is not False:
   raise RuntimeError("Unreviewed scientific scenario gate: deny deployment")
 for k in PIPELINES:
  if k not in runs:raise ValueError("Missing live pipeline classification: "+k)
  run=runs[k]
  if not isinstance(run,dict) or not all(field in run for field in ("status","conclusion","updated_at","html_url")):
   raise ValueError("Incomplete GitHub pipeline metadata: "+k)
 result={
  "schema_version":"2.0.0",
  "generated_at_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "source":"GitHub Actions run metadata and exact archived JSON evidence, not live Earth states",
  "metadata_refresh_policy":"snapshot updated by Pages deployments; live workflow requests are a separate GitHub API status check",
  "evidence":models,
  "pipelines":runs,
  "live_earth_feeds":"USGS/EONET/Open-Meteo only; fetch times shown separately",
  "historical_data_are_live":False,
  "independent_climate_physics_accepted":False,
  "calibrated_GRACE_basin_physics_accepted":False,
  "independent_crop_physics_accepted":False,
  "joint_future_skill_validated":False,
  "global_operational_ready":False,
  "forecast_scenarios_authorized":False,
  "readiness":"OBSERVATORY_AND_RESEARCH_ONLY"
 }
 (folder/"evidence-index.json").write_text(json.dumps(result,indent=2))
 print(json.dumps({"readiness":result["readiness"],
                   "reports":{k:v["state"] for k,v in models.items()},
                   "pipelines":{k:v["conclusion"] for k,v in runs.items()}},indent=2))
 return result
if __name__=="__main__":
 import sys
 compose(sys.argv[1] if len(sys.argv)>1 else "web/model")
