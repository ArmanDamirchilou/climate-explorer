# Independent science audit

Generated 2026-11-13T06:49:30.017706+00:00. Read [the exploratory protocol](SCIENCE_AUDIT_PROTOCOL.md) before interpreting this diagnostic.

## Calendar aggregation check

All 45 years from 1981 to 2025 are retained. The comparison uses every available NASA annual record, not three selected years.

| POWER request | Day-weighted slope | Equal-month slope | NASA month-13 slope | Maximum annual difference versus NASA |
|---|---:|---:|---:|---:|
| original_toronto | 0.8827 | 0.8798 | 0.8829 | 0.0050 |
| nominal_nearby_grid | 0.8827 | 0.8798 | 0.8829 | 0.0050 |
| gistemp_cell_center | 0.4462 | 0.4444 | 0.4459 | 0.0050 |
| north_neighbor | 0.3776 | 0.3751 | 0.3781 | 0.0050 |
| west_neighbor | 0.3185 | 0.3165 | 0.3188 | 0.0049 |

Slopes are °C per decade. Annual differences are °C. The small calendar-weighting and rounded annual-value differences cannot explain the original source discrepancy of about 0.572 °C per decade.

## Fixed spatial diagnostic

| GISTEMP cell latitude | Longitude | Day-weighted slope, °C per decade |
|---|---:|---:|
| 41.0 | -81.0 | 0.2936 |
| 41.0 | -79.0 | 0.2969 |
| 41.0 | -77.0 | 0.3237 |
| 43.0 | -81.0 | 0.3130 |
| 43.0 | -79.0 | 0.3103 |
| 43.0 | -77.0 | 0.3177 |
| 45.0 | -81.0 | 0.3254 |
| 45.0 | -79.0 | 0.3408 |
| 45.0 | -77.0 | 0.3492 |

The complete 3 by 3 GISTEMP neighborhood stays far below the original POWER rate. Choosing one of these adjacent GISTEMP cells does not remove the discrepancy. These smoothed fields are not independent reference stations.

POWER itself is sensitive to nearby requested locations: the original and nominal nearby grid request both give 0.883 °C per decade, while the fixed north and west requests give about 0.378 and 0.318. At the GISTEMP cell center, POWER gives about 0.446. Thus a location change within POWER substantially changes the comparison. This narrows the investigation toward spatial and source representation; it does not demonstrate which representation is correct or why they differ.

The POWER requests are fixed point diagnostics. They do not average POWER over the GISTEMP support. Exact causal interpretation requires more information about gridding, surface representation, the time series, and reference observations. No source is selected as truth. No application result is silently replaced.

## Monthly diagnostic

All rates are °C per decade. These are descriptive comparisons, with no monthly significance tests.

| Month | Original Toronto POWER rate | Central GISTEMP rate | Difference |
|---|---:|---:|---:|
| 1 | 0.7018 | 0.4008 | +0.3010 |
| 2 | 0.4099 | 0.1381 | +0.2718 |
| 3 | 0.5593 | 0.3873 | +0.1720 |
| 4 | 0.2769 | 0.0921 | +0.1848 |
| 5 | 0.5579 | 0.2863 | +0.2716 |
| 6 | 0.9501 | 0.3099 | +0.6402 |
| 7 | 1.2386 | 0.2445 | +0.9941 |
| 8 | 1.3610 | 0.2652 | +1.0958 |
| 9 | 1.6183 | 0.5277 | +1.0906 |
| 10 | 1.3543 | 0.4687 | +0.8857 |
| 11 | 0.7567 | 0.1448 | +0.6119 |
| 12 | 0.7728 | 0.4367 | +0.3361 |

These monthly rates locate where the divergence merits investigation. They do not establish its cause. In particular, lake effects, urbanization, and model changes are hypotheses, not demonstrated explanations.

## Ranked review findings

1. Keep the Toronto discrepancy visible. Numerical agreement with NASA annual summaries supports the implemented aggregation but cannot validate the reanalysis trend.
2. Do not turn conditional intervals into an automatic significance verdict. The fixed simulation already demonstrates poor coverage under several dependence models. The current labeling and method comparisons are appropriate exploratory safeguards, not a calibrated real-world decision rule.
3. Product impact remains untested. A real student or teacher pilot and the student's own explanation are still required before educational-benefit claims.
4. Precipitation has conversion tests but no second-source evaluation. Do not describe the temperature audit as validating rain.

No main application defect was demonstrated by this audit. This does not establish that the application is defect-free.

## Reproduce and sources

Run `.venv/bin/python evaluation/science_audit.py`. Frozen extra responses are in `evaluation/science-audit-snapshots/`. Output JSON preserves annual values, monthly rates, retrieval times, URLs, and payload hashes. Frozen GISTEMP file and its provenance are documented in [DATASET_CHECK.md](DATASET_CHECK.md).

NASA POWER supplies gridded meteorology, not a precise station measurement. Its point and monthly services retain source resolution. [NASA meteorology methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), [monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/). GISTEMP station smoothing and grid construction differ from POWER. [NASA GISTEMP map notes](https://data.giss.nasa.gov/gistemp/maps/).

Additional request failures: 0. Details are retained in science-audit.json.
