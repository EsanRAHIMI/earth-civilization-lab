import io,csv,unittest
from src.hadcrut_independent_climate_test import decode

class ExternalHadCRUT5Tests(unittest.TestCase):
 def fixture(self,offset=.3):
  raw=io.StringIO()
  writer=csv.writer(raw)
  writer.writerow(["Time","Anomaly (deg C)","Lower confidence limit","Upper confidence limit"])
  for y in range(1980,2025):
   writer.writerow([y,offset+.01*(y-1980),-1.,1.])
  return raw.getvalue().encode()
 def test_exact_45_years(self):
  data,head=decode(self.fixture())
  self.assertEqual(len(data),45)
  self.assertAlmostEqual(data[2024],.74)
 def test_missing_annual_observations_fails(self):
  lines=self.fixture().splitlines()
  with self.assertRaisesRegex(ValueError,"incomplete"):
   decode(b"\n".join(lines[:-1]))
 def test_not_arbitrary_non_temperature_csv(self):
  with self.assertRaisesRegex(ValueError,"anomaly"):
   decode(self.fixture().replace(b"Anomaly (deg C)",b"Rainfall (mm)"))
if __name__=="__main__":unittest.main()
