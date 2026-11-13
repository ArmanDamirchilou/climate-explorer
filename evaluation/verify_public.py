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
from climate import CODE_SHA256, PRESETS, ROOT
from evaluation.replay import verify
from story_evidence import validate_story_evidence
from window_atlas import validate_atlas
from window_analysis import FIXED_WINDOWS


def check(base_url):
    def fetch(relative):
        request = Request(base_url.rstrip("/") + "/" + relative, headers={
            "User-Agent": "ClimateExplorer-release-check/1.3.1",
            "X-Requested-With": "XMLHttpRequest", "Accept": "application/octet-stream",
        })
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
    expected_analyses = {
        f"demo/{key}{'' if window['id'] == 'full45' else '-' + window['id']}-{variable}.json":
            (place, {"start": window["start"], "end": window["end"]}, variable)
        for key, place in PRESETS.items() for variable in ("temperature", "rainfall") for window in FIXED_WINDOWS
    }
    actual_analyses = {name for name in bodies if name.startswith("demo/") and name.endswith(("-temperature.json", "-rainfall.json"))}
    if actual_analyses != set(expected_analyses):
        raise ValueError("Expected the exact forty preset and period analysis files.")
    for relative, body in bodies.items():
        if relative.startswith("demo/") and relative.endswith(("-temperature.json", "-rainfall.json")):
            record = json.loads(body)
            place, period, variable = expected_analyses[relative]
            if record["period"] != period or record["variable"] != variable or record["location"] != {field: place[field] for field in ("latitude", "longitude")}:
                raise ValueError(f"Deployed analysis does not match its preset path: {relative}")
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
    expected_video = json.loads((ROOT / "submission/climate-explorer-story-judge.json").read_text())
    if hashlib.sha256(video).hexdigest() != expected_video["sha256"] or expected_video["duration_seconds"] > 30 or expected_video["mode"] != "judge":
        raise ValueError("The public video differs from the reviewed artifact or exceeds the media limit.")
    if not bodies.get("climate-explorer-demo.vtt", b"").startswith(b"WEBVTT"):
        raise ValueError("The public English captions are missing or invalid.")
    media_records = {}
    for mode, public_name in (("judge", "demo"), ("reel", "reel"), ("technical", "technical")):
        record = json.loads((ROOT / f"submission/climate-explorer-story-{mode}.json").read_text())
        if record["mode"] != mode or record["video_codec"] != "h264" or record["audio_codec"] != "aac" or not record["native_audio_preserved"]:
            raise ValueError(f"The {mode} media review lacks the expected video and speech contract.")
        if mode == "technical" and (not 120 <= record["duration_seconds"] <= 180 or not record["checks"]["encoded_visual_review"] or not record["checks"]["full_decode_passed"]):
            raise ValueError("The technical film lacks its completed review or agreed duration.")
        body = bodies.get(f"climate-explorer-{public_name}.mp4", b"")
        if len(body) < 16 or body[4:8] != b"ftyp" or hashlib.sha256(body).hexdigest() != record["sha256"]:
            raise ValueError(f"The public {mode} video differs from the reviewed artifact.")
        captions = bodies.get(f"climate-explorer-{public_name}.vtt", b"")
        poster = bodies.get(f"story-{mode}-poster.jpg", b"")
        if not captions.startswith(b"WEBVTT") or hashlib.sha256(captions).hexdigest() != record["captions"]["sha256"]:
            raise ValueError(f"The public {mode} captions differ from the reviewed artifact.")
        if not poster.startswith(b"\xff\xd8") or hashlib.sha256(poster).hexdigest() != record["poster"]["sha256"]:
            raise ValueError(f"The public {mode} poster differs from the reviewed artifact.")
        media_records[mode] = {"sha256": record["sha256"], "duration_seconds": record["duration_seconds"],
                               "resolution": record["resolution"], "role": "short demo candidate" if mode == "judge" else "portfolio, exceeds demo limit"}
    expected_atlases = {f"atlas/{key}-{variable}.json" for key in ("tehran", "ankara", "berlin", "toronto", "milan") for variable in ("temperature", "rainfall")}
    actual_atlases = {name for name in bodies if name.startswith("atlas/")}
    if actual_atlases != expected_atlases:
        raise ValueError("Expected the ten complete frozen window atlases.")
    atlas_records = []
    for name in sorted(expected_atlases):
        atlas = json.loads(bodies[name])
        base = atlas["base_analysis"]
        if base != json.loads(bodies["demo/" + name.removeprefix("atlas/")]):
            raise ValueError("Atlas base differs from the corresponding public analysis.")
        if base["analysis"]["code_sha256"] != CODE_SHA256:
            raise ValueError("Atlas code fingerprint differs from the local source.")
        count = validate_atlas(atlas)
        if count != 666:
            raise ValueError("Expected all 666 complete windows per frozen case.")
    for name in sorted(expected_atlases):
        count = validate_atlas(json.loads(bodies[name]), full=True)
        atlas_records.append({"file": name, "windows_replayed": count})
    return {"checked_utc": datetime.now(timezone.utc).isoformat(), "base_url": base_url,
            "authentication": "none", "files_verified_against_manifest": len(bodies),
            "request_representation": "Anonymous XHR asset fetch; no cookies, authorization, script stripping or hash normalization. Navigation HTML may also contain the hosting provider's injected detection script; inspect browser navigation separately.",
            "code_sha256": CODE_SHA256, "analyses": analyses,
            "guided_story_analyses_replayed": story_count,
            "window_atlases": atlas_records,
            "atlas_windows_replayed": sum(row["windows_replayed"] for row in atlas_records),
            "demo_pdf_sha256": hashlib.sha256(pdf).hexdigest(),
            "demo_video_sha256": hashlib.sha256(video).hexdigest(),
            "demo_video_seconds": expected_video["duration_seconds"],
            "narrated_media": media_records,
            "scope": "Anonymous HTTP access, deployed file integrity and offline numerical replay; browser behavior and eligibility are separate checks."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="https://climate-explorer-evidence.techtrendmedia-ai.chatgpt.site/")
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("public-verification.json"))
    args = parser.parse_args()
    result = check(args.url)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(f"Verified {result['files_verified_against_manifest']} public files and replayed forty analyses. No authentication used.")
