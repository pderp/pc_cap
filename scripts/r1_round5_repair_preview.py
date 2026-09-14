"""Test three proposed round-5 fixture/audit edits in memory; never edit their files."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import inspect
import json
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EDITS = {
    "tests/revision_v1/test_endpoints.py": (
        "json.dumps([[list(k), v] for k, v in self.answers.items()])",
        "json.dumps([[[int(i) for i in k], v] for k, v in self.answers.items()])",
    ),
    "tests/revision_v1/test_r1_27_superseding_cpu.py": (
        'assert len(statements) == 7, "preflight changed: review extraction"',
        'assert len(statements) == 6, "preflight changed: review extraction"',
    ),
    "scripts/r1_stage2_table_audit.py": ('s["tag"].split("@")[0] == c[0]', 's["tag"] == c[0]'),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output-dir", type=Path, required=True)
    a = ap.parse_args()
    if a.output_dir.exists() or not a.output_dir.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output directory required")
    a.output_dir.mkdir(parents=True)
    bindings, modules, patches = {}, {}, []
    for rel, (old, new) in EDITS.items():
        path = ROOT / rel
        before = path.read_text()
        assert before.count(old) == 1, rel
        after = before.replace(old, new, 1)
        bindings[rel] = {
            "before_sha256": hashlib.sha256(before.encode()).hexdigest(),
            "proposed_sha256": hashlib.sha256(after.encode()).hexdigest(),
        }
        patches.extend(
            difflib.unified_diff(
                before.splitlines(True),
                after.splitlines(True),
                fromfile="a/" + rel,
                tofile="b/" + rel,
            )
        )
        mod = types.ModuleType("preview_" + path.stem)
        mod.__file__ = str(path)
        exec(compile(after, str(path), "exec"), mod.__dict__)
        modules[rel] = mod
    checks = []
    for rel, module in modules.items():
        if not rel.startswith("tests/"):
            continue
        for name, fn in vars(module).items():
            if not name.startswith("test_") or not inspect.isfunction(fn):
                continue
            kwargs = {}
            if "tmp_path" in inspect.signature(fn).parameters:
                temp = a.output_dir / name
                temp.mkdir()
                kwargs["tmp_path"] = temp
            expected = name == "test_actual_orphan_checkpoint_root_is_refused"
            try:
                fn(**kwargs)
            except pytest.fail.Exception as e:
                if not expected or "DID NOT RAISE" not in str(e):
                    raise
                status = "expected_failure_actual_checkpoint_guard"
            else:
                assert not expected, "known defect unexpectedly repaired; review expected failure"
                status = "passed"
            checks.append({"file": rel, "test": name, "status": status})
    table = modules["scripts/r1_stage2_table_audit.py"].audit(
        ROOT / "logs/r1_round5/stage2_recount_v2.json"
    )
    assert table["rows_checked"] == table["unique_matches"] == 30
    table["proposed_source_sha256"] = bindings["scripts/r1_stage2_table_audit.py"][
        "proposed_sha256"
    ]
    table["execution_note"] = (
        "One tested tag-comparison repair compiled in memory; exact patch accompanies this report."
    )
    for rel, b in bindings.items():
        assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == b["before_sha256"]
    result = {
        "task": "R1-round5",
        "edits_applied": False,
        "mode": "direct test invocation with repaired source in memory",
        "bindings": bindings,
        "checks": checks,
        "gpu_seconds": 0,
        "table_rows": table["rows_checked"],
        "table_unique_matches": table["unique_matches"],
    }
    for name, value in (
        ("verification.json", result),
        ("stage2_stream_table_audit_verified.json", table),
    ):
        with (a.output_dir / name).open("x") as f:
            json.dump(value, f, indent=2, sort_keys=True, allow_nan=False)
            f.write("\n")
    with (a.output_dir / "proposed.patch").open("x") as f:
        f.write("".join(patches))
    print(
        json.dumps(
            {
                "passed": sum(c["status"] == "passed" for c in checks),
                "expected_failures": sum(c["status"] != "passed" for c in checks),
                "table_rows_verified": table["unique_matches"],
                "edits_applied": False,
            }
        )
    )


if __name__ == "__main__":
    main()
