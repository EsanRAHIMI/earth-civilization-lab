"""Narrow, auditable historical calibration: country-level annual log(GHG per capita)
vs log(GDP per capita) and log(energy use per capita). NOT a 1000-year climate model.
Country-blocked uncertainty and strictly later-year test; not independent-source validation.
"""
import argparse,csv,collections,json,math,pathlib,random,statistics,hashlib
FEATURES=('real_gdp_per_capita','energy_use_per_capita')
TARGET='climate_ghg_per_capita'
def solve(a,b):
 n=len(b);a=[list(map(float,row))+[float(b[i])] for i,row in enumerate(a)]
 for j in range(n):
  pivot=max(range(j,n),key=lambda i:abs(a[i][j]))
  if abs(a[pivot][j])<1e-12:raise ValueError('singular fit')
  a[j],a[pivot]=a[pivot],a[j]
  d=a[j][j]
  for k in range(j,n+1):a[j][k]/=d
  for i in range(n):
   if i!=j:
    factor=a[i][j]
    for k in range(j,n+1):a[i][k]-=factor*a[j][k]
 return [a[i][-1] for i in range(n)]
def fit(samples,penalty=1.0):
 if len(samples)<30:raise ValueError('too few training observations')
 n=3;xtx=[[0.0]*n for _ in range(n)];xty=[0.0]*n
 for x,y,_ in samples:
  for i in range(n):
   xty[i]+=x[i]*y
   for j in range(n):xtx[i][j]+=x[i]*x[j]
 for j in (1,2):xtx[j][j]+=penalty
 return solve(xtx,xty)
def score(samples,coef):
 errs=[math.exp(sum(a*b for a,b in zip(x,coef)))-math.exp(y) for x,y,_ in samples]
 truths=[math.exp(y) for _,y,_ in samples]
 return {'n':len(samples),'mae':sum(map(abs,errs))/len(errs),'rmse':math.sqrt(sum(e*e for e in errs)/len(errs)),'smape_percent':100*sum(2*abs(e)/(abs(t)+abs(t+e)+1e-12) for e,t in zip(errs,truths))/len(errs)}
def calibrate(root):
 root=pathlib.Path(root);panel=root/'data/multisector_observations.csv'
 by_key=collections.defaultdict(dict)
 with panel.open() as f:
  for r in csv.DictReader(f):
   if r['indicator'] in (*FEATURES,TARGET):
    by_key[(r['country'],int(r['year']))][r['indicator']]=float(r['value'])
 samples=[]
 for (country,year),values in sorted(by_key.items()):
  if not all(k in values and math.isfinite(values[k]) and values[k]>0 for k in (*FEATURES,TARGET)):continue
  x=(1.,math.log(values[FEATURES[0]]),math.log(values[FEATURES[1]]))
  samples.append((country,year,x,math.log(values[TARGET])))
 train=[(x,y,c) for c,yr,x,y in samples if yr<=2018]
 test=[(x,y,c) for c,yr,x,y in samples if 2019<=yr<=2023]
 if len(train)<500 or len(test)<100:raise ValueError('insufficient temporal training/test overlap')
 coef=fit(train)
 predictions=[{'country':c,'year':yr,'observed_tco2e_per_person':math.exp(y),'predicted_tco2e_per_person':math.exp(sum(a*b for a,b in zip(x,coef)))} for c,yr,x,y in samples if 2019<=yr<=2023]
 # Country-block bootstrap resamples entire country histories; deterministic seed.
 groups=collections.defaultdict(list)
 for x,y,c in train:groups[c].append((x,y,c))
 keys=sorted(groups);rng=random.Random(20261013);boot=[]
 for _ in range(200):
  drawn=[sample for c in (rng.choice(keys) for _ in keys) for sample in groups[c]]
  try:boot.append(fit(drawn))
  except ValueError:pass
 if len(boot)<180:raise ValueError('unstable bootstrap')
 ci=[[sorted(b[i] for b in boot)[int(q*(len(boot)-1))] for q in (.025,.975)] for i in range(3)]
 baseline=[(x,y,c) for x,y,c in test]
 # no-leakage baseline uses global training mean; an intentionally weak reference
 trainmean=sum(y for _,y,_ in train)/len(train)
 baseline_coef=[trainmean,0.,0.]
 report={'model':'log(GHG_CO2eq_per_capita)=intercept + beta_gdp*log(real_GDP_per_capita) + beta_energy*log(energy_use_per_capita)','scope':'associational country-year panel, no country fixed effects, not causal','training_years':[2000,2018],'test_years':[2019,2023],'n_train':len(train),'n_test':len(test),'countries_train':len(keys),'countries_test':len({c for _,_,c in test}),'coefficients':dict(zip(('intercept','log_gdp','log_energy'),coef)),'country_block_bootstrap_95pct_ci':dict(zip(('intercept','log_gdp','log_energy'),ci)),'test':score(test,coef),'train_mean_baseline_test':score(test,baseline_coef),'bootstrap_replicates':len(boot),'observations_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'independent_source_validated':False,'calibrated_for_millennium':False,'limitations':['GHG series includes multiple gases; cannot infer fossil CO2 or climate temperature directly','Historical relationships are not stable policy causal effects','Temporal holdout is same provider and revised vintage, NOT independent-source validation','Non-random country-year missingness and energy coverage limit generalizability','Bootstrap interval is for coefficients, not calibrated forecast intervals','Long-horizon use forbidden until independent data and physical constraints validated']}
 folder=root/'reports';folder.mkdir(exist_ok=True)
 (folder/'historical_calibration.json').write_text(json.dumps(report,indent=2))
 with (folder/'historical_calibration_holdout.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['country','year','observed_tco2e_per_person','predicted_tco2e_per_person']);w.writeheader();w.writerows(predictions)
 print(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();calibrate(a.root)
