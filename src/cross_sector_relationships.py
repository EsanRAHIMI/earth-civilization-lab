"""Lagged historical tests for four sectors; not causal or millennium validation."""
import csv,json,math,pathlib,collections,argparse,hashlib
from src.historical_calibration import solve
RELATIONS={'water':('freshwater_withdrawals','population'),'food':('food_production_index','cereal_yield'),'population':('population','life_expectancy'),'economy':('real_gdp_per_capita','electricity_access')}
def run(root):
 root=pathlib.Path(root);data=collections.defaultdict(dict)
 panel=root/'data/multisector_observations.csv'
 with panel.open() as f:
  for r in csv.DictReader(f):data[(r['country'],int(r['year']))][r['indicator']]=float(r['value'])
 countries={c for c,y in data};results=[]
 for sector,(target,driver) in RELATIONS.items():
  train=[];test=[]
  for c in sorted(countries):
   for year in range(2001,2024):
    prev=data.get((c,year-1),{});cur=data.get((c,year),{})
    values=[prev.get(target),prev.get(driver),cur.get(target)]
    if any(v is None or not math.isfinite(v) or v<=0 for v in values):continue
    x=[1.,math.log(values[0]),math.log(values[1])]
    (train if year<=2018 else test).append((x,math.log(values[2]),c))
  if len(train)<100 or len(test)<30:
   results.append({'sector':sector,'status':'insufficient_data','n_train':len(train),'n_test':len(test)});continue
  a=[[0.0]*3 for _ in range(3)];b=[0.0]*3
  for x,y,c in train:
   for i in range(3):
    b[i]+=x[i]*y
    for j in range(3):a[i][j]+=x[i]*x[j]
  for i in (1,2):a[i][i]+=5.
  beta=solve(a,b)
  actual=[math.exp(y) for x,y,c in test]
  pred=[math.exp(sum(v*w for v,w in zip(x,beta))) for x,y,c in test]
  baseline=[math.exp(x[1]) for x,y,c in test]
  def score(values):
   return {'mae':sum(abs(p-y) for p,y in zip(values,actual))/len(actual),'smape_percent':100*sum(2*abs(p-y)/(p+y) for p,y in zip(values,actual))/len(actual)}
  results.append({'sector':sector,'target':target,'lagged_driver':driver,'status':'temporal_holdout','train_2001_2018':len(train),'test_2019_2023':len(test),'test_countries':len({c for x,y,c in test}),'coefficients':beta,'model':score(pred),'persistence_baseline':score(baseline),'independent_validated':False,'causal':False})
 out={'relations':results,'data_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'scope':'One-year historical association, not causal, not 1000-year validation','independent_source_validation':False}
 (root/'reports').mkdir(exist_ok=True)
 (root/'reports/cross_sector_relationships.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2));return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
