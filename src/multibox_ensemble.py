"""Test physical invariants and produce 1000-year sensitivity ensemble.
These are NOT statistically calibrated prediction intervals.
"""
import argparse,json,pathlib,random,math,statistics
from src.multibox_climate import State,Parameters,step
def run(root,years=1000,draws=80):
 rng=random.Random(20261013);out=pathlib.Path(root)/'reports';out.mkdir(exist_ok=True)
 result={}
 for name,rate in [('fast',.055),('medium',.02),('slow',.005)]:
  samples=[]
  for j in range(draws):
   p=Parameters(air_ocean=rng.uniform(.02,.05),ocean_mixing=rng.uniform(.0005,.004),photosynthesis=rng.uniform(.008,.025),feedback=rng.uniform(.8,1.8),heat_exchange=rng.uniform(.4,1.0),land_use_gtc=rng.uniform(.4,1.5))
   s=State();start=s.carbon();peak=s.surface_temp
   for t in range(years):
    s,_=step(s,p,10*math.exp(-rate*t),p.land_use_gtc*math.exp(-.015*t))
    peak=max(peak,s.surface_temp)
   if abs(s.carbon()-start)>1e-6:raise AssertionError('millennial mass balance')
   samples.append((s.surface_temp,peak,s.air/2.12))
  def q(k):
   x=sorted(a[k] for a in samples);return [x[int((len(x)-1)*v)] for v in (.05,.5,.95)]
  result[name]={'final_warming_c_p05_p50_p95':q(0),'peak_warming_c_p05_p50_p95':q(1),'final_co2_ppm_p05_p50_p95':q(2)}
 report={'years':years,'draws':draws,'scenario_sensitivity':result,'carbon_conservation_verified':True,'land_use_change_included':True,'ocean_surface_and_deep_pools':True,'vegetation_and_soil_pools':True,'two_layer_temperature':True,'observationally_calibrated':False,'uncertainty_intervals_calibrated':False,'valid_thousand_year_forecast':False,'warning':'Illustrative parameter ranges, simplified forcing and initial conditions. Do not present as predictive probabilities.'}
 (out/'multibox_ensemble.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({'scenarios':list(result),'carbon_conservation_verified':True,'valid_thousand_year_forecast':False}))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--years',type=int,default=1000);p.add_argument('--draws',type=int,default=80);a=p.parse_args();run(a.root,a.years,a.draws)
