import json,tempfile,unittest
from pathlib import Path
from src.coupled_operational_verdict import evaluate

class CoupledOperationalVerdictTests(unittest.TestCase):
 def populate(self,root):
  folder=root/"evidence";folder.mkdir(parents=True)
  src={
   "hadcrut5_independent_climate_test.json":{
    "status":"independent_institution_HadCRUT5_source_evaluation",
    "metrics":{"joint_physics":{"mae_c":.01},"frozen_train_last":{"mae_c":.5},
               "train_only_linear_trend":{"mae_c":.4}}},
   "climate_joint_temperature_ocean_hindcast.json":{
    "status":"joint_NOAA_0_2000m_NASA_surface_training_only_hindcast"},
   "country_wheat_no_future_weather_audit.json":{
    "status":"exploratory_country_AND_time_disjoint_crop_audit",
    "issued_at":"January 1 of target harvest year",
    "folds":[{"country_disjoint":True,"train_before_test":True,
              "beats_persistence":True} for i in range(3)]}
  }
  for k,v in src.items():(folder/k).write_text(json.dumps(v))
 def test_even_optimistic_individual_results_cannot_certify_global_coupling(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.populate(root)
   v=evaluate(root)
   self.assertEqual(v["status"],"operational_release_blocked")
   self.assertTrue(v["tests"]["met_office_climate_beats_strongest_baseline"])
   self.assertTrue(v["tests"]["crop_beats_baseline_in_all_geographies"])
   self.assertFalse(v["scientific_scenario_forecast_enabled"])
   self.assertFalse(v["operational_global_decisions_authorized"])
 def test_invalid_country_holdout_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.populate(root)
   p=root/"evidence/country_wheat_no_future_weather_audit.json"
   d=json.loads(p.read_text());d["folds"][0]["country_disjoint"]=False
   p.write_text(json.dumps(d))
   with self.assertRaisesRegex(ValueError,"holdout"):
    evaluate(root)
 def test_missing_authoritative_reference_fails_closed(self):
  with tempfile.TemporaryDirectory() as tmp:
   with self.assertRaises(FileNotFoundError):evaluate(Path(tmp))
if __name__=="__main__":unittest.main()
