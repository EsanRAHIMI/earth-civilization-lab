"""Multi-seed country-disjoint robustness audit for climate, water and food.

Each seed creates its own untouched test countries. Candidate selection uses
development countries only, never the held-out countries.
"""
import json,pathlib,random,statistics
from src.six_sector_observed_hindcast import read_panel,samples,TARGETS,fit,fit_change,evaluate

SECTORS=("climate","water","food")
SEEDS=(1103,2107,3109,4111,5113)
def predictor(name,p,rows):
 if name=="persistence":return lambda x:list(x)
 if name=="level":return fit(rows,p)[0]
 return fit_change(rows,p,name)
def run(root="."):
 root=pathlib.Path(root)
 rows=samples(read_panel(root/"data/multisector_observations.csv"))
 countries=sorted({r[0] for r in rows})
 specs=[("persistence",0.)]+[(mode,p) for mode in ("own","joint","level") for p in (.1,1.,10.,100.)]
 results=[]
 for seed in SEEDS:
  names=list(countries);random.Random(seed).shuffle(names)
  held=set(names[:max(6,len(names)//5)])
  dev=[r for r in rows if r[0] not in held and r[1]+1<=2018]
  val=[r for r in rows if r[0] not in held and 2019<=r[1]+1<=2023]
  test=[r for r in rows if r[0] in held and 2019<=r[1]+1<=2023]
  if min(map(len,(dev,val,test)))<20:
   results.append({"seed":seed,"status":"insufficient_data","counts":[len(dev),len(val),len(test)]});continue
  scored={}
  for mode,p in specs:
   key=mode+":"+str(p)
   scored[key]=evaluate(val,predictor(mode,p,dev))
  train=[r for r in rows if r[0] not in held and r[1]+1<=2023]
  metrics={}
  for sector in SECTORS:
   key=min(scored,key=lambda k:scored[k][sector]["model_smape_percent"])
   mode,p=key.split(":")
   result=evaluate(test,predictor(mode,float(p),train))[sector]
   improvement=result["persistence_smape_percent"]-result["model_smape_percent"]
   metrics[sector]={"selected":key,"test_smape":result["model_smape_percent"],"persistence_smape":result["persistence_smape_percent"],"improvement_percentage_points":round(improvement,5),"beats_persistence":improvement>1e-9}
  results.append({"seed":seed,"status":"evaluated","test_pairs":len(test),"test_country_count":len(held),"metrics":metrics})
 summary={}
 for sector in SECTORS:
  vals=[x["metrics"][sector]["improvement_percentage_points"] for x in results if x["status"]=="evaluated"]
  summary[sector]={"evaluated_splits":len(vals),"wins":sum(v>0 for v in vals),"median_improvement_percentage_points":statistics.median(vals) if vals else None,"consistent_positive":len(vals)==len(SEEDS) and all(v>0 for v in vals)}
 report={"status":"multi_split_robustness_audit","source":"World Bank only; NOT independent-source validation","seeds":list(SEEDS),"holdout_years":"2019-2023","candidate_selection":"validation countries only, 2019-2023; fit on <=2018","summary":summary,"splits":results,"limitations":["Repeated splits overlap and are not independent experiments","Only one-step observed-input hindcasts","No independent climate, water or food provider incorporated","No physical causality or scenario readiness inferred"]}
 dest=root/"reports";dest.mkdir(exist_ok=True)
 (dest/"six_sector_robustness.json").write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
 return report
if __name__=="__main__":run()
