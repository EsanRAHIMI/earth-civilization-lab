"""Dimensioned annual carbon-energy-population accounting prototype.
Not calibrated or an Earth system model. Illustrative parameters are explicitly identified.
Conservation: atmosphere + ocean + land carbon + cumulative geological extraction is invariant.
Units: GtC, EJ/year, billions of people, tCO2/person/year.
"""
from dataclasses import dataclass,asdict
import math,json,csv,pathlib,argparse
CO2_PER_C=44/12
@dataclass
class State:
 year:int=2025
 atmosphere_gtc:float=890.0
 ocean_gtc:float=38000.0
 land_gtc:float=2300.0
 fossil_remaining_gtc:float=3500.0
 population_billion:float=8.2
 energy_demand_ej:float=620.0
 wellbeing_index:float=0.65
 def carbon_total(self):return self.atmosphere_gtc+self.ocean_gtc+self.land_gtc+self.fossil_remaining_gtc
@dataclass(frozen=True)
class Policy:
 name:str
 fossil_share:float
 annual_fossil_reduction:float
 energy_growth:float
 population_growth:float
 fossil_carbon_gtc_per_ej:float=0.018
 air_ocean_exchange_rate:float=0.002
 air_land_exchange_rate:float=0.003
 reference_atmosphere_gtc:float=890.0
 ocean_equilibrium_gtc:float=38000.0
 land_equilibrium_gtc:float=2300.0
def step(s,p):
 if not 0<=p.fossil_share<=1 or not 0<=p.annual_fossil_reduction<=1:raise ValueError('invalid fossil policy')
 fossil_ej=s.energy_demand_ej*p.fossil_share
 extraction=min(s.fossil_remaining_gtc,fossil_ej*p.fossil_carbon_gtc_per_ej)
 # Explicit simplified fluxes: each flow moves carbon between two tracked stocks.
 ocean_flux=p.air_ocean_exchange_rate*(s.atmosphere_gtc-p.reference_atmosphere_gtc)
 land_flux=p.air_land_exchange_rate*(s.atmosphere_gtc-p.reference_atmosphere_gtc)
 # Limit fluxes by available stocks so no stock becomes negative.
 ocean_flux=max(-s.ocean_gtc,min(ocean_flux,s.atmosphere_gtc+extraction))
 land_flux=max(-s.land_gtc,min(land_flux,s.atmosphere_gtc+extraction-ocean_flux))
 a=s.atmosphere_gtc+extraction-ocean_flux-land_flux
 o=s.ocean_gtc+ocean_flux;l=s.land_gtc+land_flux
 f=s.fossil_remaining_gtc-extraction
 next_policy_share=p.fossil_share*(1-p.annual_fossil_reduction)
 n=State(year=s.year+1,atmosphere_gtc=a,ocean_gtc=o,land_gtc=l,fossil_remaining_gtc=f,population_billion=s.population_billion*(1+p.population_growth),energy_demand_ej=s.energy_demand_ej*(1+p.energy_growth),wellbeing_index=s.wellbeing_index)
 if any(not math.isfinite(x) or x<0 for x in [a,o,l,f,n.population_billion,n.energy_demand_ej]):raise ValueError('invalid stock')
 if not math.isclose(n.carbon_total(),s.carbon_total(),rel_tol=0,abs_tol=1e-7):raise AssertionError('carbon not conserved')
 flows={'extracted_gtc':extraction,'ocean_uptake_gtc':ocean_flux,'land_uptake_gtc':land_flux,'fossil_energy_ej':fossil_ej,'co2_emissions_gt':extraction*CO2_PER_C}
 return n,flows,next_policy_share
POLICIES={
 'current_trajectory':Policy('current_trajectory',0.8,0.01,0.008,0.004),
 'accelerated_transition':Policy('accelerated_transition',0.8,0.055,0.008,0.004),
 'slow_transition':Policy('slow_transition',0.8,0.002,0.008,0.004),
}
def run(policy,years=1000):
 s=State();initial=s.carbon_total();trace=[]
 for _ in range(years):
  s,flows,share=step(s,policy)
  if s.year%10==0 or s.year==2026:trace.append({'year':s.year,**asdict(s),**flows,'carbon_residual_gtc':s.carbon_total()-initial})
  policy=Policy(**{**asdict(policy),'fossil_share':share})
 return trace
def main(root,years):
 out=pathlib.Path(root)/'reports';out.mkdir(parents=True,exist_ok=True)
 records=[]
 for name,p in POLICIES.items():
  for row in run(p,years):records.append({'scenario':name,**row})
 with (out/'physical_core_trajectories.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=records[0].keys());w.writeheader();w.writerows(records)
 metadata={'status':'engineering_conservation_test_only','physical_carbon_conservation':True,'empirical_calibration':False,'climate_temperature_model':False,'policy_impact_validated':False,'years':years,'carbon_unit':'GtC','energy_unit':'EJ/year','parameters':'illustrative','limitations':['Atmosphere-ocean and land flux coefficients are invented placeholders','No temperature/forcing/feedback model','No births/deaths, technology cost, trade, institutions or equity mechanisms','Initial carbon stocks illustrative; do not interpret output as forecast','Constant exogenous energy/population growth produces unrealistic millennial dynamics']}
 (out/'physical_core_metadata.json').write_text(json.dumps(metadata,indent=2))
 print(json.dumps({'rows':len(records),'scenarios':list(POLICIES),'max_absolute_conservation_error_gtc':max(abs(x['carbon_residual_gtc']) for x in records),'empirically_validated':False},indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--root',default='.');ap.add_argument('--years',type=int,default=1000);a=ap.parse_args();main(a.root,a.years)
