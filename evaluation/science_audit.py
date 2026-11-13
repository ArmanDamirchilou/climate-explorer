"""Exploratory Toronto source diagnostics; see SCIENCE_AUDIT_PROTOCOL.md."""

import calendar
import gzip
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.io import netcdf_file

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from climate import annual_series, fetch_data, payload_hash

OUT = Path(__file__).resolve().parent
YEARS = list(range(1981, 2026))
POINTS = [
    ("nominal_nearby_grid", 43.5, -79.375),
    ("gistemp_cell_center", 43., -79.),
    ("north_neighbor", 44., -79.375),
    ("west_neighbor", 43.5, -80.),
]


def slope(values):
    if len(values) != len(YEARS) or not np.all(np.isfinite(values)):
        raise ValueError("Diagnostic requires all 45 finite annual values")
    return float(stats.linregress(YEARS, values).slope * 10)


def power_diagnostics(saved, label):
    payload = saved["payload"]
    annual, _, excluded = annual_series(payload, "temperature", YEARS[0], YEARS[-1])
    if excluded or [r["year"] for r in annual] != YEARS:
        raise ValueError("Missing POWER year in diagnostic")
    raw = payload["properties"]["parameter"]["T2M"]
    equal = [sum(raw[f"{year}{m:02}"] for m in range(1, 13))/12 for year in YEARS]
    nasa_annual = [raw[f"{year}13"] for year in YEARS]
    weighted = [r["value"] for r in annual]
    return {
        "label": label, "request_url": saved["request_url"], "fetched_at": saved["fetched_at"],
        "payload_sha256": payload_hash(payload), "returned_coordinates": payload.get("geometry", {}).get("coordinates"),
        "weighted_slope_c_per_decade": slope(weighted), "equal_month_slope_c_per_decade": slope(equal),
        "nasa_annual_slope_c_per_decade": slope(nasa_annual),
        "max_abs_weighted_minus_nasa_annual_c": float(max(abs(a-b) for a, b in zip(weighted, nasa_annual))),
        "monthly_slopes_c_per_decade": [{"month": m, "slope": slope([raw[f"{y}{m:02}"] for y in YEARS])} for m in range(1, 13)],
        "annual": [{"year": y, "value": v} for y, v in zip(YEARS, weighted)],
    }


def gistemp_neighbors():
    packed = (OUT/"gistemp250_GHCNv4.nc.gz").read_bytes()
    with netcdf_file(io.BytesIO(gzip.decompress(packed)), mmap=False) as ds:
        if ds.variables["time"].units != b"days since 1800-01-01 00:00:00":
            raise ValueError("Unexpected GISTEMP time encoding")
        dates = [datetime(1800, 1, 1)+timedelta(days=int(t)) for t in ds.variables["time"].data]
        variable = ds.variables["tempanomaly"]
        if variable.units != b"K":
            raise ValueError("Unexpected GISTEMP units")
        rows = []
        for lat in [41., 43., 45.]:
            for lon in [-81., -79., -77.]:
                i = list(ds.variables["lat"].data).index(lat)
                j = list(ds.variables["lon"].data).index(lon)
                grouped = {}
                for d, raw in zip(dates, variable.data[:, i, j]):
                    if YEARS[0] <= d.year <= YEARS[-1] and int(raw) != int(variable._FillValue):
                        grouped.setdefault(d.year, {})[d.month] = float(raw)*float(variable.scale_factor)
                if any(set(grouped.get(y, {})) != set(range(1, 13)) for y in YEARS):
                    rows.append({"latitude": lat, "longitude": lon, "available": False})
                    continue
                weighted = [sum(grouped[y][m]*calendar.monthrange(y, m)[1] for m in range(1, 13))/(366 if calendar.isleap(y) else 365) for y in YEARS]
                equal = [sum(grouped[y].values())/12 for y in YEARS]
                rows.append({"latitude": lat, "longitude": lon, "available": True,
                             "weighted_slope_c_per_decade": slope(weighted), "equal_month_slope_c_per_decade": slope(equal),
                             "monthly_slopes_c_per_decade": [{"month": m, "slope": slope([grouped[y][m] for y in YEARS])} for m in range(1, 13)]})
        return rows


