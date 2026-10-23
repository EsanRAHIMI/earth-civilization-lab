"""Offline public research software quality gates (Python 3.11+)."""
import json
import pathlib
import tomllib
import unittest

ROOT=pathlib.Path(__file__).resolve().parents[1]

class ResearchCommunityQualityTests(unittest.TestCase):
 def test_machine_readable_citation_and_project_metadata(self):
  citation=(ROOT/"CITATION.cff").read_text()
  self.assertIn("cff-version: 1.2.0",citation)
  self.assertIn("repository-code:",citation)
  self.assertNotIn("zenodo.1234567",citation)
  project=tomllib.loads((ROOT/"pyproject.toml").read_text())["project"]
  self.assertEqual(project["license"],"Apache-2.0")
  self.assertIn("earth",project["name"])
  metadata=json.loads((ROOT/"codemeta.json").read_text())
  self.assertTrue(metadata["codeRepository"].startswith("https://github.com/"))
 def test_contribution_security_and_research_docs_exist(self):
  for path in ("LICENSE","CONTRIBUTING.md","CODE_OF_CONDUCT.md","SECURITY.md",
               "docs/REPRODUCIBILITY.md","docs/RESEARCH_ROADMAP.md",
               ".github/CODEOWNERS",".github/PULL_REQUEST_TEMPLATE.md",
               ".github/ISSUE_TEMPLATE/bug.yml",".github/ISSUE_TEMPLATE/science.yml"):
   with self.subTest(path=path):
    self.assertTrue((ROOT/path).is_file())
    self.assertGreater((ROOT/path).stat().st_size,100)
 def test_readme_states_current_research_limitations(self):
  text=(ROOT/"README.md").read_text().lower()
  for phrase in ("not a validated","reproduc","contribut","cite"):
   with self.subTest(phrase=phrase):self.assertIn(phrase,text)
 def test_gitignore_blocks_raw_and_secrets(self):
  text=(ROOT/".gitignore").read_text()
  for line in (".env","*.nc","data/independent_raw/","reports/","web/model/"):
   self.assertIn(line,text)
 def test_pr_ci_has_no_external_provider_secrets_or_retrieval(self):
  workflow=(ROOT/".github/workflows/research-quality.yml").read_text()
  self.assertIn("pull_request:",workflow)
  self.assertIn("contents: read",workflow)
  self.assertNotIn("EARTHDATA_TOKEN",workflow)
  self.assertNotIn("src.pipeline fetch",workflow)
 def test_scientific_releases_fail_closed(self):
  from src.scientific_release_gate_v2 import GATES,evaluate_reports
  report=evaluate_reports({"status":"source_bytes_and_observation_schema_verified",
        "panel_sha256":"a"*64,"sources":[{"id":x} for x in range(10)]},{"metrics":{}})
  self.assertTrue(report["gates"][GATES[0]])
  self.assertFalse(report["gates"][GATES[2]])
  self.assertFalse(report["scenario_enabled"])

if __name__=="__main__":unittest.main()
