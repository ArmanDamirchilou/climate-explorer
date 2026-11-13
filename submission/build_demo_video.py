"""Build a silent, captioned 29-second demo from retained climate evidence."""

import argparse
import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import pymupdf
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas

from build_demo_pdf import GRID, HEIGHT, INK, MUTED, ORANGE, ROOT, TEAL, WIDTH, line, load, text


SCENES = [
    (3, "Climate Explorer: investigate historical climate change."),
    (6, "Inspect the historical rate for Tehran, 1981-2025. This is not a forecast."),
    (6, "Compare assumptions and dates. Changing the period changes the estimated rate."),
    (5, "Inspect source and location differences. The cause of this disagreement is unresolved."),
    (5, "Save the source data and settings. Recalculate the result offline."),
    (4, "Try the public examples. AI-assisted prototype. Eligibility unresolved."),
]


def frame(pdf, title, caption):
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.rect(0, 0, WIDTH, HEIGHT, stroke=0, fill=1)
    text(pdf, title, 68, 36, 39, INK, True, width=1140)
    pdf.setFillColor(HexColor("#edf4f4"))
    pdf.rect(0, 54, WIDTH, 100, stroke=0, fill=1)
    text(pdf, caption, 68, 580, 31, INK, True, width=1130)
    pdf.setFillColor(HexColor(INK))
    pdf.rect(0, 0, WIDTH, 54, stroke=0, fill=1)
    text(pdf, "AI-assisted demonstration", 68, 678, 19, "#ffffff", True)
    text(pdf, "Started 11 Nov 2026 | Eligibility unresolved", 700, 678, 19, "#ffffff")


def bars(pdf, rows, left=585, top=175, width=500, step=68):
    for value in [0, 0.25, 0.5, 0.75, 1]:
        x = left + width * value
        line(pdf, x, 150, x, 500, GRID)
        text(pdf, f"{value:g}", x - 12, 505, 17, MUTED)
    for index, (label, value) in enumerate(rows):
        y = top + index * step
        text(pdf, label, 68, y, 25, width=490)
        pdf.setFillColor(HexColor(ORANGE if index == 0 else TEAL))
        pdf.rect(left, HEIGHT - y - 34, width * value, 30, stroke=0, fill=1)
        text(pdf, f"{value:.3f}", left + width * value + 14, y, 26, INK, True)


