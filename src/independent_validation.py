"""Independent-source validation gate. No pass without actual external observations.
Input CSV: country,year,ghg_tco2e_per_capita,source_name.
Only directly comparable total GHG per-capita inventories with documented boundary
and independent upstream methodology may be used. Fossil CO2 != all-GHG CO2e.
"""
import argparse,csv,json,math,pathlib,collections
def validate(root,external):
 root=pathlib.Path(root);external=pathlib.Path(external)
 report=json.loads((root/'reports/historical_calibration.json').read_text())
 if not external.is_file():raise FileNotFoundError('Independent harmonized GHG dataset absent; validation NOT passed')
 coef=report['coefficients'];keys=('real_gdp_per_capita','energy_use_per_capita')
 obs=collections.defaultdict(dict)
 with (root/'data/multisector_observations.csv').open() as f:
  for r in csv.DictReader(f):
   if r['indicator'] in keys:obs[(r['country'],int(r['year']))][r['indicator']]=float(r['value'])
 errors=[];countries=set();sources=set();seen=set()
 with external.open() as f:
  for r in csv.DictReader(f):
   c=r['country'];year=int(r['year']);key=(c,year)
   if key in seen:raise ValueError('duplicate external country-year')
   seen.add(key);source=r['source_name'].strip()
   if not source or 'world bank' in source.lower():raise ValueError('source is not independent')
   sources.add(source)
   if not 2019<=year<=2023:continue
   x=obs.get(key,{})
   if not all(k in x and math.isfinite(x[k]) and x[k]>0 for k in keys):continue
   actual=float(r['ghg_tco2e_per_capita'])
   if not math.isfinite(actual) or actual<=0:raise ValueError('invalid external GHG')
   predicted=math.exp(coef['intercept']+coef['log_gdp']*math.log(x[keys[0]])+coef['log_energy']*math.log(x[keys[1]]))
   errors.append((actual,predicted));countries.add(c)
 if len(errors)<100 or len(countries)<30:raise ValueError('Independent overlap insufficient; no validation pass')
 mae=sum(abs(a-p) for a,p in errors)/len(errors)
 smape=100*sum(2*abs(a-p)/(a+p) for a,p in errors)/len(errors)
 result={'status':'external_source_comparison_completed_not_causal_validation','n':len(errors),'countries':len(countries),'sources':sorted(sources),'mae_tco2e_per_capita':mae,'smape_percent':smape,'methodology_review_required':True,'millennium_model_validated':False,'warning':'External dataset comparability, upstream provenance and shared methodological dependencies require human scientific review.'}
 (root/'reports/independent_ghg_comparison.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2));return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--external',required=True);a=p.parse_args();validate(a.root,a.external)
