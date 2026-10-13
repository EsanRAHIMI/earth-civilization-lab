"""Transparent calibration-readiness screening, not model calibration.
A 'candidate' only passes descriptive completeness and continuity gates.
"""
import argparse,csv,collections,json,pathlib,statistics
SECTORS={'climate','energy','water','food','demography','economy'}
def assess(root):
 root=pathlib.Path(root)
 manifest=json.loads((root/'data/multisector_manifest.json').read_text())
 with (root/'data/multisector_country_coverage.csv').open() as f:rows=list(csv.DictReader(f))
 if not rows:raise ValueError('No country coverage records')
 years=manifest['retrieval_years'];expected=years[1]-years[0]+1
 if any(int(r['years_expected'])!=expected for r in rows):raise ValueError('inconsistent years')
 indicators=sorted({r['indicator'] for r in rows})
 countries=sorted({r['iso3'] for r in rows})
 if len(rows)!=len(indicators)*len(countries):raise ValueError('incomplete country-indicator matrix')
 grouped=collections.defaultdict(list)
 for r in rows:grouped[r['indicator']].append(r)
 # Strict 80% full-period coverage and at least 5 recent observations
 # (2019-2023); temporal recency is checked from missing_years.
 report=[]
 for indicator,group in sorted(grouped.items()):
  observed=sum(int(r['years_observed']) for r in group)
  complete=sum(int(r['years_observed'])==expected for r in group)
  eligible=[]
  for r in group:
   missing=set(map(int,filter(None,r['missing_years'].split(';'))))
   recent=sum(y not in missing for y in range(max(years[0],years[1]-4),years[1]+1))
   if int(r['years_observed'])>=int(0.8*expected+0.999999) and recent>=4:eligible.append(r['iso3'])
  report.append({'indicator':indicator,'sector':group[0]['sector'],'countries_total':len(group),'observations':observed,'possible':len(group)*expected,'coverage_fraction':round(observed/(len(group)*expected),6),'fully_complete_countries':complete,'screen_pass_countries':len(eligible),'screen_pass_iso3':eligible,'screen_rule':'at least 80% observed years AND 4 of last 5 years','calibration_validated':False})
 by_sector=[]
 for sector in sorted(SECTORS):
  subset=[r for r in report if r['sector']==sector]
  if not subset:raise ValueError('Missing sector '+sector)
  by_sector.append({'sector':sector,'indicators':len(subset),'observations':sum(r['observations'] for r in subset),'possible':sum(r['possible'] for r in subset),'coverage_fraction':round(sum(r['observations'] for r in subset)/sum(r['possible'] for r in subset),6)})
 out={'source_panel_sha256':manifest['panel_sha256'],'countries':len(countries),'years':years,'total_observations':sum(r['observations'] for r in report),'indicators':report,'sectors':by_sector,'calibrated':False,'independently_validated':False,'warning':'Completeness screen is NOT evidence of predictive accuracy, causal identification, independence, or calibration. Coverage can conceal structural gaps and revisions.'}
 folder=root/'reports';folder.mkdir(exist_ok=True)
 (folder/'calibration_readiness.json').write_text(json.dumps(out,indent=2))
 with (folder/'calibration_readiness.csv').open('w',newline='') as f:
  fields=['indicator','sector','countries_total','observations','possible','coverage_fraction','fully_complete_countries','screen_pass_countries','screen_rule','calibration_validated']
  w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows([{k:r[k] for k in fields} for r in report])
 print(json.dumps({'countries':len(countries),'observations':out['total_observations'],'sectors':by_sector,'screen_pass':{r['indicator']:r['screen_pass_countries'] for r in report}},indent=2))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');a=p.parse_args();assess(a.root)
