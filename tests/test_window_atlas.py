import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
from statsmodels.regression.linear_model import OLS

from climate import PRESETS, ROOT, analyze_saved
from evaluation.replay import verify
from window_atlas import build_window_atlas, materialize, validate_atlas


def base_record(saved, start=1981, end=2025):
    return analyze_saved({**PRESETS["tehran"], "start": start, "end": end, "variable": "temperature"}, saved)


class WindowAtlasTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads((ROOT/"evaluation/source-snapshots/tehran-power.json").read_text())
        cls.base = base_record(cls.saved)
        with patch("climate.urlopen", side_effect=AssertionError("Atlas must stay offline")):
            cls.atlas = build_window_atlas(cls.base)

    def test_all_666_calendar_windows_are_present_once(self):
        expected = {(start, start+length-1) for length in range(10, 46) for start in range(1981, 2027-length)}
        actual = [(row["start"], row["end"]) for row in self.atlas["windows"]]
        self.assertEqual(len(actual), 666)
        self.assertEqual(set(actual), expected)
        self.assertEqual(len(set(actual)), len(actual))
        self.assertEqual(actual, sorted(actual))
        self.assertEqual(self.atlas["summary"]["available_windows"], 666)

    def test_every_compact_cell_materializes_and_fully_replays_offline(self):
        with patch("climate.urlopen", side_effect=AssertionError("Verification must stay offline")):
            self.assertEqual(validate_atlas(self.atlas, full=True), 666)

    def test_selected_intervals_match_independent_statsmodels_reference(self):
        for start, end in ((1981, 1990), (1981, 2025), (2001, 2020), (2011, 2025)):
            with self.subTest(start=start, end=end):
                record = materialize(self.atlas, start, end)
                x = np.array([row["year"] for row in record["annual"]], dtype=float)
                y = np.array([row["value"] for row in record["annual"]], dtype=float)
                reference = OLS(y, np.column_stack([np.ones(len(x)), x-x.mean()])).fit()
                self.assertAlmostEqual(record["trend"]["slope_per_decade"], reference.params[1]*10, places=10)
                np.testing.assert_allclose(record["trend"]["ci95_per_decade"], reference.conf_int()[1]*10, rtol=1e-9, atol=1e-9)

    def test_materialized_record_preserves_evidence_without_stale_fixed_context(self):
        atlas = copy.deepcopy(self.atlas)
        atlas["base_analysis"]["window_context"] = {"id": "full45"}
        record = materialize(atlas, 1993, 2018)
        self.assertNotIn("window_context", record)
        self.assertEqual(record["period"], {"start": 1993, "end": 2018})
        self.assertEqual(record["raw_source"], self.base["raw_source"])
        self.assertEqual(record["provenance"], self.base["provenance"])
        self.assertEqual(record["analysis"], self.base["analysis"])
        self.assertEqual(verify(record), 26)
        record["trend"]["slope_per_decade"] += 100
        self.assertEqual(validate_atlas(atlas), 666)

    def test_omitted_duplicate_reordered_and_false_coverage_rows_are_rejected(self):
        for change in ("omitted", "duplicate", "reordered", "coverage"):
            atlas = copy.deepcopy(self.atlas)
            if change == "omitted":
                atlas["windows"].pop()
            elif change == "duplicate":
                atlas["windows"][-1] = copy.deepcopy(atlas["windows"][0])
            elif change == "reordered":
                atlas["windows"][0], atlas["windows"][1] = atlas["windows"][1], atlas["windows"][0]
            else:
                atlas["windows"][0]["complete_years"] -= 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_atlas(atlas)

    def test_point_tampering_is_detected_even_when_duplicate_fields_match(self):
        atlas = copy.deepcopy(self.atlas)
        row = atlas["windows"][0]
        row["slope_per_decade"] += .1
        row["trend"]["slope_per_decade"] += .1
        with self.assertRaisesRegex(ValueError, "recomputed_slope"):
            validate_atlas(atlas)

    def test_source_location_units_and_intervals_are_checked(self):
        for change in ("location", "unit", "interval", "raw", "period"):
            atlas = copy.deepcopy(self.atlas)
            if change == "location":
                atlas["base_analysis"]["location"] = PRESETS["ankara"].copy()
            elif change == "unit":
                atlas["base_analysis"]["metadata"]["unit"] = "Fahrenheit"
            elif change == "raw":
                atlas["base_analysis"]["raw_source"]["properties"]["parameter"]["T2M"]["198101"] += 1
            elif change == "period":
                atlas["base_analysis"]["period"]["end"] = 1000000000
            else:
                row = atlas["windows"][0]
                row["ordinary_ci95_per_decade"][0] -= 1
                row["trend"]["ci95_per_decade"][0] -= 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_atlas(atlas, full=True)

    def test_cross_case_row_is_rejected_against_retained_series(self):
        berlin = json.loads((ROOT/"evaluation/source-snapshots/berlin-power.json").read_text())
        other = analyze_saved({**PRESETS["berlin"], "start": 1981, "end": 1990, "variable": "temperature"}, berlin)
        atlas = copy.deepcopy(self.atlas)
        row = atlas["windows"][0]
        row.update({"trend": other["trend"], "checks": other["checks"],
                    "slope_per_decade": other["trend"]["slope_per_decade"],
                    "ordinary_ci95_per_decade": other["trend"]["ci95_per_decade"]})
        with self.assertRaisesRegex(ValueError, "recomputed_slope"):
            validate_atlas(atlas)

    def test_missing_year_keeps_calendar_universe_and_withholds_gap_hac(self):
        saved = copy.deepcopy(self.saved)
        saved["payload"]["properties"]["parameter"]["T2M"]["200606"] = -999
        atlas = build_window_atlas(base_record(saved))
        self.assertEqual(len(atlas["windows"]), 666)
        missing = next(row for row in atlas["windows"] if (row["start"], row["end"]) == (2001, 2010))
        self.assertFalse(missing["available"])
        self.assertNotIn("trend", missing)
        with self.assertRaises(ValueError):
            materialize(atlas, 2001, 2010)
        record = materialize(atlas, 2001, 2011)
        self.assertEqual(record["excluded_years"], [2006])
        self.assertEqual(len(record["annual"]), 10)
        self.assertFalse(record["checks"]["hac_available"])
        self.assertEqual(verify(record), 10)
        self.assertEqual(validate_atlas(atlas), atlas["summary"]["available_windows"])

    def test_invalid_minimum_and_nonrecorded_selection_are_rejected(self):
        for minimum in (True, 9, 46, 10.5):
            with self.subTest(minimum=minimum), self.assertRaises(ValueError):
                build_window_atlas(self.base, minimum)
        for period in ((1980, 2025), (1981, 1989), (2025, 1981)):
            with self.subTest(period=period), self.assertRaises(ValueError):
                materialize(self.atlas, *period)

    def test_small_constant_atlas_is_deterministic_and_has_no_false_trend(self):
        saved = copy.deepcopy(self.saved)
        saved["payload"]["properties"]["parameter"]["T2M"] = {key: 10 for key in saved["payload"]["properties"]["parameter"]["T2M"]}
        base = base_record(saved, 1981, 1995)
        before = copy.deepcopy(base)
        first, second = build_window_atlas(base), build_window_atlas(base)
        self.assertEqual(first, second)
        self.assertEqual(base, before)
        self.assertEqual(len(first["windows"]), 21)
        self.assertEqual(first["summary"]["zero_slope_windows"], 21)
        self.assertEqual(first["summary"]["ordinary_interval_excludes_zero_windows"], 0)
        self.assertEqual(validate_atlas(first, full=True), 21)

    def test_cli_verifies_downloaded_atlas_and_rejects_modified_file(self):
        small = build_window_atlas(base_record(self.saved, 1981, 1995))
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)/"downloaded-atlas.json"
            path.write_text(json.dumps(small, allow_nan=False))
            result = subprocess.run([sys.executable, str(ROOT/"window_atlas.py"), "--verify", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("21 windows", result.stdout)
            small["windows"].pop()
            path.write_text(json.dumps(small, allow_nan=False))
            changed = subprocess.run([sys.executable, str(ROOT/"window_atlas.py"), "--verify", str(path)], capture_output=True, text=True)
            self.assertNotEqual(changed.returncode, 0)
            self.assertIn("Atlas verification failed", changed.stderr)


if __name__ == "__main__":
    unittest.main()
