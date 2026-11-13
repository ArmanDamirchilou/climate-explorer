"""Recompute a frozen analysis JSON without using the network."""

import argparse
import json
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from climate import DataUnavailable, VARIABLES, analyze, annual_series, payload_hash
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


def verify_context(record):
    """Bind displayed units, dates and coordinates to the retained request."""
    for field in ("period", "location", "provenance", "analysis", "raw_source"):
        if not isinstance(record[field], dict):
            raise ValueError(f"Invalid {field} object.")
    variable = record["variable"]
    if variable not in VARIABLES:
        raise ValueError("Unsupported climate variable.")
    same(record["metadata"], VARIABLES[variable], "metadata")
    start, end = record["period"]["start"], record["period"]["end"]
    if (type(start) is not int or type(end) is not int or start < 1981
            or end > datetime.now(timezone.utc).year - 1 or not 9 <= end - start < 150):
        raise ValueError("Invalid analysis calendar period.")
    location = record["location"]
    for key, limit in [("latitude", 90), ("longitude", 180)]:
        value = location[key]
        if type(value) not in (int, float) or not math.isfinite(value) or abs(value) > limit:
            raise ValueError("Invalid analysis coordinates.")
    provenance = record["provenance"]
    if provenance["provider"] != "NASA POWER":
        raise ValueError("Unsupported source provider.")
    if provenance["payload_hash_format"] != "SHA256 of Python sorted-key compact JSON after converting integral floats to integers, including negative zero":
        raise ValueError("Unsupported source hash format.")
    for value, field in [(provenance["payload_sha256"], "source hash"), (record["analysis"]["code_sha256"], "code fingerprint")]:
        if not isinstance(value, str) or not re.fullmatch(r"[a-f0-9]{64}", value):
            raise ValueError(f"Invalid {field}.")
    if not isinstance(provenance["request_url"], str):
        raise ValueError("Invalid NASA source request URL.")
    url = urlsplit(provenance["request_url"])
    if (url.scheme != "https" or url.netloc != "power.larc.nasa.gov"
            or url.path != "/api/temporal/monthly/point" or url.fragment):
        raise ValueError("Unsupported NASA source request URL.")
    query = parse_qs(url.query, keep_blank_values=True)
    required = {"latitude", "longitude", "start", "end", "parameters", "format", "community"}
    if set(query) != required or any(len(values) != 1 for values in query.values()):
        raise ValueError("Invalid or ambiguous NASA request parameters.")
    for key in ["latitude", "longitude"]:
        value = float(query[key][0])
        if not math.isfinite(value) or abs(value - location[key]) > .00005:
            raise ValueError("Source request coordinates differ from the analysis.")
    if (any(not re.fullmatch(r"\d{4}", query[key][0]) for key in ["start", "end"])
            or int(query["start"][0]) > start or int(query["end"][0]) < end):
        raise ValueError("Source request period does not cover the analysis.")
    if any(query[key][0] != value for key, value in [("parameters", "T2M,PRECTOTCORR"), ("format", "JSON"), ("community", "AG")]):
        raise ValueError("Unsupported NASA request parameters.")
    retrieved = provenance["fetched_at"]
    if not isinstance(retrieved, str) or datetime.fromisoformat(retrieved).utcoffset() is None:
        raise ValueError("Invalid source retrieval timestamp.")
    header = record["raw_source"].get("header", {})
    geometry = record["raw_source"].get("geometry", {})
    if not isinstance(header, dict) or not isinstance(header.get("api", {}), dict) or not isinstance(geometry, dict):
        raise ValueError("Invalid NASA source descriptors.")
    for key, expected in [("sources", header.get("sources", [])), ("api_version", header.get("api", {}).get("version")), ("time_standard", header.get("time_standard")), ("returned_coordinates", geometry.get("coordinates"))]:
        same(provenance[key], expected, f"provenance.{key}")


def verify(record):
    if not isinstance(record, dict):
        raise ValueError("The export must be a JSON object.")
    if record.get("format") == "Climate Explorer investigation 1":
        record = record["analysis"]
    if not isinstance(record, dict):
        raise ValueError("The analysis must be a JSON object.")
    if "raw_source" not in record:
        raise ValueError("This export predates replay support. Download a new analysis JSON.")
    verify_context(record)
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
    except (OSError, ValueError, KeyError, TypeError, DataUnavailable) as error:
        parser.exit(1, f"Replay failed: {error}\n")
    print(f"Replay passed: raw source hash, aggregation, {years} annual values, trend, and sensitivity checks agree. No network was used.")
