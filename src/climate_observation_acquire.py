"""Acquire NASA GISTEMP and NOAA GML annual observations with immutable hashes."""
import datetime,hashlib,json,pathlib,urllib.request
from src.climate_multisource_readiness import annual_records
SOURCES={
 "nasa_gistemp_global.csv":("https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv","Year","J-D"),
 "noaa_global_annual_co2.csv":("https://gml.noaa.gov/webdata/ccgg/trends/co2/co2_annmean_gl.csv","year","mean")
}
def ingest(root=".",fetcher=None):
 root=pathlib.Path(root)
 raw_dir=root/"data/independent_raw";raw_dir.mkdir(parents=True,exist_ok=True)
 if fetcher is None:
  def fetcher(url):
   req=urllib.request.Request(url,headers={"User-Agent":"EarthLab scientific archival research"})
   with urllib.request.urlopen(req,timeout=90) as response:return response.read()
 records={}
 for name,(url,year,value) in SOURCES.items():
  body=fetcher(url)
  if not isinstance(body,bytes) or len(body)<100 or b"<html" in body[:1024].lower():
   raise ValueError("Invalid source response "+name)
  staging=raw_dir/(name+".partial")
  staging.write_bytes(body)
  try:
   series=annual_records(staging,year,value)
   if set(series)!=set(range(1980,2025)):
    raise ValueError("Incomplete 1980-2024 source "+name)
   if name.startswith("noaa") and any(not 250<v<600 for v in series.values()):
    raise ValueError("NOAA CO2 range invalid")
   if name.startswith("nasa") and any(not -3<v<5 for v in series.values()):
    raise ValueError("NASA anomaly range invalid")
   staging.replace(raw_dir/name)
  finally:
   if staging.exists():staging.unlink()
  records[name]={"url":url,"sha256":hashlib.sha256(body).hexdigest(),
                 "bytes":len(body),"years":len(series),
                 "retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat()}
 report={"status":"NASA_NOAA_source_bytes_verified","sources":records,
         "asof_2014_source_vintage_certified":False}
 out=root/"reports";out.mkdir(exist_ok=True)
 (out/"climate_source_manifest.json").write_text(json.dumps(report,indent=2))
 print(json.dumps(report,indent=2))
 return report
if __name__=="__main__":ingest()
