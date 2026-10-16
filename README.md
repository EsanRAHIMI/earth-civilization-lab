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
