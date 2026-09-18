"""Reviewable DEC-063 sealed admission patch; never change the running backend."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "scripts/r1_77b_sealed_backend.py"


def proposed():
    old = (ROOT / NAME).read_text()
    source = old
    replacements = [
        (
            "from scripts import r1_68c_dev_cell as donor\n",
            "from scripts import r1_63l_full_validation_contract as full_contract\nfrom scripts import r1_68c_dev_cell as donor\n",
        ),
        (
            '        raise ValueError("recipe/protocol cadence mismatch")\n    return m\n',
            '        raise ValueError("recipe/protocol cadence mismatch")\n    full_contract.admit(m, protocol, frozen)\n    return m\n',
        ),
        (
            "    if pop != planned_population(payload):\n",
            "    expected_population = planned_population(payload)\n"
            '    if "full_validation" in m:\n'
            '        full_contract.sample(m["full_validation"], payload["endpoints"]["drift"])\n'
            '        expected_population["full_validation"] = m["full_validation"]\n'
            '        if declared.get("full_validation") != m["full_validation"]:\n'
            '            raise ValueError("frozen full-validation population root differs")\n'
            "    if pop != expected_population:\n",
        ),
    ]
    for a, b in replacements:
        if source.count(a) != 1:
            raise ValueError("sealed admission patch anchor changed: " + a[:70])
        source = source.replace(a, b)
    compile(source, str(ROOT / NAME), "exec")
    return old, source


def main():
    old, new = proposed()
    patch = "".join(
        difflib.unified_diff(
            old.splitlines(True), new.splitlines(True), fromfile="a/" + NAME, tofile="b/" + NAME
        )
    )
    path = ROOT / "docs/tasks/R1-63l-backend.patch"
    with path.open("x") as f:
        f.write(patch)
    record = dict(
        task="R1-63l",
        status="prepared_not_applied_chain_S_active",
        target=NAME,
        original_sha256=hashlib.sha256(old.encode()).hexdigest(),
        proposed_sha256=hashlib.sha256(new.encode()).hexdigest(),
        patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),
        installed_backend_modified=False,
    )
    with (ROOT / "logs/r1_round31/r1-63l-backend-patch.json").open("x") as f:
        json.dump(record, f, indent=2)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
