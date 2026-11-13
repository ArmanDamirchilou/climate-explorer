"""Build the public, network-free demonstration from frozen NASA responses."""

import argparse
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from climate import PRESETS, ROOT, analyze_saved, payload_hash
from evaluation.replay import verify
from window_analysis import FIXED_WINDOWS, analyze_window
from story_evidence import build_story_evidence
from window_atlas import build_window_atlas, validate_atlas


def write_json(path, value):
    path.write_text(json.dumps(value, allow_nan=False, separators=(",", ":")) + "\n")


def install_build(stage, output):
    """Keep the previous complete site if copying or the final rename fails."""
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{output.name}-install-", dir=output.parent) as temporary:
        temporary = Path(temporary)
        ready, previous = temporary / "ready", temporary / "previous"
        shutil.copytree(stage, ready)
        had_previous = output.exists()
        if had_previous:
            os.replace(output, previous)
        try:
            os.replace(ready, output)
        except BaseException:
            if had_previous:
                os.replace(previous, output)
            raise


def build(output):
    output = output.resolve()
    if output == ROOT or ROOT.is_relative_to(output):
        raise ValueError("Choose a build directory, not the source directory or its parent.")
    if output.exists() and not (output / ".climate-demo-build").is_file():
        raise ValueError("Output already exists without the Climate Explorer build marker.")
    with tempfile.TemporaryDirectory(prefix=".demo-build-", dir=ROOT) as temporary:
        stage = Path(temporary) / "site"
        shutil.copytree(ROOT / "static", stage)
        data = stage / "demo"
        data.mkdir()
        atlas_directory = stage / "atlas"
        atlas_directory.mkdir()
        for page in stage.glob("*.html"):
            text = page.read_text().replace("<head>", '<head>\n  <meta name="climate-mode" content="snapshot">', 1)
            page.write_text(text)
        write_json(data / "config.json", {"presets": PRESETS, "first_year": 1981, "last_year": 2025, "mode": "snapshot", "windows": FIXED_WINDOWS})
        comparison = json.loads((ROOT / "evaluation" / "dataset-check.json").read_text())
        for key, place in PRESETS.items():
            saved = json.loads((ROOT / "evaluation" / "source-snapshots" / f"{key}-power.json").read_text())
            url = urlsplit(saved["request_url"])
            request = parse_qs(url.query)
            if url.scheme != "https" or url.netloc != "power.larc.nasa.gov" or url.path != "/api/temporal/monthly/point":
                raise ValueError(f"Unexpected source endpoint for {key}.")
            expected = {"parameters": ["T2M,PRECTOTCORR"], "start": ["1981"], "end": ["2025"], "format": ["JSON"], "community": ["AG"]}
            if any(request.get(field) != values for field, values in expected.items()):
                raise ValueError(f"Unexpected source query for {key}.")
            if any(float(request[field][0]) != place[field] for field in ("latitude", "longitude")):
                raise ValueError(f"Frozen source coordinates differ for {key}.")
            reference = next(row for row in comparison["rows"] if row["name"] == place["name"])
            if payload_hash(saved["payload"]) != reference["power_payload_sha256"]:
                raise ValueError(f"Frozen source hash differs from the saved study for {key}.")
            for variable in ("temperature", "rainfall"):
                query = {**place, "start": "1981", "end": "2025", "variable": variable}
                result = analyze_saved(query, saved, "frozen NASA snapshot (public demonstration)")
                verify(result)
                write_json(data / f"{key}-{variable}.json", result)
                atlas = build_window_atlas(result)
                validate_atlas(atlas)
                write_json(atlas_directory / f"{key}-{variable}.json", atlas)
                for window in FIXED_WINDOWS[1:]:
                    period_result = analyze_window(place, saved, variable, window["id"])
                    verify(period_result)
                    write_json(data / f"{key}-{window["id"]}-{variable}.json", period_result)
        write_json(stage / "story-tehran.json", build_story_evidence())
        for source, target in (("results.json", "validation.json"), ("dataset-check.json", "dataset-check.json"), ("science-audit.json", "science-audit.json")):
            write_json(data / target, json.loads((ROOT / "evaluation" / source).read_text()))
        reviewed_media = {}
        for mode in ("judge", "reel", "technical"):
            record = json.loads((ROOT / f"submission/climate-explorer-story-{mode}.json").read_text())
            if record["mode"] != mode or (mode == "judge" and record["duration_seconds"] > 30):
                raise ValueError("Reviewed media has the wrong role or exceeds the demo limit.")
            if mode == "technical" and (not 120 <= record["duration_seconds"] <= 180 or not record["checks"]["encoded_visual_review"] or not record["checks"]["full_decode_passed"]):
                raise ValueError("The technical portfolio film is unfinished or outside the agreed duration.")
            expected = {f"climate-explorer-story-{mode}.mp4": record["sha256"],
                        f"climate-explorer-story-{mode}.vtt": record["captions"]["sha256"],
                        f"climate-explorer-story-{mode}-poster.jpg": record["poster"]["sha256"]}
            reviewed_media.update(expected)
            for name, digest in expected.items():
                if hashlib.sha256((ROOT / "submission" / name).read_bytes()).hexdigest() != digest:
                    raise ValueError(f"Media is unfinished or differs from its review record: {name}")
        shutil.copyfile(ROOT / "submission" / "climate-explorer-demo.pdf", stage / "climate-explorer-demo.pdf")
        shutil.copyfile(ROOT / "submission" / "demo.html", stage / "demo.html")
        media = {
            "climate-explorer-story-judge.mp4": "climate-explorer-demo.mp4",
            "climate-explorer-story-judge.vtt": "climate-explorer-demo.vtt",
            "climate-explorer-story-reel.mp4": "climate-explorer-reel.mp4",
            "climate-explorer-story-reel.vtt": "climate-explorer-reel.vtt",
            "climate-explorer-story-judge-poster.jpg": "story-judge-poster.jpg",
            "climate-explorer-story-reel-poster.jpg": "story-reel-poster.jpg",
            "climate-explorer-story-technical.mp4": "climate-explorer-technical.mp4",
            "climate-explorer-story-technical.vtt": "climate-explorer-technical.vtt",
            "climate-explorer-story-technical-poster.jpg": "story-technical-poster.jpg",
            "story-media.css": "story-media.css",
        }
        for source, target in media.items():
            shutil.copyfile(ROOT / "submission" / source, stage / target)
            if source in reviewed_media and hashlib.sha256((stage / target).read_bytes()).hexdigest() != reviewed_media[source]:
                raise ValueError(f"Media changed during the build: {source}")
        (stage / ".nojekyll").touch()
        (stage / ".climate-demo-build").write_text("Generated by build_demo.py from frozen NASA records.\n")
        manifest = {
            str(path.relative_to(stage)): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(stage.rglob("*")) if path.is_file() and not path.name.startswith(".")
        }
        write_json(stage / "build-manifest.json", manifest)
        install_build(stage, output)
    return len(manifest)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    print(f"Built {build(args.output)} public files. Forty analyses replayed without network access.")
