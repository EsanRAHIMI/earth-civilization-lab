"""IPCC-aligned all-forcing research hindcast from frozen ClimateIndicator/IGCC 2024 data.

Uses historical net anthropogenic forcing (including aerosol), solar and
volcanic forcing to fit a two-layer EBM, then projects ONLY train-era
components for 2015-2024. Observed post-2014 forcing is for evaluation
documentation only; never a model input. No claim of skill/causality.
"""
import csv,datetime,hashlib,io,json,math,pathlib,statistics,urllib.request
from src.climate_aggi_physical_hindcast import integrate_forcing,fit
from src.climate_multisource_readiness import annual_records
from src.climate_free_running_forecast import START,TRAIN_END,TEST_END
URL="https://raw.githubusercontent.com/ClimateIndicator/data/v2025.06.11/data/effective_radiative_forcing/ERF_best_aggregates_1750-2024.csv"
PAPER_DOI="10.5194/essd-17-2641-2025"
DATA_DOI="10.5281/zenodo.15639576"

def decode_igcc(body):
 records={}
 rows=csv.DictReader(io.StringIO(body.decode("utf-8-sig")))
 required={"timebound_lower","timebound_upper","anthro","solar","volcanic","total","aerosol"}
 if not rows.fieldnames or not required.issubset(rows.fieldnames):
  raise ValueError("IGCC forcing header schema changed; manual review required")
 for item in rows:
  year=int(item["timebound_lower"])
  if float(item["timebound_upper"])!=year+1:
   raise ValueError("Non-annual IGCC forcing row")
  pieces={name:float(item[name]) for name in ("anthro","solar","volcanic","total","aerosol")}
  if not all(math.isfinite(v) for v in pieces.values()):
   raise ValueError("Nonfinite forcing")
  if abs(sum(pieces[k] for k in ("anthro","solar","volcanic"))-pieces["total"])>1e-5:
   raise ValueError("Net forcing does not reconcile anthropogenic + solar + volcanic")
  if year in records:raise ValueError("Duplicate IGCC forcing year")
  records[year]=pieces
 if not all(y in records for y in range(START,TEST_END+1)):
  raise ValueError("Missing annual forcing in historical benchmark")
 if not -3<records[2014]["aerosol"]<0:
  raise ValueError("IGCC aerosol forcing sign/units implausible")
 return records

def projected_components(train, end_year):
 years=list(range(START,TRAIN_END+1))
 if sorted(train)!=years:
  raise ValueError("Training forcing incomplete: only <=2014 may be used")
 xm=statistics.mean(years)
 anthro=[train[y]["anthro"] for y in years]
 ym=statistics.mean(anthro)
 slope=sum((y-xm)*(v-ym) for y,v in zip(years,anthro))/sum((y-xm)**2 for y in years)
 solar=statistics.mean(train[y]["solar"] for y in years)
 volcanic=statistics.mean(train[y]["volcanic"] for y in years)
 future={y:train[y]["total"] for y in years}
 for year in range(TRAIN_END+1,end_year+1):
  anthropogenic=ym+slope*(year-xm)
  future[year]=anthropogenic+solar+volcanic
 return future,{"anthropogenic_linear_slope_W_m2_year":slope,
                "solar_training_climatology_W_m2":solar,
                "volcanic_training_climatology_W_m2":volcanic,
                "extrapolation":"future anthro linear; solar+volcanic fixed train climatology; no measured test forcing"}

