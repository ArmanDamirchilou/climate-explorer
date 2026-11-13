"""Exhaustive descriptive date sensitivity with replayable selected windows."""

import argparse
import copy
import json
import math
import time
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from climate import PRESETS, ROOT, VARIABLES, analyze, analyze_saved, validate_query
from evaluation.replay import same, verify
from trend_checks import sensitivity_checks


FORMAT = "Climate Explorer window atlas 1"
SCOPE = [
    "Every contiguous calendar window meeting the recorded minimum span is enumerated, not just windows supporting a preferred result.",
    "Changing dates changes the period being estimated. Overlapping windows are not independent replications.",
    "Slope ranges and counts describe this finite collection of windows. They are not confidence intervals, probabilities of direction, or measures of truth.",
    "Each ordinary and Newey-West interval remains conditional on its own error assumptions. None is adjusted for searching across windows.",
    "This atlas supplies no joint significance test, multiple-testing correction, causal attribution, forecast, or guarantee against selective interpretation.",
]


def _periods(start, end, minimum_years):
    for first in range(start, end-minimum_years+2):
        for last in range(first+minimum_years-1, end+1):
            yield first, last


def _basis(base):
    return {
        "source_payload_sha256": base["provenance"]["payload_sha256"],
        "analysis_code_sha256": base["analysis"]["code_sha256"],
        "location": base["location"], "variable": base["variable"],
        "period": base["period"], "unit": base["metadata"]["unit"],
    }


def _validate_base(base):
    validate_query({**base["location"], **base["period"], "variable": base["variable"]})
    same(base["metadata"], VARIABLES[base["variable"]], "atlas.base.metadata")
    request = urlsplit(base["provenance"]["request_url"])
    if request.scheme != "https" or request.netloc != "power.larc.nasa.gov" or request.path != "/api/temporal/monthly/point":
        raise ValueError("Atlas base must record a NASA POWER monthly point source.")
    query = parse_qs(request.query)
    for field in ("latitude", "longitude"):
        values = query.get(field, [])
        if len(values) != 1 or not math.isfinite(float(values[0])) or not math.isclose(float(values[0]), base["location"][field], rel_tol=0, abs_tol=1e-8):
            raise ValueError("Atlas location differs from its source request.")
    for field, expected in (("start", base["period"]["start"]), ("end", base["period"]["end"])):
        values = query.get(field, [])
        if len(values) != 1 or not values[0].isdigit():
            raise ValueError("Atlas source request must record its calendar bounds.")
        if (field == "start" and int(values[0]) > expected) or (field == "end" and int(values[0]) < expected):
            raise ValueError("Atlas base period falls outside its source request.")
    verify(base)


def _scalar_slope(annual):
    count = len(annual)
    mean_x = math.fsum(row["year"] for row in annual)/count
    mean_y = math.fsum(row["value"] for row in annual)/count
    numerator = math.fsum((row["year"]-mean_x)*(row["value"]-mean_y) for row in annual)
    denominator = math.fsum((row["year"]-mean_x)**2 for row in annual)
    return 10*numerator/denominator


def _summarize(rows):
    available = [row for row in rows if row["available"]]
    rates = [row["slope_per_decade"] for row in available]
    return {
        "candidate_windows": len(rows), "available_windows": len(available),
        "unavailable_windows": len(rows)-len(available),
        "slope_range_per_decade": [min(rates), max(rates)] if rates else None,
        "positive_slope_windows": sum(rate > 0 for rate in rates),
        "negative_slope_windows": sum(rate < 0 for rate in rates),
        "zero_slope_windows": sum(rate == 0 for rate in rates),
        "ordinary_interval_excludes_zero_windows": sum(
            row["ordinary_ci95_per_decade"][0] > 0 or row["ordinary_ci95_per_decade"][1] < 0
            for row in available
        ),
    }


def build_window_atlas(base_analysis, minimum_years=10):
    """Enumerate all eligible requested periods using one replayable record."""
    base = copy.deepcopy(base_analysis)
    _validate_base(base)
    start, end = base["period"]["start"], base["period"]["end"]
    if isinstance(minimum_years, bool) or not isinstance(minimum_years, int) or not 10 <= minimum_years <= end-start+1:
        raise ValueError("Minimum years must be an integer from ten through the base calendar span.")
    rows = []
    for first, last in _periods(start, end, minimum_years):
        annual = [row for row in base["annual"] if first <= row["year"] <= last]
        available = len(annual) >= minimum_years
        row = {"start": first, "end": last, "calendar_years": last-first+1,
               "complete_years": len(annual), "available": available}
        if available:
            trend = analyze(annual)
            row.update({"slope_per_decade": trend["slope_per_decade"],
                        "ordinary_ci95_per_decade": trend["ci95_per_decade"],
                        "trend": trend, "checks": sensitivity_checks(annual, first, last)})
        else:
            row["reason"] = f"Fewer than {minimum_years} complete years remain. No fit is reported."
        rows.append(row)
    return {
        "format": FORMAT, "base_analysis": base, "basis": _basis(base),
        "specification": {
            "minimum_calendar_years": minimum_years,
            "minimum_complete_years": minimum_years,
            "candidate_order": "Start year ascending, then end year ascending",
            "window_set": "Every contiguous requested calendar window within the base period meeting the minimum calendar span",
            "missing_years": "Incomplete years remain excluded; calendar years are never compressed. HAC intervals are withheld when retained years have gaps.",
            "point_method": "Ordinary least squares on actual calendar years; rates per decade",
            "intervals": "Existing ordinary and Newey-West conditional intervals; no selection or multiplicity adjustment",
        },
        "windows": rows, "summary": _summarize(rows), "scope": SCOPE.copy(),
    }


