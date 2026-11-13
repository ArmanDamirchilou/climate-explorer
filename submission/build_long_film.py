"""Compose supplied studio performances with deterministic evidence graphics."""

import argparse
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import re
import subprocess
import wave

import numpy as np
from PIL import Image, ImageDraw

from build_story_video import BOLD_PATHS, FONT_PATHS, INK, MUTED, ORANGE, PALE, ROOT, TEAL, Painter, ease, probe, sha


FPS = 30
SCENE_SECONDS = 27
WIDTH, HEIGHT = 1920, 1080
TITLES = ["Same record. Different dates.", "Follow the data", "Choose an explainable method", "Make every date choice visible", "Keep the evidence inspectable"]


def recorded_path(path):
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return path.name


def load_atlas(path, full):
    atlas = json.loads(path.read_text())
    if atlas.get("format") != "Climate Explorer window atlas 1":
        raise ValueError("Unsupported retained atlas format")
    base = atlas["base_analysis"]
    if base["provenance"]["payload_sha256"] != full["provenance"]["payload_sha256"]:
        raise ValueError("The film atlas must use the same retained rainfall source")
    first, last = base["period"]["start"], base["period"]["end"]
    minimum = atlas["specification"]["minimum_calendar_years"]
    expected = [(a, b) for a in range(first, last - minimum + 2) for b in range(a + minimum - 1, last + 1)]
    if [(r["start"], r["end"]) for r in atlas["windows"]] != expected:
        raise ValueError("Atlas omits or reorders the declared complete window universe")
    for row in atlas["windows"]:
        records = [r for r in base["annual"] if row["start"] <= r["year"] <= row["end"]]
        if row["complete_years"] != len(records):
            raise ValueError("Atlas complete-year count differs from its retained source")
        if row["available"]:
            mean_x = math.fsum(r["year"] for r in records) / len(records)
            mean_y = math.fsum(r["value"] for r in records) / len(records)
            slope = 10 * math.fsum((r["year"] - mean_x) * (r["value"] - mean_y) for r in records) / math.fsum((r["year"] - mean_x) ** 2 for r in records)
            if not math.isclose(slope, row["slope_per_decade"], rel_tol=1e-9, abs_tol=1e-8):
                raise ValueError("Atlas slope differs from the independent point calculation")
    return atlas


def normalized(value):
    value = value.lower()
    for words, digits in [(r"twenty[ -]thousand", "20000"), (r"forty[ -]five", "45"), (r"fifteen", "15"), (r"twelve", "12"), (r"ten", "10"), (r"two", "2"), (r"one", "1")]:
        value = re.sub(rf"\b(?:{words})\b", digits, value)
    return re.sub(r"[^a-z0-9]", "", value)


def caption_text(words):
    value = " ".join(w["word"].strip() for w in words)
    return re.sub(r"\s+([,.;:!?])", r"\1", value)


def captions_for(path, expected):
    record = json.loads(path.read_text())
    words = [w for segment in record["segments"] for w in segment.get("words", [])]
    if not words:
        raise ValueError(f"No word timestamps in {path}")
    actual = " ".join(w["word"].strip() for w in words)
    if normalized(actual) != normalized(expected):
        raise ValueError(f"Transcript does not match approved chapter: {path}\nExpected: {expected}\nActual: {actual}")
    if words[-1]["end"] > SCENE_SECONDS - 0.08:
        raise ValueError(f"Last approved word risks truncation in {path}")
    groups, pending = [], []
    for word in words:
        pending.append(word)
        text = caption_text(pending)
        boundary = bool(re.search(r"[.!?]$", word["word"].strip()))
        pause = bool(re.search(r"[,;:]$", word["word"].strip())) and len(pending) >= 6
        if boundary or pause or len(text) >= 70 or len(pending) >= 11:
            groups.append({"start": pending[0]["start"], "end": pending[-1]["end"] + 0.1, "text": text})
            pending = []
    if pending:
        groups.append({"start": pending[0]["start"], "end": pending[-1]["end"] + 0.1, "text": caption_text(pending)})
    index = 1
    while index < len(groups):
        if len(groups[index]["text"].split()) <= 2 and len(groups[index - 1]["text"]) + len(groups[index]["text"]) < 115:
            groups[index - 1]["text"] += " " + groups[index]["text"]
            groups[index - 1]["end"] = groups[index]["end"]
            groups.pop(index)
        else:
            index += 1
    for index, group in enumerate(groups):
        comfortable_end = group["start"] + len(group["text"]) / 17
        limit = groups[index + 1]["start"] - 0.02 if index + 1 < len(groups) else SCENE_SECONDS - 0.03
        group["end"] = min(max(group["end"], comfortable_end), limit)
    return groups, record


