import math
import unittest
from src.climate_free_running_forecast import (
    annual_co2_extrapolation, integrate, calibrate_physical, START, TRAIN_END
)

class OutOfSampleClimateForecastTests(unittest.TestCase):
    def test_future_co2_is_never_read(self):
        train={y:300*math.exp(.004*(y-START)) for y in range(START,TRAIN_END+1)}
        forecast,metadata=annual_co2_extrapolation(train,TRAIN_END,TRAIN_END+5)
        sabotaged={**train, **{y:99999. for y in range(TRAIN_END+1,TRAIN_END+6)}}
        alternative,_=annual_co2_extrapolation(sabotaged,TRAIN_END,TRAIN_END+5)
        self.assertEqual(forecast,alternative)
        self.assertAlmostEqual(forecast[TRAIN_END+5],300*math.exp(.004*(TRAIN_END+5-START)),places=7)
    def test_nonconsecutive_forcing_fails(self):
        train={y:350. for y in range(START,TRAIN_END+1)}
        del train[2001]
        with self.assertRaisesRegex(ValueError,"Missing"):
            annual_co2_extrapolation(train,TRAIN_END,2024)
    def test_energy_balance_nonfinite_or_nonphysical_parameters_rejected(self):
        data={y:350. for y in range(START,TRAIN_END+1)}
        with self.assertRaises(ValueError):
            integrate(data,[START],0.,.4)
        with self.assertRaises(ValueError):
            integrate(data,[START],1.,-.4)
    def test_constant_CO2_produces_deterministic_warming(self):
        data={y:380. for y in range(START,TRAIN_END+1)}
        a=integrate(data,list(range(START,TRAIN_END+1)),1.2,.3)
        b=integrate(data,list(range(START,TRAIN_END+1)),1.2,.3)
        self.assertEqual(a,b)
        self.assertGreater(a[TRAIN_END],a[START])
    def test_calibration_only_uses_supplied_training_pair(self):
        years=list(range(START,TRAIN_END+1))
        forcing={y:340. for y in years}
        truth=integrate(forcing,years,1.2,.1)
        params=calibrate_physical(forcing,truth)
        self.assertTrue(params["train_mse_c2"]<1e-7)
if __name__=="__main__":unittest.main()
