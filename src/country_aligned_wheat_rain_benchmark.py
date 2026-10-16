"""Real country-polygon-clipped NOAA precipitation × FAOSTAT wheat yield benchmark.

Country geometry is the low-resolution Natural Earth 110m edition, so small
islands/disputed boundaries and edge-cell precision remain uncertain. Country
averaged rainfall is NOT crop-field rainfall; no in-season forecast is claimed.
Historical FAOSTAT yields and rainfall have retrospective publication delay.
"""
import calendar,datetime,hashlib,json,math,pathlib,statistics,urllib.request
from src.faostat_crop_source import COUNTRIES
from src.gpcp_spatial_precipitation import SOURCE as GPCP_SOURCE

GEOMETRY_SOURCE="https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_110m_admin_0_countries.geojson"
COUNTRY_ISO={"India":"IND","Pakistan":"PAK","United States of America":"USA"}
YEARS=range(2005,2024)
def fetch_geometry(fetcher=None):
 if fetcher is None:
  def fetcher(url):
   req=urllib.request.Request(url,headers={"User-Agent":"EarthCivilizationLab scientific research"})
   with urllib.request.urlopen(req,timeout=70) as f:return f.read()
 body=fetcher(GEOMETRY_SOURCE)
 shapes=json.loads(body)
 from shapely.geometry import shape
 countries={}
 for feature in shapes["features"]:
  code=feature["properties"].get("ADM0_A3")
  if code in COUNTRY_ISO.values():
   if code in countries:raise ValueError("Repeated sovereign polygon")
   geom=shape(feature["geometry"])
   if geom.is_empty:raise ValueError("Empty Natural Earth polygon")
   if not geom.is_valid:
    from shapely import make_valid
    from shapely.ops import unary_union
    fixed=make_valid(geom)
    parts=[g for g in getattr(fixed,"geoms",[fixed]) if g.geom_type in ("Polygon","MultiPolygon")]
    if not parts:raise ValueError("No polygon after geometry repair: "+code)
    corrected=unary_union(parts)
    if not corrected.is_valid or abs(corrected.area-geom.area)/max(geom.area,1e-12)>.005:
     raise ValueError("Natural Earth repair changes country area >0.5%: "+code)
    geom=corrected
   countries[code]=geom
 if set(countries)!=set(COUNTRY_ISO.values()):
  raise ValueError("Incomplete country polygon source")
 return countries,body

def pixel_area_weights(nc,polygon):
 import numpy as np
 from shapely.geometry import box
 from pyproj import Geod
 lat=np.asarray(nc.variables["lat"][:],dtype=float)
 lon=np.asarray(nc.variables["lon"][:],dtype=float)
 geod=Geod(ellps="WGS84")
 pixels=[]
 for i,latitude in enumerate(lat):
  if latitude+1.25<polygon.bounds[1] or latitude-1.25>polygon.bounds[3]:continue
  for j,longitude in enumerate(lon):
   normalized=((longitude+180)%360)-180
   if normalized+1.25<polygon.bounds[0] or normalized-1.25>polygon.bounds[2]:continue
   intersection=polygon.intersection(box(normalized-1.25,latitude-1.25,
                                        normalized+1.25,latitude+1.25))
   if intersection.is_empty:continue
   area,_=geod.geometry_area_perimeter(intersection)
   weight=abs(area)
   if weight>0:pixels.append((i,j,weight))
 if not pixels:raise ValueError("Country has no valid GPCP grid intersections")
 return pixels

def annual_country_rainfall(nc,weights):
 import numpy as np
 from netCDF4 import num2date
 rain=nc.variables["precip"]
 if getattr(rain,"units","")!="mm/day":raise ValueError("Incompatible NOAA GPCP unit")
 time=nc.variables["time"]
 dates=num2date(time[:],time.units,only_use_cftime_datetimes=False)
 area=sum(a for _,_,a in weights)
 if area<=0:raise ValueError("Missing polygon area")
 years={}
 for index,stamp in enumerate(dates):
  if stamp.year not in YEARS:continue
  month=int(stamp.month)
  cells=rain[index,:,:]
  total=0.
  for i,j,weight in weights:
   value=float(cells[i,j])
   if not math.isfinite(value) or value<0 or value>100:
    raise ValueError("Invalid/missing clipped GPCP rainfall pixel")
   total+=value*weight
  per_month=total/area*calendar.monthrange(stamp.year,month)[1]
  months=years.setdefault(stamp.year,{})
  if month in months:raise ValueError("Duplicate NOAA rainfall month")
  months[month]=per_month
 output={}
 for year in YEARS:
  months=years.get(year,{})
  if set(months)!=set(range(1,13)):
   raise ValueError("Incomplete monthly country rainfall "+str(year))
  output[year]=sum(months.values())
 return output

