# Understanding and presenting Climate Explorer

This is a learning guide for the student, not a finished competition script. The code was produced with Codex assistance. Describe your own contribution accurately after you have reviewed, tested, and changed it yourself.

## The idea

Climate Explorer asks how a historical temperature or rainfall estimate changes over time. It then checks whether the answer depends on a few reasonable analysis choices. A useful result can be disagreement: it tells us where to investigate next.

The first audience is students and teachers. We have not yet measured whether it helps them. The project does not forecast weather, identify the cause of warming, or advise a city about drought.

## Follow one value through the code

NASA POWER returns a monthly mean temperature in degrees Celsius. To calculate the annual mean, multiply each monthly mean by the number of days in that month. Add those products and divide by the number of days in the year. February has 29 days in a leap year. If a month is missing, we exclude that whole year.

For rain, the input is a mean daily rate in millimeters per day. Multiply by the days in the month to estimate the monthly total, then add the twelve totals. A value of 1 mm/day throughout 1984 gives 366 mm for that year. Monthly rounding makes these totals approximate.

`climate.py` retrieves and aggregates these values. Its `analyze` function fits the straight line. `trend_checks.py` runs the comparisons. `static/app.js` draws the results. `evaluation/replay.py` recalculates a saved result without asking NASA for new data.

## Why keep a straight line?

The question asks for an interpretable rate of historical change. A straight line gives one rate in units per decade. We can explain and test it with only a few decades of annual values. A more flexible model could fit more detail, but that would not automatically answer this question better.

The line is a summary. A curved record or a sudden change may not be represented well. A rate over 1981–2025 can differ from a rate over 1986–2020 because the periods ask different questions.

## Why compare methods?

The original interval assumes yearly errors are independent. Climate errors can persist from one year to the next. Newey-West changes the estimated uncertainty while leaving the fitted OLS slope unchanged. It includes a chosen number of neighboring years in the calculation. It can still perform badly in short records.

Theil-Sen uses the median of pairwise slopes. It is less affected by an extreme value. We show it as a slope check, not as proof that time dependence has been fixed. Removing each year once asks whether one observation strongly affects the rate. None of these checks removes errors in the source data.

## What the experiment taught us

We tested eight displayed method configurations on the same 20,000 generated records across ten scenarios. These are synthetic records with known answers, not extra NASA observations. Some methods share the same slope and differ only in uncertainty calculation.

In the strongly dependent 45-year null case, ordinary OLS excluded zero in 42.0% of records. Newey-West with the automatic lag did so in 26.2%. That is why the app does not claim a universal statistical correction. The full results include good cases, failures, and Monte Carlo uncertainty.

We also checked temperature against GISTEMP over the same years in the five original locations. Tehran's estimates were close, but Toronto's differed substantially. These sources have different grids and processing. The difference is unresolved and must not be hidden or assigned a cause without evidence.

## Explain the limits clearly

A 95% interval is a procedure with a coverage target under specified conditions. It is not a 95% probability that this particular claim is true. An interval excluding zero does not prove a cause. Agreement between methods is not independent evidence. A model grid cell is not a street thermometer.

The full challenge and current guides have been reviewed. The project still needs real user feedback, further spatial validation, and your own explanation of the calculations. Early development started on 11 November, and competition eligibility is unresolved. Do not claim a NASA endorsement, an award, or work dates that did not happen.

## Demonstration sequence

Open Tehran temperature over 1981–2025. Explain the rate and units. Show the assumptions beside the first interval. Compare the methods, then show the fixed date checks. Open the evaluation page and explain one false-positive case. Show the Toronto dataset difference as an unresolved finding. Finish by replaying a saved JSON and stating which parts you personally understand and contributed.

The verified guide permits at most seven slides or a video of at most 30 seconds. A seven-page PDF is prepared in submission/climate-explorer-demo.pdf. A clear explanation with one honest limitation is more useful than a long feature list.

## Why the window atlas matters

Four example periods are useful, but they still leave many date choices hidden. Version 1.3 keeps every requested contiguous window with a minimum of ten years. A 45-year complete record has 36 possible ten-year windows, 35 eleven-year windows, and so on to one 45-year window. Adding these gives 666. Ten retained location/variable cases give 6,660 fits.

The raw monthly response appears once in an atlas file. Each cell retains its own dates, complete-year count, fitted result and method checks. Opening a cell combines those results with the matching observations from the shared source. It does not fetch a different NASA response. This is a small evidence format, not a database of unrelated screenshots.

Compare two nearby cells. Explain what changed in the dates and observations. Then explain why two overlapping periods are not independent evidence. A fraction of positive cells is not the probability that a trend is real. Looking through all cells does not correct an interval for selective reporting.

Download the complete atlas and run `window_atlas.py --verify` to check all cells offline. `evaluation/replay.py` checks one selected analysis. The browser checks a narrower set of point calculations. Those are three different scopes; say which check actually ran.

The longer technical film is a separate portfolio explanation. It does not replace the short official demo candidate. Read the production notes before describing its generated presenter or claiming personal work.
