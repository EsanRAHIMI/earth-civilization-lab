"""Leakage-controlled expanding-window, one-year-ahead benchmarks on observed WB panel.
No synthetic values. Results are descriptive retrospective errors, not prospective forecasts.
"""
import argparse,csv,json,math,pathlib,statistics
INDICATORS={'population','life_expectancy','gdp_growth','co2_per_capita'}
def predict(history,method):
 y=sorted(history)
 if len(y)<5:raise ValueError('insufficient training history')
 last=history[y[-1]]
 if method=='last':return last
 if method=='mean5':return statistics.mean(history[t] for t in y[-5:])
 if method=='drift5':
  # Annual linear drift over last 5 observations; missing years allowed but time accounted for
  recent=y[-5:];xs=[t-recent[0] for t in recent];vs=[history[t] for t in recent]
  xm=statistics.mean(xs);vm=statistics.mean(vs)
  den=sum((x-xm)**2 for x in xs)
  slope=sum((x-xm)*(v-vm) for x,v in zip(xs,vs))/den if den else 0
  return vs[-1]+slope
 raise ValueError(method)
def evaluate(root,start=2016,end=2024):
 root=pathlib.Path(root)
 manifest=json.loads((root/'data/manifest.json').read_text())
 import hashlib
 panel=root/'data/observations.csv'
 if hashlib.sha256(panel.read_bytes()).hexdigest()!=manifest['panel_sha256']:raise ValueError('Panel hash mismatch')
 by={}
 with panel.open(newline='') as f:
  for r in csv.DictReader(f):
   key=(r['iso3'],r['indicator']);by.setdefault(key,{})[int(r['year'])]=float(r['value'])
 predictions=[];methods=['last','mean5','drift5']
 for (iso,ind),observations in sorted(by.items()):
  if ind not in INDICATORS:continue
  for target in range(start,end+1):
   if target not in observations:continue
   train={y:v for y,v in observations.items() if y<target}
   if len(train)<5 or max(train)!=target-1:continue
   for method in methods:
    prediction=predict(train,method)
    if not math.isfinite(prediction):raise ValueError('nonfinite forecast')
    actual=observations[target]
    predictions.append({'iso3':iso,'indicator':ind,'target_year':target,'method':method,'actual':actual,'prediction':prediction,'absolute_error':abs(prediction-actual),'squared_error':(prediction-actual)**2})
 if not predictions:raise ValueError('No evaluable observations')
 out=root/'reports';out.mkdir(exist_ok=True)
 with (out/'rolling_predictions.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=predictions[0].keys());w.writeheader();w.writerows(predictions)
 summary=[]
 for ind in sorted(INDICATORS):
  for method in methods:
   rows=[r for r in predictions if r['indicator']==ind and r['method']==method]
   if not rows:continue
   summary.append({'indicator':ind,'method':method,'n':len(rows),'countries':len({r['iso3'] for r in rows}),'mae':statistics.mean(r['absolute_error'] for r in rows),'rmse':math.sqrt(statistics.mean(r['squared_error'] for r in rows))})
 report={'status':'retrospective_rolling_origin_benchmark','training_rule':'for target year t, fit only observations dated < t; require t-1 observed','target_years':[start,end],'dataset':'World Bank API latest revision as of retrieval date','historical_vintage_reconstruction':False,'actual_real_time_forecast':False,'model_calibrated_for_policy':False,'n_prediction_rows':len(predictions),'summary':summary,'limitations':['Contemporary World Bank revisions may contain retrospective revisions','One-year-ahead benchmark only; cannot validate 1000-year behavior','No uncertainty intervals or causal policy attribution','No independent external data validation','Country-level errors pooled within indicators; not population-weighted']}
 (out/'rolling_benchmark_report.json').write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
 return report
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--start',type=int,default=2016);p.add_argument('--end',type=int,default=2024);a=p.parse_args();evaluate(a.root,a.start,a.end)
