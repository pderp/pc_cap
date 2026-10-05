"""Build a separate colleague talk from completed records; no model execution.

JAX_PLATFORMS=cpu CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 \
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 ../venv/bin/python -m aw.colleague_deck
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import subprocess
from pathlib import Path

from aw.colleague_deck_content import SLIDES
from aw.refresh_report_steps import plotting

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets"
DOCS = ROOT / "docs/presentation/colleague_deck_20261004"
LOGS = ROOT / "logs/presentation/colleague_deck_20261004"
OUT = ASSETS / "presentation-materials/colleague_deck_20261004"
STEM = "active-inference-in-the-extremes-colleague-talk-20261004"
SOURCES = {
    "short_deck": ASSETS / "presentation-materials/deck_v3/deck-pdf-20261004/active-inference-in-the-extremes-deck-20261004.pdf",
    "brief": ROOT / "docs/presentation/presentation_brief_2026-09-26.md",
    "mapping": ROOT / "docs/presentation/abstract_to_testbed.md",
    "proposal": ROOT / "docs/post_conference/coupled_collaboration_proposal.md",
    "feedback": ROOT / "docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md",
    "stage4": ROOT / "docs/R1_stage4_report.md",
    "triplet": ROOT / "logs/R1/reports/triplet/summary.json",
    "examples": ASSETS / "support-information/examples.json",
    "examples_readme": ASSETS / "support-information/Capstan-README.md",
    "ht17": ROOT / "docs/additional_work/HT-17_report.md",
    "tails": ROOT / "logs/additional_work/HT-17/snapshot-20261004-complete/report.json",
    "awb": ROOT / "docs/additional_work/AW-B_report.md",
    "awb_data": ROOT / "logs/additional_work/AW-B/report-20260929/report.json",
    "pilot": ROOT / "docs/presentation/abstract_to_testbed.md",
    "pc_spec": ROOT / "docs/additional_work/PC-v0.md",
    "pc0": ROOT / "docs/additional_work/PC-v0_report.md",
    "pc1": ROOT / "docs/additional_work/PC-v1_report.md",
    "controls": ROOT / "docs/additional_work/PC-controls_report.md",
    "depth": ROOT / "logs/additional_work/PC-v0/controls-report-20260929/report.json",
    "matched": ROOT / "docs/additional_work/PC-matched-control_report.md",
    "reader": ROOT / "logs/additional_work/PC-reader/report-round63-final/report.json",
    "reader_doc": ROOT / "docs/additional_work/PC-reader_report.md",
    "upper": ROOT / "logs/additional_work/AW-L/report-round63-final/report.json",
    "upper_doc": ROOT / "docs/additional_work/AW-L_report.md",
    "option_r": ROOT / "docs/additional_work/R_report.md",
    "decisions": ROOT / "docs/decisions.md",
}
INK, MUTED, BG = "#182c3a", "#526678", "#faf9f5"
TEAL, RUST, PURPLE, BLUE = "#087e8b", "#bc5334", "#755398", "#3674b7"
COLORS = [TEAL, RUST, PURPLE]
LABELS = {"zsre": "zsRE", "counterfact": "CounterFact", "mquake": "MQuAKE"}
CONDITIONS = ["R1_learned_ff", "R1_nonlearned", "v0_stable"]
COND_LABELS = ["Learned reader", "Random reader", "Stable v0"]


def sha(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read(key):
    return json.loads(SOURCES[key].read_text())


def words(text):
    return len(re.findall(r"\b[\w’'-]+\b", text))


def clock(seconds):
    return f"{seconds // 60:02d}:{seconds % 60:02d}"


def check_headlines():
    """Reject a rebuild if fixed narrative values no longer match its sources."""
    import math

    groups = read("triplet")["groups"]
    learned = [g for g in groups if g["condition"] == "R1_learned_ff"]
    kls = [v for g in learned for v in g["fidelity"]["capoff"]["mean_kl"]]
    assert len(kls) == 45 and all(v > .001 for v in kls)
    for ds, expected in [("zsre", .9603333333), ("counterfact", .678), ("mquake", .7155555556)]:
        values = [v for g in learned if g["dataset"] == ds for v in g["primary"]["RET-GS"]]
        assert math.isclose(sum(values) / len(values), expected, abs_tol=1e-8)
    reader = read("reader")
    assert reader["completed_evaluations"] == 12
    assert len(reader["training_cost_ratios"]) == 3
    assert all(95 < r["epc_over_bp"] < 103 for r in reader["training_cost_ratios"])
    upper = read("upper")
    assert upper["completed_evaluations"] == 24
    ratios = [r["mean_loss_ratio"] for r in upper["write_comparisons"]]
    assert len(ratios) == 12 and 2.635 < min(ratios) < 2.636 and 4.368 < max(ratios) < 4.369
    mixture = [r for r in read("awb_data")["success"]["per_coordinate"] if r["config"] == "mixture:0.367879"]
    assert len(mixture) == 10 and all(r["success"] for r in mixture)
    assert sum(s["seconds"] > 0 for s in SLIDES) == 25
    assert sum(s["seconds"] for s in SLIDES) == 2365
    return {"triplet_means": "matched", "fidelity_failures": 45, "reader_evaluations": 12,
            "upper_evaluations": 24, "mixture_successes": 10}


def examples_checked():
    data = read("examples")
    bindings = {}
    for d in data.values():
        bindings.update(d["sources_sha256"])
    for path, expected in bindings.items():
        if sha(path) != expected:
            raise ValueError(f"Example input changed: {path}")
    # Independently match the selected raw checkpoint records by ID, not index.
    chosen = {"zsre": [0], "counterfact": [0, 10], "mquake": [0, 3]}
    selection = []
    for ds, indices in chosen.items():
        d = data[ds]
        cps = {Path(p).parts[-3].split(f"-{ds}-")[0]: json.loads(Path(p).read_text())
               for p in d["sources_sha256"] if Path(p).name.startswith("checkpoint-")}
        for index in indices:
            item = d["items"][index]
            for cond in CONDITIONS:
                raw = next(r for r in cps[cond]["retention"]["rows"] if r["item_id"] == item["item_id"])
                assert raw["query"]["generated"] == item["conditions"][cond]["final_prompt"]["generated"]
                assert raw["paraphrases"][0]["generated"] == item["conditions"][cond]["final_paraphrase"]["generated"]
            selection.append({"dataset": ds, "item_id": item["item_id"], "index": item["index"],
                              "realization": 0, "order": 100, "checkpoint": d["checkpoint"],
                              "selection": "purposive teaching illustration; not a success-rate sample"})
        if ds == "zsre":
            for section, saved in [("near_miss", d["near_miss"][0]), ("locality", d["locality"][0])]:
                for cond in CONDITIONS:
                    cp = cps[cond]
                    raw = next(r for r in (cp.get(section) or cp["endpoints"][section])["rows"]
                               if r["item_id"] == saved["item_id"])
                    output_key = "neighbour_cap" if section == "near_miss" else "cap"
                    query_key = "neighbour_query" if section == "near_miss" else "query"
                    assert raw[query_key]["generated"] == saved["conditions"][cond][output_key]
                    assert raw["reference"]["generated"] == saved["conditions"][cond][
                        "neighbour_reference" if section == "near_miss" else "reference"]
                selection.append({"dataset": ds, "section": section, "item_id": saved["item_id"],
                                  "realization": 0, "order": 100, "checkpoint": 1000})
    return data, bindings, selection


def figures(out):
    import matplotlib.pyplot as plt
    import numpy as np

    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 14, "axes.titlesize": 17,
                         "axes.labelsize": 14, "xtick.labelsize": 13, "ytick.labelsize": 13,
                         "axes.spines.top": False, "axes.spines.right": False,
                         "axes.edgecolor": MUTED, "text.color": INK, "axes.labelcolor": INK,
                         "figure.facecolor": BG, "axes.facecolor": BG, "savefig.facecolor": BG})
    folder = out / "figures"
    folder.mkdir(exist_ok=True)
    records = {}
    vector_sources = {}

    def save(fig, name, values):
        fig.savefig(folder / f"{name}.png", dpi=180)
        fig.savefig(folder / f"{name}.pdf")
        fig.savefig(folder / f"{name}.svg")
        plt.close(fig)
        records[name] = values

    # Each point is a realization mean, retaining the correct replication unit.
    groups = read("triplet")["groups"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2), sharey=True)
    vals = []
    for ax, ds in zip(axes, LABELS, strict=True):
        for k, cond in enumerate(CONDITIONS):
            rows = sorted((g for g in groups if g["dataset"] == ds and g["condition"] == cond),
                          key=lambda g: g["realization"])
            y = [100 * np.mean(r["primary"]["RET-GS"]) for r in rows]
            assert len(y) == 3
            ax.scatter([k - .1, k, k + .1], y, color=COLORS[k], s=48, alpha=.65)
            ax.plot([k - .24, k + .24], [np.mean(y)] * 2, color=COLORS[k], lw=4)
            vals.append(dict(dataset=ds, condition=cond, realization_means_percent=y,
                             mean_percent=float(np.mean(y))))
        ax.set(xticks=range(3), xticklabels=["Learned", "Random", "Stable"], ylim=(-5, 105),
               title=f"{LABELS[ds]} · {300 if ds == 'mquake' else 1000:,} edits")
        ax.grid(axis="y", alpha=.16)
    axes[0].set_ylabel("Retained paraphrase score (%)")
    fig.subplots_adjust(left=.07, right=.99, bottom=.17, top=.87, wspace=.15)
    save(fig, "retention", vals)

    tails = read("tails")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    vals = []
    for k, cond in enumerate(CONDITIONS):
        for i, ds in enumerate(["zsre", "counterfact"]):
            g = next(r for r in tails["groups"] if r["phase"] == "stage4" and
                     r["dataset"] == ds and r["condition"] == cond)
            t = g["thresholds"]["0.01"]
            y = i * 4 + k
            axes[0].barh(y, t["frequency"] * 100, color=COLORS[k], height=.64)
            axes[0].text(t["frequency"] * 100 + .025, y, f"{t['frequency'] * 100:.3f}%", va="center", fontsize=12)
            if t["conditional_mean_loss"] is not None:
                axes[1].barh(y, t["conditional_mean_loss"], color=COLORS[k], height=.64)
                axes[1].text(t["conditional_mean_loss"] + .04, y, f"{t['conditional_mean_loss']:.2f}", va="center", fontsize=12)
            else:
                axes[1].text(.08, y, "undefined: no observed events", va="center", fontsize=12)
            vals.append(dict(dataset=ds, condition=cond, frequency=t["frequency"], severity=t["conditional_mean_loss"]))
    ticks = [i * 4 + k for i in range(2) for k in range(3)]
    ticklabels = [f"{LABELS[ds]} · {label}" for ds in ["zsre", "counterfact"] for label in COND_LABELS]
    for ax in axes:
        ax.set_yticks(ticks)
        ax.set_ylim(6.75, -.75)
        ax.grid(axis="x", alpha=.15)
    axes[0].set(yticklabels=ticklabels, xlabel="Positions with Δ > 0.01 nat (%)", xlim=(0, 2.45), title="How often?")
    axes[1].set(yticklabels=[], xlabel="Mean Δ among those positions (nats)", xlim=(0, 4.15), title="How severe, when it happens?")
    fig.subplots_adjust(left=.215, right=.985, bottom=.18, top=.86, wspace=.15)
    save(fig, "frequency_severity", vals)

    # Exact empirical stairs on unique observed values, with the zero endpoint
    # masked on the log axis. Fits are reused, never re-estimated.
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=True)
    vals = []
    for ax, cond, label in zip(axes, ["R1_learned_ff", "v0_stable"], ["Learned reader", "Stable v0"], strict=True):
        c = next(r for r in tails["cells"] if r["phase"] == "stage4" and r["dataset"] == "zsre" and
                 r["condition"] == cond and r["realization"] == 0 and r["order"] == 100)
        p = c["vector"]["path"]
        assert sha(p) == c["vector"]["sha256"]
        vector_sources[p] = c["vector"]["sha256"]
        with np.load(p) as z:
            a = z["values"]
            delta = (a[..., 0] - a[..., 1]).ravel()
        u = .01
        x = np.unique(np.r_[u, delta[delta > u]])
        sorted_delta = np.sort(delta)
        y = (len(delta) - np.searchsorted(sorted_delta, x, side="right")) / len(delta)
        ax.step(x, np.where(y > 0, y, np.nan), where="post", color=TEAL, lw=2, label="Observed survival")
        t = c["statistics"]["thresholds"][str(u)]
        grid = np.geomspace(u, x[-1], 250)
        xi, scale = t["fit"]["shape"], t["fit"]["scale"]
        exponential = t["fraction"] * np.exp(-(grid - u) / t["exponential"]["scale"])
        gp = t["fraction"] * (1 + xi * (grid - u) / scale) ** (-1 / xi)
        ax.plot(grid, exponential, color=MUTED, ls="--", lw=2, label="Exponential fit")
        ax.plot(grid, gp, color=RUST, ls=":", lw=2.5, label="Generalized Pareto fit")
        ax.set(xscale="log", yscale="log", ylim=(3e-6, 4e-3), xlabel="Loss increase Δ (nats)",
               title=f"zsRE · {label}")
        ax.grid(alpha=.14)
        ax.legend(loc="lower left", fontsize=10, framealpha=.95)
        vals.append(dict(condition=cond, realization=0, order=100, threshold=u,
                         saved_shape=xi, source_vector=p, empirical_step="post", zero_survival="masked, not floored"))
    axes[0].set_ylabel("Fraction of all positions with Δ > x")
    fig.subplots_adjust(left=.08, right=.985, bottom=.19, top=.86, wspace=.17)
    save(fig, "survival", vals)

    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
    vals = []
    for ax, ds in zip(axes, ["zsre", "counterfact"], strict=True):
        means = []
        for cond in ["v5", "mixture:0.367879"]:
            g = next(r for r in tails["groups"] if r["phase"] == "AW-B" and r["dataset"] == ds and r["condition"] == cond)
            value = g["thresholds"]["0.01"]["conditional_mean_loss"]
            means.append(value)
            vals.append(dict(dataset=ds, condition=cond, conditional_severity=value, ret_gs=g["mean_ret_gs"]))
        ax.bar([0, 1], means, color=[RUST, TEAL], width=.58)
        for i, y in enumerate(means):
            ax.text(i, y + .06, f"{y:.3f}", ha="center", fontsize=19, weight="bold")
        ax.set(xticks=[0, 1], xticklabels=["Original cap", "Mixture"], ylim=(0, 2.25), title=LABELS[ds])
        ax.grid(axis="y", alpha=.15)
    axes[0].set_ylabel("Mean Δ given Δ > 0.01 (nats)")
    fig.subplots_adjust(left=.08, right=.985, bottom=.16, top=.86, wspace=.2)
    save(fig, "mixture_result", vals)

    depth = read("depth")["summary"]
    selected = [next(r for r in depth if r["dataset"] == "zsre" and r["arm"] == "SE-E" and r["depth"] == k) for k in [1, 8, 32]]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.2))
    x = range(3)
    axes[0].plot(x, [r["metrics"]["RET-ES"] * 100 for r in selected], "o-", color=TEAL, label="Original prompt")
    axes[0].plot(x, [r["metrics"]["RET-GS"] * 100 for r in selected], "s-", color=RUST, label="Paraphrase")
    axes[0].set(ylim=(0, 65), ylabel="Retained score (%)", title="Useful retention")
    axes[0].legend(fontsize=11, loc="center left")
    axes[1].plot(x, [r["es99_positive"] for r in selected], "o-", color=RUST)
    axes[1].set(ylim=(0, .28), ylabel="Positive-harm ES99 (nats)", title="Worst 1% average")
    axes[2].plot(x, [r["learning_seconds"] / 60 for r in selected], "o-", color=PURPLE)
    axes[2].set(ylim=(0, 30), ylabel="Learning minutes / cell", title="Learning cost")
    for ax in axes:
        ax.set(xticks=list(x), xticklabels=[1, 8, 32], xlabel="Settling steps")
        ax.grid(alpha=.16)
    fig.subplots_adjust(left=.065, right=.99, bottom=.19, top=.85, wspace=.38)
    save(fig, "depth", selected)

    reader = read("reader")
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), gridspec_kw={"width_ratios": [1.45, 1]})
    vals = []
    for di, ds in enumerate(["zsre", "counterfact"]):
        y = []
        for seed in range(3):
            a, b = [next(c for c in reader["cells"] if c["dataset"] == ds and c["seed"] == seed and c["rule"] == rule)
                    for rule in ["epc", "bp"]]
            y.append(100 * (a["metrics"]["RET-GS"]["value"] - b["metrics"]["RET-GS"]["value"]))
        positions = np.arange(3) + (di - .5) * .26
        axes[0].bar(positions, y, width=.24, color=[TEAL, RUST][di], label=LABELS[ds])
        for xpos, ypos in zip(positions, y, strict=True):
            axes[0].text(xpos, ypos - 1.0 if ypos < 0 else ypos + .9, f"{ypos:+.2f}", ha="center", va="top" if ypos < 0 else "bottom", fontsize=11)
        vals.append(dict(dataset=ds, epc_minus_bp_pp=y))
    axes[0].axhline(0, color=MUTED, lw=1)
    axes[0].set(xticks=range(3), xticklabels=["Seed 0", "Seed 1", "Seed 2"], ylim=(-30, 8),
                ylabel="ePC − BP (percentage points)", title="Paraphrase retention difference")
    axes[0].legend(fontsize=11, loc="lower right")
    ratios = reader["training_cost_ratios"]
    axes[1].bar(range(3), [r["epc_over_bp"] for r in ratios], color=PURPLE, width=.5)
    for i, r in enumerate(ratios):
        axes[1].text(i, r["epc_over_bp"] + 3, f"{r['epc_over_bp']:.1f}×", ha="center", fontsize=15)
    axes[1].set(xticks=range(3), xticklabels=["Seed 0", "Seed 1", "Seed 2"], ylim=(0, 125),
                ylabel="ePC / BP training process time", title="Actual training cost ratio")
    for ax in axes:
        ax.grid(axis="y", alpha=.14)
    fig.subplots_adjust(left=.075, right=.98, bottom=.16, top=.84, wspace=.35)
    save(fig, "reader", {"retention": vals, "training_ratios": ratios})

    upper = read("upper")["write_comparisons"]
    fig, axes = plt.subplots(1, 2, figsize=(13, 4.2), sharey=True)
    for ax, ds in zip(axes, ["zsre", "counterfact"], strict=True):
        for ri, readset in enumerate(["all", "upper"]):
            vals = sorted([r for r in upper if r["dataset"] == ds and r["read"] == readset], key=lambda r: r["seed"])
            assert len(vals) == 3
            ax.scatter(np.arange(3) + (ri - .5) * .12, [r["mean_loss_ratio"] for r in vals],
                       s=110, color=[TEAL, PURPLE][ri], marker=["o", "s"][ri], label=f"{readset.capitalize()} read taps")
        ax.axhline(1, color=RUST, ls="--", lw=1.5, label="No change (ratio 1)")
        ax.set(xticks=range(3), xticklabels=["Seed 0", "Seed 1", "Seed 2"], ylim=(0, 5), title=LABELS[ds])
        ax.grid(alpha=.12)
    axes[0].set_ylabel("Mean signed loss: last-only / all writes")
    axes[1].legend(fontsize=11, loc="lower right")
    fig.subplots_adjust(left=.08, right=.99, bottom=.15, top=.85, wspace=.17)
    save(fig, "upper", upper)
    return records, vector_sources


class Deck:
    """Small fixed-layout renderer with text overflow checks in every box."""

    def __init__(self, out):
        from matplotlib import get_data_path
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen.canvas import Canvas

        fonts = Path(get_data_path()) / "fonts/ttf"
        for name, filename in [("Deck", "DejaVuSans.ttf"), ("DeckBold", "DejaVuSans-Bold.ttf")]:
            pdfmetrics.registerFont(TTFont(name, str(fonts / filename)))
        pdfmetrics.registerFontFamily("Deck", normal="Deck", bold="DeckBold")
        self.c = Canvas(str(out / f"{STEM}.pdf"), pagesize=(1280, 720), pageCompression=1)
        self.c.setTitle("Active Inference in the Extremes — colleague talk")
        self.c.setAuthor("charlie derr; research with Matthew Iklé")
        self.c.setSubject("39-minute colleague rehearsal; completed results through 4 October 2026")
        self.c.showOutline()
        self.out = out
        self.checks = []
        self.errors = []

    def text(self, text, x, top, width, size=24, color=INK, bold=False, height=450):
        from reportlab.lib.colors import HexColor
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.platypus import Paragraph

        p = Paragraph(html.escape(str(text)).replace("\n", "<br/>"), ParagraphStyle(
            "text", fontName="DeckBold" if bold else "Deck", fontSize=size,
            leading=size * 1.27, textColor=HexColor(color), splitLongWords=False, spaceShrinkage=0))
        _, h = p.wrap(width, height)
        for line in p.blPara.lines:
            extra = line[0] if isinstance(line, tuple) else line.extraSpace
            if extra < -.1:
                self.errors.append(f"Slide {self.number}: horizontal text overflow {-extra:.1f} points: {text}")
        if h > height + .01:
            self.errors.append(f"Slide {self.number}: text overflow {h:.1f}>{height}: {text}")
        if top + h > 710:
            self.errors.append(f"Slide {self.number}: text below page: {text}")
        p.drawOn(self.c, x, 720 - top - h)
        self.checks.append(dict(slide=self.number, text=str(text), x=x, top=top, width=width, height=h, size=size))
        return h

    def rect(self, x, top, w, h, fill, stroke=None, radius=12):
        from reportlab.lib.colors import HexColor

        self.c.setFillColor(HexColor(fill))
        self.c.setStrokeColor(HexColor(stroke or fill))
        self.c.roundRect(x, 720 - top - h, w, h, radius, fill=1, stroke=bool(stroke))

    def arrow(self, x1, y1, x2, y2, color=TEAL):
        import math

        from reportlab.lib.colors import HexColor

        c = self.c
        c.setStrokeColor(HexColor(color))
        c.setLineWidth(2.4)
        c.line(x1, 720-y1, x2, 720-y2)
        a = math.atan2(y2-y1, x2-x1)
        for offset in [-.48, .48]:
            c.line(x2, 720-y2, x2 - 12*math.cos(a+offset), 720-y2 + 12*math.sin(a+offset))

    def box(self, title, body, x, top, w, h, color=TEAL, size=23):
        self.rect(x, top, w, h, "#edf2f0")
        used = self.text(title, x+20, top+18, w-40, size=22, bold=True, color=color, height=80)
        self.text(body, x+20, top+35+used, w-40, size=size, height=h-used-48)

    def table(self, headers, rows, top=260, widths=None, size=22):
        widths = widths or [1180 / len(headers)] * len(headers)
        x = 50
        header_h = 68
        for header, w in zip(headers, widths, strict=True):
            self.rect(x, top, w-3, header_h, "#e0ebe9", radius=2)
            self.text(header, x+14, top+8, w-28, size=20, bold=True, height=54)
            x += w
        row_h = min(75, (570 - top - header_h) / max(1, len(rows)))
        for i, row in enumerate(rows):
            x = 50
            y = top + header_h + i * row_h
            for value, w in zip(row, widths, strict=True):
                self.rect(x, y, w-3, row_h-2, "#f0f2ee" if i % 2 == 0 else BG, radius=1)
                self.text(value, x+14, y+10, w-28, size=size, height=row_h-14)
                x += w

    def diagrams(self, name):
        if name == "active_loop":
            self.box("Observe", "A correction, question\nor unexpected failure", 60, 210, 330, 150, PURPLE)
            self.box("Infer", "Update beliefs about\nwhat needs correcting", 475, 210, 330, 150, PURPLE)
            self.box("Choose", "Act, abstain, or ask\nan informative question", 890, 210, 330, 150, PURPLE)
            self.arrow(395, 282, 463, 282, PURPLE)
            self.arrow(810, 282, 878, 282, PURPLE)
            self.box("Preferences + consequences + uncertainty", "PROPOSED: expected-free-energy policy over outcomes and information value", 240, 445, 800, 140, PURPLE, 22)
            self.arrow(1055, 370, 1055, 410, PURPLE)
            self.arrow(1055, 410, 225, 410, PURPLE)
            self.arrow(225, 410, 225, 373, PURPLE)
        elif name == "architecture":
            for title, body, x in [("Environment", "Supplied edits\nNew questions\nOrdinary text", 55),
                                   ("Adaptive cap", "Fact memory\nLearned reader + null gate\nBounded residual writes", 450),
                                   ("Frozen transformer", "Predict next token\nRead internal features\nBase weights fixed", 845)]:
                self.box(title, body, x, 220, 375, 235)
            self.arrow(432, 295, 447, 295)
            self.arrow(827, 315, 842, 315)
            self.arrow(842, 370, 827, 370)
            self.text("A null decision leaves the base prediction in place.\nAn interface is implemented; a formal Markov blanket is not established.", 65, 500, 1150, size=25, height=85)
        elif name == "harm":
            self.text("Same text prefix, same observed next token", 65, 198, 1120, 30, bold=True, height=50)
            self.box("ILLUSTRATIVE arithmetic", "Base probability p₀ = 0.10\nCap probability pcap = 0.01\nLoss increase = log(10) ≈ 2.30 nats", 60, 285, 560, 225, RUST, 26)
            self.box("ACTUAL main-study benchmark", "45 / 45 learned-reader cells\nexceed mean KL 0.001.\nTheir data-integrity checks pass.", 660, 285, 560, 225, RUST, 26)
            self.text("Observed-token loss and whole-distribution KL answer different questions.", 65, 546, 1130, 23, height=50)
        elif name == "mixture":
            self.box("Frozen base", "37% base distribution\nρ = e⁻¹ ≈ 0.368", 70, 205, 490, 155, RUST, 28)
            self.box("Corrected model", "63% cap distribution\n1 − ρ ≈ 0.632", 720, 205, 490, 155, TEAL, 28)
            self.arrow(310, 368, 550, 427, RUST)
            self.arrow(960, 368, 730, 427)
            self.box("Probability mixture", "q = ρp₀ + (1 − ρ)pcap\nEvery token retains a floor of ρp₀.", 270, 440, 740, 150, RUST, 27)
        elif name == "pc":
            self.box("Adjoint credit · SE-A", "Differentiate the task loss\nTake a negative normalized direction\nApply the bounded memory update", 55, 210, 560, 230, TEAL, 25)
            self.box("Error inference · SE-E", "Set temporary errors e = 0\nMinimize E(e) = ½Σ‖e‖² + task loss\nNormalize inferred site errors", 665, 210, 560, 230, PURPLE, 25)
            self.text("Same target, fixed existing writes, same bounded update", 80, 478, 1120, 30, bold=True, height=70)
            self.text("8 settling steps at η = 0.1; 9 forward + 9 reverse evaluations including the terminal diagnostic.", 80, 552, 1120, 23, height=65)
        elif name == "future":
            self.box("Available evidence", "Retained corrections\nWrong-memory retrieval\nRare ordinary-text losses", 55, 205, 360, 245, TEAL, 24)
            self.box("PROPOSED policy", "Beliefs + preferences\nAction / observation model\nInformation value and cost", 460, 205, 360, 245, PURPLE, 24)
            self.box("Choose one audit", "Original prompt?\nNew paraphrase?\nNearby unedited fact?", 865, 205, 360, 245, PURPLE, 24)
            self.arrow(419, 305, 454, 305)
            self.arrow(824, 305, 859, 305, PURPLE)
            self.box("Coupled-objective collaboration: first specify the probability model", "Modeled variables · constraints · weighting / escort distribution · gradients · explicit baseline", 85, 470, 1110, 110, PURPLE, 22)

    def example(self, which, data):
        def quote(text, maximum=None):
            value = text.strip()
            if not value:
                return "[empty answer]"
            if maximum and len(value) > maximum:
                value = value[:maximum].rsplit(" ", 1)[0] + "… [excerpt]"
            return f"“{value}”"

        if which == "zsre":
            r = data["zsre"]["items"][0]
            self.text(f"Teach: {r['prompt']} → {r['target']}", 55, 192, 1170, 25, bold=True, height=70)
            self.text(f"Paraphrase: {r['paraphrase']}", 55, 248, 1160, 23, height=55)
            rows = []
            for cond, label in zip(CONDITIONS, COND_LABELS, strict=True):
                c = r["conditions"][cond]
                rows.append([label, quote(c["final_prompt"]["generated"]), quote(c["final_paraphrase"]["generated"])])
            self.table(["At the 1,000-edit endpoint", "Original prompt", "Paraphrase"], rows, top=315,
                       widths=[350, 415, 415], size=23)
            self.text("All three acquired the target immediately. Cap-free original answer: empty (newline).", 60, 594, 1160, 18, height=35)
        elif which in ["counterfact", "mquake"]:
            ds = which
            indices = [0, 10] if ds == "counterfact" else [0, 3]
            for i, ix in enumerate(indices):
                r = data[ds]["items"][ix]
                c = r["conditions"]["R1_learned_ff"]
                x = 55 + 610*i
                self.rect(x, 188, 560, 413, "#edf2f0")
                y = 205
                fields = [
                    ("PARAPHRASE SUCCESS" if i == 0 else "PARAPHRASE FAILURE", 20, True, TEAL if i == 0 else RUST),
                    ("Teach: " + r["prompt"], 20, False, INK),
                    (f"Target: {r['target']} (stored old: {r['target_true']})", 20, True, INK),
                    ("Ask: " + r["paraphrase"], 20, False, INK),
                    ("Paraphrase output: " + quote(c["final_paraphrase"]["generated"], 70), 20, True, INK),
                    ("Cap fired: " + ("yes" if c["final_paraphrase"]["fired"] else "no"), 18, False, MUTED),
                ]
                for txt, size, bold, color in fields:
                    y += self.text(txt, x+18, y, 528, size, color, bold, height=590-y) + 9
        elif which == "preservation":
            r = data["zsre"]["near_miss"][0]
            self.text(f"Teach: {r['edit_prompt']} → {r['edit_answer']}", 55, 195, 1160, 26, bold=True, height=65)
            self.text(f"Ask nearby: {r['neighbour_prompt']}", 55, 246, 1160, 25, height=50)
            rows = [["Base (no cap)", quote(r["conditions"]["R1_learned_ff"]["neighbour_reference"]), "Reference"]]
            for cond, label in zip(CONDITIONS, COND_LABELS, strict=True):
                c = r["conditions"][cond]
                rows.append([label, quote(c["neighbour_cap"]), "Preserved" if c["preserved"] else "Changed"])
            self.table(["Condition", "Neighboring answer", "Preservation score"], rows, top=303, size=22)
            self.text("Locality example: “what is the name of fred flintstones wife” → “?” both with and without cap.", 58, 580, 1160, 18, height=43)

    def page(self, s, i, data):
        self.number = i
        self.rect(0, 0, 1280, 720, BG, radius=0)
        color = PURPLE if s["section"] == "Active inference" else RUST if s["section"] == "Extremes" else TEAL
        self.rect(0, 0, 1280, 8, color, radius=0)
        self.c.bookmarkPage(f"slide-{i}")
        self.c.addOutlineEntry(f"{i:02d} · {s['title']}", f"slide-{i}")
        self.text(s["section"].upper(), 50, 27, 800, 16, color, True, height=30)
        title_h = self.text(s["title"], 50, 66, 1180, 35, INK, True, height=99)
        if s.get("subtitle") and s["kind"] != "cover":
            self.text(s["subtitle"], 52, 82+title_h, 1170, 17, MUTED, height=50)
        if s["kind"] == "cover":
            self.text(s["subtitle"], 55, 215, 1100, 33, height=130)
            self.text(s["author"], 55, 370, 1130, 29, height=75)
            self.text(s["tag"], 55, 448, 1100, 22, MUTED, height=50)
            self.text("Active inference   /   Predictive coding   /   Heavy-tailed distributions", 55, 533, 1170, 26, TEAL, True, height=75)
        elif s["kind"] == "cards":
            n = len(s["cards"])
            width = (1180 - 24*(n-1))/n
            for k, card in enumerate(s["cards"]):
                x = 50 + k*(width+24)
                self.rect(x, 213, width, 367, "#edf2f0")
                y = 234
                y += self.text(card[0], x+20, y, width-40, 26, COLORS[k % 3], True, height=90) + 26
                for line in card[1:]:
                    y += self.text(line, x+20, y, width-40, 23, height=568-y) + 20
        elif s["kind"] == "diagram":
            self.diagrams(s["diagram"])
        elif s["kind"] == "example":
            self.example(s["example"], data)
        elif s["kind"] == "table":
            if s.get("intro"):
                self.text(s["intro"], 55, 193, 1160, 26, bold=True, height=65)
            widths = [350, 590, 240] if i == 9 else [325, 855] if i == 27 else None
            self.table(s["headers"], s["rows"], top=267 if s.get("intro") else 210, widths=widths,
                       size=22 if i != 27 else 23)
            if s.get("table_note"):
                self.text(s["table_note"], 60, 580, 1160, 21, height=55)
        elif s["kind"] == "figure":
            self.c.drawImage(str(self.out / "figures" / f"{s['figure']}.png"), 38, 118,
                             width=1204, height=410, preserveAspectRatio=True, anchor="c")
        self.rect(40, 633, 1200, 3, color, radius=0)
        self.text(s["takeaway"], 50, 645, 1175, 18, INK, True, height=50)
        footer = "charlie derr · colleague rehearsal · 4 Oct 2026"
        self.text(footer, 50, 697, 700, 10, MUTED, height=13)
        self.text(f"{i:02d} / 25" if i <= 25 else f"Backup {i-25} / 5", 1090, 695, 145, 11, MUTED, height=15)
        self.c.textAnnotation(s["notes"], Rect=(1218, 675, 1235, 692), Name="Comment")
        self.c.showPage()


def documents(out, selected):
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "slides.json").write_text(json.dumps(SLIDES, indent=2, ensure_ascii=False) + "\n")
    elapsed = 0
    notes = ["# Colleague talk — timed speaker notes", "",
             "Draft for charlie. 25 main slides + 5 optional backups. Target **39:25**, including two short feedback pauses; "
             "open Q&A is additional. Rehearse to measure actual delivery. Notes are a speaking draft, not text to put on slides.", "",
             "Audience assumption: technically curious colleagues with no prior project knowledge. Full conference title: "
             "*Coupled Active Inference on a Frozen Transformer Prior: A Risk-Aware Residual Agent for Non-Equilibrium Regimes* "
             "(charlie derr and Matthew Iklé).", "", "| Slide | Clock | Words |", "|---|---|---:|"]
    for i, s in enumerate(SLIDES, 1):
        if s["seconds"]:
            notes.append(f"| {i:02d}. {s['title']} | {clock(elapsed)}–{clock(elapsed+s['seconds'])} | {words(s['notes'])} |")
            elapsed += s["seconds"]
    pdf = []
    title_style = ParagraphStyle("title", fontName="DeckBold", fontSize=18, leading=23, spaceAfter=10)
    normal = ParagraphStyle("notes", fontName="Deck", fontSize=11.5, leading=16.5, spaceAfter=9)
    small = ParagraphStyle("sources", fontName="Deck", fontSize=8.5, leading=12, textColor=colors.HexColor(MUTED))
    elapsed = 0
    for i, s in enumerate(SLIDES, 1):
        timing = f"{clock(elapsed)}–{clock(elapsed+s['seconds'])}" if s["seconds"] else "Optional backup"
        notes += ["", f"## {i:02d}. {s['title']}", "", f"**{timing}** · {s['seconds']} seconds · {words(s['notes'])} words", "",
                  "### Say", "", s["notes"], "", "### Sources / delivery", "", s["takeaway"], ""]
        if s.get("pause_seconds"):
            notes.append(f"The allocation includes a {s['pause_seconds']}-second audience pause.")
        for key in s["sources"]:
            notes.append(f"- `{key}`: `{SOURCES[key].relative_to(ROOT.parent)}`")
        pdf.append(Paragraph(html.escape(f"{i:02d}. {s['title']}"), title_style))
        pdf.append(Paragraph(timing, small))
        pdf.append(Spacer(1, 12))
        for paragraph in s["notes"].split("\n\n"):
            pdf.append(Paragraph(html.escape(paragraph.replace("\n", " ")), normal))
        pdf.append(Paragraph("Sources: " + html.escape(", ".join(s["sources"])), small))
        if i < len(SLIDES):
            pdf.append(PageBreak())
        elapsed += s["seconds"]
    (DOCS / "speaker-notes.md").write_text("\n".join(notes) + "\n")
    SimpleDocTemplate(str(out / "speaker-notes.pdf"), pagesize=(612, 792),
                      rightMargin=45, leftMargin=45, topMargin=45, bottomMargin=45,
                      title="Colleague talk — speaker notes", author="charlie derr").build(pdf)
    source_lines = ["# Sources and selected examples", "", "Result snapshot: 2026-10-04. No model calls or new fits.", "",
                    "## Source map", ""]
    source_lines += [f"- **{key}**: `{path.relative_to(ROOT.parent)}`" for key, path in SOURCES.items()]
    source_lines += ["", "## Selection and display policy", "",
                     "Examples are selected for explanation, not randomly sampled or used to estimate an endpoint. "
                     "All come from Capstan's first-30-item collection, realization 0/order 100. The slide set includes "
                     "both success and failure, plus preservation of a poor base output. Leading/trailing whitespace is "
                     "removed for display; long continuations are explicitly marked as excerpts. The full strings, "
                     "including the original prompt, are in `assets/support-information/examples.json`. "
                     "No grammar or factual content of the saved prompts was repaired. Counterfactual targets "
                     "are experimental instructions, not asserted world facts.", "",
                     "The Fred Flintstone prompt is shown without its `nq question:` prefix on slide 8; the full source "
                     "is `nq question: what is the name of fred flintstones wife`. Empty answer and no-cap-firing are "
                     "separate observations. The example's stored selection flag is used when stating whether the cap fired.", "",
                     "| Dataset | Item / endpoint | Stream index | Final checkpoint |", "|---|---|---:|---:|"]
    source_lines += [f"| {r['dataset']} | `{r['item_id']}` | {r.get('index', 'endpoint probe')} | {r['checkpoint']} |" for r in selected]
    source_lines += ["", "## Plot policy", "",
                     "Graph coordinates are exported in `logs/presentation/colleague_deck_20261004/plotted-values.json`. "
                     "Retention dots are realization means after averaging orders; all three are displayed. "
                     "Frequency and severity are the saved HT-17 group summaries with no new interval claim. "
                     "Survival curves reuse exactly two preselected zsRE cells (realization 0, order 100); "
                     "empirical stairs use unique observed values and `where=post`, with zero survival masked on "
                     "the log axis rather than floored. GPD/exponential parameters come from the saved report; no refits. "
                     "Reader differences intersect dataset/seed/rule identities. Upper-layer graph shows all twelve "
                     "paired last-only/all-write ratios. Source hashes are in the build receipt."]
    (DOCS / "sources-and-examples.md").write_text("\n".join(source_lines) + "\n")


def browser(out):
    pages = out / "pages"
    pages.mkdir(exist_ok=True)
    subprocess.run(["pdftoppm", "-scale-to", "1440", "-png", str(out / f"{STEM}.pdf"), str(pages / "slide")], check=True)
    imgs = sorted(pages.glob("slide-*.png"))
    assert len(imgs) == len(SLIDES)
    slides = []
    for path, s in zip(imgs, SLIDES, strict=True):
        slides.append(dict(image="data:image/png;base64," + base64.b64encode(path.read_bytes()).decode(),
                           title=s["title"], notes=s["notes"], seconds=s["seconds"]))
    data = json.dumps(slides, ensure_ascii=False).replace("</", "<\\/")
    page = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Active Inference in the Extremes — colleague talk</title>
<style>body{margin:0;background:#14212a;color:#fff;font:17px system-ui}main{height:calc(100vh - 56px);display:flex;align-items:center;justify-content:center}img{max-width:100%;max-height:100%;object-fit:contain}nav{height:56px;display:flex;gap:14px;align-items:center;padding:0 18px;box-sizing:border-box}button{font:inherit;background:#29434f;color:white;border:1px solid #94b8bd;border-radius:5px;padding:5px 12px;cursor:pointer}#notes{display:none;position:absolute;right:0;top:0;width:min(560px,80vw);height:calc(100vh - 76px);padding:18px;background:#fff;color:#182c3a;overflow:auto;white-space:pre-wrap;line-height:1.5;box-sizing:border-box}#notes.open{display:block}#time{margin-left:auto}button:focus{outline:3px solid #f2b26a}@media print{nav,#notes{display:none}}</style>
<main><img id="slide" alt=""></main><aside id="notes" aria-label="Speaker notes"></aside>
<nav><button id="prev" aria-label="Previous slide">←</button><span id="count"></span><button id="next" aria-label="Next slide">→</button><button id="toggle">N · notes</button><button id="full">F · fullscreen</button><span id="time">00:00</span><button id="reset">Reset clock</button></nav>
<script>const slides=DATA;let index=0,start=Date.now();const $=id=>document.getElementById(id);
function show(){const s=slides[index];$('slide').src=s.image;$('slide').alt=s.title;$('notes').textContent=(index+1)+'. '+s.title+'\\n\\n'+s.notes;$('count').textContent=(index+1)+' / '+slides.length+(index>=25?' · backup':'');$('prev').disabled=index===0;$('next').disabled=index===slides.length-1;}
function move(d){index=Math.max(0,Math.min(slides.length-1,index+d));show()}
$('prev').onclick=()=>move(-1);$('next').onclick=()=>move(1);$('toggle').onclick=()=>$('notes').classList.toggle('open');
$('full').onclick=()=>document.fullscreenElement?document.exitFullscreen():document.documentElement.requestFullscreen();$('reset').onclick=()=>{start=Date.now()};
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();move(1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();move(-1)}if(e.key==='Home'){index=0;show()}if(e.key==='End'){index=slides.length-1;show()}if(e.key.toLowerCase()==='n')$('toggle').click();if(e.key.toLowerCase()==='f')$('full').click()});
setInterval(()=>{let t=Math.floor((Date.now()-start)/1000);$('time').textContent=String(Math.floor(t/60)).padStart(2,'0')+':'+String(t%60).padStart(2,'0')},500);show();</script></html>"""
    (out / "present.html").write_text(page.replace("DATA", data))
    return imgs


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()
    out = args.out.resolve()
    if not out.is_relative_to(ASSETS / "presentation-materials"):
        raise ValueError("Presentation resources must live in assets/presentation-materials")
    out.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    plotting()
    import matplotlib

    matplotlib.use("Agg")
    sources_before = {str(p): sha(p) for p in SOURCES.values()}
    headline_checks = check_headlines()
    data, example_inputs, selected = examples_checked()
    values, vector_sources = figures(out)
    deck = Deck(out)
    for i, s in enumerate(SLIDES, 1):
        deck.page(s, i, data)
    deck.c.save()
    if deck.errors:
        raise ValueError("\n".join(deck.errors))
    documents(out, selected)
    pages = browser(out)
    # A compact contact sheet for a full-deck visual pass.
    from PIL import Image, ImageDraw

    sheet = Image.new("RGB", (1500, 6*192), "#e9ece9")
    draw = ImageDraw.Draw(sheet)
    for i, path in enumerate(pages):
        with Image.open(path) as im:
            im.thumbnail((294, 166))
            x, y = (i % 5)*300, (i // 5)*192
            sheet.paste(im, (x, y))
            draw.text((x+5, y+167), f"{i+1:02d}", fill=INK)
    sheet.save(out / "contact-sheet.png")
    for path, before in sources_before.items():
        if sha(path) != before:
            raise ValueError(f"Source changed during build: {path}")
    receipt = dict(status="built", main_slides=25, backup_slides=5,
                   target_seconds=sum(s["seconds"] for s in SLIDES),
                   main_script_words=sum(words(s["notes"]) for s in SLIDES if s["seconds"]),
                   included_pause_seconds=sum(s.get("pause_seconds", 0) for s in SLIDES),
                   model_calls=0, gpu_seconds=0, new_fits=0, headline_checks=headline_checks,
                   input_hashes=sources_before, example_source_hashes=example_inputs,
                   plotted_vector_hashes=vector_sources, selected_examples=selected,
                   generator_hashes={str(Path(__file__)): sha(__file__),
                                     str(ROOT / "aw/colleague_deck_content.py"): sha(ROOT / "aw/colleague_deck_content.py")},
                   outputs={str(p): sha(p) for p in sorted(out.rglob("*")) if p.is_file()})
    (LOGS / "build.json").write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
    (LOGS / "plotted-values.json").write_text(json.dumps(values, indent=2, ensure_ascii=False) + "\n")
    (LOGS / "layout.json").write_text(json.dumps(deck.checks, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"pdf": str(out / f"{STEM}.pdf"), "main_slides": 25, "backup": 5,
                      "target": clock(receipt["target_seconds"]), "words": receipt["main_script_words"]}))


if __name__ == "__main__":
    main()
