# Temperature dataset consistency check

Exploratory coarse-scale consistency check. Different fields and spatial supports; not independent ground truth or validation of a street-level trend.

Five locations were the existing application presets, chosen before this comparison. All available common complete years in 1981–2025 are used. Annual values are day-weighted in both datasets; no window was chosen to improve agreement.

| Location | GISTEMP cell center latitude longitude | Common years | POWER °C per decade | GISTEMP °C per decade | Difference |
|---|---|---|---:|---:|---:|
| Tehran, Iran | [35.0, 51.0] | 1981–2025 (45) | 0.504 | 0.536 | -0.033 |
| Ankara, Turkey | [39.0, 33.0] | 1981–2025 (45) | 0.495 | 0.501 | -0.006 |
| Berlin, Germany | [53.0, 13.0] | 1981–2025 (45) | 0.560 | 0.465 | +0.095 |
| Toronto, Canada | [43.0, -79.0] | 1981–2025 (45) | 0.883 | 0.310 | +0.572 |
| Milan, Italy | [45.0, 9.0] | 1981–2025 (45) | 0.487 | 0.477 | +0.010 |

## Interpretation

A difference is not automatically a software error. POWER is gridded reanalysis of near-surface air temperature. This GISTEMP file is an observation-based temperature-anomaly analysis with a different grid and smoothing. A fixed reference temperature does not change a slope, but spatial sampling, smoothing, and processing can. Shared observations also mean the datasets are not necessarily statistically independent. Neither is a local reference station.

This check evaluates temperature only. It does not validate precipitation or establish uncertainty coverage. Larger regional claims require matching spatial supports and a dedicated dataset evaluation.

## Reproduction and sources

Run `.venv/bin/python evaluation/dataset_check.py`. The frozen compressed GISTEMP input is beside the script. POWER responses are retained in `evaluation/source-snapshots/`. The output JSON contains annual values, actual coordinates, source dates, and hashes.

GISTEMP file history: Created 2026-10-22 14:38:13 by SBBX_to_nc 2.0 - ILAND=250,  IOCEAN=none,     Base: 1951-1980.
Compressed file SHA256: 06ca5386c537d48f5d4c93ebe9571f9058be0cb58aff056b972123bcb09cd6bf.

GISTEMP Team, 2026: GISS Surface Temperature Analysis, version 4. NASA GISS. Accessed 11 November 2026. [Data and methods](https://data.giss.nasa.gov/gistemp/), [download description](https://data.giss.nasa.gov/gistemp/data_v4.html). Lenssen et al. (2024), A GISTEMPv4 observational uncertainty ensemble, JGR Atmospheres 129, e2023JD040179, [doi:10.1029/2023JD040179](https://doi.org/10.1029/2023JD040179).

POWER data provided by the NASA POWER Project. [Monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/) and [meteorology sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/).
