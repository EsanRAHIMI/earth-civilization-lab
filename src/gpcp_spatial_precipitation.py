"""Real NOAA GPCP v2.3 monthly gridded rainfall, with immutable source bytes.

Subsets are exact RECTANGULAR latitude/longitude footprints, not watershed
polygons. This yields a genuine precipitation observation layer, never a
GRACE water-storage validation or a calibrated basin water balance.
NO extrapolation, invented months, or training/holdout contamination.
"""
import calendar,csv,datetime,hashlib,json,math,pathlib,urllib.request,urllib.error,http.client,time
SOURCE="https://psl.noaa.gov/thredds/fileServer/Datasets/gpcp/precip.mon.mean.nc"
REGIONS={
 "north_india_bbox":{"lat":[24.,32.],"lon":[73.,84.]},
 "lower_mekong_bbox":{"lat":[10.,23.],"lon":[100.,107.]},
 "east_africa_bbox":{"lat":[-5.,12.],"lon":[29.,40.]},
}
PERIOD=[2005,2023]

def decode_region(nc,region,start_year=2005,end_year=2023):
 import numpy as np
 lat=np.asarray(nc.variables["lat"][:],dtype=float)
 lon=np.asarray(nc.variables["lon"][:],dtype=float)
 date=nc.variables["time"]
 precip=nc.variables["precip"]
 units=getattr(precip,"units",None)
 if isinstance(units,bytes):units=units.decode()
 if str(units).replace(" ","") not in ("mm/day","mmday-1"):
  raise ValueError("GPCP precipitation must be mm/day, not mm/month")
 latindices=np.where((lat>=region["lat"][0])&(lat<=region["lat"][1]))[0]
 lonindices=np.where((lon>=region["lon"][0])&(lon<=region["lon"][1]))[0]
 if len(latindices)<2 or len(lonindices)<2:
  raise ValueError("Insufficient GPCP rectangle grid coverage")
 if hasattr(date,"units"):
  from netCDF4 import num2date
  dt=num2date(date[:],date.units,only_use_cftime_datetimes=False)
 else:raise ValueError("Missing CF time axis")
 years={}
 for index,when in enumerate(dt):
  year=int(when.year);month=int(when.month)
  if not(start_year<=year<=end_year):continue
  # Select small 2D rectangle, avoid full globe monthly arrays.
  slab=np.ma.asarray(precip[index,:,:])
  slab=slab[np.ix_(latindices,lonindices)]
  if np.ma.is_masked(slab) and np.any(np.ma.getmaskarray(slab)):
   raise ValueError("Missing NOAA satellite-gauge precipitation cells")
  sample=np.asarray(slab,dtype=float)
  if not np.all(np.isfinite(sample)) or np.any(sample<0):
   raise ValueError("Invalid satellite-gauge rainfall observations")
  # NOAA GPCP is a regular latitude grid; spherical cos latitude weights
  # suffice for a RECTANGULAR grid cell footprint. Region polygon NOT used.
  w=np.cos(np.deg2rad(lat[latindices]))
  monthly=float(np.average(sample,axis=0,weights=None).mean()) if False else float(
   (sample*w[:,None]).sum()/(w.sum()*len(lonindices)))
  mm=monthly*calendar.monthrange(year,month)[1]
  months=years.setdefault(year,{})
  if month in months:raise ValueError("Duplicated precipitation month")
  months[month]=mm
 output={}
 for year in range(start_year,end_year+1):
  months=years.get(year,{})
  if set(months)!=set(range(1,13)):
   raise ValueError("Missing NOAA monthly records in year "+str(year))
  output[year]=sum(months.values())
 return output,{"gpcp_grid_count":int(len(latindices)*len(lonindices)),
                "source_unit":"mm/day monthly mean","output_unit":"mm/year accumulated",
                "spatial_support":"geographic rectangle, no basin mask"}

def run(root="."):
 import netCDF4
 root=pathlib.Path(root)
 output=root/"data/independent_raw"
 output.mkdir(parents=True,exist_ok=True)
 path=output/"noaa_gpcp_v23_monthly.nc"
 pinned_sha="d31c53ab8180a883bd01442212948c3db4372d481b94a90e69d3d86bb65d7f68"
 reused_pinned=path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==pinned_sha
 if reused_pinned:
  payload=path.read_bytes()
 else:
  # NOAA THREDDS large HTTP transfers are occasionally truncated by the server.
  # Download independently verified HTTP 206 byte ranges, never a partial file.
  head=urllib.request.Request(SOURCE,method="HEAD",headers={"User-Agent":"EarthCivilizationLab scientific-data-review"})
  with urllib.request.urlopen(head,timeout=60) as info:
   total=int(info.headers.get("Content-Length","0"))
  if not(1000000<total<200000000):raise ValueError("Invalid NOAA source length")
  block=2*1024*1024
  buffers=[]
  for begin in range(0,total,block):
   finish=min(begin+block,total)-1
   part=None
   for attempt in range(5):
    try:
     request=urllib.request.Request(SOURCE,headers={
      "Range":f"bytes={begin}-{finish}",
      "User-Agent":"EarthCivilizationLab scientific-data-review"})
     with urllib.request.urlopen(request,timeout=90) as response:
      status=response.status
      content_range=response.headers.get("Content-Range","")
      fragment=response.read()
     if status!=206 or not content_range.startswith(f"bytes {begin}-{finish}/{total}"):
      raise ValueError("NOAA server refused precise HTTP range")
     if len(fragment)!=finish-begin+1:raise IOError("Truncated NOAA range")
     part=fragment
     break
    except (http.client.IncompleteRead,urllib.error.URLError,TimeoutError,ConnectionError,IOError):
     if attempt==4:raise
     time.sleep(min(2**attempt,8))
   if part is None:raise RuntimeError("NOAA range unavailable")
   buffers.append(part)
  payload=b"".join(buffers)
  if len(payload)!=total:raise ValueError("NOAA byte-range source length mismatch")
  path.write_bytes(payload)

 with netCDF4.Dataset(path) as nc:
  observed={name:decode_region(nc,box,*PERIOD) for name,box in REGIONS.items()}
 report={"status":"real_satellite_gauge_gpcp_rainfall_ingested",
         "retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
         "url":SOURCE,"product":"NOAA PSL GPCP v2.3 merged satellite/gauge",
         "doi":"10.7289/V56971M6",
         "input_sha256":hashlib.sha256(payload).hexdigest(),"bytes":len(payload),
         "historical_source_snapshot_reused":reused_pinned,
         "original_source_snapshot_date_utc":"2026-10-16" if reused_pinned else None,
         "regions":{name:{"bbox":REGIONS[name],**details,
                     "records":{str(year):round(v,4) for year,v in annual.items()}}
                    for name,(annual,details) in observed.items()},
         "strictly_independent_of_era5":False,
         "water_basin_model_calibrated":False,
         "GRACE_validated":False,
         "limitations":["Rects are not watersheds; no outlet discharge or TWS stocks",
           "GPCP 2.5-degree grid is unsuitable for detailed regional flood/crop effects",
           "Merged satellite and rain-gauge product has measurement dependencies",
           "No long-range water forecast skill established"]}
 folder=root/"reports";folder.mkdir(exist_ok=True)
 (folder/"gpcp_spatial_precipitation.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"status":report["status"],"years":PERIOD,
                   "regions":list(report["regions"]),"sha256":report["input_sha256"]},indent=2))
 return report
if __name__=="__main__":run()
