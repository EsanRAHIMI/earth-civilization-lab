"""Scientific skill gate: a green CI is not evidence that every component works.
Read observed holdout metrics and flag any component worse than training baseline.
"""
import json,pathlib,math
def evaluate(root='.'):
 root=pathlib.Path(root);reports=root/'reports'
 sink=json.loads((reports/'gcb_separate_sink_calibration.json').read_text())
 carbon=json.loads((reports/'noaa_gcp_carbon_hindcast.json').read_text())
 temp=json.loads((reports/'nasa_temperature_hindcast.json').read_text())
 ensemble=json.loads((reports/'multibox_ensemble.json').read_text())
 metrics={
  'ocean_sink':(sink['calibration']['ocean']['holdout_mae_gtc_per_year'],sink['calibration']['ocean']['baseline_mae_gtc_per_year']),
  'terrestrial_sink':(sink['calibration']['land']['holdout_mae_gtc_per_year'],sink['calibration']['land']['baseline_mae_gtc_per_year']),
  'atmospheric_co2':(carbon['holdout_mae_ppm_per_year'],carbon['training_mean_growth_baseline_mae_ppm_per_year']),
  'temperature_conditional':(temp['holdout_mae_c'],temp['training_mean_baseline_mae_c'])
 }
 skill={}
 for name,(error,baseline) in metrics.items():
  if not all(math.isfinite(x) and x>=0 for x in (error,baseline)) or baseline<=0:raise ValueError('Invalid metrics for '+name)
  skill[name]={'mae':error,'baseline_mae':baseline,'skill_fraction':1-error/baseline,'beats_baseline':error<baseline}
 result={
  'status':'empirical_skill_gated',
  'holdout_skill':skill,
  'all_tested_components_beat_baselines':all(x['beats_baseline'] for x in skill.values()),
  'multibox_mass_conservation':ensemble['carbon_conservation_verified'],
  'multibox_parameters_jointly_calibrated':False,
  'independent_millennial_interval_coverage_tested':False,
  'millennial_probabilities_validated':False,
  'scientific_status':'research prototype; conditional historical tests only',
  'action_required':['Improve terrestrial flux model with independently observed climate and land-use drivers','Jointly calibrate multibox exchange rates with ocean and terrestrial stocks','Validate horizon-dependent uncertainty on withheld periods and paleoclimate evidence']
 }
 (reports/'scientific_skill_gate.json').write_text(json.dumps(result,indent=2))
 print(json.dumps(result,indent=2))
 return result
if __name__=='__main__':evaluate()
