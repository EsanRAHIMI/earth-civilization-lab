"""Conservative evidence gate for joint physical carbon-box inverse fitting.

An effective rate estimate is NOT a validated physical reservoir calibration
when any out-of-sample target loses to a training-only mean baseline.
"""
import json,pathlib
def run(root='.'):
 root=pathlib.Path(root)
 fit=json.loads((root/'reports/constrained_joint_physical_fit.json').read_text())
 holdout=fit['holdout']
 comparisons={k:{'model_mae':v['holdout_mae_gtc_year'],'baseline_mae':v['baseline_mae_gtc_year'],'passes':v['holdout_mae_gtc_year']<v['baseline_mae_gtc_year']} for k,v in holdout.items()}
 passed=all(x['passes'] for x in comparisons.values())
 report={'status':'pass_effective_flux_holdouts' if passed else 'fail_effective_flux_holdouts','joint_physical_fit_accepted':passed,'all_targets_beat_baseline':passed,'comparisons':comparisons,'full_reservoir_calibration_verified':False,'warning':'Even a pass is not independent physical identification. The current fit uses observed future atmospheric CO2, and missing reservoir stocks prevent internal turnover identification.'}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'joint_physical_fit_skill_gate.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
