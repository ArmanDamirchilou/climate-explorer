import copy
import json
import shutil
import subprocess
import unittest
from unittest.mock import patch

import numpy as np
from scipy import stats

from climate import ROOT, analyze, investigate
from evaluation.replay import verify
from trend_checks import sensitivity_checks


def series(values, start=1981):
    return [{"year": start+i, "value": float(value)} for i, value in enumerate(values)]


class SensitivityTests(unittest.TestCase):
    def test_hac_interval_against_scalar_sandwich_reference(self):
        # An independent, slope-only calculation avoids using statsmodels as its own oracle.
        years = np.arange(1981, 2026)
        y = .03*(years-1981)+np.sin(np.arange(45)*.8)
        x = years-years.mean()
        b = np.dot(x, y)/np.dot(x, x)
        residuals = y-y.mean()-b*x
        scores = x*residuals
        lag = 3
        meat = np.dot(scores, scores)
        for k in range(1, lag+1):
            meat += 2*(1-k/(lag+1))*np.dot(scores[k:], scores[:-k])
        se = np.sqrt((45/43)*meat/(np.dot(x, x)**2))
        expected = (b+np.array([-1, 1])*stats.t.ppf(.975, 43)*se)*10
        result = sensitivity_checks(series(y), 1981, 2025)
        self.assertEqual(result["automatic_lag"], lag)
        np.testing.assert_allclose(result["intervals"][1]["ci95_per_decade"], expected, atol=1e-11)
        self.assertAlmostEqual(result["intervals"][1]["slope_per_decade"], b*10)

    def test_missing_year_never_compresses_time_for_hac(self):
        rows = series(np.sin(np.arange(45)))
        del rows[20]
        result = sensitivity_checks(rows, 1981, 2025)
        self.assertFalse(result["hac_available"])
        self.assertEqual(len(result["intervals"]), 1)
        self.assertIn("Missing calendar years", " ".join(result["messages"]))

    def test_short_window_reports_unavailable_date_checks(self):
        result = sensitivity_checks(series(np.arange(10)), 1981, 1990)
        self.assertEqual(sum(r["available"] for r in result["periods"]), 1)
        self.assertTrue(any("Fewer than 30" in message for message in result["messages"]))

    def test_robust_estimate_resists_single_endpoint(self):
        values = np.arange(45)*.02
        clean = sensitivity_checks(series(values), 1981, 2025)
        values[-1] += 20
        dirty = sensitivity_checks(series(values), 1981, 2025)
        self.assertAlmostEqual(dirty["theil_sen_slope_per_decade"], .2)
        self.assertGreater(abs(dirty["intervals"][0]["slope_per_decade"]-.2), .4)
        self.assertAlmostEqual(clean["theil_sen_slope_per_decade"], .2)

    def test_fixed_date_checks_can_expose_direction_reversal(self):
        values = -np.arange(45, dtype=float)
        values[:5] -= 300
        result = sensitivity_checks(series(values), 1981, 2025)
        self.assertTrue(result["period_direction_changes"])
        self.assertEqual(result["periods"][1]["first_year"], 1986)
        self.assertEqual(result["periods"][1]["last_year"], 2025)

    def test_constant_values_remain_finite_and_unclear(self):
        result = sensitivity_checks(series(np.full(45, 10)), 1981, 2025)
        self.assertTrue(all(r["evidence"] == "unclear" for r in result["intervals"]))
        json.dumps(result, allow_nan=False)

    def test_unsorted_or_nonfinite_data_rejected(self):
        for rows in [list(reversed(series(range(20)))), series([float("nan")]*20)]:
            with self.assertRaises(ValueError):
                sensitivity_checks(rows, 1981, 2000)


class ReplayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saved = json.loads((ROOT/"data/tehran-nasa-snapshot.json").read_text())
        with patch("climate.fetch_data", return_value=(saved, "frozen test snapshot")):
            cls.record = investigate({})

    def test_full_replay_uses_frozen_source_without_fetch(self):
        with patch("climate.fetch_data", side_effect=AssertionError("Replay must not fetch")):
            self.assertEqual(verify(self.record), 45)

    def test_worksheet_replays_nested_evidence_without_endorsing_notes(self):
        worksheet = {"format": "Climate Explorer investigation 1", "analysis": self.record,
                     "notes": {"interpretation": "Unverified user text"}}
        with patch("climate.fetch_data", side_effect=AssertionError("Replay must not fetch")):
            self.assertEqual(verify(worksheet), 45)
        altered = copy.deepcopy(worksheet)
        altered["analysis"]["trend"]["slope_per_decade"] += .1
        with self.assertRaisesRegex(ValueError, "Different numeric result"):
            verify(altered)

    @unittest.skipUnless(shutil.which("node"), "Node is needed for the browser JSON regression test")
    def test_replay_survives_actual_javascript_json_round_trip(self):
        javascript = "const fs=require('fs');process.stdout.write(JSON.stringify(JSON.parse(fs.readFileSync(0,'utf8'))));"
        result = subprocess.run(["node", "-e", javascript], input=json.dumps(self.record), text=True, capture_output=True, check=True)
        browser_record = json.loads(result.stdout)
        self.assertEqual(verify(browser_record), 45)

    def test_edited_raw_source_is_detected(self):
        altered = copy.deepcopy(self.record)
        altered["raw_source"]["properties"]["parameter"]["T2M"]["198101"] += 1
        with self.assertRaisesRegex(ValueError, "hash"):
            verify(altered)

    def test_edited_analysis_is_detected(self):
        altered = copy.deepcopy(self.record)
        altered["checks"]["theil_sen_slope_per_decade"] += .1
        with self.assertRaisesRegex(ValueError, "Different numeric result"):
            verify(altered)

    def test_iid_reference_agrees_with_original_calculation(self):
        a = analyze(self.record["annual"])
        b = self.record["checks"]["intervals"][0]
        self.assertAlmostEqual(a["slope_per_decade"], b["slope_per_decade"])
        np.testing.assert_allclose(a["ci95_per_decade"], b["ci95_per_decade"], atol=1e-10)

    def test_edited_method_settings_are_detected(self):
        altered = copy.deepcopy(self.record)
        altered["analysis"]["settings"]["hac_fixed_lags"] = [2, 10]
        with self.assertRaisesRegex(ValueError, "analysis.settings"):
            verify(altered)
