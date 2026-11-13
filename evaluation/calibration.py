"""Fixed, paired synthetic comparison. See PROTOCOL.md before interpreting."""

import argparse
import json
import platform
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy import stats
from scipy.linalg import solve_triangular, toeplitz
import statsmodels
from statsmodels.regression.linear_model import OLS, GLSAR

OUT = Path(__file__).resolve().parent
METHODS = ["OLS iid", "OLS HC3", "OLS HAC auto", "OLS HAC lag 1", "OLS HAC lag 5", "Theil-Sen iid", "GLSAR estimated AR1", "GLS known AR1 oracle"]
SCENARIOS = [
    ("independent null", 45, 0., 0., "normal"),
    ("independent trend", 45, .05, 0., "normal"),
    ("moderate dependence null", 45, 0., .4, "normal"),
    ("moderate dependence trend", 45, .05, .4, "normal"),
    ("strong dependence null", 45, 0., .7, "normal"),
    ("strong dependence trend", 45, .05, .7, "normal"),
    ("changing variance null", 45, 0., 0., "hetero"),
    ("endpoint contamination null", 45, 0., 0., "outlier"),
    ("short dependent null", 20, 0., .4, "normal"),
    ("longer dependent null", 100, 0., .4, "normal"),
]


def wilson(successes, total):
    z = stats.norm.ppf(.975)
    p = successes / total
    denominator = 1 + z*z/total
    center = (p + z*z/(2*total))/denominator
    half = z*np.sqrt(p*(1-p)/total + z*z/(4*total*total))/denominator
    return [float(center-half), float(center+half)]


def fit_methods(y, x, oracle_x, oracle_cholesky):
    fit = OLS(y, x).fit()
    yield "OLS iid", float(fit.params[1]), fit.conf_int()[1]
    hc3 = fit.get_robustcov_results(cov_type="HC3", use_t=True)
    yield "OLS HC3", float(hc3.params[1]), hc3.conf_int()[1]
    lag = int(np.floor(4 * (len(y)/100)**(2/9)))
    for name, length in [("OLS HAC auto", lag), ("OLS HAC lag 1", 1), ("OLS HAC lag 5", 5)]:
        hac = fit.get_robustcov_results(cov_type="HAC", maxlags=length, use_correction=True, use_t=True)
        yield name, float(hac.params[1]), hac.conf_int()[1]
    sen = stats.theilslopes(y, x[:, 1])
    yield "Theil-Sen iid", float(sen.slope), [sen.low_slope, sen.high_slope]
    glsar = GLSAR(y, x, rho=1).iterative_fit(maxiter=10)
    yield "GLSAR estimated AR1", float(glsar.params[1]), glsar.conf_int()[1]
    # Whitening with the known simulation covariance is an independent control.
    whitened_y = solve_triangular(oracle_cholesky, y, lower=True)
    oracle = OLS(whitened_y, oracle_x).fit()
    yield "GLS known AR1 oracle", float(oracle.params[1]), oracle.conf_int()[1]


