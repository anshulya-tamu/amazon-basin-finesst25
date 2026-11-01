# FINESST: Amazon river evaporation and drought river warming

Code and working notes for the NASA FINESST project *Quantification of Open-Water Evaporation from River
Channels in the Amazon River Basin through the Integration of Remote Sensing and Modeling*
(award 80NSSC25K0481; FI Anshul Yadav, PI Huilin Gao, Texas A&M University).

The current focus is the AGU26 poster on how the 2023 drought's low, shallow, slow flow changed the
temperature of the Solimões (Central Amazon). Start with `CLAUDE.md` and the files in `context/`.

## Layout
```
CLAUDE.md            project brief, loaded automatically by Claude Code
context/             distilled project knowledge: proposal, idea, plan, data, geography, decisions
analysis/            standalone analysis scripts
src/finesst/         reusable Python modules
tools/desk_atlas/    builds the printable Amazon reference atlas
data/                not in git; see data/README.md
docs/                not in git; Google Drive document archive (laptop only)
```

## Setup
```bash
conda env create -f environment.yml
conda activate finesst
export FINESST_DATA_ROOT=/path/to/large/storage/finesst-data   # add to ~/.bashrc on the server
```

Credentials (never commit these):
- Copernicus CDS (ERA5-Land): `~/.cdsapirc`
- NASA Earthdata (SWOT, VIIRS, ECOSTRESS): `~/.netrc` entry for `urs.earthdata.nasa.gov`
- Google Earth Engine (Landsat): `earthengine authenticate`

## Workflow: laptop → GitHub → server
1. Edit on the laptop and commit.
2. Push to GitHub: `git push`.
3. On the server: `git clone <repo URL>` once, then `git pull` to update.
4. Download and process data on the server into `$FINESST_DATA_ROOT`.

This folder sits inside Google Drive. Drive sync can occasionally conflict with files inside `.git/`. If git
reports a corrupt index or odd lock files, re-clone from GitHub; GitHub is the source of truth.
