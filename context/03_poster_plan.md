# 03 · AGU26 poster plan (current priority)

## Dates
- AGU26: **7–11 Dec 2026, Moscone Center, San Francisco**. Abstracts closed 5 Aug 2026.
- Print by about **2 Dec**, which leaves about four working weeks from 2 Nov.
- The title is fixed in the program. Results may differ from the abstract's preliminary numbers; say
  "updated since submission".

## Core design: test the abstract's three mechanisms against each other
The abstract names longer residence time (velocity), lower thermal inertia (depth) and weaker downstream
heat removal. Run a factorial experiment:
- weather {2023, climatology} × hydraulics {2023, climatology} × upstream inflow temperature
  {2023, climatology}: 8 runs;
- then split hydraulics into depth versus velocity.

Either outcome is a finding:
- If velocity dominates: "Reduced advective cooling amplified warming" (title confirmed).
- If depth dominates, as the scaling suggests: "Lost thermal inertia, not slower flow, drove hydraulic
  warming".

## Figures (each poster panel becomes a manuscript figure)
| # | Panel | Content | Priority |
|---|---|---|---|
| 1 | Setting | Corridor map (SWORD reaches, gauges Tabatinga → Manacapuru, tributaries, Tefé/Coari lakes); 2023 discharge and stage vs climatology; ERA5 anomalies in air temperature, shortwave and wind | Must |
| 2 | Observed warming | River-km × time plot of the Landsat water-temperature anomaly (2023 vs 2013–2022, Aug–Dec, clear-sky); in-situ points | Must |
| 3 | Framework | Each reach in depth vs residence time space, arrows normal → 2023, contours of τ = ρcₚd/K | Must (cheap) |
| 4 | Attribution | Waterfall chart of the factorial runs plus the depth/velocity split, with a ±30% depth uncertainty band | Must (core) |
| 5 | Fingerprint and implication | Observed anomaly vs Δdepth across reaches with similar weather; hotspot map; extra evaporation via DSAL | Should |

Figures 1, 3 and 4 alone make a complete poster.

## Model specification
A Lagrangian parcel model, about 200 lines of Python:
- Parcels travel downstream at reach velocity u.
- dT/dt = H(T_w, weather) / (ρcₚd), with the full bulk surface energy balance computed from the parcel's own
  T_w: absorbed shortwave, longwave in, εσT_w⁴ out, latent and sensible heat.
- Mix parcels at confluences, weighted by discharge.
- Upstream boundary at Tabatinga, with temperature from Landsat (2023 and climatological runs).
- Inputs: hydraulics from gauges (see 04), ERA5-Land hourly state variables.
- Splitting d from u is a sensitivity decomposition, not a physically realizable state. Say so on the poster.

## Pitfalls
1. Do not use ERA5-Land surface fluxes (land). Compute fluxes over water.
2. The flux must respond to modelled T_w, or the result is circular.
3. Pure water pixels only: erode the water mask by about 2 thermal pixels. Exposed sandbars in 2023 were hot.
4. Depth is the most uncertain and most influential input; put a ±30% band on every number.
5. State that Landsat sees skin temperature at about 10:00 local time.

## Four-week schedule
| Week | Dates | Work |
|---|---|---|
| 1 | 2–8 Nov | Corridor data (ANA gauges, ERA5-Land), scaling bound, Figs 1 and 3. Send emails (Fleischmann; MGB-IPH group). |
| 2 | 9–15 Nov | Landsat water temperature in Earth Engine, reach anomalies, Fig 2. **10 Nov: if no data from collaborators, commit to the backup plan.** |
| 3 | 16–22 Nov | Parcel model, factorial runs, Fig 4 (and Fig 5 if time) |
| 4 | 23 Nov–1 Dec | Layout, review with Huilin Gao, print (Thanksgiving 26 Nov) |

## From poster to manuscript
- Write methods as manuscript text now and cut the poster text from it. Make figures at journal quality
  first.
- Target: **GRL** (one clear finding, 4–5 figures).
- After AGU, add:
  - the 2024 drought as an independent replicate (the strongest addition);
  - in-situ validation;
  - a Monte Carlo ensemble over depth and K;
  - optionally the DSAL relative-wind pathway.
- Submit by spring 2027 so it lands within the award, which ends Oct 2027.
- At AGU, visit H057 and ask river-temperature modellers about the decomposition.

## Logistics
- Reuse the AGU25 48 × 36 in template (`docs/proposal/2025/docs/AGU-25/`). Confirm 2026 board size on the
  AGU site.
- Include the NASA logo and "NASA FINESST 80NSSC25K0481".
- Add a QR code to the code or preprint, and upload to the AGU online poster gallery.
