# Earth Civilization Lab

An open, research-stage effort toward reproducible and eventually interoperable Earth–human-system observations, benchmarks and simulation. **This project is NOT a validated global digital twin, physically accepted Earth-system model, real-time planetary census, or scientifically trustworthy 1000-year forecast.**

## What actually works today

- Public observation interface for selected USGS earthquakes, NASA EONET catalogue and location-specific Open-Meteo weather (these feeds have delays and incomplete coverage).
- Historical World Bank country-year observations and narrow statistical one-step hindcasts, with explicit persistence comparisons.
- Source-byte SHA-256 integrity, unit checks and upstream lineage for the World Bank panel.
- Research-only sector-specific models for emissions, freshwater withdrawals and food production index, using exact annual lagged values and country/time-blocked backtests across five fixed country seeds and two temporal windows.
- Country-block bootstrap comparisons, separate conformal interval study and explicit scientific limitation labels.
- CI-published reports with raw retrieval snapshots and manifest; no fabricated missing observations.

## What has **not** been demonstrated

Independent physical climate, freshwater-storage or crop-yield forecast skill; meaningful causal sector interactions; cross-sector conservation; global spatial rasters linked to a validated simulator; free-running multi-year predictability; independently replicated results; scientific peer review; or operational decision reliability. World Bank food/water data inherit upstream FAO sources and are not validated by re-downloading the same upstream estimates.

### The current negative result is scientifically important

In a 2026-10-16 exploratory country-and-time blocked experiment (5 fixed country splits × 2 temporal origins for each target), positive held-out improvement against persistence occurred for emissions in **1/10**, withdrawals in **0/10** and food index in **2/10** splits. Country-block bootstrap lower improvement bounds were positive in **0/10** for each target. Repeated splits are correlated and historical source vintages have already been inspected during development. The results do **not** establish new scientific predictive skill.

## Independent physical climate research benchmark (16 Oct 2026)

A separately reproducible [climate physics research workflow](.github/workflows/climate-physical-research.yml) now retrieves the actual NASA GISTEMP global temperature observations, NOAA GML global annual atmospheric CO2, NOAA AGGI radiative forcing from all long-lived greenhouse gases and the pinned IGCC 2024 global effective radiative-forcing archive (tag v2025.06.11; includes anthropogenic aerosol, solar and volcanic components). Source bytes and SHA-256 hashes are included in a CI artifact.

All three two-layer physical models calibrate through 2014 and simulate 2015-2024 **without feeding observed future atmospheric concentration, forcing or temperature into the forecast**. MAE on the ten-year interval: CO2-only **0.2510 °C**, NOAA AGGI **0.2506 °C**, IGCC total forcing **0.2195 °C**, frozen-2014 baseline **0.2340 °C**, training-only historical linear temperature trend **0.1732 °C**. The IGCC experiment improves over the former physically incomplete CO2-only model, but **still fails to beat the linear-trend baseline**. The 2015-2024 historical holdout is exploratory, not a new sealed prospective experiment, and forcing from a retrospective 2025 product is not an as-of-2014 vintage.

Full physical formulation, data DOIs, fixed experimental configuration and exclusions: [Climate frozen-2014 experiment](docs/CLIMATE_2014_FROZEN_PHYSICAL_BENCHMARK.md). Successful [empirical CI](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38909576456) publishes raw data and all three backtests; the scientific release gate **remains blocked**.

## Joint atmosphere–ocean heat experiment (2026-10-16)

The reproducible [physical climate workflow](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38910826522) additionally downloads **real NOAA NCEI annual 0–700m and 0–2000m World Ocean heat-content records** (no repository fallback used in this execution), simultaneously fits a two-layer global energy balance against NASA surface-temperature anomalies (1980–2014) and NOAA 0–2000m ocean heat (2005–2014), and **free-runs the ten-year 2015–2024 test** without observing test-year atmospheric forcing, surface temperature or ocean heat during fitting or projection.

| 2015–2024 MAE | Fitted joint physics | Frozen 2014 | Train-only trend |
| --- | ---: | ---: | ---: |
| NASA global surface temperature (°C) | 0.2011 | 0.2340 | **0.1732** |
| NOAA 0–2000m ocean-heat anomaly (ZJ) | **6.00** | 55.72 | 14.49 |

