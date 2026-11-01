# FINESST: Amazon river evaporation and drought river warming

Anshul Yadav (PhD student, Zachry Dept. of Civil & Environmental Engineering, Texas A&M; NASA FINESST
Future Investigator) works with PI Huilin Gao. NASA FINESST award 80NSSC25K0481, 1 Nov 2025 – 31 Oct 2027.
Anshul is new to Amazon geography: name places and explain where they are.

## Read before doing project work
| File | What it holds |
|---|---|
| `context/01_project.md` | The funded proposal, tasks, progress so far, legacy code and its known issues |
| `context/02_agu26_idea_feasibility.md` | The AGU26 abstract, the physics, feasibility verdict, risks |
| `context/03_poster_plan.md` | AGU26 poster plan: factorial design, figures, model spec, schedule |
| `context/04_data.md` | Data list with status, the no-collaborator backup plan, Tabatinga gauge findings |
| `context/05_amazon_primer.md` | Geography, river names, gauges, stations, coordinates, terms |
| `context/decisions.md` | Dated decisions and open questions. Append to it when something is decided |
| `context/reference/funded_proposal_2025.md` | Full text of the funded proposal (equations missing; see 01) |

## Current priority (as of 2026-11-01)
AGU26 poster, San Francisco, 7–11 Dec 2026; print by about 2 Dec. Abstract title: "Reduced Advective
Cooling Amplified River Warming During the 2023 Amazon Drought". The plan is a factorial attribution
(weather × hydraulics × upstream inflow temperature, with hydraulics split into depth vs velocity) using a
small Lagrangian heat-budget model on the Tabatinga → Manaus corridor, checked against Landsat water
temperature. The poster must not depend on collaborators' data (see the backup plan in 04).

## Physics to keep straight
- Over a few hundred km of the main stem, slower flow (advection) matters little. The main-stem relaxation
  time is about 3–4 weeks and the relaxation length about 1,000–2,500 km. Shallower water (lost thermal
  inertia) is the larger lever.
- The surface heat flux must respond to modelled water temperature. A prescribed flux makes lower
  discharge cause warming by construction.
- ERA5-Land latent and sensible fluxes are land (forest) fluxes. Use its meteorological state variables and
  compute fluxes over water.
- 2023 was not a record low at Tabatinga (2010 and 2005 were lower). The record lows were at Manaus.
  Check claims against data before writing them.

## Repo conventions
- Data never goes in git. Scripts read `FINESST_DATA_ROOT` (default `./data`); layout in `data/README.md`.
- Credentials live only in `~/.cdsapirc`, `~/.netrc` (NASA Earthdata) and the Earth Engine auth store.
  Never hard-code keys.
- `docs/` is the Google Drive document archive and is gitignored. It exists on Anshul's laptop, not on the
  server. Context from it is distilled into `context/`.
- Code: `analysis/` for scripts, `src/finesst/` for reusable modules, `tools/desk_atlas/` for the
  reference-map builder. Environment: `environment.yml` (conda-forge).
- Commit messages: short imperative subject line.

## Server (fill in when set up)
- Host: TODO
- Repo path: TODO
- `FINESST_DATA_ROOT`: TODO (earlier work used `/scratch/user/anshulya/global_dlem/data/finesst/`)
- Scheduler / job notes: TODO
