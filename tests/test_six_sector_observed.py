import math,unittest
from src.six_sector_observed_hindcast import fit,evaluate,samples,FEATURES
from src.six_sector_conformal_coverage import qceil
class ObservedTests(unittest.TestCase):
 def test_six_outcomes_fit(self):
  rows=[]
  for i in range(50):
   x=[math.log(1+i*.01+j*.2) for j in range(6)]
   y=[v+.01 for v in x]
   rows.append(("C%03d"%i,2000,x,y))
  predict,params=fit(rows,10.)
  self.assertEqual(len(predict(rows[0][2])),6)
  self.assertEqual(len(evaluate(rows,predict)),6)
 def test_conformal_quantile(self):
  self.assertEqual(qceil([1,2,3,4,5],.8),5)
 def test_complete_case_no_imputation(self):
  prev={k:1. for k in FEATURES};cur=dict(prev)
  panel={("AAA",2000):prev,("AAA",2001):cur}
  self.assertEqual(len(samples(panel)),1)
  del cur[FEATURES[0]]
  self.assertEqual(len(samples(panel)),0)
if __name__=="__main__":unittest.main()
