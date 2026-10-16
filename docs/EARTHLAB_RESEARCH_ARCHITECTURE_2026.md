# Earth Civilization Lab — scientific reconstruction and global operation specification

**Version:** 2026-10-16; **status:** engineering and research design, NOT a certified global digital twin.  
**Research objective:** Build a reproducible, independently assessed, multi-resolution Earth-and-society modelling environment. Publish negative results. Do not conflate the public observation map, historical statistical emulators, conservation-law models, and scenario experiments.

## 1. External standards, methods and reference programmes

- **ISIMIP4 (released August 2026)** / ISIMIP3a: consistent historical forcing, impact model intercomparison, controlled counterfactual experiments, and explicit past versus future protocols: https://www.isimip.org/protocol/ ; https://www.isimip.org/about/
- **ILAMB** (Collier et al., 2018, *JAMES*, DOI 10.1029/2018MS001354): observed-data benchmarking of land, carbon, hydrology and atmospheric processes; validate annual means, trends, variability and spatial differences independently: https://www.ilamb.org/doc/index.html
- **GCOS / WMO Essential Climate Variables and 2024 monitoring principles**: maintain measurement provenance, time/space representation, calibration, inhomogeneity and uncertainty: https://gcos.wmo.int/site/global-climate-observing-system-gcos/essential-climate-variables/about-essential-climate-variables
- **ERA5** (ECMWF/Copernicus; DOI 10.24381/cds.f17050d7): global physics-constrained reanalysis with known revision delay; not identical to a station measurement: https://www.ecmwf.int/en/forecasts/datasets/era5-monthly-averaged-data-single-levels-1940-present
- **NASA GRACE/GRACE-FO terrestrial water storage anomaly**: a gravity-derived storage anomaly combining groundwater, surface water, snow and soil moisture, *not* annual freshwater withdrawal: https://podaac.jpl.nasa.gov/dataset/TELLUS_GRAC_L3_CSR_RL06_LND_v04
- **UN World Population Prospects 2024**: cohort-component demographic reference and methodology; a physically different system from current annual population proxy: https://www.un.org/development/desa/pd/world-population-prospects-2024
- **Destination Earth / ECMWF**: operational digital-twin reference architecture comprising compute, a data lake, multi-resolution physical models and co-designed application services. EarthLab has none of the same HPC or accepted scientific capability today: https://www.ecmwf.int/en/newsletter/180/earth-system-science/destination-earths-digital-twins-and-digital-twin-engine
- **FAIR** (Wilkinson et al. 2016, DOI 10.1038/sdata.2016.18); **OGC API Features** and **STAC 1.1** as targets for public science assets: https://www.nature.com/articles/sdata201618 ; https://www.ogc.org/standards/ogcapi-features/ ; https://www.ogc.org/standards/stac/

## 2. Scientific ontology: do not confuse state, pressure, stock and flux

| Domain | Present WB proxy | Required state/flux targets | Independent observational references |
| --- | --- | --- | --- |
| Climate | tCO2e per person (emissions pressure) | near-surface temperature anomaly K; precipitation mm; CO2 atmospheric ppm; ocean heat J; carbon stocks PgC | NASA GISTEMP, ERA5/CRU, NOAA GML, NOAA ocean heat; independent satellite products |
| Water | withdrawals / internal resources % | terrestrial water storage equivalent cm; soil water; freshwater flux m3/s; withdrawals m3/year | GRACE/GRACE-FO, ERA5-Land, river gauging and, separately, AQUASTAT |
| Food | FAO food production index | harvested area ha, crop-specific yields t/ha, output t, nutrient availability, yield failure | FAOSTAT, independent satellite agricultural crop maps; monitor common national reporting provenance |
| Energy | electricity access % | generation / demand / supply TWh, primary energy EJ, CO2 intensity | IEA / Ember source-vetted generation and national inventories |
| Population | WB total persons | age-sex cohorts, births, deaths, migration flows | UN WPP, national census releases (watch common statistical dependence) |
| Economy | GDP per capita | sectoral production, real GDP, trade/price dynamics, damages | National accounts / IMF / WB; distinguish estimates from measurements |

**Independence rule:** World Bank food production data originate at FAO; downloading the same FAO time series is an upstream provenance check, not a second independent ground truth. Similarly AQUASTAT-derived WDI withdrawals are not independently replicated by downloading AQUASTAT again. Related reanalysis products assimilating shared inputs also do not provide strict source independence.

