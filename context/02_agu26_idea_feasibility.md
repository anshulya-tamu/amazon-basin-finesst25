# 02 · AGU26 idea and feasibility

## The submitted abstract (draft with Huilin Gao's edits)
Candidate sessions: H057 Cross-Scale Drivers of River Temperature Regimes; H075 Global River Modeling;
H028 Droughts; GC039 Hydrologic Intensification. Gao's comment on the draft: "Break into 2".

> **Reduced Advective Cooling Amplified River Warming During the 2023 Amazon Drought**
> Anshul Yadav, Huilin Gao (Texas A&M)
>
> The 2023 Amazon drought produced exceptionally low river levels and widespread atmospheric warming, yet
> its effects on the thermal behavior of large flowing rivers remain poorly understood. Under normal
> conditions, advective transport redistributes locally absorbed solar energy and limits river warming.
> During drought, however, reduced discharge and depth may increase water residence time, decrease thermal
> inertia, and weaken downstream heat removal.
>
> We test whether these processes created anomalously warm river reaches during the 2023 drought across
> the Central Solimões river corridor. Surface-water temperatures from Landsat 8/9, and VIIRS are aggregated
> over dynamically mapped reaches from SWORD. These observations are integrated with SWOT-constrained
> discharge simulations from MGB-IPH, estimates of river width, depth, and velocity, and hourly surface heat
> fluxes from ERA5-Land. For each river reach, we quantify thermal exposure as the net surface heat absorbed
> over the reach relative to its downstream advective heat-transport capacity. We then apply a
> one-dimensional heat-budget model that represents surface heat exchange, upstream advection, and
> tributary mixing, and isolate the effect of drought-altered hydraulics by comparing simulations using
> observed 2023 versus seasonally climatological discharge, depth, and velocity under identical 2023
> meteorological forcing.
>
> Preliminary results indicate that drought-driven reductions in discharge (40–60%) and flow velocity
> (20–40%) increased reach-scale residence time by approximately 43% (25–67%) and amplified river
> temperature by about 0.63°C (0.3–1.0°C). Warming was strongest in wide, shallow, slowly moving reaches,
> whereas deeper main stem reaches remained comparatively buffered. Confluences showed contrasting
> responses depending on the temperature and discharge of incoming tributaries. [...]

The preliminary numbers above are placeholders from early work. The feasibility review deliberately set
them and the methods aside and judged the idea itself.

## The idea in one line
Drought hydraulics (lower discharge, depth and velocity) make a large river warm more for the same
weather, creating uneven thermal hotspots.

## Verdict
Physically sound, testable, and a good fit for FINESST Task 3. It is feasible only in a sharpened form.
As worded, the mechanism targets the wrong variable, and the main-stem signal is probably too small to see
where the data are good.

## Physics and scaling (order-of-magnitude estimates, not results)
Well-mixed column: dT/dt = H(T_w, weather) / (ρcₚd). Linearised, H = K·(T_e − T_w), where T_e is the
equilibrium temperature (the water temperature at which surface heat gain and loss balance).

- K at about 30 °C ≈ 17 W m⁻² K⁻¹ (wind 1.5 m/s) to 28 W m⁻² K⁻¹ (3 m/s). Most of it is latent heat.
- Relaxation time τ = ρcₚd / K; relaxation length L_r = u·τ.

| Setting | τ | L_r |
|---|---|---|
| Main stem, normal (d 15 m, u 1 m/s) | ~30 d | ~2,500 km |
| Main stem, drought (10 m, 0.7 m/s) | ~20 d | ~1,200 km |
| Side channel (3 m, 0.3 m/s) | ~6 d | ~150 km |

- **Advection (velocity) pathway:** exposure number N = K·L·W / (ρcₚQ) = residence time / τ. Over a 500 km
  reach, N goes from about 0.15 to 0.20. The extra warming is (T_e − T_in) × 0.04, i.e. 0.05–0.2 °C for an
  inflow 1–4 °C below equilibrium.
- **Thermal-inertia (depth) pathway:** the damped response to a T_e anomaly is
  1 / √(1 + (ωτ)²). Going from 15 m to 10 m depth adds 0.1–0.5 °C for 20–120-day anomalies of +2–3 °C.
  A 2 m side channel tracks nearly the whole anomaly (1–3 °C).
- **Consequence:** the effect is conditional on (a) inflow being below local T_e and (b) time scale. Monthly
  means converge; peaks and transient response differ.
- **River-only mechanism (links to DSAL):** easterly winds blow upstream over the eastward-flowing Amazon, so
  the current raises the wind speed felt at the water surface. Slower drought flow means less evaporative
  cooling and a higher T_e.

## Evidence
- Johannsson et al. 2026 (J. Fish Biol.): Solimões near Manaquiri/Janauacá in late Nov 2023 was
  30.3–32.0 °C at the surface and 30.3–31.5 °C at 3 m; historical values about 30 °C. The main stem was
  buffered.
- Fleischmann et al. 2025 (Science): shallow lakes passed 37 °C, one reached 41 °C, Lake Tefé about 39 °C.
  Low wind was the strongest driver in their lake-model experiments.
- van Vliet et al. 2011 (WRR): in large rivers worldwide, a 20% (40%) discharge drop adds about 0.3 °C
  (0.8 °C) of warming.
- White et al. 2023 (Hydrol. Processes) review: low flow raises thermal sensitivity; extreme-drought cases
  are understudied.
- Novelty: the mechanism is known. What is new is the setting: the largest, tropical river; a compound
  drought–heat event; satellite-era hydraulics.

## Risks
1. Depth, not advection, is the main lever, so "reduced advective cooling" may be the wrong headline.
2. Small main-stem signal (tenths of °C) against Landsat water-temperature error (~0.7–1 °C per scene).
3. **Observability tradeoff.** Large signals (side channels, paranás, lake outlets) are where the data are
   worst: thermal pixels mixed with hot exposed sandbars, channels too small for SWORD/MGB/SWOT, and skin
   warmer than bulk under low wind and slow flow.
4. Weather and hydraulics co-vary, so only a model separates them. A prescribed flux makes the result
   circular.
5. ERA5-Land fluxes are forest fluxes, not water fluxes.

## How to make it work
1. Restate the hypothesis: hydraulic drought shortens the thermal relaxation time, so the river tracks hot,
   clear, calm weather more closely. State the conditions on T_e − T_in and time scale.
2. Bound the effect per reach with the scaling above before building anything (`analysis/scaling_estimates.py`).
3. Observational fingerprint: across reaches sharing an ERA5 cell, does the observed anomaly scale with
   Δdepth or Δ(discharge per unit width)?
4. Use several droughts (2005, 2010, 2015–16, 2023, 2024) to decorrelate heat and low flow.
5. Optionally test the DSAL relative-wind pathway.
6. Domain: main stem plus channels wide enough for pure pixels (Landsat ≥ ~300 m, VIIRS ≥ ~1.1 km). Treat
   confluences separately as mixing problems.
7. Link to evaporation: +0.5 °C raises e_w by about 0.12 kPa, roughly 8% more evaporation when
   e_w − eₐ ≈ 1.5 kPa.
