"""Conservation-constrained joint inverse fit of effective carbon-box rates.

Fits air-sea and photosynthesis coefficients jointly against GCB net sinks.
Unobserved gross ocean mixing, litter and respiration are held fixed, NOT
calibrated. No claim of complete physical parameter identification.
"""
import json,math,pathlib,statistics
from dataclasses import replace
from src.multibox_climate import State,Parameters,step
from src.gcb_separate_sink_calibration import load
from src.nasa_temperature_hindcast import observations
def simulate(params,co2,landuse,years):
 s=State(year=years[0],air=co2[years[0]]*2.124, surface_temp=0.4)
 ocean_pred={};land_pred={}
 for year in years:
  # Observed annual atmospheric concentration conditions the net-flux test.
  # This is not a free-running historical simulation.
  s.air=co2[year]*2.124
  previous=replace(s)
  s,flux=step(s,params,fossil_gtc=0.,land_use_gtc=landuse[year])
  ocean_pred[year]=flux['air_ocean']+flux['ocean_mixing']
  # Net ocean uptake includes surface-to-deep transport only when measuring
  # deep stock; ocean system total sink is air-sea flux alone.
  ocean_pred[year]=flux['air_ocean']
  land_pred[year]=flux['photosynthesis']+flux['restoration']-flux['respiration']-flux['deforestation']
 return ocean_pred,land_pred
def run(root='.'):
 root=pathlib.Path(root);co2,_,_=observations(root)
 ocean,_=load('ocean-sink',root);land,_=load('terrestrial-sink',root)
 landuse,_=load('land-use-change-emissions',root)
 years=[y for y in range(1980,2025) if all(y in d for d in (co2,ocean,land,landuse))]
 train=[y for y in years if y<=2014];test=[y for y in years if y>=2015]
 if len(train)<30 or len(test)<8:raise ValueError('Insufficient temporal overlap')
 # Coarse-to-fine bounded deterministic joint search; scale by train std.
 scales=[statistics.pstdev([d[y] for y in train]) or 1 for d in (ocean,land)]
 def score(a,p):
  op,lp=simulate(Parameters(air_ocean=a,photosynthesis=p),co2,landuse,years)
  return sum(((op[y]-ocean[y])/scales[0])**2+((lp[y]-land[y])/scales[1])**2 for y in train),op,lp
 best=None
 for a in [i*.005 for i in range(1,21)]:
  for p in [i*.005 for i in range(1,21)]:
   try:v,_,_=score(a,p)
   except (ValueError,AssertionError,OverflowError):continue
   if math.isfinite(v) and (best is None or v<best[0]):best=(v,a,p)
 if best is None:raise RuntimeError('No physically valid fit')
 for width in (.005,.001):
  candidates=[]
  for i in range(-5,6):
   for j in range(-5,6):
    a=best[1]+i*width;p=best[2]+j*width
    if not (0<a<=.3 and 0<p<=.3):continue
    try:v,_,_=score(a,p)
    except (ValueError,AssertionError,OverflowError):continue
    if math.isfinite(v):candidates.append((v,a,p))
  best=min(candidates+[best])
 _,op,lp=score(best[1],best[2])
 metrics={}
 for name,actual,pred in [('ocean',ocean,op),('land',land,lp)]:
  baseline=statistics.mean(actual[y] for y in train)
  mae=statistics.mean(abs(pred[y]-actual[y]) for y in test)
  bmae=statistics.mean(abs(baseline-actual[y]) for y in test)
  metrics[name]={'holdout_mae_gtc_year':mae,'baseline_mae_gtc_year':bmae,'beats_baseline':mae<bmae}
 report={'status':'partial_conservation_constrained_inverse_fit','train_years':len(train),'holdout_years':len(test),'joint_objective':'sum of variance-normalized squared annual net ocean and terrestrial flux residuals','fitted_rates':{'air_ocean':best[1],'photosynthesis':best[2]},'holdout':metrics,'unfitted_rates':['ocean_mixing','litter','respiration','restoration','heat_exchange','feedback'],'atmosphere_forced_with_observed_co2':True,'land_use_emissions_used_as_external_driver':True,'physical_full_calibration_complete':False,'reason':'Net flux observations alone cannot identify internal reservoir turnover; stock and gross flux observations absent. Model also has simplified flux physics.'}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'constrained_joint_physical_fit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
