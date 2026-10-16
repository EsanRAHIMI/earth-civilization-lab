import csv
import io
import math
import unittest
from src.climate_aggi_physical_hindcast import (
    parse_noaa_aggi, extrapolate_forcing, integrate_forcing, START, TRAIN_END, TEST_END
)

class AGGIPhysicalForecastTests(unittest.TestCase):
    def synthetic_noaa(self, corrupted=False):
        out=io.StringIO()
        writer=csv.writer(out)
        writer.writerow(["Year","CO2","CH4","N2O","CFC","HCFC","HFC","Total","CO2eq","AGGI","pct"])
        for y in range(1979,2025):
            target=3.110 if y==2014 else 3.539 if y==2024 else 1.9+.023*(y-1979)
            # Synthetic fixture only; does not pretend to reproduce measured NOAA series.
            factors=[.67,.16,.07,.08,.01,.01]
            parts=[target*w for w in factors]
            if corrupted and y==2014:parts[0]+=1
            writer.writerow([y,*parts,target,500,1.5,1])
        return out.getvalue().encode()
    def test_noaa_2024_reference_and_component_sum(self):
        observations=parse_noaa_aggi(self.synthetic_noaa())
        self.assertAlmostEqual(observations[2014],3.110)
        self.assertAlmostEqual(observations[2024],3.539)
    def test_mass_balance_rejects_edited_component(self):
        with self.assertRaisesRegex(ValueError,"reconcile"):
            parse_noaa_aggi(self.synthetic_noaa(corrupted=True))
    def test_future_ghg_values_not_consumed(self):
        observed={y:2+.025*(y-START) for y in range(START,TEST_END+1)}
        a,_=extrapolate_forcing({y:v for y,v in observed.items() if y<=TRAIN_END},TEST_END)
        corrupted=dict(observed)
        for y in range(TRAIN_END+1,TEST_END+1):corrupted[y]=9999.
        b,_=extrapolate_forcing({y:v for y,v in corrupted.items() if y<=TRAIN_END},TEST_END)
        self.assertEqual(a,b)
        self.assertTrue(all(v<10 for v in list(a.values())))
    def test_two_layer_forcing_responds_to_forcing(self):
        years=list(range(START,TRAIN_END+1))
        none=integrate_forcing({y:0. for y in years},years,1.2,.2)
        increasing=integrate_forcing({y:2.+.01*(y-START) for y in years},years,1.2,.2)
        self.assertTrue(all(abs(v)<1e-10 for v in none.values()))
        self.assertGreater(increasing[TRAIN_END],0)
    def test_unphysical_negative_exchange_rejected(self):
        with self.assertRaises(ValueError):
            integrate_forcing({START:2.},[START],1.,-.1)
if __name__=="__main__":unittest.main()
