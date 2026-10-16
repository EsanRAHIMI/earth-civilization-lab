"""Cross-provider observation audit for physical climate targets, not forecast skill.

NASA GISTEMP temperature, NOAA GML atmospheric CO2 and OWID's ERA5-derived
precipitation must remain three different, unit-labelled observation variables.
Their covariance does not establish causation; overlapping underlying station
assimilation must not be described as strict source independence.
"""
import collections
import csv
import hashlib
import json
import math
import pathlib

def annual_records(path, year_field, value_field, begin=1980, end=2024):
    if not path.is_file():
        raise FileNotFoundError(str(path))
    lines = path.read_text(encoding="utf-8-sig").splitlines()
    if year_field == "Year":
        lines = lines[next(i for i, s in enumerate(lines) if s.startswith("Year,")):]
    data = {}
    for row in csv.DictReader(s for s in lines if s.strip() and not s.lstrip().startswith("#")):
        try:
            year = int(row[year_field]);value=float(row[value_field])
        except (KeyError,TypeError,ValueError):
            continue
        if not begin <= year <= end or not math.isfinite(value):
            continue
        if year in data:
            raise ValueError("Repeated annual climate observation " + str(year))
        data[year] = value
    return data

def run(root="."):
    root = pathlib.Path(root)
    inputs = {
        "surface_temperature": (root/"data/independent_raw/nasa_gistemp_global.csv", "Year", "J-D", "celsius_anomaly_relative_1951_1980", "NASA GISTEMP v4", "global land+ocean temperature anomaly, 1951-1980 reference"),
        "atmospheric_co2": (root/"data/independent_raw/noaa_global_annual_co2.csv", "year", "mean", "ppm", "NOAA GML", "global mean atmospheric CO2 mole fraction"),
        "global_precipitation": (root/"data/independent_raw/global_land_precipitation_annual.csv", "year", "precipitation_mm", "mm_per_year", "ERA5 reanalysis via OWID; not certified land-only", "OWID World precipitation aggregation, exact land/ocean mask unverified"),
    }
    records = {}
    datasets = {}
    for key, (path, year_col, value_col, unit, lineage, support) in inputs.items():
        rows = annual_records(path, year_col, value_col)
        # An independent historical variable needs at least 40 observations
        # for the stated audit window; fail rather than fill missing values.
        if len(rows) < 40:
            raise ValueError("Insufficient physical observation years " + key)
        if key == "atmospheric_co2" and any(not 250 < x < 600 for x in rows.values()):
            raise ValueError("Impossible NOAA CO2 ppm")
        if key == "surface_temperature" and any(not -3 < x < 5 for x in rows.values()):
            raise ValueError("Impossible NASA temperature anomaly")
        if key == "global_precipitation" and any(not 100 < x < 5000 for x in rows.values()):
            raise ValueError("Suspicious global precipitation")
        records[key] = rows
        datasets[key] = {
            "provider_or_product": lineage, "unit": unit, "observations": len(rows),
            "first_year": min(rows), "last_year": max(rows),
            "file_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "missing_years_1980_2024": sorted(set(range(1980,2025))-set(rows)),
            "geographic_support": support,
        }
    overlap = sorted(set.intersection(*(set(data) for data in records.values())))
    if len(overlap) < 40:
        raise ValueError("Climate measurements have insufficient genuine overlap")
    nasa_report_path = root/"reports/nasa_temperature_hindcast.json"
    precip_report_path = root/"reports/precipitation_provenance.json"
    if not nasa_report_path.is_file() or not precip_report_path.is_file():
        raise FileNotFoundError("Missing primary research/source provenance reports")
    nasa = json.loads(nasa_report_path.read_text())
    precip = json.loads(precip_report_path.read_text())
    if nasa.get("nasa_sha256") != datasets["surface_temperature"]["file_sha256"]:
        raise ValueError("NASA raw temperature file does not match downloaded source")
    if precip.get("entity") != "World" or "ERA5" not in precip.get("status","").upper():
        # Upstream independently publishable evidence is unknown: fail closed.
        raise ValueError("ERA5 World precipitation provenance inconsistent")
    result = {
        "status": "three_distinct_physical_climate_variables_harmonized_by_year",
        "observed_overlap_years": overlap,
        "n_overlap": len(overlap),
        "datasets": datasets,
        "source_vintage_immutable_archive_complete": False,
        "original_precipitation_response_archived": False,
        "strict_provider_independence": False,
        "temperature_prediction_independently_validated": False,
        "integrated_physical_climate_model_accepted": False,
        "usable_for_future_scenario_forcing": False,
        "notes": [
            "Temperature anomaly, atmospheric concentration and precipitation are not interchangeable units.",
            "Historical emissions are not future CO2 forcing; NO measured future forcing exists.",
            "NASA GISTEMP and ERA5 partially depend on overlapping observations, so strict independence is not established.",
            "ERA5 precipitation aggregation via OWID has an unverified world/land mask and may be revised.",
            "No independent ocean/land carbon stocks or complete heat budget supplied.",
        ],
    }
    folder = root/"reports";folder.mkdir(exist_ok=True)
    (folder/"climate_multisource_readiness.json").write_text(json.dumps(result,indent=2))
    print(json.dumps({"status":result["status"],"n_overlap":len(overlap),"datasets":datasets,"scientific_validation":False},indent=2))
    return result
if __name__=="__main__":run()