def render_frames(directory):
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "video-frames.pdf"
    pdf = canvas.Canvas(str(path), pagesize=(WIDTH, HEIGHT), invariant=1)
    pdf.setTitle("Climate Explorer video source frames")
    pdf.setAuthor("AI-assisted Climate Explorer project")
    example = load("artifacts/tehran-temperature-v02.json")
    audit = load("evaluation/science-audit.json")
    dataset = load("evaluation/dataset-check.json")

    frame(pdf, "Climate Explorer", "Investigate historical change with NASA data.")
    text(pdf, "A climate trend can depend", 68, 205, 55, INK, True)
    text(pdf, "on the choices we make", 68, 280, 55, TEAL, True)
    text(pdf, "Be An Earth System Trend Detective!", 72, 410, 27, MUTED)
    text(pdf, "Real retained data. No generated NASA observations.", 72, 470, 24, MUTED)
    pdf.showPage()

    frame(pdf, "Tehran temperature, 1981-2025", "A fitted historical rate is not a forecast.")
    x0, y0, width, height = 105, 170, 735, 330
    for value in range(14, 20):
        y = y0 + height * (19 - value) / 5
        line(pdf, x0, y, x0 + width, y)
        text(pdf, str(value), 68, y - 10, 19, MUTED)
    text(pdf, "Annual mean (°C)", 68, 117, 20, MUTED)
    for records, color, weight in [(example["annual"], ORANGE, 3), (example["trend"]["line"], TEAL, 4)]:
        for a, b in zip(records, records[1:]):
            line(pdf, x0 + width * (a["year"] - 1981) / 44, y0 + height * (19 - a["value"]) / 5,
                 x0 + width * (b["year"] - 1981) / 44, y0 + height * (19 - b["value"]) / 5, color, weight)
    for year in [1981, 2000, 2025]:
        text(pdf, str(year), x0 + width * (year - 1981) / 44 - 22, 513, 19, MUTED)
    text(pdf, f"+{example['trend']['slope_per_decade']:.3f}", 900, 245, 61, TEAL, True)
    text(pdf, "°C per decade", 906, 330, 29)
    text(pdf, "NASA POWER\nModel grid data", 907, 405, 24, MUTED)
    pdf.showPage()

    frame(pdf, "Compare assumptions and dates", "The period changes the question and the estimated rate.")
    left, width, top = 515, 645, 190
    for value in [0, 0.2, 0.4, 0.6, 0.8]:
        x = left + width * value / 0.8
        line(pdf, x, 162, x, 415)
        text(pdf, f"{value:.1f}", x - 12, 423, 19, MUTED)
    labels = ["Ordinary interval", "Newey-West auto", "Newey-West lag 1", "Newey-West lag 5"]
    for index, row in enumerate(example["checks"]["intervals"]):
        y = top + index * 65
        lower, upper = row["ci95_per_decade"]
        a, b = left + width * lower / 0.8, left + width * upper / 0.8
        text(pdf, labels[index], 68, y - 15, 27)
        line(pdf, a, y, b, y, TEAL, 5)
        line(pdf, a, y - 7, a, y + 7, TEAL, 2)
        line(pdf, b, y - 7, b, y + 7, TEAL, 2)
    text(pdf, "Conditional 95% intervals, °C per decade. Coverage is not guaranteed.", 68, 470, 22, MUTED)
    periods = example["checks"]["periods"]
    text(pdf, f"1981-2025: {periods[0]['slope_per_decade']:.3f}  |  1986-2020: {periods[3]['slope_per_decade']:.3f} °C / decade", 68, 518, 27, TEAL, True)
    pdf.showPage()

    frame(pdf, "Toronto: a source and location difference", "The disagreement is visible. Its cause is unresolved.")
    values = {row["label"]: row["weighted_slope_c_per_decade"] for row in audit["power"]}
    toronto = next(row for row in dataset["rows"] if row["name"].startswith("Toronto"))
    bars(pdf, [("POWER at Toronto point", values["original_toronto"]),
               ("POWER at GISTEMP center", values["gistemp_cell_center"]),
               ("POWER north neighbor", values["north_neighbor"]),
               ("POWER west neighbor", values["west_neighbor"]),
               ("GISTEMP cell center", toronto["gistemp_slope_c_per_decade"])])
    text(pdf, "1981-2025 | °C per decade | Different spatial supports; no station truth", 68, 543, 20, MUTED)
    pdf.showPage()

    frame(pdf, "Save evidence that can be repeated", "Recalculate the saved result without contacting NASA.")
    text(pdf, "Raw NASA response", 68, 180, 41, TEAL, True)
    text(pdf, "Recorded settings and hashes", 68, 270, 41, TEAL, True)
    text(pdf, "Offline replay", 68, 360, 41, TEAL, True)
    text(pdf, "Retained Tehran example: 45 annual values and sensitivity checks agree.", 68, 470, 26, MUTED, width=1110)
    text(pdf, "A matching hash does not prove that source data are correct.", 68, 525, 22, MUTED)
    pdf.showPage()

    frame(pdf, "Try the public examples", "An independent prototype, not a submitted entry.")
    text(pdf, "armandamirchilou.github.io", 68, 200, 45, TEAL, True)
    text(pdf, "/climate-explorer/", 68, 270, 45, TEAL, True)
    text(pdf, "Code, methods and sources are public.", 72, 380, 30)
    text(pdf, "Codex contributed the approach and implementation.", 72, 450, 25, MUTED)
    text(pdf, "Early work and AI ideation require organizer review.", 72, 500, 25, ORANGE)
    pdf.showPage()
    pdf.save()
    document = pymupdf.open(path)
    paths = []
    for index, page in enumerate(document):
        output = directory / f"scene-{index + 1}.png"
        page.get_pixmap().save(output)
        paths.append(output)
    return paths