class Studio(Painter):
    def __init__(self, font, bold, captures, atlas=None, audio_masks=None):
        super().__init__(False, font, bold)
        self.captures = {key: Image.open(path).convert("RGBA") for key, path in captures.items() if path}
        self.atlas = atlas
        self.audio_masks = audio_masks or {}

    def footer_long(self):
        self.rect((0, 655, 1280, 720), INK)
        self.text("AI-generated adult presenter + voice", 28, 665, 17, "white", True)
        self.text("TECHNICAL PORTFOLIO FILM | Not the NASA submission demo", 28, 690, 15, "white")

    def heading(self, chapter, full=False):
        self.text(f"CLIMATE EXPLORER / {chapter + 1:02d}", 42, 30, 17, MUTED, True)
        self.text(TITLES[chapter], 42, 72, 38 if full else 33, INK, True, 1190 if full else 660)

    def subtitle(self, group):
        if not group:
            return
        self.rect((20, 553, 1260, 648), "#0d2429")
        self.text(group["text"], 42, 570, 30, "white", True, 1190)

    def source_label(self, text):
        self.text(text, 42, 516, 16, MUTED, False, 1175)

    def card(self, y, label, detail, color=TEAL):
        self.rect((42, y, 712, y + 90), "#e5eeec")
        self.rect((42, y, 49, y + 90), color)
        self.text(label, 65, y + 12, 27, color, True, 620)
        self.text(detail, 65, y + 51, 19, MUTED, False, 620)

    def capture(self, key, title, detail, t):
        self.rect((0, 0, 1280, 655), PALE)
        self.text(title, 42, 28, 32, INK, True)
        image = self.captures[key].copy()
        if key == "app":
            image = image.crop((round(image.width * 0.53), round(image.height * 0.14), round(image.width * 0.95), round(image.height * 0.41)))
        image.thumbnail((1794, 633), Image.Resampling.LANCZOS)
        x = (WIDTH - image.width) // 2
        self.image.alpha_composite(image, (x, 124))
        self.text(detail, 42, 515, 17, MUTED, False, 1180)

    def rain(self, t, full, recent):
        self.rect((0, 0, 1280, 655), PALE)
        recent_mode = t >= 14.14
        selected = recent if recent_mode else full
        self.heading(0, True)
        x, y, width, height = 85, 215, 845, 245
        self.text("NASA POWER / Tehran grid / annual rainfall", 42, 137, 22, MUTED)
        self.text("Annual rainfall, mm/year", 85, 181, 18, MUTED)
        self.text("2011–2025" if recent_mode else "1981–2025", 978, 186, 30, INK, True)
        self.text(f"{selected['trend']['slope_per_decade']:+.1f}", 973, 235, 66, ORANGE if recent_mode else TEAL, True)
        self.text("mm/year per decade", 982, 321, 20, MUTED)
        if recent_mode:
            self.rect((x + width * 30 / 44, y, x + width, y + height), "#e0eeeb")
        for value in [0, 200, 400, 600]:
            yy = y + height * (1 - value / 600)
            self.line([(x, yy), (x + width, yy)], "#cddcda")
            self.text(str(value), x - 45, yy - 10, 17, MUTED)
        points = [(x + width * (r["year"] - 1981) / 44, y + height * (1 - r["value"] / 600)) for r in full["annual"]]
        self.line(points, "#88a8aa", 2)
        fitted = [(x + width * (r["year"] - 1981) / 44, y + height * (1 - r["value"] / 600)) for r in selected["trend"]["line"]]
        count = max(2, math.ceil(ease((t - (14.14 if recent_mode else 6)) / 1.5) * len(fitted)))
        self.line(fitted[:count], ORANGE if recent_mode else TEAL, 5)
        for year in [1981, 2011, 2025]:
            self.text(str(year), x + width * (year - 1981) / 44 - 22, y + height + 12, 17, MUTED)
        if recent_mode:
            low, high = recent["trend"]["ci95_per_decade"]
            self.text(f"Recent ordinary 95% interval: {low:.1f} to {high:+.1f}. Includes zero.", 42, 495, 22, ORANGE, True)
        else:
            self.source_label("1981–2025 annual record. Same source and axes are retained for the recent period.")

    def failure(self, results):
        self.rect((0, 0, 1280, 655), PALE)
        self.heading(2, True)
        row = next(x for x in results["scenarios"] if x["scenario"] == "strong dependence null")
        self.text("SYNTHETIC FAILURE CASE / 45 years / true slope zero", 42, 140, 22, ORANGE, True)
        self.text(f"{results['replicates_per_scenario']:,} generated records in this scenario", 42, 179, 23, MUTED)
        for index, (key, label) in enumerate([("OLS iid", "Ordinary OLS"), ("OLS HAC auto", "Newey-West, auto lag")]):
            yy = 255 + index * 103
            rate = row["methods"][key]["excludes_zero"]
            self.text(label, 42, yy, 27, INK, True)
            self.rect((435, yy, 435 + rate * 1300, yy + 36), ORANGE if index == 0 else TEAL)
            self.text(f"{100 * rate:.1f}%", 1030, yy - 3, 36, INK, True)
        self.text("Intervals excluded zero even though the known trend was zero.", 42, 459, 28, INK, True)
        self.source_label("Synthetic experiment, seed 20261111. Not NASA observations. Neither interval is a universal fix.")

    def atlas_plate(self, t):
        self.rect((0, 0, 1280, 655), PALE)
        self.heading(3, True)
        self.text("RENDERED FROM RETAINED ATLAS DATA / NOT AN INTERFACE CAPTURE", 42, 135, 17, MUTED, True)
        rows = self.atlas["windows"]
        starts = sorted({r["start"] for r in rows})
        ends = sorted({r["end"] for r in rows})
        x, y, width, height = 128, 205, 700, 245
        dx, dy = width / len(starts), height / len(ends)
        bound = math.ceil(max(abs(r["slope_per_decade"]) for r in rows if r["available"]) / 50) * 50
        for row in rows:
            if not row["available"]:
                continue
            ratio = min(1, abs(row["slope_per_decade"]) / bound)
            rgb = (23, 127, 135) if row["slope_per_decade"] >= 0 else (199, 106, 53)
            color = tuple(round(245 + (channel - 245) * ratio) for channel in rgb)
            xx = x + starts.index(row["start"]) * dx
            yy = y + (len(ends) - 1 - ends.index(row["end"])) * dy
            self.rect((xx, yy, xx + dx - 0.5, yy + dy - 0.5), color)
        for year in [starts[0], starts[len(starts) // 2], starts[-1]]:
            self.text(str(year), x + starts.index(year) * dx - 18, y + height + 10, 17, MUTED)
        for year in [ends[0], ends[len(ends) // 2], ends[-1]]:
            self.text(str(year), x - 53, y + (len(ends) - 1 - ends.index(year)) * dy - 5, 17, MUTED)
        self.text("Start year", x + width / 2 - 40, y + height + 38, 18, MUTED, True)
        self.text("End year", 42, y - 30, 18, MUTED, True)
        recent = t >= 15
        selected = next(r for r in rows if r["start"] == (2011 if recent else 1981) and r["end"] == 2025)
        xx = x + starts.index(selected["start"]) * dx
        yy = y + (len(ends) - 1 - ends.index(selected["end"])) * dy
        for offset in [0, 1, 2]:
            self.line([(xx - offset, yy - offset), (xx + dx + offset, yy - offset), (xx + dx + offset, yy + dy + offset), (xx - offset, yy + dy + offset), (xx - offset, yy - offset)], INK, 1)
        self.text(f"{len(rows):,} requested windows", 885, 195, 27, INK, True, 345)
        self.text("Same source. Fixed scale.", 885, 242, 21, MUTED, False, 340)
        self.text(f"{selected['start']}–{selected['end']}", 885, 299, 32, INK, True)
        self.text(f"{selected['slope_per_decade']:+.1f}", 885, 344, 58, ORANGE if recent else TEAL, True)
        self.text("mm/year per decade", 890, 418, 20, MUTED)
        self.text(f"Fixed color: {-bound:g} to {bound:+g} mm/year per decade | ≥10 complete years", 128, 167, 17, MUTED)
        self.source_label("Overlapping estimates are not independent votes, probabilities or selection-adjusted significance.")

    def correction_plate(self, chapter, t):
        self.rect((0, 0, 1280, 655), PALE)
        self.heading(chapter, True)
        if chapter == 1:
            if t < 14:
                self.text("Temperature: a weighted yearly average", 42, 176, 39, TEAL, True)
                self.text("Sum each monthly mean × days in that month", 42, 263, 34, INK, True)
                self.line([(42, 322), (1190, 322)], MUTED, 2)
                self.text("Divide by the days in the complete calendar year", 42, 354, 32, INK, True)
                self.source_label("Calculation schematic. Calendar-day weights include leap years; no synthetic observations are plotted.")
            else:
                self.text("An incomplete calendar year is left out.", 42, 183, 43, ORANGE, True)
                self.text("No missing-month imputation.", 42, 283, 35, INK, True)
                self.text("Keep actual calendar-year spacing.", 42, 360, 35, TEAL, True)
                self.source_label("Implementation rule. This schematic does not assert that the retained Tehran record has missing months.")
        elif chapter == 2:
            labels = [("OLS baseline", "An understandable historical rate", INK), ("Newey-West", "Conditional uncertainty with a recorded lag", TEAL), ("Theil-Sen", "A slope check for unusual years", ORANGE)]
            for index, (label, text, color) in enumerate(labels):
                x = 42 + index * 407
                self.rect((x, 190, x + 378, 448), "#e1ece9")
                self.rect((x, 190, x + 378, 197), color)
                self.text(label, x + 20, 222, 33, color, True, 338)
                self.text(text, x + 20, 298, 27, INK, False, 338)
            self.source_label("Established methods. Sensitivity checks are not a universal correction for dependence or source bias.")
        elif chapter == 4:
            if t < 15:
                self.text("Strict offline Python replay", 42, 184, 48, TEAL, True)
                self.text("Retained source + settings → recalculated evidence", 42, 288, 35, INK, True, 1170)
                self.text("Browser import checks a smaller, declared subset.", 42, 388, 29, MUTED)
                self.source_label("Capability diagram, not a terminal recording. See evaluation/replay.py and the release verification record.")
            else:
                self.text("A prototype with honest open questions", 42, 186, 43, ORANGE, True)
                self.text("Real student and teacher tasks remain.", 42, 287, 34, INK, True)
                self.text("Matched station validation remains.", 42, 367, 34, TEAL, True)
                self.source_label("No invented participants, endorsements, measured learning improvement or station-validation success.")

    def frame(self, chapter, t, captions, full, recent, results):
        self.begin()
        self.rect((0, 0, 720, 655), (242, 246, 245, 255))
        if chapter != 0 or t >= 6:
            self.heading(chapter)
        if chapter == 0:
            if t < 6:
                self.text("TWO POSSIBLE HEADLINES / TEHRAN RAINFALL", 42, 46, 19, MUTED, True, 670)
                self.text("RAINFALL IS RISING.", 42, 192, 40, TEAL, True, 660)
                if t > 1.15:
                    self.text("RAINFALL IS FALLING.", 42, 260, 40, ORANGE, True, 660)
                self.text("One city. One NASA record.", 42, 365, 28, INK, True)
            elif t < 21.66:
                self.rain(t, full, recent)
            else:
                self.text("How do we make", 42, 191, 45, INK, True)
                self.text("selective choices", 42, 256, 45, TEAL, True)
                self.text("visible?", 42, 321, 57, TEAL, True)
            if t < 6 or t >= 21.66:
                self.text("Built from 11 Nov 2026 | Eligibility unresolved", 42, 492, 17, MUTED, True)
        elif chapter == 1:
            if 18 <= t < 25 and "app" in self.captures:
                self.capture("app", "Actual application / same-source comparison", "Real release 1.1 capture. Source is model-grid data, not a street weather station.", t)
            else:
                self.card(168, "Monthly rain rate × calendar days", "mm/day × days → approximate monthly total")
                self.card(275, "Twelve complete months → annual total", "Missing month? Exclude that calendar year.")
                self.card(382, "Temperature: a day-weighted mean", "Different quantity, different annual aggregation")
                self.source_label("Source response + retrieval date + raw hash are retained.")
        elif chapter == 2:
            if 10 <= t < 21:
                self.failure(results)
            else:
                self.card(165, "Ordinary regression", "A simple historical rate with explicit assumptions")
                self.card(273, "Newey-West uncertainty", "Sensitivity to dependence; no universal correction")
                self.card(381, "Theil-Sen slope", "Less sensitive to unusual years; not a dependence fix")
                self.source_label("20,000 synthetic records across ten scenarios. Historical exploration, not forecasting.")
        elif chapter == 3:
            if "atlas" in self.captures and 5 <= t < 24:
                self.capture("atlas", "Actual window atlas / start year × end year", "Every eligible contiguous window. Same retained source. Overlapping estimates are not independent votes.", t)
            elif self.atlas and 5 <= t < 24:
                self.atlas_plate(t)
            else:
                self.card(166, "Declare the full window universe", "Contiguous date windows; ≥10 complete annual observations")
                self.card(274, "Open a cell. Inspect its observations.", "Start year, end year, rate, source and assumptions")
                self.card(382, "Keep selection visible", "Overlap is dependence. Browsing does not correct significance.", ORANGE)
                self.source_label("Ten years is an exploration boundary, not a guarantee of sufficient climate evidence.")
        else:
            if "replay" in self.captures and 7 <= t < 18:
                self.capture("replay", "Actual saved investigation / offline replay", "Python recalculates the evidence. Browser import checks a smaller declared subset.", t)
            else:
                self.card(164, "Source + dates + settings + fingerprint", "Save enough evidence for another reader to inspect.")
                self.card(272, "Strict Python replay", "Recalculate the evidence without fetching new observations")
                self.card(380, "Prototype. Real validation still needed.", "User tasks and matched station checks remain.", ORANGE)
                self.source_label("armandamirchilou.github.io/climate-explorer/")
            if t > 22:
                self.rect((0, 0, 1280, 655), PALE)
                self.heading(4, True)
                self.text("Challenge. Understand. Reproduce.", 42, 200, 51, TEAL, True, 1185)
                self.text("armandamirchilou.github.io/climate-explorer/", 42, 307, 30, INK, True)
                self.text("Built from 11 Nov 2026 | Early-work and AI-ideation eligibility unresolved", 42, 407, 22, MUTED, False, 1160)
                self.text("Fictional adult narrator. Codex-assisted research and implementation.", 42, 457, 21, MUTED)
        if chapter in [1, 2, 4] and any(a <= t <= b for a, b in self.audio_masks.get(chapter + 1, [])):
            if not (chapter == 4 and t >= 22):
                self.correction_plate(chapter, t)
        self.subtitle(next((x for x in captions if x["start"] <= t < x["end"]), None))
        self.footer_long()
        return self.image


def music(path, duration):
    rate = 48000
    t = np.arange(round(duration * rate)) / rate
    sound = np.zeros_like(t)
    for frequency in [130.8128, 164.8138, 195.9977]:
        sound += np.sin(2 * np.pi * frequency * t) * 0.0025
    sound *= np.minimum(t / 2, 1) * np.minimum((duration - t) / 2, 1)
    for start in [4, 27, 54, 81, 108]:
        local = t - start
        select = (local >= 0) & (local < 0.13)
        sound[select] += np.sin(2 * np.pi * 720 * local[select]) * np.exp(-local[select] * 32) * 0.023
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes((sound * 32767).astype("<i2").tobytes())


def render_chapter(source, destination, painter, chapter, captions, full, recent, results):
    log_path = destination.with_suffix(".log")
    actor_shift = "300*min(t/1.8,1)" if chapter == 0 else "300"
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source), "-f", "rawvideo", "-pixel_format", "rgba", "-video_size", f"{WIDTH}x{HEIGHT}", "-framerate", str(FPS), "-i", "pipe:0",
               "-filter_complex", f"[0:v]setpts=PTS-STARTPTS,scale=1920:1080:flags=lanczos,fps=30[original];color=c=0xf2f6f5:s=1920x1080:r=30:d={SCENE_SECONDS}[base];[base][original]overlay=x='{actor_shift}':y=0:shortest=1[actor];[actor][1:v]overlay=0:0:shortest=1,format=yuv420p[v];[0:a]aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=8,aresample=48000[a]",
               "-map", "[v]", "-map", "[a]", "-t", str(SCENE_SECONDS), "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-maxrate", "2300k", "-bufsize", "4600k", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", str(destination)]
    with log_path.open("wb") as log:
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stderr=log)
        try:
            for index in range(SCENE_SECONDS * FPS):
                process.stdin.write(painter.frame(chapter, index / FPS, captions, full, recent, results).tobytes())
            process.stdin.close()
            status = process.wait()
        except BaseException:
            process.kill()
            process.wait()
            raise
    if status:
        raise RuntimeError(f"Chapter encode failed: {log_path.read_text()}")


def stamp(seconds):
    milliseconds = round(seconds * 1000)
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"


def join_native_audio(chapters, destination):
    samples_per_chapter = SCENE_SECONDS * 48000 * 2
    with destination.open("wb") as output:
        for chapter in chapters:
            pcm = subprocess.check_output(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(chapter), "-map", "0:a:0", "-t", str(SCENE_SECONDS), "-f", "f32le", "-ac", "2", "-ar", "48000", "pipe:1"])
            values = np.frombuffer(pcm, dtype="<f4")
            if len(values) < samples_per_chapter:
                values = np.pad(values, (0, samples_per_chapter - len(values)))
            output.write(values[:samples_per_chapter].astype("<f4").tobytes())


def mux_master(video, voice, music_path, destination, duration):
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video), "-f", "f32le", "-ac", "2", "-ar", "48000", "-i", str(voice), "-i", str(music_path), "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,volume=-3.2dB,aresample=48000[a]", "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-t", str(duration), "-movflags", "+faststart", "-metadata", "title=Climate Explorer technical portfolio film - not the NASA submission demo", "-metadata", "comment=AI-generated fictional adult presenter and native voice with documented full-clause omissions and native correction-take insertions. Original presenter sources are 480p, upscaled in a 1080p composition with deterministic evidence graphics. Work began 11 November 2026; eligibility unresolved. Original synthesized ambient tones. Continuous PCM master with conservative fixed gain.", str(destination)], check=True)


