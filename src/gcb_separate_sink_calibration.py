"""Source-audited ocean and land sink calibration using GCB 2025 annual fluxes.
GCB land sink is model-derived, not an independent direct measurement.
Holdout 2015-2024; model is a simple effective-flux emulator.
"""
import csv,io,json,math,pathlib,re,urllib.request,hashlib,statistics,html
BASE='https://openclimatedata.net/emissions/global-carbon-budget/2025/global-budget/'
def get(url):
 req=urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0'})
 with urllib.request.urlopen(req,timeout=90) as f:return f.read()
def load(kind,root):
 url=BASE+kind
 page=get(url).decode('utf-8')
 links=re.findall(r'href=["\\\']([^"\\\']+\\.csv(?:\\?[^"\\\']*)?)["\\\']',page)
 matches=[html.unescape(x) for x in links if 'global-carbon-budget-2025-'+kind+'-gcb.csv' in x]
 if len(matches)!=1:raise ValueError('Cannot unambiguously find GCB '+kind+' CSV: '+repr(matches))
 from urllib.parse import urljoin
 csvurl=urljoin(url,matches[0]);body=get(csvurl)
 path=root/'data/independent_raw'/('gcb2025_'+kind+'.csv');path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(body)
 rows=list(csv.reader(io.StringIO(body.decode('utf-8-sig'))))
 header=next((i for i,row in enumerate(rows) if any(x.strip().lower()=='year' for x in row)),None)
 if header is None:raise ValueError('Missing year column '+kind)
 cols=[x.strip().lower() for x in rows[header]]
 ycol=cols.index('year');vcols=[i for i,x in enumerate(cols) if x=='gcb']
 if len(vcols)!=1:raise ValueError('Expected one GCB sink column '+repr(cols))
 values={}
 for row in rows[header+1:]:
  try:y=int(row[ycol]);v=float(row[vcols[0]])
  except (ValueError,IndexError):continue
  if math.isfinite(v):values[y]=v
 if len(values)<40:raise ValueError('Insufficient historical GCB sink years '+kind)
 return values,{'source':csvurl,'sha256':hashlib.sha256(body).hexdigest(),'years':len(values)}
def fit(obs,train):
 # Flux = intercept + slope*(CO2 ppm - 280), regularized slope by bounded grid.
 # Separately estimated coefficients, not mechanistic deep ocean or soil turnover.
 best=None
 for slope_i in range(-100,301):
  slope=slope_i/10000
  intercept=statistics.mean(obs[y]-slope*(train[y]-280) for y in obs)
  error=sum((obs[y]-intercept-slope*(train[y]-280))**2 for y in obs)
  if best is None or error<best[0]:best=(error,intercept,slope)
 return best[1:]
def run(root='.'):
 root=pathlib.Path(root);o,osrc=load('ocean-sink',root);l,lsrc=load('terrestrial-sink',root)
 noaa=root/'data/independent_raw/noaa_global_annual_co2.csv'
 if not noaa.exists():raise FileNotFoundError('NOAA annual observations absent')
 co2={}
 for r in csv.DictReader(x for x in noaa.read_text().splitlines() if x.strip() and not x.lstrip().startswith('#')):
  try:y=int(r['year']);v=float(r['mean'])
  except (KeyError,ValueError):continue
  if 250<v<600:co2[y]=v
 train={y:co2[y] for y in range(1980,2015) if y in co2 and y in o and y in l}
 test={y:co2[y] for y in range(2015,2025) if y in co2 and y in o and y in l}
 if len(train)<30 or len(test)<8:raise ValueError('Insufficient matched flux/CO2 data')
 result={}
 for name,flux in [('ocean',o),('land',l)]:
  train_flux={y:flux[y] for y in train};a,b=fit(train_flux,train)
  predicted=[a+b*(test[y]-280) for y in test];observed=[flux[y] for y in test]
  baseline=statistics.mean(train_flux.values())
  result[name]={'intercept_gtc_per_year':a,'slope_gtc_per_year_per_ppm':b,'holdout_mae_gtc_per_year':statistics.mean(abs(x-z) for x,z in zip(observed,predicted)),'baseline_mae_gtc_per_year':statistics.mean(abs(x-baseline) for x in observed),'n_train':len(train),'n_test':len(test)}
 report={'status':'separate_effective_sink_flux_calibration_completed','calibration':result,'sources':{'ocean':osrc,'land':lsrc,'co2':'NOAA GML'},'observational_independence':'GCB ocean combines models and observation-based products; GCB land sink is model-derived; both are from same GCB synthesis','deep_ocean_exchange_identified':False,'vegetation_soil_turnover_identified':False,'multibox_parameters_calibrated':False,'millennial_probabilities_calibrated':False,'warning':'Historical effective net sink responses only; neither deep-ocean nor vegetation/soil physical parameters have been independently identified.'}
 dest=root/'reports';dest.mkdir(exist_ok=True);(dest/'gcb_separate_sink_calibration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