def run(root=".", fetcher=None):
 root=pathlib.Path(root)
 if fetcher is None:
  def fetcher(url):
   req=urllib.request.Request(url,headers={"User-Agent":"EarthCivilizationLab scientific benchmark"})
   with urllib.request.urlopen(req,timeout=90) as resp:return resp.read()
 body=fetcher(URL)
 if not isinstance(body,bytes) or len(body)<1000:raise ValueError("Missing real IGCC forcing bytes")
 observed_forcing=decode_igcc(body)
 raw=root/"data/independent_raw"
 raw.mkdir(parents=True,exist_ok=True)
 (raw/"igcc_2024_annual_erf_best.csv").write_bytes(body)
 temp_file=raw/"nasa_gistemp_global.csv"
 nasa=annual_records(temp_file,"Year","J-D")
 if any(y not in nasa for y in range(START,TEST_END+1)):
  raise ValueError("NASA temperature series incomplete")
 train={y:observed_forcing[y] for y in range(START,TRAIN_END+1)}
 full_forcing,projection_meta=projected_components(train,TEST_END)
 training_temp={y:nasa[y] for y in range(START,TRAIN_END+1)}
 loss,feedback,exchange,offset=fit({y:train[y]["total"] for y in train},training_temp)
 integration=integrate_forcing(full_forcing,list(range(START,TEST_END+1)),feedback,exchange)
 forecast={y:integration[y]+offset for y in range(TRAIN_END+1,TEST_END+1)}
 train_years=list(range(START,TRAIN_END+1))
 mean_x=statistics.mean(train_years)
 mean_y=statistics.mean(training_temp.values())
 trend=sum((y-mean_x)*(nasa[y]-mean_y) for y in train_years)/sum((y-mean_x)**2 for y in train_years)
 frozen={y:nasa[TRAIN_END] for y in forecast}
 linear={y:mean_y+trend*(y-mean_x) for y in forecast}
 def metric(pred):
  residual=[pred[y]-nasa[y] for y in sorted(pred)]
  return {"mae_c":statistics.mean(abs(e) for e in residual),
          "rmse_c":math.sqrt(statistics.mean(e*e for e in residual)),
          "bias_c":statistics.mean(residual)}
 metrics={"igcc_all_forcing_ebm":metric(forecast),
          "constant_2014":metric(frozen),"training_only_linear_trend":metric(linear)}
 report={
  "status":"frozen_2014_IGCC_all_forcing_free_running_hindcast",
  "source_tag":"v2025.06.11","source_url":URL,"paper_doi":PAPER_DOI,"dataset_doi":DATA_DOI,
  "source_sha256":hashlib.sha256(body).hexdigest(),
  "nasa_source_sha256":hashlib.sha256(temp_file.read_bytes()).hexdigest(),
  "retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "training_years":[START,TRAIN_END],"forecast_test_years":[TRAIN_END+1,TEST_END],
  "future_observed_forcing_used_in_prediction":False,
  "future_observed_temperature_used_in_prediction":False,
  "training_only_forcing_projection":projection_meta,
  "calibration":{"feedback_W_m2_K":feedback,"exchange_W_m2_K":exchange,
                 "temperature_offset_c":offset,"train_mse_c2":loss},
  "metrics":metrics,"improves_over_both_baselines":all(
    metrics["igcc_all_forcing_ebm"]["mae_c"]<metrics[s]["mae_c"]
    for s in ("constant_2014","training_only_linear_trend")),
  "yearly_predictions":[{"year":y,"forecast_c":forecast[y],
       "observed_c":nasa[y],"projected_forcing_W_m2":full_forcing[y]} for y in sorted(forecast)],
  "validation_accepted":False,"scenario_ready":False,
  "limitations":[
   "IGCC historical forcing published in 2025: revised training forcing was unavailable as frozen 2014 vintage",
   "Aerosol best estimates depend on models and uncertain historical evidence; not direct measurements",
   "The projected solar and volcanic forcings are climatology assumptions, not event forecasts",
   "Linear anthropogenic forcing projection does not model future emissions or land-energy feedbacks",
   "Previous researchers have inspected the 2015-2024 history: model comparisons remain exploratory",
   "Fixed heat capacities and only two fitted coefficients; no joint ocean-heat hindcast acceptance",
   "No independent regional validation, no predictive intervals, no long-horizon reliability"
  ]
 }
 folder=root/"reports";folder.mkdir(exist_ok=True)
 (folder/"climate_igcc_full_forcing_hindcast.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"metrics":metrics,"improves_over_both_baselines":report["improves_over_both_baselines"],
                   "future_forcing_leakage":False},indent=2))
 return report
if __name__=="__main__":run()
