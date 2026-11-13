import functools
import hashlib
import json
import tempfile
import threading
import unittest
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from build_demo import build
from evaluation.verify_public import check


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass


class PublicVerificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory()
        cls.directory = Path(cls.temporary.name) / "demo"
        build(cls.directory)
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(QuietHandler, directory=str(cls.directory)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f"http://127.0.0.1:{cls.server.server_port}/"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        cls.temporary.cleanup()

    def test_anonymous_release_verification_replays_forty_records_and_checks_media(self):
        result = check(self.url)
        self.assertEqual(len(result["analyses"]), 40)
        self.assertEqual(sorted(set(row["years_replayed"] for row in result["analyses"])), [15, 25, 35, 45])
        self.assertEqual(result["demo_video_seconds"], 29.8)
        self.assertEqual(result["narrated_media"]["reel"]["duration_seconds"], 45)
        self.assertEqual(result["authentication"], "none")
        self.assertEqual(result["guided_story_analyses_replayed"], 2)
        self.assertEqual(result["demo_video_sha256"], hashlib.sha256((self.directory / "climate-explorer-demo.mp4").read_bytes()).hexdigest())

    def test_changed_video_is_rejected_even_with_an_updated_asset_manifest(self):
        video = self.directory / "climate-explorer-demo.mp4"
        manifest_path = self.directory / "build-manifest.json"
        original_video, original_manifest = video.read_bytes(), manifest_path.read_bytes()
        try:
            video.write_bytes(original_video + b"changed")
            manifest = json.loads(original_manifest)
            manifest[video.name] = hashlib.sha256(video.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "video differs"):
                check(self.url)
        finally:
            video.write_bytes(original_video)
            manifest_path.write_bytes(original_manifest)

    def test_changed_story_is_rejected_even_with_an_updated_asset_manifest(self):
        story_path = self.directory / "story-tehran.json"
        manifest_path = self.directory / "build-manifest.json"
        original_story, original_manifest = story_path.read_bytes(), manifest_path.read_bytes()
        try:
            story = json.loads(original_story)
            story["comparison"][-1]["slope_per_decade"] = 999
            story_path.write_text(json.dumps(story))
            manifest = json.loads(original_manifest)
            manifest[story_path.name] = hashlib.sha256(story_path.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "story.comparison"):
                check(self.url)
        finally:
            story_path.write_bytes(original_story)
            manifest_path.write_bytes(original_manifest)

    def test_changed_portfolio_media_is_rejected_despite_matching_manifest(self):
        video = self.directory / "climate-explorer-reel.mp4"
        manifest_path = self.directory / "build-manifest.json"
        original_video, original_manifest = video.read_bytes(), manifest_path.read_bytes()
        try:
            video.write_bytes(original_video + b"changed")
            manifest = json.loads(original_manifest)
            manifest[video.name] = hashlib.sha256(video.read_bytes()).hexdigest()
            manifest_path.write_text(json.dumps(manifest))
            with self.assertRaisesRegex(ValueError, "reel video differs"):
                check(self.url)
        finally:
            video.write_bytes(original_video)
            manifest_path.write_bytes(original_manifest)
