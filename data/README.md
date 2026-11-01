# Data (not in git)

All data live under `$FINESST_DATA_ROOT` (default: this folder). Only this README is tracked.
What each dataset is for, and its status, is in `context/04_data.md`.

```
$FINESST_DATA_ROOT/
  raw/                     untouched downloads, one folder per source
    ana/                   HidroWeb station archives (stage, discharge, ADCP summaries, cross-sections, water quality)
    inmet/                 weather stations 82410 Benjamin Constant, 82317 Tefé, 82331 Manaus
    era5land/              hourly, 2013–2024, corridor box
    landsat_st/            Collection 2 Level-2 surface temperature extracts (from Earth Engine)
    jrc_gsw/               JRC Global Surface Water occurrence (permanent-water mask)
    sword/                 SWORD v17 reaches and nodes (South America)
    swot/                  SWOT L2 HR RiverSP (optional)
    hydrolakes/            HydroLAKES v1.0 polygons
    camrex/                CAMREX basin, sub-basins and river network (ORNL DAAC)
    naturalearth/          1:50m admin-0 countries (for maps)
    insitu/                published or shared field temperatures (Johannsson 2026, Fleischmann 2025)
  interim/                 cleaned, reach-aggregated intermediates
  processed/               model inputs and outputs used in figures
```

On Anshul's laptop, older copies of SWORD, CAMREX, HydroLAKES, GRanD, the ANA Tabatinga archive and the
Manaus climate file sit in `docs/proposal/2025/data/` on Google Drive.
