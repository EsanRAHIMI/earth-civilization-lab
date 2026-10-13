import unittest, tempfile, json, pathlib
from src.pipeline import acquire, evaluate
class PipelineTests(unittest.TestCase):
 def mock(self,url):
  code=url.split('/indicator/')[1].split('?')[0]
  entries=[{'countryiso3code':iso,'date':str(y),'value':float(y),'obs_status':''} for iso in ['USA','ARE'] for y in range(2000,2025)]
  return json.dumps([{'pages':1},entries]).encode()
 def test_acquire(self):
  with tempfile.TemporaryDirectory() as d:
   m=acquire(d, self.mock);self.assertEqual(m['rows'],200)
 def test_evaluate(self):
  with tempfile.TemporaryDirectory() as d:
   acquire(d,self.mock);r=evaluate(d);self.assertEqual(r['groups_evaluated'],8)
 def test_bad_api(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):acquire(d,lambda u:b'{}')
if __name__=='__main__':unittest.main()