## 3. Scientific construction programme

### Layer A — immutable observation and reproducibility
For each asset record producer, retrieval URL and timestamp, product DOI, processing level, content SHA-256, revision/vintage, variable, unit, coordinate reference system, spatial and temporal support, measurement uncertainty, valid range, missing masks, independence/derivation links, access licence and redistribution constraints. Preserve raw bytes. Reject silently resampled, aggregated or extrapolated data. Perform area-weighted geospatial aggregation with explicit coast/land masks and year-specific boundaries; never average country means unweighted to infer the Earth total. Enforce unit checks, duplication checks, integrity hashes and publication-date as-of logic.

### Layer B — observational targets and scientifically meaningful forcing
Start climate with NASA GISTEMP surface temperature and NOAA CO2 and independently verify a second temperature product; support ERA5 temperature/precipitation with known assimilated dependencies. For water use GRACE/GRACE-FO storage anomaly plus basin-specific discharge, precipitation and actual evaporation; do not use AQUASTAT annual withdrawal as a proxy for observed water *storage*. For food build crop/region yield targets using FAOSTAT and a source-independent geospatial agricultural product; preserve crop-specific harvest calendars and climate lags. A multinational proxy regression is an auxiliary benchmark, not a new physical process model.

### Layer C — model families and identifiability
**Physical:** carbon mass budgets (PgC), two-layer energy budget (W/m2, J/m2, K), basin water balance (P-ET-Q-dS), crop production (area × yield); check finite differences and mass/energy residuals every step. **Empirical:** persistence, seasonal climatology, drift, regularized lagged predictors, nonlinear learners *only when sample size/independent forcing justifies*. **Hybrid:** data assimilation/emulators must inherit explicit physical constraints, provenance and domain-specific validation. For causal interventions require separate identification, controls and counterfactual designs; do not interpret learned cross-domain coefficients as policy effects.

### Layer D — testing without test-set contamination
1. Lock target units and held-out experiment manifests before selection. Freeze exact raw-source snapshot hashes.
2. Geographical generalisation: leave-country/leave-region-out; spatial block rather than random row split.
3. Time generalisation: train <= year T, validate T+1..T+k, test strictly later years, including unseen countries. No future labels from other countries may enter model fitting for a later-year test.
4. Competing baselines must be evaluated on **identical observations**. Report pooled and country-macro error, skill against persistence/climatology, worst-decile regions, number of missing samples and robustness to vintage and country composition.
5. Non-overlapping calibration/test geography with observable prediction interval width and conditional coverage; disclose when coverage refers to a *different* fitted predictor.
6. Country/block bootstrap uncertainty and correction for many candidate comparisons; one successful fold, repeated reinspection of historical vintages, or apparent 90% coverage alone cannot certify a model.
7. Once historical results have influenced model development, these are exploratory. **A fresh, preregistered future data vintage, a blind external benchmark or an independently commissioned holdout is required for confirmatory evaluation.**

### Layer E — scenario system
Physical state variables and forcings must have units; document initial conditions, emissions pathways, land-use/water policy assumptions, counterfactual choices, forcing source and extrapolation envelope. Run ensembles with structural, forcing and parameter uncertainty. Provide region and time-dependent skill domains. Do not expose long-horizon numerical curves as credible forecasts until separately validated free-running multi-step tests pass. Statistical one-year models using observed input at t cannot simply be iterated for 50–1000 years.

### Layer F — real geospatial platform and service delivery
Adopt CF-compliant NetCDF/Zarr gridded assets, STAC discovery, OGC APIs for spatial features, versioned object storage, reproducible compute environment and a data lake. Prefer interoperable xarray/Dask or CDO workflows for spatial analyses, validated conservative regridding, PostGIS for geographic indexing, a job queue for HPC/batch experiments, signed immutable provenance manifests, and API-accessible versioned results. Add alerts for stale data, pipeline failures, unit violations, geographic gaps and drift. Static GitHub Pages is a **presentation layer**, not an operational worldwide compute platform.

## 4. Measurable sequential acceptance gates

