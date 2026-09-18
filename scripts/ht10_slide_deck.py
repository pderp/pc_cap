"""Build twelve presentation slides from the audited outline; no new experiments.

Use the existing status-paper plotting environment (ReportLab and Pillow).
All source/figure hashes are checked. New canonical documents stay in pc_cap;
portable presentation exports, including the PDF, go to assets.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT.parent / "assets/presentation-materials"
OUTLINE = ROOT / "docs/presentation/talk_outline_v1.md"
MANIFEST = ROOT / "logs/r1_round37/HT9-evidence-manifest.json"
FIGURES = ASSETS / "figures/ht9-v1"
SUBMITTED_TITLE = ("Coupled Active Inference on a Frozen Transformer Prior: "
                   "A Risk-Aware Residual Agent for Non-Equilibrium Regimes")
DEC054 = ("Preliminary hints at what the architecture could provide; not the coupled free energy "
          "(no coupled expectation or changed inference distribution), not a coupled Markov blanket, "
          "and not a test of the one-κ conjecture that porosity and interference are the same parameter.")
# Every numerical statement below is already in the bound outline. Notes are
# copied verbatim from its rows; the deck cannot omit their qualifications.
CONTENT = [
    dict(title="Where correction helps — and what the mean hides", kind="opening", label="RESEARCH PROGRAMME → CURRENT EXPERIMENTS",
         submitted_title=SUBMITTED_TITLE,
         points=["Charlie Derr · Matthew Iklé", "October 15, 2026 · Binghamton satellite",
                 "A frozen language model. A small adaptive memory. Controlled tests of correction and unintended interference."],
         foot="Development evidence, September 18 snapshot. The submitted abstract describes the broader programme."),
    dict(title="The system we actually built", kind="diagram", label="IMPLEMENTED IN JAX",
         points=["Frozen GPT-2 base (~124M parameters)", "3,348,228 trained reader/controller parameters (~2.7%)",
                 "Separate per-record memory state", "Gate acceptance ≠ nonzero residual ≠ changed answer"],
         foot="Interfaces are architectural analogies. Freezing weights proves neither a Markov blanket nor universal preservation."),
    dict(title="Retention and rejection compete", figure="selection_retention_rejection.png", label="ADAPTIVE DEVELOPMENT SELECTION",
         points=["42 candidates · 15 admissible", "Selected v5 macro RET-GS: 0.8033", "zsRE .98 · CounterFact .82 · MQuAKE .61",
                 "Unseen gate acceptance: 10/100", "Fixed-candidate Wilson 95%: 5.52–17.44%"],
         foot="Development selection, not confirmation. The interval is not selection-adjusted and does not certify a rate below 10%."),
    dict(title="A small average can hide a large local loss", figure="mean_vs_tail_v5.png", label="FIXED 128-WINDOW DEVELOPMENT ASSAY",
         points=["zsRE mean signed ΔNLL: .00220 nats", "ES95 positive harm: .04396 nats", "Worst position: 8.69 nats",
                 "17 of 16,256 positions exceed .1 nat", "+8 nats ≈ 3,000× less likely target token"],
         foot="Rare concentrated harm; no power-law or tail-exponent claim. Positions are dependent; saved profiles are not independent replications."),
    dict(title="Complete validation sharpens the picture", figure="full-fidelity-and-tail.png", label="245,237 FIXED POSITIONS · 300 DEVELOPMENT EDITS",
         points=["Learned MQuAKE: mean KL .005544", "Learned zsRE: mean KL .002270", "Both exceed the .001 KL benchmark",
                 "zsRE v0: mean KL .000789", "Yet its worst ΔNLL is 16.159 nats"],
         foot="DEC-064: cap benchmarks are secondary labels, without an admission veto. Continued-base certification is separate. Fixed windows are not iid."),
    dict(title="Three failures changed the investigation", kind="timeline", label="RETROSPECTIVE DEVELOPMENT LESSONS",
         points=["Reader fires too widely → explicit null / rejection training",
                 "Occupancy and source confounding → common-population qualification",
                 "Benign-looking averages → per-position tails and complete validation"],
         foot="No randomized isolation of each repair. Investigators chose these audits; the agent did not perform expected-free-energy action selection."),
    dict(title="A small, specified κ intervention", kind="objective", label="LOSS-LEVEL PILOT · THREE SEEDS",
         points=["Answer surprisal: (1 − p^κ) / κ", "κ → 0 gives ordinary −log p", "κ = .2 and .5; ordinary and clip-2 controls",
                 "Fixed checkpoint average: 150–300", "Only the answer term is bounded; not the whole objective or all gradients"],
         foot=DEC054),
    dict(title="The κ pilot did not meet its success rule", figure="kappa-tradeoff.png", label="DESCRIPTIVE TRADE-OFF, NOT A DECLARED GAIN",
         points=["RET-GS: ordinary .7961", "κ .2: .7544 · κ .5: .7478", "Predeclared retention floor: .7761",
                 "Both κ arms fail retention and tail separation", "Clip2 keeps retention; fails separation and adds a CounterFact false fire"],
         foot=DEC054),
    dict(title="Correct answers can conceal probability harm", figure="stress-trajectories.png", label="DEVELOPMENT STRESS PANEL · ONE SEED",
         points=["All 20 old exact answers remain correct", "CounterFact at edit 100:", "Mean positive ΔNLL .32379", "Maximum 12.53188 nats",
                 "Harm persists through the last observation"],
         foot="One seed, two schedules, measured probes only. Recovery is unobserved, not impossible or permanent; equal schedules do not prove order invariance."),
    dict(title="What independent confirmation can establish", kind="scope", label="PLANNED D.4 MATRIX · NO CONFIRMATORY RESULTS SHOWN",
         points=["zsRE: 120 core cells", "CounterFact: 120 core cells", "MQuAKE: 45 core cells at 300 edits",
                 "285 core + 45 optional cells", "MQuAKE core: primary v5, random reader, v0 stable"],
         foot="75 MQuAKE cells are prospectively omitted, not measured zeros. Keep 63 intervals, including 21 unavailable MQ1000 intervals. S1 is not exact-v5 compute matched."),
    dict(title="Headroom is conditional; October 9 is the stop", kind="budget", label="PLANNING SCENARIOS, NOT MEASURED PROGRESS",
         points=["431.31 expected process-hours", "646.96 at every cell ceiling", "750 shared process-hour cap", "≈227.30 elapsed hours at assumed 1.65× throughput",
                 "October 10–14: locked-data analysis, figures, rehearsal"],
         foot="Process-hours include both workers and failures; they are not elapsed hours. Transfers and memory limits are incompletely measured. Cost unsigned at outline snapshot."),
    dict(title="What would distinguish a coupled objective?", kind="closing", label="A QUESTION FOR THE ROOM",
         points=["Measured: concentrated harm and loss-level trade-offs", "Proposed: coupled expectations and correlated-regime adaptation",
                 "Test: improve the correction–tail-harm trade-off beyond clipping and better rejection training, while preserving retention"],
         foot="Preliminary hints, not coupled free energy or a test of the one-κ conjecture. The present null neither refutes nor confirms the broader programme."),
]


def ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=hashlib.sha256(path.read_bytes()).hexdigest())


def slides():
    manifest = json.loads(MANIFEST.read_text())
    bindings = [manifest["canonical_outline"], *manifest["sources"], *manifest["exports"]]
    # HT9 exports include a destination binding nested in some manifest versions.
    checked = []
    for b in bindings:
        if "path" not in b:
            b = b.get("export", b.get("destination"))
        if not isinstance(b, dict) or ref(b["path"]) != b:
            raise ValueError("HT9 evidence binding changed: " + str(b))
        checked.append(b)
    raw = OUTLINE.read_text()
    section = raw.split("## Slide-by-slide outline", 1)[1].split("## Figures,", 1)[0]
    rows = re.findall(r"^### (\d+)\. (.*?) — ([^\n]+)\n(.*?)(?=^### |\Z)", section, re.M | re.S)
    if [int(r[0]) for r in rows] != list(range(1, 13)) or len(CONTENT) != 12:
        raise ValueError("expected exactly twelve ordered outline rows")
    values = []
    for content, (number, title, duration, notes) in zip(CONTENT, rows, strict=True):
        if "**Qualification" not in notes or "**Evidence / figure:**" not in notes:
            raise ValueError("every slide needs qualifications and evidence")
        value = dict(content, number=int(number), outline_title=title,
                     suggested_duration=duration, speaker_notes=notes.strip())
        if "figure" in value:
            binding = ref(FIGURES / value["figure"])
            if binding not in checked:
                raise ValueError("figure is not in checked HT9 exports")
            value["figure_binding"] = binding
        values.append(value)
    return values, checked


def markdown(values):
    parts = ["<!-- HT-10 · evidence snapshot September 18, 2026 · 12 slides · development, not confirmation -->"]
    for s in values:
        bits = [f"# {s['number']}. {s['title']}", s["label"],
                "\n".join("- " + point for point in s["points"])]
        if s.get("submitted_title"):
            bits.insert(2, "Submitted title: *" + s["submitted_title"] + "*")
        if s.get("figure"):
            bits.append(f"![{s['outline_title']}]({s['figure_binding']['path']})")
        bits += ["> " + s["foot"], "Note:\n" + s["speaker_notes"]]
        parts.append("\n\n".join(bits))
    return "\n\n---\n\n".join(parts) + "\n"


def html_deck(values):
    sections = []
    for s in values:
        points = "".join("<li>" + html.escape(p) + "</li>" for p in s["points"])
        subtitle = ("<p class='subtitle'>" + html.escape(s["submitted_title"]) + "</p>"
                    if s.get("submitted_title") else "")
        figure = ""
        if s.get("figure"):
            data = base64.b64encode(Path(s["figure_binding"]["path"]).read_bytes()).decode()
            figure = f'<img alt="{html.escape(s["outline_title"])}" src="data:image/png;base64,{data}">'
        diagram = ""
        if s.get("kind") == "diagram":
            diagram = '<div class="diagram">Supplied fact → residual write → memory records<br>New query + frozen prior + memory → learned retrieval / null gate<br>→ selected residual or unchanged base<hr>Proposed: coupled objective and active audit policy (future work)</div>'
        sections.append(f'''<section aria-label="Slide {s['number']}"><small>{html.escape(s['label'])}</small>
<h1>{html.escape(s['title'])}</h1>{subtitle}<div class="body {'with-figure' if figure else ''}"><ul>{points}</ul>{figure}{diagram}</div>
<footer>{html.escape(s['foot'])}<span>{s['number']} / 12</span></footer>
<aside class="notes"><h2>Speaker notes · {s['suggested_duration']}</h2><pre>{html.escape(s['speaker_notes'])}</pre></aside></section>''')
    return '''<!doctype html><html lang="en"><meta charset="utf-8"><title>Controlled memory edits and concentrated harm — Charlie Derr</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#192e36;color:#142e37;font-family:system-ui,sans-serif}
section{display:none;background:#fafaf7;position:relative;width:min(100vw,177.78vh);height:min(56.25vw,100vh);margin:auto;padding:3%;overflow:auto}
section.active{display:block}small{color:#126a70;font-weight:700;letter-spacing:.12em;font-size:clamp(9px,1.1vw,18px)}
h1{font-size:clamp(20px,3.2vw,52px);line-height:1.15;margin:.4em 0 .65em;max-width:95%}.body{font-size:clamp(12px,1.9vw,30px)}.subtitle{font-size:clamp(12px,1.7vw,27px);color:#126a70}
ul{padding-left:1.2em;margin:0}li{margin:.5em 0}.with-figure{display:grid;grid-template-columns:34% 64%;gap:2%;align-items:center;font-size:clamp(11px,1.55vw,24px)}img{width:100%;max-height:54vh;object-fit:contain}
footer{position:absolute;bottom:3%;left:3%;right:3%;border-top:2px solid #b8492e;padding-top:.7em;font-size:clamp(8px,1.04vw,16px);line-height:1.3;padding-right:4%}footer span{float:right}.diagram{margin-top:1em;border:2px solid #126a70;padding:.8em;font-size:.8em}
.notes{display:none}.show-notes .notes{display:block;position:fixed;z-index:3;inset:12%;padding:2em;overflow:auto;background:white;border:3px solid #126a70;box-shadow:0 0 0 100vmax #0008}.notes pre{white-space:pre-wrap;font-family:inherit;font-size:16px;line-height:1.5}
nav{position:fixed;bottom:0;right:0;z-index:4;font:12px system-ui;background:#fff9}button{font:inherit}
@media print{section,section.active{display:block;width:100vw;height:56.25vw;break-after:page}nav{display:none}.notes{display:none!important}@page{size:landscape;margin:0}}
</style><nav><button id="prev">←</button><button id="next">→</button><button id="notes">Notes (N)</button></nav>
''' + "\n".join(sections) + '''
<script>
const slides=[...document.querySelectorAll('section')];let i=0;
function show(n){slides[i].classList.remove('active');i=Math.max(0,Math.min(slides.length-1,n));slides[i].classList.add('active');location.hash=i+1;}
document.querySelector('#prev').onclick=()=>show(i-1);document.querySelector('#next').onclick=()=>show(i+1);
document.querySelector('#notes').onclick=()=>document.body.classList.toggle('show-notes');
document.addEventListener('keydown',e=>{if(['ArrowRight','PageDown',' '].includes(e.key)){e.preventDefault();show(i+1)}if(['ArrowLeft','PageUp'].includes(e.key)){e.preventDefault();show(i-1)}if(e.key.toLowerCase()==='n')document.body.classList.toggle('show-notes')});
show((parseInt(location.hash.slice(1))||1)-1);
</script></html>'''


def pdf(values, path):
    if Path(path).exists():
        raise FileExistsError("new PDF path required")
    from matplotlib import get_data_path
    from reportlab.lib import colors
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Paragraph

    fonts = Path(get_data_path()) / "fonts/ttf"
    pdfmetrics.registerFont(TTFont("Deck", str(fonts / "DejaVuSans.ttf")))
    pdfmetrics.registerFont(TTFont("DeckBold", str(fonts / "DejaVuSans-Bold.ttf")))
    c = canvas.Canvas(str(path), pagesize=(960, 540), pageCompression=1)
    c.setTitle("Controlled memory edits, concentrated harm, and a loss-level κ pilot")
    c.setAuthor("Charlie Derr and Matthew Iklé")
    c.setSubject("September 18 development evidence snapshot; October 15 presentation draft")
    ink, teal, rust = map(colors.HexColor, ("#142e37", "#126a70", "#b8492e"))

    def paragraph(value, x, top, width, size=19, color=ink, bold=False):
        style = ParagraphStyle("deck", fontName="DeckBold" if bold else "Deck", fontSize=size,
                               leading=size * 1.28, textColor=color)
        p = Paragraph(html.escape(value), style)
        _, h = p.wrap(width, 1000)
        p.drawOn(c, x, top - h)
        return h

    def card(label, x, y, width=260, height=58, dashed=False):
        c.setFillColor(colors.HexColor("#edf4f2"))
        c.setStrokeColor(teal)
        c.setDash(5, 3) if dashed else c.setDash()
        c.roundRect(x, y, width, height, 9, stroke=1, fill=1)
        c.setDash()
        paragraph(label, x + 12, y + height - 12, width - 24, size=15)

    for s in values:
        c.setFillColor(colors.HexColor("#fafaf7"))
        c.rect(0, 0, 960, 540, fill=1, stroke=0)
        paragraph(s["label"], 36, 512, 888, size=10, color=teal, bold=True)
        title_height = paragraph(s["title"], 36, 481, 888, size=29, bold=True)
        top = 473 - title_height
        footer_size = 10 if s["number"] in (7, 8) else 10.5
        # Bottom strip always contains the scientific qualification, including
        # the complete DEC-054 wording on both κ slides.
        paragraph(s["foot"], 36, 66, 855, size=footer_size)
        c.setStrokeColor(rust)
        c.line(36, 76, 924, 76)
        paragraph(f"{s['number']:02d} / 12", 882, 34, 70, size=9)
        if s.get("figure"):
            y = top - 10
            for point in s["points"]:
                y -= paragraph(point, 36, y, 264, size=17.5) + 15
            if y < 85:
                raise ValueError("left column overflows slide " + str(s["number"]))
            c.drawImage(s["figure_binding"]["path"], 318, 94, width=606, height=top - 102,
                        preserveAspectRatio=True, anchor="c", mask="auto")
        elif s.get("kind") == "diagram":
            y = top - 2
            for point in s["points"]:
                y -= paragraph(point, 36, y, 320, size=18) + 16
            card("Supplied fact → residual write", 385, 350, 250)
            card("Per-record memory", 671, 350, 250)
            card("New query + frozen prior + memory", 385, 260, 536)
            card("Learned retrieval / null gate → residual or unchanged base", 385, 170, 536)
            card("Proposed coupled objective and active audits", 385, 93, 536, 53, True)
            c.setStrokeColor(teal)
            for x1, y1, x2, y2 in ((635, 379, 668, 379), (795, 348, 795, 320), (650, 258, 650, 231)):
                c.line(x1, y1, x2, y2)
        else:
            y = top - 13
            if s["number"] == 1:
                y -= paragraph(s["submitted_title"], 36, y, 880, size=20, color=teal) + 22
            for point in s["points"]:
                size = 23 if s["number"] in (6, 12) else 22
                y -= paragraph(point, 36, y, 862, size=size) + 18
            if y < 80:
                raise ValueError("slide content overflows " + str(s["number"]))
        # A PDF reader's note icon exposes the complete qualification/evidence.
        c.textAnnotation(s["speaker_notes"], Rect=(918, 488, 932, 502), Name="Comment")
        c.showPage()
    c.save()


def build(canonical, export):
    canonical, export = Path(canonical).resolve(), Path(export).resolve()
    if not canonical.is_relative_to(ROOT / "docs/presentation") or not export.is_relative_to(ASSETS):
        raise ValueError("canonical docs belong in repo; exports in presentation assets")
    if canonical.exists() or export.exists():
        raise FileExistsError("new deck directories required")
    values, evidence = slides()
    canonical.mkdir(parents=True, exist_ok=False)
    export.mkdir(parents=True, exist_ok=False)
    documents = {"slides.json": json.dumps(values, ensure_ascii=False, indent=2) + "\n",
                 "slides.md": markdown(values), "index.html": html_deck(values),
                 "speaker-notes.md": "# Full speaker notes and qualifications\n\n" + "\n\n".join(
                     f"## {s['number']}. {s['outline_title']}\n\n{s['speaker_notes']}" for s in values)}
    for name, content in documents.items():
        with (canonical / name).open("x") as f:
            f.write(content)
        shutil.copyfile(canonical / name, export / name)
    pdf(values, export / "current-research-deck.pdf")
    for b in evidence:
        if ref(b["path"]) != b:
            raise ValueError("source changed while rendering")
    report = dict(task="HT-10", slides=12, new_experiments=0, gpu_seconds=0,
                  snapshot="2026-09-18; development results, confirmation status as in outline",
                  outline=ref(OUTLINE), ht9_manifest=ref(MANIFEST), producer=ref(__file__),
                  evidence=evidence, canonical=[ref(p) for p in sorted(canonical.iterdir())],
                  exports=[ref(p) for p in sorted(export.iterdir())],
                  qualification_policy="Verbatim outline rows in Markdown/HTML notes and PDF annotations; short limits on all slides; complete DEC-054 on slides 7 and 8",
                  remaining="Replace slides 10–11 with actual October 9 inventory/costs; final ledger v6 awaits signed cost; lead restyling and timing review")
    with (canonical / "build-manifest.json").open("x") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--canonical", type=Path, default=ROOT / "docs/presentation/deck_v1")
    p.add_argument("--export", type=Path, default=ASSETS / "deck_v1")
    a = p.parse_args()
    report = build(a.canonical, a.export)
    print(json.dumps({k:report[k] for k in ("task", "slides", "new_experiments", "exports")}, indent=2))


if __name__ == "__main__":
    main()
