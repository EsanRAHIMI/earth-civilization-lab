"""Unified six-sector empirical skill and readiness scorecard.

Never equates successful CI, coverage, or lagged association with validated
millennial prediction. Reports actual temporal holdout and baseline comparisons.
"""
import json,pathlib,math
SECTORS=('climate','energy','water','food','demography','economy')
RELATION_SECTOR={'population':'demography'}
def run(root='.'):
 root=pathlib.Path(root)
 def read(path):
  p=root/path
  return json.loads(p.read_text()) if p.exists() else None
 coverage=read('reports/calibration_readiness.json')
 relations=read('reports/cross_sector_relationships.json')
 flux=read('reports/joint_physical_fit_skill_gate.json')
 if coverage is None or relations is None:raise FileNotFoundError('Observed panel and historical sector holdout reports are required')
 scores={s:{'sector':s,'data_coverage':None,'holdout_tests':[],'status':'not_validated','millennial_validated':False} for s in SECTORS}
 for x in coverage.get('sectors',[]):
  if x['sector'] in scores:scores[x['sector']]['data_coverage']=x['coverage_fraction']
 for r in relations.get('relations',[]):
  sector=RELATION_SECTOR.get(r['sector'],r['sector'])
  if sector not in scores:continue
  if r['status']!='temporal_holdout':
   scores[sector]['holdout_tests'].append({'status':r['status'],'n_train':r.get('n_train'),'n_test':r.get('n_test')});continue
  model=r['model']['smape_percent'];baseline=r['persistence_baseline']['smape_percent']
  scores[sector]['holdout_tests'].append({'target':r['target'],'metric':'smape_percent','model':model,'baseline':baseline,'beats_baseline':model<baseline,'test_period':'2019-2023','causal':False})
 if flux:
  for k,v in flux.get('comparisons',{}).items():
   scores['climate']['holdout_tests'].append({'target':k+'_carbon_sink','metric':'mae_gtc_per_year','model':v['model_mae'],'baseline':v['baseline_mae'],'beats_baseline':v['passes'],'test_period':'2015-2024','conditioned_on_observed_co2':True})
 for sector,entry in scores.items():
  tests=entry['holdout_tests'];evaluated=[x for x in tests if 'beats_baseline' in x]
  entry['tests_evaluated']=len(evaluated)
  entry['tests_beating_baseline']=sum(x['beats_baseline'] for x in evaluated)
  entry['status']='historical_skill_pass' if evaluated and all(x['beats_baseline'] for x in evaluated) else ('historical_skill_fail' if evaluated else 'no_evaluated_holdout')
  entry['ready_for_1000_year_forecast']=False
 report={'status':'six_sector_historical_evidence_audited','sectors':scores,'all_sectors_historical_skill_pass':all(x['status']=='historical_skill_pass' for x in scores.values()),'1000_year_forecast_validated':False,'limitations':['Country-level panel is not a dynamically coupled global Earth-system model','Energy has no dedicated independent out-of-sample sector test in this report','One-year lag tests cannot validate 1000-year projections','Missing observations are not imputed','Causal intervention effects are not identified']}
 out=root/'reports';out.mkdir(exist_ok=True)
 (out/'six_sector_evidence_scorecard.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
