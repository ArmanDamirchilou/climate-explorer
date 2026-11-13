import json
import math
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from climate import DataUnavailable, ROOT, analyze, annual_series, fetch_data, validate_query


def fixture(value, variable="temperature"):
    key, unit = ("T2M", "C") if variable == "temperature" else ("PRECTOTCORR", "mm/day")
    return {"header": {"fill_value": -999}, "parameters": {key: {"units": unit}},
            "properties": {"parameter": {key: {f"{year}{month:02}": value for year in range(1981, 2001) for month in range(1, 14)}}}}


class AggregationTests(unittest.TestCase):
    def test_precipitation_uses_days_including_leap_year(self):
        annual, monthly, excluded = annual_series(fixture(1, "rainfall"), "rainfall", 1981, 1984)
        self.assertEqual([row["value"] for row in annual], [365, 365, 365, 366])
        self.assertEqual(next(row["value"] for row in monthly if row["year"] == 1984 and row["month"] == 2), 29)
        self.assertEqual(excluded, [])

    def test_temperature_is_day_weighted_and_ignores_month_13(self):
        payload = fixture(0)
        payload["properties"]["parameter"]["T2M"]["198402"] = 10
        payload["properties"]["parameter"]["T2M"]["198413"] = 5000
        annual, _, _ = annual_series(payload, "temperature", 1984, 1984)
        self.assertAlmostEqual(annual[0]["value"], 290 / 366)

    def test_missing_or_nonfinite_month_excludes_whole_year(self):
        for value in [-999, None, float("nan"), float("inf")]:
            with self.subTest(value=value):
                payload = fixture(10)
                payload["properties"]["parameter"]["T2M"]["199006"] = value
                annual, monthly, excluded = annual_series(payload, "temperature", 1981, 2000)
                self.assertEqual(excluded, [1990])
                self.assertEqual(len(annual), 19)
                self.assertIsNone(next(row["value"] for row in monthly if row["year"] == 1990 and row["month"] == 6))

    def test_unit_change_stops_analysis(self):
        payload = fixture(1, "rainfall")
        payload["parameters"]["PRECTOTCORR"]["units"] = "mm/month"
        with self.assertRaises(DataUnavailable):
            annual_series(payload, "rainfall", 1981, 2000)


class TrendTests(unittest.TestCase):
    def test_known_linear_slope_and_interval(self):
        result = analyze([{"year": year, "value": 10 + .2 * (year - 1981)} for year in range(1981, 2001)])
        self.assertAlmostEqual(result["slope_per_decade"], 2)
        self.assertAlmostEqual(result["fitted_change"], 3.8)
        self.assertEqual(result["evidence"], "positive")
        self.assertTrue(result["ci95_per_decade"][0] <= 2 <= result["ci95_per_decade"][1])

    def test_constant_series_has_no_evidence_and_valid_json(self):
        result = analyze([{"year": year, "value": 10} for year in range(1981, 2001)])
        self.assertEqual(result["evidence"], "unclear")
        self.assertEqual(result["slope_per_decade"], 0)
        json.dumps(result, allow_nan=False)

    def test_incomplete_short_record_cannot_produce_trend(self):
        with self.assertRaises(DataUnavailable):
            analyze([{"year": year, "value": year} for year in range(1981, 1989)])

    def test_gap_disables_adjacent_year_correlation_diagnostic(self):
        years = [year for year in range(1981, 2001) if year != 1990]
        result = analyze([{"year": year, "value": math.sin(year)} for year in years])
        self.assertIsNone(result["lag1_residual_correlation"])


class ValidationTests(unittest.TestCase):
    def test_rejects_invalid_ranges_and_variables(self):
        for query in [{"latitude": "nan"}, {"longitude": "181"}, {"latitude": "-91"},
                      {"start": "2020", "end": "2025"}, {"start": "1970"},
                      {"end": "9999"}, {"variable": "arbitrary"}]:
            with self.subTest(query=query), self.assertRaises(ValueError):
                validate_query(query)

    def test_ten_year_window_is_valid(self):
        self.assertEqual(validate_query({"start": "2000", "end": "2009"})[2:4], (2000, 2009))

    def test_snapshot_is_real_and_complete(self):
        saved = json.loads((ROOT / "data/tehran-nasa-snapshot.json").read_text())
        self.assertIn("power.larc.nasa.gov/api/temporal/monthly/point", saved["request_url"])
        for variable in ["temperature", "rainfall"]:
            annual, monthly, excluded = annual_series(saved["payload"], variable, 1981, 2025)
            self.assertEqual(len(annual), 45)
            self.assertEqual(len(monthly), 540)
            self.assertEqual(excluded, [])
            json.dumps(analyze(annual), allow_nan=False)

    def test_network_failure_uses_labelled_tehran_snapshot(self):
        with patch("climate.urlopen", side_effect=URLError("offline")), patch.object(Path, "exists", lambda path: path.name == "tehran-nasa-snapshot.json"):
            saved, delivery = fetch_data(35.6892, 51.389)
            self.assertIn("offline fallback", delivery)
            self.assertEqual(saved["payload"]["header"]["sources"], ["MERRA2"])


if __name__ == "__main__":
    unittest.main()
