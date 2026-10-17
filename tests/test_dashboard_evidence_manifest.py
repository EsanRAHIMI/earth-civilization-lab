import json,tempfile,unittest
from pathlib import Path
from src.build_dashboard_evidence import compose,PIPELINES

class PublicEvidenceManifestTests(unittest.TestCase):
 def make(self,folder):
  data={key:{"status":"completed","conclusion":"success",
             "updated_at":"2026-10-17T10:00:00Z",
             "html_url":"https://github.com/Example/repo/actions/runs/123"}
        for key in PIPELINES}
  (folder/"pipeline-runs.json").write_text(json.dumps(data))
 def test_unpublished_reports_stay_unavailable_and_forecast_stays_blocked(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.make(root)
   result=compose(root)
   self.assertEqual(result["readiness"],"OBSERVATORY_AND_RESEARCH_ONLY")
   self.assertFalse(result["forecast_scenarios_authorized"])
   self.assertEqual(result["evidence"]["grace"]["state"],"UNAVAILABLE")
   self.assertEqual(result["evidence"]["climate"]["state"],"UNAVAILABLE")
 def test_operational_verdict_requires_fail_closed_fields(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.make(root)
   (root/"coupled-verdict.json").write_text(json.dumps({
    "status":"bad","scientific_scenario_forecast_enabled":True,
    "operational_global_decisions_authorized":True}))
   with self.assertRaisesRegex(RuntimeError,"gate"):compose(root)
 def test_malformed_source_artifact_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);self.make(root)
   (root/"climate-external.json").write_text('{"not_a_scientific_report":true}')
   with self.assertRaisesRegex(ValueError,"Malformed"):compose(root)
if __name__=="__main__":unittest.main()
