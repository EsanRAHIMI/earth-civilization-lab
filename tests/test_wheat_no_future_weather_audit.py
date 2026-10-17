import unittest
from src.wheat_no_future_weather_audit import form_rows,study

class LeakageSafeCropIntegrationTests(unittest.TestCase):
 def fixture(self):
  return {
   country:[{"year":year,"yield_t_ha":3.+.01*(year-2005),
             "national_precipitation_mm":250+5*(year-2005)}
            for year in range(2005,2024)]
   for country in ("India","Pakistan","United States of America")}
 def test_no_year_t_precipitation_in_inputs(self):
  values=self.fixture()
  rows=form_rows(values)
  original=[r for r in rows if r[1]==2019]
  for country in values:
   for point in values[country]:
    if point["year"]==2019:point["national_precipitation_mm"]=99999.
  changed=[r for r in form_rows(values) if r[1]==2019]
  self.assertEqual(original,changed)
 def test_countries_entirely_excluded_from_development(self):
  folds=study(form_rows(self.fixture()))
  self.assertEqual(len(folds),3)
  self.assertTrue(all(f["country_disjoint"] and f["train_before_test"] for f in folds))
  self.assertTrue(all(f["accepted"] is False for f in folds))
if __name__=="__main__":unittest.main()
