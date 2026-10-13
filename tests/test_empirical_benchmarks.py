import unittest,tempfile,pathlib,csv,json,hashlib
from src.empirical_benchmarks import predict,evaluate
class RollingTests(unittest.TestCase):
 def test_predict_methods(self):
  d={y:float(y-2000) for y in range(2000,2016)}
  self.assertEqual(predict(d,'last'),15)
  self.assertEqual(predict(d,'drift5'),16)
  self.assertEqual(predict(d,'mean5'),13)
 def test_future_data_cannot_leak(self):
  a={y:float(y) for y in range(2000,2016)}
  b={**a,2020:1e12}
  for method in ('last','mean5','drift5'):
   self.assertEqual(predict(a,method),predict({y:v for y,v in b.items() if y<2016},method))
 def test_evaluate_from_real_format(self):
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d);(root/'data').mkdir()
   p=root/'data/observations.csv'
   with p.open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['iso3','year','indicator','value']);w.writeheader()
    for y in range(2000,2025):w.writerow({'iso3':'USA','year':y,'indicator':'population','value':y*10})
   (root/'data/manifest.json').write_text(json.dumps({'panel_sha256':hashlib.sha256(p.read_bytes()).hexdigest()}))
   r=evaluate(root);self.assertEqual(r['n_prediction_rows'],27)
   self.assertEqual(next(x['mae'] for x in r['summary'] if x['method']=='drift5'),0)
if __name__=='__main__':unittest.main()
