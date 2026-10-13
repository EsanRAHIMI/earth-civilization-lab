import unittest,random,math,tempfile,pathlib
from src.physical_core import State,Policy,step,run,main,POLICIES
class PhysicalTests(unittest.TestCase):
 def test_carbon_mass_conservation_1000_years(self):
  for p in POLICIES.values():
   s=State();initial=s.carbon_total()
   for _ in range(1000):
    s,flows,share=step(s,p)
    self.assertAlmostEqual(s.carbon_total(),initial,places=6)
    p=Policy(**{**p.__dict__,'fossil_share':share})
 def test_zero_fossil_has_zero_emissions(self):
  s=State();p=Policy('zero',0,0,0,0);n,f,_=step(s,p)
  self.assertEqual(f['co2_emissions_gt'],0)
 def test_extraction_never_exceeds_reserves(self):
  s=State(fossil_remaining_gtc=0.01);p=Policy('high',1,0,0,0)
  n,f,_=step(s,p);self.assertAlmostEqual(n.fossil_remaining_gtc,0)
  self.assertLessEqual(f['extracted_gtc'],0.01)
 def test_no_negative_stocks_randomized(self):
  r=random.Random(13)
  for i in range(100):
   s=State(atmosphere_gtc=r.uniform(100,1500),ocean_gtc=r.uniform(1000,50000),land_gtc=r.uniform(100,3000),fossil_remaining_gtc=r.uniform(0,5000))
   p=Policy('random',r.random(),r.random()*0.1,r.uniform(-0.01,0.02),r.uniform(-0.01,0.02))
   n,f,_=step(s,p)
   self.assertAlmostEqual(s.carbon_total(),n.carbon_total(),places=6)
   self.assertGreaterEqual(n.atmosphere_gtc,0)
 def test_report(self):
  with tempfile.TemporaryDirectory() as d:
   main(d,40)
   self.assertTrue((pathlib.Path(d)/'reports/physical_core_trajectories.csv').exists())
if __name__=='__main__':unittest.main()
