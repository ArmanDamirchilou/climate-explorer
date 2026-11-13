# Climate Explorer verification record for version 0.2.1

This is the historical first-cycle record. See [release verification](RELEASE_VERIFICATION.md) for version 0.3.0.

Research cycle started 11 November 2026. Final verification: 12 November 2026, about 07:58 Tehran time (UTC+3:30). Implementation version 0.2.1. This record covers technical verification and the stated experiments. It does not establish competition eligibility, scientific validity for every dataset or location, or educational impact.

## Completed checks

| Check | Observed result |
|---|---|
| Python unit suite | 25 tests passed, including the JavaScript export regression test; no tests skipped on this Mac |
| JavaScript parsing | `node --check` passed for app.js and validation.js |
| Dependency consistency | `pip check` reported no broken requirements |
| Independent numerical reference | Newey-West slope interval agreed with a separate scalar sandwich calculation at absolute tolerance 1e−11 |
| Ordinary model comparison | SciPy's original result agreed with the independent statsmodels OLS result |
| Missing calendar year | Dependence-adjusted intervals withheld; retained rows not compressed into adjacent years |
| Short record | Ten-year precipitation investigation displayed short-record and unavailable-period warnings in Chrome |
| Extreme endpoint and changing dates | Tests exposed OLS influence and a constructed direction reversal; robust slope retained the known clean slope in the endpoint fixture |
| Replay integrity | Edited source, settings, and analysis values were detected |
| Browser export | Actual Chrome JSON downloaded as `artifacts/climate-explorer-analysis-v021-browser.json`; 45 years replayed from the raw response with no network |
| Code fingerprint | Browser export fingerprint matched the current implementation |
| HTTP and exported cases | Tehran temperature, Tehran precipitation, Toronto temperature, and ten-year precipitation all replayed successfully |
| CSV and invalid inputs | Ten precipitation rows with expected units; non-finite latitude rejected with HTTP 400 |
| Synthetic method experiment | 10 scenarios × 2,000 paired replicates, eight configurations; all results and failures retained |
| Dataset consistency study | Five original presets compared with frozen GISTEMP and POWER inputs; rerunning retained the displayed slopes |
| Desktop UI | Method intervals, date table, evaluation page, scenario switching, and dataset comparison inspected in Chrome |
| Mobile UI | 400-pixel emulation inspected; comparison chart resized so its intervals remain visible |

## Bugs found during verification

The first mobile interval chart required horizontal scrolling that placed all interval bars off screen. The chart now uses the available width and splits long method labels on a phone. The period table also fits the smaller layout; detailed interval tables can scroll within their section.

The first browser export failed its raw-payload hash after JavaScript rewrote integral floats such as 1.0 as 1. Hash version 0.2.1 normalizes numerically integral floats, including negative zero, before sorted compact JSON serialization. This format is recorded in provenance. The full export is now sent through an actual Node JSON parse/stringify cycle in a regression test, and an actual Chrome download was replayed successfully. The old failing download is retained with `known-hash-bug` in its name. Download a new export rather than repairing an old hash manually.

One Chrome tab retained an inconsistent emulation/paint state after DevTools closed. A clean tab completed the same short-record workflow successfully; the temporary stalled tab was closed. The final preview is a normal desktop tab.

DevTools showed zero console messages during inspection but reported a CSP issue blocking string evaluation, without identifying its source. The application source contains no eval or Function constructor. The restrictive CSP was retained. No Lighthouse score or formal accessibility certification is claimed.

## Scientific limits and remaining validation

The known-AR1 oracle is a simulation control using information unavailable in a real investigation. None of the deployable candidates passed all internal screening cases. Newey-West and method agreement must not be marketed as a guarantee of 95% real-data coverage.

Toronto's POWER and GISTEMP temperature slopes differ substantially. Spot checks of POWER's own rounded annual entries agree with our day-weighted aggregation within 0.004 °C, but that does not explain or resolve the cross-source difference. The comparison has different spatial supports and is not a station validation. Precipitation has no second-dataset validation yet.

The prepared student usability protocol has no participant results. The full official challenge, current judging/submission guide, local virtual delivery instructions, early-work eligibility, and any guardian requirements still need resolution. The student has not yet demonstrated independent understanding of the method. No submission, registration, account creation, or payment was made in this cycle.

## Repeat the checks

From the project root:

```sh
.venv/bin/python -m unittest discover -s tests -v
node --check static/app.js
node --check static/validation.js
.venv/bin/python -m pip check
.venv/bin/python evaluation/replay.py artifacts/climate-explorer-analysis-v021-browser.json
```

The fixed experiment's protocol and inputs are in this folder. The retained source files and run manifest make the reported research inspectable. Passing these checks does not close the product and scientific questions above.
