"""Inventory all physical model parameters and distinguish constrained from identified.

Physical box rates cannot be independently estimated from net annual flux
series without stock, gross flux, and heat-content observations.
"""
from dataclasses import asdict
from src.multibox_climate import Parameters
import json,pathlib
KINDS={
 'air_ocean':('carbon exchange','ocean-atmosphere net flux; surface-ocean DIC/pCO2'),
 'ocean_mixing':('carbon exchange','surface/deep DIC, ocean ventilation tracers'),
 'photosynthesis':('biosphere','gross primary productivity and atmospheric CO2'),
 'litter':('biosphere','vegetation/soil stock change and litterfall'),
 'respiration':('biosphere','soil respiration flux and soil carbon inventory'),
 'land_use_gtc':('external forcing','GCB land-use emissions and land-use area changes'),
 'restoration_gtc':('biosphere','regrowth uptake and land-cover restoration'),
 'feedback':('heat','temperature, TOA radiative imbalance and forcing'),
 'heat_exchange':('heat','surface/deep temperature and ocean heat content'),
 'heat_surface':('heat','mixed-layer heat capacity and depth'),
 'heat_deep':('heat','deep-ocean heat content and vertical distribution')
}
def run(root='.'):
 root=pathlib.Path(root)
 fitted={'air_ocean','photosynthesis'}
 data=asdict(Parameters())
 parameters={name:{'default':value,'category':KINDS[name][0],'required_observations':KINDS[name][1],'status':('joint_effective_rate_fit_only' if name in fitted else 'not_independently_calibrated')} for name,value in data.items()}
 report={'parameters':parameters,'total':len(parameters),'effective_joint_fit':len(fitted),'fully_independently_identified':0,'full_physical_calibration_complete':False,'scientific_warning':'Model parameter values are illustrative defaults unless explicitly fitted; no net-flux fit identifies unobserved gross exchange or stock turnover.'}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'physical_parameter_inventory.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
