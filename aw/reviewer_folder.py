"""Export the two Capex reviewer documents, preserving content and rebasing links."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESTINATION = ROOT.parent / "assets/presentation-materials/review-data"
LINK = re.compile(r"(!?\[[^\]]*\]\()([^\s)]+)(\))")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rebase(text, source, target):
    checked = []

    def replace(match):
        href = match[2]
        if href.startswith(("#", "http:", "https:", "mailto:")):
            return match[0]
        name, separator, fragment = href.partition("#")
        path = (source.parent / name).resolve()
        if not path.exists():
            raise FileNotFoundError(f"{source}: {href}")
        checked.append(str(path))
        return match[1] + os.path.relpath(path, target.parent) + separator + fragment + match[3]

    return LINK.sub(replace, text), checked


def export(output):
    output = Path(output)
    if output.exists():
        raise FileExistsError("choose a new refresh record directory")
    rendered = []
    for name, exported in (
        ("review-results.md", "results.md"),
        ("final-experiments.md", "final-experiments.md"),
    ):
        source = ROOT / "docs/presentation" / name
        target = DESTINATION / exported
        text, checked = rebase(source.read_text(), source, target)
        # Reversibility ensures no wording/numbers changed during copying.
        assert rebase(text, target, source)[0] == source.read_text()
        rendered.append((source, target, text, checked))
    records = []
    for source, target, text, checked in rendered:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
        records.append(
            dict(
                source=str(source),
                source_sha256=sha(source),
                export=str(target),
                export_sha256=sha(target),
                checked_local_links=checked,
                content_equal_after_link_rebasing=True,
            )
        )
    current = DESTINATION / "CURRENT.md"
    current.write_text("""# October 2 review — current entry points

Evidence through October 2; folder refreshed in Round 61.
The September 27 README is historical; begin with the October 2 update.

- [2 October update: read first](../../../pc_cap/docs/friday-10.02-review/UPDATE-2026-10-02.md)
- [Capstan's October 1 primer](../../../pc_cap/docs/friday-10.02-review/README.md)
- [Reviewer feedback and response](../../../pc_cap/docs/friday-10.02-review/feedback-MMK-nelson-entropy.md)
- [Capex's scientific review](../../../pc_cap/docs/friday-10.02-review/feedback-MMK-nelson-entropy-capex.md)
- [Current results and qualifications](results.md)
- [Remaining experiments and historical planning forms](final-experiments.md)
- [October 9 freeze checklist](../../../pc_cap/docs/freeze_checklist_20261009.md)

These are a dated snapshot. PC-reader, Option R and upper-layer results must be refreshed after completed evaluations; pending results are not zero.
""")
    _, checked = rebase(current.read_text(), current, current)
    record = dict(
        task="DOC-2",
        records=records,
        navigation=str(current),
        navigation_sha256=sha(current),
        navigation_links=checked,
        linked_documents_sha256={str(p): sha(p) for p in checked},
        folder_files_sha256={str(p): sha(p) for p in sorted(DESTINATION.iterdir()) if p.is_file()},
        code_sha256=sha(__file__),
        gpu_seconds=0,
    )
    output.mkdir(parents=True)
    (output / "refresh.json").write_text(json.dumps(record, indent=2) + "\n")
    print(
        json.dumps(
            {
                "exports": len(records),
                "checked_links": sum(len(r["checked_local_links"]) for r in records) + len(checked),
                "record": str(output / "refresh.json"),
            }
        )
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    export(parser.parse_args().output)