The improvement in effective ocean heat is meaningful as a *historical benchmark*, not scientific validation. The two-layer heat state is **not geometrically or physically identical to the observed 0–2000m ocean inventory**, and an effective ocean-storage conversion fraction is inferred on a very short **10-year NOAA training sequence**. This parameter is not physically identified, with no joint full-depth heat closure, no independent uncertainty calibration, and a retrospectively revised forcing archive. The NASA temperature forecast still loses to the training-only trend. Thus deployment/decision scenarios **remain BLOCKED**.

A separate unit/integration test **changes observed NOAA heat labels from 2015 onward by +10,000 ZJ**, and verifies that fit parameters and predicted temperature/ocean-heat curves remain *bit-for-bit identical*. That test passed in the same CI run.

[Model source](src/climate_joint_temperature_ocean.py) · [No-leakage integration test](tests/test_climate_joint_observed_holdout_leakage.py) · [Run and raw evidence artifact](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38910826522)

## First gridded water/crop observational benchmark (2026-10-16)

A new [spatial water-and-food CI](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38950921593) actually ingests official NOAA GPCP satellite/gauge precipitation NetCDF (2005–2023), preserves full source SHA and units, extracts official FAOSTAT wheat crop-specific yield/harvested area/production (with quality flags) and overlays Natural Earth country polygons using geodesic clipping of each 2.5° pixel. This yields complete national-coverage rain/yield observational pairs for India, Pakistan and the USA, not arbitrary rectangle averages.

The **independent-time 2019–2023 exploratory holdout** selected persistence and produced exactly **0.12922 t/ha MAE**, equal to the same-sample persistence baseline. A national annual precipitation covariate **did not demonstrate better crop-yield prediction**. This does not establish crop-field spatial validation or a preseason forecast. GRACE water storage, watershed outlet discharge and crop-specific cropland masks remain missing.

[Complete source provenance, results and acceptance criteria](docs/SPATIAL_WATER_CROP_2026_EVIDENCE.md).

## External Met Office temperature evaluation — 2026-10-16

A separate HadCRUT5 v5.2 Met Office annual-temperature observational product was tested against the NASA/NOAA-trained physical model on the 2015–2024 held-out decade. A reference-period temperature offset was estimated only with <=2014 observations. MAE: physical model **0.19539 °C**, frozen-2014 **0.22824 °C**, and train-only linear trend **0.16745 °C**. **The physical model does not beat the trend and is not externally accepted.** Shared source observations and the previously examined historical test mean this is independent-institution cross-product evaluation, *not* independent confirmatory forecasting evidence.

[External Met Office evaluation and precise data provenance](docs/HADCRUT5_EXTERNAL_TEMPERATURE_EVALUATION.md) · [Successful external-source CI run](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38951863932)

## Documentation

- [Scientific architecture, international methods and acceptance criteria](docs/EARTHLAB_RESEARCH_ARCHITECTURE_2026.md)
- [Prior scientific protocol and its limits](docs/SCIENTIFIC_PROTOCOL.md)
- [Independent carbon-stock acquisition blockers](docs/carbon_stock_observation_acquisition.md)
- [Research evidence workflow](.github/workflows/six-sector-observed.yml)
- [Public observational dashboard](https://esanrahimi.github.io/earth-civilization-lab/)

## Reproduce

Python 3.11+ and network access to authoritative sources are required. No model result should be cited without its source-vintage hash and CI run.

```bash
python -m src.multisector
python -m src.science_data_audit
python -m src.six_sector_observed_hindcast
python -m src.sector_lagged_research
python -m src.six_sector_conformal_coverage
python -m unittest discover -s tests -p 'test_science_data_and_lags.py' -v
```

The source audit verifies immutable raw retrieval bytes against a manifest and rejects schema or unit mismatches. The lagged sector evaluation exports `reports/sector_lagged_research.json` and **sets evidence_accepted=false by design**, because confirmatory independent/vintage-out evidence remains missing.

## Scientific communication contract

An operational GitHub Actions success is only a successful *execution*. A positive fold is not a scientifically accepted model. Upstream-overlapping data are not independent validation. A nominal 90% interval coverage number from a separately trained model must never be presented as coverage of the dashboard's selected predictor. Hypothetical scenario sensitivities are not empirical forecasts. The observation map and all visualizations must preserve these distinctions.

Research and external replication contributors should begin with the methodological gaps and acceptance gates in the architecture document. The project welcomes independent scrutiny, including failure reports.
