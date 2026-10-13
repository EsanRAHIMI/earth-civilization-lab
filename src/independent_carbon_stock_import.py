"""Strict observational reservoir-stock importer.

Only accepts externally produced, documented annual global GtC stock series;
never fabricates inventories from GLODAP cruise points or static SoilGrids maps.
"""
import csv,json,math,pathlib,hashlib
REQUIRED={
 'ocean_surface':('ocean_surface_carbon_annual.csv','carbon_gtc'),
 'ocean_deep':('ocean_deep_carbon_annual.csv','carbon_gtc'),
 'vegetation':('vegetation_carbon_annual.csv','carbon_gtc'),
 'soil':('soil_carbon_annual.csv','carbon_gtc')
}
def run(root='.'):
 root=pathlib.Path(root);folder=root/'data/independent_raw';series={};details={}
 for key,(filename,column) in REQUIRED.items():
  p=folder/filename
  if not p.exists():
   details[key]={'status':'missing','file':filename};continue
  rows={};raw=p.read_bytes()
  for row in csv.DictReader(raw.decode('utf-8-sig').splitlines()):
   try:
    y=int(row['year']);v=float(row[column]);u=float(row['uncertainty_gtc'])
    source=row['source_url'].strip()
   except (KeyError,ValueError) as e:raise ValueError(f'{filename}: malformed annual carbon stock row') from e
   if not (1800<=y<=2100 and math.isfinite(v) and math.isfinite(u) and v>0 and u>0 and source.startswith('https://')):raise ValueError(f'{filename}: invalid physical units, uncertainty or provenance')
   if y in rows:raise ValueError(f'{filename}: duplicate year {y}')
   rows[y]=(v,u)
  if len(rows)<10:raise ValueError(f'{filename}: fewer than 10 measured annual global stock estimates')
  series[key]=rows
  details[key]={'status':'validated','file':filename,'years':len(rows),'first_year':min(rows),'last_year':max(rows),'sha256':hashlib.sha256(raw).hexdigest()}
 overlap=set.intersection(*(set(v) for v in series.values())) if len(series)==len(REQUIRED) else set()
 report={'status':'ready_for_joint_stock_calibration' if len(overlap)>=10 else 'blocked_missing_independent_annual_global_stock_series','stock_series':details,'joint_overlap_years':sorted(overlap),'physical_calibration_complete':False,'caution':'File-level validation cannot prove source spatial representativeness, carbon accounting boundary consistency, or parameter identifiability. Review scientific provenance before fit.'}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'independent_carbon_stock_import.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