| Gate | Minimum evidence | Current status |
| --- | --- | --- |
| G0 Data integrity | raw snapshots + exact hashes, units, upstream lineage, missingness, revision policy | World Bank panel audited in CI; independent sources incomplete |
| G1 Observational validity | multi-source agreement for *identical physical variables*; observational uncertainty | NOT PASSED |
| G2 Predictive skill | frozen spatiotemporal external tests, skill > meaningful baseline with uncertainty, region robustness | NOT PASSED for climate/water/food |
| G3 Physical validity | mass/energy/water conservation budgets and independent stock/flux observation constraints | NOT PASSED |
| G4 Multisector interaction | identified and externally tested coupling and multi-step forecast skill | NOT PASSED |
| G5 Scientific reproducibility | third-party execution, complete manifests, DOI and scholarly peer review | NOT PASSED |
| G6 Production operations | observable service SLOs, stable data licensing, incident recovery, API and scale testing | NOT PASSED |

A pipeline green check means code and evidence-generation steps executed, *not* a G1–G6 scientific acceptance certificate.

## 5. Empirical findings that must not be concealed

2026-10-16: In a five-seed, two-time-window exploratory benchmark using actual observed historical WB values, the climate emissions proxy improved in 1/10 blocked evaluations, water withdrawals in 0/10 and food production index in 2/10; positive country-block lower confidence bound in 0/10 for each. All experimental historic vintages were visible during development. This justifies replacing the underlying physical-variable/data model rather than searching more hyperparameters for green indicators. These counts are not 10 statistically independent experiments.

## 5a. Verified physical climate-data milestone (2026-10-16)

The empirical workflow successfully aligned **45 exact common annual years (1980–2024)** of NASA GISTEMP v4 global surface-temperature anomaly (°C relative to 1951–1980), NOAA GML globally averaged atmospheric CO2 (ppm), and an ERA5-derived OWID World precipitation aggregation (mm/year, spatial land-only masking unverified). All three input files were hashed and no missing year was silently fabricated. These are **three different physical quantities**, not three independent observations of the same target; the upstream observation/assimilation lineage may overlap. The current precipitation pipeline does not archive all original upstream response bytes, so fully immutable reanalysis provenance remains incomplete.

The existing two-layer temperature *conditional hindcast* (fit through 2014, evaluated against NASA 2015–2024) obtained **MAE 0.12561 °C**, versus **observed prior-year NASA persistence MAE 0.11700 °C** and **training-only linear trend MAE 0.17321 °C**. It does **not** beat persistence. Critically, the physical integration uses **measured test-year NOAA CO2**; it is not a blind future forecast. It omits non-CO2 greenhouse gases, aerosols, solar and volcanic forcing. These results block validation claims while identifying concrete physical-variable targets for rebuilding.

The physical accounting code now encodes basin water mass conservation and crop harvest mass identities with explicit units, return flows, imports/exports, area conversion and fail-closed spatial-support checks. **Passing conservation identity unit tests is not evidence that basin or crop forecasts are calibrated.**

## 6. Strict immediate backlog and dependencies

**P0 completed this cycle:** source-hash/data-contract audit, target-specific exactly observed t-1/t lags, country-and-time blocked folds, train-only standardization, common per-sector evaluation cohorts, country-block resampling, research reports in CI, public evidence table, deployment artifact path repair.

**P1 next gate:** ingest and validate actual global NASA/ERA5 temperature and precipitation records, GRACE/GRACE-FO terrestrial storage, FAO + *different-origin* agricultural satellite yield/area, with source/version/rights/uncertainty verified. Align observational scales rather than blindly joining national annual proxies.

**P2 next gate:** physically dimensioned climate, basin water and crop-yield modules with documented conservation equations, independent observational constraints and parameter identifiability. Compare against established environmental modelling packages/benchmarks.

**P3 next gate:** frozen blind v2 external evaluation and calibrated predictive uncertainty, hierarchical geography; reject modules that do not outperform meaningful climatological/physical baselines.

**P4 conditional:** add physically compatible hydrology/agriculture/energy/demography/economy couplers; decision-support application and scientifically bounded uncertainty-aware scenarios only for accepted model domains.

**P5 conditional:** external scientific audit, performance engineering, globally licensed data, operational service design, publication and public research API.

**Governance:** never change FAILED to PASSED by using persistence as the model; never silently replace a missing observation, transplant carbon flux as carbon stock, or iterate a one-year regression as a 1000-year climate forecast. All model releases must be tied to frozen evidence artifacts and explicitly disclose unresolved blockers.
