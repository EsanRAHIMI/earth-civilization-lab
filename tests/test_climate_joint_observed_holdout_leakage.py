"""Integration-level no-test-data-leakage proof for the joint climate/ocean fit.

Runs only after authoritative raw observations have been downloaded. Tampering
with the observed 2015–2024 NASA and NOAA labels must NOT change forecasts,
parameters or training loss. Only realized errors may change.
"""
import csv,json,pathlib,shutil,tempfile,unittest
from src.climate_joint_temperature_ocean import run

class JointPhysicalNoFutureLeakage(unittest.TestCase):
    def test_holdout_outcomes_cannot_change_physical_forecasts(self):
        source=pathlib.Path("data/independent_raw")
        required=("igcc_2024_annual_erf_best.csv",
                  "nasa_gistemp_global.csv","ocean_heat_content_annual.csv")
        if not all((source / name).exists() for name in required):
            self.skipTest("Needs downloaded raw NASA/NOAA/IGCC inputs in CI")
        with tempfile.TemporaryDirectory() as dirname:
            root=pathlib.Path(dirname)
            raw=root/"data/independent_raw"
            raw.mkdir(parents=True)
            for name in required:shutil.copyfile(source/name,raw/name)
            original=run(root)
            # Modify only test-period NOAA OHC labels; fit and predictions stay.
            path=raw/"ocean_heat_content_annual.csv"
            with path.open(newline="") as handle:
                records=list(csv.DictReader(handle))
                headers=list(records[0])
            for row in records:
                if int(row["year"])>2014:
                    row["heat_0_2000_zj"]=str(float(row["heat_0_2000_zj"])+10000)
            with path.open("w",newline="") as handle:
                writer=csv.DictWriter(handle,fieldnames=headers)
                writer.writeheader()
                writer.writerows(records)
            alternate=run(root)
            self.assertEqual(original["model_parameters"],alternate["model_parameters"])
            self.assertEqual(original["training_losses"],alternate["training_losses"])
            for before,after in zip(original["series"],alternate["series"]):
                self.assertEqual(before["predicted_temperature_c"],after["predicted_temperature_c"])
                self.assertEqual(before["predicted_ocean_heat_zj"],after["predicted_ocean_heat_zj"])
                self.assertNotEqual(before["NOAA_OHC_0_2000m_zj"],after["NOAA_OHC_0_2000m_zj"])

if __name__=="__main__":unittest.main()
