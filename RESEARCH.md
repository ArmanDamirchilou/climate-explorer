# Climate Explorer research and decisions

Research cycle: 11–12 November 2026. This record separates verified source facts, our experiments, and product hypotheses.

The current decision is to keep a simple linear estimate and expose its sensitivity. None of the deployable interval methods in our fixed experiment passed every screening case. A more complex method must not be described as a universal solution merely because its name includes "robust."

## Product value and existing tools

NASA Giovanni already supports time series, fitted lines, and provenance. Its guide cautions that a displayed regression line alone does not establish a scientific trend. NASA GISTEMP also provides trend maps. A general climate chart is therefore insufficient as our distinctive contribution. [Giovanni guide](https://giovanni.gsfc.nasa.gov/giovanni/doc/UsersManualworkingdocument.docx.html), [GISTEMP maps](https://data.giss.nasa.gov/gistemp/maps/).

Our hypothesis: a student benefits from seeing whether conclusions change with method assumptions or dates, then exporting enough evidence for a teacher to reproduce the calculation. This is a proposed educational benefit. No students or teachers have tested it yet, and originality across all existing products has not been established.

## Requirements and open questions

| Requirement or constraint | Evidence | Project response | State |
|---|---|---|---|
| Select an Earth science variable | Previously retrieved official challenge summary | Temperature and precipitation selector | Implemented; full brief pending |
| Show changes over time | Same summary | Annual series and monthly view | Implemented |
| Explain what changes, where, and by how much | Same summary | Units, coordinates, native grid scale, rate per decade | Implemented; full brief pending |
| Assess statistical significance | Same summary | Conditional intervals, method comparison, failure cases | Implemented as exploratory comparisons; real-data coverage not established |
| Full challenge requirements and data resources | Main official page currently renders only the title and site navigation; repeated web requests fail | Re-read when accessible. Do not replace the brief with a local site's summary. | Open |
| Current judging and submission requirements | Earlier FAQ check records guides scheduled for 13 November | Map exact criteria and required media when published | Open; no assumed weights or first-place formula |
| Before-event development | Earlier official FAQ check prohibits challenge work before the event | Preserve the true 11 November start date and original prototype | Eligibility unresolved |

Official links: [challenge](https://www.spaceappschallenge.org/2026/challenges/earth-system-trend-detective/), [participant FAQs](https://www.spaceappschallenge.org/resources/participant-faqs/). The current research did not recover the full brief. This limits claims of challenge compliance.

## Data choices

NASA POWER's monthly API gives MERRA-2 meteorology from 1981 through the previous year. Its meteorology documentation gives a native grid of 0.5° latitude by 0.625° longitude. Daily near-real-time products can append GEOS-IT; its documentation advises stopping climate-trend analysis at least two months behind real time. We use complete prior calendar years and retain the actual response's source list. [Monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/), [meteorology sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/).

| Data option | Suitability and cost | Decision |
|---|---|---|
| POWER monthly MERRA-2 | Accessible without account setup; long record for temperature and rain. Coarse model grid and possible source biases. | Keep as the first data source. It cannot represent a street or prove station-level conditions. |
| GISTEMP v4 | Observation-based temperature anomalies with a different analysis pipeline; 2° grid and spatial smoothing. No rain. | Used in the five-location consistency check over matching years. Different spatial supports are explicit. Not ground truth. |
| CHIRPS | Satellite and gauge rainfall record from 1981 at finer resolution. Version transition matters: CHIRPS v2 production ends after December 2026. | Review v3 and access before integrating. Do not silently mix versions. |
| Giovanni data holdings | Many variables and analyses, but full access requires Earthdata Login and dataset-specific review. | Useful reference tool. Avoid making new account access a dependency of the first investigation. |

GISTEMP uses GHCN v4 stations and ERSST v5 ocean data; anomalies and absolute temperatures have different baselines, but subtracting a fixed baseline does not change a linear slope. Its coarser field is not an exact match to a POWER point. [GISTEMP data](https://data.giss.nasa.gov/gistemp/). CHIRPS combines gauges and satellite estimates; complex terrain and station coverage can affect its estimates too. [CHIRPS provider](https://www.chc.ucsb.edu/data/chirps).

Do not infer daily heat extremes from monthly mean temperature. Do not rename annual rain change as drought risk without a separate definition and suitable data. Do not force Tehran's precipitation result to match a preferred story.

## Statistical alternatives

These are reasoned engineering assessments for this question and data volume. They are not an official NASA ranking. Statistical robustness to outliers differs from robustness to related errors across years.

| Approach | Useful property | Main cost or failure | Decision |
|---|---|---|---|
| OLS with ordinary t interval | Simple rate and familiar model | Correlated errors and extreme endpoints can mislead intervals and slopes | Keep point estimate; label interval assumptions |
| OLS with HC3 variance | Allows changing variance | Does not handle serial dependence | Evaluate; not a universal default |
| OLS with Newey-West variance | Allows limited serial dependence and changing variance asymptotically | Lag choice and short-record undercoverage | Show as sensitivity, not a guaranteed correction |
| Theil-Sen slope | Less sensitive to extreme values | Standard interval still does not solve dependence | Show slope comparison; do not promote its interval as dependence-safe |
| Mann-Kendall | Tests monotonic association without Gaussian value assumptions | Ordinary form still assumes independence; does not directly give rate | Defer. It would duplicate evidence without fixing the key weakness |
| Seasonal or modified Mann-Kendall | Can address seasonal/dependence structure under particular assumptions | More choices to explain and validate; we currently use annual records | Consider if moving to a monthly inference question |
| Feasible AR(1) GLS | Explicit model for neighboring errors | Estimated dependence is uncertain; stronger model assumptions | Evaluate; not selected as universal default |
| GLS with known covariance | Valid control under the exact simulation model | Real covariance is not known | Simulation control only |
| Moving-block bootstrap | Preserves some local temporal structure | Short records give few effective blocks; block-length sensitivity | Future candidate with its own calibration study |
| LOWESS or a spline | Reveals nonlinear patterns | Smoothing choices alter the result; no single comparable rate | Future diagnostic, not replacement for current question |
| Segmented regression or change-point test | Can expose abrupt change | Break selection and extra testing need validation | Future investigation if data and question justify it |
| Neural or flexible forecasting model | Can model complex patterns with sufficient data | Only 45 annual points per location; forecasting is a different task | Exclude from current scope |

NCAR explains the importance of serial dependence, the limitations of reanalysis trends, and the sensitivity of rates to starting dates. USGS describes modified trend procedures when autocorrelation is present. These sources support checking assumptions rather than treating any named method as universally best. [NCAR trend guide](https://climatedataguide.ucar.edu/climate-tools/trend-analysis), [USGS methods](https://pubs.usgs.gov/publication/sir20235064A/full).

For implementation, use established SciPy and statsmodels functions. Theil-Sen uses the median of pairwise slopes. Newey-West uses the documented Bartlett kernel and records lag and small-sample settings. GLSAR is explicitly marked experimental in the library documentation. [SciPy Theil-Sen](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.theilslopes.html), [statsmodels HAC](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html), [GLSAR](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.GLSAR.html).

## Evaluation and resulting decision

The fixed study uses 10 scenarios with 2,000 paired replicates each. Methods include three predeclared Newey-West lag settings. The protocol preceded the run. Its screening rule was not changed after looking at the result. See [protocol](evaluation/PROTOCOL.md), [results](evaluation/RESULTS.md), and `evaluation/results.json` for uncertainty bounds and all metrics.

For 45-year null records with AR(1) rho = 0.7, the original interval excluded zero in 42.0% of simulations. Newey-West with the automatic lag excluded zero in 26.2%, Theil-Sen in 39.0%, and estimated AR(1) GLS in 14.7%. Only the oracle passed all uncontaminated screening cases; it uses unavailable knowledge. These rates are properties of this experiment, not measured error rates for Tehran. They show why a silent substitution of methods would overstate confidence.

In the endpoint-contamination case, Theil-Sen's slope RMSE was about 0.136 units per decade versus 0.259 for OLS. That justifies a slope comparison. It does not justify treating Theil-Sen as a complete climate analysis.

Decision: keep OLS for the displayed rate, show dependence-adjusted intervals beside the ordinary interval, and show a Theil-Sen slope plus fixed date and one-year influence checks. Expose disagreements. No automatic choice based on which method gives a smaller p-value. Method agreement uses the same observations and cannot remove dataset bias or establish a calibrated joint confidence level.

A NOAA-hosted simulation study also reports biased rejection rates in short, autocorrelated environmental series. Our experiment is a small project-specific check, not a new general statistical result. [NOAA study](https://www.integratedecosystemassessment.noaa.gov/publications/144).

## Architecture and reproducibility

The local Python service and plain browser interface support the current load and keep calculations inspectable. A focused module separates sensitivity checks from retrieval. The implementation uses statsmodels for covariance calculations rather than copying an unverified implementation. The independent numerical test uses a separate scalar calculation.

Record the selected query, raw NASA response, payload hash, analysis version, dependency versions, and method settings in the analysis export. Provide a replay command that recomputes from that frozen response without network access. Preserve the original prototype in `artifacts/baseline-2026-11-11.zip` with its manifest. A reproducible incorrect result is still incorrect; independent reference tests and source checks remain necessary.

## Validation still needed

A five-location temperature comparison is now complete in [DATASET_CHECK.md](evaluation/DATASET_CHECK.md). All five original presets use the same 45 complete years, with no selection for agreement. Tehran rates are about 0.504 and 0.536 °C per decade for POWER and GISTEMP. Toronto rates are about 0.883 and 0.310. This is a comparison of different spatial supports, not a matched station validation. Toronto's day-weighted annual values agree with NASA's own rounded annual values in the inspected 1981, 2000, and 2025 records within 0.004 °C. That check does not explain the source difference.

Actual user feedback, matched spatial validation, the full official brief, and the student's ability to explain the method are not completed by passing code tests. The next product decision depends on whether students can correctly distinguish an estimated rate, an assumption-dependent interval, and a conclusion that changed when the dates changed. Use the prepared [usability protocol](evaluation/USER_TEST.md); its results are currently empty.
