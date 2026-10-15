import math, tempfile, unittest
from pathlib import Path
from src.coupled_six_sector_research import SECTORS,simulate,step,spatial_country_panel,independent_holdout

class SixSectorResearchTests(unittest.TestCase):
 def test_deterministic_ensemble(self):
  a=simulate(years=12,replicates=20,scenario={'shock_std':.02})
  b=simulate(years=12,replicates=20,scenario={'shock_std':.02})
  self.assertEqual(a,b)
  self.assertEqual(set(a['sectors']),set(SECTORS))
  for points in a['sectors'].values():
   self.assertEqual(len(points),13)
   for p in points:self.assertTrue(0<p['p05']<=p['median']<=p['p95'])
 def test_cross_sector_coupling(self):
  base={s:1 for s in SECTORS}
  changed={**base,'energy':1.5}
  self.assertNotEqual(step(base)['climate'],step(changed)['climate'])
  self.assertNotEqual(step(base)['economy'],step(changed)['economy'])
 def test_no_fabricated_spatial_or_skill(self):
  with tempfile.TemporaryDirectory() as d:
   self.assertEqual(spatial_country_panel(d)['status'],'missing_world_bank_observations')
   self.assertFalse(independent_holdout(d).get('validated_coupled_model',False))
 def test_invalid_input(self):
  with self.assertRaises(ValueError):simulate(initial={s:float('nan') for s in SECTORS})
  with self.assertRaises(ValueError):simulate(years=0)
if __name__=='__main__':unittest.main()
