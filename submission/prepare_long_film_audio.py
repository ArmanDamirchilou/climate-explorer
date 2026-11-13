"""Apply declared full-sentence edits from one verified native correction take."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess

import numpy as np

from build_long_film import ROOT, normalized, recorded_path
from build_story_video import probe, sha


RATE = 48000
CHANNELS = 2
REPLACEMENTS = [
    {"chapter": 2, "target": [7.50, 10.48], "old": "Temperature needs a day-weighted annual mean.", "text": "Temperature uses a weighted yearly average."},
    {"chapter": 2, "target": [15.85, 18.10], "old": "Incomplete years are excluded.", "text": "Incomplete years are left out."},
    {"chapter": 3, "target": [4.55, 8.00], "old": "Newey-West intervals explore sensitivity to correlated errors.", "text": "Adjusted intervals examine correlated errors."},
    {"chapter": 3, "target": [8.00, 10.90], "old": "Theil-Sen reduces sensitivity to unusual years.", "text": "A robust slope checks unusual years."},
    {"chapter": 4, "target": [5.80, 11.20], "old": "The new window atlas examines every continuous period with at least ten complete years.", "text": "The map shows every eligible date window."},
]


def decoded(path):
    output = subprocess.check_output(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path), "-vn", "-f", "f32le", "-ac", str(CHANNELS), "-ar", str(RATE), "pipe:1"])
    return np.frombuffer(output, dtype="<f4").reshape(-1, CHANNELS).copy()


def donor_windows(record):
    words = [w for segment in record["segments"] for w in segment.get("words", [])]
    actual = " ".join(w["word"].strip() for w in words)
    expected = " ".join(row["text"] for row in REPLACEMENTS)
    if normalized(actual) != normalized(expected):
        raise ValueError(f"Correction take does not match the approved clauses.\nExpected: {expected}\nActual: {actual}")
    cursor, windows = 0, []
    for row in REPLACEMENTS:
        target, group = normalized(row["text"]), []
        while cursor < len(words) and normalized(" ".join(w["word"] for w in group)) != target:
            group.append(words[cursor])
            cursor += 1
            if not target.startswith(normalized(" ".join(w["word"] for w in group))):
                raise ValueError("Correction clause cannot be aligned exactly to its actual word timestamps")
        if not group or normalized(" ".join(w["word"] for w in group)) != target:
            raise ValueError("Incomplete correction clause")
        windows.append([max(0, group[0]["start"] - 0.025), group[-1]["end"] + 0.025])
    if cursor != len(words):
        raise ValueError("Unapproved words remain after correction clauses")
    return windows


def tempo(audio, factor):
    if abs(factor - 1) < 1e-7:
        return audio.copy()
    result = subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "f32le", "-ac", str(CHANNELS), "-ar", str(RATE), "-i", "pipe:0", "-af", f"atempo={factor:.9f}", "-f", "f32le", "pipe:1"], input=audio.astype("<f4").tobytes(), stdout=subprocess.PIPE, check=True)
    return np.frombuffer(result.stdout, dtype="<f4").reshape(-1, CHANNELS).copy()


def build(args):
    record = json.loads(args.transcript.read_text())
    windows = donor_windows(record)
    take_info = probe(args.take)
    take_duration = float(take_info["format"]["duration"])
    donor_audio = decoded(args.take)
    edits = []
    for row, donor in zip(REPLACEMENTS, windows):
        if donor[1] > take_duration + 0.03:
            raise ValueError("Correction timestamp extends past its source")
        available = row["target"][1] - row["target"][0] - 0.08
        factor = max(1.0, (donor[1] - donor[0]) / available)
        if factor > 1.4:
            raise ValueError(f"Sentence requires an excessive tempo change: {factor:.3f}")
        edits.append({**row, "donor_interval_seconds": donor, "tempo_factor": factor})
    draft = {"scope": "Whole-sentence native generated voice correction. No word cloning or replacement synthesis in post.", "take": recorded_path(args.take), "take_sha256": sha(args.take), "transcript": recorded_path(args.transcript), "transcript_sha256": sha(args.transcript), "take_automatic_transcript_agreement": True, "planned_edits": edits, "human_listening_performed": False, "applied": False}
    if not args.apply:
        print(json.dumps(draft, indent=2))
        return
    script = json.loads(args.script.read_text())
    for row in REPLACEMENTS:
        paragraph = script["script"][row["chapter"] - 1]
        if paragraph.count(row["old"]) != 1:
            raise ValueError("Approved original clause is missing or repeated; do not silently rewrite the script")
    args.temporary.mkdir(parents=True, exist_ok=True)
    chapters = []
    staged = []
    for chapter in sorted({row["chapter"] for row in edits}):
        current = args.sources / f"scene-{chapter}.mp4"
        raw = args.sources / f"scene-{chapter}-raw.mp4"
        if not raw.exists():
            shutil.copy2(current, raw)
        transcript = args.sources / f"scene-{chapter}-transcript.json"
        raw_transcript = args.sources / f"scene-{chapter}-raw-transcript.json"
        if transcript.exists() and not raw_transcript.exists():
            shutil.copy2(transcript, raw_transcript)
        data = decoded(raw)
        raw_info = probe(raw)
        raw_duration = float(raw_info["format"]["duration"])
        chapter_edits = []
        for edit in (row for row in edits if row["chapter"] == chapter):
            begin, end = [round(seconds * RATE) for seconds in edit["target"]]
            donor_begin, donor_end = [round(seconds * RATE) for seconds in edit["donor_interval_seconds"]]
            replacement = tempo(donor_audio[donor_begin:donor_end], edit["tempo_factor"])
            if len(replacement) > end - begin - round(0.04 * RATE):
                raise ValueError("Adjusted correction exceeds its declared sentence window")
            fade = min(round(0.005 * RATE), len(replacement) // 4)
            replacement[:fade] *= np.linspace(0, 1, fade)[:, None]
            replacement[-fade:] *= np.linspace(1, 0, fade)[:, None]
            data[begin:end] = 0
            placement = begin + (end - begin - len(replacement)) // 2
            data[placement:placement + len(replacement)] = replacement
            chapter_edits.append({**edit, "placement_seconds": placement / RATE, "placed_duration_seconds": len(replacement) / RATE, "edge_fade_seconds": 0.005, "unused_window": "Quiet edit space around the inserted complete sentence; timeline duration is preserved. Figures cover the mouth."})
        audio_path = args.temporary / f"scene-{chapter}-corrected.f32"
        audio_path.write_bytes(data.astype("<f4").tobytes())
        candidate = args.temporary / f"scene-{chapter}-corrected.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(raw), "-f", "f32le", "-ar", str(RATE), "-ac", str(CHANNELS), "-i", str(audio_path), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", str(raw_duration), "-movflags", "+faststart", "-metadata", "comment=AI-generated adult performance with documented whole-sentence native correction-take insertions. Original video timing retained; edited sentences covered by evidence graphics.", str(candidate)], check=True)
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(candidate), "-f", "null", "-"], check=True)
        chapters.append({"chapter": chapter, "raw_source": recorded_path(raw), "raw_source_sha256": sha(raw), "edited_source": recorded_path(current), "edited_source_sha256": sha(candidate), "edits": chapter_edits, "full_decode_passed": True, "derived_transcript_review": "Required after applying; no automatic transcript success is preclaimed."})
        staged.append((candidate, current))
    for candidate, current in staged:
        candidate.replace(current)
    for row in REPLACEMENTS:
        chapter = row["chapter"] - 1
        script["script"][chapter] = script["script"][chapter].replace(row["old"], row["text"])
    args.script.write_text(json.dumps(script, indent=2) + "\n")
    receipt = {**draft, "applied": True, "chapters": chapters, "script": recorded_path(args.script), "script_sha256": sha(args.script), "helper_sha256": sha(Path(__file__)), "created_utc": datetime.now(timezone.utc).isoformat(), "checks": {"correction_take_automatic_transcript_agreement": True, "all_derived_sources_full_decode": True, "derived_sources_transcript_agreement": False, "human_listening_performed": False}, "next_check": "Re-transcribe each derived chapter and compare against its revised canonical paragraph before final film rendering."}
    args.receipt.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps({"receipt": recorded_path(args.receipt), "chapters_edited": [x["chapter"] for x in chapters], "maximum_tempo": max(row["tempo_factor"] for row in edits)}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=ROOT / "tmp/long-film")
    parser.add_argument("--take", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--script", type=Path, default=ROOT / "submission/long-film-script.json")
    parser.add_argument("--receipt", type=Path, default=ROOT / "submission/long-film-sentence-edits.json")
    parser.add_argument("--temporary", type=Path, default=ROOT / "tmp/long-film/audio-edits")
    parser.add_argument("--apply", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
