# Window-sensitivity atlas: protocol and interpretation

The atlas enumerates every contiguous calendar period of at least ten years within a retained source record. It extends the four fixed examples into a complete, inspectable set of date choices. Each available cell can restore a full analysis export that replays from the same frozen monthly response.

This is a descriptive sensitivity tool. It is not a new climate estimator, a complete specification-curve analysis, a multiple-testing correction, or a claim of algorithmic novelty. No measured educational impact or human evaluation is claimed.

## Why this enhancement

| Candidate | Benefit | Main limitation | Decision now |
|---|---|---|---|
| Exhaustive date-window atlas | Exposes the full date-choice space rather than four editorial examples; preserves a reproducible audit trail for any selected cell | Overlapping periods estimate different quantities; pointwise intervals remain selection-sensitive | Implement as descriptive investigation |
| Block bootstrap or another dependence estimator | Could improve uncertainty under a specified process | Needs a separate calibrated study of block lengths, finite samples and failure cases; existing experiments already reject universal corrections | Do not silently replace current intervals |
| A change-point or acceleration test | Addresses a different, explicit scientific question | Break searching and dependence require dedicated inference and validation | Defer rather than infer from changing slopes |
| A second precipitation source or local station | Could expose source bias and representation differences | Access, quality control, spatial matching and station changes need substantive work | Valuable follow-up; not claimed by this release |
| More narrative or interface polish | Can improve comprehension | Adds no scientific evidence by itself | Keep separate from the backend contribution |

Simonsohn, Simmons and Nelson's specification-curve method includes defining suitable specifications, displaying their results, and joint inference. This atlas does not implement that joint inferential stage. Its date windows also change the period being estimated. Describing it as a complete implementation of their method would overstate the work. [Primary paper](https://doi.org/10.1038/s41562-020-0912-z).

Start/end-year trend matrices also predate this project. Yosef, Aguilar and Alpert calculate such matrices to examine period-length sensitivity in climate indices (section 3 and Figure 6). Their variables and trend methods differ from this application's annual OLS calculations. The precedent limits the originality claim: this project combines an established sensitivity display with retained inputs, selected-period reconstruction and offline replay for a proposed learner workflow. It does not introduce the trend-matrix concept or demonstrate an educational advantage over earlier tools. [Author-hosted primary paper, published online in 2020](https://www.tau.ac.il/~pinhas/papers/2020/Yosef_et_al_IJC_2020.pdf), [doi:10.1002/joc.6740](https://doi.org/10.1002/joc.6740).

## Fixed enumeration rule

Let the base period be the inclusive calendar range S through E, with T = E − S + 1. Set the minimum calendar span and minimum complete-year count to m = 10 by default. Enumerate each pair (a, b) satisfying S ≤ a ≤ b ≤ E and b − a + 1 ≥ m, in ascending start-year order and then ascending end-year order.

There are (T − m + 1)(T − m + 2)/2 candidate windows. With T = 45 and m = 10 this is **666**. All five city presets and both variables produce **6,660** candidate windows. The minimum is an engineering threshold consistent with the existing application, not a claim that ten years always establishes a scientifically reliable climate trend.

A requested window remains in the atlas even when incomplete years leave fewer than m usable annual values. Such a cell is marked unavailable and has no fit. Missing years are never filled, compressed into adjacent rows, or used to shrink the enumerated calendar universe.

The four existing examples and the Tehran sign difference were already known before this work. The complete enumeration rule was implemented before the first full asset generation and was not tuned to its results. This is an exploratory protocol, not external preregistration or an unbiased sample of all climate questions.

## Calculation for each available cell

For its retained annual observations (t_i, y_i), use actual calendar years and the existing ordinary least-squares model with intercept. With centered calendar years x_i = t_i − mean(t), the annual slope is:

`b = sum(x_i * (y_i - mean(y))) / sum(x_i^2)`

The displayed rate is `10*b`. For n observations, residual sum of squares SSE, and Sxx = sum(x_i²), the ordinary slope interval is:

`10 * [b ± t(0.975, n-2) * sqrt(SSE / ((n-2)*Sxx))]`

It assumes the existing independent, approximately normal, constant-variance error model. Its nominal 95% coverage is not guaranteed for correlated climate records. The project's fixed simulation already demonstrates failures under some dependent processes. Its rates are not error probabilities for a real city.

Every cell also retains the existing Newey–West automatic-lag, lag-1 and lag-5 comparisons, Theil–Sen slope, leave-one-year influence summary, and fixed five-year trimming checks. Method settings remain explicit. HAC comparisons are withheld if retained years have internal calendar gaps. Theil–Sen has no dependence-adjusted interval in this application. No lag or method is selected by its p-value. [SciPy linear regression](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.linregress.html), [statsmodels covariance methods](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.RegressionResults.get_robustcov_results.html).

The implementation reuses the validated analysis functions rather than introducing a second numerical trend implementation. Default atlas verification independently recomputes every OLS point estimate with centered scalar sums. Full verification additionally replays every retained interval and sensitivity result. Selected ordinary intervals are checked against a separate statsmodels regression in the test suite.

## Interpretation and selection risk

