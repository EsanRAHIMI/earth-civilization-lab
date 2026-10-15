"""Verify NOAA network outage fallback uses real versioned observations."""
import csv,pathlib,tempfile,unittest,urllib.error
from unittest.mock import patch
from src.noaa_ocean_heat_import import run
class TestNoaaOutage(unittest.TestCase):
 def test_outage_uses_versioned_observations(self):
  with tempfile.TemporaryDirectory() as t:
   root=pathlib.Path(t);ref=root/'data/reference/noaa_world_ocean_heat_2005_2025.csv'
   ref.parent.mkdir(parents=True)
   ref.write_bytes((pathlib.Path(__file__).resolve().parents[1]/'data/reference/noaa_world_ocean_heat_2005_2025.csv').read_bytes())
   with patch('src.noaa_ocean_heat_import.get',side_effect=urllib.error.URLError('simulated outage')):
    report=run(root)
   self.assertTrue(report['used_repository_noaa_reference'])
   self.assertEqual(report['years'],21)
   rows=list(csv.DictReader((root/'data/independent_raw/ocean_heat_content_annual.csv').open()))
   self.assertEqual(len(rows),21)
   self.assertEqual(rows[0]['year'],'2005')
   self.assertEqual(rows[-1]['year'],'2025')
   self.assertAlmostEqual(float(rows[0]['heat_0_700_zj']),84.12)
   self.assertAlmostEqual(float(rows[0]['heat_0_2000_zj']),101.71)
if __name__=='__main__':unittest.main()
