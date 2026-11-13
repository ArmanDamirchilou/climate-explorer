# Synthetic method evaluation results

Seed 20261111. 2,000 replicates per scenario. See PROTOCOL.md for the fixed assumptions. These are synthetic validation results, not NASA data.

Coverage is the percentage of intervals containing the known slope. Excluding zero is a false positive in null cases and detection in trend cases. Rates have Monte Carlo uncertainty; Wilson intervals and all metrics are in results.json.

| Scenario | Method | Coverage | Excludes zero | Slope RMSE per decade | Failures |
|---|---|---:|---:|---:|---:|
| independent null | OLS iid | 94.5% | 5.5% | 0.114 | 0 |
| independent null | OLS HC3 | 94.8% | 5.2% | 0.114 | 0 |
| independent null | OLS HAC auto | 89.3% | 10.7% | 0.114 | 0 |
| independent null | OLS HAC lag 1 | 91.5% | 8.5% | 0.114 | 0 |
| independent null | OLS HAC lag 5 | 87.1% | 13.0% | 0.114 | 0 |
| independent null | Theil-Sen iid | 94.5% | 5.5% | 0.118 | 0 |
| independent null | GLSAR estimated AR1 | 93.0% | 7.0% | 0.117 | 0 |
| independent null | GLS known AR1 oracle | 94.5% | 5.5% | 0.114 | 0 |
| independent trend | OLS iid | 94.8% | 98.5% | 0.117 | 0 |
| independent trend | OLS HC3 | 94.3% | 98.2% | 0.117 | 0 |
| independent trend | OLS HAC auto | 89.3% | 98.8% | 0.117 | 0 |
| independent trend | OLS HAC lag 1 | 92.0% | 98.7% | 0.117 | 0 |
| independent trend | OLS HAC lag 5 | 87.0% | 99.0% | 0.117 | 0 |
| independent trend | Theil-Sen iid | 95.0% | 97.9% | 0.121 | 0 |
| independent trend | GLSAR estimated AR1 | 93.0% | 98.0% | 0.121 | 0 |
| independent trend | GLS known AR1 oracle | 94.8% | 98.5% | 0.117 | 0 |
| moderate dependence null | OLS iid | 82.5% | 17.5% | 0.165 | 0 |
| moderate dependence null | OLS HC3 | 82.6% | 17.4% | 0.165 | 0 |
| moderate dependence null | OLS HAC auto | 85.5% | 14.5% | 0.165 | 0 |
| moderate dependence null | OLS HAC lag 1 | 85.2% | 14.8% | 0.165 | 0 |
| moderate dependence null | OLS HAC lag 5 | 83.9% | 16.1% | 0.165 | 0 |
| moderate dependence null | Theil-Sen iid | 83.8% | 16.2% | 0.168 | 0 |
| moderate dependence null | GLSAR estimated AR1 | 91.0% | 9.0% | 0.177 | 0 |
| moderate dependence null | GLS known AR1 oracle | 95.2% | 4.8% | 0.163 | 0 |
| moderate dependence trend | OLS iid | 79.2% | 94.5% | 0.173 | 0 |
| moderate dependence trend | OLS HC3 | 81.0% | 94.2% | 0.173 | 0 |
| moderate dependence trend | OLS HAC auto | 83.2% | 90.8% | 0.173 | 0 |
| moderate dependence trend | OLS HAC lag 1 | 83.2% | 92.2% | 0.173 | 0 |
| moderate dependence trend | OLS HAC lag 5 | 81.2% | 91.1% | 0.173 | 0 |
| moderate dependence trend | Theil-Sen iid | 80.5% | 93.5% | 0.176 | 0 |
| moderate dependence trend | GLSAR estimated AR1 | 90.5% | 79.5% | 0.185 | 0 |
| moderate dependence trend | GLS known AR1 oracle | 95.0% | 82.3% | 0.170 | 0 |
| strong dependence null | OLS iid | 58.0% | 42.0% | 0.248 | 0 |
| strong dependence null | OLS HC3 | 58.5% | 41.5% | 0.248 | 0 |
| strong dependence null | OLS HAC auto | 73.8% | 26.2% | 0.248 | 0 |
| strong dependence null | OLS HAC lag 1 | 67.0% | 33.1% | 0.248 | 0 |
| strong dependence null | OLS HAC lag 5 | 74.7% | 25.3% | 0.248 | 0 |
| strong dependence null | Theil-Sen iid | 61.1% | 39.0% | 0.252 | 0 |
| strong dependence null | GLSAR estimated AR1 | 85.3% | 14.7% | 0.282 | 0 |
| strong dependence null | GLS known AR1 oracle | 95.7% | 4.3% | 0.235 | 0 |
| strong dependence trend | OLS iid | 57.9% | 87.2% | 0.246 | 0 |
| strong dependence trend | OLS HC3 | 58.4% | 86.9% | 0.246 | 0 |
| strong dependence trend | OLS HAC auto | 72.7% | 80.0% | 0.246 | 0 |
| strong dependence trend | OLS HAC lag 1 | 66.5% | 83.4% | 0.246 | 0 |
| strong dependence trend | OLS HAC lag 5 | 73.5% | 78.0% | 0.246 | 0 |
| strong dependence trend | Theil-Sen iid | 59.9% | 85.8% | 0.250 | 0 |
| strong dependence trend | GLSAR estimated AR1 | 84.5% | 57.1% | 0.276 | 0 |
| strong dependence trend | GLS known AR1 oracle | 94.8% | 54.2% | 0.234 | 0 |
| changing variance null | OLS iid | 93.6% | 6.4% | 0.159 | 0 |
| changing variance null | OLS HC3 | 94.9% | 5.1% | 0.159 | 0 |
| changing variance null | OLS HAC auto | 89.6% | 10.3% | 0.159 | 0 |
| changing variance null | OLS HAC lag 1 | 92.4% | 7.6% | 0.159 | 0 |
| changing variance null | OLS HAC lag 5 | 87.0% | 13.1% | 0.159 | 0 |
| changing variance null | Theil-Sen iid | 94.8% | 5.2% | 0.154 | 0 |
| changing variance null | GLSAR estimated AR1 | 92.1% | 7.9% | 0.167 | 0 |
| changing variance null | GLS known AR1 oracle | 93.6% | 6.4% | 0.159 | 0 |
| endpoint contamination null | OLS iid | 85.2% | 14.8% | 0.259 | 0 |
| endpoint contamination null | OLS HC3 | 99.1% | 0.9% | 0.259 | 0 |
| endpoint contamination null | OLS HAC auto | 95.9% | 4.2% | 0.259 | 0 |
| endpoint contamination null | OLS HAC lag 1 | 97.4% | 2.6% | 0.259 | 0 |
| endpoint contamination null | OLS HAC lag 5 | 94.2% | 5.8% | 0.259 | 0 |
| endpoint contamination null | Theil-Sen iid | 93.5% | 6.6% | 0.136 | 0 |
| endpoint contamination null | GLSAR estimated AR1 | 83.5% | 16.6% | 0.270 | 0 |
| endpoint contamination null | GLS known AR1 oracle | 85.2% | 14.8% | 0.259 | 0 |
| short dependent null | OLS iid | 82.5% | 17.5% | 0.546 | 0 |
| short dependent null | OLS HC3 | 84.2% | 15.8% | 0.546 | 0 |
| short dependent null | OLS HAC auto | 80.9% | 19.1% | 0.546 | 0 |
| short dependent null | OLS HAC lag 1 | 81.7% | 18.3% | 0.546 | 0 |
| short dependent null | OLS HAC lag 5 | 73.9% | 26.1% | 0.546 | 0 |
| short dependent null | Theil-Sen iid | 83.8% | 16.2% | 0.564 | 0 |
| short dependent null | GLSAR estimated AR1 | 86.0% | 14.1% | 0.671 | 0 |
| short dependent null | GLS known AR1 oracle | 95.5% | 4.5% | 0.534 | 0 |
| longer dependent null | OLS iid | 80.0% | 20.1% | 0.052 | 0 |
| longer dependent null | OLS HC3 | 80.6% | 19.4% | 0.052 | 0 |
| longer dependent null | OLS HAC auto | 87.9% | 12.1% | 0.052 | 0 |
| longer dependent null | OLS HAC lag 1 | 85.5% | 14.5% | 0.052 | 0 |
| longer dependent null | OLS HAC lag 5 | 87.8% | 12.2% | 0.052 | 0 |
| longer dependent null | Theil-Sen iid | 81.6% | 18.4% | 0.053 | 0 |
| longer dependent null | GLSAR estimated AR1 | 92.5% | 7.4% | 0.054 | 0 |
| longer dependent null | GLS known AR1 oracle | 94.8% | 5.1% | 0.052 | 0 |

## Screening decision

Methods passing every uncontaminated null scenario under the predeclared screening rule:

- GLS known AR1 oracle

The known-AR1 oracle uses information unavailable for a real location. Even if it passes the screen, it cannot be selected for the application. Agreement between methods is not independent confirmation. Synthetic calibration does not establish real-data coverage or remove source bias.

Environment: {"python": "3.14.7", "numpy": "2.5.4", "scipy": "1.18.1", "statsmodels": "0.15.0"}. Total elapsed: 24.0 seconds.
