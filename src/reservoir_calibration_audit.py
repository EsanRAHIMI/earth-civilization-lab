"""Calibrate effective land/ocean sink allocation from GCP and NOAA observations.
The two sinks are not separately identifiable from atmospheric CO2 alone.
Thus a fixed allocation is NEVER presented as independently calibrated.
"""
import json,pathlib,statistics,math
def run(root='.'):
 root=pathlib.Path(root)
 carbon=json.loads((root/'reports/noaa_gcp_carbon_hindcast.json').read_text())
 multi=json.loads((root/'reports/multibox_ensemble.json').read_text())
 report={
 'status':'identifiability_audit_completed',
 'observed_constraints':['GCP fossil CO2 emissions','NOAA atmospheric CO2 annual changes'],
 'calibrated_from_observations':{'aggregate_effective_sink_response':True,'ocean_sink_separately':False,'land_sink_separately':False},
 'atmospheric_holdout_mae_ppm_per_year':carbon['holdout_mae_ppm_per_year'],
 'reason':'The observed atmospheric budget constrains net ocean+land uptake, not its unique partition; independent ocean flux and terrestrial land-use observations are required.',
 'long_horizon_uncertainty':{'method':'parameter-range scenario ensemble','scenarios':list(multi['scenario_sensitivity']),'parameter_posterior':False,'out_of_sample_interval_coverage_validated':False,'probabilities_for_real_world':False},
 'additional_observations_required':['Ocean air-sea CO2 flux observations and ocean carbon inventories','Independent land-use change emissions and terrestrial carbon stocks','Ocean heat content and non-CO2 radiative forcing','Paleoclimate constraints for centennial and millennial behavior'],
 'scientifically_validated_thousand_year_forecast':False}
 path=root/'reports/reservoir_calibration_audit.json';path.write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
