"""Fetch ERA5-derived OWID World annual precipitation, never country averages.
World is the published global series, not necessarily land-only; provenance
and spatial coverage are recorded to prevent a misleading land-only label.
"""
import csv,io,urllib.request,hashlib,json,pathlib,math
URL='https://ourworldindata.org/grapher/average-precipitation-per-year.csv?v=1&csvType=full&useColumnShortNames=false'
def run(root='.'):
 root=pathlib.Path(root)
 request=urllib.request.Request(URL,headers={'User-Agent':'EarthCivilizationLab/1.0'})
 with urllib.request.urlopen(request,timeout=90) as response:raw=response.read()
 rows=list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig'))))
 if not rows:raise ValueError('Empty OWID precipitation response')
 headers=rows[0].keys()
 col=next((k for k in headers if k not in ('Entity','Code','Year') and 'precipitation' in k.lower()),None)
 if not col:raise ValueError('No precipitation column: '+str(list(headers)))
 world=[r for r in rows if r.get('Entity')=='World']
 if not world:raise ValueError('OWID chart lacks World entity; cannot substitute unweighted country mean')
 values={}
 for row in world:
  try:y=int(row['Year']);v=float(row[col])
  except (KeyError,ValueError):continue
  if math.isfinite(v) and 100<v<5000:values[y]=v
 if len([y for y in range(1980,2025) if y in values])<45:raise ValueError('Missing required 1980-2024 global annual precipitation')
 path=root/'data/independent_raw/global_land_precipitation_annual.csv'
 path.parent.mkdir(parents=True,exist_ok=True)
 with path.open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['year','precipitation_mm'])
  for year in sorted(values):writer.writerow([year,values[year]])
 report={'status':'owid_era5_global_precipitation_downloaded','source':URL,'source_sha256':hashlib.sha256(raw).hexdigest(),'entity':'World','source_column':col,'years':len(values),'start_year':min(values),'end_year':max(values),'units':'mm/year','spatial_coverage_warning':'World aggregate from ERA5/OWID; verify land-only mask before claiming global land precipitation','not_independent_of_era5':True}
 out=root/'reports';out.mkdir(exist_ok=True);(out/'precipitation_provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
