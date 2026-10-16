import tempfile,unittest,calendar
from pathlib import Path
try:
 import numpy as np
 from netCDF4 import Dataset,date2num
except ImportError:
 Dataset=None
from src.gpcp_spatial_precipitation import decode_region

@unittest.skipIf(Dataset is None,"netCDF4 required in spatial science CI")
class SpatialGPCPTests(unittest.TestCase):
 def test_unit_conversion_area_and_exact_monthly_completeness(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"synthetic.nc"
   with Dataset(path,"w",format="NETCDF4") as nc:
    nc.createDimension("lat",3);nc.createDimension("lon",3);nc.createDimension("time",12)
    latitude=nc.createVariable("lat","f4",("lat",));latitude[:]=[0.,2.5,5.]
    longitude=nc.createVariable("lon","f4",("lon",));longitude[:]=[100.,102.5,105.]
    ts=nc.createVariable("time","f8",("time",));ts.units="days since 2005-01-01"
    import datetime
    ts[:]=date2num([datetime.datetime(2005,m,15) for m in range(1,13)],ts.units)
    rainfall=nc.createVariable("precip","f4",("time","lat","lon"))
    rainfall.units="mm/day";rainfall[:,:,:]=2.
   with Dataset(path) as nc:
    records,metadata=decode_region(nc,{"lat":[0,5],"lon":[100,105]},2005,2005)
   self.assertAlmostEqual(records[2005],730.)
   self.assertEqual(metadata["gpcp_grid_count"],9)
 def test_invalid_units_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   path=Path(tmp)/"synthetic.nc"
   with Dataset(path,"w") as nc:
    nc.createDimension("lat",2);nc.createDimension("lon",2);nc.createDimension("time",1)
    nc.createVariable("lat","f4",("lat",))[:]=[0.,2.]
    nc.createVariable("lon","f4",("lon",))[:]=[100.,102.]
    t=nc.createVariable("time","f8",("time",));t.units="days since 2005-01-01"
    v=nc.createVariable("precip","f4",("time","lat","lon"));v.units="meters"
   with Dataset(path) as nc:
    with self.assertRaisesRegex(ValueError,"mm/day"):
     decode_region(nc,{"lat":[0,2],"lon":[100,102]},2005,2005)
if __name__=="__main__":unittest.main()
