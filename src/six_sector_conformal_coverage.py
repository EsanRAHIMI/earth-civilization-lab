"""Separate-model split-conformal empirical coverage study for annual World Bank proxies.

This study MUST NOT be presented as coverage of the separately refitted
dashboard predictor: models have different training/calibration splits.
"""
import json
import math
import pathlib
import random
import statistics
from src.six_sector_observed_hindcast import read_panel, samples, fit, fit_change, evaluate, TARGETS

def qceil(values, coverage=.9):
    xs = sorted(values)
    if not xs:
        raise ValueError("No calibration errors")
    k = min(len(xs)-1, max(0, math.ceil((len(xs)+1)*coverage)-1))
    return xs[k]

def candidate(mode, p, training):
    if mode == "persistence":
        return lambda x: list(x)
    if mode == "level":
        return fit(training, p)[0]
    return fit_change(training, p, mode)

def run(root="."):
    root = pathlib.Path(root)
    rows = samples(read_panel(root / "data/multisector_observations.csv"))
    countries = sorted({r[0] for r in rows})
    random.Random(20261016).shuffle(countries)
    n = max(6, len(countries) // 5)
    test = set(countries[:n])
    cal = set(countries[n:n + max(6, (len(countries)-n)//5)])
    dev = set(countries) - test - cal
    train = [r for r in rows if r[0] in dev and r[1]+1 <= 2015]
    validation = [r for r in rows if r[0] in dev and 2016 <= r[1]+1 <= 2018]
    retrain = [r for r in rows if r[0] in dev and r[1]+1 <= 2018]
    calibration = [r for r in rows if r[0] in cal and 2019 <= r[1]+1 <= 2023]
    evaluation = [r for r in rows if r[0] in test and 2019 <= r[1]+1 <= 2023]
    if min(map(len, (train, validation, retrain, calibration, evaluation))) < 20:
        raise ValueError("Insufficient geographic-temporal country-disjoint calibration sample")
    specs = [("persistence", 0.)]
    specs += [(name, p) for name in ("own", "joint", "level") for p in (.1, 1., 10., 100.)]
    scores = {}
    for name, p in specs:
        key = name + ":" + str(p)
        scores[key] = evaluate(validation, candidate(name, p, train))
    results = {}
    for i, sector in enumerate(TARGETS):
        key = min(scores, key=lambda k: scores[k][sector]["model_smape_percent"])
        name, parameter = key.split(":")
        fitted_model = candidate(name, float(parameter), retrain)
        cal_residuals = [abs(fitted_model(x)[i]-y[i]) for _, _, x, y in calibration]
        radius = qceil(cal_residuals)
        covered = [abs(fitted_model(x)[i]-y[i]) <= radius for _, _, x, y in evaluation]
        results[sector] = {
            "selected_predictor_in_this_study": key,
            "log_scale_half_width": radius,
            "multiplicative_interval_factor": math.exp(radius),
            "calibration_pairs": len(cal_residuals),
            "test_pairs": len(covered),
            "empirical_coverage": statistics.mean(covered),
            "target_coverage": .9,
            "calibrated_on_disjoint_countries": True,
            "test_is_later_than_training": True,
            "matches_dashboard_predictor": False
        }
    report = {
        "status": "separate_country_time_disjoint_conformal_study",
        "method": "validation-selected regression, symmetric log-residual split conformal",
        "results": results,
        "training_period": "<=2018 after 2016-2018 model selection",
        "calibration_and_test_period": "2019-2023; countries disjoint from train and one another",
        "train_countries": len(dev),
        "calibration_countries": len(cal),
        "test_countries": len(test),
        "training_pairs": len(retrain),
        "validation_pairs": len(validation),
        "coverage_of_public_holdout_selected_model": False,
        "independent_provider": False,
        "warning": "Different fitted estimators and splits from the dashboard selected holdout. Coverage numbers must not be interpreted as that predictor's calibrated intervals. Exchangeability not established; historical observed-input one-step hindcast only."
    }
    folder = root / "reports"
    folder.mkdir(exist_ok=True)
    (folder / "six_sector_conformal_coverage.json").write_text(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))
    return report

if __name__ == "__main__":
    run()
