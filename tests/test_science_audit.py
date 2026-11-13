import json
import unittest

from climate import ROOT
from evaluation.science_audit import power_diagnostics


class ExternalAnnualReferenceTests(unittest.TestCase):
    def test_all_toronto_years_agree_with_nasa_rounded_annual_values(self):
        saved = json.loads((ROOT/"evaluation/source-snapshots/toronto-power.json").read_text())
        result = power_diagnostics(saved, "external annual reference")
        self.assertEqual(len(result["annual"]), 45)
        self.assertLessEqual(result["max_abs_weighted_minus_nasa_annual_c"], .0051)
        self.assertLess(abs(result["weighted_slope_c_per_decade"] - result["nasa_annual_slope_c_per_decade"]), .001)


if __name__ == "__main__":
    unittest.main()
