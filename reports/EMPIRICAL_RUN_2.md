# EarthLab empirical run 2 — evidence record
Date: 2026-10-13 UTC
Run: https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38444008964
Commit: f09c0b483609fc8918e2bab9405a0367b2e2163a
Conclusion: success
Observed in GitHub job logs:
- Python unit tests: 3 passed.
- World Bank retrieval: 1000 non-null observations across 10 configured countries, four indicators, 2000–2024.
- Raw-data and panel integrity checks: passed.
- Historical holdout evaluation: 40 country/indicator groups.
- Artifact ID: 11836154176, SHA-256 15500609f9e3f385565e02f8367fa67c770446db1d30511a71d3a320355f07fe
- Evidence archive: https://github.com/EsanRAHIMI/earth-civilization-lab/actions/runs/38444008964/artifacts/11836154176

## Interpretation
This is a *frozen-last-observation baseline*, not a calibrated integrated Earth-system simulation. The metrics are reported in their native units, and no pooled MAE across incompatible units is scientifically meaningful.

## Required corrections before stronger claims
1. Compare to drift and trend baselines; rolling-origin evaluation and uncertainty intervals.
2. Identify World Bank metadata, vintage, revision and indicator definitions (especially CO2).
3. Separate retrospective evaluation from genuine prospective forecasting: API values are contemporary revisions, so training data through 2015 are not necessarily historical vintages.
4. Add independent source validation (UN population, Global Carbon Budget, IEA) and spatial/environmental modules.
5. Document uncertainty, missingness, model structural validity, sensitivity, governance and conflict mechanisms.
6. Do not claim thousand-year survival probabilities or civilization model validation from these results.
