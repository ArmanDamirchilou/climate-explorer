"""Composite a supplied adult performance with reproducible climate figures."""

import argparse
import hashlib
import json
import math
import subprocess
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
INK = "#123b40"
TEAL = "#177f87"
ORANGE = "#c76a35"
MUTED = "#507075"
PALE = "#f2f6f5"
FONT_PATHS = ["/System/Library/Fonts/Supplemental/Arial.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
BOLD_PATHS = ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]


def probe(path):
    return json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)]))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ease(value):
    value = min(1, max(0, value))
    return 1 - (1 - value) ** 3


def load_captions(path, speed):
    transcript = json.loads(path.read_text())
    segments, omitted = [], []
    finished = False
    for item in transcript["segments"]:
        if finished:
            omitted.append(item)
            continue
        segments.append(item)
        if "check what changed" in item["text"].lower():
            finished = True
    if not finished:
        raise ValueError("The supplied transcript lacks the approved final sentence; review the source first")
    groups = []
    for item in segments:
        words = item.get("words", [])
        for offset in range(0, len(words), 6):
            group = words[offset:offset + 6]
            groups.append({"start": group[0]["start"] / speed, "end": group[-1]["end"] / speed + 0.16,
                           "words": [{**w, "start": w["start"] / speed, "end": w["end"] / speed} for w in group]})
    for group, following in zip(groups, groups[1:]):
        group["end"] = min(group["end"], following["start"])
    return groups, omitted, max(item["end"] for item in segments) / speed


