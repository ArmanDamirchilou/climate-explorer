# Climate Explorer

A reproducible investigation tool for testing historical climate claims with NASA data. Version 0.3.0 brings method, date, and source checks into one workflow. The proposed audience is students and teachers. Educational benefit has not yet been measured.

[Open the public demonstration](https://armandamirchilou.github.io/climate-explorer/) · [Research and decisions](RESEARCH.md) · [Seven-slide demo](https://armandamirchilou.github.io/climate-explorer/climate-explorer-demo.pdf) · [Submission preparation](submission/README.md) · [AI assistance](AI_ASSISTANCE.md)

The public demonstration contains ten frozen NASA analyses: temperature and precipitation for five locations, 1981–2025. It makes no live NASA request. The full Python app also supports custom coordinates and dates. Both export the exact displayed evidence for offline replay.

## Competition status

Development began **11 November 2026**, before the hackathon. Codex substantially contributed the approach, implementation, research and documentation. The event's early-work rule and AI-ideation restriction create unresolved eligibility concerns. This is a completed, shareable software prototype, not an approved or submitted competition entry. Preserve the history and obtain organizer guidance before making competition declarations. See [the verified requirements and open checks](submission/REQUIREMENTS.md).

The student selected the project name. This project is separate from the established KNMI Climate Explorer and is not affiliated with NASA or KNMI. It claims no competition result or endorsement.

## Open the full app

Use Python 3.14. The exact lock was tested on macOS arm64 and is checked on Linux in GitHub Actions.

```sh
git clone https://github.com/ArmanDamirchilou/climate-explorer.git
cd climate-explorer
python3.14 -m venv .venv
.venv/bin/python -m pip install -r requirements-lock.txt
.venv/bin/python server.py
```

Open http://127.0.0.1:8766. The server listens only on this computer. If the port is busy, use `server.py --port 8767` and the matching address. On Windows use `.venv\Scripts\python.exe` in place of `.venv/bin/python`.

On macOS, `Start.command` creates the environment if needed and opens the local server. Keep its Terminal window open. If a server is already running, use its browser address.

No NASA account or API key is needed for this POWER endpoint. Other NASA services may require an account. NASA network failure falls back to a clearly labelled real Tehran snapshot or an older cached response when available.

## What works

- Temperature and precipitation, selectable locations, and a period of at least 10 complete years.
- Annual chart, fitted trend, 95% slope interval, p-value, R², and total fitted change.
- Monthly heatmap with pointer and keyboard inspection.
- Downloadable annual CSV, analysis JSON, and SVG chart.
- Source URL, retrieval timestamp, API version, source model, and live/cache status.
- Missing-month handling, leap years, unit checks, and complete-year filtering.
- A real NASA Tehran snapshot, labelled as an offline fallback if the live service fails.
- Mobile layout, keyboard controls, data table, and loading/error messages.
- Newey-West interval comparison with recorded automatic and fixed lags.
- Theil-Sen slope, one-year influence range, and fixed five-year date checks.
- A [method evaluation page](http://127.0.0.1:8766/validation.html) with 20,000 synthetic records across ten scenarios.
- A five-location temperature consistency check against GISTEMP, including the unresolved Toronto disagreement.
- Frozen raw NASA response, payload hash, code fingerprint, analysis settings, and dependency versions in the JSON export, with offline replay.

## Data and method

The backend requests NASA POWER monthly `T2M` and `PRECTOTCORR` for 1981 through the previous complete calendar year. These records currently come from MERRA-2 reanalysis. The native meteorology grid is 0.5° latitude by 0.625° longitude. A point request does not represent a precise street or a local weather station. No district-level or causal conclusions are justified.

For temperature, each monthly mean is weighted by the days in the month before forming the annual mean. For precipitation, a monthly mean rate in mm/day is multiplied by calendar days and the monthly totals are summed. Totals are approximate because the source rates are rounded. NASA month-13 records are ignored. Years with any missing, non-finite, or fill-valued month are excluded. Negative precipitation is treated as invalid.

SciPy `linregress` fits annual values against year. The first slope interval and the annual chart's mean band use the ordinary independent-error model with a Student t critical value and n−2 degrees of freedom. They assume approximately normal, constant-variance independent residuals. The band is not a prediction interval. A lag-one residual correlation above 0.3 in magnitude triggers a heuristic warning; it is not a statistical test.

The comparison uses statsmodels Newey-West covariance with Bartlett weights, n/(n−2) correction, and t(n−2) critical values. The automatic lag is floor(4(n/100)^(2/9)); fixed lags 1 and 5 expose tuning sensitivity. These are conditional sensitivity intervals, not a universal correction or independent confirmation. They are withheld if calendar years are missing rather than treating retained rows as adjacent years.

Theil-Sen gives an outlier-resistant slope, without a dependence-adjusted interval. Removing one year at a time gives a descriptive influence range. Fixed period checks omit the first five calendar years, the last five, and both ends, requiring at least ten complete years in each fit. Their ranges are not confidence intervals. Changing a window changes the period being estimated.

The [fixed synthetic study](evaluation/PROTOCOL.md) found that no deployable candidate passed every internal screening case. For example, with 45 years and strong AR(1) dependence under no true trend, the original interval excluded zero in 42.0% of simulations and automatic-lag Newey-West in 26.2%. Those are experiment-specific rates, not measured error probabilities for Tehran. See [all results](evaluation/RESULTS.md).

The [GISTEMP comparison](evaluation/DATASET_CHECK.md) uses the same complete years but different spatial supports. Tehran rates are close; Toronto rates differ substantially. It is a coarse-scale consistency check, not independent ground truth, station validation, or precipitation validation. The cause of the Toronto difference is unresolved.

Changing periods or locations repeatedly can generate misleading apparent significance. This is an exploratory educational tool, not a climate attribution study or a forecast.

## Files

- `climate.py`: NASA retrieval, caching, aggregation, validation, and statistics.
- `trend_checks.py`: method, period, and one-year sensitivity checks.
- `server.py`: local HTTP server and CSV endpoint.
- `static/`: interface with no third-party JavaScript or font requests.
- `data/tehran-nasa-snapshot.json`: unchanged NASA response plus request and retrieval metadata.
- `tests/`: conversion, missing data, independent numerical reference, known failures, and replay tests.
- `evaluation/`: fixed protocol, synthetic study, frozen dataset comparison, and usability-study protocol.
- `artifacts/`: dated verification examples. The original baseline archive is retained locally and excluded from publication because it contains a local account path; its original hash remains in the manifest. It has not been silently rewritten.

Run checks:

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check static/app.js
node --check static/validation.js
```

To replay an analysis JSON, including an investigation worksheet export:

```sh
.venv/bin/python evaluation/replay.py /path/to/climate-explorer-analysis.json
```

Replay verifies the payload hash, recorded settings, aggregation, annual and monthly values, trend, and sensitivity results without using the network. Worksheet notes are user text and are not assessed or endorsed by replay. A hash detects an input change relative to the recorded hash; it is not proof that a dataset is correct. A code fingerprint records the source files at server startup. Restart the server after changing code.

To reproduce the studies:

```sh
.venv/bin/python evaluation/calibration.py
.venv/bin/python evaluation/dataset_check.py
```

The first command regenerates the synthetic results with the fixed seed and 2,000 replicates per scenario. The second reuses the retained GISTEMP file and frozen POWER responses. The reports preserve source dates and hashes. Verification results for the current iteration are recorded in `evaluation/RELEASE_VERIFICATION.md`; the earlier iteration remains in `evaluation/VERIFICATION.md`.

## Authorship and next work

This first prototype was written with Codex assistance at the student's request. Disclose AI assistance in any competition entry. The student should review the implementation, understand the calculations, make their own contributions, and describe those contributions accurately.

The public source repository and frozen demonstration are separate from any competition team page. No competition entry has been submitted. Current requirements, full challenge fit, and unresolved personal or organizer checks are recorded in submission/REQUIREMENTS.md.

The independent science review in evaluation/SCIENCE_AUDIT.md checked all 45 Toronto annual values against NASA summaries and fixed nearby locations. It narrows the discrepancy toward spatial/source representation without proving a cause. Matched spatial support and a suitable station reference remain future scientific work. Run the actual usability pilot before claiming educational impact. Keep any event version separate from later portfolio changes.

## References and acknowledgement

- [NASA POWER Monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/)
- [NASA POWER meteorology methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/)
- [SciPy linear regression](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html)
- [SciPy Theil-Sen](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html)
- [statsmodels covariance methods](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html)
- [NCAR trend analysis guide](https://climatedataguide.ucar.edu/climate-tools/trend-analysis)
- [NOAA-hosted environmental trend simulation study](https://www.integratedecosystemassessment.noaa.gov/publications/144)
- [NASA GISTEMP](https://data.giss.nasa.gov/gistemp/) and [comparison citations](evaluation/DATASET_CHECK.md)
- [Intended Space Apps challenge](https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/)
- [Space Apps Participant FAQs](https://www.spaceappschallenge.org/resources/participant-faqs/)

NASA POWER data are provided by the NASA POWER Project. This is an independent student prototype, not a NASA product or endorsement. Each export carries provenance. No NASA logo is used.

## Build and publish the frozen demonstration

```sh
.venv/bin/python build_demo.py --output dist
```

This build uses retained NASA records, checks their hashes against the frozen study, and replays all ten analyses without contacting NASA. The generated directory can be served by any static host. GitHub Actions tests the code and builds the demonstration before publishing it to GitHub Pages. Pull requests run checks without deploying. The workflow has no NASA key or application secret.

An optional investigation worksheet saves the user's question, interpretation, uncertainty, readable evidence summary and exact displayed analysis. Notes stay in the current tab until downloaded. CSV exports also use the displayed record instead of fetching a potentially different response.

Original code and documentation use [Apache-2.0](LICENSE). NASA data and installed dependencies retain their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md). For development, use [CONTRIBUTING.md](CONTRIBUTING.md).
