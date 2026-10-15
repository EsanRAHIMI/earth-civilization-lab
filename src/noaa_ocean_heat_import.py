"""Import observed NOAA NCEI World Ocean heat-content anomaly time series.

Source units 10^22 J, output zettajoules (1 ZJ = 10^21 J).
0-700m and 0-2000m are overlapping depth integrals, NOT two independent
layers; 700-2000m is their difference, with correlated uncertainty.
"""
import csv,hashlib,json,math,pathlib,urllib.request,urllib.error,time,random,socket
BASE='https://www.ncei.noaa.gov/data/oceans/woa/DATA_ANALYSIS/3M_HEAT_CONTENT/DATA/basin/yearly/'
FILES={'0_700m':'h22-w0-700m.dat','0_2000m':'h22-w0-2000m.dat'}
def get(url,attempts=5,timeout=35):
 # Retry transient network/server failures; never fabricate observations.
 req=urllib.request.Request(url,headers={'User-Agent':'EarthCivilizationLab/1.0','Accept':'text/plain'})
 for attempt in range(attempts):
  try:
   with urllib.request.urlopen(req,timeout=timeout) as f:
    raw=f.read()
    if len(raw)<200:raise ValueError('Suspiciously short NOAA response')
    return raw
  except urllib.error.HTTPError as e:
   if e.code not in (408,429,500,502,503,504) or attempt==attempts-1:raise
  except (urllib.error.URLError,TimeoutError,socket.timeout,ConnectionError):
   if attempt==attempts-1:raise
  time.sleep(min(2**attempt,12)+random.uniform(0,0.5))
 raise RuntimeError('NOAA download exhausted retries')
def run(root='.'):
 root=pathlib.Path(root);observed={};sources={}
 reference=root/'data/reference/noaa_world_ocean_heat_2005_2025.csv'
 used_reference=False
 for layer,name in FILES.items():
  url=BASE+name;data={}
  try:raw=get(url)
  except (urllib.error.URLError,TimeoutError,socket.timeout,ConnectionError) as e:
   if not reference.exists():raise
   used_reference=True
   with reference.open(newline='') as f:
    for row in csv.DictReader(f):
     y=int(row['year'])
     v=float(row['heat_'+layer+'_zj']);se=float(row['heat_'+layer+'_se_zj'])
     if not (math.isfinite(v) and math.isfinite(se) and se>=0):raise ValueError('Invalid NOAA reference value')
     if y in data:raise ValueError('Duplicate NOAA reference year')
     data[y]=(v,se)
   if len(data)!=21 or min(data)!=2005 or max(data)!=2025:raise ValueError('Incomplete NOAA reference')
   observed[layer]=data
   sources[layer]={'url':url,'source_type':'NOAA NCEI observed annual published values, repository reference snapshot','snapshot_sha256':hashlib.sha256(reference.read_bytes()).hexdigest(),'first_year':min(data),'last_year':max(data),'n':len(data),'live_download_error':str(e)[:240]}
   continue
  for line in raw.decode('utf-8-sig').splitlines()[1:]:
   parts=line.split()
   if len(parts)<3:continue
   try:y=int(float(parts[0]));v=float(parts[1]);se=float(parts[2])
   except ValueError:continue
   if math.isfinite(v) and math.isfinite(se) and se>=0:data[y]=(10*v,10*se)
  if len(data)<15:raise ValueError('Insufficient NOAA data '+layer)
  observed[layer]=data;sources[layer]={'url':url,'sha256':hashlib.sha256(raw).hexdigest(),'first_year':min(data),'last_year':max(data),'n':len(data)}
 years=sorted(set(observed['0_700m'])&set(observed['0_2000m']))
 if len([y for y in years if 2005<=y<=2024])<20:raise ValueError('NOAA heat-content overlap insufficient')
 out=root/'data/independent_raw';out.mkdir(parents=True,exist_ok=True)
 path=out/'ocean_heat_content_annual.csv'
 with path.open('w',newline='') as f:
  writer=csv.writer(f);writer.writerow(['year','heat_0_700_zj','heat_0_700_se_zj','heat_0_2000_zj','heat_0_2000_se_zj','heat_700_2000_zj'])
  for y in years:
   a,ase=observed['0_700m'][y];b,bse=observed['0_2000m'][y]
   writer.writerow([y,a,ase,b,bse,b-a])
 report={'status':'noaa_observed_ocean_heat_content_imported','used_repository_noaa_reference':used_reference,'output':str(path),'years':len(years),'first_year':min(years),'last_year':max(years),'sources':sources,'quantity':'heat-content anomaly','units':'zettajoules','spatial':'World Ocean','overlap_note':'700-2000m anomaly computed as difference; uncertainty of difference cannot be calculated assuming independence','cannot_constrain':'below 2000m ocean heat or ocean carbon stocks'}
 folder=root/'reports';folder.mkdir(exist_ok=True);(folder/'ocean_heat_content_provenance.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
