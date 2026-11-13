# Trend method evaluation protocol

Protocol written on 11 November 2026, before running this experiment. Synthetic data are used only for validation. They are never shown as NASA observations.

## Question

For records as short as the available annual NASA record, how often do nominal 95% trend intervals contain the known generating slope? Does an autocorrelation adjustment reliably solve the problem?

## Fixed experiment

Use NumPy PCG64 seed 20261111 and 2,000 replicates per scenario. Every method sees the same replicate. Let calendar time be centered integer years and y = 10 + slope × time + error. Units are arbitrary. Report slopes per decade.

Gaussian AR(1) errors start in their stationary distribution with variance 1. Innovations have standard deviation sqrt(1 − rho²). This avoids an arbitrary warm-up. Cases with independent errors have rho = 0.

| Scenario | Years | Annual slope | Error process |
|---|---:|---:|---|
| independent null | 45 | 0 | Independent Gaussian |
| independent trend | 45 | 0.05 | Independent Gaussian |
| moderate dependence null | 45 | 0 | AR(1), rho = 0.4 |
| moderate dependence trend | 45 | 0.05 | AR(1), rho = 0.4 |
| strong dependence null | 45 | 0 | AR(1), rho = 0.7 |
| strong dependence trend | 45 | 0.05 | AR(1), rho = 0.7 |
| changing variance null | 45 | 0 | Independent Gaussian, standard deviation increases linearly from 0.5 to 2 |
| endpoint contamination null | 45 | 0 | Independent Gaussian plus either +8 or −8 at the final year, chosen with equal probability |
| short dependent null | 20 | 0 | AR(1), rho = 0.4 |
| longer dependent null | 100 | 0 | AR(1), rho = 0.4 |

Compare OLS with the ordinary Student t interval, OLS with HC3 variance, OLS with Newey-West/Bartlett variance, Theil-Sen with its standard interval, feasible AR(1) GLS, and an oracle GLS using the known generating rho. Newey-West uses floor(4(n/100)^(2/9)), n/(n−2) covariance correction, and t(n−2) critical values. Also evaluate fixed lags 1 and 5 to expose tuning sensitivity. GLSAR uses up to 10 iterations and its reported t interval. The oracle is a simulation control, not an available real-data method or a competitor we can deploy.

## Metrics and decision rules

Report interval coverage, interval width, slope bias, slope RMSE, interval exclusion of zero, failures, and calculation time. For null scenarios, exclusion of zero is the false-positive rate. For nonzero scenarios it is detection rate, which is useful only alongside coverage. Include Wilson 95% Monte Carlo intervals for coverage and rejection rates. Count failed fits separately and do not hide them.

A candidate is provisionally suitable as a universal default interval only if observed coverage is at least 92% and the upper Wilson bound for false positives is at most 8% in every uncontaminated null scenario, and there are no non-finite results. These are internal screening thresholds, not guarantees of 95% coverage or a published scientific standard. Do not change them after seeing results. The contamination scenario evaluates resistance to one extreme endpoint, not a complete outlier model.

If no candidate passes, retain the easy-to-explain OLS estimate and present method sensitivity with conditional intervals. Do not advertise a universal correction. Use Theil-Sen as a check on slope sensitivity, not as a cure for serial correlation. Do not select dates, methods, or lag values because they produce stronger apparent significance in Tehran.

This experiment does not cover long-memory processes, all forms of nonlinearity, missing-not-at-random data, dataset bias, changing observation networks, or multiplicity from repeated exploration. Good synthetic performance cannot validate the NASA dataset itself or prove educational benefit.

## Reproduction

Run `../.venv/bin/python calibration.py` from this directory, or `.venv/bin/python evaluation/calibration.py` from the project root. The script saves results and an environment record next to itself. The full protocol and script should be retained with the results.
