"""Check the deployed frozen demonstration anonymously and replay its analyses."""

import argparse
import hashlib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from climate import CODE_SHA256, ROOT
from evaluation.replay import verify
from story_evidence import validate_story_evidence


def check(base_url):
    def fetch(relative):
        request = Request(base_url.rstrip("/") + "/" + relative, headers={"User-Agent": "ClimateExplorer-release-check/1.0.0"})
        try:
            with urlopen(request, timeout=30) as response:
                return response.read()
        except OSError as error:
            raise ValueError(f"Could not fetch public file: {relative}") from error

    manifest = json.loads(fetch("build-manifest.json"))
    for relative, digest in manifest.items():
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or ":" in relative or not relative or len(digest) != 64:
            raise ValueError("Invalid path or digest in the deployed manifest.")
    with ThreadPoolExecutor(max_workers=4) as pool:
        bodies = dict(zip(manifest, pool.map(fetch, manifest)))
    for relative, body in bodies.items():
        if hashlib.sha256(body).hexdigest() != manifest[relative]:
            raise ValueError(f"Deployed content does not match its manifest: {relative}")
    analyses = []
    for relative, body in bodies.items():
        if relative.startswith("demo/") and relative.endswith(("-temperature.json", "-rainfall.json")):
            record = json.loads(body)
            if record["analysis"]["code_sha256"] != CODE_SHA256:
                raise ValueError(f"Deployed code fingerprint differs from the local source: {relative}")
            analyses.append({"file": relative, "years_replayed": verify(record)})
    if len(analyses) != 40:
        raise ValueError("Expected forty deployed frozen analyses.")
    story = json.loads(bodies.get("story-tehran.json", b"{}"))
    story_count = validate_story_evidence(story)
    for record in story["analyses"].values():
        if record["analysis"]["code_sha256"] != CODE_SHA256:
            raise ValueError("Guided story fingerprint differs from the local source.")
    pdf = bodies.get("climate-explorer-demo.pdf", b"")
    if not pdf.startswith(b"%PDF-"):
        raise ValueError("The public demonstration PDF is missing or invalid.")
    expected_pdf = json.loads((ROOT / "submission/demo-verification.json").read_text())
    if hashlib.sha256(pdf).hexdigest() != expected_pdf["sha256"] or expected_pdf["pages"] > 7:
        raise ValueError("The public PDF differs from the reviewed artifact or exceeds the media limit.")
    video = bodies.get("climate-explorer-demo.mp4", b"")
    if len(video) < 16 or video[4:8] != b"ftyp":
        raise ValueError("The public demonstration MP4 is missing or invalid.")
    expected_video = json.loads((ROOT / "submission/video-verification.json").read_text())
    if hashlib.sha256(video).hexdigest() != expected_video["sha256"] or expected_video["duration_seconds"] > 30:
        raise ValueError("The public video differs from the reviewed artifact or exceeds the media limit.")
    if not bodies.get("climate-explorer-demo.vtt", b"").startswith(b"WEBVTT"):
        raise ValueError("The public English captions are missing or invalid.")
    return {"checked_utc": datetime.now(timezone.utc).isoformat(), "base_url": base_url,
            "authentication": "none", "files_verified_against_manifest": len(bodies),
            "code_sha256": CODE_SHA256, "analyses": analyses,
            "guided_story_analyses_replayed": story_count,
            "demo_pdf_sha256": hashlib.sha256(pdf).hexdigest(),
            "demo_video_sha256": hashlib.sha256(video).hexdigest(),
            "demo_video_seconds": expected_video["duration_seconds"],
            "scope": "Anonymous HTTP access, deployed file integrity and offline numerical replay; browser behavior and eligibility are separate checks."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://armandamirchilou.github.io/climate-explorer/")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("public-verification.json"))
    args = parser.parse_args()
    result = check(args.url)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Verified {result['files_verified_against_manifest']} public files and replayed forty analyses. No authentication used.")
