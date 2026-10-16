import unittest
from src.physical_water_food_accounting import (
    BasinAnnualWaterBudget, CropHarvestBudget, water_regime_accepted
)
class ConservationLawTests(unittest.TestCase):
    def test_water_mass_conservation_mm_to_km3(self):
        budget=BasinAnnualWaterBudget(
            basin_area_km2=1000.,precipitation_mm=1000.,
            evapotranspiration_mm=600.,outlet_discharge_mm=300.,
            gross_withdrawals_mm=150.,return_flows_mm=100.
        )
        self.assertAlmostEqual(budget.expected_storage_change_mm(),50.)
        self.assertAlmostEqual(budget.expected_storage_change_km3(),.05)
    def test_observation_spatial_mismatch_fails_closed(self):
        budget=BasinAnnualWaterBudget(1000.,1000.,600.,300.,150.,100.)
        with self.assertRaisesRegex(ValueError,"spatial"):
            budget.compare_gravity_storage(10,15,1)
        result=budget.compare_gravity_storage(10,15,1,same_spatial_support=True)
        self.assertAlmostEqual(result["residual_mm"],0.)
    def test_water_negative_flux_rejected(self):
        with self.assertRaisesRegex(ValueError,"nonnegative"):
            BasinAnnualWaterBudget(100.,0.,0.,0.,-1.,0.)
    def test_crop_harvest_mass_and_trade_balance(self):
        crop=CropHarvestBudget(100.,4.,imported_t=50.,exported_t=100.,
            seed_feed_t=20.,storage_losses_t=10.,net_stock_change_t=30.)
        self.assertAlmostEqual(crop.harvested_mass_t(),400.)
        self.assertAlmostEqual(crop.available_mass_t(),290.)
    def test_negative_available_crop_rejected(self):
        with self.assertRaises(ValueError):
            CropHarvestBudget(10.,1.,exported_t=100.).available_mass_t()
    def test_conservation_identity_cannot_pass_prediction_gate(self):
        self.assertFalse(water_regime_accepted(True,True,True,False))
        self.assertTrue(water_regime_accepted(True,True,True,True))
if __name__=="__main__":unittest.main()
