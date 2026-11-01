# 01 · The funded project

## Award
- NASA FINESST 2025, Earth Science Division. Award **80NSSC25K0481**.
- Period of performance: **1 Nov 2025 – 31 Oct 2027**.
- PI: Huilin Gao (Texas A&M). Future Investigator: Anshul Yadav.
- Letter of support: Colin Gleason (UMass Amherst; leads the SWOT discharge product). He offered guidance on
  deriving reach velocity from SWOT discharge parameters (area, slope, Manning's n).
- Products must credit NASA FINESST and the award number, and carry the NASA logo.

## Proposal in brief
Title: *Quantification of Open-Water Evaporation from River Channels in the Amazon River Basin through the
Integration of Remote Sensing and Modeling.* Full text: `reference/funded_proposal_2025.md`.

Motivation: Amazon river channels cover about 70,000 km², roughly three times the lake and reservoir area
(about 26,000 km²; SWORD v1.7 and HydroLAKES v1.0). Basin ET products seldom isolate open-water
evaporation, and those that do treat rivers like still water.

Questions and hypotheses:
- **Q1/H1** How does river evaporation compare with lake and reservoir evaporation, especially in droughts
  and heatwaves? Flow-driven advection and minimal heat storage should make river evaporation
  systematically different.
- **Q2/H2** How do meteorology and channel morphology control volumetric river evaporation, and what
  fraction of discharge is lost in extremes? Climate dominates; morphology shapes sub-basin differences;
  the lost fraction spikes in drought.
- **Q3/H3** How does in-stream advective heat flux place high-evaporation hotspots, normally and in
  extremes?

Tasks:
1. **Flowing-water evaporation with DSAL** (Double-deck Surface Air Layer; Kobayashi et al. 2013). Under
   weak wind advection:

   E = B / (1 + B·Uₐ / (A·U_w)) · Uₐ · (e_w − eₐ)

   A = 18k² / (R·T_w·[ln(δ/z_w0)]²),  B = 18k² / (R·Tₐ·[ln(zₐ/δ)]²)

   U_w = river velocity, Uₐ = wind, δ = lower-layer thickness, z_w0 = roughness of running water,
   zₐ = measurement height, k = 0.4, R = 8.314 J mol⁻¹ K⁻¹. Inputs: ERA5/ERA5-Land, MGB-IPH velocities
   (validated against GRDC/ANA, refined with SWOT after 2022). Benchmark: DLEM (Daily Lake Evaporation
   Model; Zhao et al. 2024, WRR), Penman-based with heat storage and fetch.
2. **Volumetric loss and drivers**: monthly 30 m water masks (Landsat/Sentinel-2) × E; fraction of
   discharge; Mann–Kendall and Theil–Sen trends; wavelets versus ENSO.
3. **Advective heat flux (AHF) and hotspots**: AHF(x,t) = ρ·cₚ·U_w·T_w·A*. Note: this metric depends on the
   temperature reference (absolute T), so it is not physically meaningful on its own. The AGU26 framing
   (surface heat input versus downstream transport capacity) is the better-posed version. See 02.

Uncertainty plan: Monte Carlo on DSAL inputs, P − Q − ΔS checks, DLEM cross-checks, SAR for clouds.

## History
- **2024 submission** ("Deciphering the Role of Surface Water Evaporation in the Amazon River Basin") was
  not funded. The panel rated it Very Good/Good. Critiques:
  - no treatment of satellite and model errors;
  - Landsat too cloudy and infrequent, so try ECOSTRESS or isotopes;
  - too many hypotheses;
  - unclear how the lake model handles rivers.
- **2025 resubmission** (above) was funded.
- **AGU25** poster, session H032, New Orleans, 15–19 Dec 2025: "Flow-Driven Open-Water Evaporation in the
  Amazon River Basin: Integrating DSAL, SWOT, and Harmonized Landsat–Sentinel Data".
- **Progress report draft** (Sep 2026):
  - Objective 1: DSAL proof of concept for 2023 near Balbina Reservoir compared with DLEM. River evaporation
    approaches or exceeds reservoir evaporation in dry, high-radiation months.
  - Objective 2: SWORD/HydroLAKES/HLS framework; exploring HLS, OPERA (with Sentinel-1) and CYGNSS water
    masks.
  - Objective 3 (advective heat, hotspots): scheduled for the next reporting period. The AGU26 work
    delivers it.

## Legacy code (Google Drive, `docs/`, not in git)
- `docs/proposal/2025/finesst.ipynb`: AGU25 figures, HLS tile handling, ERA5-Land daily download, DSAL
  for 2023. Ran on HPC under `/scratch/user/anshulya/global_dlem/`.
  - **Contains a hard-coded Copernicus CDS API key. Rotate it and move it to `~/.cdsapirc`.**
- Known issues in that DSAL cell:
  1. `U_w` is a constant 2.0 m/s, not MGB velocity.
  2. B uses `np.log10(z_a/delta)`, but the proposal equation uses natural log. Likely a bug.
  3. A and B both use air temperature `t2m`; the proposal uses T_w for A.
  4. `e_w` comes from ERA5-Land skin temperature `skt`, which is the land or forest skin in that grid
     cell, not water.
  5. The unit factor `*6*24*100` is undocumented.

  Parameters used: δ = 0.1 m, z_w0 = 1e-5 m, zₐ = 10 m.
- `docs/proposal/2025/lake_evap.ipynb`: maps and the Manaus climatology (Colab).
- `docs/proposal/2024/Code/river_evaporation.ipynb`: early exploration, GLEV lake data, HLS download routine.
- AGU25 poster: `docs/proposal/2025/docs/AGU-25/FINESST-Amazon-poster_draft2.pptx`, 48 × 36 in.
- AGU26 abstract drafts: `docs/conferences/AGU-26/`. Printable reference atlas:
  `docs/conferences/AGU-26/amazon_desk_atlas.pdf`.
