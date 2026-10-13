"""Observed global carbon response: GCP fossil CO2 emissions -> NOAA global CO2.
One-box mass-accounting approximation; land-use emissions are omitted.
Annual out-of-sample hindcast and residual bootstrap predictive coverage.
NOT a calibrated Earth-system or 1000-year forecast.
"""
import argparse,csv,hashlib,io,json,math,pathlib,random,statistics,urllib.request
NOAA_URL='https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv'
PPM_GTC=2.12
def noaa(root):
 folder=root/'data/independent_raw';folder.mkdir(parents=True,exist_ok=True)
 req=urllib.request.Request(NOAA_URL,headers={'User-Agent':'EarthCivilizationLab/1.0 academic research'})
 with urllib.request.urlopen(req,timeout=90) as f:body=f.read()
 (folder/'noaa_global_annual_co2.csv').write_bytes(body)
 result={}
 for r in csv.DictReader(x for x in body.decode('utf-8-sig').splitlines() if x.strip() and not x.lstrip().startswith('#')):
  try:yr=int(r['year']);v=float(r['mean'])
  except (KeyError,ValueError):continue
  if 250<v<600:result[yr]=v
 if len(result)<35:raise ValueError('NOAA global annual CO2 coverage too short')
 return result,hashlib.sha256(body).hexdigest()
def gcp(root):
 path=root/'data/independent_raw/gcp_fossil_co2_national_2025.csv'
 if not path.is_file():raise FileNotFoundError('GCP inventory missing')
 rows={}
 with path.open(encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   if r['Country'].strip().lower() not in ('global','world'):continue
   try:yr=int(r['Year']);v=float(r['Total'])
   except (ValueError,TypeError):continue
   if v>0:rows[yr]=v*1e-3*(12/44) # MtCO2 -> GtC
 if len(rows)<35:raise ValueError('GCP global total row absent or insufficient; cannot substitute sum of countries')
 return rows,hashlib.sha256(path.read_bytes()).hexdigest()
def fit(rows):
 # dC (ppm) = alpha * fossil emissions (GtC)/2.12 - k*(Cprev-278)
 # Bounds are structural constraints, not identification of natural fluxes.
 best=None
 for ia in range(0,201):
  alpha=ia/100
  for ik in range(0,101):
   k=ik/2000
   err=sum((d-alpha*e+k*x)**2 for e,x,d in rows)
   if best is None or err<best[0]:best=(err,alpha,k)
 return best[1:]
def predict(row,a,k):
 e,x,d=row
 return a*e-k*x
def run(root):
 root=pathlib.Path(root);observed,noaa_sha=noaa(root);emissions,gcp_sha=gcp(root)
 rows={}
 for year in sorted(set(observed)&set(emissions)):
  if year-1 not in observed:continue
  rows[year]=(emissions[year]/PPM_GTC,observed[year-1]-278,observed[year]-observed[year-1])
 train=[rows[y] for y in rows if 1980<=y<=2014]
 test=[(y,rows[y]) for y in rows if 2015<=y<=2024]
 if len(train)<25 or len(test)<8:raise ValueError('Insufficient NOAA/GCP training or holdout overlap')
 alpha,k=fit(train)
 residuals=[r[2]-predict(r,alpha,k) for r in train]
 actual=[r[2] for _,r in test];pred=[predict(r,alpha,k) for _,r in test]
 # Benchmark: constant average growth learned exclusively on training years.
 base=statistics.mean(r[2] for r in train)
 mae=lambda p:statistics.mean(abs(y-z) for y,z in zip(actual,p))
 rng=random.Random(20261013);intervals=[]
 for p in pred:
  draws=sorted(p+rng.choice(residuals) for _ in range(1000))
  intervals.append((draws[24],draws[974]))
 coverage=statistics.mean(lo<=v<=hi for v,(lo,hi) in zip(actual,intervals))
 # Bootstrap whole training years to represent coefficient sampling variability.
 params=[]
 for i in range(40):
  sample=[rng.choice(train) for _ in train]
  params.append(fit(sample))
 summary={'status':'observational_one_box_carbon_hindcast_completed','model':'delta_CO2_ppm=alpha*fossil_emissions_GtC/2.12-k*(previous_CO2_ppm-278)','training_years':[1980,2014],'holdout_years':[2015,2024],'n_train':len(train),'n_holdout':len(test),'alpha_fitted':alpha,'sink_rate_per_year_fitted':k,'holdout_mae_ppm_per_year':mae(pred),'training_mean_growth_baseline_mae_ppm_per_year':mae([base]*len(test)),'residual_bootstrap_nominal_95pct_coverage':coverage,'residual_bootstrap_95pct_mean_width_ppm_per_year':statistics.mean(hi-lo for lo,hi in intervals),'bootstrap_alpha_95pct_range':[sorted(x[0] for x in params)[0],sorted(x[0] for x in params)[-1]],'bootstrap_sink_rate_range':[min(x[1] for x in params),max(x[1] for x in params)],'noaa_url':NOAA_URL,'noaa_sha256':noaa_sha,'gcp_sha256':gcp_sha,'units':'CO2 concentration ppm; fossil emissions GtC/year','upstream_source_independence':'NOAA direct atmospheric observations; GCP fossil emissions inventory','physical_mass_balance_scope':'atmosphere versus aggregate inferred sink; missing land-use flux','forecast_horizon_validated_years':1,'thousand_year_forecast_validated':False,'temperature_validated':False,'probabilistic_interval_calibrated':False,'limitations':['One-box effective sink not resolved into ocean/land carbon pools','Land-use change and other carbon sources are omitted; alpha absorbs confounding','Residual bootstrap assumes exchangeable annual errors and ignores structural uncertainty','Holdout emissions are observed ex post, not forecasts; this is a conditional hindcast','Grid-fit and bootstrap uncertainty are approximate; no paleoclimate or temperature validation']}
 folder=root/'reports';folder.mkdir(exist_ok=True)
 (folder/'noaa_gcp_carbon_hindcast.json').write_text(json.dumps(summary,indent=2))
 with (folder/'noaa_gcp_carbon_hindcast_rows.csv').open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['year','observed_co2_change_ppm','model_co2_change_ppm','baseline_co2_change_ppm','lower_95_ppm','upper_95_ppm'])
  for (year,_),y,p,(lo,hi) in zip(test,actual,pred,intervals):w.writerow([year,y,p,base,lo,hi])
 print(json.dumps(summary,indent=2));return summary
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
