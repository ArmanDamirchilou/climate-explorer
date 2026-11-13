"""NASA POWER data retrieval and transparent annual trend analysis."""

import calendar
import hashlib
import json
import math
import platform
import threading
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import numpy as np
import scipy
import statsmodels
from scipy import stats

from trend_checks import SETTINGS, sensitivity_checks

ROOT = Path(__file__).resolve().parent
FIRST_YEAR = 1981
LAST_YEAR = datetime.now(timezone.utc).year - 1
VARIABLES = {
    "temperature": {"parameter": "T2M", "name": "Temperature", "unit": "°C", "monthly_unit": "°C", "aggregation": "Day-weighted annual mean"},
    "rainfall": {"parameter": "PRECTOTCORR", "name": "Precipitation", "unit": "mm/year", "monthly_unit": "mm/month", "aggregation": "Sum of monthly precipitation totals"},
}
PRESETS = {
    "tehran": {"name": "Tehran, Iran", "latitude": 35.6892, "longitude": 51.389},
    "ankara": {"name": "Ankara, Turkey", "latitude": 39.9334, "longitude": 32.8597},
    "berlin": {"name": "Berlin, Germany", "latitude": 52.52, "longitude": 13.405},
    "toronto": {"name": "Toronto, Canada", "latitude": 43.6532, "longitude": -79.3832},
    "milan": {"name": "Milan, Italy", "latitude": 45.4642, "longitude": 9.19},
}
FETCH_LOCK = threading.Lock()
CODE_FILES = ["climate.py", "trend_checks.py", "server.py", "build_demo.py", "evaluation/replay.py", "requirements-lock.txt", "static/app.js", "static/index.html", "static/style.css", "static/validation.js", "static/validation.html"]
CODE_SHA256 = hashlib.sha256(b"".join(
    name.encode() + b"\0" + (ROOT / name).read_bytes()
    for name in CODE_FILES
)).hexdigest()


