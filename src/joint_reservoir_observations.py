"""Assemble verified available flux and ocean heat observations for inversion.

This is an observation bundle, not an assertion that internal reservoir stocks
or gross fluxes have been measured. Missing independent series are explicit.
"""
import csv,json,pathlib,statistics
from src.gcb_separate_sink_calibration import load
from src.nasa_temperature_hindcast import observations
def run(root='.'):
 root=pathlib.Path(root);o,osrc=load('ocean-sink',root);l,lsrc=load('terrestrial-sink',root)
 landuse,lusrc=load('land-use-change-emissions',root);co2,temp,_=observations(root)
 path=root/'data/independent_raw/ocean_heat_content_annual.csv'
 if not path.exists():raise FileNotFoundError('Run NOAA ocean heat import first')
 heat={}
 for row in csv.DictReader(path.open()):
  try:heat[int(row['year'])]=float(row['heat_0_2000_zj'])
  except (ValueError,KeyError):continue
 years=sorted(set(o)&set(l)&set(landuse)&set(co2)&set(temp)&set(heat))
 if len([y for y in years if 2005<=y<=2024])<20:raise ValueError('Insufficient independent annual overlap')
 out=root/'data/independent_raw/joint_reservoir_observations.csv'
 with out.open('w',newline='') as f:
  w=csv.writer(f);w.writerow(['year','co2_ppm','temperature_anomaly_c','ocean_net_sink_gtc_year','land_net_sink_gtc_year','land_use_emissions_gtc_year','ocean_heat_0_2000_anomaly_zj'])
  for y in years:w.writerow([y,co2[y],temp[y],o[y],l[y],landuse[y],heat[y]])
 report={'status':'observed_joint_flux_and_heat_bundle_created','n_years':len(years),'years':[min(years),max(years)],'sources':{'ocean_sink':osrc,'land_sink':lsrc,'land_use':lusrc,'heat':'NOAA NCEI','co2':'NOAA GML','temperature':'NASA GISTEMP'},'independent_gross_internal_carbon_fluxes_present':False,'independent_deep_ocean_dic_stock_present':False,'independent_vegetation_soil_stock_present':False,'physical_complete_calibration':False,'warning':'GCB net sinks are synthesis/model products, not independent gross internal reservoir flux measurements.'}
 dest=root/'reports';dest.mkdir(exist_ok=True);(dest/'joint_reservoir_observation_bundle.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
