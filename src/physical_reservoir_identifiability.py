"""Evidence-based joint physical-reservoir calibration readiness.

Net atmospheric, ocean and land fluxes do not uniquely determine gross
air-surface ocean, surface-deep, vegetation-soil turnover. A full inverse
calibration needs independent stock and exchange observations.
"""
import json,pathlib
REQUIRED={
 'surface_ocean_dissolved_inorganic_carbon':('ocean_surface_dic_annual.csv','year,dic_gtc'),
 'deep_ocean_carbon_inventory':('ocean_deep_carbon_annual.csv','year,carbon_gtc'),
 'vegetation_carbon_stock':('vegetation_carbon_annual.csv','year,carbon_gtc'),
 'soil_carbon_stock':('soil_carbon_annual.csv','year,carbon_gtc'),
 'ocean_heat_content':('ocean_heat_content_annual.csv','year,heat_0_700_zj,heat_0_2000_zj')
}
def audit(root='.'):
 root=pathlib.Path(root);folder=root/'data/independent_raw'
 found={key:(folder/filename).is_file() for key,(filename,_) in REQUIRED.items()}
 required={key:{'file':filename,'columns':columns,'available':found[key]} for key,(filename,columns) in REQUIRED.items()}
 # Presence is necessary, not sufficient: data require provenance, units, observation
 # errors, temporal alignment and identifiability analysis before fitting.
 ready=False
 report={
  'status':'joint_physical_reservoir_calibration_blocked_insufficient_independent_stocks',
  'required_observations':required,
  'independent_reservoir_stock_observations_complete':all(found.values()),
  'physical_reservoir_parameters_jointly_calibrated':ready,
  'physical_parameters_identifiable':False,
  'ocean_heat_content_observed':found['ocean_heat_content'],
  'note':'Observed 0-2000m ocean heat anomalies do not identify ocean carbon inventories or internal gross carbon fluxes.',
  'reason':'Annual net ocean and land fluxes constrain only total net uptake. They do not uniquely identify deep-ocean mixing, air-sea exchange, gross photosynthesis, litterfall, respiration and soil turnover.',
  'do_not_claim':['Full coupled physical calibration','1000-year predictive validation','Calibrated long-horizon probabilities'],
  'next_requirements':['Acquire source-verified observational stock time series and uncertainty estimates','Reconcile inventory boundaries and baseline pool masses','Fit conservation-constrained dynamic state-space model','Test independent stock, flux, CO2 and temperature holdouts','Run parameter identifiability and posterior predictive checks']
 }
 out=root/'reports';out.mkdir(exist_ok=True)
 (out/'physical_reservoir_identifiability.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':audit()
