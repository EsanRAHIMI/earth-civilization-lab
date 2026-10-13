"""Fail-closed operational scientific readiness gate. Distinguishes pipeline
execution, external target backtesting and genuine independent model validation.
"""
import argparse,json,pathlib,datetime,math
REQUIRED=('historical_calibration.json','cross_sector_relationships.json','physical_validation_audit.json','bitcoin_primary_calibration.json','independent_source_evidence.json','independent_population_consistency.json','gcp_independent_target_calibration.json')
def audit(root):
 root=pathlib.Path(root);folder=root/'reports'
 reports={};missing=[]
 for name in REQUIRED:
  p=folder/name
  if not p.is_file():missing.append(name);continue
  reports[name]=json.loads(p.read_text())
 checks={}
 checks['all_reports_present']=not missing
 sources=reports.get('independent_source_evidence.json',{})
 checks['gcp_sources_downloaded']=len(sources.get('sources',[]))==2 and all(x.get('status')=='downloaded' for x in sources.get('sources',[]))
 demo=reports.get('independent_population_consistency.json',{})
 checks['cross_source_demography_measured']=demo.get('observations',0)>=100 and demo.get('countries',0)>=30
 gcp=reports.get('gcp_independent_target_calibration.json',{})
 checks['gcp_fossil_co2_holdout_measured']=gcp.get('n_test',0)>=100 and gcp.get('test_countries',0)>=30 and isinstance(gcp.get('holdout_model'),dict)
 btc=reports.get('bitcoin_primary_calibration.json',{})
 links=btc.get('relations',[])
 checks['bitcoin_six_sector_backtests_present']=len(links)==6 and all(x.get('status')=='held_out_global_annual_test' for x in links)
 checks['independent_upstream_provenance_verified']=False
 checks['independent_water_food_economy_validation']=False
 checks['physical_climate_calibrated_to_temperature']=False
 checks['bitcoin_physical_energy_emissions_validated']=False
 checks['millennium_forecast_scientifically_validated']=False
 operational=all(checks[k] for k in ('all_reports_present','gcp_sources_downloaded','cross_source_demography_measured','gcp_fossil_co2_holdout_measured','bitcoin_six_sector_backtests_present'))
 out={'generated_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operational_pipeline_pass':operational,'scientific_validation_pass':False,'checks':checks,'missing_reports':missing,'gcp_holdout_metrics':gcp.get('holdout_model'),'gcp_baseline_metrics':gcp.get('training_mean_baseline'),'bitcoin_sector_results':[{k:r.get(k) for k in ('sector','status','n_train','n_test','btc_improves_mae')} for r in links],'critical_notes':['Operational completion is not causal or independent upstream scientific validation','A target published by GCP differs from total GHG; never transfer coefficients','Bitcoin annual regressions are contemporaneous, very short, and not forward predictions','No 1000-year calibrated forecast can be certified']}
 folder.mkdir(exist_ok=True)
 (folder/'operational_readiness.json').write_text(json.dumps(out,indent=2))
 print(json.dumps(out,indent=2))
 if not operational:raise RuntimeError('Required empirical evidence or backtests missing; fail closed')
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');audit(p.parse_args().root)
