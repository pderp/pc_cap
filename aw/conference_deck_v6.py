"""Build the separate 15-slide deck from Markdown and saved results; CPU only.

Run: ../assets/envs/status-paper-20260911/bin/python -m aw.conference_deck_v6
PDF and native editable PPTX share a drawing list and the same wrapped text.
"""
from __future__ import annotations

import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

import numpy as np
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.graphics.barcode.qr import QrCodeWidget

from aw.focused_long_deck import parse, strings, tokens

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT.parent / 'assets/presentation-materials/deck_v6'
LOG = ROOT / 'logs/presentation/deck_v6'
W, H = 1280, 720
BG, INK, MUTED = '#FAFAF7', '#162F3B', '#52666F'
TEAL, RUST, PURPLE, GRID = '#007E80', '#B44D32', '#675399', '#D8E1E2'
PALE, WHITE = '#EAF3F1', '#FFFFFF'
FILES = {
    'triplet': ROOT / 'logs/R1/reports/triplet/summary.json',
    'tails': ROOT / 'logs/additional_work/HT-17/snapshot-20261004-complete/report.json',
    'depth': ROOT / 'logs/additional_work/PC-v0/controls-report-20260929/report.json',
    'reader': ROOT / 'logs/additional_work/PC-reader/report-round63-final/report.json',
    'credit': ROOT / 'docs/additional_work/PC-v1_report.md',
    'extension': ROOT / 'docs/additional_work/R_report.md',
    'mixture': ROOT / 'docs/additional_work/AW-B_report.md',
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def pct(value, places=1):
    return f'{100 * value:.{places}f}%'


def load_and_check(slides):
    data = {key: json.loads(p.read_text()) for key, p in FILES.items() if p.suffix == '.json'}
    checks = []

    def table(number, expected):
        actual = [row[1:] for row in slides[number-1]['table'][1:]]
        assert actual == expected, (number, actual, expected)
        checks.append({'slide': number, 'verified_table': expected})

    result = []
    for ds in ['zsre', 'counterfact', 'mquake']:
        row = []
        for cond, metric in [('v0_stable', 'RET-ES'), ('v0_stable', 'RET-GS'), ('R1_learned_ff', 'RET-GS')]:
            groups = [g for g in data['triplet']['groups'] if g['dataset'] == ds and g['condition'] == cond]
            assert len(groups) == 3
            value = np.mean([np.mean(g['primary'][metric]) for g in groups])
            row.append(f'{100*value:.0f}%' if value in (0, 1) else f'{100*value:.2f}%')
        result.append(row)
    table(6, result)
    fidelity = [v for g in data['triplet']['groups'] if g['condition'] == 'R1_learned_ff'
                for v in g['fidelity']['capoff']['mean_kl']]
    assert len(fidelity) == 45 and all(v > .001 for v in fidelity)
    checks.append({'slide': 7, 'fidelity_failures': len(fidelity), 'threshold': .001})

    report = FILES['credit'].read_text()

    def rows(section):
        block = report.split(section, 1)[1].split('\n## ', 1)[0]
        return [[v.strip() for v in line.strip('|').split('|')] for line in block.splitlines()
                if line.startswith(('| zsre |', '| counterfact |'))]

    result = []
    for e, c, h in zip(rows('## Checkpoint 300'), rows('## Acquisition and evaluation cost'),
                       rows('## Ordinary-text harm and cost')[:4], strict=True):
        assert e[:2] == c[:2] == h[:2]
        result.append(['Adjoint' if e[1] == 'SE-A' else 'Error inference', pct(float(e[4])),
                       f'{float(c[3]):.0f} s', f'{float(h[7]):.2f} nats'])
    table(9, result)
    result = []
    lower = 0
    for ds in ['zsre', 'counterfact']:
        for seed in range(3):
            pair = [next(c for c in data['reader']['cells'] if c['dataset'] == ds and c['seed'] == seed
                         and c['rule'] == rule)['metrics']['RET-GS']['value'] for rule in ['bp', 'epc']]
            result.append([pct(v) for v in pair])
            lower += pair[1] < pair[0]
    table(10, result)
    assert lower == 5
    result = []
    for depth, arm in [(1, 'SE-A'), (1, 'SE-E'), (8, 'SE-E'), (32, 'SE-E')]:
        row = next(x for x in data['depth']['summary'] if x['dataset'] == 'zsre'
                   and x['depth'] == depth and x['arm'] == arm)
        result.append([pct(row['metrics']['RET-ES']), pct(row['metrics']['RET-GS']),
                       f"{row['learning_seconds']/60:.1f} min"])
    table(11, result)
    result = []
    for ds in ['zsre', 'counterfact']:
        result.append([f"{next(g for g in data['tails']['groups'] if g['phase'] == 'AW-B' and g['dataset'] == ds and g['condition'] == cond)['thresholds']['0.01']['conditional_mean_loss']:.3f} nats"
                       for cond in ['v5', 'mixture:0.367879']])
    table(13, result)
    assert '44.07 percentage points' in FILES['extension'].read_text()
    assert '56.20 percentage points' in FILES['extension'].read_text()
    assert len(slides) == 15
    assert sum(int(s['meta']['seconds']) for s in slides) == 1080
    return data, checks


class Page:
    def __init__(self, slide, number, data):
        self.s, self.number, self.data = slide, number, data
        self.commands, self.printed, self.boxes, self.errors = [], [], [], []

    def rect(self, x, y, w, h, fill, radius=0):
        self.commands.append(dict(kind='rect', x=x, y=y, w=w, h=h, fill=fill, radius=radius))

    def path(self, points, color=TEAL, width=2, dash=False):
        if len(points) >= 2:
            self.commands.append(dict(kind='path', points=points, color=color, width=width, dash=dash))

    def arrow(self, x1, y1, x2, y2, color=TEAL):
        self.path([(x1, y1), (x2, y2)], color, 2.4)
        angle = math.atan2(y2-y1, x2-x1)
        for offset in [-.45, .45]:
            self.path([(x2-11*math.cos(angle+offset), y2-11*math.sin(angle+offset)), (x2, y2)], color, 2.4)

    def wrap(self, text, width, size, bold):
        font = 'DeckBold' if bold else 'Deck'
        lines = []
        for paragraph in text.split('\n'):
            line = ''
            for word in paragraph.split():
                if pdfmetrics.stringWidth(word, font, size) > width:
                    self.errors.append(f'unbreakable word too wide: {word}')
                test = f'{line} {word}'.strip()
                if line and pdfmetrics.stringWidth(test, font, size) > width:
                    lines.append(line)
                    line = word
                else:
                    line = test
            lines.append(line)
        return lines

    def text(self, value, x, y, width, size=24, bold=False, color=INK, max_h=None, link=None):
        lines = self.wrap(value, width, size, bold)
        leading = size * 1.25
        height = len(lines)*leading
        if max_h is not None and height > max_h + .1:
            self.errors.append(f'height {height:.1f}>{max_h}: {value}')
        self.printed.append(value)
        for i, line in enumerate(lines):
            command = dict(kind='text', text=line, x=x, y=y+i*leading, w=width, h=leading,
                           size=size, bold=bold, color=color, link=link)
            self.commands.append(command)
            actual_w = pdfmetrics.stringWidth(line, 'DeckBold' if bold else 'Deck', size)
            box = [x, y+i*leading, x+actual_w, y+i*leading+size*1.05]
            self.boxes.append({'text': line, 'bounds': box, 'size': size})
            if box[0] < 0 or box[1] < 0 or box[2] > W or box[3] > H:
                self.errors.append(f'off-slide text: {line}')
        return height

    def stack(self, values, x, y, w, size=23, gap=12, **kw):
        for value in values:
            y += self.text(value, x, y, w, size, **kw) + gap
        return y

    def frame(self, dark=False):
        self.rect(0, 0, W, H, INK if dark else BG)
        self.rect(0, 0, W, 7, TEAL)
        self.text(self.s['section'], 54, 28, 1172, 14, True, '#9ADFD4' if dark else TEAL)
        self.text(self.s['title'], 54, 67, 1172, 35, True, WHITE if dark else INK, max_h=90)
        self.rect(54, 614, 1172, 60, '#204955' if dark else PALE, 9)
        self.text(self.s['takeaway'], 72, 625, 1136, 21, True, WHITE if dark else INK, max_h=53)
        self.text(self.s['source'], 55, 692, 1080, 10.5, color='#C3D8DC' if dark else MUTED)
        self.text(self.s['meta']['page'], 1145, 692, 85, 12, color='#C3D8DC' if dark else MUTED)

    def table(self, rows, x, y, widths, row_h=55, header_h=64, size=22, header_size=17, accent_col=None):
        width = sum(widths)
        self.rect(x, y, width, header_h, INK, 5)
        for r, row in enumerate(rows):
            top = y if r == 0 else y+header_h+(r-1)*row_h
            height = header_h if r == 0 else row_h
            if r > 0:
                self.rect(x, top, width, height, WHITE if r % 2 else '#EEF3F3')
                self.path([(x, top+height), (x+width, top+height)], GRID, .7)
            left = x
            for c, (value, cell_w) in enumerate(zip(row, widths, strict=True)):
                fs = header_size if r == 0 else size
                bold = r == 0 or c == accent_col
                lines = self.wrap(value, cell_w-26, fs, bold)
                used = len(lines)*fs*1.25
                self.text(value, left+13, top+(height-used)/2, cell_w-26, fs, bold,
                          WHITE if r == 0 else TEAL if c == accent_col else INK, max_h=height-8)
                left += cell_w
        return y+header_h+(len(rows)-1)*row_h

    def card(self, card, x, y, w, h, color=TEAL, body_size=24):
        self.rect(x, y, w, h, WHITE, 8)
        self.rect(x, y, 5, h, color)
        used = self.text(card['title'], x+23, y+20, w-46, 25, True, color)
        self.stack(card['body'], x+23, y+30+used, w-46, body_size, 8)

    def cover(self):
        self.rect(0, 0, W, H, INK)
        self.rect(950, 0, 330, H, '#204955')
        for i in range(6):
            self.rect(989+i*21, 240+i*28, 115, 115, '#28606A', 12)
        self.rect(56, 50, 74, 6, '#79DCC8')
        self.text(self.s['section'], 55, 84, 1110, 18, True, '#9ADFD4')
        self.text(self.s['title'], 55, 150, 945, 58, True, WHITE, max_h=150)
        self.text(self.s['intro'][0], 59, 334, 940, 31, color='#A9E2D9')
        self.text(self.s['intro'][1], 59, 437, 1030, 29, color=WHITE)
        self.text(self.s['intro'][2], 59, 487, 1060, 22, color='#C3D8DC')
        self.text(self.s['takeaway'], 59, 590, 1110, 25, True, WHITE, max_h=70)
        self.text(self.s['source'], 59, 692, 1030, 11, color='#C3D8DC')
        self.text(self.s['meta']['page'], 1145, 692, 85, 12, color='#C3D8DC')

    def question(self):
        self.text(self.s['intro'][0], 56, 170, 1165, 29, max_h=82)
        for i, c in enumerate(self.s['cards']):
            self.card(c, 56+i*398, 285, 374, 266, [TEAL, PURPLE, RUST][i])

    def architecture(self):
        self.text(self.s['intro'][0], 56, 163, 1160, 25, max_h=66)
        self.card(self.s['cards'][0], 56, 268, 520, 212)
        self.card(self.s['cards'][1], 704, 268, 520, 212, PURPLE)
        self.arrow(596, 340, 683, 340)
        self.arrow(683, 408, 596, 408, PURPLE)
        self.stack(self.s['post'], 59, 511, 1160, 23, 8)

    def readers(self):
        bottom = self.table(self.s['table'], 56, 179, [270, 898], row_h=91, header_h=50, size=25, header_size=21)
        self.stack(self.s['post'], 59, bottom+26, 1160, 23)

    def procedure(self):
        self.text(self.s['intro'][0], 56, 164, 1168, 26)
        self.table(self.s['table'], 56, 273, [305, 191], row_h=60, header_h=64, size=25, header_size=20)
        self.card(self.s['cards'][0], 580, 257, 644, 134, body_size=23)
        self.card(self.s['cards'][1], 580, 408, 644, 148, PURPLE, body_size=23)
        self.stack(self.s['post'], 58, 572, 1166, 18)

    def retention(self):
        end = self.table(self.s['table'], 56, 180, [326, 277, 277, 288], row_h=76, header_h=88,
                         size=27, header_size=21, accent_col=3)
        self.text(self.s['post'][0], 60, end+21, 1160, 20)
        self.text(self.s['post'][1], 60, end+60, 1160, 21, max_h=58)

    def preservation(self):
        for i, c in enumerate(self.s['cards']):
            self.card(c, 56+i*398, 194, 374, 313, [RUST, PURPLE, TEAL][i], body_size=24)
        self.stack(self.s['post'], 59, 549, 1160, 23)

    def credit(self):
        self.text(self.s['intro'][0], 56, 168, 1165, 26)
        self.card(self.s['cards'][0], 56, 245, 566, 248, TEAL, body_size=25)
        self.card(self.s['cards'][1], 647, 245, 577, 248, PURPLE, body_size=25)
        self.stack(self.s['post'], 58, 522, 1165, 22, 10)

    def acquisition(self):
        end = self.table(self.s['table'], 56, 186, [203, 228, 230, 219, 288], row_h=66, header_h=74,
                         size=25, header_size=20)
        self.stack(self.s['post'], 59, end+25, 1160, 22)

    def reader_training(self):
        self.table(self.s['table'], 56, 186, [268, 190, 190], row_h=55, header_h=58,
                   size=24, header_size=21, accent_col=2)
        self.card(self.s['cards'][0], 735, 186, 489, 173, RUST, body_size=24)
        self.card(self.s['cards'][1], 735, 382, 489, 192, PURPLE, body_size=23)

    def settling(self):
        end = self.table(self.s['table'], 56, 175, [390, 260, 260, 258], row_h=59, header_h=61,
                         size=25, header_size=22)
        self.text(self.s['post'][0], 59, end+21, 1160, 21)
        self.text(self.s['post'][1], 59, end+70, 1160, 20, max_h=57)

    def survival(self):
        self.text(self.s['intro'][0], 56, 158, 1170, 22, max_h=61)
        self.text(self.s['post'][1], 58, 224, 1150, 18, color=MUTED)
        top, bottom, width = 287, 486, 454
        for i, (card, condition) in enumerate(zip(self.s['cards'], ['R1_learned_ff', 'v0_stable'], strict=True)):
            color, left = (TEAL if i == 0 else RUST), 147+i*577
            self.text(card['title'], left, 253, width, 23, True, color)
            record = next(c for c in self.data['tails']['cells'] if c['phase'] == 'stage4'
                          and c['dataset'] == 'zsre' and c['condition'] == condition
                          and c['realization'] == 0 and c['order'] == 100)
            path = Path(record['vector']['path'])
            assert sha(path) == record['vector']['sha256']
            with np.load(path) as z:
                delta = (z['values'][..., 0]-z['values'][..., 1]).ravel()
            assert len(delta) == 245237
            labels = card['body']
            assert len(labels) == 9

            def tx(x):
                return left+width*(math.log10(x)-math.log10(.01))/(math.log10(35)-math.log10(.01))

            def ty(y):
                y = max(3e-6, min(.004, y))
                return top+(bottom-top)*(math.log10(.004)-math.log10(y))/(math.log10(.004)-math.log10(3e-6))

            for label in labels[2:6]:
                x = tx(float(label))
                self.path([(x, top), (x, bottom)], GRID, .8)
                self.text(label, x-17, bottom+9, 76, 17)
            for label in labels[6:]:
                y = ty(float(label[:-1])/100)
                self.path([(left, y), (left+width, y)], GRID, .8)
                self.text(label, left-82, y-9, 80, 17)
            values = np.sort(delta)
            xs = np.unique(np.r_[.01, delta[delta > .01]])
            ys = (len(delta)-np.searchsorted(values, xs, side='right'))/len(delta)
            points = [(tx(float(xs[0])), ty(float(ys[0])))]
            for x, prev, value in zip(xs[1:], ys[:-1], ys[1:], strict=True):
                points.extend([(tx(float(x)), ty(float(prev))), (tx(float(x)), ty(float(value)))])
            self.path(points, color, 2.4)
            stats = record['statistics']['thresholds']['0.01']
            grid = np.geomspace(.01, xs[-1], 160)
            fitted = stats['fraction'] * np.exp(-(grid-.01)/stats['exponential']['scale'])
            self.path([(tx(float(x)), ty(float(y))) for x, y in zip(grid, fitted, strict=True)], MUTED, 1.7, True)
            self.rect(left+6, bottom-70, 258, 61, BG)
            self.path([(left+13, bottom-51), (left+40, bottom-51)], color, 2.4)
            self.text(labels[0], left+47, bottom-61, 226, 16, color=color)
            self.path([(left+13, bottom-25), (left+40, bottom-25)], MUTED, 1.7, True)
            self.text(labels[1], left+47, bottom-35, 226, 16, color=MUTED)
        self.text(self.s['post'][0], 320, 531, 900, 22)
        self.text(self.s['post'][2], 59, 575, 1165, 18)

    def mixture(self):
        self.rect(56, 164, 1168, 92, PALE, 8)
        self.text(self.s['intro'][0], 77, 177, 1123, 27, True, TEAL)
        self.text(self.s['intro'][1], 77, 224, 1123, 21)
        end = self.table(self.s['table'], 135, 294, [420, 289, 289], row_h=58, header_h=49,
                         size=27, header_size=21, accent_col=2)
        self.text(self.s['post'][0], 59, end+20, 1160, 20)
        self.text(self.s['post'][1], 59, end+61, 1160, 22, max_h=60)

    def future(self):
        self.card(self.s['cards'][0], 56, 188, 464, 242, TEAL, body_size=26)
        self.card(self.s['cards'][1], 546, 188, 678, 242, PURPLE, body_size=28)
        self.text(self.s['post'][0], 59, 464, 1160, 24)
        self.text(self.s['post'][1], 59, 529, 1160, 23, max_h=67)

    def closing(self):
        self.frame(dark=True)
        p = self.s['intro']
        url = 'https://' + p[0]
        self.text(p[0], 58, 174, 832, 40, True, '#9ADFD4', link=url)
        self.text(p[1], 59, 233, 800, 22, color=WHITE)
        self.text(p[2], 59, 315, 815, 28, True, WHITE)
        self.text(p[3], 59, 362, 840, 20, color='#C3D8DC')
        for i, text in enumerate(p[4:]):
            link = ('https://' + text.split(': ', 1)[1]) if text.startswith(('Code:', 'Materials:')) else None
            self.text(text, 59, 420+i*40, 885, 19, color=WHITE, link=link)
        qr = QrCodeWidget(url)
        qr.qr.make()
        matrix = qr.qr.modules
        size, left, top = 257, 935, 237
        self.rect(left-20, top-20, size+40, size+40, WHITE, 10)
        unit = size/(len(matrix)+8)
        for y, row in enumerate(matrix):
            for x, black in enumerate(row):
                if black:
                    self.rect(left+(x+4)*unit, top+(y+4)*unit, unit+.08, unit+.08, '#111111')

    def render(self):
        kind = self.s['meta']['layout']
        if kind not in ['cover', 'closing']:
            self.frame()
        getattr(self, kind)()
        assert tokens(' '.join(self.printed)) == tokens(' '.join(strings(self.s) + [self.s['meta']['page']])), self.number
        for i, a in enumerate(self.boxes):
            for b in self.boxes[i+1:]:
                x0, y0, x1, y1 = a['bounds']
                u0, v0, u1, v1 = b['bounds']
                area = max(0, min(x1, u1)-max(x0, u0))*max(0, min(y1, v1)-max(y0, v0))
                if area > 2:
                    self.errors.append(f"overlapping text: {a['text']} / {b['text']}")
        return self


def write_pdf(pages, target):
    pdf = canvas.Canvas(str(target), pagesize=(W, H), pageCompression=1)
    pdf.setTitle('Predictive coding cap experiments — 15-slide conference version')
    pdf.setAuthor('charlie derr and Matthew Iklé')
    for page in pages:
        for c in page.commands:
            if c['kind'] == 'rect':
                pdf.setFillColor(HexColor(c['fill']))
                pdf.roundRect(c['x'], H-c['y']-c['h'], c['w'], c['h'], c['radius'], fill=1, stroke=0)
            elif c['kind'] == 'text':
                pdf.setFillColor(HexColor(c['color']))
                pdf.setFont('DeckBold' if c['bold'] else 'Deck', c['size'])
                pdf.drawString(c['x'], H-c['y']-c['size']*.83, c['text'])
                if c['link']:
                    pdf.linkURL(c['link'], (c['x'], H-c['y']-c['h'], c['x']+c['w'], H-c['y']), relative=0)
            else:
                pdf.setStrokeColor(HexColor(c['color']))
                pdf.setLineWidth(c['width'])
                pdf.setDash([7, 5] if c['dash'] else [])
                path = pdf.beginPath()
                path.moveTo(c['points'][0][0], H-c['points'][0][1])
                for x, y in c['points'][1:]:
                    path.lineTo(x, H-y)
                pdf.drawPath(path)
        pdf.showPage()
    pdf.save()


NS = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
REL = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/'
GROUP = '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>'


def emu(x):
    return round(x*12700)


def xml(body):
    return '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>' + body


def rels(entries):
    return xml('<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">' + ''.join(
        f'<Relationship Id="{rid}" Type="{REL}{typ}" Target="{escape(target)}"{extra}/>' for rid, typ, target, extra in entries) + '</Relationships>')


def shape(command, ident, hyperlink=None):
    c = command
    x, y = c.get('x', 0), c.get('y', 0)
    w, h = c.get('w', 0), c.get('h', 0)
    nv = f'<p:nvSpPr><p:cNvPr id="{ident}" name="{c["kind"]} {ident}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
    if c['kind'] == 'path':
        xs, ys = zip(*c['points'], strict=True)
        x, y, w, h = min(xs), min(ys), max(max(xs)-min(xs), .01), max(max(ys)-min(ys), .01)
        pts = [(emu(px-x), emu(py-y)) for px, py in c['points']]
        commands = f'<a:moveTo><a:pt x="{pts[0][0]}" y="{pts[0][1]}"/></a:moveTo>'
        commands += ''.join(f'<a:lnTo><a:pt x="{px}" y="{py}"/></a:lnTo>' for px, py in pts[1:])
        geom = f'<a:custGeom><a:avLst/><a:gdLst/><a:ahLst/><a:cxnLst/><a:rect l="0" t="0" r="r" b="b"/><a:pathLst><a:path w="{emu(w)}" h="{emu(h)}" fill="none">{commands}</a:path></a:pathLst></a:custGeom>'
        fill = '<a:noFill/>'
        line = f'<a:ln w="{emu(c["width"])}"><a:solidFill><a:srgbClr val="{c["color"][1:]}"/></a:solidFill><a:prstDash val="{"dash" if c["dash"] else "solid"}"/></a:ln>'
    else:
        geom = '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>'
        fill = f'<a:solidFill><a:srgbClr val="{c["fill"][1:]}"/></a:solidFill>' if c['kind'] == 'rect' else '<a:noFill/>'
        line = '<a:ln><a:noFill/></a:ln>'
    transform = f'<a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
    text = ''
    if c['kind'] == 'text':
        click = f'<a:hlinkClick r:id="{hyperlink}"/>' if hyperlink else ''
        run = f'<a:rPr lang="en-US" sz="{round(c["size"]*100)}" b="{int(c["bold"])}"><a:solidFill><a:srgbClr val="{c["color"][1:]}"/></a:solidFill><a:latin typeface="DejaVu Sans"/>{click}</a:rPr>'
        text = f'<p:txBody><a:bodyPr wrap="none" lIns="0" tIns="0" rIns="0" bIns="0" anchor="t"><a:noAutofit/></a:bodyPr><a:lstStyle/><a:p><a:pPr><a:lnSpc><a:spcPct val="100000"/></a:lnSpc><a:spcBef><a:spcPts val="0"/></a:spcBef><a:spcAft><a:spcPts val="0"/></a:spcAft></a:pPr><a:r>{run}<a:t>{escape(c["text"])}</a:t></a:r></a:p></p:txBody>'
    return f'<p:sp>{nv}<p:spPr>{transform}{geom}{fill}{line}</p:spPr>{text}</p:sp>'


def write_pptx(pages, notes, target):
    files = {}
    color_map = '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
    scheme = ''.join(f'<a:{name}><a:srgbClr val="{value}"/></a:{name}>' for name, value in [
        ('dk1', '162F3B'), ('lt1', 'FAFAF7'), ('dk2', '52666F'), ('lt2', 'EAF3F1'),
        ('accent1', '007E80'), ('accent2', 'B44D32'), ('accent3', '675399'), ('accent4', '316F9B'),
        ('accent5', '8AB1AD'), ('accent6', 'BACDD0'), ('hlink', '007E80'), ('folHlink', '675399')])
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    theme = f'<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Cap"><a:themeElements><a:clrScheme name="Cap">{scheme}</a:clrScheme><a:fontScheme name="Cap"><a:majorFont><a:latin typeface="DejaVu Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="DejaVu Sans"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme><a:fmtScheme name="Cap"><a:fillStyleLst>{solid*3}</a:fillStyleLst><a:lnStyleLst>{("<a:ln w=\"12700\">"+solid+"</a:ln>")*3}</a:lnStyleLst><a:effectStyleLst>{"<a:effectStyle><a:effectLst/></a:effectStyle>"*3}</a:effectStyleLst><a:bgFillStyleLst>{solid*3}</a:bgFillStyleLst></a:fmtScheme></a:themeElements></a:theme>'
    files['ppt/theme/theme1.xml'] = xml(theme)
    files['_rels/.rels'] = rels([('rId1', 'officeDocument', 'ppt/presentation.xml', '')])
    slideids = ''.join(f'<p:sldId id="{256+i}" r:id="rId{i+2}"/>' for i in range(len(pages)))
    files['ppt/presentation.xml'] = xml(f'<p:presentation {NS}><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst><p:notesMasterIdLst><p:notesMasterId r:id="rIdNotes"/></p:notesMasterIdLst><p:sldIdLst>{slideids}</p:sldIdLst><p:sldSz cx="{emu(W)}" cy="{emu(H)}"/><p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>')
    files['ppt/_rels/presentation.xml.rels'] = rels([
        ('rId1', 'slideMaster', 'slideMasters/slideMaster1.xml', ''),
        ('rIdNotes', 'notesMaster', 'notesMasters/notesMaster1.xml', ''),
        *[(f'rId{i+2}', 'slide', f'slides/slide{i+1}.xml', '') for i in range(len(pages))]])
    files['ppt/slideMasters/slideMaster1.xml'] = xml(f'<p:sldMaster {NS}><p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>{color_map}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst><p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles></p:sldMaster>')
    files['ppt/slideMasters/_rels/slideMaster1.xml.rels'] = rels([
        ('rId1', 'slideLayout', '../slideLayouts/slideLayout1.xml', ''), ('rId2', 'theme', '../theme/theme1.xml', '')])
    files['ppt/slideLayouts/slideLayout1.xml'] = xml(f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Blank"><p:spTree>{GROUP}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')
    files['ppt/slideLayouts/_rels/slideLayout1.xml.rels'] = rels([('rId1', 'slideMaster', '../slideMasters/slideMaster1.xml', '')])
    files['ppt/notesMasters/notesMaster1.xml'] = xml(f'<p:notesMaster {NS}><p:cSld><p:spTree>{GROUP}</p:spTree></p:cSld>{color_map}<p:notesStyle/></p:notesMaster>')
    files['ppt/notesMasters/_rels/notesMaster1.xml.rels'] = rels([('rId1', 'theme', '../theme/theme1.xml', '')])
    for n, page in enumerate(pages, 1):
        entries = [('rId1', 'slideLayout', '../slideLayouts/slideLayout1.xml', ''),
                   ('rId2', 'notesSlide', f'../notesSlides/notesSlide{n}.xml', '')]
        parts = []
        for ident, c in enumerate(page.commands, 2):
            linkid = None
            if c.get('link'):
                linkid = f'rId{len(entries)+1}'
                entries.append((linkid, 'hyperlink', c['link'], ' TargetMode="External"'))
            parts.append(shape(c, ident, linkid))
        files[f'ppt/slides/slide{n}.xml'] = xml(f'<p:sld {NS}><p:cSld><p:spTree>{GROUP}{"".join(parts)}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')
        files[f'ppt/slides/_rels/slide{n}.xml.rels'] = rels(entries)
        paragraphs = ''.join(f'<a:p><a:r><a:t>{escape(line)}</a:t></a:r></a:p>' for line in notes[n-1].split('\n'))
        body = f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notes"/><p:cNvSpPr txBox="1"/><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr><p:spPr/><p:txBody><a:bodyPr/><a:lstStyle/>{paragraphs}</p:txBody></p:sp>'
        files[f'ppt/notesSlides/notesSlide{n}.xml'] = xml(f'<p:notes {NS}><p:cSld><p:spTree>{GROUP}{body}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>')
        files[f'ppt/notesSlides/_rels/notesSlide{n}.xml.rels'] = rels([
            ('rId1', 'notesMaster', '../notesMasters/notesMaster1.xml', ''), ('rId2', 'slide', f'../slides/slide{n}.xml', '')])
    types = {'ppt/presentation.xml': 'presentation', 'ppt/slideMasters/slideMaster1.xml': 'slideMaster',
             'ppt/slideLayouts/slideLayout1.xml': 'slideLayout', 'ppt/notesMasters/notesMaster1.xml': 'notesMaster'}
    types.update({f'ppt/slides/slide{n}.xml': 'slide' for n in range(1, len(pages)+1)})
    types.update({f'ppt/notesSlides/notesSlide{n}.xml': 'notesSlide' for n in range(1, len(pages)+1)})
    overrides = ''.join(f'<Override PartName="/{path}" ContentType="application/vnd.openxmlformats-officedocument.presentationml.{kind}{".main" if kind == "presentation" else ""}+xml"/>' for path, kind in types.items())
    overrides += '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>'
    files['[Content_Types].xml'] = xml(f'<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/>{overrides}</Types>')
    with ZipFile(target, 'w', ZIP_DEFLATED) as z:
        for name, content in files.items():
            z.writestr(name, content)


def main():
    pdfmetrics.registerFont(TTFont('Deck', '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf'))
    pdfmetrics.registerFont(TTFont('DeckBold', '/usr/share/fonts/dejavu-sans-fonts/DejaVuSans-Bold.ttf'))
    slides = parse(OUT / 'main_deck.md')
    data, checks = load_and_check(slides)
    pages = [Page(slide, n, data).render() for n, slide in enumerate(slides, 1)]
    LOG.mkdir(parents=True, exist_ok=True)
    errors = [{'slide': p.number, 'errors': p.errors} for p in pages if p.errors]
    save(LOG / 'layout.json', {'errors': errors, 'pages': [dict(slide=p.number, text_boxes=p.boxes) for p in pages]})
    if errors:
        raise ValueError(json.dumps(errors, indent=2))
    write_pdf(pages, OUT / 'main_deck.pdf')
    note_parts = re.split(r'\n## \d{2} · ', (OUT / 'speaker-notes.md').read_text())[1:]
    note_parts[-1] = note_parts[-1].split('\n## Evidence', 1)[0]
    assert len(note_parts) == 15
    write_pptx(pages, note_parts, OUT / 'main_deck.pptx')
    text = subprocess.check_output(['pdftotext', '-layout', str(OUT / 'main_deck.pdf'), '-'], text=True)
    (LOG / 'pdf-extracted.txt').write_text(text)
    extracted = [p for p in text.split('\f') if p.strip()]
    assert len(extracted) == 15
    parity = []
    for page, actual in zip(pages, extracted, strict=True):
        desired = tokens(' '.join(page.printed))
        got = tokens(actual)
        parity.append({'slide': page.number, 'missing': dict(desired-got), 'extra': dict(got-desired)})
    save(LOG / 'text-parity.json', parity)
    assert all(not p['missing'] and not p['extra'] for p in parity), parity
    manifest = {'status': 'complete', 'slides': 15, 'planned_seconds': 1080,
                'visible_words': sum(len(' '.join(p.printed).split()) for p in pages),
                'model_calls': 0, 'gpu_seconds': 0, 'numeric_checks': checks,
                'layout_errors': 0, 'pdf_text_parity': 'all 15 pages',
                'sources_sha256': {str(p): sha(p) for p in FILES.values()},
                'outputs_sha256': {p.name: sha(p) for p in OUT.glob('main_deck.*')},
                'builder_sha256': sha(__file__)}
    save(LOG / 'build.json', manifest)
    print(json.dumps({k: manifest[k] for k in ['status', 'slides', 'planned_seconds', 'visible_words', 'layout_errors']}))


if __name__ == '__main__':
    main()
