"""Unit-safe basin water accounting and crop mass accounting.

These are conservation identities, NOT a calibrated hydrological or agricultural
predictor. The records explicitly reject mismatched observation supports.
"""
from dataclasses import dataclass
import math

def nonnegative(name, value):
    if not isinstance(value, (float, int)) or not math.isfinite(value) or value < 0:
        raise ValueError(name + " must be a finite nonnegative quantity")
    return float(value)

@dataclass(frozen=True)
class BasinAnnualWaterBudget:
    """All water depths in mm over exactly the same basin polygon/year.

    Withdrawal is gross removal within the basin and must exclude water
    already counted in the external runoff boundary flux; imports/exports
    and return flows are explicit. A GRACE water-storage anomaly is NOT an
    absolute reservoir volume or an observed human withdrawal.
    """
    basin_area_km2: float
    precipitation_mm: float
    evapotranspiration_mm: float
    outlet_discharge_mm: float
    gross_withdrawals_mm: float
    return_flows_mm: float
    external_imports_mm: float = 0.
    external_exports_mm: float = 0.

    def __post_init__(self):
        for name, value in vars(self).items():
            nonnegative(name, value)
        if self.basin_area_km2 == 0:
            raise ValueError("Basin polygon area must be positive")

    def expected_storage_change_mm(self):
        return (self.precipitation_mm + self.return_flows_mm
                + self.external_imports_mm - self.evapotranspiration_mm
                - self.outlet_discharge_mm - self.gross_withdrawals_mm
                - self.external_exports_mm)

    def expected_storage_change_km3(self):
        return self.expected_storage_change_mm() * self.basin_area_km2 / 1000000.

    def compare_gravity_storage(self, begin_anomaly_cm, end_anomaly_cm,
                                combined_uncertainty_cm, same_spatial_support=False):
        """Only compare compatible area/time anomalies, with supplied uncertainty.

        The caller must verify geospatial mask, processing correction and
        consistent temporal support for two GRACE observations.
        """
        if not same_spatial_support:
            raise ValueError("GRACE and basin flux spatial integration supports not independently verified")
        nonnegative("combined_uncertainty_cm", combined_uncertainty_cm)
        for value in (begin_anomaly_cm, end_anomaly_cm):
            if not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Invalid GRACE anomaly")
        observed_mm = (end_anomaly_cm - begin_anomaly_cm) * 10.
        predicted_mm = self.expected_storage_change_mm()
        residual = observed_mm - predicted_mm
        return {
            "observed_storage_change_mm": observed_mm,
            "budget_storage_change_mm": predicted_mm,
            "residual_mm": residual,
            "combined_uncertainty_mm": combined_uncertainty_cm * 10.,
            "within_supplied_one_sigma": abs(residual) <= combined_uncertainty_cm * 10.,
            "interpretation": "single-support accounting comparison; NOT globally validated hydrology",
        }

@dataclass(frozen=True)
class CropHarvestBudget:
    """Production mass identity for ONE crop, geographic area, and harvest year.

    Nutrition, markets, consumption, prices and food security are outside the
    scope of this mass balance.
    """
    harvested_area_ha: float
    realized_yield_t_per_ha: float
    imported_t: float = 0.
    exported_t: float = 0.
    seed_feed_t: float = 0.
    storage_losses_t: float = 0.
    net_stock_change_t: float = 0.

    def __post_init__(self):
        for name, value in vars(self).items():
            if name == "net_stock_change_t":
                if not isinstance(value, (int, float)) or not math.isfinite(value):
                    raise ValueError("Invalid signed stock change")
            else:
                nonnegative(name, value)

    def harvested_mass_t(self):
        return self.harvested_area_ha * self.realized_yield_t_per_ha

    def available_mass_t(self):
        available = (self.harvested_mass_t() + self.imported_t - self.exported_t
                     - self.seed_feed_t - self.storage_losses_t - self.net_stock_change_t)
        if available < -1e-9:
            raise ValueError("Negative available crop mass: inconsistent budget")
        return max(0., available)

def water_regime_accepted(independent_grace_validation, independent_discharge_validation,
                          verified_spatial_weights, multi_origin_skill):
    """Fail-closed gate: an identity alone is never prediction validation."""
    return all((independent_grace_validation, independent_discharge_validation,
                verified_spatial_weights, multi_origin_skill))
