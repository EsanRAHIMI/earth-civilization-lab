# Earth Civilization Laboratory

Reproducible World Bank empirical pipeline. Scientific validation of a civilization model is **not** claimed.

## Execution
GitHub Actions → **EarthLab empirical retrieval and evaluation** → Run workflow. A monthly schedule is configured. Each run uploads evidence artifacts (raw JSON snapshots, hashes, validation and holdout metrics).

## Scope
2000–2024; 10 countries; World Bank population, life expectancy, GDP growth and CO2 per capita. Historical baseline trained through 2015, evaluated 2016–2024. Data failures stop the run; no fabricated replacement.

## Research limitation
A World Bank baseline is not an integrated Earth system model. Source: https://datahelpdesk.worldbank.org/knowledgebase/articles/889392
