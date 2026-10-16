"""Authenticated NASA PO.DAAC JPL GRACE/GRACE-FO Mascon data acquisition.

This is a *protected* physical-state observation; NASA Earthdata Login is
required. The tool refuses to substitute NOAA rainfall for terrestrial water
storage or report validation without spatial leak-correction metadata.
"""
import datetime,hashlib,json,os,pathlib
COLLECTION="TELLUS_GRAC-GRFO_MASCON_GRID_RL06.3_V4"
DATASET_URL="https://podaac.jpl.nasa.gov/dataset/"+COLLECTION

def inspect(path):
 from netCDF4 import Dataset,num2date
 with Dataset(path) as nc:
  variables={name:{"dimensions":list(v.dimensions),"units":str(getattr(v,"units","")),
                   "shape":list(v.shape)} for name,v in nc.variables.items()}
  if "lwe_thickness" not in nc.variables:
   raise ValueError("NASA GRACE land-water-equivalent thickness is missing")
  if "time" not in nc.variables:
   raise ValueError("NASA GRACE monthly time coordinate is missing")
  lw=nc.variables["lwe_thickness"]
  if str(getattr(lw,"units","")).strip().lower() not in ("cm","cm water equivalent","centimeters"):
   raise ValueError("Unknown NASA water-equivalent thickness unit")
  t=nc.variables["time"]
  try:
   dates=num2date(t[:],t.units,only_use_cftime_datetimes=False)
   strings=[str(getattr(value,"year"))+"-"+f"{value.month:02d}" for value in dates]
  except Exception as e:raise ValueError("Uninterpretable GRACE monthly calendar") from e
  if len(strings)<24 or len(strings)!=len(set(strings)):
   raise ValueError("Insufficient or duplicated NASA GRACE monthly observations")
  return {"variables":variables,"first_month":min(strings),"last_month":max(strings),
          "months":len(strings),"water_equivalent_unit":"cm anomaly",
          "relative_storage_only":True}

def run(root="."):
 if not(os.environ.get("EARTHDATA_TOKEN") or
        (os.environ.get("EARTHDATA_USERNAME") and os.environ.get("EARTHDATA_PASSWORD"))):
  raise RuntimeError("EARTHDATA_TOKEN GitHub Actions secret required; protected GRACE cannot be retrieved anonymously")
 import earthaccess
 root=pathlib.Path(root)
 authentication=earthaccess.login(strategy="environment",persist=False)
 if not authentication.authenticated:
  raise RuntimeError("NASA Earthdata authentication failed")
 granules=earthaccess.search_data(short_name=COLLECTION,
             temporal=("2019-01-01","2023-12-31"),count=10)
 if not granules:raise RuntimeError("CMR returned no real JPL GRACE/GRACE-FO mascon granules")
 raw=root/"data/independent_raw/grace"
 raw.mkdir(parents=True,exist_ok=True)
 downloaded=earthaccess.download(granules,str(raw))
 files=[]
 for name in downloaded:
  p=pathlib.Path(name)
  if p.suffix.lower() not in (".nc",".nc4"):
   continue
  if not p.is_file() or p.stat().st_size<10000:
   raise ValueError("Invalid Earthdata GRACE NetCDF")
  details=inspect(p)
  files.append({"filename":p.name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                "bytes":p.stat().st_size,**details})
 if not files:raise RuntimeError("No matching valid GRACE NetCDF downloaded")
 report={
  "status":"authenticated_NASA_GRACE_mascon_bytes_and_physical_unit_verified",
  "collection":COLLECTION,"source":DATASET_URL,
  "retrieved_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
  "files":files,"interpolation_fabrication":False,
  "basin_polygon_matched":False,
  "gain_scale_correction_validated":False,
  "spatial_leakage_correction_validated":False,
  "observational_error_covariance_validated":False,
  "land_water_storage_model_calibrated":False,
  "operational_hydrology_authorized":False,
  "not_a_plant_available_soil_water_measurement":True,
  "next_step":"Apply JPL coastline/land leakage-corrected mascon mask to independently georeferenced basin polygons, then compare with independent hydrological P-ET-Q time series.",
 }
 out=root/"reports";out.mkdir(exist_ok=True)
 (out/"nasa_grace_mascon_observation_manifest.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"status":report["status"],"n_files":len(files),
                   "bytes":sum(f["bytes"] for f in files),"scientific_calibration":False},indent=2))
 return report
if __name__=="__main__":run()