The collection contains many overlapping windows. It does not contain 666 independent experiments or 666 equally plausible accounts of one identical estimand. A short recent slope and a long historical slope answer different period-specific questions.

Counts of positive slopes, negative slopes, or ordinary intervals excluding zero describe this finite collection. They are not probabilities of a true direction, probabilities of climate change, votes from independent evidence, or false-positive rates. A range across windows is not a confidence interval. The choice of minimum duration changes the collection.

No interval or p-value is adjusted for having searched the collection. There is no family-wise error control, false discovery rate procedure, joint null test, posterior probability, causal attribution, or proof of acceleration. Searching all cells and then publishing only a dramatic one remains selective reporting. The atlas makes that choice inspectable; it cannot prevent misuse.

Use the start/end grid and a fixed slope color scale to show where changes arise. Do not default to the most significant, most positive, or most negative cell. Keep the source, dates, duration, missing years and conditional interval visible. Selecting a cell should open its retained evidence rather than relabel an unrelated chart. A short-period result should not silently replace the 45-year context. NCAR discusses date sensitivity, serial dependence and the need to assess the data product itself. [NCAR trend analysis](https://climatedataguide.ucar.edu/climate-tools/trend-analysis).

## Verified initial results

The retained 1981–2025 sources have all 45 complete years in all ten cases, so every candidate is available. Every one of the **6,660** compact cells was materialized and fully replayed during the initial benchmark.

For Tehran precipitation, the 666 fitted rates range from **−164.21454545454543 mm/year per decade over 2016–2025** to **+246.67212121212123 over 1998–2007**. The former ordinary interval is [−401.063268035451, 72.63417712636016]; the latter is [108.38934333830676, 384.9548990859357]. There are 530 positive and 136 negative point estimates. These are descriptions of the chosen window universe, not inferential probabilities. The extrema are reported to document the universe, not as preferred claims.

For Tehran temperature, the rates range from **−1.3124746816922865°C per decade over 1999–2009** to **+3.062404956821757 over 1992–2001**. Neither range endpoint establishes a long-term cooling or acceleration claim. The full-period result and the source limitations remain the relevant context.

Initial generation and full replay of all ten cases took approximately **72 seconds** on the current Mac. Compact JSON totaled **32,733,135 bytes**, around 3.25–3.29 MB per case before transport compression. A separate one-case benchmark compressed to about 654 KB. These are environment-specific observations, not a performance guarantee. Host assets should load only when needed.

## Evidence contract

Envelope: `Climate Explorer window atlas 1`.

- `base_analysis`: one complete, replayable source analysis with raw monthly response, annual/monthly arrays, units, request URL, retrieval date, source hash, method settings and source-code fingerprint.
- `basis`: source payload hash, analysis fingerprint, location, variable, base period and unit. Verification checks consistency with the base rather than treating a hash as NASA authentication.
- `specification`: minimum span, minimum complete years, ordering, missing-year rule, point method and interval scope.
- `windows`: every candidate's start, end, calendar span, complete count and availability. Available cells retain the complete `trend` and `checks`, plus duplicate slope and ordinary interval fields for lightweight display. Unavailable cells retain a reason and no fit.
- `summary`: descriptive candidate/availability counts, slope range, sign counts and ordinary interval-exclusion count.
- `scope`: the explicit interpretation limits.

The raw response and long observation arrays appear once. To materialize a selected cell, copy the base, filter annual/monthly/excluded-year arrays to its requested bounds, set the new period, and restore that cell's complete `trend` and `checks`. Remove the old fixed-window label and add the atlas context. No calculation is invented in the browser. The resulting ordinary analysis export remains compatible with Python replay.

## Reproduce and verify

Generate all ten cases without contacting NASA:

```sh
.venv/bin/python window_atlas.py --output tmp/window-atlas --deep
```

Verify an arbitrary downloaded atlas offline, including every available cell:

```sh
.venv/bin/python window_atlas.py --verify /path/to/downloaded-atlas.json
```

The verification CLI limits input to 16 MiB, checks source URL/location/units/hash, bounds the base calendar range before numerical replay, checks the complete ordered universe and coverage, recomputes every point slope, and fully replays every available cell. Missing, duplicated, reordered, cross-case or altered rows are rejected when inconsistent. JSON/content hashes establish consistency with retained inputs, not authenticity, peer review or data correctness.

Python API: `build_window_atlas(base_analysis, minimum_years=10)`, `materialize(atlas, start, end)`, and `validate_atlas(atlas, full=True)`. Default validation checks all point estimates but does not recompute every interval; full validation does. The `deep=True` alias is retained for build integration. Builds contain no generation timestamp, so identical retained input and source versions give identical output.

Run the dedicated suite:

```sh
.venv/bin/python -m unittest discover -s tests -p test_window_atlas.py -v
```

No NASA requests, accounts, invented observations, generated user feedback, or modified historical source records are needed for the atlas. Frozen NASA input provenance remains in [the dataset comparison](DATASET_CHECK.md); precipitation conversion and broader source limitations remain in the project README. The atlas does not resolve Toronto's temperature source discrepancy or independently validate rainfall.
