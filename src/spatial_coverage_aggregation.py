"""Area-weighted global gridded aggregation with explicit missing-data coverage.

Cells are assumed equal angular width and height on a spherical Earth.
A global mean is NOT reported if the valid area is below the threshold.
"""
import math
def aggregate(cells,minimum_coverage=0.9):
 if not 0<minimum_coverage<=1:raise ValueError("Invalid minimum coverage")
 total=valid=weighted=0.
 for cell in cells:
  lat=float(cell["latitude"]);width=float(cell["longitude_width_deg"]);height=float(cell["latitude_height_deg"])
  if not (-90<=lat<=90 and 0<width<=360 and 0<height<=180):raise ValueError("Invalid cell geometry")
  lo=max(-90,lat-height/2);hi=min(90,lat+height/2)
  area=math.radians(width)*(math.sin(math.radians(hi))-math.sin(math.radians(lo)))
  if area<=0:raise ValueError("Nonpositive area")
  total+=area
  value=cell.get("value")
  if value is None:continue
  value=float(value)
  if not math.isfinite(value):raise ValueError("Nonfinite observation")
  weighted+=area*value;valid+=area
 if total<=0:raise ValueError("Empty grid")
 coverage=valid/total
 return {"coverage_fraction":coverage,"area_weighted_mean":weighted/valid if valid and coverage>=minimum_coverage else None,"status":"covered" if coverage>=minimum_coverage else "insufficient_spatial_coverage","warning":"Area-weighted mean over supplied cells only. Full global inference requires a complete global grid, verified units, land/ocean mask and uncertainty propagation."}
