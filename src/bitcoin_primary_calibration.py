"""Bitcoin as a primary measured global covariate in six annual sector backtests.
Use annual country medians and first differences, never duplicate global BTC across
countries. Compare no-BTC vs BTC, same time holdout; not causal validation.
"""
import argparse,csv,collections,datetime,json,math,pathlib,statistics,hashlib
from src.historical_calibration import solve
TARGETS={'climate':'climate_ghg_per_capita','energy':'energy_use_per_capita','water':'freshwater_withdrawals','food':'food_production_index','demography':'population','economy':'real_gdp_per_capita'}
BTC=('market_price_usd','network_hashrate','confirmed_transactions','miners_revenue_usd')
def fit(rows,features,penalty=10.):
 n=len(features)+1;a=[[0.]*n for _ in range(n)];b=[0.]*n
 for x,y in rows:
  v=[1.]+[x[k] for k in features]
  for i in range(n):
   b[i]+=v[i]*y
   for j in range(n):a[i][j]+=v[i]*v[j]
 for i in range(1,n):a[i][i]+=penalty
 return solve(a,b)
def predict(x,features,beta):return beta[0]+sum(beta[i+1]*x[k] for i,k in enumerate(features))
def run(root):
 root=pathlib.Path(root);btc=root/'data/bitcoin_observations.csv';panel=root/'data/multisector_observations.csv'
 daily=collections.defaultdict(lambda:collections.defaultdict(list))
 with btc.open() as f:
  for r in csv.DictReader(f):
   d=datetime.datetime.fromisoformat(r['timestamp_utc'].replace('Z','+00:00')).date()
   v=float(r['value'])
   if math.isfinite(v) and v>=0:daily[r['indicator']][d.year].append((d,v))
 annual={};coverage={}
 for k in BTC:
  annual[k]={};coverage[k]={}
  for year,vals in daily[k].items():
   unique={d:v for d,v in vals}
   coverage[k][year]=len(unique)
   if len(unique)>=180:
    annual[k][year]=statistics.median(unique.values())
 global_values=collections.defaultdict(lambda:collections.defaultdict(list))
 with panel.open() as f:
  for r in csv.DictReader(f):
   value=float(r['value'])
   if math.isfinite(value) and value>0:global_values[r['indicator']][int(r['year'])].append(value)
 sector_values={}
 for sector,k in TARGETS.items():
  sector_values[sector]={year:statistics.median(v) for year,v in global_values[k].items() if len(v)>=100}
 btc_changes={}
 for year in range(2011,2024):
  if all(year in annual[k] and year-1 in annual[k] and annual[k][year-1]>0 for k in BTC):
   btc_changes[year]={k:math.log1p(annual[k][year])-math.log1p(annual[k][year-1]) for k in BTC}
 results=[]
 for sector,values in TARGETS.items():
  data=sector_values[sector];rows=[]
  for year in range(2011,2024):
   if year not in btc_changes or year not in data or year-1 not in data:continue
   y=math.log(data[year]/data[year-1])
   x={k:btc_changes[year][k] for k in BTC}
   rows.append((year,x,y))
  train=[(x,y) for yr,x,y in rows if yr<=2018]
  test=[(x,y) for yr,x,y in rows if yr>=2019]
  if len(train)<6 or len(test)<3:
   results.append({'sector':sector,'status':'insufficient_common_annual_history','train':len(train),'test':len(test)});continue
  beta=fit(train,BTC)
  # Baseline predicts zero growth (persistence). Compare additional Bitcoin features.
  errors=[predict(x,BTC,beta)-y for x,y in test]
  null=[-y for x,y in test]
  def metric(err):return {'mean_absolute_log_change_error':sum(abs(e) for e in err)/len(err),'rmse_log_change':math.sqrt(sum(e*e for e in err)/len(err))}
  results.append({'sector':sector,'status':'held_out_global_annual_test','training_years':[min(y for y,x,z in rows if y<=2018),2018],'test_years':[2019,max(y for y,x,z in rows if y>=2019)],'n_train':len(train),'n_test':len(test),'bitcoin_features':list(BTC),'btc_augmented':metric(errors),'no_bitcoin_persistence':metric(null),'btc_improves_mae':metric(errors)['mean_absolute_log_change_error']<metric(null)['mean_absolute_log_change_error'],'coefficients':beta,'causal_validated':False})
 out={'scope':'Exploratory global first-difference sector medians; BTC primary candidate covariates, NOT independent causal effects','annual_bitcoin_days_by_indicator':{k:{str(y):n for y,n in sorted(coverage[k].items())} for k in BTC},'bitcoin_panel_sha256':hashlib.sha256(btc.read_bytes()).hexdigest(),'world_panel_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'relations':results,'independent_source_validated':False,'millennium_model_calibrated':False,'warnings':['Annual medians across countries are not world totals and country composition changes','Same-year Bitcoin change is contemporaneous explanatory fit, NOT an ex-ante forecast','Small annual sample with four Bitcoin features risks overfitting','Bitcoin has no meaningful observations before its creation','Network hashrate is not measured electricity or carbon emissions','Do not insert estimated coefficients into physical climate stocks or policy simulations']}
 folder=root/'reports';folder.mkdir(exist_ok=True)
 (folder/'bitcoin_primary_calibration.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({'relations':results,'warnings':out['warnings']},indent=2));return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
