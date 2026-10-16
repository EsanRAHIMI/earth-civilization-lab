"""Audit source lineage, observed-value integrity and annual forecasting feasibility.

A successful audit certifies *data integrity only*, never model skill or physics.
No source is relabelled independent merely because it has a different API host.
"""
import collections
import csv
import hashlib
import json
import math
import pathlib
import statistics
from src.multisector import INDICATORS

UPSTREAM = {
    "climate_ghg_per_capita": "World Bank GHG estimate; emissions PRESSURE, not observed climate state",
    "freshwater_withdrawals": "FAO AQUASTAT via World Bank; not GRACE water storage or river flow",
    "food_production_index": "FAOSTAT via World Bank; not independently measured crop yields",
    "cereal_yield": "FAOSTAT / national agricultural statistics via World Bank; upstream overlap possible",
}
ROLE = {
    "climate_ghg_per_capita": "anthropogenic_emissions_proxy",
    "freshwater_withdrawals": "water_abstraction_pressure_proxy",
    "food_production_index": "agricultural_output_index_proxy",
}
TARGET_NAMES = tuple(ROLE)

def inspect_observations(root):
    root = pathlib.Path(root)
    path = root / "data/multisector_observations.csv"
    manifest_path = root / "data/multisector_manifest.json"
    if not path.is_file() or not manifest_path.is_file():
        raise FileNotFoundError("World Bank panel and manifest must both exist")
    manifest = json.loads(manifest_path.read_text())
    if manifest.get("panel_sha256") != hashlib.sha256(path.read_bytes()).hexdigest():
        raise ValueError("Observed panel SHA-256 does not match retrieval manifest")
    sources = manifest.get("sources", [])
    if not sources:
        raise ValueError("No retrieval provenance in manifest")
    verified = []
    for entry in sources:
        name = entry["indicator"]
        raw_name = "country_metadata.json" if name == "country_metadata" else name + ".json"
        raw_path = root / "data/multisector_raw" / raw_name
        if not raw_path.is_file():
            raise FileNotFoundError("Missing immutable source snapshot: " + raw_name)
        actual_hash = hashlib.sha256(raw_path.read_bytes()).hexdigest()
        if actual_hash != entry["sha256"]:
            raise ValueError("Raw source hash mismatch: " + raw_name)
        verified.append({"name": name, "sha256": actual_hash, "url": entry.get("url"), "retrieved_utc": entry.get("retrieved_utc")})
    series = collections.defaultdict(dict)
    seen = set()
    country_set = set(manifest.get("countries", []))
    with path.open(newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"country", "year", "indicator", "value", "unit", "source_code", "sector"}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError("Observed panel is missing required provenance fields")
        for line, row in enumerate(reader, 2):
            name = row["indicator"]
            if name not in INDICATORS:
                raise ValueError("Unregistered indicator in row " + str(line))
            code, unit, sector = INDICATORS[name]
            if (row["source_code"], row["unit"], row["sector"]) != (code, unit, sector):
                raise ValueError("Unit/source/sector mismatch at row " + str(line))
            country = row["country"]
            if country not in country_set:
                raise ValueError("Country absent from source metadata at row " + str(line))
            year = int(row["year"])
            value = float(row["value"])
            if not math.isfinite(value):
                raise ValueError("Nonfinite observation at row " + str(line))
            key = (country, year, name)
            if key in seen:
                raise ValueError("Duplicate country-year-indicator: " + str(key))
            seen.add(key)
            series[(country, name)][year] = value
    metrics = {}
    for name in INDICATORS:
        groups = [values for (country, indicator), values in series.items() if indicator == name]
        years = [year for values in groups for year in values]
        consecutive = sum(1 for values in groups for year in values if year + 1 in values)
        lag_two = sum(1 for values in groups for year in values if year - 1 in values and year + 1 in values)
        gaps = [b - a for values in groups for a, b in zip(sorted(values), sorted(values)[1:])]
        metrics[name] = {
            "observations": len(years),
            "countries": len(groups),
            "first_year": min(years) if years else None,
            "last_year": max(years) if years else None,
            "consecutive_annual_pairs": consecutive,
            "consecutive_three_year_windows": lag_two,
            "median_report_gap_years": statistics.median(gaps) if gaps else None,
            "max_report_gap_years": max(gaps) if gaps else None,
            "physical_role": ROLE.get(name, "socioeconomic_or_agricultural_proxy"),
            "underlying_source_lineage": UPSTREAM.get(name, "See World Bank series metadata; not independently adjudicated"),
        }
    return {
        "status": "source_bytes_and_observation_schema_verified",
        "panel_sha256": manifest["panel_sha256"],
        "country_count": len(country_set),
        "total_observations": len(seen),
        "sources": verified,
        "indicators": metrics,
        "independent_provider_validation": False,
        "climate_state_observed_by_ghg_indicator": False,
        "water_storage_observed_by_withdrawal_indicator": False,
        "world_food_security_observed_by_food_index": False,
        "scenario_ready": False,
        "notes": [
            "Reported annual frequency does not imply every country is annually observed.",
            "FAO via World Bank and the same FAO product direct are not independent truth sources.",
            "Complete-case six-sector selection can bias geography and time; sector cohorts must be reported.",
            "No causal or long-horizon skill claim follows from integrity checks.",
        ],
    }

def run(root="."):
    root = pathlib.Path(root)
    report = inspect_observations(root)
    out = root / "reports"
    out.mkdir(exist_ok=True)
    (out / "scientific_data_lineage.json").write_text(json.dumps(report, indent=2))
    print(json.dumps({"status": report["status"], "country_count": report["country_count"], "critical_series": {k: report["indicators"][k] for k in TARGET_NAMES}}, indent=2))
    return report

if __name__ == "__main__":
    run()
