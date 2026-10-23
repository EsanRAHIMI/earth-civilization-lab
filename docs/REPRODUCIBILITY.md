# Reproducing Earth Civilization Lab

This guide distinguishes **offline code verification**, **historical scientific data retrieval**, **physical-model evaluation**, and **scientific acceptance**.

## Supported environments

Python 3.11–3.12 is the reference runtime. Start with a clean environment and a fixed git commit. For each paper/claim record `git rev-parse HEAD`, `python --version`, source download time, product version, SHA-256 and the exact CI run ID.

```bash
git clone https://github.com/EsanRAHIMI/earth-civilization-lab.git
cd earth-civilization-lab
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
python -m pip install -e '.[dev]'
python -m compileall -q src tests
python -m unittest discover -s tests -p 'test_research_governance.py' -v
python -m unittest discover -s tests -p 'test_scientific_release_gate.py' -v
python -m unittest discover -s tests -p 'test_coupled_operational_verdict.py' -v
```

These offline commands require no account, source credentials or external data. For a reproducible scientific environment also install `pip install -e '.[spatial]'` (exact versions pinned in `pyproject.toml`). Heavy NASA Earthdata retrieval is optional and requires separate provider authorization.

## Research workflows and evidence

| Research subsystem | Source/data scope | Script / workflow | Scientific status |
| --- | --- | --- | --- |
| Public observational UI | USGS earthquakes, NASA EONET event catalogue, Open-Meteo model-assisted weather | `.github/workflows/deploy-dashboard.yml` | Observational feeds only; fetch time ≠ measurement time |
| Historical cross-sector statistics | World Bank country indicators, raw-byte provenance | `src/multisector.py` / `six-sector-observed.yml` | Statistical one-step hindcast; not causal/physical |
| Physical climate evaluation | NASA GISTEMP, NOAA GML and OHC, Met Office HadCRUT5, pinned IGCC forcing | `climate-physical-research.yml` | Retrospective, no confirmed forecast skill |
| Spatial precipitation | NOAA GPCP monthly, Natural Earth boundaries | `spatial-water-food.yml` | Archived gridded observations, not verified basin storage |
| Crop yield | FAOSTAT QCL wheat, area and yield, audited country-year alignment | `spatial-water-food.yml` | Three-country exploratory hindcast; no robust out-of-country skill |
| Basin storage | NASA JPL GRACE/GRACE-FO protected observations | `nasa-grace-water.yml` | Authentication/data/correction missing, block physical validation |
| Coupled release decision | Results of external climate, crop and water gates | `coupled-operational-verdict.yml` | Fail-closed: operational forecasts blocked |

Some providers return mutable historical revisions, time out, require auth, or prohibit redistribution. The original workflow artifacts and SHA digests are **part of the experimental record**; avoid treating new downloads as the same frozen dataset. GitHub artifacts expire, so an externally archived DOI snapshot is still needed for stable research citation. Source-data terms always take precedence over this project's Apache-2.0 code license.

## Isolating scientific validation

Do **not** run an empirical `src/pipeline.py fetch` step as a PR gate: it creates variable, network-dependent measurements. Separate deterministic source-free CI from schedule/manual retrieval. Data workflows should upload report JSON + source hashes even on failure, but **must not** display failed code as validated science.

Use separate development/validation/test geographical regions and years; freeze evaluation before feature/parameter search. Never use a target-year observation as a feature for a forecast issued before that observation. Repeatedly consulting 2015–2024 means these outcomes can no longer be presented as unexamined confirmatory truth.

## Expected refusal cases

- Raw NetCDF country or basin polygon mask missing → no claim about basin mass/GRACE storage.
- Upstream FAOSTAT and WDI statistics describe the same primary source → not independent validation.
- Only one or two successful blocked folds → no generalizable out-of-country skill.
- Excellent score on a dataset inspected during model selection → exploratory, not prospectively confirmed.
- Github Action **green** → numerical experiment executed; scientific readiness unaffected until gates actually pass.

## Citing results

Cite source DOIs, Git commit and workflow run, source-year/product vintage and data checksum. For this software use GitHub's **Cite this repository** button generated from [CITATION.cff](../CITATION.cff). A permanent software DOI has **not** been assigned; archive an authorized release through Zenodo only after provenance and licensing review.
