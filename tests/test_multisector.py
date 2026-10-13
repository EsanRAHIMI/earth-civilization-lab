import unittest,tempfile,json,pathlib,hashlib
from src.multisector import collect,INDICATORS
def metadata():
 return json.dumps([{'pages':1},[{'id':f'X{i:02d}','iso2Code':'XX','region':{'id':'ECS','value':'Region'},'name':f'Country {i}','incomeLevel':{'value':'Low'}} for i in range(200)]]).encode()
class MultiSectorTests(unittest.TestCase):
 def test_real_format_and_missingness(self):
  def fake(url):
   if '/indicator/' not in url:return metadata()
   code=url.split('/indicator/')[1].split('?')[0]
   return json.dumps([{'pages':1},[{'countryiso3code':'X00','date':'2020','value':1.2},{'countryiso3code':'USA','date':'2021','value':None}]]).encode()
  with tempfile.TemporaryDirectory() as d:
   m=collect(d,fake)
   self.assertEqual(m['total_observations'],len(INDICATORS))
   self.assertTrue(all(x['observed']==1 for x in m['quality']))
   self.assertFalse(m['independent_source_validation'])
 def test_duplicate_rejected(self):
  def fake(url):
   if '/indicator/' not in url:return metadata()
   x={'countryiso3code':'USA','date':'2020','value':1}
   return json.dumps([{'pages':1},[x,x]]).encode()
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):collect(d,fake)
 def test_nonfinite_rejected(self):
  def fake(url):
   if '/indicator/' not in url:return metadata()
   return json.dumps([{'pages':1},[{'countryiso3code':'USA','date':'2020','value':'NaN'}]]).encode()
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):collect(d,fake)
if __name__=='__main__':unittest.main()
