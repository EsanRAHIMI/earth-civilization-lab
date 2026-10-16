"""Observed World Bank six-sector one-step emulator with country-disjoint holdout.

No missing values are imputed. Fit only complete consecutive-year pairs.
All six outcomes are estimated jointly from previous-year observed features.
This is predictive association, NOT a causal Earth-system model.
"""
import csv,collections,json,math,pathlib,random,statistics
from src.multisector import INDICATORS
from src.historical_calibration import solve
TARGETS={"climate":"climate_ghg_per_capita","energy":"electricity_access","water":"freshwater_withdrawals","food":"food_production_index","population":"population","economy":"real_gdp_per_capita"}
FEATURES=tuple(TARGETS.values())
def read_panel(path):
 panel=collections.defaultdict(dict)
 with open(path,newline="") as f:
  for row in csv.DictReader(f):
   if row["indicator"] in FEATURES:
    val=float(row["value"])
    if math.isfinite(val):panel[(row["country"],int(row["year"]))][row["indicator"]]=val
 return panel
def samples(panel):
 result=[]
 for (country,year),prev in sorted(panel.items()):
  nxt=panel.get((country,year+1),{})
  if not all(k in prev and k in nxt and prev[k]>0 and nxt[k]>0 for k in FEATURES):continue
  x=[math.log(prev[k]) for k in FEATURES]
  y=[math.log(nxt[k]) for k in FEATURES]
  result.append((country,year,x,y))
 return result
def fit(train,penalty):
 if len(train)<20:raise ValueError("Insufficient complete six-sector training pairs")
 means=[statistics.mean(row[2][i] for row in train) for i in range(6)]
 scales=[statistics.pstdev(row[2][i] for row in train) or 1 for i in range(6)]
 def design(x):return [1.]+[(x[i]-means[i])/scales[i] for i in range(6)]
 coefs=[]
 for target in range(6):
  a=[[0.]*7 for _ in range(7)];b=[0.]*7
  for _,_,x,y in train:
   xx=design(x)
   for i in range(7):
    b[i]+=xx[i]*y[target]
    for j in range(7):a[i][j]+=xx[i]*xx[j]
  for i in range(1,7):a[i][i]+=penalty
  coefs.append(solve(a,b))
 def predict(x):
  z=design(x)
  return [sum(a*b for a,b in zip(beta,z)) for beta in coefs]
 return predict,{"means":means,"scales":scales,"coefficients":coefs,"penalty":penalty}
def evaluate(rows,predict):
 out={}
 for i,sector in enumerate(TARGETS):
  if not rows:continue
  errors=[];baseline=[]
  for _,_,x,y in rows:
   actual=math.exp(y[i]);pred=math.exp(max(-50,min(50,predict(x)[i])));persist=math.exp(x[i])
   errors.append(2*abs(pred-actual)/(abs(pred)+abs(actual)))
   baseline.append(2*abs(persist-actual)/(abs(persist)+abs(actual)))
  out[sector]={"n":len(rows),"model_smape_percent":100*statistics.mean(errors),"persistence_smape_percent":100*statistics.mean(baseline),"beats_persistence":statistics.mean(errors)<statistics.mean(baseline)}
 return out
def run(root="."):
 root=pathlib.Path(root);panel=read_panel(root/"data/multisector_observations.csv");rows=samples(panel)
 countries=sorted({r[0] for r in rows})
 if len(countries)<30:raise ValueError("Insufficient complete-case countries for country-disjoint holdout")
 rng=random.Random(20261016);rng.shuffle(countries)
 hold_c=set(countries[:max(6,len(countries)//5)]);development=[r for r in rows if r[0] not in hold_c and r[1]+1<=2018]
 validation=[r for r in rows if r[0] not in hold_c and 2019<=r[1]+1<=2023]
 holdout=[r for r in rows if r[0] in hold_c and 2019<=r[1]+1<=2023]
 if min(len(development),len(validation),len(holdout))<20:raise ValueError("Insufficient disjoint train/validation/test complete pairs")
 choices=[]
 for p in (0.1,1.,10.,100.):
  fn,_=fit(development,p);m=evaluate(validation,fn)
  choices.append((statistics.mean(v["model_smape_percent"] for v in m.values()),p))
 penalty=min(choices)[1]
 # Choose model versus persistence for each sector using development validation only.
 selected_fn,_=fit(development,penalty)
 validation_metrics=evaluate(validation,selected_fn)
 selected={sector:("regression" if val["beats_persistence"] else "persistence") for sector,val in validation_metrics.items()}
 train=[r for r in rows if r[0] not in hold_c and r[1]+1<=2023]
 fn,parameters=fit(train,penalty)
 metrics=evaluate(holdout,fn)
 # Honest held-out evaluation of the validation-selected predictor.
 # No test information influences predictor choice.
 for sector,values in metrics.items():
  values["selected_predictor"]=selected[sector]
  values["selected_smape_percent"]=values["model_smape_percent"] if selected[sector]=="regression" else values["persistence_smape_percent"]
  values["selected_beats_persistence"]=values["selected_smape_percent"]<values["persistence_smape_percent"]
 report={"status":"country_disjoint_historical_holdout_evaluated","data_source":"World Bank country indicator observations","indicator_mapping":TARGETS,"sample_policy":"Six strictly positive observed indicators in both consecutive years; no imputation","train_pairs":len(train),"validation_pairs":len(validation),"holdout_pairs":len(holdout),"holdout_countries":sorted(hold_c),"train_countries":len(set(r[0] for r in train)),"validation_selection_penalty":penalty,"validation_selected_predictors":selected,"validation_model_vs_persistence":validation_metrics,"validation_scores":choices,"holdout_years":"2019-2023","metrics":metrics,"all_sectors_beat_persistence":all(v["beats_persistence"] for v in metrics.values()),"selected_predictors_all_beat_persistence":all(v["selected_beats_persistence"] for v in metrics.values()),"selected_predictors_have_no_verified_skill_when_tied":True,"independent_provider_validation":False,"causal":False,"physical_units_conserved":False,"warnings":["Country-disjoint temporal holdout, but all outcomes share World Bank source","Complete-case selection biases toward well-reported countries","Using observed prior-year indicators means this is a one-step hindcast, not a free-running forecast","Regression coefficients are predictive associations, not physical interactions","Uncertainty calibration and geospatial rasters require separate evaluation"]}
 out=root/"reports";out.mkdir(exist_ok=True);(out/"six_sector_observed_holdout.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=="__main__":run()
