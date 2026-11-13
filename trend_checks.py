"""Sensitivity checks. Agreement is not a calibrated joint confidence level."""

import numpy as np
from scipy import stats
from statsmodels.regression.linear_model import OLS


SETTINGS = {
    "version": "0.2.1", "confidence_level": .95,
    "hac_kernel": "bartlett", "hac_lag_rule": "floor(4*(n/100)^(2/9))",
    "hac_fixed_lags": [1, 5], "hac_small_sample_correction": True,
    "hac_critical_distribution": "Student t with n-2 degrees of freedom",
    "theil_sen": "Median of pairwise slopes; slope only, no dependence-adjusted interval",
    "period_checks": "Full period; omit first 5 calendar years; omit last 5; omit both ends",
    "minimum_complete_years_per_check": 10,
    "minimum_years_for_long_record_note": 30,
    "interpretation": "Conditional sensitivity checks on shared data, not independent confirmation or a joint confidence interval",
}


def direction(value):
    return "positive" if value > 1e-12 else "negative" if value < -1e-12 else "zero"


def interval_direction(interval):
    low, high = interval
    return "positive" if low > 1e-12 else "negative" if high < -1e-12 else "unclear"


def sensitivity_checks(annual, start, end):
    x = np.array([r["year"] for r in annual], dtype=float)
    y = np.array([r["value"] for r in annual], dtype=float)
    if len(x) < 10 or np.any(np.diff(x) <= 0) or not np.all(np.isfinite(y)):
        raise ValueError("Sensitivity checks need at least 10 finite values in increasing calendar years.")
    fit = OLS(y, np.column_stack([np.ones(len(x)), x-x.mean()])).fit()
    slope = float(fit.params[1]*10)
    constant = np.ptp(y) == 0
    ordinary = [0., 0.] if constant else list(map(float, fit.conf_int()[1]*10))
    intervals = [{"method": "Ordinary OLS", "lag": None, "slope_per_decade": 0. if constant else slope,
                  "ci95_per_decade": ordinary, "evidence": interval_direction(ordinary)}]
    consecutive = bool(np.all(np.diff(x) == 1))
    automatic_lag = int(np.floor(4*(len(x)/100)**(2/9)))
    if consecutive:
        for label, lag in [("Newey-West automatic lag", automatic_lag), ("Newey-West lag 1", 1), ("Newey-West lag 5", 5)]:
            adjusted = fit.get_robustcov_results(cov_type="HAC", maxlags=lag, kernel="bartlett", use_correction=True, use_t=True)
            interval = [0., 0.] if constant else list(map(float, adjusted.conf_int()[1]*10))
            intervals.append({"method": label, "lag": lag, "slope_per_decade": 0. if constant else slope,
                              "ci95_per_decade": interval, "evidence": interval_direction(interval)})
    sen = stats.theilslopes(y, x)
    robust_slope = float(sen.slope*10)
    periods = []
    for label, first, last in [("Selected period", start, end), ("Start 5 years later", start+5, end),
                                ("End 5 years earlier", start, end-5), ("Trim 5 years at both ends", start+5, end-5)]:
        selected = (x >= first) & (x <= last)
        count = int(selected.sum())
        available = last >= first and count >= 10
        row = {"label": label, "requested_start": first, "requested_end": last, "years": count, "available": available}
        if available:
            rate = float(stats.linregress(x[selected], y[selected]).slope*10)
            row.update({"first_year": int(x[selected][0]), "last_year": int(x[selected][-1]), "slope_per_decade": rate, "direction": direction(rate)})
        else:
            row["reason"] = "Fewer than 10 complete years remain."
        periods.append(row)
    leave_one_out = [float(stats.linregress(np.delete(x, i), np.delete(y, i)).slope*10) for i in range(len(x))]
    min_index, max_index = int(np.argmin(leave_one_out)), int(np.argmax(leave_one_out))
    influence = {"minimum_slope_per_decade": leave_one_out[min_index], "maximum_slope_per_decade": leave_one_out[max_index],
                 "year_removed_for_minimum": int(x[min_index]), "year_removed_for_maximum": int(x[max_index]),
                 "direction_changes": any(direction(s) != direction(slope) for s in leave_one_out)}
    interval_agreement = len(intervals) > 1 and len({r["evidence"] for r in intervals}) == 1
    available_periods = [r for r in periods if r["available"]]
    period_changes = any(r["direction"] != direction(slope) for r in available_periods)
    messages = []
    if len(x) < 30:
        messages.append("Fewer than 30 complete years: a short period can reflect temporary variability.")
    if not consecutive:
        messages.append("Missing calendar years: dependence-adjusted intervals are withheld. Retained rows are not treated as adjacent years.")
    if len(intervals) > 1 and not interval_agreement:
        messages.append("Interval conclusions differ across the displayed error assumptions or lag choices.")
    if period_changes:
        messages.append("The estimated direction changes in the fixed period checks.")
    if influence["direction_changes"]:
        messages.append("Removing a single year can change the estimated direction.")
    if direction(robust_slope) != direction(slope):
        messages.append("The ordinary and robust slope estimates have different directions.")
    if len(available_periods) < len(periods):
        messages.append("Some period checks cannot be calculated because too few complete years remain.")
    return {"intervals": intervals, "hac_available": consecutive, "automatic_lag": automatic_lag if consecutive else None,
            "interval_conclusions_agree": interval_agreement, "theil_sen_slope_per_decade": robust_slope,
            "leave_one_out": influence, "periods": periods, "period_direction_changes": period_changes,
            "messages": messages,
            "scope": SETTINGS["interpretation"],
            "calibration_caution": "Our saved synthetic study found false positives above the nominal level for ordinary and adjusted intervals in dependent records. Nominal 95% intervals are not guaranteed to achieve 95% coverage for a real location. See evaluation/results.json for the protocol-specific rates."}
