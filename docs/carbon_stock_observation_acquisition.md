# Carbon stock observation acquisition plan

The physical acceptance gate requires four independently sourced, annual global carbon stocks with overlapping years: surface-ocean, deep-ocean, vegetation and soil. No current catalogued source provides all four as directly observed global annual inventories.

## Source-to-stock transformation
- Ocean: NOAA GLODAP bottle DIC profiles (https://www.ncei.noaa.gov/access/ocean-carbon-acidification-data-system/oceans/GLODAPv2_2023/). Filter QC, interpolate depth/area/years, integrate seawater carbon inventory, propagate interpolation error. Sparse sampling must be represented as missing years rather than interpolated measurements.
- Vegetation: ESA CCI Biomass (https://climate.esa.int/en/projects/biomass/data/). Annual aboveground woody biomass maps must be area-weighted, converted from dry biomass to carbon using an explicit documented factor, and supplemented with belowground and other vegetation components. Not yet total vegetation stock.
- Soil: ISRIC SoilGrids (https://soilgrids.org/). Gridded soil carbon maps are not annual measurements. Do not repeat static values as annual stocks.
- Ecosystem flux: FLUXNET (https://fluxnet.org/data/). Site fluxes constrain dynamics but cannot directly stand in for global annual carbon stocks.

## Scientific blockers
The current acceptance test cannot be made valid simply by supplying four CSV files. Independent measurement, spatial completeness, consistent stock definitions, at least ten overlapping observed years, and propagated uncertainties must be audited. Do not turn model-derived fluxes into independent stock observations.

## Land sink model correction
Nested validation should include a train-only mean baseline as a candidate during inner validation, alongside ridge regressions. A selected baseline must be reported as a baseline, not as a physically calibrated model. Never select based on the untouched 2015-2024 holdout.
