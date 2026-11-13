"""Fixed-period comparisons from one frozen NASA source record."""

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from climate import PRESETS, ROOT, analyze_saved


FIXED_WINDOWS = (
    {"id": "full45", "start": 1981, "end": 2025, "label": "1981–2025 · 45 years"},
    {"id": "recent35", "start": 1991, "end": 2025, "label": "1991–2025 · 35 years"},
    {"id": "recent25", "start": 2001, "end": 2025, "label": "2001–2025 · 25 years"},
    {"id": "recent15", "start": 2011, "end": 2025, "label": "2011–2025 · 15 years"},
)
WINDOW_SCOPE = (
    "Fixed comparisons of different periods in the same frozen source record. "
    "The windows overlap and are not independent evidence. A changed slope describes "
    "a different selected period; it does not by itself establish acceleration or a cause. "
    "Do not choose the window with the smallest p-value."
)
DELIVERY = "frozen NASA snapshot (public demonstration)"


def _validate_source_location(place, saved):
    source = urlsplit(saved["request_url"])
    query = parse_qs(source.query)
    if source.scheme != "https" or source.netloc != "power.larc.nasa.gov" or source.path != "/api/temporal/monthly/point":
        raise ValueError("Expected a saved NASA POWER monthly point request.")
    for field in ("latitude", "longitude"):
        values = query.get(field, [])
        if len(values) != 1:
            raise ValueError(f"Frozen source must record one {field}.")
        actual, requested = float(values[0]), float(place[field])
        if not math.isfinite(actual) or not math.isfinite(requested) or not math.isclose(actual, requested, rel_tol=0, abs_tol=1e-8):
            raise ValueError(f"Frozen source {field} differs from the selected location.")


def analyze_window(place, saved, variable, window_id):
    """Return a replayable analysis; never retrieve data or alter the source."""
    window = next((row for row in FIXED_WINDOWS if row["id"] == window_id), None)
    if window is None:
        raise ValueError("Choose one of the four fixed comparison windows.")
    _validate_source_location(place, saved)
    query = {"latitude": place["latitude"], "longitude": place["longitude"],
             "start": window["start"], "end": window["end"], "variable": variable}
    result = analyze_saved(query, saved, DELIVERY)
    result["window_context"] = {
        **window,
        "requested_years": window["end"] - window["start"] + 1,
        "scope": WINDOW_SCOPE,
    }
    return result


def analyze_windows(place, saved, variable):
    """Return all four windows in fixed longest-to-shortest order."""
    return [analyze_window(place, saved, variable, row["id"]) for row in FIXED_WINDOWS]


def write_report(directory):
    """Save every preset comparison without ranking windows by significance."""
    rows = []
    for key, place in PRESETS.items():
        saved = json.loads((ROOT/"evaluation/source-snapshots"/f"{key}-power.json").read_text())
        for variable in ("temperature", "rainfall"):
            records = analyze_windows(place, saved, variable)
            rows.append({
                "place_id": key, "name": place["name"], "variable": variable,
                "rate_unit": f"{records[0]['metadata']['unit']} per decade",
                "source": {field: records[0]["provenance"][field] for field in ("request_url", "fetched_at", "payload_sha256")},
                "analysis_settings": records[0]["analysis"]["settings"],
                "windows": [{
                    **record["window_context"], "complete_years": len(record["annual"]),
                    "excluded_years": record["excluded_years"],
                    "slope_per_decade": record["trend"]["slope_per_decade"],
                    "ordinary_ci95_per_decade": record["trend"]["ci95_per_decade"],
                    "theil_sen_slope_per_decade": record["checks"]["theil_sen_slope_per_decade"],
                    "conditional_intervals": record["checks"]["intervals"],
                } for record in records],
            })
    report = {"generated_utc": datetime.now(timezone.utc).isoformat(), "scope": WINDOW_SCOPE, "rows": rows}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    (directory/"window-analysis.json").write_text(json.dumps(report, indent=2, allow_nan=False)+"\n")
    lines = [
        "# Fixed date-window comparison", "",
        "The same frozen NASA responses are analyzed over four fixed windows ending in 2025. All five existing city presets and both variables are shown. No window is selected because it gives a smaller p-value.", "",
        "| Location | Variable | 1981–2025 | 1991–2025 | 2001–2025 | 2011–2025 |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        rates = " | ".join(f"{window['slope_per_decade']:+.3f}" for window in row["windows"])
        lines.append(f"| {row['name']} | {row['variable']} | {rates} |")
    lines += [
        "", "Temperature rates are °C per decade. Rainfall rates are mm/year per decade, describing the change in annual totals. These are fitted rates over the selected periods, not forecasts.", "",
        "## Interpretation", "", WINDOW_SCOPE, "",
        "A useful demonstration is Tehran rainfall. Its full-period rate is about +36.9 mm/year per decade, while its last-15-year rate is about −52.8. The ordinary last-15-year interval includes zero. The different directions show why the dates must accompany a claim; they do not prove a permanent reversal or its cause.", "",
        "Shorter periods contain fewer observations and can be strongly affected by temporary variability. Intervals still depend on error assumptions, and the project's synthetic study shows that nominal 95% coverage can fail. Overlapping windows share observations. Their estimates and interval exclusions must not be counted as independent confirmations. Neither significance shopping nor a comparison of which confidence intervals overlap is a valid test of acceleration.", "",
        "The 15-year window is retained as an educational sensitivity case. It should not silently replace the 45-year default or be described as a complete climate baseline. Missing years, if present, remain excluded by the common aggregation function; no annual values are filled or resampled.", "",
        "## Reproduce", "",
        "Run `.venv/bin/python window_analysis.py --report evaluation`. The report JSON retains source URL, retrieval date, payload hash, settings, complete-year counts, rates, robust slopes, and all displayed conditional intervals. Full analysis exports generated by the app retain the underlying monthly response and support `evaluation/replay.py`.", "",
        "This comparison implements the already-documented date-sensitivity question. It adds no new significance test, causal claim, station validation, or measured educational benefit.", "",
    ]
    (directory/"WINDOW_ANALYSIS.md").write_text("\n".join(lines))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT/"evaluation")
    args = parser.parse_args()
    report = write_report(args.report)
    print(f"Saved {len(report['rows'])*len(FIXED_WINDOWS)} fixed-window summaries without network access.")
