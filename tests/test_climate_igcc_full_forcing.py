import csv,io,unittest
from src.climate_igcc_full_forcing import decode_igcc,projected_components
from src.climate_free_running_forecast import START,TRAIN_END,TEST_END

class IGCCPhysicalClimateTests(unittest.TestCase):
 def test_exactly_reconciled_forcing(self):
  stream=io.StringIO()
  writer=csv.DictWriter(stream,fieldnames=["timebound_lower","timebound_upper","anthro","solar","volcanic","total","aerosol"])
  writer.writeheader()
  for y in range(START,TEST_END+1):
   writer.writerow({"timebound_lower":y,"timebound_upper":y+1,
     "anthro":1.1+.02*(y-START),"solar":.1,"volcanic":.2,
     "total":1.4+.02*(y-START),"aerosol":-1.})
  rows=decode_igcc(stream.getvalue().encode())
  self.assertEqual(len(rows),45)
  self.assertAlmostEqual(rows[2014]["total"],2.08)
 def test_reject_unbalanced_physical_forcing(self):
  stream=io.StringIO()
  writer=csv.DictWriter(stream,fieldnames=["timebound_lower","timebound_upper","anthro","solar","volcanic","total","aerosol"])
  writer.writeheader()
  writer.writerow({"timebound_lower":1980,"timebound_upper":1981,
    "anthro":1,"solar":.1,"volcanic":.2,"total":9,"aerosol":-1})
  with self.assertRaisesRegex(ValueError,"reconcile"):
   decode_igcc(stream.getvalue().encode())
 def test_future_forcing_cannot_contaminate_extrapolation(self):
  full={y:{"anthro":1+.03*(y-START),"solar":.1,"volcanic":.2,
     "total":1.3+.03*(y-START)} for y in range(START,TEST_END+1)}
  training={y:full[y] for y in range(START,TRAIN_END+1)}
  forecast,_=projected_components(training,TEST_END)
  for y in range(TRAIN_END+1,TEST_END+1):
   full[y]["anthro"]=1000.
   full[y]["solar"]=-1000.
   full[y]["volcanic"]=-1000.
  second,_=projected_components({y:full[y] for y in range(START,TRAIN_END+1)},TEST_END)
  self.assertEqual(forecast,second)
if __name__=="__main__":unittest.main()
