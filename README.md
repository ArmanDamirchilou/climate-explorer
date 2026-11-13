# Climate Explorer

A reproducible investigation tool for testing historical climate claims with NASA data. Version 1.3.1 hardens evidence replay and cache recovery after a critical judging review. The 1.3 atlas and technical film remain available. The proposed audience is students and teachers. Educational benefit has not yet been measured.

[Open the public demonstration](https://armandamirchilou.github.io/climate-explorer/) · [Project overview](https://armandamirchilou.github.io/climate-explorer/review.html) · [Research and decisions](RESEARCH.md) · [Films](https://armandamirchilou.github.io/climate-explorer/demo.html) · [Seven-slide demo](https://armandamirchilou.github.io/climate-explorer/climate-explorer-demo.pdf) · [Submission preparation](submission/README.md) · [AI assistance](AI_ASSISTANCE.md)

The public demonstration contains forty frozen NASA analyses: temperature and precipitation for five locations across four fixed periods ending in 2025. It makes no live NASA request. The full Python app also supports custom coordinates and dates. Both export the exact displayed evidence for offline replay.

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

Verification includes numerical references, input failure paths, browser-module behavior, HTTP boundaries and offline replay. Actual release test counts, Linux CI and anonymous public checks are recorded in [the release evidence](evaluation/RELEASE_VERIFICATION.md).

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

Replay verifies the payload hash, variable units, recorded request and coordinates, covered dates, source metadata, analysis settings, aggregation, annual and monthly values, trend, and sensitivity results without using the network. Compatible historical fingerprints remain replayable; a recorded fingerprint is not an authenticity certificate. Worksheet notes are user text and are not assessed or endorsed by replay. A hash detects an input change relative to the recorded hash; it is not proof that a dataset is correct. A code fingerprint records the source files at server startup. Restart the server after changing code.

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

This build uses retained NASA records, checks their hashes against the frozen study, and replays all forty analyses without contacting NASA. The generated directory can be served by any static host. GitHub Actions tests the code, builds the frozen demonstration and publishes it to GitHub Pages from this dedicated project repository. The personal-site repository is untouched. See [deployment and publication](HOSTING.md). Pull requests run checks without deploying. The workflow has no NASA key or application secret.

An optional investigation worksheet saves the user's question, interpretation, uncertainty, readable evidence summary and exact displayed analysis. Notes stay in the current tab unless optional saving in this browser is enabled. Saved copies can be restored or cleared. CSV exports also use the displayed record instead of fetching a potentially different response.

Original code and documentation use [Apache-2.0](LICENSE). NASA data and installed dependencies retain their own terms; see [third-party notices](THIRD_PARTY_NOTICES.md). For development, use [CONTRIBUTING.md](CONTRIBUTING.md).

## Reopen and check an investigation

Use **Open saved evidence** to select an analysis or investigation JSON from version 0.2.1 or later, up to 2 MiB. The browser verifies the recorded raw-source hash, monthly and annual aggregation, OLS fitted values, and slope sensitivity calculations. It does not recompute uncertainty intervals, p-values, residual correlation or mean bands. The Python replay remains the full numerical check. Imported text is displayed as text and is not evaluated as markup or instructions. Nothing is uploaded.

Choose **Keep my latest investigation in this browser** to save the latest evidence and notes on this device. Saving is optional and off by default. Use **Restore saved investigation** after reload. Turning saving off or choosing **Clear local copy** removes that stored copy. This does not delete downloaded files. Anyone using this browser profile may be able to read the saved notes.

The public demo offers 1981–2025, 1991–2025, 2001–2025 and 2011–2025. All four rates appear together. Changing dates changes the question, so a different slope does not prove acceleration. See [all fixed-window results](evaluation/WINDOW_ANALYSIS.md). The source comparison remains available only for its matched 1981–2025 record.

The downloadable investigation format is **Climate Explorer investigation 1**. It retains the nested analysis for Python replay. Version-by-version additions, changes, fixes and limits are in [CHANGELOG.md](CHANGELOG.md).

## Review and handoff

Start with [Farhad's review guide](submission/FARHAD_HANDOFF.md). The [video page](https://armandamirchilou.github.io/climate-explorer/demo.html) provides the long technical film, separate short demonstration, portrait reel, captions and seven-slide PDF. The [student practice guide](submission/STUDENT_PRACTICE.md) prepares explanations without inventing student contributions. The [1.x software contract](RELEASE_CONTRACT.md) states compatibility and limits.

Each published release has a handoff ZIP containing the tracked source, frozen demo, media and SHA-256 manifest. After extracting it, follow START_HERE.md. Its static demo needs Python's built-in HTTP server but no scientific packages or NASA network access. Optional source links still use the internet. To reproduce an archive from a clean checkout, run `.venv/bin/python package_release.py`.


## Follow a guided investigation

Choose **Start the 3-step story** to investigate Tehran rainfall. The same frozen response gives a +36.901 mm/year-per-decade fitted rate over 1981–2025 and −52.832 over 2011–2025. The shorter ordinary interval includes zero. Dates change the question, not proof of a permanent climate reversal. Each step opens the matching observations and keeps your existing worksheet notes. The final step asks you to choose a supported claim. This teaching example was selected after reviewing the four windows; all four remain inspectable.

`story_evidence.py` rebuilds both complete story analyses offline. The public build regenerates the file so its evidence matches the current source fingerprint. [Science review](evaluation/STORY_SCIENCE_REVIEW.md) records exact values and limits.


## Narrated story and shareable views

Version 1.2 adds a narrated, edited short film and a 45-second portrait portfolio reel. [Watch both](https://armandamirchilou.github.io/climate-explorer/demo.html). The fictional adult presenter and voice are generated with Higgsfield and visibly disclosed. Actual NASA data figures and a real app capture connect the story to the working investigation. The longer reel exceeds the NASA demo limit and is not the submission demo. The current seven-page PDF updates the 1.0 evidence deck with release 1.3.1, atlas scope and the dedicated GitHub Pages project site; prior bytes remain in earlier tags.

Use **Copy view link** beside the source downloads to share a supported public location, variable and period. For example, [Tehran rainfall, 2011–2025](https://armandamirchilou.github.io/climate-explorer/?place=tehran&variable=rainfall&period=recent15#workspace). The link does not include notes or freeze the hosted app/data version. Download an investigation for its exact retained evidence. If clipboard access is unavailable, select and copy the displayed URL. Unsupported links announce the default; the full local app does not apply these public-view parameters.

[Production research and rebuild instructions](submission/STORY_PRODUCTION.md) and the [generation receipt](submission/higgsfield-generation.json) record the method and limits. The original silent video remains identifiable in Git history and its 1.0 release.

## Inspect every date window

Version 1.3 adds **666 windows for each of ten frozen location/variable cases**, or 6,660 retained analyses. [Open Tehran rainfall](https://armandamirchilou.github.io/climate-explorer/?place=tehran&variable=rainfall&period=full45#window-atlas), then choose **Load the atlas**. The start/end grid and chronological table contain every requested contiguous period of at least ten calendar years. A fit also requires ten complete annual observations. Missing years remain excluded; dependence checks are withheld where their calendar-spacing assumption fails.

Display-only length and direction filters keep the full universe visible in the count. They do not change calculations, select a preferred result or correct for searching. Opening a cell reconstructs its exact source-backed analysis and preserves your worksheet notes. Atlas data load only when requested, about 3.3 MB per case before transport compression. The full local server also serves these frozen cases and announces when they differ from its current live source.

Download the complete atlas from its source details. Verify its raw source, complete enumeration, every estimate, interval and sensitivity check offline:

```sh
.venv/bin/python window_atlas.py --verify /path/to/climate-explorer-window-atlas.json
```

To regenerate all ten cases: `.venv/bin/python window_atlas.py --output tmp/window-atlas --deep`. To replay only a selected analysis, use `evaluation/replay.py`; that checks the selected calculations, not completeness of the parent atlas. The browser independently checks aggregation and point calculations but retains precomputed uncertainty. [The scientific protocol](evaluation/WINDOW_ATLAS.md) defines this difference.

The atlas exposes date sensitivity. Its overlapping windows are not independent votes, and their sign counts are not direction probabilities. Intervals remain conditional and have no selection adjustment. Ten years is a product exploration boundary, not a guarantee of reliable climate evidence. This is not a forecast or causal analysis.

## The longer technical story

[Watch the 2-minute-15-second technical film](https://armandamirchilou.github.io/climate-explorer/demo.html#technical-film). Five chapters connect the opening question to source conversions, competing methods, synthetic failure cases, the atlas and offline replay. Accurate figures are composited outside the generative model; the atlas plate is explicitly a rendering from retained data, not an interface capture. The separately labeled app capture is from the working 1.1 release.

The fictional adult studio presenter and voice are AI-generated. Presenter sources are 480p within a 1080p composition. The first chapter omits an ambiguous-place-name sentence while its accurate full-period figure is shown; no unspoken replacement name is inserted in captions. [The production brief](submission/LONG_FILM_BRIEF.md), [chapter records](submission/long-film-script.json) and [audio-edit receipt](submission/long-film-word-edit.json) preserve the details. The longer film is a portfolio explanation, separate from the existing short demo candidate.

[The innovation review](INNOVATION_REVIEW.md) records 100 concrete alternatives, tradeoffs and selection criteria. It distinguishes implemented work from proposals and human validation tasks. No measured learning impact, original invention of trend matrices or award is claimed.
