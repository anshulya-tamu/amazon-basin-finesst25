# 04 · Data: list, status and backup plan

Status: **have** = a copy exists on Anshul's Google Drive (`docs/proposal/2025/data/`, laptop only).
Everything must be (re)downloaded on the server into `$FINESST_DATA_ROOT/raw/...` (layout in `data/README.md`).

## 1. Geometry and domain
| Dataset | Use | Status |
|---|---|---|
| SWORD v17 reaches, South America `hb62` (Amazon) | Reach network, width, slope, topology, `dist_out` | have |
| SWORD v17 nodes | Width every ~200 m, for pure-pixel reach selection | have |
| CAMREX basin, sub-basins, river network (ORNL DAAC) | Basin outline; tributary basins (no names; IDs below) | have |
| JRC Global Surface Water occurrence (Earth Engine) | Permanent-water mask, eroded away from banks | need |
| HydroLAKES v1.0 | Tefé, Coari, Janauacá, Balbina outlines | have |
| Natural Earth 1:50m countries | Maps | have (`GIS/naturalearth/`) |

CAMREX sub-basin IDs, identified with towns on each river: Negro 18 (includes Branco), Madeira 16, Purus 20,
Juruá 25, Japurá 24, Içá 27, Napo 30, Ucayali 33, Tapajós 9, Xingu 5, Trombetas 11, Javari 29, Tefé 23,
Coari 22, Jutaí 26. The Amazon main stem crosses several polygons (e.g. Manaus sits in 18), so exclude
main-stem reaches before computing any per-basin maximum.

## 2. Hydraulics
| Dataset | Use | Status |
|---|---|---|
| ANA HidroWeb, main-stem gauges: Tabatinga (10100000), Santo Antônio do Içá, Fonte Boa, Itapéua, Manacapuru (14100000, verify) | Daily stage and discharge; ADCP summaries (`ResumoDescarga`: area, width, mean velocity, mean depth); cross-sections | Tabatinga have; others need |
| ANA gauges near tributary mouths: Içá, Juruá, Japurá, Purus | Mixing weights at confluences | need |
| MGB-IPH South America (daily Q, depth, velocity) | Continuous hydraulics between gauges | Request from IPH-UFRGS. Public release is discharge only, 1990–2009 |
| SWOT L2 HR RiverSP (PO.DAAC) | Drought widths and water levels between gauges; the science orbit covers the 2023 drought | optional |

## 3. Weather forcing
| Dataset | Variables | Status |
|---|---|---|
| ERA5-Land hourly, 2013–2024 | 2 m air temperature, 2 m dewpoint, 10 m u/v wind, surface pressure, incoming shortwave, incoming longwave | Partial: daily 2023 t2m, d2m, skt, u10, v10 only (on the old HPC scratch) |
| INMET stations 82410 Benjamin Constant, 82317 Tefé, 82331 Manaus | Check ERA5 wind and radiation biases | need |

Use only meteorological state variables from ERA5-Land, never its latent or sensible fluxes.

## 4. Water temperature
| Dataset | Use | Status |
|---|---|---|
| Landsat 8/9 Collection 2 Level-2 surface temperature + quality flags, 2013–2024 (Earth Engine) | Main observed anomaly; upstream boundary; tributary temperatures | need (priority) |
| Landsat 7 Collection 2 surface temperature, 2000–2012 | Longer baseline (SLC-off striping after 2003) | optional |
| VIIRS daily LST (VNP21, day and night) | Timing and day/night at the widest reaches | optional |
| ECOSTRESS LSTE (70 m) | Different times of day, if 2023 scenes exist | optional |

## 5. In-situ validation
| Source | What | Status |
|---|---|---|
| Johannsson et al. 2026, J. Fish Biol., Table 2 | Solimões near Manaquiri, Nov 2023: surface 30.3–32.0 °C, 3 m 30.3–31.5 °C; Rio Negro values | in the paper |
| Fleischmann et al. 2025, Science, supplement | Lake loggers (Table S1 coordinates); Tefé channel profile to the Amazon, 2 Oct 2023 (Fig S1); Figs S3, S4 | Digitize figures; check the Data Availability statement; email the authors |
| ANA water-quality files (`TempAmostra`) | Sparse historical spot water temperatures | Tabatinga have (17 samples, 1990s) |
| SO-HYBAM | Possibly water temperature at Tabatinga and Manacapuru | check |

## Minimum set for the poster
1. ANA: 4 remaining main-stem gauges and 4 tributary gauges.
2. ERA5-Land hourly, 7 variables, 2013–2024, corridor box (about 70.6–59.4 °W, 5.1–1.4 °S).
3. Landsat 8/9 surface temperature, 2013–2024.
4. INMET, 3 stations.

## Backup plan if collaborators don't reply (decide by 10 Nov)
| Component | Planned | Public backup | Loss |
|---|---|---|---|
| Discharge | MGB-IPH | ANA daily Q; interpolate between gauges by distance and add tributary inflows | Floodplain exchange and backwater between gauges |
| Depth | MGB-IPH | ADCP baseline depth at normal stage + 2023 stage anomaly (≈ depth anomaly) | Detail between gauges |
| Velocity | MGB-IPH / SWOT | Velocity–discharge fit per gauge, or u = Q/(W·d) with SWORD width | Little in the main stem |
| Climatology | MGB-IPH | Day-of-year gauge statistics (1990–2022); public MGB Q 1990–2009 as cross-check | — |
| In-situ | Fleischmann | Published tables, digitized figures, ANA spot samples, satellite consistency checks | Mostly lake data |

Keep the model domain inside the gauged corridor. On the poster, call it "observation-constrained hydraulics".
If HidroWeb is down, use SO-HYBAM or GRDC for discharge.

## Findings from the Tabatinga archive (ANA 10100000)
Reproduce with `analysis/tabatinga_hydraulic_geometry.py`.
- 77 discharge measurements, Oct 1995 – Mar 2024. Exponents against discharge: depth **0.48**
  (r 0.87), velocity **0.38** (r 0.84), width **0.14** (r 0.45). Depth responds more than velocity.
- Mean depth versus stage: **1.02 m per m** (r 0.88), so a stage anomaly ≈ a depth anomaly.
- 2023 drought measurements (date: Q m³/s, width m, mean velocity m/s, mean depth m):
  - 20 Sep: 13,309, 990, 0.98, 13.8
  - 20 Oct: 14,030, 999, 1.28, 11.0
  - 24 Oct: 15,767, 996, 1.39, 11.4

  Compare 22 Oct 2019: 30,700 m³/s, 1.47 m/s, 19.5 m.
- Daily discharge 1995–2022: mean **39,700 m³/s**. Monthly medians peak in May (~56,700) and bottom out in
  Sep (~19,400).
- 2023: minimum **10,686 m³/s on 15 Oct**, 54% below the median for that date (23,138). Third-lowest annual
  minimum since 1995 (2010: 9,504; 2005: 10,144). Second-lowest October mean (2010 lower). The 2023 daily
  data are provisional (ANA consistency level 1).
- River distance Tabatinga → Negro confluence: about 1,604 km (SWORD `dist_out` 3,225 vs 1,621 km).

## Credentials
- `~/.cdsapirc` for ERA5-Land.
- `~/.netrc` for NASA Earthdata.
- `earthengine authenticate` for Earth Engine.

The old notebook's CDS key must be rotated and must never be committed.
