"""Explicit, recursively verified normative dependency graph for Stage 4 D.1."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
PROTOCOL = "docs/R1_stage4_protocol_v5_2_D_1.md"
GRAPH = {
    PROTOCOL: [
        "docs/R1_stage4_protocol_draft_v5_1.md",
        "docs/R1_stage4_queue_concurrency_v2.md",
    ],
    "docs/R1_stage4_protocol_draft_v5_1.md": ["docs/updated_plan9.md"],
    "docs/R1_stage4_queue_concurrency_v2.md": [],
    "docs/updated_plan9.md": [
        "docs/more_input/pc_cap_coding_agent_guide (1).pdf",
        "docs/more_input/pc_cap_joint_redesign_proposal (1).pdf",
    ],
    "docs/more_input/pc_cap_coding_agent_guide (1).pdf": [],
    "docs/more_input/pc_cap_joint_redesign_proposal (1).pdf": [],
}
HISTORICAL = {"docs/R1_stage4_protocol_draft_v5_2_option_D.md"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def closure(root=ROOT):
    root = Path(root).resolve()
    seen, visiting = set(), set()

    def visit(name):
        if name in visiting:
            raise ValueError("normative dependency cycle")
        if name in seen:
            return
        if name not in GRAPH or not (root / name).is_file():
            raise ValueError("normative dependency missing: " + name)
        visiting.add(name)
        if name.endswith(".md"):
            for paragraph in (root / name).read_text().split("\n\n"):
                if "incorporat" not in paragraph.lower():
                    continue
                for target in re.findall(r"\]\(([^)]+)\)", paragraph):
                    target = unquote(target.split("#")[0])
                    if not target or "://" in target:
                        continue
                    resolved = ((root / name).parent / target).resolve()
                    if not resolved.is_relative_to(root):
                        raise ValueError("normative reference escapes repository")
                    rel = str(resolved.relative_to(root))
                    if rel not in GRAPH[name] and rel not in HISTORICAL:
                        raise ValueError("undeclared incorporated target: " + rel)
        for child in GRAPH[name]:
            visit(child)
        visiting.remove(name)
        seen.add(name)

    visit(PROTOCOL)
    return {
        "schema_version": 1,
        "root_document": PROTOCOL,
        "graph": GRAPH,
        "bindings_sha256": {str(root / n): sha(root / n) for n in sorted(seen)},
        "precedence": "D.1 and later adopted decisions govern superseded provisions",
    }


def verify(candidate, root=ROOT):
    expected = closure(root)
    if candidate.get("normative_closure") != expected:
        raise ValueError("normative closure differs or is absent")
    for path, digest in expected["bindings_sha256"].items():
        if candidate["bindings_sha256"].get(path) != digest:
            raise ValueError("normative file missing or changed: " + path)
    return {"normative_files": len(expected["bindings_sha256"]), "normative_closure_verified": True}


if __name__ == "__main__":
    print(json.dumps(closure(), indent=2))
