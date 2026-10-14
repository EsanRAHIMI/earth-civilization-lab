"""Strict scientific acceptance gate, separate from successful data collection.

Nonzero exit if any observed physical sink fails the training-mean baseline,
or independent carbon-stock data are missing. Not a CI infrastructure failure.
"""
import json,pathlib,sys
def main(root='.'):
 root=pathlib.Path(root)
 flux=json.loads((root/'reports/joint_physical_fit_skill_gate.json').read_text())
 stock=json.loads((root/'reports/independent_carbon_stock_import.json').read_text())
 issues=[]
 if not flux.get('joint_physical_fit_accepted',False):
  issues.append('Independent ocean/land holdout skill not both above baseline')
 if stock.get('status')!='ready_for_joint_stock_calibration':
  issues.append('Four independent annual global carbon stock series unavailable')
 result={'physical_calibration_accepted':not issues,'failures':issues,'flux_gate':flux.get('status'),'stock_gate':stock.get('status')}
 print(json.dumps(result,indent=2))
 return 1 if issues else 0
if __name__=='__main__':sys.exit(main())
