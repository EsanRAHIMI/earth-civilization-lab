# EarthLab: first reproducible geographically aligned water–crop benchmark
**Experiment completed 2026-10-16. Status: exploratory, NOT accepted for forecasting.**

## Published source evidence
1. NOAA GPCP Version 2.3 combined satellite/rain-gauge precipitation, complete monthly observations from 2005 through 2023, originally `mm/day`, accumulated exactly by calendar-month duration to `mm/year`. Official CDR description and DOI: https://www.ncei.noaa.gov/products/climate-data-records/precipitation-gpcp-monthly , DOI 10.7289/V56971M6.
2. FAOSTAT Crops and livestock products QCL original official bulk ZIP, with wheat crop code 15, area harvested element **5312** (`ha`), yield **5412** (`kg/ha` or `hg/ha` normalized to `t/ha`) and observed production **5510** (`t`); preserve per-row data-quality flags. Do not reuse obsolete yield code 5419 in this domain. Original ZIP SHA256: `c5835418c18f9322e7decbd6800f93a216eaae3cdfa31acb08f0518c0c6d6853`.
3. Natural Earth 110m administrative country polygons. Clip each NOAA 2.5-degree geographic cell against exact country geometry, then weight contributions by WGS84 geodesic fractional intersection area, not by cell-center voting or equal number of pixels. Detect and conservatively repair existing invalid Natural Earth geometry only with less than 0.5% planar-area change. Publish the original geometry GeoJSON and a SHA256 digest with the reports.

All original source datasets and the report are preserved in [this successful GitHub CI run](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38950921593). Data may be revised upstream. Each future retrieval gets a new hash and source vintage.

## Actually aligned records

| Country | Intersecting NOAA grid cells | National wheat area/yield observation years | National annual rainfall years |
| --- | ---: | ---: | ---: |
| India | 73 | 19 | 19 |
| Pakistan | 27 | 19 | 19 |
| United States of America | 259 | 19 | 19 |

All rows cover 2005–2023. Spatial support is **full nation**, not a wheat-field mask. Country-average rainfall is not necessarily representative of growing-season precipitation over harvested wheat area. National FAO yields may be official, estimated or imputed: preserve the per-record source Flag. Annual yield timing does not precisely match crop calendars for rain or the official data release date.

## Real withheld-period evaluation

Identical country-year cohorts; development 2006–2016, validation 2017–2018, holdout 2019–2023. Candidates: previous year's wheat yield as persistence; shrinkage regression using last observed yield and country effects; shrinkage regression adding **same-year observed national rainfall**. The model selected **persistence**, and holdout MAE was **0.12922 t/ha** for both the selected and baseline predictors. There was **no gain** from adding this crude precipitation covariate. The country count and validation sample are far too small for credible geography generalization. This is a **retrospective conditional hindcast**, not a harvest-season forecast because the year's rainfall is not available at the beginning of the year. This repeated historical holdout is not confirmatory.

## What is actually needed before scientifically accepted water and food forecasting
- Hydrology: exact basin polygons, evapotranspiration, independent outlet discharge, GRACE/GRACE-FO terrestrial water storage equivalent (with uncertainty/mask/leakage correction), temporal gap logic, explicit basin (P-ET-Q-\Delta S) closure and multi-basin spatial/temporal blocked validation. NASA PO.DAAC GRACE gridded datasets require Earthdata Login or authorised cloud credentials. No GRACE ingestion is certified yet.
- Crops: independent crop-specific cropland/harvested-area maps (ESA WorldCover is *general cropland*, not a wheat map), wheat phenology and growing-season land climate, irrigation, soil/management, the actual dated harvest target, uncertainty, and multiple years of unseen growing-season held-out regions. A global country mean precipitation must not be substituted for a wheat-crop climate exposure.
- Coupled climate–water–food skill: process models with physically compatible variables and forcings, train-only calibration, external observations never used as future input, leave-region AND year-out blind evaluation, hierarchical uncertainty and multiple unexamined data vintages. ISIMIP4a (updated 2026-10-08) is the current common forcing and historical impact-model evaluation framework: https://protocol4.isimip.org/.
- Operational gates: export only versioned observational and exploratory benchmark layers until independent skill, storage budgets and observational uncertainty pass. **Do not publish global crop-yield or water-storage forecast maps** based on these tests.

## Reproduce

```bash
python -m pip install numpy==2.2.6 netCDF4==1.7.2 shapely==2.1.2 pyproj==3.7.2
python -m src.gpcp_spatial_precipitation
python -m src.faostat_crop_source
python -m src.country_aligned_wheat_rain_benchmark
python -m unittest discover -s tests -p test_country_aligned_wheat_rain.py -v
```

All returns fail rather than silently filling missing physical observations. Source archives are large, and the spatial pipeline should move to checksummed immutable object storage for production rather than relying on GitHub artifact retention.
