import hashlib
import copy
import json
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
from urllib.parse import urljoin, urlsplit

from build_demo import build
from climate import PRESETS, ROOT, analyze_saved, investigate, payload_hash
from evaluation.replay import verify


class LocalReferences(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.reports = []

    def handle_starttag(self, tag, attributes):
        attributes = dict(attributes)
        if "data-report" in attributes:
            self.reports.append(attributes["data-report"])
            return
        for key, value in attributes.items():
            if key in {"src", "href"} and value:
                self.references.append(value)


class DemoBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="climate-demo-test-")
        cls.output = Path(cls.temporary.name) / "site"
        with patch("socket.socket.connect", side_effect=AssertionError("Build must not use the network")):
            with patch("climate.fetch_data", side_effect=AssertionError("Build must use frozen records")):
                cls.file_count = build(cls.output)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def test_ten_frozen_analyses_replay_without_network(self):
        records = sorted((self.output / "demo").glob("*-temperature.json"))
        records += sorted((self.output / "demo").glob("*-rainfall.json"))
        self.assertEqual(len(records), 10)
        with patch("socket.socket.connect", side_effect=AssertionError("Replay must not use the network")):
            for path in records:
                with self.subTest(path=path.name):
                    record = json.loads(path.read_text())
                    self.assertEqual(verify(record), 45)
                    self.assertEqual(record["period"], {"start": 1981, "end": 2025})
                    self.assertIn("frozen NASA snapshot", record["provenance"]["delivery"])

    def test_source_fixtures_match_previously_recorded_hashes(self):
        rows = json.loads((ROOT / "evaluation/dataset-check.json").read_text())["rows"]
        expected = {row["power_source_url"]: row["power_payload_sha256"] for row in rows}
        self.assertEqual(len(expected), 5)
        for key in PRESETS:
            with self.subTest(location=key):
                saved = json.loads((ROOT / "evaluation/source-snapshots" / f"{key}-power.json").read_text())
                self.assertEqual(payload_hash(saved["payload"]), expected[saved["request_url"]])

    def test_live_wrapper_matches_explicit_frozen_analysis(self):
        saved = json.loads((ROOT / "evaluation/source-snapshots/tehran-power.json").read_text())
        query = {"start": "1990", "end": "2025", "variable": "rainfall"}
        expected = analyze_saved(query, saved, "controlled test source")
        with patch("climate.fetch_data", return_value=(saved, "controlled test source")) as fetch:
            actual = investigate(query)
        fetch.assert_called_once_with(35.6892, 51.389)
        self.assertEqual(actual, expected)
        self.assertEqual(verify(actual), 36)

    def test_edited_source_hash_endpoint_or_period_stops_build(self):
        source = ROOT / "evaluation/source-snapshots/tehran-power.json"
        saved = json.loads(source.read_text())
        original_read = Path.read_text
        variants = []
        edited = copy.deepcopy(saved)
        edited["payload"]["properties"]["parameter"]["T2M"]["198101"] += 1
        variants.append((edited, "hash differs"))
        for old, new, error in [
            ("https://power.larc.nasa.gov", "http://power.larc.nasa.gov", "source endpoint"),
            ("power.larc.nasa.gov", "example.test", "source endpoint"),
            ("end=2025", "end=2024", "source query"),
        ]:
            edited = copy.deepcopy(saved)
            edited["request_url"] = saved["request_url"].replace(old, new)
            variants.append((edited, error))
        for i, (edited, error) in enumerate(variants):
            def read(path, *args, **kwargs):
                return json.dumps(edited) if path == source else original_read(path, *args, **kwargs)
            output = Path(self.temporary.name) / f"invalid-source-{i}"
            with self.subTest(error=error), patch.object(Path, "read_text", read):
                with self.assertRaisesRegex(ValueError, error):
                    build(output)
            self.assertFalse(output.exists())

    def test_public_files_do_not_contain_local_user_paths_or_private_keys(self):
        for path in self.output.rglob("*"):
            if not path.is_file():
                continue
            try:
                contents = path.read_text()
            except UnicodeDecodeError:
                continue
            with self.subTest(file=path.relative_to(self.output)):
                self.assertNotIn("/Users/", contents)
                self.assertNotIn("-----BEGIN PRIVATE KEY", contents)
                self.assertNotIn("github_pat_", contents)

    def test_manifest_covers_every_published_file(self):
        manifest = json.loads((self.output / "build-manifest.json").read_text())
        files = {
            str(path.relative_to(self.output)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in self.output.rglob("*")
            if path.is_file() and path.name != "build-manifest.json"
        }
        self.assertEqual(manifest, files)
        self.assertEqual(self.file_count, len(files))

    def test_snapshot_mode_is_explicit_on_both_pages(self):
        for name in ["index.html", "validation.html"]:
            with self.subTest(page=name):
                self.assertIn('name="climate-mode" content="snapshot"', (self.output / name).read_text())
        config = json.loads((self.output / "demo/config.json").read_text())
        self.assertEqual(config["mode"], "snapshot")
        self.assertEqual(config["last_year"], 2025)
        self.assertTrue((self.output / ".nojekyll").is_file())

    def test_page_references_work_under_repository_subpath(self):
        for page in ["index.html", "validation.html"]:
            parser = LocalReferences()
            parser.feed((self.output / page).read_text())
            for reference in parser.references:
                if reference.startswith("#"):
                    continue
                address = urlsplit(urljoin(f"https://example.test/climate-explorer/{page}", reference))
                if address.netloc != "example.test":
                    continue
                with self.subTest(page=page, reference=reference):
                    self.assertTrue(address.path.startswith("/climate-explorer/"), reference)
                    relative = address.path.removeprefix("/climate-explorer/") or "index.html"
                    self.assertTrue((self.output / relative).is_file(), reference)

    @unittest.skipUnless(shutil.which("node"), "Node is needed for the report-link mode regression test")
    def test_actual_validation_script_rewrites_report_links_for_each_mode(self):
        parser = LocalReferences()
        parser.feed((self.output / "validation.html").read_text())
        self.assertEqual(set(parser.reports), {"validation", "dataset-check", "science-audit"})
        javascript = """
const fs = require('fs');
const vm = require('vm');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const links = input.reports.map(report => ({dataset: {report}}));
const document = {
  querySelector: () => ({content: input.mode}),
  querySelectorAll: () => links,
  getElementById: () => ({})
};
vm.runInNewContext(input.source, {document, fetch: () => new Promise(() => {})});
process.stdout.write(JSON.stringify(links.map(link => link.href)));
"""
        source = (self.output / "validation.js").read_text()
        for mode in ["snapshot", "local"]:
            result = subprocess.run(
                ["node", "-e", javascript],
                input=json.dumps({"source": source, "reports": parser.reports, "mode": mode}),
                text=True, capture_output=True, check=True,
            )
            links = json.loads(result.stdout)
            for report, link in zip(parser.reports, links):
                with self.subTest(mode=mode, report=report):
                    if mode == "snapshot":
                        self.assertEqual(link, f"demo/{report}.json")
                        self.assertTrue((self.output / link).is_file())
                    else:
                        self.assertEqual(link, f"api/{report}")

    def test_source_directory_and_ancestors_are_never_outputs(self):
        for output in [ROOT, ROOT.parent, ROOT.parent.parent]:
            with self.subTest(output=output), self.assertRaisesRegex(ValueError, "source directory"):
                build(output)

    def test_unmarked_output_is_preserved(self):
        output = Path(self.temporary.name) / "unrelated"
        output.mkdir()
        sentinel = output / "keep.txt"
        sentinel.write_text("keep this file")
        with self.assertRaisesRegex(ValueError, "build marker"):
            build(output)
        self.assertEqual(sentinel.read_text(), "keep this file")

    def test_failed_build_keeps_previous_site(self):
        before = (self.output / "build-manifest.json").read_bytes()
        with patch("build_demo.analyze_saved", side_effect=ValueError("bad source")):
            with self.assertRaisesRegex(ValueError, "bad source"):
                build(self.output)
        self.assertEqual((self.output / "build-manifest.json").read_bytes(), before)

    def test_coordinate_mismatch_stops_build(self):
        incorrect = {"tehran": {**PRESETS["tehran"], "latitude": 0}}
        output = Path(self.temporary.name) / "bad-coordinate"
        with patch("build_demo.PRESETS", incorrect):
            with self.assertRaisesRegex(ValueError, "coordinates differ"):
                build(output)
        self.assertFalse(output.exists())


if __name__ == "__main__":
    unittest.main()
