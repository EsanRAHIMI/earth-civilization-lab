"""Explicit horizon-by-horizon empirical interval coverage.
Do not extrapolate 10 observed years into calibrated millennium probabilities.
"""
import json,pathlib,statistics
def run(root='.'):
 root=pathlib.Path(root)
 carbon=json.loads((root/'reports/noaa_gcp_carbon_hindcast.json').read_text())
 temp=json.loads((root/'reports/nasa_temperature_hindcast.json').read_text())
 sink=json.loads((root/'reports/gcb_separate_sink_calibration.json').read_text())
 checks={'carbon_one_year_interval_coverage_measured':carbon.get('n_holdout',0)>=8,'temperature_one_year_error_measured':temp.get('n_holdout',0)>=8,'ocean_flux_holdout_measured':sink['calibration']['ocean']['n_test']>=8,'land_flux_holdout_measured':sink['calibration']['land']['n_test']>=8,'millennial_out_of_sample_coverage_measured':False}
 report={'status':'finite_horizon_uncertainty_validation_audit','checks':checks,'carbon_nominal_95pct_interval_empirical_coverage':carbon['residual_bootstrap_nominal_95pct_coverage'],'carbon_coverage_sample_years':carbon['n_holdout'],'temperature_holdout_mae_c':temp['holdout_mae_c'],'ocean_flux_holdout_mae_gtc_year':sink['calibration']['ocean']['holdout_mae_gtc_per_year'],'land_flux_holdout_mae_gtc_year':sink['calibration']['land']['holdout_mae_gtc_per_year'],'1000_year_probabilities_validated':False,'reasons':['Only 10 years of held-out observations: no empirical millennium coverage test possible','Carbon interval test is one-year conditional and uses realized emissions','Temperature holdout conditions on realized CO2','GCB fluxes combine model estimates and observational products; not independent direct ocean and land observations','Structural uncertainty, paleoclimate constraints and future forcing scenario probabilities unresolved']}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'long_horizon_uncertainty_audit.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
