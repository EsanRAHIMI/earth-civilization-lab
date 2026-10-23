# Contributing to Earth Civilization Lab

Thank you for helping make Earth-system research reproducible and independently reviewable. We welcome **scientific corrections, negative results, new independent datasets, reproducible tests, security fixes, accessible visualization, and documentation**.

## Choose a contribution

1. **Good first issue:** isolated documentation corrections, reproducible bugs, schema validation, tests.
2. **Scientific model or dataset:** open an issue **before** implementing; identify the physical variable, observation lineage, units, data rights, training/validation/test years, and source-independent comparator.
3. **Data engineering:** add a source manifest with provider, retrieval time, product version, geography/time support, original SHA-256, redistribution rights, measurement uncertainty and missingness.
4. **Visualization:** distinguish live observations, archived datasets, model outputs and experimental scenarios; never label old observations live.

## Quick local setup

Python 3.12+ is recommended. Standard-library smoke tests must run **offline**, without API keys or raw data downloads:

```bash
git clone https://github.com/EsanRAHIMI/earth-civilization-lab.git
cd earth-civilization-lab
python -m compileall -q src tests
python -m unittest discover -s tests -p 'test_research_governance.py' -v
python -m unittest discover -s tests -p 'test_scientific_release_gate.py' -v
python -m unittest discover -s tests -p 'test_coupled_operational_verdict.py' -v
```

For gridded or empirical research, use the dedicated scientific GitHub workflow and source-specific environment: [research reproduction guide](docs/REPRODUCIBILITY.md). Do not run all remote-source workflows as a default unit test.

## Scientific contribution contract

- State a **falsifiable hypothesis** and the observable target (for example temperature anomaly °C, runoff m³/s, basin TWS cm, wheat yield t/ha). Emissions are not global temperature; freshwater withdrawals are not terrestrial water storage.
- Supply an exact, pinned data source and license. Provide retrieval DOI/URL, publication vintage, units, spatial mask, and a deterministic way to regenerate the result.
- Declare the prediction issue date, available-at-issue features, any observational release lag, geographic blocks, temporal cutoff, and the *unchanged comparator cohort*.
- Select hyperparameters using training/validation **only**. Never tune on a public test result and then call it confirmatory.
- Compare to persistence, seasonal climatology, and domain-specific strong benchmarks. Include negative findings and uncertainty, not just R² or a PASS badge.
- Scientific acceptance requires independent evidence **and** domain-specific physical constraints. Passing Python unit tests or GitHub Actions is not scientific acceptance.
- Never enable long-range or decision-grade forecast interfaces without the versioned [release gates](docs/EARTHLAB_RESEARCH_ARCHITECTURE_2026.md).

## Pull-request checklist

Include links to an issue, motivation, source provenance, changed files, exact reproduction commands, expected results/units, test results, downstream impacts, licensing, and limitations. **Reviewers can request independent replication**.

Small PRs are encouraged. Keep raw data and API credentials out of Git: publish allowed snapshots through dataset archives with checksums; keep access-restricted observations behind provider terms.

## Attribution and licensing

Code contributions are accepted under [Apache-2.0](LICENSE) unless an explicit exception is agreed upon. Submit only material you own or are authorized to contribute. Scientific data from NASA, NOAA, FAO, World Bank, ESA, etc. retain **their own source licences and attribution**; the code licence does not relicense upstream data. Cite upstream products and commits/release identifiers in published work; see [CITATION.cff](CITATION.cff).

For responsible vulnerability reports, use [SECURITY.md](SECURITY.md), not a public issue. For respectful collaboration, follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).
