"""Train-only model selection for global terrestrial net carbon sink.

Compares physically motivated observed covariates to historical-mean baseline,
with 2008-2014 inner validation and untouched 2015-2024 outer holdout.
An empirical emulator, not identification of vegetation/soil turnover.
"""
import json,pathlib,statistics,math
from src.gcb_separate_sink_calibration import load
from src.nasa_temperature_hindcast import observations
from src.joint_sink_drivers import read_precip,ridge
def run(root='.'):
 root=pathlib.Path(root)
 co2,temp,_=observations(root)
 rain=read_precip(root/'data/independent_raw/global_land_precipitation_annual.csv')
 land,source=load('terrestrial-sink',root)
 landuse,_=load('land-use-change-emissions',root)
 data={'co2':co2,'temperature':temp,'precipitation':rain,'landuse':landuse}
 years=[y for y in range(1980,2025) if all(y in d for d in [land,*data.values()])]
 fit=[y for y in years if y<=2007];val=[y for y in years if 2008<=y<=2014];train=[y for y in years if y<=2014];hold=[y for y in years if 2015<=y<=2024]
 if min(len(fit),len(val),len(hold))<6:raise ValueError('Insufficient chronological train, validation or holdout observations')
 designs=[('co2',),('co2','temperature'),('co2','precipitation'),('co2','temperature','precipitation'),('co2','temperature','precipitation','landuse'),('temperature','precipitation'),('precipitation','landuse')]
 candidates=[]
 for names in designs:
  def feat(y):return [data[n][y] for n in names]
  for penalty in (0.5,5.0,50.0,500.0):
   try:fn,_=ridge([feat(y) for y in fit],[land[y] for y in fit],penalty)
   except ValueError:continue
   validation=statistics.mean(abs(fn(feat(y))-land[y]) for y in val)
   candidates.append((validation,names,penalty))
 if not candidates:raise ValueError('No valid empirical land model')
 candidates.sort(key=lambda x:(x[0],len(x[1]),x[2]))
 validation,names,penalty=candidates[0]
 def feat(y):return [data[n][y] for n in names]
 fn,params=ridge([feat(y) for y in train],[land[y] for y in train],penalty)
 mean=statistics.mean(land[y] for y in train)
 predictions={str(y):fn(feat(y)) for y in hold}
 model_mae=statistics.mean(abs(predictions[str(y)]-land[y]) for y in hold)
 baseline_mae=statistics.mean(abs(mean-land[y]) for y in hold)
 report={'status':'empirical_land_sink_nested_holdout_evaluated','model_type':'ridge_regression_observed_drivers','train_selection_years':[min(fit),max(fit)],'validation_years':[min(val),max(val)],'refit_years':[min(train),max(train)],'untouched_holdout_years':[min(hold),max(hold)],'selected_features':names,'ridge_penalty':penalty,'inner_validation_mae_gtc_per_year':validation,'outer_holdout_mae_gtc_per_year':model_mae,'training_mean_baseline_mae_gtc_per_year':baseline_mae,'beats_baseline':model_mae<baseline_mae,'candidate_count':len(candidates),'holdout_predictions_gtc_per_year':predictions,'parameters':params,'source':source,'physical_reservoir_calibration_complete':False,'cautions':['Observed CO2 and climate covariates are supplied at holdout time; not free-running forecasts','GCB land sink is a budget synthesis and not direct independent stock measurement','Inner validation selection does not remove all statistical uncertainty','Global precipitation series must be audited for land-only spatial coverage']}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'terrestrial_sink_nested_validation.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
