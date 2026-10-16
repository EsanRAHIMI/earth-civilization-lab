"""Observed grid ingestion from a documented CSV, with missingness and units.

Input cells must represent a complete, non-overlapping latitude-longitude grid
for the intended domain; this routine validates geometry and area coverage only,
not satellite provenance or overlapping geometry.
"""
import csv,json,pathlib
from src.spatial_coverage_aggregation import aggregate
def run(input_path,root=".",minimum_coverage=.9):
 p=pathlib.Path(input_path)
 if not p.is_file():raise FileNotFoundError(p)
 with p.open(newline="") as f:
  reader=csv.DictReader(f)
  needed={"latitude","longitude_width_deg","latitude_height_deg","value","source_url","unit"}
  if not needed.issubset(reader.fieldnames or []):raise ValueError("Missing required grid fields")
  rows=list(reader)
 if not rows:raise ValueError("Empty spatial grid")
 sources={r["source_url"] for r in rows};units={r["unit"] for r in rows}
 if len(sources)!=1 or len(units)!=1 or not next(iter(sources)).startswith("https://"):raise ValueError("Mixed units or unverified provenance")
 cells=[{"latitude":r["latitude"],"longitude_width_deg":r["longitude_width_deg"],"latitude_height_deg":r["latitude_height_deg"],"value":r["value"] if r["value"].strip() else None} for r in rows]
 result=aggregate(cells,minimum_coverage)
 result.update({"source_url":next(iter(sources)),"unit":next(iter(units)),"cells":len(rows),"observed_grid_verified":False,"limitations":["Grid tiling and overlap require external validation","Land/ocean masks and measurement uncertainty not yet included"]})
 root=pathlib.Path(root);out=root/"reports";out.mkdir(exist_ok=True);(out/"spatial_observed_grid.json").write_text(json.dumps(result,indent=2));return result
