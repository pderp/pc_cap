"""PC-10 copies and combined PC-9/10 patch; never edits live source files."""

from __future__ import annotations

import difflib
import hashlib
import json

from aw.pc9_stage import DEST, ROOT, replace


def report(text):
    text = replace(
        text,
        "ROOT = Path(__file__)",
        "from aw import pc_treatments as treatment\n\nROOT = Path(__file__)",
    )
    text = replace(
        text,
        "directory=str(dest.resolve()))",
        "directory=str(dest.resolve()), treatment=treatment.planned(plan))",
    )
    text = replace(
        text,
        "        if smoke:\n            verify",
        "        row.update(treatment.recorded(cfg, plan=plan))\n        if smoke:\n            verify",
    )
    text = replace(
        text,
        "if cfg['weights_sha256'] != WEIGHTS_SHA or cfg['credit_iters'] != 8 or cfg['error_lr'] != .1:",
        "if cfg['weights_sha256'] != WEIGHTS_SHA:",
    )
    text = replace(text, "'error_lr', 'credit_iters', 'drift')", "'drift')")
    text = replace(
        text,
        "\n        row.update(status=finish",
        "\n        row.update(treatment.recorded(cfg, finish, plan))\n        row.update(status=finish",
    )
    text = replace(
        text,
        "def compare(rows, expected):\n    indexed",
        "def compare(rows, expected):\n    treatment.homogeneous(rows)\n    indexed",
    )
    text = replace(
        text,
        "    cells, pairs, aggregates = compare(rows, expected)",
        '    variants = {treatment.key(r["treatment"]) for r in rows}\n    if variants - {treatment.key(treatment.DEFAULT)} and Path(document).resolve() == ROOT / "docs/additional_work/PC-v0_report.md":\n        raise ValueError("variant needs a separate document, not the original result slot")\n    if len(variants) > 1:\n        return treatment.build_sweep(groups, output, document, build, read, orders=orders, smoke=smoke, diagnostics=diagnostics)\n    selected = treatment.homogeneous(rows)\n    cells, pairs, aggregates = compare(rows, expected)',
    )
    text = replace(
        text,
        "    report = dict(smoke=smoke, cells=cells",
        "    bindings[str(Path(treatment.__file__).resolve())] = sha(treatment.__file__)\n    report = dict(smoke=smoke, treatment=selected, treatment_label=treatment.label(selected), cells=cells",
    )
    text = replace(
        text,
        "    text += f\"{sum(c['status']",
        '    text += "Treatment: " + treatment.label(selected) + "\\n\\n"\n    text += f"{sum(c[\'status\']',
    )
    text = replace(
        text,
        "Eight-step error credit requires 9 forwards + 9 reverses per inference call;",
        "Error credit at k steps requires k+1 forwards + k+1 reverses per inference call;",
    )
    text = replace(
        text,
        "    import matplotlib\n",
        '    report = json.loads(Path(report_path).read_bytes())\n    if report.get("schema") == "pc-treatment-sweep-v1":\n        raise ValueError("plot an individual treatment report; never pool sweep arms")\n    import matplotlib\n',
    )
    text = replace(
        text,
        "    import matplotlib.pyplot as plt\n    report = json.loads(Path(report_path).read_bytes())",
        "    import matplotlib.pyplot as plt",
    )
    text = replace(
        text,
        "fig.suptitle('PC-v0: efficacy and measured cost'",
        "fig.suptitle('PC-v0: ' + treatment.label(report.get('treatment', treatment.DEFAULT))",
    )
    text = replace(
        text,
        "print(json.dumps({'cells': len(r['cells']), 'complete': sum(c['status']=='complete' for c in r['cells'])}))",
        "print(json.dumps({'treatments': len(r['treatments'])} if 'treatments' in r else {'cells': len(r['cells']), 'complete': sum(c['status']=='complete' for c in r['cells'])}))",
    )
    return text


