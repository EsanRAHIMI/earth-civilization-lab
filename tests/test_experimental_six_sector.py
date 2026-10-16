import math,unittest
from src.experimental_six_sector_engine import SECTORS,step,ensemble
from src.spatial_coverage_aggregation import aggregate
class SixSectorTests(unittest.TestCase):
 def test_six_sector_coupling(self):
  initial={s:0. for s in SECTORS};initial["energy"]=1.
  next_state=step(initial)
  self.assertGreater(next_state["climate"],0)
  self.assertGreater(next_state["economy"],0)
  self.assertEqual(len(next_state),6)
 def test_reproducible_sensitivity(self):
  s={k:0.1 for k in SECTORS}
  self.assertEqual(ensemble(s,years=3,members=10,seed=3),ensemble(s,years=3,members=10,seed=3))
 def test_reject_nonfinite(self):
  with self.assertRaises(ValueError):step({s:math.nan for s in SECTORS})
 def test_area_weight(self):
  cells=[{"latitude":0,"longitude_width_deg":180,"latitude_height_deg":20,"value":10},{"latitude":0,"longitude_width_deg":180,"latitude_height_deg":20,"value":20}]
  self.assertAlmostEqual(aggregate(cells)["area_weighted_mean"],15)
 def test_missingness(self):
  cells=[{"latitude":0,"longitude_width_deg":180,"latitude_height_deg":20,"value":10},{"latitude":0,"longitude_width_deg":180,"latitude_height_deg":20,"value":None}]
  self.assertIsNone(aggregate(cells)["area_weighted_mean"])
if __name__=="__main__":unittest.main()
