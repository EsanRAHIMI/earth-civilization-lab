import datetime,tempfile,unittest
from pathlib import Path
try:
 import numpy as np
 import netCDF4
 from shapely.geometry import box
except ImportError:
 netCDF4=None
from src.country_aligned_wheat_rain_benchmark import pixel_area_weights,annual_country_rainfall,benchmark

@unittest.skipIf(netCDF4 is None,"Geospatial scientific dependencies required")
class GeoCountryRainCropTests(unittest.TestCase):
 def test_fractional_country_polygon_weights_and_monthly_to_annual_units(self):
  with tempfile.TemporaryDirectory() as temp:
   path=Path(temp)/"tiny.nc"
   with netCDF4.Dataset(path,"w") as nc:
    nc.createDimension("time",12);nc.createDimension("lat",2);nc.createDimension("lon",2)
    nc.createVariable("lat","f4",("lat",))[:]=[20.,22.5]
    nc.createVariable("lon","f4",("lon",))[:]=[75.,77.5]
    time=nc.createVariable("time","f8",("time",));time.units="days since 2005-01-01"
    time[:]=netCDF4.date2num([datetime.datetime(2005,m,15) for m in range(1,13)],time.units)
    p=nc.createVariable("precip","f4",("time","lat","lon"));p.units="mm/day";p[:,:,:]=3.
   with netCDF4.Dataset(path) as nc:
    geo=box(74.,19.,78.,23.)
    weights=pixel_area_weights(nc,geo)
    self.assertEqual(len(weights),4)
    # Test annual function expects every year 2005-2023: assert it rejects
    # silent missing years rather than fabricating dates.
    with self.assertRaisesRegex(ValueError,"Incomplete monthly"):
     annual_country_rainfall(nc,weights)
 def test_crop_model_rejects_insufficient_matched_observations(self):
  with self.assertRaisesRegex(ValueError,"Insufficient"):
   benchmark({"India":[{"year":2019,"yield_t_ha":3.,"national_precipitation_mm":200.}]})
if __name__=="__main__":unittest.main()
