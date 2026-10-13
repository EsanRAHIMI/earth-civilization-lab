"""Physical carbon accounting audit and explicit non-identifiability checks."""
import argparse,json,pathlib,math
from src.physical_core import POLICIES,State,step,Policy,CO2_PER_C
def audit(root):
 results=[]
 for name,policy in POLICIES.items():
  state=State();initial=state.carbon_total();maxerr=0.;minstock=float('inf');maxenergy=0.
  for i in range(1000):
   before=state.carbon_total()
   state,flows,nextshare=step(state,policy)
   residual=abs(state.carbon_total()-initial)
   maxerr=max(maxerr,residual)
   minstock=min(minstock,state.atmosphere_gtc,state.ocean_gtc,state.land_gtc,state.fossil_remaining_gtc)
   maxenergy=max(maxenergy,state.energy_demand_ej)
   if abs(flows['co2_emissions_gt']-flows['extracted_gtc']*CO2_PER_C)>1e-10:raise AssertionError('unit conversion')
   if abs(before-state.carbon_total())>1e-7:raise AssertionError('carbon balance')
   policy=Policy(**{**vars(policy),'fossil_share':nextshare})
  results.append({'scenario':name,'years':1000,'max_mass_balance_error_gtc':maxerr,'min_carbon_stock_gtc':minstock,'max_energy_demand_ej_per_year':maxenergy,'mass_conservation_pass':maxerr<1e-7,'empirical_flux_validation':False})
 out={'status':'physical_conservation_verified_only','results':results,'empirically_calibrated':False,'independent_earth_system_validation':False,'temperature_predictions_valid':False,'caveats':['Initial stocks and exchange rates are illustrative','GHG CO2e cannot be directly mapped into fossil CO2 GtC','Mass conservation is necessary but insufficient for climate physics','Exogenous growth is not a validated millennium forecast']}
 folder=pathlib.Path(root)/'reports';folder.mkdir(exist_ok=True)
 (folder/'physical_validation_audit.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2));return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');audit(p.parse_args().root)
