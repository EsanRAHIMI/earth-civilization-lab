"""Transparent six-sector regional research simulator, NOT a calibrated Earth digital twin.

Inputs are World Bank country-year observations. Missing values remain missing
during validation. Simulation uses explicit normalized scenario parameters.
"""
import csv, json, math, pathlib, random, statistics
from collections import defaultdict

FIELDS=('climate_ghg_per_capita','energy_use_per_capita','freshwater_withdrawals','food_production_index','population','real_gdp_per_capita')
SECTORS=('climate','energy','water','food','population','economy')
DRIVERS={
 'climate':{'energy':0.22,'economy':0.12,'food':0.04},
 'energy':{'economy':0.15,'water':-0.04,'climate':-0.05},
 'water':{'climate':-0.12,'food':-0.05,'population':-0.06},
 'food':{'water':0.20,'energy':0.12,'climate':-0.12},
 'population':{'food':0.08,'water':0.05,'economy':0.06},
 'economy':{'energy':0.16,'food':0.09,'climate':-0.10,'water':0.06},
}
# All coefficients are illustrative. In particular these are not causal estimates.
def step(state, scenario=None, rng=None):
 scenario=scenario or {}; rng=rng or random.Random(0)
 next_state={}
 for sector in SECTORS:
  forcing=sum(weight*(state[other]-1) for other,weight in DRIVERS[sector].items())
  drift=scenario.get(sector,0)
  perturb=rng.gauss(0,scenario.get('shock_std',0))
  next_state[sector]=max(0.001,state[sector]*math.exp(max(-0.4,min(0.4,forcing+drift+perturb))))
 return next_state

def simulate(initial=None,years=30,replicates=100,seed=2026,scenario=None):
 if not 1<=years<=1000 or not 1<=replicates<=1000:raise ValueError('Invalid horizon or ensemble size')
 initial=initial or {k:1.0 for k in SECTORS}
 if set(initial)!=set(SECTORS) or any(not math.isfinite(v) or v<=0 for v in initial.values()):raise ValueError('Invalid initial sector indices')
 traces={k:defaultdict(list) for k in SECTORS}
 for i in range(replicates):
  rng=random.Random(seed+i);state=dict(initial)
  for y in range(years+1):
   for k in SECTORS:traces[k][y].append(state[k])
   if y<years:state=step(state,scenario,rng)
 output={}
 for k in SECTORS:
  output[k]=[]
  for y,values in traces[k].items():
   values.sort();n=len(values)
   output[k].append({'year_offset':y,'p05':values[int((n-1)*.05)],'median':statistics.median(values),'p95':values[int((n-1)*.95)]})
 return {'model':'exploratory normalized six-sector coupled scenario','scientifically_validated':False,'confidence_interval_interpretation':'conditional Monte Carlo spread only; NOT empirically calibrated uncertainty','coefficients':'illustrative, not fitted causal effects','years':years,'replicates':replicates,'seed':seed,'sectors':output}

def read_observations(path):
 by=defaultdict(dict)
 with open(path,newline='') as f:
  for r in csv.DictReader(f):
   if r['indicator'] not in FIELDS:continue
   v=float(r['value'])
   if math.isfinite(v):by[(r['country'],r['indicator'])][int(r['year'])]=v
 return by

def spatial_country_panel(root):
 """Country-indexed spatial panel, not a gridded geospatial raster."""
 root=pathlib.Path(root);p=root/'data/multisector_observations.csv'
 if not p.exists():return {'status':'missing_world_bank_observations','countries':0}
 rows=read_observations(p);coverage=defaultdict(lambda:defaultdict(int))
 for (country,indicator),years in rows.items():coverage[country][indicator]=len(years)
 return {'status':'country_level_spatial_index_only','countries':len(coverage),'coordinate_geometry_available':False,'gridded_spatial_integration_complete':False,'coverage':dict(coverage)}

def independent_holdout(root):
 """2019-2023 one-year-ahead persistence reference, never train on future observations."""
 root=pathlib.Path(root);p=root/'data/multisector_observations.csv'
 if not p.exists():return {'status':'blocked_missing_observed_panel','indicators':{}}
 rows=read_observations(p);result={}
 for indicator in FIELDS:
  errors=[]
  for (country,name),d in rows.items():
   if name!=indicator:continue
   for y in range(2019,2024):
    if y in d and y-1 in d:errors.append(abs(d[y]-d[y-1]))
  result[indicator]={'n_pairs':len(errors),'persistence_mae':statistics.mean(errors) if errors else None,'coupled_model_skill':'not_evaluated','independent_source_verified':False}
 return {'status':'historical_reference_only','holdout_years':[2019,2023],'indicators':result,'validated_coupled_model':False}

def run(root='.'):
 root=pathlib.Path(root);out=root/'reports';out.mkdir(exist_ok=True)
 report={'simulation':simulate(years=50,replicates=120,scenario={'shock_std':.015}),'spatial':spatial_country_panel(root),'validation':independent_holdout(root)}
 (out/'coupled_six_sector_research.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'status':'exploratory_only','sectors':list(SECTORS),'spatial':report['spatial']['status'],'validation':report['validation']['status']}))
 return report
if __name__=='__main__':run()
