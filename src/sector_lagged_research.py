"""Leakage-controlled sector-specific lagged research benchmark.

Exploratory historical backtest: full *country AND time* separation, repeated
fixed evaluation splits, identical complete-case cohorts for candidate models.
NOT a physical or deployable forecast: predictor publication lags are unknown,
and the same historical vintages have been examined during model development.
"""
import collections
import csv
import json
import math
import pathlib
import random
import statistics
from src.historical_calibration import solve

SECTOR_FEATURES = {
    "climate": ("climate_ghg_per_capita", ("electricity_access", "real_gdp_per_capita", "population")),
    "water": ("freshwater_withdrawals", ("electricity_access", "real_gdp_per_capita", "population")),
    "food": ("food_production_index", ("cereal_yield", "real_gdp_per_capita", "population")),
}
SPLITS = ((2013, 2016, 2019), (2016, 2019, 2023))
SEEDS = (1103, 2107, 3109, 4111, 5113)
MIN_TRAIN, MIN_VALIDATION, MIN_TEST = 25, 10, 10

def read_full_panel(path):
    """Read every registered World Bank indicator, not just the old six targets."""
    panel = collections.defaultdict(dict)
    with pathlib.Path(path).open(newline="") as stream:
        for record in csv.DictReader(stream):
            value = float(record["value"])
            if not math.isfinite(value):
                raise ValueError("Nonfinite predictor in raw panel")
            key = (record["country"], int(record["year"]))
            name = record["indicator"]
            if name in panel[key]:
                raise ValueError("Repeated country-year-indicator")
            panel[key][name] = value
    return panel

def cohort(panel, sector):
    target, drivers = SECTOR_FEATURES[sector]
    result = []
    for (country, year), current in sorted(panel.items()):
        previous = panel.get((country, year - 1), {})
        future = panel.get((country, year + 1), {})
        if not (target in current and target in previous and target in future):
            continue
        keys = (target,) + drivers
        if not all(k in current and current[k] > 0 and math.isfinite(current[k]) for k in keys):
            continue
        if previous[target] <= 0 or future[target] <= 0:
            continue
        # First two log features: x(t), x(t-1); all drivers observed at t only.
        x = (math.log(current[target]), math.log(previous[target])) + tuple(math.log(current[k]) for k in drivers)
        result.append((country, year + 1, x, math.log(future[target])))
    return result

def fitted(rows, mode, penalty=0.):
    if mode == "persistence":
        return lambda x: x[0]
    if mode.startswith("trend_"):
        coefficient = float(mode.split("_", 1)[1])
        return lambda x: x[0] + coefficient * (x[0] - x[1])
    if mode not in ("own_ridge", "driver_ridge"):
        raise ValueError("Unregistered model " + mode)
    if len(rows) < 10:
        raise ValueError("Too few training observations")
    # Ridge learns change residual. Normalize ONLY on training observations.
    def raw(x):
        values = [x[0], x[0] - x[1]]
        if mode == "driver_ridge":
            values.extend(x[2:])
        return values
    width = len(raw(rows[0][2]))
    means = [statistics.mean(raw(r[2])[i] for r in rows) for i in range(width)]
    scales = [statistics.pstdev(raw(r[2])[i] for r in rows) or 1. for i in range(width)]
    def design(x):
        z = raw(x)
        return [1.] + [(z[i] - means[i]) / scales[i] for i in range(width)]
    matrix = [[0.] * (width + 1) for _ in range(width + 1)]
    rhs = [0.] * (width + 1)
    for _, _, x, y in rows:
        z = design(x)
        target = y - x[0]
        for i in range(len(z)):
            rhs[i] += z[i] * target
            for j in range(len(z)):
                matrix[i][j] += z[i] * z[j]
    for i in range(1, width + 1):
        matrix[i][i] += penalty
    beta = solve(matrix, rhs)
    return lambda x: x[0] + sum(b * z for b, z in zip(beta, design(x)))

def options():
    candidates = [("persistence", 0.)]
    candidates += [("trend_" + str(alpha), 0.) for alpha in (.25, .5, 1.)]
    candidates += [(mode, p) for mode in ("own_ridge", "driver_ridge") for p in (1., 10., 100.)]
    return candidates

def errors(rows, predict):
    values = []
    for country, target_year, x, actual_log in rows:
        pred_log = max(-50, min(50, predict(x)))
        # Stable, symmetric APE for positive values, via tanh of log ratio.
        error = 200 * abs(math.tanh((pred_log - actual_log) / 2))
        values.append((country, target_year, error))
    return values

def bootstrap_improvement(base, model, seed, draws=1200):
    # Both score arrays refer to precisely the same country/year cohort.
    if [(r[0], r[1]) for r in base] != [(r[0], r[1]) for r in model]:
        raise ValueError("Paired comparison cohort mismatch")
    by_country = collections.defaultdict(list)
    for a, b in zip(base, model):
        by_country[a[0]].append(a[2] - b[2])
    names = sorted(by_country)
    if len(names) < 5:
        return {"ci95_percentage_points": None, "countries": len(names), "claim_supported": False}
    rng = random.Random(seed)
    sims = []
    for _ in range(draws):
        selected = [rng.choice(names) for _ in names]
        sims.append(statistics.mean(v for name in selected for v in by_country[name]))
    sims.sort()
    ci = [sims[int(.025 * (draws - 1))], sims[int(.975 * (draws - 1))]]
    return {"ci95_percentage_points": [round(v, 5) for v in ci], "countries": len(names), "claim_supported": ci[0] > 0}