class Painter:
    def __init__(self, portrait, font, bold):
        self.portrait = portrait
        self.w, self.h = (720, 1280) if portrait else (1280, 720)
        self.scale = 1.5
        self.font_path, self.bold_path = font, bold
        self.fonts = {}

    def begin(self, opaque=False):
        self.image = Image.new("RGBA", (int(self.w * self.scale), int(self.h * self.scale)), PALE if opaque else (0, 0, 0, 0))
        self.draw = ImageDraw.Draw(self.image)

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self.fonts:
            self.fonts[key] = ImageFont.truetype(self.bold_path if bold else self.font_path, int(size * self.scale))
        return self.fonts[key]

    def rect(self, box, fill):
        self.draw.rectangle(tuple(round(v * self.scale) for v in box), fill=fill)

    def line(self, points, fill, width=1):
        self.draw.line([(round(x * self.scale), round(y * self.scale)) for x, y in points], fill=fill, width=max(1, round(width * self.scale)))

    def text(self, value, x, y, size=28, fill=INK, bold=False, max_width=None):
        font = self.font(size, bold)
        lines = []
        for paragraph in str(value).split("\n"):
            row = ""
            for word in paragraph.split():
                candidate = f"{row} {word}".strip()
                if row and max_width and self.draw.textlength(candidate, font=font) > max_width * self.scale:
                    lines.append(row)
                    row = word
                else:
                    row = candidate
            lines.append(row)
        for index, row in enumerate(lines):
            self.draw.text((round(x * self.scale), round((y + index * size * 1.22) * self.scale)), row, font=font, fill=fill)

    def footer(self, reel):
        height = 76 if self.portrait else 58
        self.rect((0, self.h - height, self.w, self.h), INK)
        self.text("AI-generated adult presenter + voice", 26, self.h - height + 9, 19 if self.portrait else 17, "white", True)
        self.text("Built from 11 Nov 2026 | Eligibility unresolved", 26, self.h - height + 36, 19 if self.portrait else 15, "white")
        if reel:
            self.rect((0, 0, self.w, 45), INK)
            self.text("PORTFOLIO REEL | Not the NASA submission demo", 24, 10, 19, "white", True)

    def caption(self, group, t):
        if not group or t < 2.65:
            return
        size = 30 if self.portrait else 28
        y = self.h - (222 if self.portrait else 164)
        self.rect((28, y, self.w - 28, self.h - (86 if self.portrait else 66)), "#0c1f23")
        value = " ".join(w["word"].strip() for w in group["words"])
        self.text(value, 52, y + 18, size, "white", True, self.w - 104)

    def presenter_overlay(self, t, reel):
        self.begin()
        if not self.portrait:
            self.rect((0, 0, 850, self.h), PALE)
            x, y, width = 56, 150, 730
        else:
            x, y, width = 40, 735, 640
            self.rect((0, 690, self.w, 1080), (241, 246, 245, 244))
        if t < 3.1:
            self.text("TEHRAN / RAINFALL", x, y - 75, 21, MUTED, True)
            self.text("ONE CITY.", x, y, 76 if not self.portrait else 65, INK, True)
            if t > 0.82:
                self.text("TWO CLIMATE", x, y + 96 - 12 * (1 - ease((t - 0.82) / 0.45)), 61 if not self.portrait else 52, TEAL, True)
            if t > 1.65:
                self.text("STORIES?", x, y + 180 - 12 * (1 - ease((t - 1.65) / 0.4)), 78 if not self.portrait else 68, TEAL, True)
        elif t < 22.3:
            self.text("Same source.", x, y + 30, 64 if not self.portrait else 57, INK, True)
            self.text("Different dates.", x, y + 120, 64 if not self.portrait else 57, TEAL, True)
        elif t < 26:
            self.text("Save the evidence.", x, y + 20, 56 if not self.portrait else 49, INK, True, width)
            self.text("Source. Settings. Replay.", x, y + 150, 32, TEAL, True, width)
        else:
            self.text("Check what", x, y + 10, 70 if not self.portrait else 61, INK, True)
            self.text("changed.", x, y + 105, 80 if not self.portrait else 70, TEAL, True)
            self.text("Climate Explorer", x, y + 225, 28, INK, True)
        if not self.portrait:
            self.text("armandamirchilou.github.io/climate-explorer/", 56, 498, 22, MUTED)
        self.footer(reel)
        return self.image.copy()

    def chart(self, t, full, recent, reel):
        self.begin(True)
        margin_top = 55 if reel else 22
        self.text("NASA POWER / TEHRAN MODEL GRID", 46, margin_top + 14, 20, MUTED, True)
        recent_mode = t >= 8.65
        selected = recent if recent_mode else full
        self.text("2011–2025" if recent_mode else "1981–2025", 46, margin_top + 59, 52, INK, True)
        if self.portrait:
            x, y, width, height = 76, 370, 580, 350
            self.text(f"{selected['trend']['slope_per_decade']:+.1f}", 46, 195, 82, ORANGE if recent_mode else TEAL, True)
            self.text("mm/year per decade", 52, 293, 24, MUTED)
        else:
            x, y, width, height = 80, 175, 850, 270
            self.text(f"{selected['trend']['slope_per_decade']:+.1f}", 990, 195, 74, ORANGE if recent_mode else TEAL, True)
            self.text("mm/year", 1000, 292, 27, MUTED)
            self.text("per decade", 1000, 328, 27, MUTED)
        if recent_mode:
            x_recent = x + width * 30 / 44
            self.rect((x_recent, y, x + width, y + height), (221, 237, 236, 255))
        for value in [0, 200, 400, 600]:
            yy = y + height * (1 - value / 600)
            self.line([(x, yy), (x + width, yy)], "#d4e1df")
            self.text(str(value), x - 49, yy - 12, 18, MUTED)
        self.text("Annual rainfall, mm/year", x, y - 33, 18, MUTED)
        points = [(x + width * (row["year"] - 1981) / 44, y + height * (1 - row["value"] / 600)) for row in full["annual"]]
        self.line(points, "#9eb6b7", 2)
        progress = ease((t - 4.9) / 2.2)
        for px, py in points[:max(1, math.ceil(progress * len(points)))]:
            radius = 3 * self.scale
            self.draw.ellipse((px * self.scale - radius, py * self.scale - radius, px * self.scale + radius, py * self.scale + radius), fill=TEAL)
        records = selected["trend"]["line"]
        fit = [(x + width * (row["year"] - 1981) / 44, y + height * (1 - row["value"] / 600)) for row in records]
        fit_progress = ease((t - (8.65 if recent_mode else 5.3)) / 1.0)
        self.line(fit[:max(2, math.ceil(fit_progress * len(fit)))], ORANGE if recent_mode else TEAL, 5)
        for year in [1981, 2011, 2025]:
            self.text(str(year), x + width * (year - 1981) / 44 - 24, y + height + 13, 18, MUTED)
        if recent_mode:
            low, high = recent["trend"]["ci95_per_decade"]
            yy = 848 if self.portrait else 505
            left, bar_width = (90, 530) if self.portrait else (555, 610)
            self.text("Recent estimate uncertain", 46, yy - (82 if self.portrait else 21), 31 if self.portrait else 27, ORANGE, True)
            if not self.portrait:
                self.text("Ordinary 95% interval includes zero", 46, yy + 18, 20, MUTED)
            else:
                self.text("Ordinary 95% interval includes zero", 46, yy - 34, 22, MUTED)
            transform = lambda value: left + bar_width * (value + 200) / 300
            self.line([(transform(low), yy), (transform(high), yy)], ORANGE, 5)
            self.line([(transform(0), yy - 22), (transform(0), yy + 22)], MUTED, 2)
            px = transform(recent["trend"]["slope_per_decade"])
            self.rect((px - 5, yy - 7, px + 5, yy + 7), INK)
            self.text(f"{low:.1f}", transform(low) - 24, yy + 18, 17, MUTED)
            self.text("0", transform(0) - 5, yy + 25, 17, MUTED)
            self.text(f"{high:+.1f}", transform(high) - 17, yy + 18, 17, MUTED)
        if t >= 15.65:
            self.text("Climate Explorer", 46 if self.portrait else 990, 973 if self.portrait else 117, 29 if self.portrait else 27, TEAL, True)
        self.footer(reel)
        return self.image.copy()

    def extra(self, t, full, recent, app_frame):
        self.begin(True)
        self.text("THE INVESTIGATION", 42, 86, 24, MUTED, True)
        if t < 35:
            self.text("01 / Ask a question", 42, 155, 43, INK, True, self.w - 84)
            self.text("How much does the selected period change the fitted rainfall rate?", 42, 264, 33, TEAL, True, self.w - 84)
            if app_frame:
                source = Image.open(app_frame).convert("RGBA")
                source = source.crop((round(source.width * 0.53), round(source.height * 0.14), round(source.width * 0.95), round(source.height * 0.41)))
                source.thumbnail((int((self.w - 70) * self.scale), int(570 * self.scale)))
                self.image.alpha_composite(source, (int(35 * self.scale), int(470 * self.scale)))
                self.text("Actual app / guided investigation", 42, 850, 26, TEAL, True, self.w - 84)
                self.text("One frozen source. Two selected periods.", 42, 925, 28, MUTED, False, self.w - 84)
            else:
                self.text("1981–2025", 44, 490, 36, MUTED, True)
                self.text(f"{full['trend']['slope_per_decade']:+.1f}", 44, 550, 85, TEAL, True)
                self.text("2011–2025", 44, 705, 36, MUTED, True)
                self.text(f"{recent['trend']['slope_per_decade']:+.1f}", 44, 765, 85, ORANGE, True)
                self.text("mm/year per decade", 44, 902, 24, MUTED)
        elif t < 40:
            self.text("02 / Inspect uncertainty", 42, 155, 43, INK, True, self.w - 84)
            self.text("The recent point estimate is negative.", 42, 305, 37, ORANGE, True, self.w - 84)
            self.text("Its ordinary interval includes zero.", 42, 465, 37, TEAL, True, self.w - 84)
            self.text("That does not establish a significant decline or prove a reversal.", 42, 650, 32, MUTED, False, self.w - 84)
        else:
            self.text("03 / Save the evidence", 42, 155, 43, INK, True, self.w - 84)
            self.text("Raw NASA response\nSelected period\nAnalysis settings\nSource and code hashes", 42, 310, 33, TEAL, True, self.w - 84)
            self.text("Full Python replay recalculates the analysis. Browser checks have a narrower scope.", 42, 630, 30, MUTED, False, self.w - 84)
            self.text("armandamirchilou.github.io\n/climate-explorer/", 42, 865, 28, INK, True, self.w - 84)
        self.footer(True)
        return self.image.copy()

    def actual_app(self, t, app_frame, reel):
        self.begin(True)
        self.text("ACTUAL APP / GUIDED INVESTIGATION", 40, 75 if self.portrait else 26, 22, MUTED, True, self.w - 80)
        self.text("Keep the source. Change the dates.", 40, 140 if self.portrait else 70, 37 if self.portrait else 34, INK, True, self.w - 80)
        source = Image.open(app_frame).convert("RGBA")
        if self.portrait:
            source = source.crop((round(source.width * 0.53), round(source.height * 0.14), round(source.width * 0.95), round(source.height * 0.41)))
            source.thumbnail((int(650 * self.scale), int(650 * self.scale)))
            self.image.alpha_composite(source, (int(35 * self.scale), int(395 * self.scale)))
            self.text("A captured result from the working app", 42, 795, 28, TEAL, True, self.w - 84)
        else:
            box = (round(source.width * 0.045), round(source.height * 0.05), round(source.width * 0.96), round(source.height * 0.46))
            source = source.crop(box)
            target_width, target_height = int(1200 * self.scale), int(410 * self.scale)
            zoom = 1 + 0.025 * ease((t - 15.7) / 4)
            source = source.resize((round(target_width * zoom), round(target_height * zoom)), Image.Resampling.LANCZOS)
            dx, dy = (source.width - target_width) // 2, (source.height - target_height) // 2
            source = source.crop((dx, dy, dx + target_width, dy + target_height))
            self.image.alpha_composite(source, (int(40 * self.scale), int(130 * self.scale)))
        self.footer(reel)
        return self.image.copy()


