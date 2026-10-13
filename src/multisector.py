"""Observed multi-sector World Bank data, with explicit missingness and no imputation.
Independent-source validation and causal calibration are NOT performed here.
"""
import argparse,csv,datetime,hashlib,json,math,pathlib,urllib.request,urllib.error,collections,time,random,socket
COUNTRIES=None  # Determined at runtime from World Bank country metadata; excludes aggregate groups.
INDICATORS={
 'climate_ghg_per_capita':('EN.GHG.CO2.PC.CE.AR5','tCO2e_per_person','climate'),
 'energy_use_per_capita':('EG.USE.PCAP.KG.OE','kg_oil_equivalent_per_person','energy'),
 'electricity_access':('EG.ELC.ACCS.ZS','percent_population','energy'),
 'freshwater_withdrawals':('ER.H2O.FWTL.ZS','percent_internal_freshwater_resources','water'),
 'food_production_index':('AG.PRD.FOOD.XD','index_2014_2016_100','food'),
 'cereal_yield':('AG.YLD.CREL.KG','kg_per_hectare','food'),
 'population':('SP.POP.TOTL','people','demography'),
 'life_expectancy':('SP.DYN.LE00.IN','years','demography'),
 'real_gdp_per_capita':('NY.GDP.PCAP.KD','constant_2015_usd','economy'),
 'gdp_growth':('NY.GDP.MKTP.KD.ZG','percent_per_year','economy'),
}
def request(url):
 # Retry transient World Bank API throttling, server errors and socket read timeouts.
 # Permanent 4xx errors are surfaced immediately; no fabricated fallback.
 for attempt in range(5):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0 evidence research','Accept':'application/json'}),timeout=60) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (408,429,500,502,503,504) or attempt==4:raise
  except (TimeoutError,socket.timeout,urllib.error.URLError,ConnectionError):
   if attempt==4:raise
  time.sleep(min(2**attempt,12)+random.uniform(0,0.5))
 raise RuntimeError('unreachable')
def collect(root,fetcher=request,years=(2000,2023)):
 root=pathlib.Path(root);raw=root/'data'/'multisector_raw';raw.mkdir(parents=True,exist_ok=True)
 observations=[];sources=[];quality=[]
 country_url='https://api.worldbank.org/v2/country?format=json&per_page=500'
 country_body=fetcher(country_url)
 country_response=json.loads(country_body)
 if not isinstance(country_response,list) or len(country_response)!=2 or not isinstance(country_response[1],list):raise ValueError('Country metadata unavailable')
 if int(country_response[0].get('pages',1))!=1:raise ValueError('Country metadata pagination incomplete')
 countries={x['id']:x for x in country_response[1] if x.get('region',{}).get('id')!='NA' and len(x.get('id',''))==3 and x.get('iso2Code') and x.get('iso2Code')!='NA'}
 if len(countries)<180:raise ValueError('Country universe suspiciously small: '+str(len(countries)))
 country_codes=set(countries)
 (raw/'country_metadata.json').write_bytes(country_body)
 sources.append({'indicator':'country_metadata','url':country_url,'sha256':hashlib.sha256(country_body).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'entities':len(countries)})
 for name,(code,unit,sector) in INDICATORS.items():
  url=f'https://api.worldbank.org/v2/country/all/indicator/{code}?format=json&date={years[0]}:{years[1]}&per_page=20000'
  body=fetcher(url);parsed=json.loads(body)
  if not isinstance(parsed,list) or len(parsed)!=2 or not isinstance(parsed[0],dict):raise ValueError('World Bank response invalid: '+code+' '+str(parsed)[:400])
  if not isinstance(parsed[1],list):
   # WB returns [metadata, null] for indicators with zero records; preserve missingness, do not invent data.
   if parsed[1] is None and int(parsed[0].get('total',0))==0:parsed[1]=[]
   else:raise ValueError('World Bank observations unavailable: '+code+' '+str(parsed)[:400])
  if int(parsed[0].get('pages',1))!=1:raise ValueError('World Bank pagination incomplete: '+code+'; increase per_page or implement pagination')
  (raw/(name+'.json')).write_bytes(body)
  count=0;seen=set()
  for item in parsed[1]:
   iso=item.get('countryiso3code');yr=item.get('date');v=item.get('value')
   if iso not in country_codes or not str(yr).isdigit() or not years[0]<=int(yr)<=years[1] or v is None:continue
   value=float(v)
   if not math.isfinite(value):raise ValueError('Nonfinite value '+name)
   key=(iso,int(yr),name)
   if key in seen:raise ValueError('Duplicate observation '+str(key))
   seen.add(key);count+=1
   observations.append({'country':iso,'year':int(yr),'indicator':name,'sector':sector,'value':value,'unit':unit,'source_code':code})
  sources.append({'indicator':name,'source_code':code,'url':url,'sha256':hashlib.sha256(body).hexdigest(),'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'observations':count})
  quality.append({'indicator':name,'sector':sector,'observed':count,'possible':len(countries)*(years[1]-years[0]+1),'coverage_fraction':count/(len(COUNTRIES)*(years[1]-years[0]+1)),'countries_with_data':len({x['country'] for x in observations if x['indicator']==name})})
 out=root/'data'/'multisector_observations.csv'
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['country','year','indicator','sector','value','unit','source_code']);w.writeheader();w.writerows(sorted(observations,key=lambda x:(x['indicator'],x['country'],x['year'])))
 manifest={'status':'observed_only_no_imputation','source':'World Bank API v2','independent_source_validation':False,'calibrated_coupled_model':False,'retrieval_years':years,'countries':sorted(countries),'country_universe_count':len(countries),'country_universe_definition':'World Bank country metadata excluding aggregates; includes some territories and economies, not identical to UN sovereign state membership','total_observations':len(observations),'sources':sources,'quality':quality,'panel_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'limitations':['Missingness may be highly non-random','World Bank indicators may have differing revisions and definitions','Water and energy series may end before 2023','Not independent climate, energy, water or food source verification','No causal policy model or uncertainty quantification']}
 country_index=root/'data'/'multisector_countries.csv'
 with country_index.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['iso3','name','region','income_level']);w.writeheader()
  for iso,x in sorted(countries.items()):
   w.writerow({'iso3':iso,'name':x.get('name',''),'region':x.get('region',{}).get('value',''),'income_level':x.get('incomeLevel',{}).get('value','')})
 (root/'data'/'multisector_manifest.json').write_text(json.dumps(manifest,indent=2))
 (root/'reports').mkdir(exist_ok=True)
 (root/'reports'/'multisector_coverage.json').write_text(json.dumps({'quality':quality,'total_observations':len(observations),'all_sectors_represented':set(x['sector'] for x in observations)=={'climate','energy','water','food','demography','economy'}},indent=2))
 if not observations:raise ValueError('No real observations acquired')
 print(json.dumps({'total_observations':len(observations),'quality':quality},indent=2))
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();collect(a.root)
