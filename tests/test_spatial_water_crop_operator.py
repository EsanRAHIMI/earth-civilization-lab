import math,unittest
from src.spatial_water_crop_operator import (Cell,aggregate_region,
 basin_balance_mm,water_storage_change_from_grace,crop_region_production_tonnes,
 crop_weather_features)

class SpatialPhysicalWaterCropTests(unittest.TestCase):
 def make(self):
  a=Cell("A",0,1,0,1,1,1);b=Cell("B",0,1,1,2,1,1)
  return a,b
 def test_equal_area_area_weighted_mean(self):
  a,b=self.make()
  polygon=a.included_area_km2()+b.included_area_km2()
  result=aggregate_region((a,b),{"A":10.,"B":20.},"mm",polygon)
  self.assertAlmostEqual(result["area_mean"],15.)
  self.assertEqual(result["status"],"observed_area_mean")
 def test_missing_fraction_not_fabricated(self):
  a,b=self.make();area=a.included_area_km2()+b.included_area_km2()
  result=aggregate_region((a,b),{"A":10.},"cm",area)
  self.assertIsNone(result["area_mean"])
  self.assertEqual(result["status"],"insufficient_coverage")
 def test_polygon_area_disagreement_fails(self):
  a,b=self.make()
  with self.assertRaisesRegex(ValueError,"area disagreement"):
   aggregate_region((a,b),{"A":10.,"B":20.},"mm",5000.)
 def test_land_crop_fraction_changes_area_not_value(self):
  land=Cell("C",0,1,0,1,.5,.8)
  self.assertAlmostEqual(land.included_area_km2(),land.area_km2()*.4)
 def test_grace_storage_change_uses_cm_to_mm(self):
  result=water_storage_change_from_grace({"2020-01":-2.5,"2020-12":-1.3},"2020-01","2020-12")
  self.assertAlmostEqual(result["delta_storage_mm"],12.)
  self.assertFalse(result["is_absolute_groundwater_volume"])
 def test_missing_month_not_imputed(self):
  with self.assertRaisesRegex(ValueError,"Missing GRACE"):
   water_storage_change_from_grace({"2020-01":1.},"2020-01","2020-12")
 def test_internal_withdrawals_not_double_counted_in_basin(self):
  self.assertAlmostEqual(basin_balance_mm(1000.,600.,300.),100.)
  self.assertAlmostEqual(basin_balance_mm(1000.,600.,300.,50.,20.),130.)
 def test_crop_area_yield_mass_identity(self):
  self.assertEqual(crop_region_production_tonnes(500,2.5),1250.)
 def test_crop_daily_phenology_calculated_not_fabricated(self):
  daily=[(f"2020-06-{i:02d}",20.,37.,2.) for i in range(1,31)]
  x=crop_weather_features(daily)
  self.assertAlmostEqual(x["growing_degree_days_c_day"],555.)
  self.assertAlmostEqual(x["heat_excess_c_day"],60.)
  self.assertAlmostEqual(x["seasonal_precipitation_mm"],60.)
if __name__=="__main__":unittest.main()