def run():
    saved = json.loads((OUT/"source-snapshots/toronto-power.json").read_text())
    rows = [power_diagnostics(saved, "original_toronto")]
    failures = []
    folder = OUT/"science-audit-snapshots"
    folder.mkdir(exist_ok=True)
    for label, lat, lon in POINTS:
        path = folder/f"{label}.json"
        try:
            if path.exists():
                saved = json.loads(path.read_text())
            else:
                saved, _ = fetch_data(lat, lon)
                path.write_text(json.dumps(saved, allow_nan=False)+"\n")
            rows.append(power_diagnostics(saved, label))
            print(label, rows[-1]["weighted_slope_c_per_decade"], flush=True)
        except Exception as error:
            failures.append({"label": label, "error": str(error)})
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "years": YEARS,
              "scope": "Exploratory fixed-location diagnostic; not station validation or matched spatial support", "power": rows,
              "gistemp_neighbors": gistemp_neighbors(), "failures": failures}
    central_gistemp = next(r for r in result["gistemp_neighbors"] if r["latitude"] == 43 and r["longitude"] == -79)
    (OUT/"science-audit.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    lines = ["# Independent science audit", "", f"Generated {result['generated_utc']}. Read [the exploratory protocol](SCIENCE_AUDIT_PROTOCOL.md) before interpreting this diagnostic.", "", "## Calendar aggregation check", "", "All 45 years from 1981 to 2025 are retained. The comparison uses every available NASA annual record, not three selected years.", "", "| POWER request | Day-weighted slope | Equal-month slope | NASA month-13 slope | Maximum annual difference versus NASA |", "|---|---:|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['label']} | {row['weighted_slope_c_per_decade']:.4f} | {row['equal_month_slope_c_per_decade']:.4f} | {row['nasa_annual_slope_c_per_decade']:.4f} | {row['max_abs_weighted_minus_nasa_annual_c']:.4f} |")
    lines += ["", "Slopes are °C per decade. Annual differences are °C. The small calendar-weighting and rounded annual-value differences cannot explain the original source discrepancy of about 0.572 °C per decade.", "", "## Fixed spatial diagnostic", "", "| GISTEMP cell latitude | Longitude | Day-weighted slope, °C per decade |", "|---|---:|---:|"]
    for row in result["gistemp_neighbors"]:
        lines.append(f"| {row['latitude']} | {row['longitude']} | {row['weighted_slope_c_per_decade']:.4f} |" if row["available"] else f"| {row['latitude']} | {row['longitude']} | unavailable |")
    lines += ["", "The complete 3 by 3 GISTEMP neighborhood stays far below the original POWER rate. Choosing one of these adjacent GISTEMP cells does not remove the discrepancy. These smoothed fields are not independent reference stations.", "", "POWER itself is sensitive to nearby requested locations: the original and nominal nearby grid request both give 0.883 °C per decade, while the fixed north and west requests give about 0.378 and 0.318. At the GISTEMP cell center, POWER gives about 0.446. Thus a location change within POWER substantially changes the comparison. This narrows the investigation toward spatial and source representation; it does not demonstrate which representation is correct or why they differ.", "", "The POWER requests are fixed point diagnostics. They do not average POWER over the GISTEMP support. Exact causal interpretation requires more information about gridding, surface representation, the time series, and reference observations. No source is selected as truth. No application result is silently replaced.", "", "## Monthly diagnostic", "", "All rates are °C per decade. These are descriptive comparisons, with no monthly significance tests.", "", "| Month | Original Toronto POWER rate | Central GISTEMP rate | Difference |", "|---|---:|---:|---:|"]
    for item, g in zip(rows[0]["monthly_slopes_c_per_decade"], central_gistemp["monthly_slopes_c_per_decade"]):
        lines.append(f"| {item['month']} | {item['slope']:.4f} | {g['slope']:.4f} | {item['slope']-g['slope']:+.4f} |")
    lines += ["", "These monthly rates locate where the divergence merits investigation. They do not establish its cause. In particular, lake effects, urbanization, and model changes are hypotheses, not demonstrated explanations.", "", "## Ranked review findings", "", "1. Keep the Toronto discrepancy visible. Numerical agreement with NASA annual summaries supports the implemented aggregation but cannot validate the reanalysis trend.", "2. Do not turn conditional intervals into an automatic significance verdict. The fixed simulation already demonstrates poor coverage under several dependence models. The current labeling and method comparisons are appropriate exploratory safeguards, not a calibrated real-world decision rule.", "3. Product impact remains untested. A real student or teacher pilot and the student's own explanation are still required before educational-benefit claims.", "4. Precipitation has conversion tests but no second-source evaluation. Do not describe the temperature audit as validating rain.", "", "No main application defect was demonstrated by this audit. This does not establish that the application is defect-free.", "", "## Reproduce and sources", "", "Run `.venv/bin/python evaluation/science_audit.py`. Frozen extra responses are in `evaluation/science-audit-snapshots/`. Output JSON preserves annual values, monthly rates, retrieval times, URLs, and payload hashes. Frozen GISTEMP file and its provenance are documented in [DATASET_CHECK.md](DATASET_CHECK.md).", "", "NASA POWER supplies gridded meteorology, not a precise station measurement. Its point and monthly services retain source resolution. [NASA meteorology methodology](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/), [monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/). GISTEMP station smoothing and grid construction differ from POWER. [NASA GISTEMP map notes](https://data.giss.nasa.gov/gistemp/maps/).", "", f"Additional request failures: {len(failures)}. Details are retained in science-audit.json.", ""]
    (OUT/"SCIENCE_AUDIT.md").write_text("\n".join(lines))


if __name__ == "__main__":
    run()
