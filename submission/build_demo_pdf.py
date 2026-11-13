"""Build the seven-page PDF demo from retained project evidence."""

import argparse
import hashlib
import json
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


ROOT = Path(__file__).resolve().parents[1]
WIDTH, HEIGHT = 1280, 720
INK, MUTED = "#123c3f", "#496c70"
TEAL, ORANGE = "#177e85", "#c46632"
PALE, GRID = "#edf4f4", "#d8e5e5"
REPO = "https://github.com/ArmanDamirchilou/climate-explorer"
DEMO = "https://climate-explorer-evidence.techtrendmedia-ai.chatgpt.site/"


def load(relative):
    return json.loads((ROOT / relative).read_text())


def text(pdf, value, x, top, size=26, color=INK, bold=False, width=None):
    font = "Helvetica-Bold" if bold else "Helvetica"
    pdf.setFont(font, size)
    pdf.setFillColor(HexColor(color))
    lines = []
    for paragraph in str(value).split("\n"):
        line = ""
        for word in paragraph.split():
            candidate = f"{line} {word}".strip()
            if width and line and stringWidth(candidate, font, size) > width:
                lines.append(line)
                line = word
            else:
                line = candidate
        lines.append(line)
    for index, line in enumerate(lines):
        pdf.drawString(x, HEIGHT - top - size - index * size * 1.3, line)
    return top + len(lines) * size * 1.3


def line(pdf, x1, top1, x2, top2, color=GRID, width=1):
    pdf.setStrokeColor(HexColor(color))
    pdf.setLineWidth(width)
    pdf.line(x1, HEIGHT - top1, x2, HEIGHT - top2)


def start(pdf, number, title, subtitle=None):
    pdf.setFillColor(HexColor("#ffffff"))
    pdf.rect(0, 0, WIDTH, HEIGHT, fill=1, stroke=0)
    text(pdf, title, 72, 44, 42, bold=True)
    if subtitle:
        text(pdf, subtitle, 74, 110, 25, MUTED, width=1120)
    text(pdf, "AI-assisted demonstration | Independent student prototype", 74, 682, 14, MUTED)
    text(pdf, f"{number} / 7", 1150, 682, 14, MUTED)


def source(pdf, value, target=None):
    text(pdf, value, 74, 642, 17, MUTED, width=1120)
    if target:
        pdf.linkURL(target, (72, 38, 1200, 80), relative=0, thickness=0)


def horizontal_bars(pdf, rows, max_value, left=560, top=205, plot_width=570, step=70, unit="", colors=None):
    for tick in range(6):
        value = max_value * tick / 5
        x = left + plot_width * tick / 5
        line(pdf, x, top - 12, x, top + len(rows) * step - 10)
        text(pdf, f"{value:g}{unit}", x - 12, top + len(rows) * step + 1, 18, MUTED)
    for index, (label, value) in enumerate(rows):
        y = top + index * step
        text(pdf, label, 76, y + 1, 23, width=460)
        pdf.setFillColor(HexColor((colors or [TEAL] * len(rows))[index]))
        pdf.rect(left, HEIGHT - y - 35, plot_width * value / max_value, 30, fill=1, stroke=0)
        text(pdf, f"{value:.3f}{unit}" if max_value <= 1 else f"{value:.1f}{unit}", left + plot_width * value / max_value + 12, y, 24, bold=True)


