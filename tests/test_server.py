import csv
import io
import json
import threading
import unittest
from functools import partial
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

from climate import DataUnavailable, ROOT
from server import Handler


class QuietHandler(Handler):
    def log_message(self, format, *args):
        pass


class HTTPTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads((ROOT / "data/tehran-nasa-snapshot.json").read_text())
        cls.server = ThreadingHTTPServer(
            ("127.0.0.1", 0), partial(QuietHandler, directory=str(ROOT / "static"))
        )
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=5)

    def request(self, path, method="GET"):
        connection = HTTPConnection(*self.server.server_address, timeout=5)
        try:
            connection.request(method, path)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read()
        finally:
            connection.close()

    def test_config_exposes_supported_locations_and_years(self):
        status, headers, body = self.request("/api/config")
        self.assertEqual(status, 200)
        result = json.loads(body)
        self.assertIn("tehran", result["presets"])
        self.assertEqual(result["first_year"], 1981)
        self.assertGreaterEqual(result["last_year"], 2025)
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_climate_response_contains_replay_evidence(self):
        with patch("climate.fetch_data", return_value=(self.saved, "frozen HTTP test")):
            status, headers, body = self.request("/api/climate?start=1981&end=2025")
        self.assertEqual(status, 200)
        result = json.loads(body)
        self.assertEqual(len(result["annual"]), 45)
        self.assertEqual(result["raw_source"], self.saved["payload"])
        self.assertEqual(result["provenance"]["delivery"], "frozen HTTP test")
        self.assertEqual(len(result["provenance"]["payload_sha256"]), 64)
        self.assertEqual(int(headers["Content-Length"]), len(body))

    def test_csv_preserves_units_and_provenance(self):
        with patch("climate.fetch_data", return_value=(self.saved, "frozen HTTP test")):
            status, headers, body = self.request("/api/download?variable=rainfall&start=2000&end=2009")
        self.assertEqual(status, 200)
        self.assertEqual(headers["Content-Type"], "text/csv; charset=utf-8")
        self.assertIn("attachment", headers["Content-Disposition"])
        rows = list(csv.DictReader(io.StringIO(body.decode())))
        self.assertEqual(len(rows), 10)
        self.assertEqual(rows[0]["unit"], "mm/year")
        self.assertEqual(rows[0]["parameter"], "PRECTOTCORR")
        self.assertEqual(rows[0]["source_url"], self.saved["request_url"])
        self.assertEqual(rows[0]["retrieved_utc"], self.saved["fetched_at"])

    def test_invalid_input_is_rejected_before_data_fetch(self):
        with patch("climate.fetch_data") as fetch:
            for query in ["latitude=nan", "longitude=181", "variable=unknown", "start=2020&end=2025"]:
                with self.subTest(query=query):
                    status, _, body = self.request("/api/climate?" + query)
                    self.assertEqual(status, 400)
                    self.assertIn("error", json.loads(body))
            fetch.assert_not_called()

    def test_upstream_failure_has_actionable_error(self):
        with patch("server.investigate", side_effect=DataUnavailable("NASA data unavailable")):
            status, _, body = self.request("/api/climate")
        self.assertEqual(status, 502)
        self.assertEqual(json.loads(body), {"error": "NASA data unavailable"})

    def test_unexpected_exception_does_not_expose_details(self):
        with patch("server.investigate", side_effect=RuntimeError("private diagnostic")):
            with self.assertLogs(level="ERROR"):
                status, _, body = self.request("/api/climate")
        self.assertEqual(status, 500)
        self.assertIn("try again", json.loads(body)["error"])
        self.assertNotIn(b"private diagnostic", body)

    def test_unknown_api_returns_json_404(self):
        status, headers, body = self.request("/api/not-a-route")
        self.assertEqual(status, 404)
        self.assertTrue(headers["Content-Type"].startswith("application/json"))
        self.assertEqual(json.loads(body), {"error": "Unknown endpoint."})

    def test_saved_evidence_endpoints_serve_valid_json(self):
        for path in ["/api/validation", "/api/dataset-check", "/api/science-audit"]:
            with self.subTest(path=path):
                status, _, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertIsInstance(json.loads(body), dict)

    def test_missing_saved_report_returns_json_404(self):
        with patch.object(Path, "read_text", side_effect=FileNotFoundError("missing report")):
            status, headers, body = self.request("/api/validation")
        self.assertEqual(status, 404)
        self.assertTrue(headers["Content-Type"].startswith("application/json"))
        self.assertIn("not available", json.loads(body)["error"])

    def test_corrupt_or_nonfinite_saved_reports_return_recovery_message(self):
        for path in ["/api/validation", "/api/dataset-check", "/api/science-audit"]:
            for contents in ["{", '{"metric": NaN}']:
                with self.subTest(path=path, contents=contents):
                    with patch.object(Path, "read_text", return_value=contents):
                        with self.assertLogs(level="ERROR"):
                            status, _, body = self.request(path)
                    self.assertEqual(status, 500)
                    self.assertIn("Restore it from the repository", json.loads(body)["error"])

    def test_unreadable_saved_report_does_not_expose_filesystem_details(self):
        with patch.object(Path, "read_text", side_effect=PermissionError("private filesystem detail")):
            with self.assertLogs(level="ERROR"):
                status, _, body = self.request("/api/science-audit")
        self.assertEqual(status, 500)
        self.assertNotIn(b"private filesystem detail", body)

    def test_static_root_has_security_headers(self):
        status, headers, body = self.request("/")
        self.assertEqual(status, 200)
        self.assertIn(b"Climate Explorer", body)
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Referrer-Policy"], "no-referrer")
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertNotIn("unsafe-eval", headers["Content-Security-Policy"])

    def test_static_traversal_cannot_expose_python_or_snapshot(self):
        for path in ["/../climate.py", "/%2e%2e/climate.py", "/../data/tehran-nasa-snapshot.json"]:
            with self.subTest(path=path):
                status, _, _ = self.request(path)
                self.assertEqual(status, 404)

    def test_static_head_has_no_body(self):
        status, headers, body = self.request("/app.js", method="HEAD")
        self.assertEqual(status, 200)
        self.assertGreater(int(headers["Content-Length"]), 0)
        self.assertEqual(body, b"")


if __name__ == "__main__":
    unittest.main()
