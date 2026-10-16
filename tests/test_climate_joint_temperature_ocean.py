import unittest
from src.climate_joint_temperature_ocean import (
    two_layer,heat_equivalent_zj,measured_ohc,ZJ_CONVERSION
)
class CoupledHeatTests(unittest.TestCase):
    def test_energy_unit_conversion(self):
        self.assertGreater(ZJ_CONVERSION,10.)
        self.assertLess(ZJ_CONVERSION,12.)
        states={2005:(0.,0.),2006:(1.,.1)}
        q=heat_equivalent_zj(states,2005,2006,8.,100.)
        self.assertAlmostEqual(q,ZJ_CONVERSION*18.)
    def test_no_unphysical_parameters(self):
        with self.assertRaises(ValueError):
            two_layer({2005:1.},[2005],1.,0.)
        with self.assertRaises(ValueError):
            two_layer({2005:1.},[2005],1.,.1,8.,-100.)
    def test_consecutive_annual_energy_response(self):
        years=list(range(1980,2015))
        states=two_layer({y:1. for y in years},years,1.2,.3)
        self.assertGreater(states[2014][0],states[1980][0])
        self.assertGreater(states[2014][1],0.)
    def test_future_observed_forcing_is_not_an_input(self):
        from src.climate_igcc_full_forcing import projected_components
        observations={y:{"anthro":1.+(y-1980)*.05,"solar":.1,"volcanic":0.,
                        "total":1.1+(y-1980)*.05} for y in range(1980,2025)}
        before,_=projected_components({y:observations[y] for y in range(1980,2015)},2024)
        observations.update({y:{"anthro":900.,"solar":900.,"volcanic":900.,
                                "total":2700.} for y in range(2015,2025)})
        after,_=projected_components({y:observations[y] for y in range(1980,2015)},2024)
        self.assertEqual(before,after)
if __name__=="__main__":unittest.main()
