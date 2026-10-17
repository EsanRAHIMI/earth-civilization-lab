# EARTH CIVILIZATION LAB — Cross-domain release decision
**Date:** 17 October 2026  
**Scope:** Planetary climate/terrestrial water/food operational forecasting.
**Decision:** **NOT ACCEPTED. NO OPERATIONAL GLOBAL DIGITAL TWIN OR PHYSICALLY VALIDATED CLIMATE–WATER–FOOD FORECAST.**

This result derives from the successful end-to-end [cross-domain GitHub Actions execution](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/39023367760) and the binary, machine-readable `coupled_operational_verdict.json`. Successful execution is not successful predictive validation.

## Empirical tests, identical evidence rather than status badges

| Scientific gate | Observed result | Decision |
| --- | --- | --- |
| External surface-temperature skill | NASA/NOAA-trained two-layer model vs separately downloaded Met Office HadCRUT5 v5.2 on 2015–2024: MAE **0.1953858 °C**, strongest train-era-only linear trend **0.1674465 °C** | FAIL |
| Ocean thermal inventory | Model compared to real NOAA 0–2000m OHC; training-era fitting and 2015–2024 historical free-running test accomplished. Effective ocean-storage scaling partly fit; deep heat budget and parameter identifiability not independently established | INCOMPLETE |
| Geospatial crop observational support | NOAA GPCP original monthly NetCDF 2005–2023 + FAOSTAT QCL wheat annual statistics for India, Pakistan and USA; Natural Earth 110m country polygons clipped by geodesic intersection weights | OBSERVATIONS VERIFIED |
| True issue-time crop forecasting | `yield(t-1), national_rainfall(t-1)` to predict `yield(t)`, development 2006–2016, model selection 2017–2018, test 2019–2023 on **entirely unseen country** per fold; 54 eligible historical pairs | **1/3** small positive improvements, no geographically repeatable model skill |
| India crop generalisation | MAE model **0.4018674 t/ha**, persistence **0.0745800 t/ha** | FAIL |
| Pakistan crop generalisation | MAE model **0.0989698 t/ha**, persistence **0.1016600 t/ha** | tiny improvement; not confirmatory |
| USA crop generalisation | Selected persistence **0.2114200 t/ha**, persistence **0.2114200 t/ha** | NO GAIN |
| Independent basin water-storage calibration | NASA JPL GRACE/GRACE-FO ingestion code, scientific-unit checks, Earthdata-authenticated workflow prepared; **no authenticated satellite source retrieval, basin spatial correction, source-independent discharge, uncertainty or calibration result** | NOT DONE |
| Actually coupled climate–water–crop physical dynamics | No shared, jointly calibrated conservation-constrained multi-domain predictor and no unseen prospective climate–water–crop joint outcome | NOT DONE |
| Fresh blind future outcomes | Previously inspected historical NOAA/Met Office/FAO releases reused; 2024/2025 product vintages not observational snapshots frozen as-of 2014 | NOT AVAILABLE |

## Fail-closed safety of scientific use

`scenario_enabled=false`, `operational_global_decisions_authorized=false`, and `accepted_physical_global_digital_twin=false` regardless of green Github Actions status.

The new cross-domain science workflow combines evidence from:
- [NASA/NOAA/Met Office climate run 39023303340](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/39023303340).
- [Blocked-space+time NOAA/FAOSTAT crop run 39023101657](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/39023101657); its NetCDF is **SHA-matched archived historical NOAA source** when upstream server replied HTTP 503, explicitly not fresh observation.
- [Actual cross-domain verdict run 39023367760](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/39023367760), with both input report sources and the machine-readable decision archived together.

A major scientific error in the prior code was fixed: *internal withdrawals and return flows cannot be counted as external fluxes in the total basin water budget* `ΔS = P + imports − ET − Q − exports`. Previous accounting double-counted internal water usage. Its tests now verify correct water-equivalent depths and conversions.

## Current 2026 methods and the next genuine acceptance experiment

For **crop forecasting**, benchmark against the 2026 peer-reviewed **CY-Bench** global subnational crop-yield forecasting data design, with ESA WorldCereal wheat crop maps, harvest calendars, ERA5/AgERA5/GPCP in-season meteorology, field/subnational observed yields and country/year blocked validation. Reference https://essd.copernicus.org/articles/18/3997/2026/. Do not use whole-country annual precipitation as if it were wheat growing-season precipitation. Current FAOSTAT wheat national statistics are useful controls but cannot establish independent crop-map-based regional predictions.

For **water**, target NASA GRACE/GRACE-FO JPL mascon TWS anomalies with explicit gain factors and leakage corrections, independent outlet runoff/discharge, ET and precipitation on hydrological **basin boundaries**, measurement uncertainty and mass balance across several geographically unseen catchments; GRACE effective resolution is hundreds of kilometres and must not be interpreted as field-scale soil moisture. Recent example: https://hess.copernicus.org/articles/30/6057/2026/. The NASA Earthdata authorization workflow exists but without Earthdata token **cannot perform authenticated GRACE calibration**. The correct GitHub secret is `EARTHDATA_TOKEN`; never commit a credential.

For **climate**, include heat-uptake ocean-depth, aerosol forcing uncertainty, multiple independently evaluated regional temperature products and publication-vintage limits; surface-temperature MAE must beat frozen and linear climatological baselines across protected future decades and with uncertainty and physics audits.

For **prospective evidence**, freeze a preregistered model release, hashes, geographic regions, seasons and scoring functions *before obtaining the next still-unobserved release*, then let a different evaluator score incoming observed outcomes once. Multiple historical re-shuffles of the same data cannot become truly unseen by renaming a test file.

**Final scientific conclusion:** This project can responsibly operate as a transparently sourced **observational and experimental research platform** now. It **cannot** yet claim reliable global coupled Earth/human forecasts. An operational-release PASS requires new and different evidence, not stronger prose, more parameter tuning on the same historic folds, or passing code tests.