def run(replicates=2000):
    rng = np.random.default_rng(20261111)
    output = []
    started = time.perf_counter()
    for name, n, slope, rho, kind in SCENARIOS:
        x = np.column_stack([np.ones(n), np.arange(n)-(n-1)/2])
        cholesky = np.linalg.cholesky(toeplitz(rho**np.arange(n)))
        oracle_x = solve_triangular(cholesky, x, lower=True)
        records = {m: [] for m in METHODS}
        failures = {m: 0 for m in METHODS}
        errors = rng.normal(size=(replicates, n))
        if rho:
            for t in range(1, n):
                errors[:, t] = rho*errors[:, t-1] + np.sqrt(1-rho*rho)*errors[:, t]
        if kind == "hetero":
            errors *= np.linspace(.5, 2, n)
        if kind == "outlier":
            errors[:, -1] += 8*rng.choice([-1, 1], size=replicates)
        scenario_start = time.perf_counter()
        for error in errors:
            y = 10+slope*x[:, 1]+error
            seen = set()
            try:
                for method, estimate, interval in fit_methods(y, x, oracle_x, cholesky):
                    low, high = map(float, interval)
                    seen.add(method)
                    if not np.all(np.isfinite([estimate, low, high])) or low > high:
                        failures[method] += 1
                        continue
                    records[method].append([estimate, low, high])
            except (ValueError, np.linalg.LinAlgError, ZeroDivisionError):
                # An exception does not silently remove this replicate.
                pass
            for method in set(METHODS)-seen:
                failures[method] += 1
        summaries = {}
        for method, rows in records.items():
            values = np.array(rows)
            count = len(values)
            if not count:
                summaries[method] = {"failures": failures[method], "successful": 0}
                continue
            covered = int(np.sum((values[:, 1] <= slope) & (slope <= values[:, 2])))
            rejected = int(np.sum((values[:, 1] > 0) | (values[:, 2] < 0)))
            summaries[method] = {
                "successful": count, "failures": failures[method],
                "coverage": covered/count, "coverage_mc95": wilson(covered, count),
                "excludes_zero": rejected/count, "excludes_zero_mc95": wilson(rejected, count),
                "mean_interval_width_per_decade": float(np.mean(values[:, 2]-values[:, 1])*10),
                "bias_per_decade": float(np.mean(values[:, 0]-slope)*10),
                "rmse_per_decade": float(np.sqrt(np.mean((values[:, 0]-slope)**2))*10),
            }
        output.append({"scenario": name, "n": n, "true_slope_per_decade": slope*10, "rho": rho, "error": kind, "methods": summaries, "seconds": time.perf_counter()-scenario_start})
        print(f"Finished {name}: {replicates} paired replicates", flush=True)
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(), "seed": 20261111,
        "replicates_per_scenario": replicates, "bit_generator": "PCG64", "synthetic_only": True,
        "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "statsmodels": statsmodels.__version__},
        "elapsed_seconds": time.perf_counter()-started, "scenarios": output,
    }


def markdown(result):
    lines = ["# Synthetic method evaluation results", "", f"Seed {result['seed']}. {result['replicates_per_scenario']:,} replicates per scenario. See PROTOCOL.md for the fixed assumptions. These are synthetic validation results, not NASA data.", "", "Coverage is the percentage of intervals containing the known slope. Excluding zero is a false positive in null cases and detection in trend cases. Rates have Monte Carlo uncertainty; Wilson intervals and all metrics are in results.json.", "", "| Scenario | Method | Coverage | Excludes zero | Slope RMSE per decade | Failures |", "|---|---|---:|---:|---:|---:|"]
    for scenario in result["scenarios"]:
        for method, values in scenario["methods"].items():
            lines.append(f"| {scenario['scenario']} | {method} | {values.get('coverage', 0):.1%} | {values.get('excludes_zero', 0):.1%} | {values.get('rmse_per_decade', 0):.3f} | {values['failures']} |")
    lines += ["", "## Screening decision", "", "Methods passing every uncontaminated null scenario under the predeclared screening rule:", ""]
    passing = []
    for method in METHODS:
        eligible = [s["methods"][method] for s in result["scenarios"] if s["true_slope_per_decade"] == 0 and s["error"] != "outlier"]
        if all(v.get("coverage", 0) >= .92 and v.get("excludes_zero_mc95", [0, 1])[1] <= .08 and v["failures"] == 0 for v in eligible):
            passing.append(method)
    lines += ["- "+m for m in passing] if passing else ["None."]
    lines += ["", "The known-AR1 oracle uses information unavailable for a real location. Even if it passes the screen, it cannot be selected for the application. Agreement between methods is not independent confirmation. Synthetic calibration does not establish real-data coverage or remove source bias.", "", f"Environment: {json.dumps(result['versions'])}. Total elapsed: {result['elapsed_seconds']:.1f} seconds.", ""]
    return "\n".join(lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--replicates", type=int, default=2000)
    args = parser.parse_args()
    if args.replicates < 1:
        parser.error("replicates must be positive")
    result = run(args.replicates)
    (OUT/"results.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    (OUT/"RESULTS.md").write_text(markdown(result))
