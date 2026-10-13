"""Auditable World Bank historical panel, zero fabricated observations. Stdlib only."""
import argparse,csv,datetime,hashlib,json,math,pathlib,statistics,urllib.request
INDICATORS={'population':('SP.POP.TOTL','people'),'life_expectancy':('SP.DYN.LE00.IN','years'),'gdp_growth':('NY.GDP.MKTP.KD.ZG','percent_per_year'),'co2_per_capita':('EN.GHG.CO2.PC.CE.AR5','tonnes_per_person')}
COUNTRIES=['USA','CHN','IND','BRA','ZAF','DEU','JPN','NGA','IDN','ARE']
YEARS=(2000,2024)
def fetch(url):
 req=urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/0.7 research reproducibility'})
 with urllib.request.urlopen(req,timeout=30) as r:return r.read()
def acquire(root,fetcher=fetch):
 root=pathlib.Path(root);raw=root/'data'/'raw';raw.mkdir(parents=True,exist_ok=True)
 entries=[];records=[]
 for name,(code,unit) in INDICATORS.items():
  url=f'https://api.worldbank.org/v2/country/{";".join(COUNTRIES)}/indicator/{code}?format=json&date={YEARS[0]}:{YEARS[1]}&per_page=20000'
  body=fetcher(url);data=json.loads(body)
  if not isinstance(data,list) or len(data)!=2 or not isinstance(data[1],list):raise ValueError('Invalid World Bank response')
  if int(data[0].get('pages',1))!=1:raise ValueError('Incomplete pagination')
  p=raw/(name+'.json');p.write_bytes(body)
  entries.append({'indicator':name,'source_indicator':code,'url':url,'sha256':hashlib.sha256(body).hexdigest(),'bytes':len(body),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
  for item in data[1]:
   v=item.get('value');iso=item.get('countryiso3code');yr=item.get('date')
   if v is None or iso not in COUNTRIES or not str(yr).isdigit():continue
   if not math.isfinite(float(v)):raise ValueError('Nonfinite observation')
   records.append({'iso3':iso,'year':int(yr),'indicator':name,'value':float(v),'unit':unit,'source_code':code,'obs_status':item.get('obs_status') or ''})
 panel=root/'data'/'observations.csv'
 with panel.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['iso3','year','indicator','value','unit','source_code','obs_status']);w.writeheader();w.writerows(sorted(records,key=lambda r:(r['iso3'],r['indicator'],r['year'])))
 manifest={'schema':'earthlab-v7','sources':entries,'panel_sha256':hashlib.sha256(panel.read_bytes()).hexdigest(),'rows':len(records),'no_imputation':True,'training_cutoff':2015,'holdout_start':2016,'holdout_end':2024}
 (root/'data'/'manifest.json').write_text(json.dumps(manifest,indent=2));return manifest
def evaluate(root):
 root=pathlib.Path(root);p=root/'data'/'observations.csv';manifest=json.loads((root/'data'/'manifest.json').read_text())
 if hashlib.sha256(p.read_bytes()).hexdigest()!=manifest['panel_sha256']:raise ValueError('Panel hash mismatch')
 by={}
 with p.open() as f:
  for r in csv.DictReader(f):
   key=(r['iso3'],r['indicator']);by.setdefault(key,{})[int(r['year'])]=float(r['value'])
 output=[]
 for (country,indicator),series in sorted(by.items()):
  train={y:v for y,v in series.items() if y<=2015};test={y:v for y,v in series.items() if 2016<=y<=2024}
  if len(train)<8 or len(test)<3:continue
  last=train[max(train)];errors=[last-v for y,v in sorted(test.items())]
  output.append({'iso3':country,'indicator':indicator,'n_train':len(train),'n_holdout':len(test),'mae':statistics.mean(map(abs,errors)),'rmse':math.sqrt(statistics.mean(e*e for e in errors)),'unit':INDICATORS[indicator][1]})
 report={'status':'baseline_only_not_civilization_model','method':'frozen_2015_last_observation','holdout':'2016-2024','groups':output,'groups_evaluated':len(output),'scientific_ready':False}
 (root/'reports').mkdir(exist_ok=True);(root/'reports'/'historical_baseline.json').write_text(json.dumps(report,indent=2));return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('command',choices=['fetch','evaluate']);p.add_argument('--root',default='.');a=p.parse_args();print(json.dumps(acquire(a.root) if a.command=='fetch' else evaluate(a.root),indent=2))
