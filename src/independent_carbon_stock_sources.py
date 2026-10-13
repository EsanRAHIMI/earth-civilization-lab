"""Independent carbon-stock dataset provenance and ingestion readiness.

Ocean GLODAP is bottle-sample DIC (umol/kg), NOT global annual carbon
inventory. ESA CCI is above-ground dry biomass (Mg/ha), NOT total vegetation
carbon. SoilGrids SOC is gridded stock/density, NOT annual soil turnover.
Never treat these products as interchangeable annual global stocks.
"""
import json,pathlib
SOURCES={
 'ocean_dic':{'provider':'NOAA OCADS / GLODAPv2.2023','url':'https://www.ncei.noaa.gov/access/ocean-carbon-acidification-data-system/oceans/GLODAPv2_2023/','measurement':'quality-controlled discrete ocean dissolved inorganic carbon','native_units':'umol/kg','required_processing':'quality filter; interpolate with uncertainty by ocean depth and area; integrate with seawater mass; stratify surface/deep; avoid pretending cruise samples are annual global inventories','annual_global_inventory_ready':False},
 'vegetation_agb':{'provider':'ESA CCI Biomass v7','url':'https://climate.esa.int/en/projects/biomass/data/','measurement':'above-ground dry biomass at 100 m and coarser aggregated maps','native_units':'Mg/ha','required_processing':'download annual gridded maps; area-weight spatial integration; convert dry biomass to carbon with documented fraction and uncertainty; add below-ground and non-woody vegetation separately','annual_global_inventory_ready':False},
 'soil_soc':{'provider':'ISRIC SoilGrids','url':'https://soilgrids.org/','measurement':'gridded soil organic carbon stocks by depth','native_units':'tonnes C/ha (layer stock products; verify product units)','required_processing':'obtain gridded stock and depth coverage; area-weight sum with land mask and uncertainty; do not invent an annual trend from static spatial maps','annual_global_inventory_ready':False},
 'gross_flux':{'provider':'FLUXNET / ICOS ecosystem flux observations','url':'https://fluxnet.org/data/','measurement':'site-level ecosystem carbon and energy fluxes','native_units':'variable by product','required_processing':'verify licensing, site coverage and partitioned GPP/respiration; spatial upscaling and uncertainty; cannot directly assume globally observed annual gross flux','annual_global_inventory_ready':False}
}
def run(root='.'):
 root=pathlib.Path(root);out=root/'reports';out.mkdir(exist_ok=True)
 report={'status':'verified_source_catalogued_not_ingested','sources':SOURCES,'independent_global_annual_stocks_ingested':False,'reason':'The sources require scientific spatial integration, unit conversion, coverage and uncertainty handling before global reservoir stock observations can be constructed. Source URLs alone are not measured inventory time series.'}
 (out/'independent_carbon_stock_sources.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report
if __name__=='__main__':run()