def benchmark(panel):
 import numpy as np
 examples=[]
 for country,observations in panel.items():
  annual={r["year"]:r for r in observations}
  for year in range(2006,2024):
   if year not in annual or year-1 not in annual:continue
   current=annual[year];past=annual[year-1]
   if "national_precipitation_mm" not in current:continue
   examples.append((country,year,
      (float(past["yield_t_ha"]),float(current["national_precipitation_mm"])),
      float(current["yield_t_ha"])))
 train=[x for x in examples if x[1]<=2016]
 valid=[x for x in examples if 2017<=x[1]<=2018]
 test=[x for x in examples if 2019<=x[1]<=2023]
 if min(len(train),len(valid),len(test))<6:raise ValueError("Insufficient complete crop/rain paired records")
 def fit(data, use_rain):
  rainavg=statistics.mean(e[2][1] for e in data)
  rainstd=statistics.pstdev(e[2][1] for e in data) or 1.
  names=sorted(COUNTRY_ISO)
  def features(row):
   country,_,(previous,precip),_=row
   return [previous,1.]+([max(-5,min(5,(precip-rainavg)/rainstd))] if use_rain else [])+[
      float(country==n) for n in names[:-1]]
  X=np.asarray([features(row) for row in data],dtype=float)
  y=np.asarray([row[3] for row in data],dtype=float)
  penalty=np.eye(X.shape[1])*10.
  penalty[1,1]=0.
  coef=np.linalg.solve(X.T@X+penalty,X.T@y)
  return lambda row:max(0.,float(np.dot(features(row),coef)))
 baseline=lambda row:row[2][0]
 candidates={"persistence":baseline,
             "prior_yield_country_ridge":fit(train,False),
             "prior_yield_rain_country_ridge":fit(train,True)}
 errors=lambda rows,predict:statistics.mean(abs(row[3]-predict(row)) for row in rows)
 scores={name:errors(valid,p) for name,p in candidates.items()}
 winner=min(scores,key=lambda n:(scores[n],n))
 if winner=="persistence":selected=baseline
 else:selected=fit(train+valid,winner=="prior_yield_rain_country_ridge")
 paired=[{"country":c,"year":y,"truth_yield_t_ha":truth,
          "persistence_t_ha":baseline(row),"selected_t_ha":selected(row)}
         for row in test for c,y,_,truth in [row]]
 selected_mae=errors(test,selected);reference_mae=errors(test,baseline)
 return {"train":len(train),"validation":len(valid),"test":len(test),
         "selected":winner,"validation_mae_t_ha":scores,
         "holdout_mae_t_ha":selected_mae,"persistence_mae_t_ha":reference_mae,
         "beats_persistence":selected_mae<reference_mae-1e-9,
         "holdout_pairs":paired,
         "confirmatory_skill_established":False,
         "model_domain":"retrospective observed same-year national rainfall after measurement; NOT preseason crop forecasts"}

def run(root="."):
 import netCDF4
 root=pathlib.Path(root)
 raw=root/"data/independent_raw"
 ncpath=raw/"noaa_gpcp_v23_monthly.nc"
 faoreport=root/"reports/faostat_wheat_country_observations.json"
 if not ncpath.is_file() or not faoreport.is_file():raise FileNotFoundError("NOAA GPCP or FAOSTAT upstream data missing")
 observation=json.loads(faoreport.read_text())["countries"]
 polygons,geojson=fetch_geometry()
 (raw/"naturalearth_country_polygons_110m.geojson").write_bytes(geojson)
 records={}
 with netCDF4.Dataset(ncpath) as nc:
  for country,iso in COUNTRY_ISO.items():
   geometry=polygons[iso]
   weights=pixel_area_weights(nc,geometry)
   annual_rain=annual_country_rainfall(nc,weights)
   crop=observation[country]
   for entry in crop:
    if entry["year"] in annual_rain:entry["national_precipitation_mm"]=annual_rain[entry["year"]]
   records[country]={"annual_rain_years":len(annual_rain),
                     "clipped_nonzero_gpcp_cells":len(weights),
                     "matched_crop_records":sum("national_precipitation_mm" in row for row in crop),
                     "country_polygon_geodesic_weight_area_km2":sum(w for _,_,w in weights)/1e6}
 result=benchmark(observation)
 report={"status":"national_paired_geographic_rainfall_and_crop_hindcast_exploratory",
   "country_geometry":"Natural Earth 110m admin0 polygons; repairs limited to <=0.5% planar area change",
   "pixel_intersection":"Shapely polygon clipping + WGS84 geodesic area, 2.5deg GPCP precipitation",
   "geometry_source_url":GEOMETRY_SOURCE,
   "geometry_sha256":hashlib.sha256(geojson).hexdigest(),
   "rain_source":GPCP_SOURCE,"rain_sha256":hashlib.sha256(ncpath.read_bytes()).hexdigest(),
   "FAOSTAT_qcl_sha256":json.loads(faoreport.read_text())["original_zip_sha256"],
   "country_alignment":records,"evaluation":result,
   "source_independent_crop_yield_validation":False,
   "land_use_cropland_mask_validated":False,"scenario_eligible":False,
   "caveats":["Natural Earth 110m is coarse, country borders can be disputed",
     "National rainfall includes non-agricultural areas; cropland weighting and irrigation absent",
     "Annual same-year rainfall is a historical covariate and cannot be known preseason",
     "Only three countries and one crop; results too small for independent geographic claim",
     "Reused historical outcomes and FAOSTAT revisions are not a blind evaluation"] }
 dest=root/"reports";dest.mkdir(exist_ok=True)
 (dest/"country_aligned_wheat_rain_benchmark.json").write_text(json.dumps(report,indent=2))
 print(json.dumps({"status":report["status"],"countries":records,
                   "selected":result["selected"],"selected_mae":result["holdout_mae_t_ha"],
                   "baseline_mae":result["persistence_mae_t_ha"]},indent=2))
 return report
if __name__=="__main__":run()
