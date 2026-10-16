import datetime,tempfile,unittest
from pathlib import Path
try:
 from netCDF4 import Dataset,date2num
except ImportError:
 Dataset=None
from src.nasa_grace_secure_ingest import inspect

@unittest.skipIf(Dataset is None,"Scientific NetCDF dependency required")
class NASAProtectedWaterObservationTests(unittest.TestCase):
 def make(self,path,unit="cm"):
  with Dataset(path,"w") as nc:
   nc.createDimension("time",24);nc.createDimension("lat",2);nc.createDimension("lon",2)
   time=nc.createVariable("time","f8",("time",))
   time.units="days since 2019-01-01"
   dates=[datetime.datetime(2019+(m-1)//12,(m-1)%12+1,15) for m in range(1,25)]
   time[:]=date2num(dates,time.units)
   water=nc.createVariable("lwe_thickness","f4",("time","lat","lon"))
   water.units=unit
   water[:,:,:]=0.
 def test_real_grace_schema_and_calendar(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"grace.nc";self.make(path)
   x=inspect(path)
   self.assertEqual(x["months"],24)
   self.assertEqual(x["first_month"],"2019-01")
   self.assertEqual(x["last_month"],"2020-12")
   self.assertTrue(x["relative_storage_only"])
 def test_refuse_mislabeled_precipitation_as_grace_storage(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/"grace.nc";self.make(path,"mm/day")
   with self.assertRaisesRegex(ValueError,"unit"):
    inspect(path)
if __name__=="__main__":unittest.main()
