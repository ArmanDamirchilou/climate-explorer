"""Preserve scene five while omitting three explicitly rejected audio clauses."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

from build_long_film import ROOT, recorded_path
from build_story_video import probe, sha
from prepare_long_film_audio import CHANNELS, RATE, decoded


EDITS = [
    {"interval": [7.15, 9.85], "reason": "Omit the complete mispronounced offline-replay sentence. The accurate replay capability is shown visually."},
    {"interval": [19.20, 22.10], "reason": "Omit the complete mispronounced matched-station sentence. The actual remaining validation gaps are shown visually."},
    {"interval": [25.18, 27.072], "reason": "End the spoken goal after challenge; omit the entire following understand-and-reproduce clause, including the incorrect final word."},
]


def build(args):
    source = args.sources / "scene-5.mp4"
    raw = args.sources / "scene-5-raw.mp4"
    script = json.loads(args.script.read_text())
    paragraph = script["script"][4]
    changes = [("Offline replay recalculates the evidence. ", ""), ("Real user testing and matched station checks remain. ", ""), ("The goal is a climate claim that another person can challenge, understand, and reproduce.", "The goal is a climate claim that another person can challenge.")]
    for old, new in changes:
        if paragraph.count(old) != 1:
            raise ValueError("Original scene5 clause is missing or repeated; refuse an ambiguous script rewrite")
        paragraph = paragraph.replace(old, new)
    if not args.apply:
        print(json.dumps({"planned_omissions": EDITS, "new_canonical_paragraph": paragraph}, indent=2))
        return
    if not raw.exists():
        shutil.copy2(source, raw)
    transcript = args.sources / "scene-5-transcript.json"
    raw_transcript = args.sources / "scene-5-raw-transcript.json"
    if transcript.exists() and not raw_transcript.exists():
        shutil.copy2(transcript, raw_transcript)
    data = decoded(raw)
    duration = float(probe(raw)["format"]["duration"])
    for edit in EDITS:
        start, end = [min(len(data), round(t * RATE)) for t in edit["interval"]]
        fade = round(0.015 * RATE)
        if start >= fade:
            data[start - fade:start] *= np.linspace(1, 0, fade)[:, None]
        data[start:end] = 0
        if end + fade <= len(data):
            data[end:end + fade] *= np.linspace(0, 1, fade)[:, None]
    args.temporary.mkdir(parents=True, exist_ok=True)
    audio = args.temporary / "scene-5-omissions.f32"
    audio.write_bytes(data.astype("<f4").tobytes())
    candidate = args.temporary / "scene-5-omissions.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-f", "f32le", "-ar", str(RATE), "-ac", str(CHANNELS), "-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", str(duration), "-movflags", "+faststart", "-metadata", "comment=AI-generated adult narrator. Three complete audio clauses are deliberately omitted beneath accurate evidence graphics. Original video timing retained. No replacement speech.", str(candidate)], check=True)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(candidate), "-f", "null", "-"], check=True)
    receipt = {"chapter": 5, "scope": "Full-clause omissions, no replacement speech. Raw source and original transcript retained separately.", "raw_source": recorded_path(raw), "raw_source_sha256": sha(raw), "edited_source": recorded_path(source), "edited_source_sha256": sha(candidate), "raw_transcript": recorded_path(raw_transcript), "raw_transcript_sha256": sha(raw_transcript), "edits": EDITS, "edge_fade_seconds": 0.015, "duration_seconds": duration, "replacement": "Quiet graphic-reading pauses; final music is added by the separate compositor.", "canonical_paragraph": paragraph, "checks": {"full_decode_passed": True, "edited_transcript_agreement": False, "human_listening_performed": False}, "next_check": "Transcribe this derived source and compare with the revised canonical paragraph.", "helper_sha256": sha(Path(__file__)), "created_utc": datetime.now(timezone.utc).isoformat()}
    candidate.replace(source)
    script["script"][4] = paragraph
    args.script.write_text(json.dumps(script, indent=2) + "\n")
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": recorded_path(args.receipt), "edited_sha256": receipt["edited_source_sha256"]}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=ROOT / "tmp/long-film")
    parser.add_argument("--script", type=Path, default=ROOT / "submission/long-film-script.json")
    parser.add_argument("--receipt", type=Path, default=ROOT / "submission/long-film-scene5-omissions.json")
    parser.add_argument("--temporary", type=Path, default=ROOT / "tmp/long-film/audio-edits")
    parser.add_argument("--apply", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