def harm(text):
    text = replace(
        text,
        "from aw import scoring",
        "from aw import pc_treatments as treatment\nfrom aw import scoring",
    )
    text = replace(
        text,
        "            summary=summarize(values),",
        '            treatment=getattr(reader, "treatment", dict(treatment.DEFAULT)),\n            summary=summarize(values),',
    )
    text = replace(
        text,
        '    records = json.loads((dest / "checkpoints.json").read_bytes())',
        '    saved_finish = json.loads((dest / "finish.json").read_bytes())\n    solver = treatment.recorded(cfg, saved_finish)["solver"]\n    if base.error_lr != solver["error_lr"]:\n        raise ValueError("readout base rate differs from acquisition configuration")\n    records = json.loads((dest / "checkpoints.json").read_bytes())',
    )
    text = replace(
        text,
        "                credit_iters=8,",
        '                credit_iters=solver["credit_iters"],',
    )
    text = replace(
        text,
        'int(cfg["named_seeds"]["seed_cap_init"]))',
        'int(cfg["named_seeds"]["seed_cap_init"]), credit_iters=solver["credit_iters"])',
    )
    text = replace(
        text,
        "    expected = json.loads((Path(group)",
        "    selected = treatment.homogeneous(rows)\n    expected = json.loads((Path(group)",
    )
    text = replace(
        text,
        "report = dict(smoke=smoke, selection=meta,",
        "report = dict(smoke=smoke, treatment=selected, treatment_label=treatment.label(selected), selection=meta,",
    )
    text = replace(
        text,
        "            for row in rows:\n                cap",
        """            for row in rows:
                rate = row["solver"]["error_lr"]
                if base.error_lr != rate:
                    from pccap.bases.epc import EPCBase

                    # Preserve tiny-fixture batch methods as well as production params.
                    replacement = object.__new__(type(base))
                    EPCBase.__init__(replacement, params_np=jax.tree_util.tree_map(np.asarray, base.params),
                                     cfg=base.cfg, ledger=base.ledger, error_lr=rate)
                    base = replacement
                cap""",
    )
    text = replace(
        text,
        "                result = read_arm(reader,",
        "                reader.treatment = selected\n                result = read_arm(reader,",
    )
    text = replace(
        text,
        "| dict(readout=result)",
        '| dict(readout=result, treatment=selected, solver=row["solver"])',
    )
    text = replace(
        text,
        "                        dataset=ds,\n                        realization=r,",
        "                        dataset=ds,\n                        treatment=selected,\n                        realization=r,",
    )
    text = replace(
        text,
        '                ROOT / "aw/scoring.py",',
        '                Path(treatment.__file__),\n                ROOT / "aw/scoring.py",',
    )
    text = replace(
        text,
        '(out / "table.md").write_text(table_block(report))',
        '(out / "table.md").write_text("Treatment: " + treatment.label(selected) + "\\n\\n" + table_block(report))',
    )
    return text


def v1(text):
    text = replace(
        text,
        "from aw.pc_v0_report import sha",
        "from aw import pc_treatments as treatment\nfrom aw.pc_v0_report import sha",
    )
    text = replace(
        text, "binding, *, batch_size=16):", "binding, *, batch_size=16, config=None, finish=None):"
    )
    text = replace(
        text,
        """        if binding["credit"] not in ("adjoint", "error") or binding["iters"] != 8:
            raise ValueError("supplemental fixed-v5 credit must be adjoint/error with eight steps")""",
        """        if binding["credit"] not in ("adjoint", "error"):
            raise ValueError("supplemental credit must be adjoint/error")
        actual = treatment.normalized(binding["iters"], binding.get("error_lr", 0.1))
        if (config is None) != (finish is None):
            raise ValueError("supply both config and finish for treatment validation")
        if config is None:
            if actual != treatment.DEFAULT:
                raise ValueError("variant snapshot requires its config and finish")
            selected = dict(treatment.DEFAULT)
        else:
            record = treatment.recorded(config, finish)
            solver, selected = record["solver"], record["treatment"]
            if actual != {k: solver[k] for k in treatment.DEFAULT}:
                raise ValueError("checkpoint and recorded solver differ")
            if binding["credit"] != ("error" if solver["error_solver_active"] else "adjoint"):
                raise ValueError("checkpoint and recorded credit arm differ")
        if base.error_lr != actual["error_lr"]:
            raise ValueError("construct EPCBase with the recorded error learning rate before restoration")""",
    )
    text = replace(
        text,
        "        reader.checkpoint = dict(binding, path=str(path))",
        "        reader.checkpoint = dict(binding, path=str(path))\n        reader.treatment = selected",
    )
    return text


def main():
    records, patches = {}, []
    for name, transform in (
        ("pc_v0_report.py", report),
        ("pc_harm_readout.py", harm),
        ("pc_v1_readout.py", v1),
    ):
        original = (ROOT / "aw" / name).read_text()
        candidate = transform(original)
        compile(candidate, name, "exec")
        with (DEST / name).open("x") as f:
            f.write(candidate)
        records["aw/" + name] = dict(
            before_sha256=hashlib.sha256(original.encode()).hexdigest(),
            candidate_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
        )
        patches.extend(
            difflib.unified_diff(
                original.splitlines(True),
                candidate.splitlines(True),
                fromfile="a/aw/" + name,
                tofile="b/aw/" + name,
            )
        )
    helper = (DEST / "pc_treatments.py").read_text()
    patches.extend(
        difflib.unified_diff(
            [], helper.splitlines(True), fromfile="/dev/null", tofile="b/aw/pc_treatments.py"
        )
    )
    records["aw/pc_treatments.py"] = dict(
        before_sha256=None, candidate_sha256=hashlib.sha256(helper.encode()).hexdigest()
    )
    with (DEST / "reporting-options.patch").open("x") as f:
        f.writelines(patches)
    with (DEST / "combined-PC-9-PC-10.patch").open("x") as f:
        f.write((DEST / "solver-options.patch").read_text())
        f.writelines(patches)
    with (DEST / "reporting-sources.json").open("x") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


if __name__ == "__main__":
    main()
