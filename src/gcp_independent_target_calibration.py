"""Independent-target fossil CO2 calibration using GCP observations.
GDP and energy covariates are World Bank; target is GCP, not WB total GHG.
Temporal holdout 2019-2023; source lineage remains partly shared.
"""
import csv,json,math,pathlib,collections,argparse,statistics,hashlib
from src.historical_calibration import fit,score
def run(root):
 root=pathlib.Path(root)
 target=root/'data/independent_raw/gcp_fossil_co2_per_capita_2025.csv'
 if not target.exists():raise FileNotFoundError('GCP target missing; validation blocked')
 y={}
 with target.open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   c=r['ISO 3166-1 alpha-3'].strip().upper()
   try:year=int(r['Year']);v=float(r['Total'])
   except (TypeError,ValueError):continue
   if len(c)==3 and c.isalpha() and 2000<=year<=2023 and math.isfinite(v) and v>0:y[(c,year)]=v
 cov=collections.defaultdict(dict)
 with (root/'data/multisector_observations.csv').open() as f:
  for r in csv.DictReader(f):
   if r['indicator'] in ('real_gdp_per_capita','energy_use_per_capita'):
    cov[(r['country'].upper(),int(r['year']))][r['indicator']]=float(r['value'])
 train=[];test=[]
 for (c,year),v in sorted(y.items()):
  x=cov.get((c,year),{})
  if any(k not in x or not math.isfinite(x[k]) or x[k]<=0 for k in ('real_gdp_per_capita','energy_use_per_capita')):continue
  row=((1.,math.log(x['real_gdp_per_capita']),math.log(x['energy_use_per_capita'])),math.log(v),c)
  (train if year<=2018 else test).append(row)
 if len(train)<500 or len(test)<100 or len({c for _,_,c in test})<30:raise ValueError('Independent target overlap insufficient')
 coef=fit(train)
 mean=sum(y for x,y,c in train)/len(train)
 result={'status':'independent_provider_target_historical_holdout_completed','target':'GCP fossil CO2 per capita (tCO2/person), NOT total GHG CO2e','features':'World Bank GDP per capita and energy use per capita','train_years':[2000,2018],'test_years':[2019,2023],'n_train':len(train),'n_test':len(test),'test_countries':len({c for x,y,c in test}),'coefficients':dict(zip(('intercept','log_gdp','log_energy'),coef)),'holdout_model':score(test,coef),'training_mean_baseline':score(test,[mean,0,0]),'independent_target_source':'Global Carbon Project 2025 fossil CO2','gcp_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'independent_provider_target':True,'upstream_independence_verified':False,'causal_validation':False,'physical_climate_model_validated':False,'bitcoin_effect_validated':False,'limitations':['Separate fossil CO2 target recalibrated: coefficients cannot be substituted into World Bank total GHG model','Features are from World Bank and source upstream dependencies not fully audited','Temporal holdout is retrospective and uses latest revised data','No country fixed effects or physical climate temperature validation','Baseline is training mean, not a strong autoregressive benchmark']}
 folder=root/'reports';folder.mkdir(exist_ok=True)
 (folder/'gcp_independent_target_calibration.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