def timestamp(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"00:{minutes:02d}:{seconds:02d}.000"


def build(output, temporary):
    for binary in ["ffmpeg", "ffprobe"]:
        if not shutil.which(binary):
            raise RuntimeError(f"{binary} is required")
    frames = render_frames(temporary)
    concat = temporary / "frames.txt"
    entries = []
    captions = ["WEBVTT", ""]
    elapsed = 0
    for path, (duration, caption) in zip(frames, SCENES):
        entries.extend([f"file '{path.name}'", f"duration {duration}"])
        captions.extend([f"{timestamp(elapsed)} --> {timestamp(elapsed + duration)}", caption, ""])
        elapsed += duration
    entries.append(f"file '{frames[-1].name}'")
    concat.write_text("\n".join(entries) + "\n")
    output.with_suffix(".vtt").write_text("\n".join(captions))
    command = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(concat),
               "-vf", "fps=24,format=yuv420p", "-t", str(elapsed),
               "-c:v", "libx264", "-crf", "18", "-preset", "medium", "-an", "-movflags", "+faststart",
               "-metadata", "title=Climate Explorer project demonstration", "-metadata", "artist=Climate Explorer with OpenAI Codex assistance",
               "-metadata", "comment=AI-assisted demonstration. Actual retained NASA data. No synthetic voice or human likeness. Work began 11 November 2026; eligibility unresolved.", str(output)]
    subprocess.run(command, check=True)
    probe = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(output)]))
    duration = float(probe["format"]["duration"])
    videos = [stream for stream in probe["streams"] if stream["codec_type"] == "video"]
    assert duration <= 30 and duration == elapsed
    assert len(videos) == 1 and (videos[0]["width"], videos[0]["height"]) == (WIDTH, HEIGHT)
    assert not any(stream["codec_type"] == "audio" for stream in probe["streams"])
    source_paths = [ROOT / "artifacts/tehran-temperature-v02.json", ROOT / "evaluation/science-audit.json", ROOT / "evaluation/dataset-check.json"]
    manifest = {"generated_utc": datetime.now(timezone.utc).isoformat(), "artifact": output.name,
                "sha256": hashlib.sha256(output.read_bytes()).hexdigest(), "duration_seconds": duration,
                "resolution": [WIDTH, HEIGHT], "codec": videos[0]["codec_name"], "pixel_format": videos[0]["pix_fmt"],
                "frame_rate": videos[0]["r_frame_rate"], "frame_count": int(videos[0]["nb_frames"]), "audio_streams": 0,
                "ffmpeg_version": subprocess.check_output(["ffmpeg", "-version"], text=True).splitlines()[0],
                "visuals": "Data figures calculated from retained analysis records. Not a screen recording or a fictional interface.",
                "ai_disclosure": "All frames visibly marked AI-assisted demonstration; embedded MP4 comment also acknowledges assistance.",
                "scenes": [{"duration_seconds": d, "caption": c} for d, c in SCENES],
                "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
                "visual_review": "Pending inspection of encoded video frames"}
    output.with_name("video-verification.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"{output}: {duration:.2f}s, {WIDTH}x{HEIGHT}, silent {videos[0]['codec_name']}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("climate-explorer-demo.mp4"))
    parser.add_argument("--temporary", type=Path, default=ROOT / "tmp/pdfs/video-demo")
    args = parser.parse_args()
    args.output = args.output.resolve()
    args.temporary = args.temporary.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(args.output, args.temporary)


if __name__ == "__main__":
    main()
