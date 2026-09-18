"""D.2 incorporates the complete immutable D.1 normative closure."""

from __future__ import annotations

import re
from pathlib import Path
from urllib.parse import unquote

from scripts import r1_49j_normative_closure as prior

ROOT = prior.ROOT
PROTOCOL = "docs/R1_stage4_protocol_v5_2_D_2.md"


def closure(root=ROOT):
    root = Path(root).resolve()
    for paragraph in (root / PROTOCOL).read_text().split("\n\n"):
        if "incorporat" not in paragraph.lower():
            continue
        for target in re.findall(r"\]\(([^)]+)\)", paragraph):
            target = unquote(target.split("#")[0])
            if not target or "://" in target:
                continue
            resolved = ((root / PROTOCOL).parent / target).resolve()
            if resolved != root / prior.PROTOCOL:
                raise ValueError("undeclared D.2 incorporated target: " + target)
    value = prior.closure(root)
    return dict(
        schema_version=1,
        root_document=PROTOCOL,
        graph={**value["graph"], PROTOCOL: [prior.PROTOCOL]},
        bindings_sha256={
            **value["bindings_sha256"],
            str(root / PROTOCOL): prior.sha(root / PROTOCOL),
        },
        precedence="D.2 and later adopted decisions govern superseded provisions",
    )


def verify(candidate, root=ROOT):
    expected = closure(root)
    if candidate.get("normative_closure") != expected:
        raise ValueError("D.2 normative closure differs or is absent")
    for path, value in expected["bindings_sha256"].items():
        if candidate["bindings_sha256"].get(path) != value:
            raise ValueError("D.2 normative file missing or changed: " + path)
    return dict(normative_files=7, normative_closure_verified=True)
