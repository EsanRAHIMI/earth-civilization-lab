"""Regression tests for observed-only data audit and leakage-resistant lag models."""
import csv
import hashlib
import json
import math
import tempfile
import unittest
from pathlib import Path
from src.science_data_audit import inspect_observations
from src.sector_lagged_research import cohort, fitted, execute, read_full_panel
from src.multisector import INDICATORS

class DataContractTests(unittest.TestCase):
    def make_fixture(self, root):
        data=root/"data"; raw=data/"multisector_raw";raw.mkdir(parents=True)
        body=b'{"test":"fixture"}'
        (raw/"country_metadata.json").write_bytes(body)
        (raw/"food_production_index.json").write_bytes(body)
        code,unit,sector=INDICATORS["food_production_index"]
        with (data/"multisector_observations.csv").open("w",newline="") as stream:
            writer=csv.DictWriter(stream,fieldnames=["country","year","indicator","sector","value","unit","source_code"])
            writer.writeheader()
            writer.writerow({"country":"AAA","year":2018,"indicator":"food_production_index","sector":sector,"value":99,"unit":unit,"source_code":code})
            writer.writerow({"country":"AAA","year":2019,"indicator":"food_production_index","sector":sector,"value":100,"unit":unit,"source_code":code})
        sha=hashlib.sha256(body).hexdigest()
        (data/"multisector_manifest.json").write_text(json.dumps({
            "countries":["AAA"],
            "panel_sha256":hashlib.sha256((data/"multisector_observations.csv").read_bytes()).hexdigest(),
            "sources":[{"indicator":"country_metadata","sha256":sha,"url":"fixture"},
                       {"indicator":"food_production_index","sha256":sha,"url":"fixture"}]
        }))
    def test_lineage_explicit_upstream_and_annual_gaps(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.make_fixture(root)
            report=inspect_observations(root)
            food=report["indicators"]["food_production_index"]
            self.assertEqual(food["consecutive_annual_pairs"],1)
            self.assertIn("FAOSTAT",food["underlying_source_lineage"])
            self.assertFalse(report["independent_provider_validation"])
    def test_source_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.make_fixture(root)
            (root/"data/multisector_raw/food_production_index.json").write_text("tampered")
            with self.assertRaisesRegex(ValueError,"hash mismatch"):
                inspect_observations(root)
    def test_source_units_mismatch_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);self.make_fixture(root)
            obs=root/"data/multisector_observations.csv"
            obs.write_text(obs.read_text().replace("index_2014_2016_100","fake_unit"))
            manifest=root/"data/multisector_manifest.json"
            report=json.loads(manifest.read_text())
            report["panel_sha256"]=hashlib.sha256(obs.read_bytes()).hexdigest()
            manifest.write_text(json.dumps(report))
            with self.assertRaisesRegex(ValueError,"Unit/source/sector mismatch"):
                inspect_observations(root)

class LaggedResearchTests(unittest.TestCase):
    def test_only_exact_prior_year_features(self):
        panel={}
        for year in range(2000,2006):
            panel[("AAA",year)]={"food_production_index":100+year-2000,
                                  "cereal_yield":2500+year-2000,
                                  "real_gdp_per_capita":10000+year-2000,
                                  "population":1000000+year-2000}
        rows=cohort(panel,"food")
        self.assertEqual(rows[0][1],2002)
        self.assertAlmostEqual(rows[0][2][0],math.log(101))
        self.assertAlmostEqual(rows[0][2][1],math.log(100))
        self.assertAlmostEqual(rows[0][3],math.log(102))
        del panel[("AAA",2001)]["food_production_index"]
        rows=cohort(panel,"food")
        self.assertTrue(all(r[1]!=2002 for r in rows))
    def test_candidate_persistence_and_ridge_anchor(self):
        samples=[]
        for i in range(30):
            x=(math.log(100+i),math.log(99+i),math.log(60+i),math.log(10000+i),math.log(50000+i))
            samples.append(("C"+str(i),2012,x,x[0]+.02))
        baseline=fitted(samples,"persistence")
        self.assertEqual(baseline(samples[0][2]),samples[0][2][0])
        self.assertTrue(math.isfinite(fitted(samples,"own_ridge",10)(samples[0][2])))
    def test_folds_fail_closed_on_insufficient_data(self):
        rows=[("C"+str(i),2020,(1.,.99,2.,3.,4.),1.02) for i in range(8)]
        self.assertEqual(execute(rows,1103,2013,2016,2019)["status"],"insufficient_data")
if __name__=="__main__":unittest.main()
