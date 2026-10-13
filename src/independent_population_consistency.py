"""Independent-source consistency check, not causal climate validation."""
import csv,json,math,pathlib,statistics,argparse
def read(path):
 data={}
 with open(path,encoding='utf-8-sig') as f:
  for r in csv.DictReader(f):
   iso=r['ISO 3166-1 alpha-3']
   if len(iso)!=3 or not iso.isalpha():continue
   try:key=(iso,int(r['Year']));value=float(r['Total'])
   except (ValueError,TypeError):continue
   if math.isfinite(value) and value>0:data[key]=value
 return data
def run(root):
 root=pathlib.Path(root);folder=root/'data/independent_raw'
 per=read(folder/'gcp_fossil_co2_per_capita_2025.csv')
 total=read(folder/'gcp_fossil_co2_national_2025.csv')
 population={}
 with (root/'data/multisector_observations.csv').open() as f:
  for r in csv.DictReader(f):
   if r['indicator']=='population':
    population[(r['country'],int(r['year']))]=float(r['value'])
 diffs=[];countries=set()
 for (iso,year),v in per.items():
  key=(iso,year)
  if key not in total or key not in population or not 2000<=year<=2023:continue
  implied=total[key]*1000000/v
  actual=population[key]
  if actual<=0:continue
  diffs.append(abs(implied/actual-1)*100);countries.add(iso)
 if len(diffs)<100 or len(countries)<30:raise ValueError('Insufficient comparable independent-source overlap')
 out={'status':'cross_source_demographic_consistency_measured','observations':len(diffs),'countries':len(countries),'median_absolute_percent_difference':statistics.median(diffs),'mean_absolute_percent_difference':statistics.mean(diffs),'fraction_within_5_percent':sum(x<=5 for x in diffs)/len(diffs),'comparison':'GCP MtCO2 divided by GCP tCO2/person versus World Bank population','population_upstream_independence_verified':False,'climate_relationship_validated':False,'bitcoin_relationship_validated':False,'warning':'GCP fossil CO2 is not total GHG CO2e; do not validate climate model with this comparison'}
 dest=root/'reports';dest.mkdir(exist_ok=True)
 (dest/'independent_population_consistency.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2));return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');run(p.parse_args().root)
