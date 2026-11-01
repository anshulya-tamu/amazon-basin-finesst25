# Desk atlas builder

Builds the printable Amazon reference atlas (basin map, corridor map, hydrograph, field notes).

```bash
python tools/desk_atlas/build_data.py   # SVG maps + hydrograph data -> build/
python tools/desk_atlas/assemble.py     # fills template.html -> amazon-desk-atlas.html
```

Inputs follow the legacy Google Drive layout (`docs/proposal/2025/data/`). On another machine, set
`FINESST_ATLAS_DATA` to a folder with the same layout: SWORD, CAMREX, HydroLAKES, the ANA Tabatinga archive,
the Manaus climate CSV and `GIS/naturalearth/`. `validate_palette.py` checks the map colours for
colour-blind separation.
