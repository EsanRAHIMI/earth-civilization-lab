# Research roadmap: from transparent observatory to scientifically accepted coupled model

**North star:** a community-reproducible, physically grounded and independently tested climate–water–food research platform. Star count, green CI and attractive maps are *not* scientific success criteria.

| Stage | Milestone / practical contribution | Acceptance evidence | Current |
| --- | --- | --- | --- |
| 0 | Source provenance, immutable hashes, disclosure of limits | Source manifests and unit tests | Partial |
| 1 | Independent terrestrial water storage | Real JPL GRACE/GRACE-FO mascons, gain/leakage masks, basin boundary and third-party runoff/discharge | BLOCKED |
| 2 | Crop-specific subnational exposures | Wheat maps, calendars, land-only weather, irrigation and yield measurement uncertainty | BLOCKED |
| 3 | Physical conservation | Storage and energy balance closure across diverse basins/regions | BLOCKED |
| 4 | Nonleaky multi-origin prediction | Spatial + time holdouts fixed *before* tuning; robust skill against strong baselines | BLOCKED |
| 5 | Multisector coupling | Joint constraints, identifiable impacts, and independent multi-step forecasts | BLOCKED |
| 6 | Community reproduction / scholarly release | Third-party repeatability, frozen data DOI, software release DOI, external review | BLOCKED |
| 7 | Operational readiness | Legal data access, API/compute performance, on-call SLO, security, monitoring | BLOCKED |

## High-value research opportunities

**Hydrology:** Authenticate NASA Earthdata and pin GRACE product/version; calibrate masked TWS against precipitation, ET and runoff on precise watersheds with genuine uncertainties. Never infer groundwater alone from total-water anomalies.

**Agriculture:** Move from whole-country rainfall to crop-phenology-aligned wheat exposures, use independent crop masks, and test out-of-region yields against climatology and persistence.

**Climate:** Bind two-layer surface/ocean energy balance to independently calibrated ocean heat uptake and regional observation networks; benchmark forcing and parametric uncertainties. Do not tune to previously consulted 2015–2024 outcomes.

**Infrastructure:** Store licensed datasets with versioned manifests, STAC/CF metadata, reproducible containers and long-term archive identifiers; publication dashboards consume versioned evidence rather than recomputing research claims.

## How to contribute

Open the [scientific issue template](../.github/ISSUE_TEMPLATE/science.yml) with a clear hypothesis, pinned source/version and proposed blocked evaluation. Only after that choose the implementation approach. Review negative outcomes as carefully as positive ones. See [CONTRIBUTING.md](../CONTRIBUTING.md).
