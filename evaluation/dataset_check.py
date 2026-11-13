"""Coarse-scale temperature consistency check, not station validation."""

import calendar
import gzip
import hashlib
import io
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
from scipy import stats
from scipy.io import netcdf_file

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from climate import PRESETS, annual_series, fetch_data, payload_hash

OUT = Path(__file__).resolve().parent
SOURCE = "https://data.giss.nasa.gov/pub/gistemp/gistemp250_GHCNv4.nc.gz"


def run():
    path = OUT / "gistemp250_GHCNv4.nc.gz"
    if not path.exists():
        raise SystemExit(f"Download {SOURCE} to {path} before running. No account is needed.")
    packed = path.read_bytes()
    with netcdf_file(io.BytesIO(gzip.decompress(packed)), mmap=False) as ds:
        latitudes = ds.variables["lat"].data.copy()
        longitudes = ds.variables["lon"].data.copy()
        times = ds.variables["time"]
        if times.units != b"days since 1800-01-01 00:00:00":
            raise ValueError("Unexpected GISTEMP calendar encoding")
        dates = [datetime(1800, 1, 1)+timedelta(days=int(t)) for t in times.data]
        variable = ds.variables["tempanomaly"]
        if variable.units != b"K":
            raise ValueError("Unexpected GISTEMP anomaly unit")
        scale, fill = float(variable.scale_factor), int(variable._FillValue)
        history = ds.history.decode()
        rows = []
        for key, place in PRESETS.items():
            i = int(np.argmin(abs(latitudes-place["latitude"])))
            j = int(np.argmin(abs(longitudes-place["longitude"])))
            cell = variable.data[:, i, j].copy()
            grouped = {}
            for date, value in zip(dates, cell):
                if not 1981 <= date.year <= 2025 or int(value) == fill:
                    continue
                grouped.setdefault(date.year, []).append((date.month, float(value)*scale))
            gistemp = {}
            for year, months in grouped.items():
                if len(months) != 12 or len({m for m, _ in months}) != 12:
                    continue
                days = [calendar.monthrange(year, m)[1] for m, _ in months]
                gistemp[year] = sum(v*d for (_, v), d in zip(months, days))/sum(days)
            snapshots = OUT / "source-snapshots"
            snapshot = snapshots/f"{key}-power.json"
            if snapshot.exists():
                saved = json.loads(snapshot.read_text())
            else:
                saved, _ = fetch_data(place["latitude"], place["longitude"])
            power_rows, _, _ = annual_series(saved["payload"], "temperature", 1981, 2025)
            power = {r["year"]: r["value"] for r in power_rows}
            years = sorted(set(gistemp) & set(power))
            if len(years) < 30:
                raise ValueError(f"Fewer than 30 common complete years for {key}")
            g = [gistemp[y] for y in years]
            p = [power[y] for y in years]
            g_slope, p_slope = stats.linregress(years, g).slope*10, stats.linregress(years, p).slope*10
            rows.append({"name": place["name"], "requested_coordinates": [place["latitude"], place["longitude"]],
                         "gistemp_cell_center": [float(latitudes[i]), float(longitudes[j])], "years": years,
                         "gistemp_slope_c_per_decade": float(g_slope), "power_slope_c_per_decade": float(p_slope),
                         "slope_difference_power_minus_gistemp": float(p_slope-g_slope),
                         "annual_correlation": float(np.corrcoef(g, p)[0, 1]),
                         "power_source_url": saved["request_url"], "power_retrieved_utc": saved["fetched_at"],
                         "power_payload_sha256": payload_hash(saved["payload"]),
                         "annual": [{"year": y, "gistemp_anomaly_c": gistemp[y], "power_temperature_c": power[y]} for y in years]})
            snapshots.mkdir(exist_ok=True)
            if not snapshot.exists():
                snapshot.write_text(json.dumps(saved, allow_nan=False)+"\n")
            print(f"Compared {place['name']}: {len(years)} years; POWER {p_slope:.3f}, GISTEMP {g_slope:.3f} °C/decade", flush=True)
    result = {"generated_utc": datetime.now(timezone.utc).isoformat(), "gistemp_source": SOURCE,
              "gistemp_compressed_sha256": hashlib.sha256(packed).hexdigest(), "gistemp_history": history,
              "gistemp_resolution": "2° by 2°, land-only, 250 km station smoothing",
              "aggregation": "Day-weighted complete calendar years in both sources; identical intersection of years per place",
              "scope": "Exploratory coarse-scale consistency check. Different fields and spatial supports; not independent ground truth or validation of a street-level trend.",
              "rows": rows}
    (OUT/"dataset-check.json").write_text(json.dumps(result, indent=2, allow_nan=False)+"\n")
    lines = ["# Temperature dataset consistency check", "", result["scope"], "", "Five locations were the existing application presets, chosen before this comparison. All available common complete years in 1981–2025 are used. Annual values are day-weighted in both datasets; no window was chosen to improve agreement.", "", "| Location | GISTEMP cell center latitude longitude | Common years | POWER °C per decade | GISTEMP °C per decade | Difference |", "|---|---|---|---:|---:|---:|"]
    for row in rows:
        lines.append(f"| {row['name']} | {row['gistemp_cell_center']} | {row['years'][0]}–{row['years'][-1]} ({len(row['years'])}) | {row['power_slope_c_per_decade']:.3f} | {row['gistemp_slope_c_per_decade']:.3f} | {row['slope_difference_power_minus_gistemp']:+.3f} |")
    lines += ["", "## Interpretation", "", "A difference is not automatically a software error. POWER is gridded reanalysis of near-surface air temperature. This GISTEMP file is an observation-based temperature-anomaly analysis with a different grid and smoothing. A fixed reference temperature does not change a slope, but spatial sampling, smoothing, and processing can. Shared observations also mean the datasets are not necessarily statistically independent. Neither is a local reference station.", "", "This check evaluates temperature only. It does not validate precipitation or establish uncertainty coverage. Larger regional claims require matching spatial supports and a dedicated dataset evaluation.", "", "## Reproduction and sources", "", "Run `.venv/bin/python evaluation/dataset_check.py`. The frozen compressed GISTEMP input is beside the script. POWER responses are retained in `evaluation/source-snapshots/`. The output JSON contains annual values, actual coordinates, source dates, and hashes.", "", f"GISTEMP file history: {history}.", f"Compressed file SHA256: {result['gistemp_compressed_sha256']}.", "", "GISTEMP Team, 2026: GISS Surface Temperature Analysis, version 4. NASA GISS. Accessed 11 November 2026. [Data and methods](https://data.giss.nasa.gov/gistemp/), [download description](https://data.giss.nasa.gov/gistemp/data_v4.html). Lenssen et al. (2024), A GISTEMPv4 observational uncertainty ensemble, JGR Atmospheres 129, e2023JD040179, [doi:10.1029/2023JD040179](https://doi.org/10.1029/2023JD040179).", "", "POWER data provided by the NASA POWER Project. [Monthly API](https://power.larc.nasa.gov/docs/services/api/temporal/monthly/) and [meteorology sources](https://power.larc.nasa.gov/docs/methodology/data/sources_meteorology/).", ""]
    (OUT/"DATASET_CHECK.md").write_text("\n".join(lines))


if __name__ == "__main__":
    run()