def ambient(path, duration, reel):
    sample_rate = 48000
    t = np.arange(math.ceil(duration * sample_rate)) / sample_rate
    music = np.zeros_like(t)
    chords = [(261.6256, 329.6276, 391.9954), (220, 261.6256, 329.6276), (261.6256, 349.2282, 440)]
    phase = (t / 8) % 3
    for index, chord in enumerate(chords):
        distance = np.abs(phase - index)
        weight = np.clip(1 - np.minimum(distance, 3 - distance), 0, 1)
        for frequency in chord:
            music += weight * np.sin(2 * np.pi * frequency * t) * 0.004
    envelope = np.minimum(1, t / 1.2) * np.minimum(1, (duration - t) / 1.5)
    tail_rise = np.clip((t - 29.8) / 1.2, 0, 1)
    music *= envelope * (1 + 11 * tail_rise if reel else 1)
    for start in [4.9, 8.65, 15.65, 22.3] + ([30, 35, 40] if reel else []):
        local = t - start
        mask = (local >= 0) & (local < 0.12)
        music[mask] += 0.045 * np.sin(2 * np.pi * (850 * local[mask] + 1200 * local[mask] ** 2)) * np.exp(-local[mask] * 35)
    with wave.open(str(path), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes((np.clip(music, -1, 1) * 32767).astype("<i2").tobytes())


def build(args):
    full_path = ROOT / "submission/story-inputs/tehran-rainfall.json"
    recent_path = ROOT / "submission/story-inputs/tehran-recent15-rainfall.json"
    full, recent = json.loads(full_path.read_text()), json.loads(recent_path.read_text())
    assert full["provenance"]["payload_sha256"] == recent["provenance"]["payload_sha256"]
    assert full["trend"]["slope_per_decade"] > 0 > recent["trend"]["slope_per_decade"]
    assert recent["trend"]["ci95_per_decade"][0] < 0 < recent["trend"]["ci95_per_decade"][1]
    portrait = args.mode == "reel"
    duration, speed = (45, 1.0) if portrait else (29.8, 1.015)
    captions, omitted, last_spoken = load_captions(args.transcript, speed)
    if last_spoken > duration - 0.2:
        raise ValueError("Last approved word is too close to the cut; review timing instead of clipping speech")
    source_probe = probe(args.presenter)
    if not any(s["codec_type"] == "audio" for s in source_probe["streams"]):
        raise ValueError("The presenter source must contain its original native audio")
    font = args.font or next((Path(x) for x in FONT_PATHS if Path(x).exists()), None)
    bold = args.bold_font or next((Path(x) for x in BOLD_PATHS if Path(x).exists()), font)
    if not font:
        raise ValueError("Provide --font and --bold-font with installed TrueType fonts")
    painter = Painter(portrait, str(font), str(bold))
    directory = args.temporary / args.mode
    directory.mkdir(parents=True, exist_ok=True)
    frames = round(duration * 30)
    for index in range(frames):
        t = index / 30
        if portrait and t >= 30:
            image = painter.extra(t, full, recent, args.app_frame)
        else:
            image = painter.presenter_overlay(t, portrait)
            if args.app_frame and 15.7 <= t < 19.9:
                image = painter.actual_app(t, args.app_frame, portrait)
            else:
                alpha = min(ease((t - 4.9) / 0.22), ease((22.3 - t) / 0.24))
                if alpha > 0:
                    figure = painter.chart(t, full, recent, portrait)
                    if alpha < 1:
                        figure.putalpha(figure.getchannel("A").point(lambda v: round(v * alpha)))
                    image = Image.alpha_composite(image, figure)
            painter.image, painter.draw = image, ImageDraw.Draw(image)
            group = next((g for g in captions if g["start"] <= t <= g["end"]), None)
            painter.caption(group, t)
            image = painter.image
        image.save(directory / f"frame-{index:05d}.png", compress_level=1)
    accents = directory / "original-ambience.wav"
    ambient(accents, duration, portrait)
    width, height = int(painter.w * painter.scale), int(painter.h * painter.scale)
    actor_width = width if portrait else 645
    actor_x = 0 if portrait else width - actor_width
    actor = (f"[0:v]setpts=(PTS-STARTPTS)/{speed},scale={actor_width}:{height}:force_original_aspect_ratio=increase,"
             f"crop={actor_width}:{height}:(iw-ow)/2:(ih-oh)*0.18,pad={width}:{height}:{actor_x}:0:color=0xf2f6f5,"
             f"tpad=stop_mode=clone:stop_duration=16,fps=30,zoompan=z='1+0.022*min(on/160,1)':x='iw/2-iw/zoom/2':y='ih*0.4-ih/zoom*0.4':d=1:s={width}x{height}:fps=30[actor]")
    sound = f"[0:a]atempo={speed},aresample=48000,loudnorm=I=-16:TP=-1.5:LRA=8,apad=pad_dur=16[voice]"
    filters = f"{actor};[actor][1:v]overlay=0:0:shortest=1,format=yuv420p[video];{sound};[voice][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[audio]"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(args.presenter), "-framerate", "30", "-i", str(directory / "frame-%05d.png"),
               "-i", str(accents), "-filter_complex", filters, "-map", "[video]", "-map", "[audio]", "-t", str(duration),
               "-c:v", "libx264", "-crf", "19", "-preset", "fast", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
               "-metadata", "title=Climate Explorer story demonstration" if not portrait else "title=Climate Explorer portfolio reel - not NASA submission demo",
               "-metadata", "comment=AI-generated fictional adult presenter and native voice from Higgsfield Seedance 2.5. Charts use retained NASA POWER data. Work began 11 November 2026; eligibility unresolved. Original synthesized ambient tones and accents added in post.", str(args.output)]
    subprocess.run(command, check=True)
    output_probe = probe(args.output)
    video_stream = next(stream for stream in output_probe["streams"] if stream["codec_type"] == "video")
    audio_stream = next(stream for stream in output_probe["streams"] if stream["codec_type"] == "audio")
    def stamp(seconds):
        whole, millis = divmod(round(seconds * 1000), 1000)
        minutes, second = divmod(whole, 60)
        return f"00:{minutes:02d}:{second:02d}.{millis:03d}"
    vtt = ["WEBVTT", "", "NOTE AI-generated fictional adult narrator and voice. Data figures use retained NASA POWER records.", ""]
    for group in captions:
        vtt.extend([f"{stamp(group['start'])} --> {stamp(min(group['end'], duration))}", " ".join(w["word"].strip() for w in group["words"]), ""])
    if portrait:
        vtt.extend(["00:30.000 --> 00:45.000", "[Quiet original instrumental tones; the real investigation evidence is shown.]", ""])
    args.output.with_suffix(".vtt").write_text("\n".join(vtt))
    poster = args.output.with_name(args.output.stem + "-poster.jpg")
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-ss", "2.2", "-i", str(args.output), "-frames:v", "1", str(poster)], check=True)
    manifest = {"mode": args.mode, "file": args.output.name, "sha256": sha(args.output), "duration_seconds": float(output_probe["format"]["duration"]),
                "resolution": [width, height], "fps": 30, "native_audio_preserved": True, "whole_performance_speed": speed,
                "video_codec": video_stream["codec_name"], "pixel_format": video_stream["pix_fmt"], "frame_count": int(video_stream["nb_frames"]),
                "audio_codec": audio_stream["codec_name"], "audio_channels": audio_stream["channels"], "audio_sample_rate": int(audio_stream["sample_rate"]),
                "last_approved_word_seconds": last_spoken, "automatic_transcript_tail_omitted_from_captions": omitted,
                "sources": {str(p.relative_to(ROOT)): sha(p) for p in [full_path, recent_path]},
                "presenter_source_sha256": sha(args.presenter), "transcript_sha256": sha(args.transcript),
                "actual_app_capture": {"file": args.app_frame.name, "sha256": sha(args.app_frame), "scope": "Real release 1.1 guided story capture, framed in post without simulated clicks or altered data"} if args.app_frame else None,
                "captions": {"file": args.output.with_suffix(".vtt").name, "sha256": sha(args.output.with_suffix(".vtt"))},
                "poster": {"file": poster.name, "sha256": sha(poster)},
                "ai_disclosure": "Persistent visible generated-adult/voice label plus descriptive text and MP4 metadata",
                "scientific_scope": "Two fitted periods from the same NASA grid response. Recent ordinary interval includes zero. No claim of climate reversal.",
                "audio_processing": "Original native speech with synchronized tempo adjustment, loudness normalization, original synthesized ambience and accents.",
                "extra_audio": "Original deterministic synthesized ambient tones and short musical accents; not weather recordings.",
                "review": "Candidate only. Actual speech, captions, all cuts and figures require review before publication."}
    args.output.with_suffix(".json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"file": str(args.output), "duration": manifest["duration_seconds"], "resolution": manifest["resolution"]}))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--presenter", type=Path, required=True)
    parser.add_argument("--transcript", type=Path, required=True)
    parser.add_argument("--mode", choices=["judge", "reel"], default="judge")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--temporary", type=Path, default=ROOT / "tmp/story-production/render")
    parser.add_argument("--font", type=Path)
    parser.add_argument("--bold-font", type=Path)
    parser.add_argument("--app-frame", type=Path)
    args = parser.parse_args()
    args.presenter, args.transcript = args.presenter.resolve(), args.transcript.resolve()
    args.output, args.temporary = args.output.resolve(), args.temporary.resolve()
    build(args)


if __name__ == "__main__":
    main()
