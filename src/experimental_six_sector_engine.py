"""Experimental six-sector dynamical emulator, NOT an Earth-system digital twin.

All variables are dimensionless anomalies from an explicitly supplied baseline.
Couplings are illustrative and must not be interpreted as estimated causal effects.
No claim of millennial predictive validity is made.
"""
import math,random,statistics

SECTORS=("climate","energy","water","food","population","economy")
# Signed interaction coefficients are hypotheses, not fitted physical parameters.
COUPLINGS={
 "climate":{"energy":0.008,"economy":0.004},
 "energy":{"economy":0.025,"climate":-0.018},
 "water":{"climate":-0.024,"population":-0.009},
 "food":{"water":0.036,"climate":-0.029,"energy":0.012},
 "population":{"food":0.010,"economy":0.006},
 "economy":{"energy":0.028,"food":0.018,"climate":-0.015},
}
DAMPING={"climate":0.012,"energy":0.06,"water":0.09,"food":0.08,"population":0.025,"economy":0.055}
def validate(state):
 if set(state)!=set(SECTORS):raise ValueError("Exactly six sectors required")
 if any(not math.isfinite(float(v)) or abs(float(v))>100 for v in state.values()):raise ValueError("Invalid anomaly")
def step(state,forcing=None,coefficients=COUPLINGS):
 validate(state);forcing=forcing or {}
 if any(k not in SECTORS or not math.isfinite(v) for k,v in forcing.items()):raise ValueError("Invalid forcing")
 nxt={}
 for target in SECTORS:
  delta=-DAMPING[target]*state[target]+sum(w*state[src] for src,w in coefficients[target].items())+forcing.get(target,0.)
  nxt[target]=state[target]+delta
 validate(nxt)
 return nxt
def ensemble(initial,years=50,members=200,seed=42,forcing=None,parameter_spread=0.2):
 if not 1<=years<=1000 or not 2<=members<=2000:raise ValueError("Invalid horizon or ensemble size")
 if not 0<=parameter_spread<=1:raise ValueError("Invalid parameter spread")
 rng=random.Random(seed);out={s:[[] for _ in range(years+1)] for s in SECTORS}
 for _ in range(members):
  coefficients={s:{k:v*rng.uniform(1-parameter_spread,1+parameter_spread) for k,v in d.items()} for s,d in COUPLINGS.items()}
  state=dict(initial)
  for y in range(years+1):
   for s in SECTORS:out[s][y].append(state[s])
   if y<years:state=step(state,forcing,coefficients)
 def quantile(xs,q):
  a=sorted(xs);z=(len(a)-1)*q;i=int(z);return a[i]+(a[min(i+1,len(a)-1)]-a[i])*(z-i)
 return {"status":"illustrative_sensitivity_only","seed":seed,"members":members,"years":years,"quantiles":{s:[{"year":y,"p05":quantile(vals,.05),"median":quantile(vals,.5),"p95":quantile(vals,.95)} for y,vals in enumerate(series)] for s,series in out.items()},"warning":"Parameter perturbations are NOT calibrated probabilistic confidence intervals. No empirical skill or physical stock conservation is established."}
