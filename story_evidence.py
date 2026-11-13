"""Generate the guided Tehran story from the frozen monthly NASA record."""

import argparse
import json
from pathlib import Path

from climate import PRESETS, ROOT
from evaluation.replay import same, verify
from window_analysis import FIXED_WINDOWS, analyze_windows


FORMAT = "Climate Explorer guided story 1"
SELECTION_NOTE = (
    "This illustrative case was selected after examining the four fixed windows. "
    "It is not a predeclared test or an unbiased sample of climate trends. "
    "All four period estimates remain available."
)
CLAIM_LIMITS = [
    "The two slopes describe different, overlapping periods, not conflicting measurements of one identical period.",
    "A negative fitted rate does not establish a decline when its conditional interval includes zero.",
    "Changing the dates does not demonstrate a permanent climate reversal, acceleration, or a cause.",
    "The gridded NASA record is not a local rain gauge, a drought measure, or a forecast.",
    "Method intervals are conditional on assumptions; agreement is not independent confirmation.",
]


def _summary(record):
    return {
        "window_id": record["window_context"]["id"],
        "start": record["period"]["start"], "end": record["period"]["end"],
        "complete_years": len(record["annual"]),
        "slope_per_decade": record["trend"]["slope_per_decade"],
        "ordinary_ci95_per_decade": record["trend"]["ci95_per_decade"],
        "ordinary_interval_includes_zero": record["trend"]["ci95_per_decade"][0] <= 0 <= record["trend"]["ci95_per_decade"][1],
        "theil_sen_slope_per_decade": record["checks"]["theil_sen_slope_per_decade"],
        "conditional_intervals": record["checks"]["intervals"],
    }


def build_story_evidence(saved=None):
    """Return deterministic JSON content without retrieving or altering data."""
    if saved is None:
        saved = json.loads((ROOT/"evaluation/source-snapshots/tehran-power.json").read_text())
    records = analyze_windows(PRESETS["tehran"], saved, "rainfall")
    for record in records:
        record["location_name"] = PRESETS["tehran"]["name"]
        verify(record)
    full, recent = records[0], records[-1]
    story = {
        "format": FORMAT, "id": "tehran-rainfall",
        "question": "Is Tehran getting wetter or drier?",
        "analyses": {"full45": full, "recent15": recent},
        "source": {field: full["provenance"][field] for field in ("request_url", "fetched_at", "payload_sha256")},
        "variable": "rainfall", "rate_unit": "mm/year per decade",
        "selection_note": SELECTION_NOTE, "claim_limits": CLAIM_LIMITS.copy(),
        "comparison": [_summary(record) for record in records],
        "plot_context": {
            "annual_values_from": "analyses.full45.annual",
            "year_domain": [1981, 2025],
            "instruction": "Keep the same annual values and axis scale when highlighting the shorter window. Mark the selected dates. Do not extend either fitted line beyond its selected period.",
        },
    }
    validate_story_evidence(story)
    return story


def validate_story_evidence(story):
    """Check story labels and summaries against replayed underlying evidence."""
    if story.get("format") != FORMAT or story.get("id") != "tehran-rainfall":
        raise ValueError("Unsupported guided story format or identifier.")
    if story.get("variable") != "rainfall" or story.get("rate_unit") != "mm/year per decade":
        raise ValueError("The guided story must retain its precipitation variable and rate unit.")
    if set(story["source"]) != {"request_url", "fetched_at", "payload_sha256"}:
        raise ValueError("The guided story must retain its source URL, date and hash.")
    if set(story["analyses"]) != {"full45", "recent15"}:
        raise ValueError("The guided story needs the two named period analyses.")
    for window_id, record in story["analyses"].items():
        verify(record)
        expected = next(window for window in FIXED_WINDOWS if window["id"] == window_id)
        same(record["period"], {"start": expected["start"], "end": expected["end"]}, "story.period")
        same(record["location"], {"latitude": PRESETS["tehran"]["latitude"], "longitude": PRESETS["tehran"]["longitude"]}, "story.location")
        if record["variable"] != "rainfall" or record["location_name"] != "Tehran, Iran":
            raise ValueError("The guided story must identify Tehran precipitation.")
        same(story["source"], {field: record["provenance"][field] for field in story["source"]}, "story.source")
    full = story["analyses"]["full45"]
    saved = {"payload": full["raw_source"], "request_url": full["provenance"]["request_url"], "fetched_at": full["provenance"]["fetched_at"]}
    expected_comparison = [_summary(record) for record in analyze_windows(PRESETS["tehran"], saved, "rainfall")]
    same(story["comparison"], expected_comparison, "story.comparison")
    if story["selection_note"] != SELECTION_NOTE or story["claim_limits"] != CLAIM_LIMITS:
        raise ValueError("The evidence selection and interpretation limits must be retained.")
    return 2


def write_story(path):
    story = build_story_evidence()
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(story, ensure_ascii=False, allow_nan=False, separators=(",", ":"))+"\n")
    return story


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT/"static/story-tehran.json")
    args = parser.parse_args()
    write_story(args.output)
    print("Saved guided Tehran evidence. Both full analyses replayed without network access.")
