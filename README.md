# Earth Civilization Lab

**Open research infrastructure for reproducible planetary observations, scientific benchmarking, and experimental Earth–society modelling.**

[![Offline research CI](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/workflows/research-quality.yml/badge.svg)](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/workflows/research-quality.yml)
[![Climate experiments](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/workflows/climate-physical-research.yml/badge.svg)](https://github.com/EsanRAHIMI/earth-civilization-lab/actions/workflows/climate-physical-research.yml)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)
[![Cite this research software](https://img.shields.io/badge/Cite-CITATION.cff-informational)](CITATION.cff)

**[Explore the live observatory](https://esanrahimi.github.io/earth-civilization-lab/)** · **[Reproduce experiments](docs/REPRODUCIBILITY.md)** · **[Research roadmap](docs/RESEARCH_ROADMAP.md)** · **[Contribute](CONTRIBUTING.md)** · **[Scientific readiness](docs/OPERABILITY_DECISION_2026-10-17.md)**

> **Scientific disclosure:** This is **not a validated global digital twin** or a dependable climate, water or food forecasting system. Data feeds are partial observations; most predictive experiments are exploratory historical hindcasts. We publish negative outcomes and reject claims of scientific skill without independent evidence.

## Why this project exists

Climate, freshwater, food systems, energy, population and economies interact across scales, but their datasets and evaluation practices are scattered. Earth Civilization Lab aims to provide an **inspectable and extensible research environment** that separates raw observations, tested models and hypothetical scenarios while preserving data lineage, physical units, uncertainty, and reproducibility.

The project is an invitation for researchers to challenge assumptions and improve models—not a claim that the Earth is already accurately simulated.

## What you can inspect today

| Layer | Inputs / methods | Scientific interpretation |
| --- | --- | --- |
| **Planetary observatory** | USGS earthquake feeds, NASA EONET event catalogue, Open-Meteo weather | Public live-*retrieved* feeds, with upstream measurement delays and incomplete coverage |
| **Six-sector observational benchmarks** | World Bank historical indicators, withheld-country and period evaluations | One-step predictive associations, not causal physical couplings |
| **Climate physics** | NASA GISTEMP, NOAA CO₂ and ocean heat, IGCC radiative forcing, Met Office HadCRUT5 | Two-layer energy balance; historical decade tests do not beat strongest temperature trend baseline |
| **Hydrology research** | NOAA GPCP gridded precipitation, basin accounting checks; NASA GRACE ingestion workflow | GRACE spatial corrections and independent basin-water validation still missing |
| **Agriculture research** | FAOSTAT wheat yield/harvested area, NOAA precipitation, country polygon clipping | Valid observed crop records; cross-country crop forecasts not robust |
| **Scientific release gates** | Provenance checks, no-future-leakage tests, blocked regional/time splits, machine-readable verdict | Only observational and exploratory outputs are authorized |

### Representative published **negative** results

- Global temperature, external Met Office HadCRUT5 evaluation for 2015–2024: physical model MAE **0.1954 °C** vs a training-only linear trend **0.1674 °C**. No accepted temperature forecast skill.
- Out-of-country wheat-yield experiments with pre-issue-date covariates: improvements in only **1 of 3** geography-blocked historical folds; no demonstrated transferable crop forecasting.
- Hydrology: basin-level GRACE/GRACE-FO storage assimilation and independent discharge skill **not yet demonstrated**.
- Cross-sector global operational release: **blocked** by missing physics, independent data and genuinely new confirmatory evaluation.

These are *historical exploratory assessments* on already inspected public data, not previously unseen prospective trials. [Read the evidence and operational verdict](docs/OPERABILITY_DECISION_2026-10-17.md).

## Architecture

```text
PUBLIC + SCIENTIFIC INPUTS
 USGS / NASA / NOAA / Met Office / FAOSTAT / World Bank
                 |
                 v
  SOURCE ADAPTERS + PROVENANCE
 original bytes · SHA-256 · units · version · spatial/temporal support
                 |
          +------+------+
          |             |
          v             v
 OBSERVATION UI     RESEARCH ENGINES
 live feed status   physical / statistical models
          |             |
          |     blocked time + region test
          |             |
          +------+------+
                 v
       SCIENTIFIC EVIDENCE STORE
 holdout metrics · uncertainty · negative results · release gates
                 |
                 v
     PUBLIC RESEARCH DASHBOARD
 clear separation: observed ≠ modelled ≠ validated
```

Implementation is intentionally research-oriented: Python models and retrieval workflows, archived experiment artifacts in GitHub Actions, static JavaScript observational UI, and source-specific rather than one giant network-dependent CI. **GitHub Pages is the presentation layer, not an operational compute backend.**

## Run and verify locally

A fresh checkout supports a **no-secrets, no-network** research-quality check:

```bash
git clone https://github.com/EsanRAHIMI/earth-civilization-lab.git
cd earth-civilization-lab
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev]'
python -m compileall -q src tests
python -m unittest discover -s tests -p 'test_research_governance.py' -v
python -m unittest discover -s tests -p 'test_scientific_release_gate.py' -v
```

See [Reproducibility](docs/REPRODUCIBILITY.md) for Windows setup, pinned spatial dependencies, original dataset download workflows, SHA-256 integrity, CI run artifacts, protected NASA Earthdata access, and how to **avoid accidental test leakage**.

## Research and community

The highest-value work is not adding more dashboards or green badges: it is independent physical observations, audited water/energy conservation, crop-specific masks and calendars, spatial/temporal tests, meaningful baselines and fresh blind validation. See [Research roadmap](docs/RESEARCH_ROADMAP.md) and [Scientific architecture](docs/EARTHLAB_RESEARCH_ARCHITECTURE_2026.md).

**We welcome collaborators.** Open a [scientific proposal](https://github.com/EsanRAHIMI/earth-civilization-lab/issues/new/choose), file a reproducible bug, or submit a small PR. Read the [contribution guide](CONTRIBUTING.md), [security policy](SECURITY.md), and [code of conduct](CODE_OF_CONDUCT.md). Negative findings and corrections are first-class contributions.

### Citation, licence and attribution

Software source code is made available under [Apache License 2.0](LICENSE), subject to verification that contributors own the work they submit. **Upstream scientific datasets retain their separate rights** and are not relicensed by this repository.

To cite this code, use GitHub's **Cite this repository** button ([CITATION.cff](CITATION.cff)) and identify the **commit SHA or archived version**. No project DOI or peer-reviewed EarthLab paper is claimed. For scientific results, also cite each underlying data product and version; see [CodeMeta](codemeta.json).

---

*Earth Civilization Lab is an open scientific project in active development. Success means trustworthy independent replication, not a high star count.*