def payload_hash(payload):
    """Hash numeric-equivalent JSON consistently after a JavaScript round trip.

    JSON has one number type. JavaScript serializes 1.0 as 1, so normalize
    integral floats (including negative zero) before using Python's JSON writer.
    This is our recorded project format, not a claim to implement RFC 8785.
    """
    def normalize(value):
        if isinstance(value, dict):
            return {key: normalize(item) for key, item in value.items()}
        if isinstance(value, list):
            return [normalize(item) for item in value]
        if isinstance(value, float) and math.isfinite(value) and value.is_integer():
            return int(value)
        return value
    return hashlib.sha256(json.dumps(normalize(payload), sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


class DataUnavailable(Exception):
    pass


def validate_query(query):
    """Validate all user input before building a fixed-host NASA request."""
    try:
        lat = float(query.get("latitude", "35.6892"))
        lon = float(query.get("longitude", "51.389"))
        start = int(query.get("start", "1981"))
        end = int(query.get("end", str(LAST_YEAR)))
    except (ValueError, TypeError):
        raise ValueError("Coordinates and years must be numbers.") from None
    if not math.isfinite(lat) or not math.isfinite(lon) or not -90 <= lat <= 90 or not -180 <= lon <= 180:
        raise ValueError("Use a latitude from −90 to 90 and a longitude from −180 to 180.")
    if start < FIRST_YEAR or end > LAST_YEAR or end - start < 9:
        raise ValueError(f"Choose at least 10 years between {FIRST_YEAR} and {LAST_YEAR}.")
    variable = query.get("variable", "temperature")
    if variable not in VARIABLES:
        raise ValueError("Choose temperature or precipitation.")
    return round(lat, 4), round(lon, 4), start, end, variable


def source_url(lat, lon):
    return "https://power.larc.nasa.gov/api/temporal/monthly/point?" + urlencode({
        "parameters": "T2M,PRECTOTCORR", "community": "AG", "longitude": lon,
        "latitude": lat, "format": "JSON", "start": FIRST_YEAR, "end": LAST_YEAR,
    })


def fetch_data(lat, lon):
    url = source_url(lat, lon)
    key = hashlib.sha256(url.encode()).hexdigest()[:20]
    cache = ROOT / "data" / "cache" / f"{key}.json"
    # Small local cache avoids repeatedly requesting the same historical record.
    with FETCH_LOCK:
        if cache.exists():
            try:
                saved = json.loads(cache.read_text())
                age = (datetime.now(timezone.utc) - datetime.fromisoformat(saved["fetched_at"])).total_seconds()
                if 0 <= age < 86400:
                    return saved, "cached NASA response"
            except (ValueError, KeyError, OSError):
                pass
        try:
            request = Request(url, headers={"User-Agent": "ClimateExplorer/0.3.0 (independent student research tool)"})
            with urlopen(request, timeout=40) as response:
                payload = json.load(response)
            if not payload.get("properties", {}).get("parameter"):
                raise DataUnavailable("NASA returned no climate variables for this location.")
            saved = {"fetched_at": datetime.now(timezone.utc).isoformat(), "request_url": url, "payload": payload}
            try:
                cache.parent.mkdir(parents=True, exist_ok=True)
                temp = cache.with_suffix(".tmp")
                temp.write_text(json.dumps(saved))
                temp.replace(cache)
            except OSError:
                pass  # A read-only disk must not prevent live analysis.
            return saved, "live NASA response"
        except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
            # A real, dated Tehran snapshot supports a useful first run offline.
            if abs(lat - 35.6892) < 0.0001 and abs(lon - 51.389) < 0.0001:
                sample = ROOT / "data" / "tehran-nasa-snapshot.json"
                if sample.exists():
                    return json.loads(sample.read_text()), "bundled NASA snapshot (offline fallback)"
            if cache.exists():
                try:
                    return json.loads(cache.read_text()), "older cached NASA response (live service unavailable)"
                except (OSError, ValueError):
                    pass
            raise DataUnavailable("NASA data could not be loaded. Try again, or choose Tehran to use the included real NASA snapshot.") from error


def annual_series(payload, variable, start, end):
    info = VARIABLES[variable]
    parameters = payload.get("parameters", {})
    raw_unit = parameters.get(info["parameter"], {}).get("units")
    expected = {"temperature": {"C", "°C"}, "rainfall": {"mm/day"}}
    if raw_unit not in expected[variable]:
        raise DataUnavailable(f"NASA returned an unexpected unit ({raw_unit}). Analysis stopped to avoid an incorrect conversion.")
    raw = payload["properties"]["parameter"][info["parameter"]]
    fill = payload.get("header", {}).get("fill_value", -999)
    monthly, annual, excluded = [], [], []
    for year in range(start, end + 1):
        months = []
        for month in range(1, 13):
            value = raw.get(f"{year}{month:02}")
            valid = isinstance(value, (int, float)) and math.isfinite(value) and value != fill
            if valid and variable == "rainfall" and value < 0:
                valid = False
            days = calendar.monthrange(year, month)[1]
            display_value = value * days if valid and variable == "rainfall" else value if valid else None
            monthly.append({"year": year, "month": month, "value": display_value})
            if valid:
                months.append((value, days))
        # Do not use NASA's month 13 aggregate or annualize a partial year.
        if len(months) == 12:
            total = sum(value * days for value, days in months)
            value = total / sum(days for _, days in months) if variable == "temperature" else total
            annual.append({"year": year, "value": value})
        else:
            excluded.append(year)
    return annual, monthly, excluded


def analyze(annual):
    if len(annual) < 10:
        raise DataUnavailable("Fewer than 10 complete years are available. Choose a longer period or another location.")
    x = np.array([row["year"] for row in annual], dtype=float)
    y = np.array([row["value"] for row in annual], dtype=float)
    fit = stats.linregress(x, y)
    critical = float(stats.t.ppf(0.975, len(x) - 2))
    # Recent SciPy versions return a NaN standard error for constant values.
    # That degenerate series has slope zero and no evidence of a trend.
    stderr = 0.0 if np.ptp(y) == 0 else float(fit.stderr)
    margin = critical * stderr
    fitted = fit.intercept + fit.slope * x
    residuals = y - fitted
    lag1 = None
    if len(x) > 2 and np.all(np.diff(x) == 1) and np.std(residuals[:-1]) > 1e-10 and np.std(residuals[1:]) > 1e-10:
        lag1 = float(np.corrcoef(residuals[:-1], residuals[1:])[0, 1])
    # This is a confidence band for the fitted mean, not a prediction interval.
    spread = float(np.sum((x - x.mean()) ** 2))
    sigma = float(np.sqrt(np.sum(residuals ** 2) / (len(x) - 2)))
    band = critical * sigma * np.sqrt(1 / len(x) + (x - x.mean()) ** 2 / spread)
    low, high = float((fit.slope - margin) * 10), float((fit.slope + margin) * 10)
    p_value = float(fit.pvalue) if np.isfinite(fit.pvalue) else 1.0
    return {
        "years": len(x), "slope_per_decade": float(fit.slope * 10),
        "ci95_per_decade": [low, high], "p_value": p_value,
        "r_squared": float(fit.rvalue ** 2) if np.isfinite(fit.rvalue) else 0.0,
        "evidence": "positive" if low > 0 else "negative" if high < 0 else "unclear",
        "lag1_residual_correlation": lag1,
        "fitted_change": float(fit.slope * (x[-1] - x[0])),
        "mean": float(y.mean()), "first_year": int(x[0]), "last_year": int(x[-1]),
        "line": [{"year": int(year), "value": float(value), "low": float(value - width), "high": float(value + width)} for year, value, width in zip(x, fitted, band)],
    }


def investigate(query):
    lat, lon, *_ = validate_query(query)
    saved, delivery = fetch_data(lat, lon)
    return analyze_saved(query, saved, delivery)


def analyze_saved(query, saved, delivery="frozen NASA response"):
    """Analyze an explicit source record; no network access or cache mutation."""
    lat, lon, start, end, variable = validate_query(query)
    annual, monthly, excluded = annual_series(saved["payload"], variable, start, end)
    trend = analyze(annual)
    checks = sensitivity_checks(annual, start, end)
    header = saved["payload"].get("header", {})
    return {
        "location": {"latitude": lat, "longitude": lon},
        "period": {"start": start, "end": end}, "variable": variable,
        "metadata": VARIABLES[variable], "annual": annual, "monthly": monthly,
        "excluded_years": excluded, "trend": trend, "checks": checks,
        "analysis": {"settings": SETTINGS, "app_release": "0.3.0", "code_sha256": CODE_SHA256, "code_files": CODE_FILES, "build_started": "2026-11-11",
                     "versions": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__, "statsmodels": statsmodels.__version__}},
        "raw_source": saved["payload"],
        "provenance": {"provider": "NASA POWER", "sources": header.get("sources", []),
            "api_version": header.get("api", {}).get("version"),
            "fetched_at": saved["fetched_at"], "request_url": saved["request_url"],
            "payload_sha256": payload_hash(saved["payload"]),
            "payload_hash_format": "SHA256 of Python sorted-key compact JSON after converting integral floats to integers, including negative zero",
            "spatial_resolution": {"latitude_degrees": .5, "longitude_degrees": .625,
                                   "description": "Native MERRA-2 meteorology grid: 0.5° latitude × 0.625° longitude. Requested coordinates do not imply street-level precision.",
                                   "source": "https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/"},
            "delivery": delivery, "time_standard": header.get("time_standard"),
            "returned_coordinates": saved["payload"].get("geometry", {}).get("coordinates")},
    }
