# Science review of the guided story

Reviewed 13 November 2026. This is an AI-assisted scientific and communication review, not a NASA judge assessment, human peer review, or user study.

## Recommended story

Open with a question a person can understand: **“Is Tehran getting wetter or drier?”** Show the place and the actual annual record immediately. Let the viewer see why choosing the dates matters before introducing the application's controls.

Use three stages: the 45-year fitted rate, the last-15-year fitted rate, and the evidence needed to interpret their difference. Keep the same annual values and chart scale while highlighting the selected dates. Draw each fitted line only over its own period. The shorter line describes a subset of the original record, not a second measurement of the same period.

The defensible story is that dates change the estimated rate and the question. It is not that two equally supported climate conclusions conflict. The shorter negative estimate has wide intervals that include zero. Show that fact before the viewer leaves the comparison.

This example was selected after examining the fixed-window results. It is an illustrative teaching case, not a predeclared test, a representative sample, or a discovery of a permanent rainfall reversal. All four fixed windows remain available.

## Exact evidence

Location requested: 35.6892° N, 51.389° E. Variable: NASA POWER `PRECTOTCORR`, monthly mean precipitation rate in mm/day. Calendar-day multiplication and summation produce approximate annual totals in mm/year. The source rates are rounded.

| Quantity | 1981–2025 | 2011–2025 |
|---|---:|---:|
| Complete annual values | 45 | 15 |
| OLS rate, mm/year per decade | +36.901133069828724 | −52.83214285714284 |
| Ordinary 95% interval, same units | [17.318071961678008, 56.48419417797943] | [−172.27585386960618, 66.61156815532051] |
| Ordinary two-sided p-value | 0.0004504004669808015 | 0.3567220989735217 |
| Theil–Sen rate, same units | +35.518526785714286 | −29.014285714285716 |

For compact screen copy, use **+36.9** and **−52.8**, accompanied by dates and the label “change in annual rainfall, mm per decade.” The underlying rate unit is mm/year per decade. Do not present the numbers as rainfall totals or annual changes of 36.9 and −52.8 mm every year.

All four displayed interval methods include zero in the 15-year record. The automatic-lag Newey–West interval is [−159.79731643592186, 54.133030721636146]. The ordinary interval is the simplest interval to explain in the short story; the detailed method comparison remains available. The methods use shared data, and agreement is not independent confirmation or a guarantee of real-world coverage.

The 35-year and 25-year rainfall rates are +60.674 and +47.751 mm/year per decade, respectively, rounded to three decimals. See [all fixed-window results](WINDOW_ANALYSIS.md) and the complete numeric contract rather than copying rounded values into application logic.

## Source and reproducibility

- [Exact NASA request](https://power.larc.nasa.gov/api/temporal/monthly/point?parameters=T2M%2CPRECTOTCORR&community=AG&longitude=51.389&latitude=35.6892&format=JSON&start=1981&end=2025).
- Frozen response retrieved at **2026-11-11T14:22:17.905516+00:00**. Opening the source link later may return a revised response; the frozen export retains the actual input.
- Response source: `MERRA2`; NASA API `v2.10.0`.
- Payload SHA-256 in the project's documented normalized JSON format: `debc7b7a881f8443990fdb1efa9323fcae9283eb0cbb227a5025291e56bc3d2c`.
- Retained input: `evaluation/source-snapshots/tehran-power.json`.
- Generated story: `static/story-tehran.json`. Both analyses retain complete raw input, settings, provenance, and code fingerprint.

Rebuild with `.venv/bin/python story_evidence.py`. Run `.venv/bin/python -m unittest discover -s tests -p test_story_evidence.py -v`. The generator replays both complete analyses and recomputes all four comparison summaries without contacting NASA. Regenerate the story after changes to fingerprinted source files. The analysis version and app release remain the root release's responsibility.

## Limits that belong in the experience

NASA POWER represents a model grid, not a Tehran rain gauge or street. The meteorology grid is 0.5° latitude by 0.625° longitude. Preserve the source and spatial-scale explanation in the evidence view. [NASA meteorology methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), [NASA monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/).

Do not call this a drought forecast, prove a cause, infer daily extremes from monthly means, or extrapolate the fitted line. The 15-year comparison is intentionally short and can reflect temporary variability. WMO standard climate normals use specified 30-year reference periods. A fitted 15-year trend is a different object from a climate normal; the WMO definition does not make every shorter-period trend invalid. [WMO climatological normals](https://community.wmo.int/site/knowledge-hub/programmes-and-initiatives/climate-services/wmo-climatological-normals).

Ordinary and Newey–West intervals remain conditional on assumptions. The saved synthetic study demonstrates substantial coverage failures in some correlated records. Those simulation-specific rates are not measured error probabilities for Tehran. Do not turn a small p-value into certainty, or a p-value above 0.05 into proof of no change.

## Toronto as a separate follow-up story

Toronto is a useful later example of source sensitivity, using temperature rather than rain. Its original 1981–2025 POWER rate is about 0.883°C per decade, compared with about 0.310°C per decade in the selected GISTEMP field. A fixed local diagnostic found nearby POWER rates around 0.318–0.883 and neighboring GISTEMP rates around 0.294–0.349. Calendar aggregation matched NASA's annual values within 0.005°C across all 45 years. The investigation narrows the issue toward spatial/source representation but does not establish its cause or select either dataset as truth. [Diagnostic](SCIENCE_AUDIT.md), [temperature comparison](DATASET_CHECK.md).

Keep Toronto out of the initial Tehran rainfall conclusion. The temperature diagnostic does not validate precipitation, supply a local reference station, or explain Iranian drought. It supports a broader lesson: a reproducible result still needs source checks.

## Suggested short narration

“Is Tehran getting wetter or drier? Across forty-five years, this NASA record slopes up. Use the last fifteen, and the fitted slope points down. But its uncertainty still includes no trend. The dates changed the question. Climate Explorer lets you compare periods and methods, then share the exact evidence.”

Synchronize “slopes up” and “points down” with the actual fitted lines and visible dates. Show the interval caveat during its spoken sentence. A presenter may introduce the question, but do not invent personal experience, testimonials, community impact, user testing, or a student's contribution. The application's educational benefit remains unmeasured.
