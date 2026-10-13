"""Exploratory coupled civilization stress test. NOT a validated forecast.
All parameters are illustrative, explicit and sensitivity-tested.
No historical calibration or claims of 1000-year survival probability.
"""
import argparse,csv,json,math,pathlib,random,statistics
SCENARIOS={
 'baseline':{'mitigation':0.03,'innovation':0.012,'cooperation':0.60,'shocks':0.06},
 'cooperative_transition':{'mitigation':0.065,'innovation':0.018,'cooperation':0.85,'shocks':0.06},
 'fragmented':{'mitigation':0.012,'innovation':0.006,'cooperation':0.25,'shocks':0.12},
}
def simulate(policy,seed=0,years=1000,params=None):
 p={'climate_sensitivity':0.004,'resource_recovery':0.012,'shock_damage':0.035,'decarbonization_floor':0.001}
 if params:p.update(params)
 rng=random.Random(seed)
 s={'population':8.0,'wellbeing':0.65,'ecosystem':0.8,'resources':0.9,'knowledge':1.0,'carbon':1.0,'warming':1.2,'institutions':0.65}
 trace=[];collapse=None
 for year in range(years+1):
  if year%10==0 or year==years:trace.append({'year':year,**{k:round(v,6) for k,v in s.items()}})
  if year==years:break
  shock=rng.random()<policy['shocks']
  damage=p['shock_damage']*(1.5-policy['cooperation']) if shock else 0
  innovation=policy['innovation']*s['institutions']*s['ecosystem']
  emissions=s['population']*s['carbon']*0.018
  s['warming']=max(0,s['warming']+p['climate_sensitivity']*emissions-0.0006*s['warming'])
  climate_pressure=max(0,s['warming']-1.5)*0.0018
  s['ecosystem']=max(0,min(1,s['ecosystem']+p['resource_recovery']*(1-s['ecosystem'])-0.002*emissions-climate_pressure-damage*0.5))
  s['resources']=max(0,min(1,s['resources']+0.012*s['ecosystem']*(1-s['resources'])-0.005*s['population']/8*(1-0.3*min(s['knowledge'],4))-damage*0.2))
  s['knowledge']=min(100,s['knowledge']*(1+innovation)*(1-damage*0.2))
  s['carbon']=max(p['decarbonization_floor'],s['carbon']*(1-policy['mitigation']*s['institutions']))
  s['institutions']=max(0,min(1,s['institutions']+0.008*(policy['cooperation']-s['institutions'])-damage*0.7))
  stress=max(0,0.55-s['resources'])+max(0,0.55-s['ecosystem'])+max(0,s['warming']-3)*0.08
  s['wellbeing']=max(0,min(1,s['wellbeing']+0.007*(s['ecosystem']-0.5)+0.004*(s['resources']-0.5)+0.002*math.log1p(s['knowledge'])-0.012*stress-damage))
  s['population']=max(0,s['population']*(1+0.002*(s['wellbeing']-0.55)-0.003*stress-damage*0.35))
  if collapse is None and (s['population']<2 or s['wellbeing']<0.25 or s['ecosystem']<0.2):collapse=year+1
 return {'collapse_year':collapse,'final':s,'trace':trace}
def experiment(root,replicates=60,years=1000):
 root=pathlib.Path(root);out=root/'reports';out.mkdir(exist_ok=True)
 rows=[];traces={}
 for name,policy in SCENARIOS.items():
  for i in range(replicates):
   # Same seed across policies is a variance-reduction comparison, not identical shock paths.
   result=simulate(policy,seed=i,years=years)
   f=result['final']
   rows.append({'scenario':name,'seed':i,'collapse_year':result['collapse_year'] or '', 'survived_horizon':int(result['collapse_year'] is None),'final_wellbeing':f['wellbeing'],'final_ecosystem':f['ecosystem'],'final_population_billion':f['population'],'final_warming_proxy':f['warming']})
   if i==0:traces[name]=result['trace']
 with (out/'scenario_runs.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 summary={}
 for name in SCENARIOS:
  group=[r for r in rows if r['scenario']==name]
  summary[name]={'runs':len(group),'fraction_not_crossing_failure_threshold':statistics.mean(r['survived_horizon'] for r in group),'median_final_wellbeing':statistics.median(r['final_wellbeing'] for r in group),'median_final_ecosystem':statistics.median(r['final_ecosystem'] for r in group)}
 # Parameter perturbations: demonstrate structural sensitivity, not calibrated confidence intervals.
 sensitivity=[]
 for label,changes in [('low_climate',{'climate_sensitivity':0.002}),('high_climate',{'climate_sensitivity':0.008}),('low_recovery',{'resource_recovery':0.006}),('high_shock_damage',{'shock_damage':0.07})]:
  for name,policy in SCENARIOS.items():
   vals=[simulate(policy,i,years,changes) for i in range(20)]
   sensitivity.append({'perturbation':label,'scenario':name,'fraction_not_crossing_failure_threshold':statistics.mean(v['collapse_year'] is None for v in vals)})
 report={'model_class':'illustrative coupled stress-test; NOT empirical forecast','years':years,'replicates_per_scenario':replicates,'parameters_are_calibrated':False,'survival_probability_claim_valid':False,'thresholds_are_normative_illustrations':True,'summary':summary,'sensitivity':sensitivity,'sample_trajectories':traces,'caveats':['No fitted parameters from historical data','No conservation-consistent carbon cycle','No demographic age structure','No policy causality identification','Scenario fractions are conditional on chosen toy assumptions, not probabilities for the real world']}
 (out/'scenario_report.json').write_text(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--years',type=int,default=1000);ap.add_argument('--replicates',type=int,default=60);a=ap.parse_args()
 r=experiment(a.root,a.replicates,a.years)
 print(json.dumps({'model_class':r['model_class'],'summary':r['summary'],'scientifically_validated':False},indent=2))
