"""Official FAOSTAT QCL wheat yield and harvested-area observations (streaming).

Raw source is a 30+ MB FAO ZIP with >4 million normalized records. Data are
official/estimated depending on per-record Flag and must not be conflated
with independent geospatial crop-yield validation.
"""
import csv,datetime,hashlib,io,json,math,pathlib,urllib.request,zipfile
MANIFEST="https://bulks-faostat.fao.org/production/datasets_E.json"
COUNTRIES={"100":"India","5":"China","231":"United States of America"}
WHEAT="15"
ELEMENTS={"5312":"harvested_area","5419":"yield","5510":"production"}
YEARS=range(2005,2024)

def extract(selected_zip):
 out={}
 with zipfile.ZipFile(io.BytesIO(selected_zip)) as archive:
  candidates=[p for p in archive.namelist() if p.lower().endswith(".csv")
             and "all_data" in p.lower()]
  if len(candidates)!=1:
   raise ValueError("FAOSTAT QCL normalized CSV entry unclear")
  with archive.open(candidates[0]) as stream:
   reader=csv.DictReader(io.TextIOWrapper(stream,encoding="utf-8-sig",newline=""))
   required={"Area Code","Item Code","Element Code","Year","Unit","Value","Flag"}
   if not reader.fieldnames or not required.issubset(reader.fieldnames):
    raise ValueError("Unexpected FAOSTAT normalized schema")
   for record in reader:
    country=record["Area Code"];element=record["Element Code"]
    if country not in COUNTRIES or record["Item Code"]!=WHEAT or element not in ELEMENTS:
     continue
    try:year=int(record["Year"]);v=float(record["Value"])
    except (TypeError,ValueError):continue
    if year not in YEARS or not math.isfinite(v) or v<=0:continue
    flag=record["Flag"]
    if not flag:raise ValueError("Missing FAOSTAT source status flag")
    key=(country,year,element)
    if key in out:raise ValueError("Duplicate FAOSTAT crop observation")
    unit=record["Unit"]
    if element=="5419" and unit not in ("100 g/ha","hg/ha","kg/ha"):
     raise ValueError("Unexpected wheat-yield measurement unit: "+unit)
    if element=="5312" and unit!="ha":
     raise ValueError("Unexpected harvested-area measurement unit")
    if element=="5419":
     tonnes_per_ha=v/10000 if unit in ("hg/ha","100 g/ha") else v/1000
     value=tonnes_per_ha
     new_unit="t/ha"
    else:
     if element=="5510" and unit not in ("t","tonnes"):
      raise ValueError("Unexpected wheat-production mass unit: "+unit)
     value=v
     new_unit="ha" if element=="5312" else "t"
    out[key]={"value":value,"unit":new_unit,"flag":flag,"source_unit":unit}
 return out

def run(root="."):
 root=pathlib.Path(root)
 def request(url):
  req=urllib.request.Request(url,headers={"User-Agent":"Earth Civilization Lab academic research"})
  with urllib.request.urlopen(req,timeout=180) as response:return response.read()
 index=request(MANIFEST)
 catalog=json.loads(index)
 datasets=catalog["Datasets"]["Dataset"]
 record=next((a for a in datasets if a.get("DatasetCode")=="QCL"),None)
 if not record or "bulks-faostat.fao.org/production/" not in record.get("FileLocation",""):
  raise ValueError("FAOSTAT official QCL URL not present in published manifest")
 url=record["FileLocation"]
 raw=request(url)
 if len(raw)<1000000:raise ValueError("FAOSTAT archive unusually small")
 values=extract(raw)
 panel={}
 for country,name in COUNTRIES.items():
  for year in YEARS:
   a=values.get((country,year,"5312"))
   y=values.get((country,year,"5419"))
   production=values.get((country,year,"5510"))
   if not a or not y or not production:continue
   panel.setdefault(name,[]).append({"year":year,
      "yield_t_ha":round(y["value"],8),"harvested_area_ha":round(a["value"],2),
      "wheat_output_estimate_t":round(a["value"]*y["value"],2),
      "reported_production_t":production["value"],"reported_production_flag":production["flag"],
      "production_mass_residual_t":round(a["value"]*y["value"]-production["value"],2),
      "yield_flag":y["flag"],"area_flag":a["flag"]})
 if any(len(panel.get(name,[]))<12 for name in COUNTRIES.values()):
  raise ValueError("Insufficient observed country-specific annual wheat records; per-country="+str({name:len(panel.get(name,[])) for name in COUNTRIES.values()})+"; extracted="+str(len(values))+"; first_keys="+str(list(values)[:10]))
 folder=root/"data/independent_raw";folder.mkdir(parents=True,exist_ok=True)
 (folder/"faostat_qcl_original.zip").write_bytes(raw)
 report={"status":"FAOSTAT_country_wheat_yield_and_area_observations",
   "producer":"United Nations FAO, FAOSTAT domain QCL",
   "catalog_retrieved":datetime.datetime.now(datetime.timezone.utc).isoformat(),
   "catalog_sha256":hashlib.sha256(index).hexdigest(),
   "original_zip_sha256":hashlib.sha256(raw).hexdigest(),
   "official_bulk_url":url,"source_update_date":record.get("DateUpdate"),
   "item":"wheat","crop_code":15,"elements":{"5312":"harvested_area","5419":"yield","5510":"production"},
   "countries":panel,"unit_conversion":"hg/ha divided by 10000 = metric tons per ha",
   "directly_measured_global_crop_yield":False,
   "independent_satellite_crop_area_validation":False,
   "spatial_support":"WHOLE COUNTRY: must not be joined directly to gridded NOAA rainfall rectangle",
   "quality_flags_included":True,"crop_model_calibrated":False}
 target=root/"reports";target.mkdir(exist_ok=True)
 (target/"faostat_wheat_country_observations.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"status":report["status"],"rows":{k:len(v) for k,v in panel.items()},
                   "sha256":report["original_zip_sha256"]},indent=2))
 return report
if __name__=="__main__":run()
