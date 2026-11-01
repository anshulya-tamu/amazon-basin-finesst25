# Decisions and open questions

Append new entries at the top of each list, with the date.

## Decisions
- **2026-11-01** Repo created in the Google Drive project folder. `docs/` and all data stay out of git.
  GitHub is the source of truth; the server pulls from GitHub and downloads data itself.
- **2026-11-01** AGU26 poster framed as a factorial attribution: weather × hydraulics × inflow temperature,
  with hydraulics split into depth vs velocity. The outcome decides whether the headline is "reduced
  advective cooling" or "lost thermal inertia".
- **2026-11-01** The poster rests on public data only. Collaborator data (MGB-IPH 2023 runs, Fleischmann
  in-situ temperatures) are upgrades for the manuscript. Commit to the backup plan if nothing arrives by
  10 Nov.
- **2026-11-01** Model domain is the gauged corridor, Tabatinga → Manacapuru/Manaus. Hydraulics come from
  ANA gauges and ADCP fits (depth anomaly ≈ stage anomaly).
- **2026-11-01** Surface fluxes are computed over water from ERA5-Land state variables, with T_w feedback.
  ERA5-Land fluxes are not used.
- **2026-11-01** Manuscript target: GRL, submit by spring 2027.

## Open questions
- GitHub remote: name and visibility (private recommended). Not yet created.
- Server details for `CLAUDE.md`: host, paths, scheduler.
- Can MGB-IPH 2023 depth and velocity be obtained? (email IPH-UFRGS)
- Does Fleischmann et al. 2025 have a public data deposit? Check the Data Availability section.
- ANA codes for Santo Antônio do Içá, Fonte Boa and Itapéua; confirm Manacapuru 14100000.
- Legacy DSAL notebook: is the `log10` in coefficient B a bug? (see 01)
- Rotate the CDS API key that is hard-coded in `docs/proposal/2025/finesst.ipynb`.