def execute(rows, seed, train_end, valid_end, test_end):
    countries = sorted({r[0] for r in rows})
    shuffled = list(countries)
    random.Random(seed).shuffle(shuffled)
    held = set(shuffled[:max(6, len(shuffled) // 5)])
    dev = [r for r in rows if r[0] not in held and r[1] <= train_end]
    valid = [r for r in rows if r[0] not in held and train_end < r[1] <= valid_end]
    test = [r for r in rows if r[0] in held and valid_end < r[1] <= test_end]
    audit = {"seed": seed, "train_end": train_end, "validation_end": valid_end, "test_end": test_end,
             "n_train": len(dev), "n_validation": len(valid), "n_test": len(test),
             "held_countries": len(held), "test_countries": len({r[0] for r in test})}
    if min(len(dev) / MIN_TRAIN, len(valid) / MIN_VALIDATION, len(test) / MIN_TEST) < 1 or len({r[0] for r in test}) < 5:
        return dict(audit, status="insufficient_data", accepted=False)
    candidates = options()
    selection = []
    for name, penalty in candidates:
        prediction = fitted(dev, name, penalty)
        value = statistics.mean(r[2] for r in errors(valid, prediction))
        selection.append((value, name, penalty))
    best = min(selection)
    # Strictly demand improvement in validation to replace persistence.
    persistence_score = next(s for s in selection if s[1] == "persistence")[0]
    if best[0] >= persistence_score - 1e-8:
        best = next(s for s in selection if s[1] == "persistence")
    training = dev + valid
    selected = fitted(training, best[1], best[2])
    baseline = fitted(training, "persistence")
    model_errors = errors(test, selected)
    baseline_errors = errors(test, baseline)
    model_smape = statistics.mean(e[2] for e in model_errors)
    base_smape = statistics.mean(e[2] for e in baseline_errors)
    estimate = bootstrap_improvement(baseline_errors, model_errors, seed + valid_end)
    audit.update({
        "status": "exploratory_out_of_country_and_time_test",
        "selected_model": best[1],
        "ridge_penalty": best[2],
        "validation_smape": round(best[0], 5),
        "validation_persistence_smape": round(persistence_score, 5),
        "test_smape": round(model_smape, 5),
        "test_persistence_smape": round(base_smape, 5),
        "test_improvement_percentage_points": round(base_smape - model_smape, 5),
        "uncertainty": estimate,
        # Repeated examined vintages cannot yield independent confirmatory evidence.
        "accepted": False,
        "confounded_by_repeated_historical_model_development": True
    })
    return audit

def run(root="."):
    root = pathlib.Path(root)
    panel = read_full_panel(root / "data/multisector_observations.csv")
    report = {"status": "exploratory_multiorigin_geographic_temporal_backtest",
              "design": "country-disjoint, time-disjoint, target-specific complete-case with exactly observed 1- and 2-year lags",
              "comparison": "identical cohort for each candidate per fold",
              "publication_time_asof_validated": False,
              "independent_provider_validated": False,
              "confirmatory_new_vintage_holdout": False,
              "scenario_ready": False,
              "metrics": {}}
    for sector in SECTOR_FEATURES:
        rows = cohort(panel, sector)
        checks = [execute(rows, seed, *fold) for fold in SPLITS for seed in SEEDS]
        evaluated = [c for c in checks if c["status"].startswith("exploratory_")]
        report["metrics"][sector] = {
            "target_indicator": SECTOR_FEATURES[sector][0],
            "lagged_drivers": list(SECTOR_FEATURES[sector][1]),
            "eligible_rows": len(rows),
            "eligible_countries": len({r[0] for r in rows}),
            "evaluated_folds": len(evaluated),
            "not_evaluable_folds": len(checks) - len(evaluated),
            "positive_skill_folds": sum(c["test_improvement_percentage_points"] > 0 for c in evaluated),
            "positive_lower_ci_folds": sum(c["uncertainty"]["claim_supported"] for c in evaluated),
            "folds": checks,
            "evidence_accepted": False,
        }
    report["scientific_limitations"] = [
        "Climate target is GHG emissions, not observed temperature or atmospheric physical state.",
        "Water target is FAO-sourced withdrawal pressure, not basin water balance.",
        "Food target is FAO-sourced aggregate index, not nutrition or food security.",
        "Previously inspected annual data prevent confirmatory inference from repeated folds.",
        "Operational release-time availability and independent provider agreement are unverified.",
        "Cross-sector coefficients are predictive correlations, never identified causal effects.",
    ]
    out = root / "reports"
    out.mkdir(exist_ok=True)
    (out / "sector_lagged_research.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({s: {k: v for k, v in data.items() if k != "folds"} for s, data in report["metrics"].items()}, indent=2))
    return report

if __name__ == "__main__":
    run()
