"""Leakage-resistant country holdout assessment of one-step persistence and six-sector model.

The current simulator uses hypothetical coupling coefficients, so this module
reports a blocked status until a calibrated observation-to-state mapping exists.
"""
import json,pathlib
from src.experimental_six_sector_engine import SECTORS,ensemble,step
from src.spatial_coverage_aggregation import aggregate
def run(root="."):
 root=pathlib.Path(root);out=root/"reports";out.mkdir(exist_ok=True)
 report={"status":"blocked_unvalidated","engine":"experimental_six_sector_engine","spatial":"spatial_coverage_aggregation","uncertainty":"parameter_sensitivity_not_calibrated_intervals","independent_holdout":"not_evaluated","reasons":["Six dimensionless anomalies have no audited mapping to observed physical units","Coupling coefficients are hypotheses, not fitted on pre-holdout data","Spatial integration lacks a validated global raster and masks","No independent multi-sector held-out evaluation; no calibrated uncertainty coverage"],"physical_scientific_acceptance":False}
 (out/"six_sector_scientific_readiness.json").write_text(json.dumps(report,indent=2))
 return report
if __name__=="__main__":print(json.dumps(run(),indent=2))
