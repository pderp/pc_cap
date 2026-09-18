"""Prepare the DEC-063 driver and reconciled sealed-fork patches, never apply them."""

from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRIVER = "scripts/r1_68c_dev_cell.py"
BACKEND = "scripts/r1_77b_sealed_backend.py"


def change(source, old, new):
    if source.count(old) != 1:
        raise ValueError("patch anchor changed: " + old[:90])
    return source.replace(old, new)


def proposed_sources():
    original = {p: (ROOT / p).read_text() for p in (DRIVER, BACKEND)}
    if "from scripts import r1_68f_full_validation as full_validation" in original[DRIVER]:
        record = json.loads((ROOT / "logs/r1_round30/r1-68f-patch.json").read_text())
        for path, expected in record["proposed_files_sha256"].items():
            if hashlib.sha256(original[path].encode()).hexdigest() != expected:
                raise ValueError("installed R1-68f patch differs from reviewed bytes")
        before = {p: (ROOT / "logs/r1_round30/source_snapshot" / p).read_text() for p in original}
        if {p: hashlib.sha256(s.encode()).hexdigest() for p, s in before.items()} != record[
            "original_files_sha256"
        ]:
            raise ValueError("R1-68f source snapshot changed")
        return before, original
    revised = dict(original)
    a = change(
        original[DRIVER],
        "from scripts.r1_68b_integrity_runtime import (\n",
        "from scripts import r1_68f_full_validation as full_validation\n"
        "from scripts.r1_68b_integrity_runtime import (\n",
    )
    a = change(
        a,
        '    "scripts/r1_68e_batched_drift_v0.py",\n',
        '    "scripts/r1_68e_batched_drift_v0.py",\n    "scripts/r1_68f_full_validation.py",\n',
    )
    a = change(
        a,
        "    return profile, batch\n",
        "    full_validation.validate_spec(manifest)\n    return profile, batch\n",
    )
    a = change(
        a,
        '    validate_payload({**manifest, "mode": "synthetic"}, payload)\n',
        '    validate_payload({**manifest, "mode": "synthetic"}, payload)\n'
        '    full_validation.validate_sample(manifest, payload["endpoints"]["drift"])\n',
    )
    revised[DRIVER] = a
    revised[BACKEND] = change(
        original[BACKEND],
        "from scripts import r1_68c_dev_cell as donor\n",
        "from scripts import r1_68c_dev_cell as donor\n"
        "from scripts import r1_68f_full_validation as full_validation\n",
    )
    for path in (DRIVER, BACKEND):
        source = revised[path]
        source = change(
            source,
            '            "drift",\n',
            '            "drift",\n            "full_validation",\n',
        )
        source = change(
            source,
            '            report = read_binding(rec["report"])\n',
            '            report = read_binding(rec["report"])\n'
            "            full_validation.verify_report(\n"
            "                report, manifest, report_path, expected_sha256\n"
            "            )\n",
        )
        dispatch = "donor.run_drift_assay" if path == BACKEND else "run_drift_assay"
        source = change(
            source,
            "            if n == len(items):\n",
            '            if n != len(items) and "full_validation" in manifest:\n'
            '                cp["endpoints"]["drift"] = phase(\n'
            '                    f"drift:{n}",\n'
            f'                    lambda ep=ep: {dispatch}(assays, ep["drift"], manifest, profile),\n'
            "                )\n"
            "            if n == len(items):\n",
        )
        source = change(
            source,
            '            cp["observation"] = adapter.observe()\n',
            '                if "full_validation" in manifest:\n'
            '                    cp["endpoints"]["full_validation"] = phase(\n'
            '                        f"full_validation:{n}",\n'
            "                        lambda n=n, ep=ep, cp=cp: full_validation.run(\n"
            '                            assays, manifest, ep["drift"], cp["endpoints"]["drift"],\n'
            '                            attempt / f"full-validation-{n}.npz",\n'
            "                            checkpoint=n, manifest_sha256=expected_sha256,\n"
            "                        ),\n"
            "                    )\n"
            '            cp["observation"] = adapter.observe()\n',
        )
        # Both entry points validate the ordinary-text sample before any update.
        source = change(
            source,
            "    profile, batch_edits = profile_config(manifest, code_root)\n",
            "    profile, batch_edits = profile_config(manifest, code_root)\n"
            '    full_validation.validate_sample(manifest, payload["endpoints"]["drift"])\n',
        )
        revised[path] = source
    old_sha = hashlib.sha256(original[DRIVER].encode()).hexdigest()
    new_sha = hashlib.sha256(revised[DRIVER].encode()).hexdigest()
    revised[BACKEND] = change(
        revised[BACKEND], f'DONOR_SHA256 = "{old_sha}"', f'DONOR_SHA256 = "{new_sha}"'
    )
    for p, source in revised.items():
        compile(source, str(ROOT / p), "exec")
    return original, revised


def main():
    original, revised = proposed_sources()
    output = ROOT / "docs/tasks/R1-68f-driver.patch"
    patch = "".join(
        "".join(
            difflib.unified_diff(
                original[p].splitlines(True),
                revised[p].splitlines(True),
                fromfile="a/" + p,
                tofile="b/" + p,
            )
        )
        for p in original
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as stream:
        stream.write(patch)
    logs = ROOT / "logs/r1_round30"
    logs.mkdir(parents=True, exist_ok=True)
    for path, source in original.items():
        snapshot = logs / "source_snapshot" / path
        snapshot.parent.mkdir(parents=True, exist_ok=True)
        with snapshot.open("x") as stream:
            stream.write(source)
    record = dict(
        task="R1-68f",
        status="prepared_not_applied",
        installed_files_modified=False,
        original_files_sha256={
            p: hashlib.sha256(s.encode()).hexdigest() for p, s in original.items()
        },
        proposed_files_sha256={
            p: hashlib.sha256(s.encode()).hexdigest() for p, s in revised.items()
        },
        patch_sha256=hashlib.sha256(patch.encode()).hexdigest(),
        new_implementation_files_sha256={
            "scripts/r1_68f_full_validation.py": hashlib.sha256(
                (ROOT / "scripts/r1_68f_full_validation.py").read_bytes()
            ).hexdigest()
        },
        owner_action="apply both hooks at idle boundary; rebind all recipes, backend and candidates",
    )
    with (logs / "r1-68f-patch.json").open("x") as stream:
        json.dump(record, stream, indent=2)
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
