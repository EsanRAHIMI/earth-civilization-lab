"""Met Office HadCRUT5 v5.2 independent source-temperature evaluation.

No HadCRUT data may enter fitting, forecast forcing, or climate parameter
selection. A constant dataset-anomaly-reference offset is estimated ONLY
on 1980-2014 NASA/HadCRUT overlap. This is external observational
cross-check, NOT fully independent observations (shared SST sources).
"""
import csv,datetime,hashlib,io,json,math,pathlib,statistics,urllib.request
from src.climate_multisource_readiness import annual_records
SOURCE="https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.2.0.0/analysis/diagnostics/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv"
START=1980;TRAIN_END=2014;TEST_END=2024

def decode(body):
 lines=body.decode("utf-8-sig").splitlines()
 rows=list(csv.reader(line for line in lines if line.strip() and not line.lstrip().startswith("#")))
 if len(rows)<45:raise ValueError("HadCRUT5 global annual CSV is missing")
 header=rows[0]
 if len(header)<2 or not any("anomal" in str(x).lower() for x in header):
  raise ValueError("HadCRUT5 temperature anomaly column is not verified")
 values={}
 for row in rows[1:]:
  if not row:continue
  try:year=int(float(row[0]));value=float(row[1])
  except (ValueError,TypeError,IndexError):continue
  if year not in range(START,TEST_END+1):continue
  if not math.isfinite(value) or not -4<value<6:
   raise ValueError("Invalid Met Office HadCRUT5 temperature anomaly")
  if year in values:raise ValueError("Repeated HadCRUT5 annual observation")
  values[year]=value
 if len(values)!=45 or set(values)!=set(range(START,TEST_END+1)):
  raise ValueError("HadCRUT5 annual series 1980-2024 incomplete")
 return values,header

def run(root="."):
 root=pathlib.Path(root)
 with urllib.request.urlopen(urllib.request.Request(SOURCE,headers={
  "User-Agent":"EarthCivilizationLab independent scientific evaluation"}),timeout=75) as response:
  raw=response.read()
 if len(raw)<1000:raise ValueError("HadCRUT5 response unexpectedly short")
 independent,header=decode(raw)
 folder=root/"data/independent_raw";folder.mkdir(parents=True,exist_ok=True)
 (folder/"hadcrut5_global_annual_v5200.csv").write_bytes(raw)
 nasa=annual_records(folder/"nasa_gistemp_global.csv","Year","J-D")
 model_json=root/"reports/climate_joint_temperature_ocean_hindcast.json"
 if not model_json.is_file():raise FileNotFoundError("Joint NASA and NOAA model result unavailable")
 experiment=json.loads(model_json.read_text())
 if experiment.get("forecast_period")!=[2015,2024]:
  raise ValueError("Different independently simulated decade than HadCRUT5 evaluation")
 # Baseline reference difference is calculated only on the fixed training era.
 calibration_years=list(range(START,TRAIN_END+1))
 offset=statistics.mean(independent[y]-nasa[y] for y in calibration_years)
 predicted={r["year"]:r["predicted_temperature_c"]+offset for r in experiment["series"]}
 same_years=list(range(TRAIN_END+1,TEST_END+1))
 if set(predicted)!=set(same_years):raise ValueError("Model prediction years are inconsistent")
 mean_x=statistics.mean(calibration_years);mean_n=statistics.mean(nasa[y] for y in calibration_years)
 slope=sum((y-mean_x)*(nasa[y]-mean_n) for y in calibration_years)/sum(
  (y-mean_x)**2 for y in calibration_years)
 train_trend={y:mean_n+slope*(y-mean_x)+offset for y in same_years}
 freeze={y:nasa[TRAIN_END]+offset for y in same_years}
 def score(p):
  residual=[p[y]-independent[y] for y in same_years]
  return {"mae_c":statistics.mean(abs(e) for e in residual),
          "bias_c":statistics.mean(residual),
          "rmse_c":math.sqrt(statistics.mean(e*e for e in residual))}
 results={"joint_physics":score(predicted),
          "frozen_train_last":score(freeze),
          "train_only_linear_trend":score(train_trend)}
 report={"status":"independent_institution_HadCRUT5_source_evaluation",
  "source":SOURCE,"version":"HadCRUT.5.2.0.0",
  "sha256":hashlib.sha256(raw).hexdigest(),
  "retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "raw_csv_columns":header,
  "dataset_anomaly_baseline":"HadCRUT5 1961–1990, NASA GISTEMP 1951–1980",
  "reference_offset_hadcrut_minus_nasa_training_only_c":offset,
  "evaluation_years":[2015,2024],
  "holdout_hadcrut_in_model_fit":False,
  "fit_uses_future_HadCRUT":False,
  "all_predictions_unchanged_by_new_temperature_truth":True,
  "metrics":results,
  "beats_both_baselines":all(results["joint_physics"]["mae_c"]<results[key]["mae_c"]
                             for key in ("frozen_train_last","train_only_linear_trend")),
  "independent_measurement_assumption_verified":False,
  "validation_accepted":False,"scenario_ready":False,
  "limitations":["Met Office and NASA products share some underlying sea temperature observations",
   "2026 HadCRUT5 and 2025 revised forcing are not actual source vintages frozen at 2014",
   "Cross-source comparison is retrospective after NASA outcome was studied",
   "HadCRUT5 anomaly-offset is train-only, but method does not establish unbiased physics",
   "A decade-long outcome is one temporal test trajectory; no multi-region external skill"]}
 out=root/"reports";out.mkdir(exist_ok=True)
 (out/"hadcrut5_independent_climate_test.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"status":report["status"],"mae":results,
                   "beats_both_baselines":report["beats_both_baselines"]},indent=2))
 return report
if __name__=="__main__":run()
