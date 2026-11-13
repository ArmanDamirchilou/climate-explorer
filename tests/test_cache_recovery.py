import hashlib
import io
import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from climate import DataUnavailable, PRESETS, ROOT, fetch_data, source_url


class CacheRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.saved = json.loads((ROOT / 'evaluation/source-snapshots/berlin-power.json').read_text())
        cls.lat, cls.lon = PRESETS['berlin']['latitude'], PRESETS['berlin']['longitude']
        cls.url = source_url(cls.lat, cls.lon)

    def cache(self, root, contents):
        path = root / 'data/cache' / (hashlib.sha256(self.url.encode()).hexdigest()[:20] + '.json')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(contents))
        return path

    def test_wrong_shape_or_identity_cache_is_refreshed_and_replaced(self):
        valid = {**self.saved, 'request_url': self.url, 'fetched_at': datetime.now(timezone.utc).isoformat()}
        variants = [[], None, {'fetched_at': None}, {**valid, 'fetched_at': None},
                    {**valid, 'fetched_at': '2026-11-13'}, {**valid, 'payload': []},
                    {**valid, 'request_url': self.url + '&latitude=0'},
                    {**valid, 'payload': {'properties': {'parameter': []}, 'parameters': {}}}]
        for malformed in variants:
            with self.subTest(malformed=malformed), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                path = self.cache(root, malformed)
                with patch('climate.ROOT', root), patch('climate.urlopen', return_value=io.BytesIO(json.dumps(self.saved['payload']).encode())) as network:
                    saved, delivery = fetch_data(self.lat, self.lon)
                network.assert_called_once()
                self.assertEqual(delivery, 'live NASA response')
                self.assertEqual(saved['request_url'], self.url)
                self.assertEqual(json.loads(path.read_text()), saved)

    def test_invalid_cache_does_not_become_offline_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.cache(root, {'fetched_at': None, 'payload': self.saved['payload']})
            with patch('climate.ROOT', root), patch('climate.urlopen', side_effect=URLError('offline')):
                with self.assertRaisesRegex(DataUnavailable, 'NASA data could not be loaded'):
                    fetch_data(self.lat, self.lon)

    def test_valid_old_cache_remains_available_with_honest_delivery_label(self):
        saved = {**self.saved, 'request_url': self.url, 'fetched_at': '2000-01-01T00:00:00+00:00'}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.cache(root, saved)
            with patch('climate.ROOT', root), patch('climate.urlopen', side_effect=URLError('offline')):
                result, delivery = fetch_data(self.lat, self.lon)
        self.assertEqual(result, saved)
        self.assertEqual(delivery, 'older cached NASA response (live service unavailable)')

    def test_unexpected_network_programming_error_is_not_hidden(self):
        with tempfile.TemporaryDirectory() as directory, patch('climate.ROOT', Path(directory)), patch('climate.urlopen', side_effect=RuntimeError('programming defect')):
            with self.assertRaisesRegex(RuntimeError, 'programming defect'):
                fetch_data(self.lat, self.lon)
