"""X26: inventory spoken numbers; verify slots, expose literal-source gaps.

CPU only. A matching value in a cited ledger row is a *candidate*, not semantic
proof: dataset, endpoint, sign and units still require contextual review.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import re
from bisect import bisect_right
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHEET = ROOT / "docs/presentation/numbers_to_say.md"
LEDGER = ROOT / "docs/talk_claim_ledger_v7.md"
DECK = ROOT / "docs/presentation/deck_v3"
PACK = ROOT.parent / "assets/presentation-materials/deck_v3/rehearsal"
SLOT = re.compile(r"\{\{([\w.-]+)\}\}")
DIGIT = re.compile(r"[+−-]?(?:\d{1,3}(?:,\d{3})+|\d+|(?=\.\d))(?:\.\d+)?(?:[eE][+−-]?\d+)?")
SMALL = dict(
    zip(
        "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split(),
        range(20),
        strict=True,
    )
)
SMALL.update(
    dict(
        zip(
            "twenty thirty forty fifty sixty seventy eighty ninety".split(),
            range(20, 100, 10),
            strict=True,
        )
    )
)
WORDS = re.compile(r"\b(?:" + "|".join(SMALL) + r"|hundred|thousand|million|half)\b", re.I)
INTERMEDIATE = re.compile(
    r"(?:^|/)(?:[^/]*(?:intermediate|candidate|preview|round\d+-delivered)[^/]*)(?:/|$)", re.I
)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def numbers(text):
    """All digit spans (even identifiers), plus English cardinals/fractions.

    Deliberately retains 'one' in rhetorical phrases: unresolved cases are visible.
    Offsets refer to the original text. Unsupported wording is not silently certified.
    """
    found = []
    for match in DIGIT.finditer(text):
        raw = match[0]
        value = float(raw.replace(",", "").replace("−", "-"))
        sign_word = re.search(r"\bminus\s*$", text[: match.start()], re.I)
        if sign_word:
            value = -abs(value)
        mantissa, _, exponent = raw.lower().partition("e")
        places = len(mantissa.partition(".")[2]) if "." in mantissa else 0
        if not math.isfinite(value) or abs(int(exponent or 0)) > 1000:
            # Hex hashes can resemble enormous exponents. Retain the span but
            # never treat an unrepresentable token as numerical evidence.
            found.append(
                dict(
                    start=match.start(),
                    end=match.end(),
                    raw=raw,
                    value=None,
                    tolerance=0,
                    percent=False,
                    kind="unrepresentable",
                )
            )
            continue
        tolerance = 0.5 * 10 ** (int(exponent or 0) - places) if (places or exponent) else 0
        end = match.end()
        scale = re.match(r"\s*(million|thousand|M)\b", text[end:])
        if scale:
            multiplier = {"million": 1000000, "thousand": 1000, "M": 1000000}[scale[1]]
            value *= multiplier
            tolerance *= multiplier
            end += len(scale[0])
        suffix = text[end:]
        percent = bool(
            re.match(
                r"(?:\*\*)?\s*(?:(?:to|–)\s*[.\d]+\s*)?(?:%|[- ]?percent\b|percentage points?\b)",
                suffix,
                re.I,
            )
        )
        if percent:
            value /= 100
            tolerance = (tolerance or 0.5) / 100
        found.append(
            dict(
                start=match.start(),
                end=end,
                raw=text[match.start() : end],
                value=value,
                tolerance=tolerance,
                percent=percent,
                kind="digits",
            )
        )
    matches = [
        m
        for m in WORDS.finditer(text)
        if not any(n["start"] <= m.start() < n["end"] for n in found)
    ]
    index = 0
    while index < len(matches):
        first = matches[index]
        last = first
        group = [first[0].lower()]
        index += 1
        while index < len(matches):
            nxt = matches[index]
            gap = text[last.end() : nxt.start()]
            word = nxt[0].lower()
            # 'three and five' is two numbers; allow 'and' only within hundreds.
            allowed_gap = bool(re.fullmatch(r"[\s,-]+", gap)) or (
                bool(re.fullmatch(r"\s+and\s+", gap))
                and any(w in group for w in ("hundred", "thousand"))
            )
            composable = (
                word in ("hundred", "thousand", "million")
                or group[-1] in ("hundred", "thousand", "million")
                or (SMALL.get(group[-1], 0) >= 20 and 0 < SMALL.get(word, 99) < 10)
            )
            if "and" in gap and re.match(r"\s+hundred\b", text[nxt.end() :], re.I):
                composable = False  # 'one hundred and three hundred' denotes two endpoints.
            if not allowed_gap or not composable:
                break
            group.append(word)
            last = nxt
            index += 1
        value, subtotal = 0, 0
        for word in group:
            if word == "hundred":
                subtotal = (subtotal or 1) * 100
            elif word in ("thousand", "million"):
                value += (subtotal or 1) * {"thousand": 1000, "million": 1000000}[word]
                subtotal = 0
            else:
                subtotal += 0.5 if word == "half" else SMALL[word]
        value += subtotal
        end = last.end()
        fraction = re.match(r"[- ](third|tenth)\b", text[end:], re.I)
        if fraction:
            value /= {"third": 3, "tenth": 10}[fraction[1].lower()]
            end += len(fraction[0])
        if re.search(r"\bminus\s*$", text[: first.start()], re.I):
            value = -value
        percent = bool(re.match(r"\s*(?:percent\b|percentage points?\b)", text[end:], re.I))
        if percent:
            value /= 100
        found.append(
            dict(
                start=first.start(),
                end=end,
                raw=text[first.start() : end],
                value=value,
                tolerance=0.005 if percent else 0,
                percent=percent,
                kind="words",
            )
        )
    return sorted(found, key=lambda row: row["start"])


def close(number, reference):
    if number["value"] is None or reference["value"] is None:
        return False
    return abs(number["value"] - reference["value"]) <= number["tolerance"] + 1e-12


def resolved(template, slots):
    parts, spans, end, length = [], [], 0, 0
    for match in SLOT.finditer(template):
        before = template[end : match.start()]
        value = slots.get(match[1], "PENDING")
        parts.extend((before, value))
        length += len(before)
        spans.append((length, length + len(value), match[1]))
        length += len(value)
        end = match.end()
    parts.append(template[end:])
    return "".join(parts), spans


def ledger_rows():
    rows = {}
    for line in LEDGER.read_text().splitlines():
        if not line.startswith("| ") or line.startswith(("| ID ", "| ---")):
            continue
        cells = [s.strip().replace("\\|", "|") for s in re.split(r"(?<!\\)\|", line)[1:-1]]
        if len(cells) != 9:
            raise ValueError("changed ledger table")
        # Exclude ID, filenames, limitations and negated claims from numerical evidence.
        rows[cells[0]] = dict(text="; ".join(cells[3:6]), source=cells[8])
    return rows


def sections(text, kind):
    """Yield line, offset, speakability, and IDs scoped to a slide/question."""
    chunks = re.split(r"(?m)(?=^## (?:Slide \d|\d+\.))", text) if kind != "slide" else [text]
    offset = 0
    for chunk in chunks:
        cited = set(re.findall(r"`([^`]+)`", chunk))
        cited.update(re.findall(r"([\w-]+_report\.md)", chunk))
        spoken = kind == "qa" and chunk.startswith("## ")
        for line in chunk.splitlines(keepends=True):
            stripped = line.strip()
            if kind == "script":
                if stripped == "Say:":
                    spoken = True
                elif stripped.startswith(("Evidence:", "## ")):
                    spoken = False
            elif kind == "slide":
                if stripped.startswith(("**On screen:", "## Speaker text")):
                    spoken = True
                elif stripped.startswith("## "):
                    spoken = False
            else:
                if stripped.startswith("Evidence:"):
                    spoken = False
            yield line, offset, spoken and not stripped.startswith(("## ", "[", "Evidence:")), cited
            offset += len(line)


def inventory(text, kind, rows, sheet, spans=(), reports=None):
    result = []
    line_sections = list(sections(text, kind))
    offsets = [s[1] for s in line_sections]
    for num in numbers(text):
        start, end = num["start"], num["end"]
        line, offset, spoken, cited = line_sections[bisect_right(offsets, start) - 1]
        # Embedded numerals in v5, R1, ES99 etc are retained, not experimental quantities.
        identifier = bool(
            (start and re.match(r"[A-Za-z_]", text[start - 1]))
            or re.match(r"[A-Za-z_]", text[end:])
        )
        slot = next((key for a, b, key in spans if a <= start and end <= b), None)
        candidates = [
            key
            for key in sorted(cited & rows.keys())
            if any(close(num, n) for n in rows[key].get("numbers", numbers(rows[key]["text"])))
        ]
        report_matches = []
        report_keys = (
            sorted(cited & (reports or {}).keys())
            if spoken and not identifier and not slot and not candidates
            else []
        )
        for report in report_keys:
            for fact in reports[report]:
                if close(num, fact):
                    report_matches.append(
                        {k: fact[k] for k in ("path", "line", "raw", "value", "context")}
                    )
                    if len(report_matches) == 5:
                        break
            if len(report_matches) == 5:
                break
        status = (
            "metadata"
            if not spoken
            else "identifier"
            if identifier
            else "verified_slot"
            if slot
            else "ledger_candidate"
            if candidates
            else "report_candidate"
            if report_matches
            else "unmatched"
        )
        result.append(
            dict(
                num,
                start=start,
                end=end,
                line=text.count("\n", 0, start) + 1,
                context=text[offset : max(offset + len(line), end)].strip(),
                spoken=spoken,
                status=status,
                slot=slot,
                ledger_candidates=candidates,
                sheet_value_candidates=sorted({n["raw"] for n in sheet if close(num, n)}),
                source=["docs/talk_claim_ledger_v7.md row " + key for key in candidates],
                report_candidates=report_matches,
            )
        )
    return result


def run(output, pack=PACK):
    # Import existing resolver only at execution; extraction/tests remain stdlib-only.
    from aw.presentation_pc import resolve

    output = Path(output)
    if output.exists():
        raise FileExistsError("choose a new audit output directory")
    binding = resolve()
    rows = ledger_rows()
    for row in rows.values():
        row["numbers"] = numbers(row["text"])
    sheet = numbers(SHEET.read_text())
    entries, placeholders, issues, inputs = [], [], [], {}
    inputs[str(SHEET)] = digest(SHEET)
    inputs[str(LEDGER)] = digest(LEDGER)
    report_by_claim = {
        key: set(re.findall(r"docs/[\w./-]+\.md", row["source"])) for key, row in rows.items()
    }
    reports = {}
    for name in {p for paths in report_by_claim.values() for p in paths} | {
        "docs/additional_work/PC-reader_report.md",
        "docs/additional_work/R_report.md",
    }:
        path = ROOT / name
        if not path.exists():
            continue
        inputs[str(path)] = digest(path)
        facts = []
        for i, line in enumerate(path.read_text().splitlines(), 1):
            if line.startswith("#") or re.search(r"(?:https?://|sha256|sources_sha256)", line):
                continue
            facts.extend(dict(n, path=name, line=i, context=line) for n in numbers(line))
        reports[name] = facts
    scoped_reports = {
        key: [fact for path in sorted(paths) for fact in reports.get(path, [])]
        for key, paths in report_by_claim.items()
    }
    scoped_reports.update({Path(name).name: facts for name, facts in reports.items()})
    sources = [
        (pack / f"speaking-script-{n}min.md", "script", DECK / f"speaking-script-{n}min.md")
        for n in (15, 25)
    ]
    sources += [(ROOT / "docs/presentation/qa.md", "qa", None)]
    sources += [(p, "slide", p) for p in sorted(DECK.glob("slide[0-9][0-9]-*.md"))]
    sources += [(p, "slide", p) for p in sorted(DECK.glob("backup-*.md"))]
    for path, kind, template_path in sources:
        text = path.read_text()
        inputs[str(path)] = digest(path)
        spans = []
        if template_path:
            template = template_path.read_text()
            inputs[str(template_path)] = digest(template_path)
            expected, spans = resolved(template, binding["slots"])
            for match in SLOT.finditer(template):
                placeholders.append(
                    dict(
                        path=str(template_path),
                        line=template.count("\n", 0, match.start()) + 1,
                        literal=match[0],
                        resolved=binding["slots"].get(match[1]),
                        status="intentional_resolved_template"
                        if match[1] in binding["slots"]
                        else "unresolved",
                    )
                )
            if kind == "slide":
                text = expected
            elif text != expected:
                issues.append(
                    dict(path=str(path), issue="export differs from freshly resolved template")
                )
                spans = []  # Never award a slot trace to a stale export.
        values = inventory(text, kind, rows, sheet, spans, scoped_reports)
        entries.extend(dict(item, path=str(path)) for item in values)
        for line, offset, spoken, _ in sections(text, kind):
            for match in re.finditer(
                r"\{\{[^}]+\}\}|\b(?:PENDING|TO FILL|TBD|UNAVAILABLE)\b|_{3,}", line
            ):
                placeholders.append(
                    dict(
                        path=str(path),
                        line=text.count("\n", 0, offset) + 1,
                        literal=match[0],
                        status="spoken_placeholder" if spoken else "metadata_placeholder",
                    )
                )
    intermediate = []
    for name in [*binding["sources_sha256"], *(row["source"] for row in rows.values())]:
        if INTERMEDIATE.search(name):
            intermediate.append(name)
    archived_code = [p for p in intermediate if "/docs/tasks/PC-9-candidate/" in p]
    issues.extend(
        dict(issue="intermediate_source", path=p)
        for p in sorted(set(intermediate) - set(archived_code))
    )
    report = dict(
        status="inventory_complete_with_review_items",
        method="Slots checked against the existing canonical resolver. Ledger/report matches are numerical candidates, not semantic certification. Unmatched literals and all candidates need context review; metadata and identifier digits are retained separately. Report candidates supplement missing ledger values; locations capped at five per occurrence.",
        sheet_bridge="numbers_to_say.md headline anchors and its linked claim-ledger/PC-slot source registers",
        rounding="Fractions: half the last displayed decimal unit; integer counts exact. Percentages divided by 100 with half the last displayed percent unit (integer percentages: 0.5 percentage point). Scientific notation uses its exponent. English cardinals exact; one-third/tenth interpreted arithmetically. Source rounded values receive no extra tolerance; signs are preserved. Matching 95 percent in a disclaimer does not establish coverage.",
        counts=dict(Counter(e["status"] for e in entries)),
        entries=entries,
        ledger_sources={key: row["source"] for key, row in rows.items()},
        placeholders=placeholders,
        issues=issues,
        intermediate_sources=sorted(set(intermediate)),
        documented_historical_code=archived_code,
        archive_qualification="PC-9-candidate/old contains preserved executed source bytes, not intermediate experimental results; sources.json/reporting-sources.json describe that archive. Hashes remain checked by the canonical resolver.",
        source_bindings={
            **inputs,
            **binding["sources_sha256"],
            str(Path(__file__).resolve()): digest(__file__),
        },
        slot_values=binding["slots"],
        slot_status=binding["status"],
    )
    output.mkdir(parents=True)
    (output / "audit.json").write_text(json.dumps(report, indent=2) + "\n")
    columns = [
        "path",
        "line",
        "raw",
        "value",
        "tolerance",
        "spoken",
        "status",
        "slot",
        "ledger_candidates",
        "sheet_value_candidates",
        "source",
        "report_candidates",
        "context",
    ]
    with (output / "numbers.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(entries)
    review = [
        "# Spoken-number review items",
        "",
        report["method"],
        "",
        report["rounding"],
        "",
        "## Unmatched spoken literals",
        "",
    ]
    for e in entries:
        if e["status"] == "unmatched":
            review.append(f"- `{Path(e['path']).name}:{e['line']}` **{e['raw']}** — {e['context']}")
    review += [
        "",
        "## Export/source issues",
        "",
        json.dumps(issues, indent=2),
        "",
        "## Literal placeholders",
        "",
        "Intentional template slots and nonspoken fallback instructions are recorded in audit.json; they are not missing results.",
    ]
    for p in placeholders:
        if p["status"] in ("unresolved", "spoken_placeholder"):
            review.append(f"- `{p['path']}:{p['line']}` {p['literal']} ({p['status']})")
    (output / "review.md").write_text("\n".join(review) + "\n")
    print(json.dumps({"output": str(output), "counts": report["counts"], "issues": issues}))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--pack", type=Path, default=PACK)
    args = parser.parse_args()
    run(args.output, args.pack)
