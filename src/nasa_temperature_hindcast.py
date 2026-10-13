"""Independent temperature observation hindcast for the CO2-driven two-layer
climate response. Observed forcing from NOAA CO2; observed temperature from
NASA GISTEMP annual global anomalies. Conditional hindcast, not a forecast.
"""
import csv,io,json,pathlib,urllib.request,math,hashlib,statistics
from src.multibox_climate import State,Parameters,step
NASA='https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
def download(url):
 req=urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0'})
 with urllib.request.urlopen(req,timeout=90) as r:return r.read()
def observations(root):
 path=root/'data/independent_raw/noaa_global_annual_co2.csv'
 if not path.exists():raise FileNotFoundError('NOAA input missing')
 co2={}
 for r in csv.DictReader(x for x in path.read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')):
  try:y=int(r['year']);v=float(r['mean'])
  except (ValueError,KeyError):continue
  if 250<v<600:co2[y]=v
 raw=download(NASA);(root/'data/independent_raw/nasa_gistemp_global.csv').write_bytes(raw)
 lines=raw.decode('utf-8-sig').splitlines()
 header=next(i for i,line in enumerate(lines) if line.startswith('Year,'))
 temps={}
 for r in csv.DictReader(lines[header:]):
  try:y=int(r['Year']);v=float(r['J-D'])
  except (ValueError,TypeError,KeyError):continue
  if -3<v<5:temps[y]=v
 if len(temps)<80:raise ValueError('NASA annual temperature data insufficient')
 return co2,temps,hashlib.sha256(raw).hexdigest()
def integrate(co2,years,feedback,exchange):
 # Hold measured CO2 forcing as external input: isolates thermal response.
 p=Parameters(feedback=feedback,heat_exchange=exchange)
 t1=0.;t2=0.;pred={}
 for y in years:
  if y not in co2:continue
  forcing=5.35*math.log(co2[y]/co2[years[0]])
  a=1+(p.feedback+p.heat_exchange)/p.heat_surface
  b=-p.heat_exchange/p.heat_surface
  c=-p.heat_exchange/p.heat_deep
  d=1+p.heat_exchange/p.heat_deep
  det=a*d-b*c
  n1=(d*(t1+forcing/p.heat_surface)-b*t2)/det
  n2=(-c*(t1+forcing/p.heat_surface)+a*t2)/det
  t1,t2=n1,n2;pred[y]=t1
 return pred
def run(root):
 root=pathlib.Path(root);co2,temp,sha=observations(root)
 years=list(range(1980,2025))
 if any(y not in co2 or y not in temp for y in years):raise ValueError('Missing NOAA/NASA annual overlap')
 # NASA GISTEMP anomalies referenced to 1951-1980; anchor with TRAINING ONLY.
 train=[y for y in years if y<=2014];test=[y for y in years if y>=2015]
 best=None
 for f in [i/20 for i in range(10,61)]:
  for h in [i/20 for i in range(2,41)]:
   pred=integrate(co2,years,f,h)
   offset=statistics.mean(temp[y]-pred[y] for y in train)
   err=statistics.mean((pred[y]+offset-temp[y])**2 for y in train)
   if best is None or err<best[0]:best=(err,f,h,offset)
 _,feedback,exchange,offset=best
 pred=integrate(co2,years,feedback,exchange)
 baseline=statistics.mean(temp[y] for y in train)
 model_mae=statistics.mean(abs(pred[y]+offset-temp[y]) for y in test)
 baseline_mae=statistics.mean(abs(baseline-temp[y]) for y in test)
 result={'status':'independent_nasa_temperature_conditional_hindcast','temperature_provider':'NASA GISTEMP v4','co2_provider':'NOAA GML','training_years':[1980,2014],'holdout_years':[2015,2024],'n_train':len(train),'n_holdout':len(test),'feedback_w_m2_k':feedback,'heat_exchange_w_m2_k':exchange,'train_only_temperature_offset_c':offset,'holdout_mae_c':model_mae,'training_mean_baseline_mae_c':baseline_mae,'nasa_sha256':sha,'observed_future_co2_used_in_holdout':True,'nonco2_forcing_included':False,'full_multibox_climate_validated':False,'thousand_year_forecast_validated':False,'limitations':['Temperature anomalies are NASA 1951-1980 reference; offset learned on training only','Observed holdout CO2 is supplied: conditional response test, not a true forward forecast','Non-CO2 greenhouse gases, aerosols, volcanic and solar forcing omitted','Two heat parameters and constant offset only; no independent ocean heat validation']}
 out=root/'reports';out.mkdir(exist_ok=True)
 (out/'nasa_temperature_hindcast.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':run('.')
