import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from climate import PRESETS, ROOT, analyze_saved, payload_hash
from evaluation.replay import verify


class ReplayContextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        saved = json.loads((ROOT / 'data/tehran-nasa-snapshot.json').read_text())
        cls.record = analyze_saved({**PRESETS['tehran'], 'variable': 'rainfall', 'start': 1981, 'end': 2025}, saved)

    def test_context_and_nested_investigation_remain_replayable(self):
        self.assertEqual(verify(self.record), 45)
        record = copy.deepcopy(self.record)
        record['analysis']['code_sha256'] = '0' * 64
        record['analysis']['app_release'] = '0.2.1'
        self.assertEqual(verify({'format': 'Climate Explorer investigation 1', 'analysis': record, 'notes': {'question': 'Unverified user text'}}), 45)

    def test_displayed_identity_and_source_metadata_tampering_is_rejected(self):
        mutations = [
            ('metadata', 'unit', '°C'),
            ('metadata', 'name', 'Temperature'),
            ('location', 'latitude', PRESETS['toronto']['latitude']),
            ('location', 'longitude', True),
            ('provenance', 'request_url', 'https://example.com/api/temporal/monthly/point'),
            ('provenance', 'request_url', self.record['provenance']['request_url'] + '&latitude=0'),
            ('provenance', 'request_url', self.record['provenance']['request_url'].replace('start=1981', 'start=2020')),
            ('provenance', 'provider', 'Independent station'),
            ('provenance', 'payload_hash_format', 'SHA-1'),
            ('provenance', 'fetched_at', '2026-11-11'),
            ('provenance', 'sources', ['Independent station']),
            ('provenance', 'api_version', 'invented'),
            ('provenance', 'returned_coordinates', [0, 0, 0]),
            ('analysis', 'code_sha256', 'not-a-fingerprint'),
            ('period', 'start', True),
            ('period', 'start', 1981.5),
            ('period', 'end', 10**12),
            ('raw_source', 'header', []),
            ('raw_source', 'geometry', None),
        ]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key, value=value):
                record = copy.deepcopy(self.record)
                record[section][key] = value
                with self.assertRaises((ValueError, TypeError)):
                    verify(record)

    def test_cli_reports_wrong_source_unit_without_traceback(self):
        record = copy.deepcopy(self.record)
        record['raw_source']['parameters']['PRECTOTCORR']['units'] = 'mm/month'
        record['provenance']['payload_sha256'] = payload_hash(record['raw_source'])
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'wrong-unit.json'
            path.write_text(json.dumps(record))
            result = subprocess.run([sys.executable, str(ROOT / 'evaluation/replay.py'), str(path)], text=True, capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('Replay failed:', result.stderr)
        self.assertIn('unexpected unit', result.stderr)
        self.assertNotIn('Traceback', result.stderr)

    def test_nonobject_exports_fail_clearly(self):
        for record in [[], None, {'format': 'Climate Explorer investigation 1', 'analysis': []}]:
            with self.subTest(record=record), self.assertRaises(ValueError):
                verify(record)
