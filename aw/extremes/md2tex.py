"""Minimal Markdown -> LaTeX -> PDF for the ext-20261009 report (no pandoc on this machine; xelatex is present).

Supports: ATX headings (#..####), paragraphs, bullet/numbered lists (one level), fenced code blocks, pipe tables,
inline code, bold, italics, images ![caption](path), links [text](url), inline math $...$ and display math $$...$$
left untouched, horizontal rules. Everything else is escaped text.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ESC = {"&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}", "\\": r"\textbackslash{}"}


def esc(s: str) -> str:
    return "".join(ESC.get(ch, ch) for ch in s)


def inline(s: str) -> str:
    out, i = [], 0
    # protect math and code spans first
    tokens = re.split(r"(\$[^$]+\$|`[^`]+`)", s)
    for t in tokens:
        if not t:
            continue
        if t.startswith("$") and t.endswith("$") and len(t) > 2:
            out.append(t)
        elif t.startswith("`") and t.endswith("`"):
            out.append(r"\texttt{" + esc(t[1:-1]) + "}")
        else:
            u = esc(t)
            u = re.sub(r"\\\[([^\]]+)\\\]\(([^)]+)\)", lambda m: r"\href{" + m.group(2).replace("\\_", "_").replace("\\%", "%").replace("\\#", "#") + "}{" + m.group(1) + "}", u) if False else u
            u = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: m.group(1) + r" (\texttt{" + m.group(2) + "})", u)
            u = re.sub(r"\*\*(.+?)\*\*", r"\\textbf{\1}", u)
            u = re.sub(r"(?<![\w\\])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"\\emph{\1}", u)
            out.append(u)
    return "".join(out)


def table(lines: list[str]) -> str:
    rows = [[c.strip() for c in l.strip().strip("|").split("|")] for l in lines if not re.match(r"^\s*\|?\s*:?-{2,}", l)]
    if not rows:
        return ""
    ncol = max(len(r) for r in rows)
    head, body = rows[0], rows[1:]
    spec = "@{}" + "".join("l" if i == 0 else "l" for i in range(ncol)) + "@{}"
    out = [r"\begin{center}\footnotesize", r"\begin{tabularx}{\textwidth}{" + "@{}" + "p{0.22\\textwidth}" + "".join("X" for _ in range(ncol - 1)) + "@{}}", r"\toprule"]
    out.append(" & ".join(inline(c) for c in head + [""] * (ncol - len(head))) + r" \\ \midrule")
    for r in body:
        out.append(" & ".join(inline(c) for c in r + [""] * (ncol - len(r))) + r" \\")
    out += [r"\bottomrule", r"\end{tabularx}", r"\end{center}"]
    return "\n".join(out)


def convert(md: str, root: Path) -> str:
    lines = md.splitlines()
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if l.startswith("```"):
            j = i + 1
            block = []
            while j < len(lines) and not lines[j].startswith("```"):
                block.append(lines[j]); j += 1
            out.append(r"\begin{small}\begin{verbatim}" + "\n" + "\n".join(block) + "\n" + r"\end{verbatim}\end{small}")
            i = j + 1; continue
        if l.strip().startswith("$$"):
            j = i + 1
            block = []
            while j < len(lines) and not lines[j].strip().startswith("$$"):
                block.append(lines[j]); j += 1
            out.append(r"\[" + " ".join(block) + r"\]")
            i = j + 1; continue
        m = re.match(r"^(#{1,4})\s+(.*)$", l)
        if m:
            level = len(m.group(1))
            cmd = {1: r"\section", 2: r"\subsection", 3: r"\subsubsection", 4: r"\paragraph"}[level]
            out.append(cmd + "{" + inline(m.group(2)) + "}")
            i += 1; continue
        if l.strip().startswith("|"):
            j = i
            block = []
            while j < len(lines) and lines[j].strip().startswith("|"):
                block.append(lines[j]); j += 1
            out.append(table(block)); i = j; continue
        m = re.match(r"^!\[(.*?)\]\((.+?)\)", l.strip())
        if m:
            path = (root / m.group(2)).resolve()
            out.append(r"\begin{figure}[H]\centering\includegraphics[width=\textwidth]{" + str(path).replace("\\", "/") + "}\caption{" + inline(m.group(1)) + "}\end{figure}")
            i += 1; continue
        if re.match(r"^\s*[-*]\s+", l):
            j = i
            items = []
            while j < len(lines) and re.match(r"^\s*[-*]\s+", lines[j]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[j])); j += 1
            out.append(r"\begin{itemize}" + "\n" + "\n".join(r"\item " + inline(x) for x in items) + "\n" + r"\end{itemize}")
            i = j; continue
        if re.match(r"^\s*\d+[.)]\s+", l):
            j = i
            items = []
            while j < len(lines) and re.match(r"^\s*\d+[.)]\s+", lines[j]):
                items.append(re.sub(r"^\s*\d+[.)]\s+", "", lines[j])); j += 1
            out.append(r"\begin{enumerate}" + "\n" + "\n".join(r"\item " + inline(x) for x in items) + "\n" + r"\end{enumerate}")
            i = j; continue
        if l.strip() in ("---", "***"):
            out.append(r"\par\noindent\rule{\textwidth}{0.4pt}"); i += 1; continue
        if not l.strip():
            out.append(""); i += 1; continue
        j = i
        para = []
        while j < len(lines) and lines[j].strip() and not re.match(r"^(#{1,4}\s|```|\||!\[|\s*[-*]\s+|\s*\d+[.)]\s+)", lines[j]) and not lines[j].strip().startswith("$$"):
            para.append(lines[j]); j += 1
        out.append(inline(" ".join(para)))
        i = j
    return "\n\n".join(out)


PREAMBLE = r"""\documentclass[10pt,a4paper]{article}
\usepackage{fontspec}\setmainfont{DejaVu Serif}\setmonofont{DejaVu Sans Mono}[Scale=0.85]
\usepackage[margin=2.2cm]{geometry}\usepackage{graphicx}\usepackage{float}\usepackage{booktabs}\usepackage{tabularx}\usepackage{amsmath}\usepackage{hyperref}\usepackage{microtype}
\hypersetup{colorlinks=true,linkcolor=blue!50!black,urlcolor=blue!50!black}
\setlength{\parskip}{4pt}\setlength{\parindent}{0pt}
\title{%s}\author{%s}\date{%s}
\begin{document}\maketitle\tableofcontents\clearpage
"""


def build(md_path: Path, pdf_path: Path, title: str, author: str, date: str) -> dict:
    md = md_path.read_text()
    body = convert(md, md_path.parent)
    tex = (PREAMBLE % (esc(title), esc(author), esc(date))) + body + "\n\\end{document}\n"
    work = pdf_path.parent / "_tex"
    work.mkdir(parents=True, exist_ok=True)
    texfile = work / (pdf_path.stem + ".tex")
    texfile.write_text(tex)
    log = ""
    for _ in range(2):
        r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", str(work), str(texfile)], capture_output=True, text=True)
        log = r.stdout[-3000:]
        if r.returncode != 0:
            return dict(status="failed", log=log)
    built = work / (pdf_path.stem + ".pdf")
    pdf_path.write_bytes(built.read_bytes())
    return dict(status="ok", pages=len(re.findall(r"/Type\s*/Page[^s]", built.read_bytes().decode("latin1"))), log=log[-500:])


if __name__ == "__main__":
    md, pdf = Path(sys.argv[1]), Path(sys.argv[2])
    print(build(md, pdf, sys.argv[3] if len(sys.argv) > 3 else md.stem, "Capstan (pc_cap)", sys.argv[4] if len(sys.argv) > 4 else ""))
