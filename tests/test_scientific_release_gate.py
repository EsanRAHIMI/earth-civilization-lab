import unittest
from src.scientific_release_gate_v2 import GATES, evaluate_reports

class ScientificReleaseGateTests(unittest.TestCase):
    def test_green_data_integrity_does_not_certify_earth_model(self):
        lineage={"status":"source_bytes_and_observation_schema_verified",
                 "panel_sha256":"a"*64,
                 "sources":[{"name":str(i)} for i in range(11)]}
        lagged={"metrics":{"climate":{"evaluated_folds":10,"positive_skill_folds":10,
                                     "positive_lower_ci_folds":10},
                           "water":{"evaluated_folds":10,"positive_skill_folds":10,
                                     "positive_lower_ci_folds":10},
                           "food":{"evaluated_folds":10,"positive_skill_folds":10,
                                    "positive_lower_ci_folds":10}}}
        report=evaluate_reports(lineage,lagged)
        self.assertTrue(report["gates"][GATES[0]])
        self.assertFalse(any(report["gates"][k] for k in GATES[1:]))
        self.assertFalse(report["scenario_enabled"])
        self.assertFalse(report["accepted_global_digital_twin"])
    def test_missing_immutable_sources_fails_data_gate(self):
        self.assertFalse(evaluate_reports({"status":"unverified","sources":[]}, {})["gates"][GATES[0]])
if __name__=="__main__":unittest.main()