def build(output):
    example_path = ROOT / "artifacts/tehran-temperature-v02.json"
    example = load("artifacts/tehran-temperature-v02.json")
    audit = load("evaluation/science-audit.json")
    study = load("evaluation/results.json")
    scenario = next(row for row in study["scenarios"] if row["n"] == 45 and row["rho"] == 0.7 and row["true_slope_per_decade"] == 0)
    pdf = canvas.Canvas(str(output), pagesize=(WIDTH, HEIGHT), invariant=1)
    pdf.setTitle("Climate Explorer 1.3.1 project demonstration")
    pdf.setAuthor("Climate Explorer student project with OpenAI Codex assistance")
    pdf.setSubject("Seven-page PDF demonstration; early work and AI ideation eligibility unresolved")

    start(pdf, 1, "Climate Explorer 1.3.1")
    text(pdf, "Historical climate trends", 74, 190, 58, bold=True)
    text(pdf, "with visible assumptions", 74, 270, 58, TEAL, bold=True)
    text(pdf, "Be An Earth System Trend Detective!", 78, 390, 30, MUTED)
    text(pdf, "A proposed investigation tool for students and teachers", 78, 450, 26, MUTED)
    text(pdf, "Work began 11 November 2026, before the event.", 78, 552, 25, ORANGE)
    text(pdf, "Early work and AI ideation require organizer review.", 78, 590, 25, ORANGE)
    source(pdf, "Not affiliated with NASA or the existing KNMI Climate Explorer.")
    pdf.showPage()

    start(pdf, 2, "A historical rate is the start of an investigation", "Tehran temperature | NASA POWER | 1981-2025 | 45 complete years")
    x0, y0, w, h = 120, 200, 720, 310
    ymin, ymax = 14, 20
    for value in range(ymin, ymax + 1):
        yy = y0 + h * (ymax - value) / (ymax - ymin)
        line(pdf, x0, yy, x0 + w, yy)
        text(pdf, str(value), 78, yy - 11, 19, MUTED)
    text(pdf, "Annual mean (°C)", 78, 158, 20, MUTED)
    for year in [1981, 1990, 2000, 2010, 2025]:
        xx = x0 + w * (year - 1981) / 44
        text(pdf, str(year), xx - 22, 522, 19, MUTED)
    for records, color, weight in [(example["annual"], ORANGE, 2.5), (example["trend"]["line"], TEAL, 4)]:
        for a, b in zip(records, records[1:]):
            line(pdf, x0 + w * (a["year"] - 1981) / 44, y0 + h * (ymax - a["value"]) / 6,
                 x0 + w * (b["year"] - 1981) / 44, y0 + h * (ymax - b["value"]) / 6, color, weight)
    text(pdf, f"+{example['trend']['slope_per_decade']:.3f}", 902, 228, 58, TEAL, bold=True)
    text(pdf, "°C per decade", 908, 310, 29)
    text(pdf, "Fitted historical rate", 908, 357, 23, MUTED, width=280)
    text(pdf, "Orange: annual values\nTeal: fitted line", 910, 430, 21, MUTED)
    text(pdf, "A model grid is not a street thermometer. The rate does not identify a cause.", 76, 572, 25, width=1110)
    source(pdf, "Frozen NASA response and calculation: artifacts/tehran-temperature-v02.json", REPO + "/blob/main/artifacts/tehran-temperature-v02.json")
    pdf.showPage()

    start(pdf, 3, "The same rate can have different uncertainty", "Tehran 1981-2025 | Conditional 95% intervals in °C per decade")
    rows = example["checks"]["intervals"]
    left, plot_w, lo, hi, top = 500, 660, 0, 0.8, 220
    for tick in [0, 0.2, 0.4, 0.6, 0.8]:
        x = left + tick / (hi - lo) * plot_w
        line(pdf, x, 195, x, 440)
        text(pdf, f"{tick:.1f}", x - 13, 450, 20, MUTED)
    labels = ["Ordinary OLS", "Newey-West auto (lag 3)", "Newey-West lag 1", "Newey-West lag 5"]
    for index, row in enumerate(rows):
        y = top + index * 60
        lower, upper = row["ci95_per_decade"]
        a, b = left + lower / hi * plot_w, left + upper / hi * plot_w
        point = left + row["slope_per_decade"] / hi * plot_w
        text(pdf, labels[index], 76, y - 14, 25)
        line(pdf, a, y, b, y, TEAL, 5)
        line(pdf, a, y - 8, a, y + 8, TEAL, 2)
        line(pdf, b, y - 8, b, y + 8, TEAL, 2)
        pdf.setFillColor(HexColor(ORANGE))
        pdf.circle(point, HEIGHT - y, 6, fill=1, stroke=0)
    periods = example["checks"]["periods"]
    text(pdf, "Changing the dates changes the estimated rate", 76, 510, 28, bold=True)
    text(pdf, f"1981-2025: {periods[0]['slope_per_decade']:.3f}  |  1986-2020: {periods[3]['slope_per_decade']:.3f} °C per decade", 76, 555, 26)
    text(pdf, "Agreement on shared data does not remove source bias or guarantee coverage.", 76, 598, 23, MUTED)
    source(pdf, "Intervals are sensitivity checks, not a universal statistical correction.", REPO + "/blob/main/RESEARCH.md")
    pdf.showPage()

    start(pdf, 4, "Some intervals are too certain in our experiment", f"No true trend | 45 annual values | AR(1) correlation 0.7 | {study['replicates_per_scenario']:,} records")
    horizontal_bars(pdf, [("Nominal false-positive target", 5),
                          ("Ordinary interval: observed", 100 * scenario["methods"]["OLS iid"]["excludes_zero"]),
                          ("Newey-West auto: observed", 100 * scenario["methods"]["OLS HAC auto"]["excludes_zero"])],
                    50, left=555, top=220, plot_width=550, step=90, unit="%", colors=[MUTED, ORANGE, TEAL])
    text(pdf, "A narrow interval can fail when neighboring years are related.", 76, 565, 28, bold=True)
    text(pdf, "These rates describe this synthetic scenario, not a real city's error probability.", 76, 610, 23, MUTED)
    source(pdf, f"Full fixed study: {len(study['scenarios'])} scenarios, {len(study['scenarios']) * study['replicates_per_scenario']:,} records, {len(scenario['methods'])} method configurations. evaluation/", REPO + "/blob/main/evaluation/RESULTS.md")
    pdf.showPage()

    start(pdf, 5, "A source disagreement led to a spatial check", "Toronto investigation | Annual temperature rate | 1981-2025 | °C per decade")
    values = {row["label"]: row["weighted_slope_c_per_decade"] for row in audit["power"]}
    dataset = load("evaluation/dataset-check.json")
    toronto = next(r for r in dataset["rows"] if r["name"].startswith("Toronto"))
    bars = [("POWER at selected Toronto point", values["original_toronto"]),
            ("POWER at GISTEMP cell center", values["gistemp_cell_center"]),
            ("POWER at fixed north neighbor", values["north_neighbor"]),
            ("POWER at fixed west neighbor", values["west_neighbor"]),
            ("GISTEMP cell center", toronto["gistemp_slope_c_per_decade"])]
    horizontal_bars(pdf, bars, 1, left=600, top=195, plot_width=500, step=65,
                    colors=[ORANGE, TEAL, TEAL, TEAL, MUTED])
    text(pdf, "Changing the POWER location changes the comparison substantially.", 76, 574, 26, bold=True)
    text(pdf, "Different spatial supports. No station truth or physical cause established.", 76, 614, 23, MUTED)
    source(pdf, "Fixed exploratory diagnostic: evaluation/SCIENCE_AUDIT.md. All requested points retained.", REPO + "/blob/main/evaluation/SCIENCE_AUDIT.md")
    pdf.showPage()

    start(pdf, 6, "Keep and check an investigation", "The browser workflow preserves the chosen evidence and makes its verification limits visible")
    text(pdf, "Browser investigation", 76, 195, 32, TEAL, bold=True)
    text(pdf, "Compare four fixed periods.\nInspect all 666 date windows.\nOpen and save exact evidence.\nKeep optional notes on this device.", 76, 258, 26, width=500)
    text(pdf, "Two levels of verification", 660, 195, 32, TEAL, bold=True)
    text(pdf, "Browser: units, hash, aggregation,\nOLS and slope point checks.\nPython: selected result replay.\nAtlas verifier: all 666 windows.", 660, 258, 26, width=500)
    text(pdf, "Browser import retains precomputed intervals, p-values and chart bands.", 76, 490, 27, bold=True, width=1110)
    text(pdf, "Windows overlap. Selection has no multiplicity correction. A hash does not establish source truth.", 76, 554, 24, MUTED, width=1120)
    source(pdf, "Browser checks and saved notes verified 13 November. Frozen example SHA-256: " + hashlib.sha256(example_path.read_bytes()).hexdigest()[:20], REPO + "/blob/main/evaluation/replay.py")
    pdf.showPage()

    start(pdf, 7, "Working prototype and next evidence", "Public frozen demonstration and reproducible source")
    text(pdf, "Try the frozen examples", 76, 190, 30, TEAL, bold=True)
    text(pdf, DEMO, 76, 239, 25)
    pdf.linkURL(DEMO, (76, 430, 1170, 485), relative=0, thickness=0)
    text(pdf, "Read the source and evidence", 76, 305, 30, TEAL, bold=True)
    text(pdf, REPO, 76, 354, 25)
    pdf.linkURL(REPO, (76, 315, 1180, 370), relative=0, thickness=0)
    text(pdf, "Next: observe real student tasks and improve the explanations.", 76, 430, 28, width=1100)
    text(pdf, "Educational impact is not yet measured. This tool does not forecast or establish causes.", 76, 486, 25, MUTED, width=1110)
    text(pdf, "Codex contributed the approach, code and documentation.", 76, 563, 25, ORANGE)
    text(pdf, "Early work and AI ideation remain unresolved eligibility concerns.", 76, 603, 25, ORANGE)
    source(pdf, "AI_ASSISTANCE.md and submission/REQUIREMENTS.md retain the full history and rules.", REPO + "/blob/main/AI_ASSISTANCE.md")
    pdf.showPage()
    pdf.save()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path(__file__).with_name("climate-explorer-demo.pdf"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    build(args.output)
    print(args.output)


if __name__ == "__main__":
    main()
