# External surface-temperature evaluation — Met Office HadCRUT5 v5.2 (16 October 2026)

**Result: NOT independently validated for forecasting.** This is a distinct institutional observation product, but NASA and Met Office historical ocean temperature observations partly overlap. Model outcomes from 2015–2024 were previously examined in this project: this is exploratory cross-product confirmation of error, not a new blinded experiment.

## Real-world source
The latest Met Office **HadCRUT.5.2.0.0** global annual temperature-anomaly series is downloaded directly from:
https://www.metoffice.gov.uk/hadobs/hadcrut5/data/HadCRUT.5.2.0.0/analysis/diagnostics/HadCRUT.5.2.0.0.analysis.summary_series.global.annual.csv

The raw CSV bytes, SHA-256, source identity and all 45 annual temperature anomalies for 1980–2024 are archived with the [successful climate physical research CI execution](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38951863932).

## Forecast and evaluation design
The joint NASA surface-temperature and NOAA ocean-heat model is fitted through December 2014. NOAA/IGCC future forcing is extrapolated from the training era rather than reading measured future forcing. HadCRUT5 **never enters model training or prediction**. Because NASA GISTEMP uses a 1951–1980 anomaly reference while HadCRUT uses 1961–1990, one constant offset is fitted between the historical products **using only 1980–2014 overlapping data**. The offset is then frozen before evaluating HadCRUT5 2015–2024, along with fixed-2014 and training-only linear-trend baselines.

| Model against Met Office HadCRUT5 2015–2024 | MAE °C | RMSE °C | Bias °C |
| --- | ---: | ---: | ---: |
| Joint global physical EBM, NASA and NOAA training only | 0.195386 | 0.227910 | -0.195386 |
| Frozen last training temperature | 0.228236 | 0.264869 | -0.228236 |
| Training-only temperature trend | **0.167447** | **0.202812** | -0.167447 |

The two-layer model improves on a frozen-temperature benchmark but remains worse than a trivial training-period linear trend. The model underpredicts the held-out decade in both NASA and Met Office reference products. **No operational forecasting gate is cleared**; passing CI establishes that the numerical experiment ran, not that the physics or uncertainties are calibrated.

## Remaining scientific barriers
- Shared SST records mean this is cross-product evaluation rather than a fully independent measurement network.
- Dataset vintages are retrospective (HadCRUT5 v5.2 released in 2026, forcing IGCC 2025), not archived “as-known-2014” values.
- A ten-year global outcome is one correlated time trajectory, not ten independently randomized forecasts.
- The EBM ocean-state conversion uses a fitted effective fraction and does not establish vertically resolved 0–2000m ocean physics, energy-budget closure or independently calibrated parametric uncertainty.
- No independent regional tests; no future climate scenarios or risk probabilities authorized.

Source: [Implementation](../src/hadcrut_independent_climate_test.py), [regression tests](../tests/test_hadcrut_independent_climate.py), [CI evidence](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38951863932).

Next definitive physical criteria: constrain state heat capacities/exchange against **independent 0–2000m and deep-ocean inventory** data with explicit overlap and uncertainty covariance; test with clean pre-registered unseen data and new release vintages; evaluate spatial skill under ISIMIP4a-style forcing and regional masks. Do not adjust parameters based on the 2015–2024 test and then count that test as independent.
