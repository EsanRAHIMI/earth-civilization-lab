"""Independent persistence baselines for all ten observed sector indicators.

Leakage-free country-level 2019-2023 one-year holdout. Persistence is a
reference, not a learned model; absent consecutive observations are omitted.
"""
import collections,csv,json,pathlib,statistics,math
from src.multisector import INDICATORS
def run(root='.'):
 root=pathlib.Path(root);p=root/'data/multisector_observations.csv'
 rows=collections.defaultdict(dict)
 with p.open() as f:
  for r in csv.DictReader(f):rows[(r['country'],r['indicator'])][int(r['year'])]=float(r['value'])
 results={}
 for name,(_,unit,sector) in INDICATORS.items():
  errors=[];pairs=0;countries=set()
  for (country,indicator),d in rows.items():
   if indicator!=name:continue
   for y in range(2019,2024):
    if y not in d or y-1 not in d:continue
    current,prev=d[y],d[y-1]
    if not all(map(math.isfinite,(current,prev))):continue
    errors.append(abs(current-prev));pairs+=1;countries.add(country)
  results[name]={'sector':sector,'units':unit,'n_holdout_pairs':pairs,'countries':len(countries),'persistence_mae':statistics.mean(errors) if errors else None,'holdout_years':'2019-2023','model_skill_evaluated':False}
 report={'status':'all_indicator_persistence_baselines_computed','indicators':results,'limitations':['Persistence benchmarks are not fitted physical models','Only countries with consecutive annual observations are evaluated','Different indicators use different units and MAEs must not be compared directly']}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'all_sector_persistence_baselines.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
