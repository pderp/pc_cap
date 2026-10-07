"""Render the focused practice deck from editable Markdown, without model calls.

Run from pc_cap: ../venv/bin/python -m aw.focused_long_deck
The Markdown, not this module, owns every visible word and chart label.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import site
import subprocess
import unicodedata
from collections import Counter
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
DEFAULT = ASSETS / "presentation-materials/deck_v4"
LOG = ROOT / "logs/presentation/deck_v4-long-v1"
W, H = 1280, 720
BG, INK, MUTED = "#f7f7f2", "#142d3b", "#52646b"
TEAL, RUST, PURPLE, BLUE = "#007f7d", "#b64e33", "#6852a2", "#316f9b"
SERIES = [TEAL, PURPLE, "#78888d"]
SOURCES = {
    "triplet": ROOT / "logs/R1/reports/triplet/summary.json",
    "tails": ROOT / "logs/additional_work/HT-17/snapshot-20261004-complete/report.json",
    "depth": ROOT / "logs/additional_work/PC-v0/controls-report-20260929/report.json",
    "reader": ROOT / "logs/additional_work/PC-reader/report-round63-final/report.json",
    "upper": ROOT / "logs/additional_work/AW-L/report-round63-final/report.json",
    "mixture": ROOT / "logs/additional_work/AW-B/report-20260929/report.json",
    "examples": ASSETS / "support-information/examples.json",
    "credit_report": ROOT / "docs/additional_work/PC-v1_report.md",
    "proposal": ROOT / "docs/post_conference/coupled_collaboration_proposal.md",
    "objective": ROOT / "docs/additional_work/coupled_objective_note.md",
    "synthesis": ROOT / "docs/additional_work_report.md",
    "counterbench": DEFAULT / "section_3/2502.11008v2.pdf",
    "mquake_paper": DEFAULT / "section_3/2305.14795v3.pdf",
}


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save(path, data):
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def plain(text):
    return text.replace("**", "").replace("`", "").strip()


def flush_paragraph(buffer, destination):
    if buffer:
        destination.append(plain(" ".join(buffer)))
        buffer.clear()


def parse(path):
    slides = []
    for chunk in Path(path).read_text().split("\n---\n"):
        meta = next(re.finditer(r"<!-- layout: ([^>]+) -->", chunk), None)
        if meta is None:
            raise ValueError("Every slide needs a layout comment")
        options = dict(part.strip().split(": ", 1) for part in ("layout: " + meta[1]).split(";") if part.strip())
        s = dict(meta=options, title="", section="", intro=[], cards=[], post=[], table=[], takeaway="", source="")
        destination = s["intro"]
        buffer = []

        for line in chunk.splitlines():
            line = line.strip()
            if not line:
                flush_paragraph(buffer, destination)
            elif line.startswith("<!--"):
                flush_paragraph(buffer, destination)
                if line == "<!-- body -->":
                    destination = s["post"]
            elif line.startswith("# "):
                flush_paragraph(buffer, destination)
                s["title"] = plain(line[2:])
            elif line.startswith("*") and line.endswith("*") and not s["section"]:
                flush_paragraph(buffer, destination)
                s["section"] = line.strip("*")
            elif line.startswith("### "):
                flush_paragraph(buffer, destination)
                c = {"title": plain(line[4:]), "body": []}
                s["cards"].append(c)
                destination = c["body"]
            elif line.startswith("| "):
                flush_paragraph(buffer, destination)
                cells = [plain(v) for v in line.strip("|").split("|")]
                if not all(re.fullmatch(r"[-: ]+", v) for v in cells):
                    s["table"].append(cells)
                destination = s["post"]
            elif line.startswith("> "):
                flush_paragraph(buffer, destination)
                s["takeaway"] = plain(line[2:])
            elif line.startswith("Source:"):
                flush_paragraph(buffer, destination)
                s["source"] = plain(line)
            elif line.startswith("- "):
                flush_paragraph(buffer, destination)
                destination.append(plain(line[2:]))
            else:
                buffer.append(line)
        flush_paragraph(buffer, destination)
        if not all(s[k] for k in ["title", "section", "takeaway", "source"]):
            raise ValueError(f"Incomplete slide: {s['title']}")
        slides.append(s)
    return slides


def strings(slide):
    out = [slide["title"], slide["section"], *slide["intro"]]
    for card in slide["cards"]:
        out.extend([card["title"], *card["body"]])
    for row in slide["table"]:
        out.extend(row)
    return [*out, *slide["post"], slide["takeaway"], slide["source"]]


def tokens(text):
    return Counter(unicodedata.normalize("NFC", text).split())


def percent(value):
    return str(Decimal(str(round(value * 100, 9))).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) + "%"


def check_numbers(slides):
    """Bind presentation numbers to saved measurements, never to model reruns."""
    data = {k: json.loads(p.read_text()) for k, p in SOURCES.items() if p.suffix == ".json"}
    records = []

    def same(number, expected):
        actual = [row[1:] for row in slides[number-1]["table"][1:]]
        if actual != expected:
            raise ValueError(f"Slide {number} values disagree with saved results: {actual} != {expected}")
        records.append({"slide": number, "verified_values": expected})

    dslist = ["zsre", "counterfact", "mquake"]
    conds = ["R1_learned_ff", "R1_nonlearned", "v0_stable"]
    expected = []
    for ds in dslist:
        row = []
        for cond in conds:
            groups = [g for g in data["triplet"]["groups"] if g["dataset"] == ds and g["condition"] == cond]
            means = [sum(g["primary"]["RET-GS"]) / len(g["primary"]["RET-GS"]) for g in groups]
            row.append(percent(sum(means) / len(means)))
        expected.append(row)
    same(11, expected)
    expected = []
    for ds in dslist[:2]:
        for cond in conds:
            g = next(g for g in data["tails"]["groups"] if g["phase"] == "stage4" and g["dataset"] == ds and g["condition"] == cond)
            t = g["thresholds"]["0.01"]
            severity = t["conditional_mean_loss"]
            expected.append([f"{100*t['frequency']:.4f}%", f"{severity:.3f} nats" if severity is not None else "Undefined"])
    same(13, expected)
    expected = []
    for ds in dslist[:2]:
        row = []
        for cond in ["v5", "mixture:0.367879"]:
            g = next(g for g in data["tails"]["groups"] if g["phase"] == "AW-B" and g["dataset"] == ds and g["condition"] == cond)
            row.append(f"{g['thresholds']['0.01']['conditional_mean_loss']:.3f} nats")
        expected.append(row)
    same(16, expected)
    expected = []
    for depth in [1, 8, 32]:
        r = next(r for r in data["depth"]["summary"] if r["depth"] == depth and r["dataset"] == "zsre" and r["arm"] == "SE-E")
        expected.append([f"{100*r['metrics']['RET-ES']:.1f}%", f"{100*r['metrics']['RET-GS']:.1f}%", f"{r['learning_seconds']/60:.1f} min"])
    same(19, expected)
    credit = SOURCES["credit_report"].read_text()

    def report_rows(section):
        block = credit.split(section, 1)[1].split("\n## ", 1)[0]
        return [[x.strip() for x in line.strip("|").split("|")] for line in block.splitlines()
                if line.startswith("| zsre |") or line.startswith("| counterfact |")]

    efficacy = report_rows("## Checkpoint 300")
    cost = report_rows("## Acquisition and evaluation cost")
    harm = report_rows("## Ordinary-text harm and cost")
    expected = []
    for e, c, h in zip(efficacy, cost, harm[:4], strict=True):
        assert e[:2] == c[:2] == h[:2]
        label = "Adjoint" if e[1] == "SE-A" else "Error inference"
        expected.append([label, percent(float(e[4])), f"{float(c[3]):.0f} s", f"{float(h[7]):.2f} nats"])
    same(20, expected)
    expected = []
    for ds in dslist[:2]:
        for seed in range(3):
            row = []
            for rule in ["bp", "epc"]:
                c = next(c for c in data["reader"]["cells"] if c["dataset"] == ds and c["seed"] == seed and c["rule"] == rule)
                row.append(f"{100*c['metrics']['RET-GS']['value']:.1f}%")
            expected.append(row)
    same(21, expected)
    expected = []
    for seed in range(3):
        row = []
        for rule in ["bp", "epc"]:
            c = next(c for c in data["reader"]["trainings"] if c["seed"] == seed and c["rule"] == rule)
            row.append(f"{c['cost']['seconds']/3600:.3f} h")
        expected.append(row)
    same(22, expected)
    expected = []
    for ds in dslist[:2]:
        for seed in range(3):
            row = []
            for read in ["all", "upper"]:
                r = next(r for r in data["upper"]["write_comparisons"] if r["dataset"] == ds and r["seed"] == seed and r["read"] == read)
                row.append(f"{r['mean_loss_ratio']:.2f}×")
            expected.append(row)
    same(23, expected)

    # Output examples are literal saved strings, with only leading/trailing space removed.
    for number, ds in [(6, "zsre"), (7, "counterfact")]:
        item = data["examples"][ds]["items"][0]
        expected = []
        for cond in conds:
            c = item["conditions"][cond]
            expected.append([c[k]["generated"].strip() or "[empty answer]" for k in ["final_prompt", "final_paraphrase"]])
        same(number, expected)
        if item["paraphrase"] not in " ".join(strings(slides[number-1])):
            raise ValueError("Saved paraphrase was altered")
    kl = [v for g in data["triplet"]["groups"] if g["condition"] == "R1_learned_ff" for v in g["fidelity"]["capoff"]["mean_kl"]]
    assert len(kl) == 45 and all(v > .001 for v in kl)
    assert data["reader"]["completed_evaluations"] == 12
    assert data["upper"]["completed_evaluations"] == 24
    mixture = [r for r in data["mixture"]["success"]["per_coordinate"] if r["config"] == "mixture:0.367879"]
    assert len(mixture) == 10 and all(r["success"] for r in mixture)
    return data, records


class Renderer:
    def __init__(self, slide, number, data):
        import matplotlib.pyplot as plt

        self.s, self.number, self.data = slide, number, data
        self.fig = plt.figure(figsize=(W/72, H/72), dpi=96, facecolor=BG)
        self.fig.canvas.draw()
        self.renderer = self.fig.canvas.get_renderer()
        self.printed, self.boxes, self.errors = [], [], []
        self.color = {"1": TEAL, "2": PURPLE, "3": BLUE, "4": TEAL, "5": PURPLE}[slide["section"][0]]

    def rect(self, x, y, w, h, fill, radius=0, alpha=1):
        from matplotlib.patches import FancyBboxPatch, Rectangle

        if radius:
            p = FancyBboxPatch((x/W, 1-(y+h)/H), w/W, h/H, boxstyle=f"round,pad=0,rounding_size={radius/W}",
                              transform=self.fig.transFigure, facecolor=fill, edgecolor="none", alpha=alpha)
        else:
            p = Rectangle((x/W, 1-(y+h)/H), w/W, h/H, transform=self.fig.transFigure,
                          facecolor=fill, edgecolor="none", alpha=alpha)
        self.fig.patches.append(p)

    def wrapped(self, value, width, size, bold=False):
        from matplotlib.font_manager import FontProperties

        prop = FontProperties(family="DejaVu Sans", size=size, weight="bold" if bold else "normal")

        def measure(v):
            return self.renderer.get_text_width_height_descent(v, prop, False)[0] * 72 / self.fig.dpi

        lines = []
        for paragraph in value.split("\n"):
            line = ""
            for word in paragraph.split():
                test = (line + " " + word).strip()
                if line and measure(test) > width:
                    lines.append(line)
                    line = word
                else:
                    line = test
                if measure(word) > width:
                    self.errors.append(f"Unbreakable text exceeds width: {word}")
            lines.append(line)
        return "\n".join(lines), len(lines) * size * 1.23

    def text(self, value, x, y, width, size=23, bold=False, color=INK, height=None, minimum=None, rotation=0):
        size0 = size
        while True:
            wrapped, used = self.wrapped(value, width, size, bold)
            if height is None or used <= height or minimum is None or size <= minimum:
                break
            size -= .5
        if height is not None and used > height + .1:
            self.errors.append(f"Slide {self.number}: text height {used:.1f}>{height:.1f}: {value}")
        obj = self.fig.text(x/W, 1-y/H, wrapped, fontsize=size, color=color,
                            fontfamily="DejaVu Sans", fontweight="bold" if bold else "normal",
                            va="top", ha="left", linespacing=1.23, rotation=rotation,
                            rotation_mode="anchor", zorder=20)
        self.printed.append(value)
        self.boxes.append({"slide": self.number, "text": value, "x": x, "y": y,
                           "width": width, "planned_height": used, "font_size": size,
                           "requested_font_size": size0, "rotation": rotation, "object": obj})
        return used

    def paragraph_stack(self, values, x, y, width, size=23, gap=12):
        for value in values:
            y += self.text(value, x, y, width, size=size) + gap
        return y

    def arrow(self, x1, y1, x2, y2):
        from matplotlib.patches import FancyArrowPatch

        self.fig.patches.append(FancyArrowPatch((x1/W, 1-y1/H), (x2/W, 1-y2/H),
                                                transform=self.fig.transFigure, arrowstyle="-|>",
                                                mutation_scale=14, linewidth=2, color=self.color))

    def frame(self):
        self.rect(0, 0, W, 7, self.color)
        self.text(self.s["section"], 56, 29, 1168, 14, bold=True, color=self.color)
        h = self.text(self.s["title"], 56, 64, 1168, 36, bold=True, height=94, minimum=33)
        self.rect(56, 610, 1168, 67, self.color, radius=10)
        self.text(self.s["takeaway"], 74, 622, 1132, 21, bold=True, color="white", height=53, minimum=19.5)
        self.text(self.s["source"], 58, 691, 1164, 11, color=MUTED, height=23, minimum=10)
        return max(159, 64+h+17)

    def cover(self):
        self.rect(0, 0, W, H, INK)
        self.rect(915, 0, 365, H, "#1b444b")
        for k in range(7):
            self.rect(970+k*22, 140+k*29, 105, 105, TEAL, radius=14, alpha=.13+k*.025)
        self.rect(55, 51, 65, 6, "#58d2bb")
        self.text(self.s["section"], 140, 41, 740, 15, bold=True, color="#9be3d4")
        self.text(self.s["title"], 55, 102, 1035, 51, bold=True, color="white", height=190, minimum=48)
        a, b, c, d = self.s["intro"]
        self.text(a, 58, 312, 1150, 25, bold=True, color="#9be3d4")
        self.text(b, 58, 366, 1080, 29, color="white", height=110)
        self.text(c, 58, 489, 1090, 22, color="white")
        self.text(d, 58, 535, 1140, 18, color="#b3c8cb")
        self.text(self.s["takeaway"], 58, 599, 1150, 24, bold=True, color="white", height=75)
        self.text(self.s["source"], 58, 694, 1150, 11, color="#b3c8cb")

    def cards(self, y, flow=False):
        y = self.paragraph_stack(self.s["intro"], 58, y, 1164, 23, 12) + 7
        after_height = sum(self.wrapped(p, 1164, 22)[1]+11 for p in self.s["post"])
        bottom = 594-after_height
        cards = self.s["cards"]
        ncols = 2 if len(cards) == 4 else len(cards)
        nrows = math.ceil(len(cards)/ncols)
        gap = 26 if flow else 18
        width = (1164-gap*(ncols-1))/ncols
        height = (bottom-y-16*(nrows-1))/nrows
        for i, card in enumerate(cards):
            col, row = i % ncols, i // ncols
            x, top = 58+col*(width+gap), y+row*(height+16)
            self.rect(x, top, width, height, "#e9efeb", radius=12)
            self.rect(x+18, top+20, 37, 4, self.color)
            title_h = self.text(card["title"], x+18, top+40, width-36, 24, True,
                                self.color, height=70, minimum=21)
            body_y = top+48+title_h
            body = "\n\n".join(card["body"])
            self.text(body, x+18, body_y, width-36, 22, height=top+height-17-body_y, minimum=18.5)
            if flow and col < ncols-1:
                self.arrow(x+width+2, top+height/2, x+width+gap-2, top+height/2)
        self.paragraph_stack(self.s["post"], 58, bottom+9, 1164, 22, 11)

    def table(self, y):
        y = self.paragraph_stack(self.s["intro"], 58, y, 1164, 23, 12) + 5
        rows = self.s["table"]
        ratios = [float(v) for v in self.s["meta"].get("widths", "").split(",") if v]
        widths = [v*1164 for v in ratios] if ratios else [1164/len(rows[0])]*len(rows[0])
        post_h = sum(self.wrapped(p, 1164, 21)[1]+9 for p in self.s["post"])
        max_bottom = 597-post_h-8
        header_h = max(self.wrapped(v, w-24, 19, True)[1] for v, w in zip(rows[0], widths, strict=True))+22
        row_h = (max_bottom-y-header_h)/len(rows[1:])
        x = 58
        for value, width in zip(rows[0], widths, strict=True):
            self.rect(x, y, width-3, header_h, "#dce9e4", radius=3)
            self.text(value, x+12, y+10, width-24, 19, True, height=header_h-16)
            x += width
        for index, row in enumerate(rows[1:]):
            x, top = 58, y+header_h+index*row_h
            for value, width in zip(row, widths, strict=True):
                self.rect(x, top+3, width-3, row_h-4, "#eaf0ec" if index % 2 == 0 else "#f0f2ee", radius=3)
                self.text(value, x+12, top+13, width-24, 22, bold=index == 0,
                          height=row_h-22, minimum=19)
                x += width
        self.paragraph_stack(self.s["post"], 58, max_bottom+12, 1164, 21, 9)

    def metricbars(self, y):
        y = self.paragraph_stack(self.s["intro"], 58, y, 1164, 23, 11) + 9
        table = self.s["table"]
        maxima = [float(v) for v in self.s["meta"]["maxima"].split(",")]
        ncols = len(table[0])-1
        left_w = 300 if ncols == 2 else 280
        col_w = (1164-left_w)/ncols
        post_h = sum(self.wrapped(p, 1164, 21)[1]+10 for p in self.s["post"])
        bottom = 594-post_h
        header_h = max(self.wrapped(v, (left_w if i == 0 else col_w)-23, 19, True)[1]
                       for i, v in enumerate(table[0])) + 15
        row_h = min(89, (bottom-y-header_h)/len(table[1:]))
        self.text(table[0][0], 58, y, left_w-23, 19, True, color=MUTED)
        for j, label in enumerate(table[0][1:]):
            x = 58+left_w+j*col_w
            self.text(label, x+12, y, col_w-24, 19, True, color=SERIES[j])
        for i, row in enumerate(table[1:]):
            top = y+header_h+i*row_h
            if i % 2 == 0:
                self.rect(58, top, 1164, row_h-3, "#ebefea", radius=3)
            self.text(row[0], 66, top+12, left_w-28, 21, True, height=row_h-14, minimum=19)
            for j, value in enumerate(row[1:]):
                x = 58+left_w+j*col_w
                self.text(value, x+12, top+7, col_w-28, 23, True, color=SERIES[j], height=row_h-10, minimum=20)
                self.rect(x+12, top+row_h-12, col_w-32, 5, "#d8dfd9", radius=2)
                numeric = re.match(r"[\d.]+", value)
                if numeric:
                    n = float(numeric[0])
                    if not 0 <= n <= maxima[j]:
                        raise ValueError("Chart range clips a value")
                    self.rect(x+12, top+row_h-12, (col_w-32)*n/maxima[j], 5, SERIES[j], radius=2)
        self.paragraph_stack(self.s["post"], 58, y+header_h+len(table[1:])*row_h+13, 1164, 21, 10)

    def survival(self, y):
        import numpy as np

        self.paragraph_stack(self.s["intro"], 58, y, 1164, 22, 10)
        top, bottom = 280, 508
        for i, (card, condition) in enumerate(zip(self.s["cards"], ["R1_learned_ff", "v0_stable"], strict=True)):
            left = 160+i*553
            width = 480
            self.text(card["title"], left, 236, width, 24, True, color=TEAL if i == 0 else RUST)
            ax = self.fig.add_axes([left/W, 1-bottom/H, width/W, (bottom-top)/H], facecolor=BG)
            c = next(r for r in self.data["tails"]["cells"] if r["phase"] == "stage4" and r["dataset"] == "zsre"
                     and r["condition"] == condition and r["realization"] == 0 and r["order"] == 100)
            path = Path(c["vector"]["path"])
            assert digest(path) == c["vector"]["sha256"]
            with np.load(path) as z:
                values = z["values"]
                delta = (values[..., 0]-values[..., 1]).ravel()
            sorted_delta = np.sort(delta)
            x = np.unique(np.r_[.01, delta[delta > .01]])
            survival = (len(delta)-np.searchsorted(sorted_delta, x, side="right"))/len(delta)
            stats = c["statistics"]["thresholds"]["0.01"]
            grid = np.geomspace(.01, x[-1], 250)
            ref = stats["fraction"]*np.exp(-(grid-.01)/stats["exponential"]["scale"])
            ax.step(x, np.where(survival > 0, survival, np.nan), where="post", color=TEAL if i == 0 else RUST, lw=2.3)
            ax.plot(grid, ref, color=MUTED, ls="--", lw=1.8)
            ax.set(xscale="log", yscale="log", xlim=(.01, 35), ylim=(3e-6, .004))
            ax.set_xticks([.01, .1, 1, 10], labels=[])
            ax.set_yticks([.001, .0001, .00001], labels=[])
            ax.tick_params(which="both", length=0)
            ax.grid(which="major", color="#d8dfd9", lw=.65)
            for spine in ax.spines.values():
                spine.set_visible(False)
            labels = card["body"]
            assert len(labels) == 9
            for k, label in enumerate(labels[:2]):
                self.rect(left+14, 420+27*k, 228, 24, BG, alpha=.96)
                self.text(label, left+20, 425+27*k, 227, 15, color=TEAL if k == 0 and i == 0 else RUST if k == 0 else MUTED)
            for value in labels[2:6]:
                n = float(value)
                fx = (math.log10(n)-math.log10(.01))/(math.log10(35)-math.log10(.01))
                self.text(value, left+width*fx-13, bottom+9, 65, 16)
            for value in labels[6:]:
                n = float(value[:-1])/100
                fy = (math.log10(.004)-math.log10(n))/(math.log10(.004)-math.log10(3e-6))
                self.text(value, left-77, top+(bottom-top)*fy-8, 72, 16)
        self.text(self.s["post"][0], 367, 557, 810, 20)
        self.text(self.s["post"][1], 32, 505, 245, 14, rotation=90)

    def render(self):
        kind = self.s["meta"]["layout"]
        if kind == "cover":
            self.cover()
        else:
            y = self.frame()
            if kind in {"cards", "flow"}:
                self.cards(y, flow=kind == "flow")
            else:
                getattr(self, kind)(y)
        if tokens(" ".join(self.printed)) != tokens(" ".join(strings(self.s))):
            raise ValueError(f"Slide {self.number}: unprinted or invented Markdown text")
        self.fig.canvas.draw()
        for record in self.boxes:
            box = record.pop("object").get_window_extent(self.fig.canvas.get_renderer())
            bounds = [box.x0*72/self.fig.dpi, H-box.y1*72/self.fig.dpi,
                      box.x1*72/self.fig.dpi, H-box.y0*72/self.fig.dpi]
            record["bounds"] = bounds
            if bounds[0] < 0 or bounds[1] < 0 or bounds[2] > W+.1 or bounds[3] > H+.1:
                self.errors.append(f"Off-page text: {record['text']}")
        for i, a in enumerate(self.boxes):
            for b in self.boxes[i+1:]:
                ax0, ay0, ax1, ay1 = a["bounds"]
                bx0, by0, bx1, by1 = b["bounds"]
                overlap = max(0, min(ax1, bx1)-max(ax0, bx0))*max(0, min(ay1, by1)-max(ay0, by0))
                if overlap > 3:
                    self.errors.append(f"Text overlap on slide {self.number}: {a['text']} / {b['text']}")
        return self.fig


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT / "long_deck_v1.md")
    parser.add_argument("--output", type=Path, default=DEFAULT / "long_deck_v1.pdf")
    args = parser.parse_args()
    os.environ.setdefault("MPLCONFIGDIR", str(ASSETS / "presentation-materials/.matplotlib"))
    # Reuse installed reporting packages while preserving the project's NumPy.
    import numpy  # noqa: F401

    site.addsitedir(str(ASSETS / "envs/status-paper-20260911/lib/python3.12/site-packages"))
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_pdf import PdfPages

    matplotlib.rcParams.update({"font.family": "DejaVu Sans", "pdf.fonttype": 42,
                                "svg.fonttype": "none", "text.parse_math": False})
    slides = parse(args.source)
    data, numeric_checks = check_numbers(slides)
    LOG.mkdir(parents=True, exist_ok=True)
    resources = args.output.parent / "long_deck_v1_assets"
    previews, figures = resources / "previews", resources / "figures"
    previews.mkdir(parents=True, exist_ok=True)
    figures.mkdir(exist_ok=True)
    layout, errors = [], []
    with PdfPages(args.output, metadata={"Title": slides[0]["title"], "Author": "charlie derr",
                                       "Subject": "Focused colleague practice; all visible text from long_deck_v1.md"}) as pdf:
        for index, slide in enumerate(slides, 1):
            r = Renderer(slide, index, data)
            fig = r.render()
            pdf.savefig(fig, facecolor=fig.get_facecolor())
            fig.savefig(previews / f"slide-{index:02}.png", dpi=96)
            if slide["meta"]["layout"] in {"metricbars", "survival"}:
                for ext in ["svg", "pdf", "png"]:
                    fig.savefig(figures / f"slide-{index:02}.{ext}", dpi=160)
            layout.extend(r.boxes)
            errors.extend(r.errors)
            plt.close(fig)
    save(LOG / "layout.json", {"errors": errors, "text_boxes": layout})
    if errors:
        raise ValueError("\n".join(errors))
    extracted = subprocess.check_output(["pdftotext", "-layout", str(args.output), "-"], text=True)
    (LOG / "pdf-extracted.txt").write_text(extracted)
    pages = extracted.split("\f")
    if not pages[-1].strip():
        pages.pop()
    if len(pages) != len(slides):
        raise ValueError("Unexpected PDF page count")
    text_checks = []
    for index, (s, page) in enumerate(zip(slides, pages, strict=True), 1):
        want, got = tokens(" ".join(strings(s))), tokens(page)
        missing, extra = want-got, got-want
        text_checks.append({"slide": index, "match": not missing and not extra,
                            "missing": dict(missing), "extra": dict(extra)})
    save(LOG / "text-parity.json", text_checks)
    if not all(r["match"] for r in text_checks):
        raise ValueError("PDF text differs from Markdown; see text-parity.json")
    from PIL import Image

    thumbs = []
    for path in sorted(previews.glob("slide-*.png")):
        im = Image.open(path).convert("RGB")
        im.thumbnail((384, 216))
        thumbs.append(im)
    sheet = Image.new("RGB", (4*400, math.ceil(len(thumbs)/4)*240), BG)
    for i, im in enumerate(thumbs):
        sheet.paste(im, (8+(i % 4)*400, 8+(i//4)*240))
    sheet.save(resources / "contact-sheet.png")
    source_hashes = {str(p): digest(p) for p in SOURCES.values()}
    for p in sorted(DEFAULT.glob("*_section_of_slides")):
        source_hashes[str(p)] = digest(p)
    record = {"status": "complete", "slides": len(slides),
              "planned_seconds": sum(int(s["meta"]["seconds"]) for s in slides),
              "visible_words": sum(len(" ".join(strings(s)).split()) for s in slides),
              "source_markdown": str(args.source), "source_sha256": digest(args.source),
              "pdf": str(args.output), "pdf_sha256": digest(args.output),
              "sources_sha256": source_hashes, "numeric_checks": numeric_checks,
              "text_parity": "all visible words/numbers match page by page, including chart text",
              "layout_errors": 0, "model_calls": 0, "gpu_seconds": 0,
              "matplotlib": matplotlib.__version__, "builder_sha256": digest(__file__)}
    save(LOG / "build.json", record)
    print(json.dumps({k: record[k] for k in ["status", "slides", "planned_seconds", "visible_words", "pdf", "layout_errors"]}))


if __name__ == "__main__":
    main()
