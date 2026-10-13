"""Auditable real Bitcoin network time series from Blockchain.com charts API.
No price forecasting, no synthetic data, no inference of electricity use from hashrate.
"""
import argparse,csv,datetime,hashlib,json,math,pathlib,time,urllib.request,urllib.error,socket
CHARTS={
 'market_price_usd':('market-price','USD_per_BTC'),
 'network_hashrate':('hash-rate','TH_per_second'),
 'confirmed_transactions':('n-transactions','transactions_per_day'),
 'miners_revenue_usd':('miners-revenue','USD_per_day'),
}
BASE='https://api.blockchain.info/charts/'
def request(url):
 for attempt in range(4):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0 research','Accept':'application/json'}),timeout=45) as r:return r.read()
  except urllib.error.HTTPError as e:
   if e.code not in (408,429,500,502,503,504) or attempt==3:raise
  except (TimeoutError,socket.timeout,urllib.error.URLError,ConnectionError):
   if attempt==3:raise
  time.sleep(2**attempt)
def parse_chart(body,name,unit):
 obj=json.loads(body)
 if not isinstance(obj,dict) or not isinstance(obj.get('values'),list):raise ValueError('invalid chart response: '+name)
 rows=[];seen=set()
 for point in obj['values']:
  if not isinstance(point,dict) or not isinstance(point.get('x'),(int,float)) or not isinstance(point.get('y'),(int,float)):raise ValueError('invalid point')
  ts=int(point['x']);value=float(point['y'])
  if not math.isfinite(value) or value<0 or ts in seen:raise ValueError('invalid/duplicate chart observation')
  seen.add(ts)
  rows.append({'timestamp_utc':datetime.datetime.fromtimestamp(ts,datetime.timezone.utc).isoformat(),'unix_timestamp':ts,'indicator':name,'value':value,'unit':unit})
 if not rows:raise ValueError('empty chart '+name)
 return sorted(rows,key=lambda r:r['unix_timestamp'])
def collect(root,fetcher=request,timespan='1year'):
 if timespan not in ('30days','1year','2years','3years'):raise ValueError('unsupported timespan')
 root=pathlib.Path(root);raw=root/'data'/'bitcoin_raw';raw.mkdir(parents=True,exist_ok=True)
 records=[];sources=[]
 for name,(chart,unit) in CHARTS.items():
  url=f'{BASE}{chart}?timespan={timespan}&format=json'
  body=fetcher(url);rows=parse_chart(body,name,unit)
  (raw/(name+'.json')).write_bytes(body)
  records.extend(rows)
  sources.append({'indicator':name,'url':url,'sha256':hashlib.sha256(body).hexdigest(),'observations':len(rows),'first_timestamp':rows[0]['timestamp_utc'],'last_timestamp':rows[-1]['timestamp_utc'],'retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
 out=root/'data'/'bitcoin_observations.csv'
 with out.open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['timestamp_utc','unix_timestamp','indicator','value','unit']);w.writeheader();w.writerows(sorted(records,key=lambda x:(x['indicator'],x['unix_timestamp'])))
 manifest={'status':'observed_only_not_forecast','source':'Blockchain.com Charts API','timespan_requested':timespan,'observations':len(records),'sources':sources,'panel_sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'climate_energy_link_validated':False,'bitcoin_electricity_consumption_measured':False,'limitations':['Hashrate is not measured energy consumption','Provider estimates may be revised and sampled','Market price is not a proxy for civilization wellbeing','No causal links to the six-sector model are estimated','Price/transactions are observations, not investment recommendations']}
 (root/'data'/'bitcoin_manifest.json').write_text(json.dumps(manifest,indent=2))
 print(json.dumps({'observations':len(records),'sources':sources,'empirically_calibrated':False},indent=2))
 return manifest
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--timespan',default='1year');a=p.parse_args();collect(a.root,timespan=a.timespan)