def materialize(atlas, start, end):
    """Restore an ordinary full analysis export for one recorded atlas cell."""
    if atlas.get("format") != FORMAT:
        raise ValueError("Unsupported window atlas format.")
    matches = [row for row in atlas["windows"] if row["start"] == start and row["end"] == end]
    if len(matches) != 1 or not matches[0]["available"]:
        raise ValueError("Select one available window recorded in the atlas.")
    row = matches[0]
    record = copy.deepcopy(atlas["base_analysis"])
    record.pop("window_context", None)
    record["period"] = {"start": start, "end": end}
    for field in ("annual", "monthly"):
        record[field] = [item for item in record[field] if start <= item["year"] <= end]
    record["excluded_years"] = [year for year in record["excluded_years"] if start <= year <= end]
    record["trend"], record["checks"] = copy.deepcopy(row["trend"]), copy.deepcopy(row["checks"])
    record["window_atlas_context"] = {
        "format": FORMAT, "minimum_calendar_years": atlas["specification"]["minimum_calendar_years"],
        "candidate_windows": atlas["summary"]["candidate_windows"], "scope": atlas["scope"].copy(),
    }
    return record


def validate_atlas(atlas, deep=False, *, full=None):
    """Check all point estimates; full/deep additionally replays every interval."""
    if full is not None:
        if not isinstance(full, bool):
            raise ValueError("Full verification must be true or false.")
        deep = full
    if atlas.get("format") != FORMAT or atlas.get("scope") != SCOPE:
        raise ValueError("Unsupported atlas format or missing interpretation limits.")
    base = atlas["base_analysis"]
    _validate_base(base)
    same(atlas["basis"], _basis(base), "atlas.basis")
    specification = atlas["specification"]
    minimum = specification["minimum_calendar_years"]
    start, end = base["period"]["start"], base["period"]["end"]
    if isinstance(minimum, bool) or not isinstance(minimum, int) or not 10 <= minimum <= end-start+1:
        raise ValueError("Invalid atlas minimum calendar span.")
    if specification["minimum_complete_years"] != minimum:
        raise ValueError("Atlas complete-year threshold must match its recorded minimum.")
    rows = atlas["windows"]
    expected = list(_periods(start, end, minimum))
    if len(rows) != len(expected) or [(row["start"], row["end"]) for row in rows] != expected:
        raise ValueError("Atlas does not contain the complete ordered window set.")
    for row in rows:
        annual = [r for r in base["annual"] if row["start"] <= r["year"] <= row["end"]]
        if row["calendar_years"] != row["end"]-row["start"]+1 or row["complete_years"] != len(annual) or not isinstance(row["available"], bool) or row["available"] != (len(annual) >= minimum):
            raise ValueError("Atlas window coverage differs from the base record.")
        if row["available"]:
            values = [row["slope_per_decade"], *row["ordinary_ci95_per_decade"]]
            if len(values) != 3 or not all(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value) for value in values) or values[1] > values[2]:
                raise ValueError("Atlas window needs finite ordered estimate and interval values.")
            same(row["slope_per_decade"], row["trend"]["slope_per_decade"], "atlas.row.slope")
            same(row["slope_per_decade"], _scalar_slope(annual), "atlas.row.recomputed_slope")
            same(row["ordinary_ci95_per_decade"], row["trend"]["ci95_per_decade"], "atlas.row.interval")
            if deep:
                verify(materialize(atlas, row["start"], row["end"]))
        elif any(field in row for field in ("slope_per_decade", "ordinary_ci95_per_decade", "trend", "checks")):
            raise ValueError("An unavailable window must not report a fitted result.")
    same(atlas["summary"], _summarize(rows), "atlas.summary")
    return sum(row["available"] for row in rows)


def build_presets(output, deep=False):
    """Generate all ten frozen cases for a static host; no network is used."""
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    reports = []
    for key, place in PRESETS.items():
        saved = json.loads((ROOT/"evaluation/source-snapshots"/f"{key}-power.json").read_text())
        for variable in ("temperature", "rainfall"):
            started = time.perf_counter()
            base = analyze_saved({**place, "start": 1981, "end": 2025, "variable": variable}, saved, "frozen NASA snapshot (public demonstration)")
            base["location_name"] = place["name"]
            atlas = build_window_atlas(base)
            validate_atlas(atlas, deep=deep)
            content = json.dumps(atlas, ensure_ascii=False, allow_nan=False, separators=(",", ":"))+"\n"
            path = output/f"{key}-{variable}.json"
            path.write_text(content)
            report = {"case": f"{key}-{variable}", "bytes": len(content.encode()), "seconds": time.perf_counter()-started, **atlas["summary"]}
            reports.append(report)
            print(json.dumps(report, allow_nan=False), flush=True)
    return reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"tmp/window-atlas")
    parser.add_argument("--deep", action="store_true", help="Replay every available compact cell after generation")
    parser.add_argument("--verify", type=Path, help="Verify a downloaded atlas offline instead of generating cases")
    args = parser.parse_args()
    if args.verify:
        try:
            if args.verify.stat().st_size > 16*1024*1024:
                raise ValueError("Atlas file exceeds the 16 MiB verification limit.")
            atlas = json.loads(args.verify.read_text())
            count = validate_atlas(atlas, full=True)
        except (OSError, ValueError, KeyError, TypeError, IndexError, OverflowError) as error:
            parser.exit(1, f"Atlas verification failed: {error}\n")
        print(f"Atlas verification passed: {count} windows, raw source, complete enumeration, estimates, intervals and sensitivity checks. No network was used.")
    else:
        build_presets(args.output, deep=args.deep)