def build(args):
    args.temporary.mkdir(parents=True, exist_ok=True)
    script = json.loads(args.script.read_text())["script"]
    if len(script) != 5:
        raise ValueError("Exactly five approved chapters are required")
    data_paths = [ROOT / "submission/story-inputs/tehran-rainfall.json", ROOT / "submission/story-inputs/tehran-recent15-rainfall.json", ROOT / "evaluation/results.json"]
    full, recent, results = [json.loads(p.read_text()) for p in data_paths]
    if full["provenance"]["payload_sha256"] != recent["provenance"]["payload_sha256"]:
        raise ValueError("Rainfall scenes must retain the same raw source")
    captures = {"app": args.app_frame, "atlas": args.atlas_frame, "replay": args.replay_frame}
    font = args.font or next((Path(p) for p in FONT_PATHS if Path(p).exists()), None)
    bold = args.bold_font or next((Path(p) for p in BOLD_PATHS if Path(p).exists()), font)
    if not font:
        raise ValueError("Provide installed TrueType --font and --bold-font paths")
    atlas = load_atlas(args.atlas_data, full) if args.atlas_data else None
    if args.atlas_data:
        data_paths.append(args.atlas_data)
    edit_record = args.audio_edit_record or ROOT / "submission/long-film-word-edit.json"
    if edit_record.exists():
        data_paths.append(edit_record)
    sentence_record = args.sentence_edits or ROOT / "submission/long-film-sentence-edits.json"
    omissions_record = args.omissions_record or ROOT / "submission/long-film-scene5-omissions.json"
    expected_audio_hashes, audio_masks = {}, {}
    if sentence_record.exists():
        data_paths.append(sentence_record)
        for chapter in json.loads(sentence_record.read_text())["chapters"]:
            expected_audio_hashes[chapter["chapter"]] = chapter["edited_source_sha256"]
            audio_masks[chapter["chapter"]] = [[edit["target"][0] - 0.08, edit["target"][1] + 0.08] for edit in chapter["edits"]]
    if omissions_record.exists():
        data_paths.append(omissions_record)
        omissions = json.loads(omissions_record.read_text())
        expected_audio_hashes[5] = omissions["edited_source_sha256"]
        audio_masks[5] = [[edit["interval"][0] - 0.08, edit["interval"][1] + 0.08] for edit in omissions["edits"]]
    painter = Studio(str(font), str(bold), captures, atlas, audio_masks)
    if args.preview_only:
        for chapter in range(5):
            for time in [2, 13, 24]:
                painter.frame(chapter, time, [{"start": 0, "end": 27, "text": "Preview of the caption position. Final captions follow the actual spoken performance."}], full, recent, results).save(args.temporary / f"preview-{chapter + 1}-{time}.png")
        print(json.dumps({"preview_only": True, "directory": str(args.temporary)}))
        return
    if not args.atlas_frame and not args.atlas_data:
        raise ValueError("Final production requires an actual --atlas-frame or retained --atlas-data")
    chapters, source_records, all_captions = [], [], []
    for index in range(5):
        source = args.sources / f"scene-{index + 1}.mp4"
        transcript = args.sources / f"scene-{index + 1}-transcript.json"
        if index == 0 and edit_record.exists() and sha(source) != json.loads(edit_record.read_text())["edited_source_sha256"]:
            raise ValueError("Chapter1 does not match the documented edited-source hash")
        if index + 1 in expected_audio_hashes and sha(source) != expected_audio_hashes[index + 1]:
            raise ValueError("Chapter does not match its documented native-audio correction hash")
        metadata = probe(source)
        audio = next((s for s in metadata["streams"] if s["codec_type"] == "audio"), None)
        video = next(s for s in metadata["streams"] if s["codec_type"] == "video")
        if not audio or float(metadata["format"]["duration"]) < SCENE_SECONDS:
            raise ValueError(f"Chapter lacks native audio or complete duration: {source}")
        captions, record = captions_for(transcript, script[index])
        destination = args.temporary / f"chapter-{index + 1}.mp4"
        render_chapter(source, destination, painter, index, captions, full, recent, results)
        chapters.append(destination)
        all_captions.extend({**group, "start": group["start"] + index * SCENE_SECONDS, "end": group["end"] + index * SCENE_SECONDS} for group in captions)
        source_records.append({"chapter": index + 1, "source": recorded_path(source), "sha256": sha(source), "source_resolution": [video["width"], video["height"]], "duration_seconds": float(metadata["format"]["duration"]), "native_audio_preserved": True, "transcript": recorded_path(transcript), "transcript_sha256": sha(transcript), "automatic_transcript_matches_approved_script": True, "last_word_seconds": max(w["end"] for s in record["segments"] for w in s.get("words", []))})
    concat = args.temporary / "chapters.txt"
    concat.write_text("\n".join(f"file '{p.resolve()}'" for p in chapters) + "\n")
    raw = args.temporary / "assembled-native.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-map", "0:v:0", "-an", "-c:v", "copy", str(raw)], check=True)
    duration = SCENE_SECONDS * 5
    music_path = args.temporary / "original-ambience.wav"
    music(music_path, duration)
    continuous_voice = args.temporary / "continuous-native-voice.f32"
    join_native_audio(chapters, continuous_voice)
    staged = args.temporary / "final-staged.mp4"
    mux_master(raw, continuous_voice, music_path, staged, duration)
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(staged), "-f", "null", "-"], check=True)
    final_probe = probe(staged)
    if staged.stat().st_size >= 50_000_000:
        raise ValueError("Encoded film exceeds 50 MB; inspect bitrate before publishing")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    staged.replace(args.output)
    vtt = ["WEBVTT", "", "NOTE AI-generated fictional adult narrator and native voice. Technical portfolio film, not the NASA demo.", ""]
    for item in all_captions:
        vtt.extend([f"{stamp(item['start'])} --> {stamp(item['end'])}", item["text"], ""])
    args.output.with_suffix(".vtt").write_text("\n".join(vtt))
    poster = args.output.with_name(args.output.stem + "-poster.jpg")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "2.2", "-i", str(args.output), "-frames:v", "1", str(poster)], check=True)
    caption_flags = [{"start": c["start"], "characters_per_second": round(len(c["text"]) / max(0.01, c["end"] - c["start"]), 1), "text": c["text"]} for c in all_captions if len(c["text"]) / max(0.01, c["end"] - c["start"]) > 22]
    video = next(s for s in final_probe["streams"] if s["codec_type"] == "video")
    audio = next(s for s in final_probe["streams"] if s["codec_type"] == "audio")
    caption_speeds = [len(c["text"]) / max(0.01, c["end"] - c["start"]) for c in all_captions]
    manifest = {"mode": "technical", "file": args.output.name, "sha256": sha(args.output), "bytes": args.output.stat().st_size, "duration_seconds": float(final_probe["format"]["duration"]), "resolution": [WIDTH, HEIGHT], "fps": FPS, "video_codec": video["codec_name"], "audio_codec": audio["codec_name"], "native_audio_preserved": True, "native_audio_scope": "Native generated performances with documented full-clause omissions and separately generated native correction-take insertions; chapter loudness normalization and original quiet instrumental bed" if edit_record.exists() else "Native generated voice with chapter loudness normalization and original quiet instrumental bed", "audio_edit_record": {"file": recorded_path(edit_record), "sha256": sha(edit_record)} if edit_record.exists() else None, "audio_edit_records": [{"file": recorded_path(p), "sha256": sha(p)} for p in [edit_record, sentence_record, omissions_record] if p.exists()], "chapters": source_records, "script": recorded_path(args.script), "script_sha256": sha(args.script), "sources": {recorded_path(p): sha(p) for p in data_paths}, "captures": {key: {"file": recorded_path(p), "sha256": sha(p)} for key, p in captures.items() if p}, "atlas_visual": "Actual verified app capture" if args.atlas_frame else "Data-derived plate, explicitly labeled as not an interface capture", "builder_sha256": sha(Path(__file__)), "ffmpeg_version": subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0], "captions": {"file": args.output.with_suffix(".vtt").name, "sha256": sha(args.output.with_suffix(".vtt")), "maximum_characters_per_second": round(max(caption_speeds), 1), "median_characters_per_second": round(float(np.median(caption_speeds)), 1), "high_reading_speed_review_flags": caption_flags}, "poster": {"file": poster.name, "sha256": sha(poster)}, "source_resolution_disclosure": "480p generated presenter sources upscaled; deterministic graphics and composition are 1080p", "checks": {"full_decode_passed": True, "source_transcript_agreement": True, "encoded_visual_review": False, "human_listening_performed": False}, "review": "Candidate. Review encoded scenes, captions, native audio continuity, and actual figures before publication.", "generated_utc": datetime.now(timezone.utc).isoformat()}
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"file": str(args.output), "duration": manifest["duration_seconds"], "bytes": manifest["bytes"], "sha256": manifest["sha256"]}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sources", type=Path, default=ROOT / "tmp/long-film")
    parser.add_argument("--script", type=Path, default=ROOT / "submission/long-film-script.json")
    parser.add_argument("--output", type=Path, default=ROOT / "submission/climate-explorer-story-technical.mp4")
    parser.add_argument("--temporary", type=Path, default=ROOT / "tmp/long-film/render")
    parser.add_argument("--app-frame", type=Path)
    parser.add_argument("--atlas-frame", type=Path)
    parser.add_argument("--atlas-data", type=Path)
    parser.add_argument("--audio-edit-record", type=Path)
    parser.add_argument("--sentence-edits", type=Path)
    parser.add_argument("--omissions-record", type=Path)
    parser.add_argument("--replay-frame", type=Path)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--bold-font", type=Path)
    parser.add_argument("--preview-only", action="store_true")
    build(parser.parse_args())


if __name__ == "__main__":
    main()
