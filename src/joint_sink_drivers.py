"""Joint effective sink regression with temperature, precipitation and land use.
Required independent annual precipitation CSV must be supplied. No fabricated
climate observations or invented validation scores.
CSV columns: year,precipitation_mm (global land-area weighted annual mean).
"""
import csv,json,math,pathlib,statistics
from src.gcb_separate_sink_calibration import load
from src.nasa_temperature_hindcast import observations
def read_precip(path):
 if not path.exists():raise FileNotFoundError(str(path))
 rows={}
 for r in csv.DictReader(path.open()):
  try:y=int(r['year']);v=float(r['precipitation_mm'])
  except (KeyError,ValueError):continue
  if math.isfinite(v) and 100<v<5000:rows[y]=v
 return rows
def solve(a,b):
 n=len(b)
 for i in range(n):
  j=max(range(i,n),key=lambda k:abs(a[k][i]))
  if abs(a[j][i])<1e-10:raise ValueError('Singular design matrix')
  a[i],a[j]=a[j],a[i];b[i],b[j]=b[j],b[i]
  v=a[i][i]
  for k in range(i,n):a[i][k]/=v
  b[i]/=v
  for j in range(n):
   if j==i:continue
   v=a[j][i]
   for k in range(i,n):a[j][k]-=v*a[i][k]
   b[j]-=v*b[i]
 return b
def ridge(x,y,penalty=.5):
 p=len(x[0]);means=[statistics.mean(row[j] for row in x) for j in range(p)]
 scales=[statistics.pstdev(row[j] for row in x) or 1 for j in range(p)]
 z=[[(row[j]-means[j])/scales[j] for j in range(p)] for row in x]
 ym=statistics.mean(y);a=[[sum(row[i]*row[j] for row in z)+(penalty if i==j else 0) for j in range(p)] for i in range(p)]
 b=[sum(row[i]*(v-ym) for row,v in zip(z,y)) for i in range(p)]
 weights=solve(a,b)
 return lambda row:ym+sum(weights[j]*(row[j]-means[j])/scales[j] for j in range(p)),{'standardized_weights':weights,'means':means,'scales':scales}
def run(root='.'):
 root=pathlib.Path(root)
 precipitation=root/'data/independent_raw/global_land_precipitation_annual.csv'
 if not precipitation.exists():
  out=root/'reports';out.mkdir(exist_ok=True)
  report={'status':'blocked_missing_independent_precipitation','required_csv':str(precipitation),'columns':['year','precipitation_mm'],'calibration_completed':False,'warning':'Do not replace missing observations with fabricated or climatological constants.'}
  (out/'joint_sink_calibration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));return report
 rain=read_precip(precipitation)
 co2,temp,_=observations(root)
 ocean,_=load('ocean-sink',root);land,_=load('terrestrial-sink',root)
 landuse,_=load('land-use-change-emissions',root)
 years=[y for y in range(1980,2025) if all(y in d for d in (rain,co2,temp,ocean,land,landuse))]
 train=[y for y in years if y<=2014];test=[y for y in years if y>=2015]
 if len(train)<30 or len(test)<8:raise ValueError('Insufficient overlap in independent data')
 # Both responses fitted simultaneously with the same predictor design.
 # Land-use emissions are a separate flux, not automatically the land sink.
 def features(y):return [co2[y],temp[y],rain[y],landuse[y]]
 x=[features(y) for y in train];out={}
 for name,target in [('ocean',ocean),('land',land)]:
  fn,parameters=ridge(x,[target[y] for y in train])
  mae=statistics.mean(abs(fn(features(y))-target[y]) for y in test)
  base=statistics.mean(target[y] for y in train)
  bmae=statistics.mean(abs(base-target[y]) for y in test)
  out[name]={'holdout_mae_gtc_per_year':mae,'baseline_mae_gtc_per_year':bmae,'beats_baseline':mae<bmae,'parameters':parameters}
 report={'status':'joint_effective_flux_regression_completed','years_train':len(train),'years_test':len(test),'ocean_and_land':out,'drivers':['NOAA CO2','NASA GISTEMP temperature','external observed global precipitation','GCB land-use emissions'],'jointly_fitted':'common covariate design; separately fitted targets, not a coupled inverse Earth-system model','multibox_reservoir_rates_identified':False,'millennial_probabilities_calibrated':False}
 dest=root/'reports';dest.mkdir(exist_ok=True);(dest/'joint_sink_calibration.json').write_text(json.dumps(report,indent=2));print(json.dumps(report));return report
if __name__=='__main__':run()
