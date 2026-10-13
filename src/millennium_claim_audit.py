"""Scientific claim firewall for millennial scenario outputs.
A passing workflow cannot confer forecast validity. Conservative checks are
machine-readable and the research claim remains blocked until evidence exists.
"""
import argparse,json,pathlib,math
REQUIRED=('operational_readiness.json','physical_validation_audit.json','gcp_independent_target_calibration.json')
def evaluate(root):
 root=pathlib.Path(root);reports=root/'reports';data={}
 for name in REQUIRED:
  p=reports/name
  if not p.exists():raise FileNotFoundError('Required audit missing: '+name)
  data[name]=json.loads(p.read_text())
 op=data['operational_readiness.json'];gcp=data['gcp_independent_target_calibration.json']
 metrics=gcp.get('holdout_model',{})
 numeric=all(isinstance(metrics.get(k),(int,float)) and math.isfinite(metrics[k]) for k in ('mae','rmse','smape_percent'))
 checks={
  'operational_evidence_available':op.get('operational_pipeline_pass') is True,
  'external_target_holdout_has_numeric_errors':numeric,
  'external_target_holdout_meets_20pct_smape':numeric and metrics['smape_percent']<=20,
  'cross_sector_independent_validation':False,
  'physical_temperature_historical_hindcast':False,
  'bitcoin_energy_emissions_measurement_validated':False,
  'parameter_identifiability_demonstrated':False,
  'uncertainty_coverage_out_of_sample_calibrated':False,
  'long_horizon_structural_stability_demonstrated':False
 }
 valid=all(checks.values())
 output={'model_horizon_years':1000,'scientifically_validated_1000_year_forecast':valid,'scientific_claim':'validated probabilistic 1000-year forecast' if valid else 'exploratory conditional scenario stress test only','checks':checks,'gcp_holdout_smape_percent':metrics.get('smape_percent'),'limitations':['Scientific validity requires external hindcasts, identifiable physical mechanisms and uncertainty coverage','Observed 2000-2023 data cannot establish 1000-year social or Bitcoin predictability','Passing computational conservation checks is not empirical calibration']}
 (reports/'millennium_claim_audit.json').write_text(json.dumps(output,indent=2))
 print(json.dumps(output,indent=2));return output
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');evaluate(p.parse_args().root)
