# Climate physical hindcast benchmark — frozen 2014 inputs (2026-10-16)

## The precise scientific question

Can a simple physically dimensioned two-layer global energy-balance model, calibrated to NASA GISTEMP temperature anomalies from 1980 through 2014, predict *all ten years 2015–2024* without accessing measured test-period temperature or measured test-period greenhouse-gas/radiative forcing?

**Answer: not competitively.** The best of three forcing designs remains worse than the training-only linear-trend baseline. This is an exploratory retrospective model evaluation, **not** a deployment-ready climate forecast, and historical outcomes have already been inspected elsewhere in the project.

## Strict evaluation inputs

- NASA GISTEMP v4, 1980–2024 global annual J-D temperature anomaly, Celsius relative to 1951–1980. [NASA dataset](https://data.giss.nasa.gov/gistemp/)
- NOAA Global Monitoring Laboratory global annual mean CO2 concentration, ppm. [NOAA official data](https://gml.noaa.gov/ccgg/trends/gl_data.html)
- NOAA Annual Greenhouse Gas Index (AGGI), effective radiative forcing from all long-lived greenhouse gases relative to preindustrial, W/m2. [AGGI](https://gml.noaa.gov/aggi/aggi.html)
- **Indicators of Global Climate Change 2024**, fixed Git tag v2025.06.11, aggregate anthropogenic forcing (including aerosols), natural solar forcing and volcanic forcing, W/m2. Source paper DOI **10.5194/essd-17-2641-2025**; archival dataset DOI **10.5281/zenodo.15639576**.

The NASA, NOAA and IGCC raw bytes and SHA256 checksums are saved in the dedicated CI artifact. Only 1980–2014 time-slices may enter parameter fitting and forcing extrapolation, even though the downloaded 2024-vintage source files include future observations for later audit.

## Benchmark evidence (MAE, 2015–2024, °C)

| Baseline/model | MAE | Bias | Future measured forcing used? |
|---|---:|---:|---|
| Frozen 2014 NASA temperature | 0.2340 | -0.2340 | No |
| Training-only 1980–2014 linear temperature trend | **0.1732** | -0.1732 | No |
| EBM with projected CO2-only forcing | 0.2510 | -0.2510 | No |
| EBM with projected NOAA AGGI long-lived GHG ERF | 0.2506 | -0.2506 | No |
| EBM with projected IGCC full effective forcing (aerosols, solar, volcanic included) | 0.2195 | -0.2195 | No |

IGCC forcing reduces the absolute model error relative to CO2-only forcing and outperforms the frozen 2014 temperature, but is still worse than the training-only linear trend. **Do not claim net predictive skill, successful validation, causality, or reliable future scenarios.**

## Physics, methods and restrictions

The implicit-Euler energy balance is:

C_s ΔT_s = F - λT_s - γ(T_s - T_d)  
C_d ΔT_d = γ(T_s - T_d).

Time step: one year. Radiative forcing F W/m2. Surface/deep temperature K. Heat capacities W·year/(m²·K). λ and γ W/(m²·K). The implementation searches fixed ranges for λ and γ and learns a NASA anomaly-reference offset on training data only. Heat capacities are assumed, **not independently identified from ocean observations**.

Future forcing is **not known**: CO2 is extrapolated log-linearly from 1980–2014 measurements; NOAA AGGI total GHG forcing is extrapolated from historical trends; IGCC anthropogenic forcing is extrapolated linearly with solar and volcanic components held at training climatological means. Thus IGCC is not a forecast of volcanic eruptions or solar cycles. The historical source is a post-2014 revised release; no true 2014-vintage forcing archive is verified. All EBM outcomes require investigation of aerosols, model structural error, heat uptake and ocean heat content; adding degrees of freedom solely to beat the known holdout is prohibited.

Reference comparative methods: ISIMIP4 / ISIMIP3a forcing-and-impact-model protocols (https://www.isimip.org/protocol/); ILAMB model-versus-observation framework (DOI 10.1029/2018MS001354); IGCC 2024 model-data forcing paper (DOI 10.5194/essd-17-2641-2025).

## Concrete acceptance tasks, in order

1. **Separate parameter identifiability from fitted accuracy.** Retrieve NOAA NCEI ocean heat content and constrain heat capacities and exchange using properly matched ocean heat anomaly and heat-balance definitions, including area conversions and error covariance. A 0–2000m heat anomaly is not full-depth global ocean storage.
2. **Use climate forcing with uncertainty.** Adopt IGCC historical ensemble/5th–95th percentile forcing and external observational errors. Quantify aerosol uncertainty, solar volcanic variability and structural physics uncertainty. Do not treat post-2014 forcing as observable at a hypothetical 2014 forecast issue date.
3. **Predefine new independent evaluation.** Freeze training/model version and wait for new data vintage or external blind evaluation by researchers. Already-examined 2015–2024 results cannot be made confirmatory by further tuning.
4. **Expand spatial/physical validity.** Jointly compare NASA temperature, NOAA OHC and energy imbalance, then evaluate independent land-temperature and regional basin diagnostics.
5. **Reject until peer replication.** Publish full machine-readable results and source hashes, with all failed comparisons and known uncertainties. Do not enable long-term forecast scenarios until the physics and spatiotemporal forecast gates are met.

## Reproduce in isolation

Use GitHub Actions **Climate physical research**, not the much larger unrelated financial/Bitcoin workflow. Its artifact includes the actual NASA, NOAA AGGI, IGCC annual input data and the three JSON benchmark reports. The physics and future-input-leakage tests run before any model fit.

```bash
python -m src.climate_observation_acquire
python -m src.climate_free_running_forecast
python -m src.climate_aggi_physical_hindcast
python -m src.climate_igcc_full_forcing
```
