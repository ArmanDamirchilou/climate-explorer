"""Recompute a frozen analysis JSON without using the network."""

import argparse
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from climate import analyze, annual_series, payload_hash
from trend_checks import SETTINGS, sensitivity_checks


def same(expected, actual, path="result"):
    if isinstance(expected, dict) and isinstance(actual, dict):
        if set(expected) != set(actual):
            raise ValueError(f"Different fields at {path}")
        for key in expected:
            same(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list) and isinstance(actual, list):
        if len(expected) != len(actual):
            raise ValueError(f"Different lengths at {path}")
        for i, (left, right) in enumerate(zip(expected, actual)):
            same(left, right, f"{path}[{i}]")
    elif isinstance(expected, (int, float)) and not isinstance(expected, bool) and isinstance(actual, (int, float)):
        if not math.isclose(expected, actual, rel_tol=1e-9, abs_tol=1e-9):
            raise ValueError(f"Different numeric result at {path}")
    elif expected != actual:
        raise ValueError(f"Different value at {path}")


def verify(record):
    if record.get("format") == "Climate Explorer investigation 1":
        record = record["analysis"]
    if "raw_source" not in record:
        raise ValueError("This export predates replay support. Download a new analysis JSON.")
    if record["analysis"]["settings"]["version"] != SETTINGS["version"]:
        raise ValueError("Analysis versions differ. Use the recorded code version for this export.")
    same(record["analysis"]["settings"], SETTINGS, "analysis.settings")
    if payload_hash(record["raw_source"]) != record["provenance"]["payload_sha256"]:
        raise ValueError("Raw NASA payload hash does not match the export.")
    start, end = record["period"]["start"], record["period"]["end"]
    annual, monthly, excluded = annual_series(record["raw_source"], record["variable"], start, end)
    same(record["annual"], annual, "annual")
    same(record["monthly"], monthly, "monthly")
    same(record["excluded_years"], excluded, "excluded_years")
    same(record["trend"], analyze(annual), "trend")
    same(record["checks"], sensitivity_checks(annual, start, end), "checks")
    return len(annual)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis_json", type=Path)
    args = parser.parse_args()
    try:
        record = json.loads(args.analysis_json.read_text())
        years = verify(record)
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, f"Replay failed: {error}\n")
    print(f"Replay passed: raw source hash, aggregation, {years} annual values, trend, and sensitivity checks agree. No network was used.")
