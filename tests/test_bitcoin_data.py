import unittest,tempfile,json,hashlib,pathlib
from src.bitcoin_data import collect,parse_chart,CHARTS
class BitcoinDataTests(unittest.TestCase):
 def test_parse(self):
  data=json.dumps({'values':[{'x':1609459200,'y':100.0},{'x':1609545600,'y':105.0}]}).encode()
  r=parse_chart(data,'market_price_usd','USD_per_BTC')
  self.assertEqual(len(r),2);self.assertEqual(r[0]['value'],100)
 def test_duplicate_fails(self):
  data=json.dumps({'values':[{'x':1609459200,'y':1},{'x':1609459200,'y':2}]}).encode()
  with self.assertRaises(ValueError):parse_chart(data,'x','y')
 def test_real_format_audit(self):
  def fake(url):return json.dumps({'values':[{'x':1609459200,'y':1.0}]}).encode()
  with tempfile.TemporaryDirectory() as d:
   m=collect(d,fake)
   self.assertEqual(m['observations'],len(CHARTS))
   self.assertFalse(m['bitcoin_electricity_consumption_measured'])
   p=pathlib.Path(d)/'data/bitcoin_observations.csv'
   self.assertEqual(m['panel_sha256'],hashlib.sha256(p.read_bytes()).hexdigest())
 def test_negative_fails(self):
  with self.assertRaises(ValueError):parse_chart(json.dumps({'values':[{'x':1609459200,'y':-1}]}).encode(),'x','y')
if __name__=='__main__':unittest.main()
