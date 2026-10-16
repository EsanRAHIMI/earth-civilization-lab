"""Machine-readable, fail-closed scientific release gate.

Green CI means reproducible execution; model/scenario acceptance requires
additional independently observed physical-state forecasts and external review.
"""
import datetime
import hashlib
import json
import os
import pathlib
import platform

GATES = ("G0_raw_data_integrity", "G1_physical_observation_validity",
         "G2_confirmatory_predictive_skill", "G3_physical_conservation_calibrated",
         "G4_independent_multisector_skill", "G5_external_replication",
         "G6_operational_reliability")

def evaluate_reports(lineage, lagged):
    integrity = (lineage.get("status") == "source_bytes_and_observation_schema_verified"
                 and bool(lineage.get("panel_sha256"))
                 and len(lineage.get("sources", [])) >= 10)
    sectors = ("climate", "water", "food")
    blocking = {}
    for sector in sectors:
        evidence = lagged.get("metrics", {}).get(sector, {})
        blocking[sector] = {
            "proxy": evidence.get("target_indicator"),
            "evaluated_folds": evidence.get("evaluated_folds", 0),
            "positive_skill_folds": evidence.get("positive_skill_folds", 0),
            "bootstrap_positive_lower_bound_folds": evidence.get("positive_lower_ci_folds", 0),
            "has_external_physical_skill_certificate": False,
            "scenario_forecast_authorized": False,
            "required_to_unlock": [
                "genuine physical-state variable with standardized units",
                "independent and matched observation support",
                "blind fresh-vintage or independent-provider skill",
                "calibrated uncertainty with regional robustness",
                "conservation and multi-step free-running evaluation"
            ],
        }
    return {
        "gates": {
            GATES[0]: integrity,
            GATES[1]: False,
            GATES[2]: False,
            GATES[3]: False,
            GATES[4]: False,
            GATES[5]: False,
            GATES[6]: False
        },
        "sector_assessments": blocking,
        "scenario_enabled": False,
        "accepted_global_digital_twin": False,
        "model_output_suitable_for_operational_decisions": False,
        "source_caveat": "Water and food WDI are upstream FAO-based; GHG is an emissions proxy, not climate state",
        "false_positive_prevention": "Historical CI>0 and CI green do not override physical, blind and external release gates."
    }

def run(root="."):
    root = pathlib.Path(root)
    output = root / "reports"
    files = (output/"scientific_data_lineage.json", output/"sector_lagged_research.json")
    if any(not f.is_file() for f in files):
        raise FileNotFoundError("Missing genuine evidence reports; cannot emit readiness status")
    lineage, lagged = (json.loads(f.read_text()) for f in files)
    result = evaluate_reports(lineage, lagged)
    if not result["gates"][GATES[0]]:
        raise RuntimeError("G0 source integrity failed: block all data releases")
    result.update({
        "status": "data_integrity_pass_scientific_release_blocked",
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "git_commit": os.environ.get("GITHUB_SHA", "unverified_local_revision"),
        "python_version": platform.python_version(),
        "source_panel_sha256": lineage["panel_sha256"],
        "report_sha256": {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
    })
    (output/"scientific_release_gate.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({"status":result["status"],"gates":result["gates"],
                      "scenario_enabled":result["scenario_enabled"]},indent=2))
    return result

if __name__=="__main__":
    run()
