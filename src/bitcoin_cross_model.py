"""Bitcoin is a separate global observed subsystem, not a country indicator.
Create explicit six-sector and physical-model linkage records without claiming
unidentified causal effects. Never silently impute missing Bitcoin history.
"""
import argparse,csv,datetime,hashlib,json,math,pathlib,collections
SECTORS=('climate','energy','water','food','demography','economy')
CHARTS=('market_price_usd','network_hashrate','confirmed_transactions','miners_revenue_usd')
def build(root):
 root=pathlib.Path(root);btc=root/'data/bitcoin_observations.csv'
 world=root/'data/multisector_manifest.json'
 if not btc.is_file() or not world.is_file():raise FileNotFoundError('Both observed Bitcoin and World Bank evidence are required')
 manifest=json.loads(world.read_text())
 rows=collections.defaultdict(list)
 with btc.open() as f:
  for r in csv.DictReader(f):
   name=r['indicator'];v=float(r['value'])
   if name not in CHARTS or not math.isfinite(v) or v<0:raise ValueError('invalid Bitcoin observation')
   stamp=datetime.datetime.fromisoformat(r['timestamp_utc'].replace('Z','+00:00'))
   if stamp.tzinfo is None:raise ValueError('Bitcoin timestamp must have timezone')
   rows[name].append((stamp,v))
 if set(rows)!=set(CHARTS):raise ValueError('Bitcoin series incomplete')
 stats={}
 for name in CHARTS:
  seq=sorted(rows[name]);dates=[d for d,v in seq]
  if len(set(dates))!=len(dates):raise ValueError('duplicate timestamps')
  stats[name]={'observations':len(seq),'first_utc':dates[0].isoformat(),'last_utc':dates[-1].isoformat(),'minimum':min(v for _,v in seq),'maximum':max(v for _,v in seq)}
 start=max(min(d for d,v in rows[k]) for k in CHARTS)
 end=min(max(d for d,v in rows[k]) for k in CHARTS)
 if start>end:raise ValueError('Bitcoin indicators have no overlapping time span')
 years=manifest['retrieval_years']
 overlap_years=[y for y in range(years[0],years[1]+1) if start.year<=y<=end.year]
 # No annual regression when overlap is insufficient; avoid attaching one global
 # time series to 216 countries as if it were independent country observations.
 links=[]
 for sector in SECTORS:
  links.append({'sector':sector,'bitcoin_parameter_group':'bitcoin_network_and_market','indicators':list(CHARTS),'role':'observed global contextual covariates only','estimated_effect':None,'calibrated':False,'causal_validated':False,'historical_overlap_years':overlap_years,'blocked_reason':'No comparable multi-year common annual panel with independent global variation; country duplication would be pseudoreplication'})
 links.append({'sector':'physical_carbon_core','bitcoin_parameter_group':'bitcoin_network_and_market','indicators':list(CHARTS),'role':'context only, no carbon or electricity flux inserted','estimated_effect':None,'calibrated':False,'causal_validated':False,'blocked_reason':'Hashrate does not measure energy, emissions, power mix or location. Requires independently measured electricity and carbon intensity.'})
 out={'status':'bitcoin_integrated_as_separate_observed_global_subsystem','bitcoin_manifest_sha256':hashlib.sha256((root/'data/bitcoin_manifest.json').read_bytes()).hexdigest(),'world_manifest_sha256':hashlib.sha256(world.read_bytes()).hexdigest(),'bitcoin_data_sha256':hashlib.sha256(btc.read_bytes()).hexdigest(),'bitcoin_series':stats,'joint_complete_series_window_utc':[start.isoformat(),end.isoformat()],'world_bank_years':years,'links':links,'bitcoin_effects_estimated':False,'bitcoin_used_to_modify_1000_year_predictions':False,'independent_validation':False,'warnings':['Bitcoin observations have global time index; no defensible country attribution from these series','Bitcoin price and miner revenue are financial, not physical energy units','No invented electricity or emissions conversion','Missing years remain missing; longer historical sources needed for statistical calibration']}
 dest=root/'reports';dest.mkdir(exist_ok=True)
 (dest/'bitcoin_cross_model_integration.json').write_text(json.dumps(out,indent=2))
 print(json.dumps({'status':out['status'],'bitcoin_series':stats,'world_bank_years':years,'link_count':len(links),'effects_estimated':False},indent=2))
 return out
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');build(p.parse_args().root)
