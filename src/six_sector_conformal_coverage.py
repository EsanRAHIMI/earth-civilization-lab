"""Distribution-free split-conformal intervals on held-out countries.

Calibration and evaluation countries never overlap. This measures empirical
coverage on held-out observed one-year changes; it does not validate causality.
"""
import json,pathlib,random,statistics,math
from src.six_sector_observed_hindcast import read_panel,samples,fit,TARGETS
def qceil(values,coverage=.9):
 xs=sorted(values)
 if not xs:raise ValueError("No calibration errors")
 k=min(len(xs)-1,max(0,math.ceil((len(xs)+1)*coverage)-1))
 return xs[k]
def run(root="."):
 root=pathlib.Path(root);rows=samples(read_panel(root/"data/multisector_observations.csv"))
 countries=sorted({r[0] for r in rows});rng=random.Random(20261016);rng.shuffle(countries)
 test=set(countries[:max(6,len(countries)//5)]);remaining=[c for c in countries if c not in test]
 cal=set(remaining[:max(6,len(remaining)//5)])
 train=[r for r in rows if r[0] not in test|cal and r[1]+1<=2018]
 calibration=[r for r in rows if r[0] in cal and 2019<=r[1]+1<=2023]
 evaluation=[r for r in rows if r[0] in test and 2019<=r[1]+1<=2023]
 if min(len(train),len(calibration),len(evaluation))<20:raise ValueError("Insufficient country-disjoint observed pairs")
 model,_=fit(train,10.)
 results={}
 for i,sector in enumerate(TARGETS):
  errors=[abs(model(x)[i]-y[i]) for _,_,x,y in calibration]
  radius=qceil(errors)
  hit=[abs(model(x)[i]-y[i])<=radius for _,_,x,y in evaluation]
  results[sector]={"log_scale_half_width":radius,"calibration_pairs":len(errors),"test_pairs":len(hit),"empirical_coverage":statistics.mean(hit),"target_coverage":.9,"calibrated_on_independent_countries":True}
 report={"status":"country_disjoint_conformal_interval_coverage_evaluated","method":"absolute log residual split conformal","results":results,"calibration_countries":len(cal),"test_countries":len(test),"training_pairs":len(train),"warning":"Exchangeability across countries is unverified; nominal 90% is not a guarantee under temporal/geographic distribution shift. Only one-year observational predictions; no uncertainty for millennium simulations."}
 out=root/"reports";out.mkdir(exist_ok=True);(out/"six_sector_conformal_coverage.json").write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=="__main__":run()
