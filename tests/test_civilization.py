import unittest,tempfile
from src.civilization import simulate,experiment,SCENARIOS
class TestCivilization(unittest.TestCase):
 def test_reproducibility(self):
  self.assertEqual(simulate(SCENARIOS['baseline'],7,30),simulate(SCENARIOS['baseline'],7,30))
 def test_bounds(self):
  for policy in SCENARIOS.values():
   r=simulate(policy,2,300)
   self.assertTrue(0<=r['final']['wellbeing']<=1)
   self.assertTrue(0<=r['final']['ecosystem']<=1)
   self.assertTrue(r['final']['population']>=0)
 def test_scenario_outputs(self):
  with tempfile.TemporaryDirectory() as d:
   r=experiment(d,3,30)
   self.assertEqual(len(r['summary']),3)
   self.assertFalse(r['parameters_are_calibrated'])
 def test_no_claimed_probability(self):
  with tempfile.TemporaryDirectory() as d:
   r=experiment(d,2,10)
   self.assertFalse(r['survival_probability_claim_valid'])
if __name__=='__main__':unittest.main()
