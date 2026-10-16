"""Area-conservative geospatial water and crop observational operator.

The operator accepts REAL georeferenced cell observations and externally
computed polygon intersection fractions; it neither invents raster values nor
pretends center-point containment is exact polygon clipping. Regridding,
retrieval, QA and licensing are separate, explicitly blocked prerequisites.
"""
from dataclasses import dataclass
import math
from collections import defaultdict

EARTH_RADIUS_KM=6371.0088

@dataclass(frozen=True)
class Cell:
    id: str
    south: float
    north: float
    west: float
    east: float
    land_fraction: float
    area_fraction_in_region: float
    def area_km2(self):
        if not(-90<=self.south<self.north<=90 and -180<=self.west<self.east<=180):
            raise ValueError("Cell coordinates must be valid EPSG:4326 bounds, split antimeridian cells")
        if not(0<=self.land_fraction<=1 and 0<=self.area_fraction_in_region<=1):
            raise ValueError("Unverified land/region fractional overlap")
        return (EARTH_RADIUS_KM**2 * math.radians(self.east-self.west) *
                (math.sin(math.radians(self.north))-math.sin(math.radians(self.south))))
    def included_area_km2(self):
        return self.area_km2()*self.land_fraction*self.area_fraction_in_region

def aggregate_region(cells, values, unit, expected_area_km2, coverage_required=.9):
    """Fractional-area mean. Rejects partial coverage masquerading as region mean.

    expected_area_km2 must be calculated from an INDEPENDENT GIS region polygon,
    not from the observed valid-cell sum. The input values MUST share temporal
    support, reference and units. No silent interpolation or imputation.
    """
    if not unit or not math.isfinite(expected_area_km2) or expected_area_km2<=0:
        raise ValueError("Missing measurement unit or independent polygon area")
    if not 0<coverage_required<=1:
        raise ValueError("Invalid coverage threshold")
    seen=set();eligible_area=0.;valid_area=0.;weighted=0.
    for cell in cells:
        if cell.id in seen:raise ValueError("Overlapping/repeated grid cell identifier")
        seen.add(cell.id)
        area=cell.included_area_km2()
        eligible_area+=area
        if cell.id not in values or values[cell.id] is None:
            continue
        v=float(values[cell.id])
        if not math.isfinite(v):raise ValueError("Nonfinite observed cell")
        valid_area+=area
        weighted+=area*v
    # Polygon/grid area disagreement is reported, not used to rescale silently.
    if not .97<=eligible_area/expected_area_km2<=1.03:
        raise ValueError("Polygon/grid weighted area disagreement greater than 3%")
    coverage=valid_area/expected_area_km2
    return {"unit":unit,"eligible_area_km2":eligible_area,"valid_area_km2":valid_area,
            "polygon_area_km2":expected_area_km2,"area_coverage":coverage,
            "area_mean":weighted/valid_area if valid_area>0 and coverage>=coverage_required else None,
            "status":"observed_area_mean" if coverage>=coverage_required else "insufficient_coverage",
            "spatial_support":"fractional_polygon_and_land_area_weights",
            "regional_uncertainty_calibrated":False}

def water_storage_change_from_grace(monthly_grace, begin_month, end_month):
    """GRACE land-water-equivalent anomalies are centimeters, not fluxes.

    Exact monthly dates (YYYY-MM) and processing-version-matched support are
    mandatory. Never interpret relative anomalies as total storage.
    """
    for date in (begin_month,end_month):
        if date not in monthly_grace:raise ValueError("Missing GRACE monthly observation "+date)
    start=monthly_grace[begin_month];end=monthly_grace[end_month]
    if any(not math.isfinite(float(x)) for x in (start,end)):
        raise ValueError("Nonfinite GRACE observation")
    return {"delta_storage_mm":10*(end-start),"source_unit":"cm liquid water equivalent",
            "target_unit":"mm storage change","is_absolute_groundwater_volume":False}

def basin_balance_mm(precipitation_mm, evapotranspiration_mm, runoff_out_mm,
                     imports_mm=0.,exports_mm=0.):
    """Closed basin total water storage: delta S = P + imports - ET - Q - exports.

    Internal water extraction and internal return flows do NOT alter basin-total
    mass; including them again double-counts basin net balance. All inputs
    use SAME basin, period, mm water-equivalent support.
    """
    data=(precipitation_mm,evapotranspiration_mm,runoff_out_mm,imports_mm,exports_mm)
    if any(not math.isfinite(x) or x<0 for x in data):
        raise ValueError("Negative or nonfinite basin water flux")
    return precipitation_mm+imports_mm-evapotranspiration_mm-runoff_out_mm-exports_mm

def crop_region_production_tonnes(harvested_area_ha,yield_t_ha):
    if not all(math.isfinite(v) and v>=0 for v in (harvested_area_ha,yield_t_ha)):
        raise ValueError("Invalid harvested area/crop yield")
    return harvested_area_ha*yield_t_ha

def crop_weather_features(daily,base_temp_c=10.,heat_threshold_c=35.):
    """Crop-specific phenology must be supplied as pre-fixed daily dates.

    Growing degree-days and cumulative water supply are covariates, not crop
    yield estimates and do not constitute a calibrated crop model.
    """
    if len(daily)<30:raise ValueError("Growing season requires at least 30 actual days")
    seen=set();gdd=hot=rain=0.
    previous=None
    for date,tmin,tmax,p_mm in daily:
        if date in seen or (previous is not None and date<=previous):
            raise ValueError("Daily climate observations must be ordered, distinct")
        seen.add(date);previous=date
        if any(not math.isfinite(v) for v in (tmin,tmax,p_mm)) or tmin>tmax or p_mm<0:
            raise ValueError("Invalid daily climate variables")
        mean=(tmin+tmax)/2
        gdd+=max(0.,mean-base_temp_c)
        hot+=max(0.,tmax-heat_threshold_c)
        rain+=p_mm
    return {"growing_degree_days_c_day":gdd,
            "heat_excess_c_day":hot,"seasonal_precipitation_mm":rain,
            "climate_reanalysis_is_independent_crop_yield_measurement":False}
