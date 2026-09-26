"""PC-5: matched-position harm after acquisition; no training or queue operations.

The production CLI reads completed PC-v0 groups. ``read_arm`` also accepts an
audited fixed-v5 batch reader once that runner supplies its restored checkpoint.
No logits are retained. The imported scorer and frozen batch readers are unchanged.
"""

from __future__ import annotations

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
import hashlib
import json
import time
from contextlib import nullcontext
from pathlib import Path

import numpy as np
from scripts import r1_68f_full_validation as fv
from scripts.r1_68e_batched_drift_v0 import V0PositionBatchReader

from aw import scoring
from aw.pc_v0 import CUTOFF, archive, build_cap, dump, wall_limit
from aw.pc_v0_report import ROOT, compare, load_group, sha, table
from pccap.harness.snapshot import restore
from pccap.revision_v1.stage4_adapters import CellAdapter

OUTPUT = ROOT / "results/additional_work/PC-v0/harm"


def selection(mode="v0"):
    """Outcome-independent inventories; v0 matches Evaluator's first 32 windows."""
    spec = fv.make_spec()
    windows, _ = fv.population(spec["source"])
    if mode == "v0":
        windows = windows[:32]
    elif mode == "v5":
        fv.validate_spec({"full_validation": spec})
    else:
        raise ValueError("selection mode must be v0 or v5")
    return windows, dict(
        mode=mode,
        source=spec["source"],
        inventory=spec["source_inventory"],
        windows=len(windows),
        window_tokens=128,
        positions=windows.size - len(windows),
        windows_sha256=window_hash(windows),
        context="reset every window",
        order="window then target position, starting at target position 1",
    )


def window_hash(windows):
    return hashlib.sha256(np.asarray(windows, dtype="<i8").tobytes()).hexdigest()


def tails(values, width):
    """Fractional empirical ES99: average of the worst 1% positive harm, zeros included."""
    d = np.asarray(values, np.float64).reshape(-1)
    if not len(d) or not np.isfinite(d).all() or width < 1 or len(d) % width:
        raise ValueError("nonfinite, empty or malformed harm vector")
    pos = np.sort(np.maximum(d, 0))[::-1]
    mass = 0.01 * len(d)
    whole = int(mass)
    es = (pos[:whole].sum() + (mass - whole) * pos[whole]) / mass
    cum = np.cumsum(pos)
    half = int(np.searchsorted(cum, 0.5 * cum[-1], side="left") + 1) if cum[-1] > 0 else None
    i = int(d.argmax())
    return dict(
        positions=len(d),
        mean_signed=float(d.mean()),
        mean_positive=float(np.maximum(d, 0).mean()),
        es99_positive=float(es),
        maximum_signed=float(d[i]),
        maximum_positive=float(max(0, d[i])),
        maximum_location=f"w{i // width}:p{i % width + 1}",
        maximum_ties=int((d == d[i]).sum()),
        tie_policy="first in window/target order",
        half_mass_positions=half,
        half_mass_fraction=half / len(d) if half is not None else None,
        positive_mass=float(cum[-1]),
        exceedance={
            str(t): dict(count=int((d > t).sum()), fraction=float((d > t).mean()))
            for t in (0.01, 0.1, 1.0)
        },
    )


def summarize(values):
    v = np.asarray(values)
    if v.ndim != 3 or v.shape[2] != len(scoring.FIELDS):
        raise ValueError("expected window, target, five-field 68f layout")
    return {
        ref: dict(
            loss=tails(v[:, :, 0] - v[:, :, i], v.shape[1]), kl=tails(v[:, :, i + 2], v.shape[1])
        )
        for ref, i in (("capoff", 1), ("original", 2))
    }


def read_arm(reader, windows, metadata, output):
    """One shared base/cap pass per batch; reader handles any required partial passes.

    Fixed-v5 integration supplies a reader with last_logits_batch, last_capoff,
    events and adapter (base, locality_base, state_hash). The two reference bases
    must be identical for these PC interventions. No class checks are bypassed.
    """
    windows = np.asarray(windows)
    base = reader.adapter.base
    if reader.adapter.locality_base is not base:
        raise ValueError("PC comparison requires unchanged identical original/capoff base")
    if (
        windows.ndim != 2
        or windows.dtype.kind not in "iu"
        or not len(windows)
        or not 2 <= windows.shape[1] <= min(128, base.cfg.n_pos)
        or np.any(windows < 0)
        or np.any(windows >= base.cfg.vocab)
        or metadata["windows_sha256"] != window_hash(windows)
        or metadata["positions"] != windows.size - len(windows)
    ):
        raise ValueError("invalid or changed selected positions")
    out = Path(output)
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    state, weights = reader.adapter.state_hash(), base.checksum(recompute=True)
    values = np.full((*windows[:, :-1].shape, len(scoring.FIELDS)), np.nan, np.float64)
    counts, done = {}, 0
    finish = dict(
        status="failed",
        cost_scope="harm readout only; separate from acquisition/replication",
        selection=metadata,
        state_before=state,
        base_before=weights,
    )
    try:
        for chunk in fv.chunks(windows, reader.batch_size):
            try:
                on = reader.last_logits_batch([r[2] for r in chunk])
                off = reader.last_capoff
                # "v5" is the shared scorer's name for unwrapped logits, including v0.
                scored = scoring.score_configs(
                    on, off, off, np.asarray([r[3] for r in chunk]), [("v5", None)]
                )["v5"]
                for row, (wi, pos, _, _) in zip(scored, chunk, strict=True):
                    values[wi, pos - 1] = row
                done += len(chunk)
            finally:
                fv.aggregate_events(reader.events, counts)
                reader.events.clear()
        if done != metadata["positions"] or not np.isfinite(values).all():
            raise ValueError("incomplete/nonfinite position coverage")
        if reader.adapter.state_hash() != state or base.checksum(recompute=True) != weights:
            raise RuntimeError("readout mutated learner or base")
        with (out / "vectors.npz").open("xb") as f:
            np.savez_compressed(f, values=values)
        result = dict(
            summary=summarize(values),
            selection=metadata,
            fields=list(scoring.FIELDS),
            vectors=dict(
                path=str((out / "vectors.npz").resolve()), sha256=sha(out / "vectors.npz")
            ),
            state_sha256=state,
            base_sha256=weights,
        )
        dump(out / "summary.json", result)
        finish["status"] = "complete"
        return result
    except Exception as exc:
        finish["error"] = f"{type(exc).__name__}: {exc}"
        raise
    finally:
        finish.update(
            positions_completed=done,
            elapsed_process_seconds=time.monotonic() - started,
            query_costs=counts,
        )
        dump(out / "cost.json", finish)


def pair(left, right, output):
    if (
        left["selection"] != right["selection"]
        or left["base_sha256"] != right["base_sha256"]
        or left["fields"] != right["fields"]
    ):
        raise ValueError("paired selection/base/field identities differ")
    arrays = []
    for row in (left, right):
        if sha(row["vectors"]["path"]) != row["vectors"]["sha256"]:
            raise ValueError("arm vectors changed")
        with np.load(row["vectors"]["path"], allow_pickle=False) as f:
            arrays.append(f["values"])
    a, e = arrays
    if a.shape != e.shape or not np.array_equal(a[:, :, 1:3], e[:, :, 1:3]):
        raise ValueError("paired base losses/position coverage differ")
    # Difference of the harms at the SAME positions, not a difference of sorted tails.
    delta = e - a
    with Path(output).open("xb") as f:
        np.savez_compressed(f, values=delta)
    return dict(
        direction="SE-E minus SE-A",
        vectors=dict(path=str(Path(output).resolve()), sha256=sha(output)),
        positionwise=summarize(delta),
        difference_of_arm_es99={
            ref: right["summary"][ref]["loss"]["es99_positive"]
            - left["summary"][ref]["loss"]["es99_positive"]
            for ref in ("capoff", "original")
        },
        interpretation="Descriptive paired positions, not independent experimental replicates. ES99 of paired differences is not difference of ES99s.",
    )


def restore_v0(base, row, bindings, *, smoke=False):
    dest = Path(row["directory"])
    cfg = json.loads((dest / "config.json").read_bytes())
    records = json.loads((dest / "checkpoints.json").read_bytes())
    final = [r for r in records if r["tag"] == "end"]
    if len(final) != 1 or final[0]["items"] != row["items_completed"]:
        raise ValueError("final checkpoint does not cover completed stream")
    snapshot = (
        Path(pccap.ASSETS_ROOT) / "runs" / dest.relative_to(ROOT / "results") / "learner_end.ckpt"
    )
    if sha(snapshot) != final[0]["checkpoint_sha256"]:
        raise ValueError("checkpoint file hash differs")
    st = restore(snapshot.read_bytes(), expected_hash=final[0]["state_hash"])
    if smoke:
        from pccap.cap.cap import Cap, CapConfig

        cap = Cap(
            base,
            CapConfig(
                d=base.d,
                arm="C1",
                credit="adjoint" if row["arm"] == "SE-A" else "error",
                credit_iters=8,
                radii={m: 0.5 for m in (1, 2, 3)},
                bank_scales={m: 1.0 for m in (1, 2, 3)},
            ),
            base.ledger,
        )
    else:
        cap = build_cap(base, row["dataset"], row["arm"], int(cfg["named_seeds"]["seed_cap_init"]))
    cap.import_state(st)
    if (
        cap.state_hash() != final[0]["state_hash"]
        or base.checksum(recompute=True) != cfg["base_hash_before"]
    ):
        raise ValueError("restored state/base identity differs")
    bindings.update(
        {
            str(snapshot): sha(snapshot),
            str(dest / "checkpoints.json"): sha(dest / "checkpoints.json"),
        }
    )
    return cap


def table_block(report):
    text = "## Matched-position ordinary-text harm\n\n"
    text += "CPU fixture only; not an experimental result.\n\n" if report["smoke"] else ""
    text += (
        "Population: "
        + (
            "six synthetic positions per arm"
            if report["smoke"]
            else "Legacy S5: 32 windows × 127 targets = 4,064 positions per arm"
        )
        + ". Fixed prefixes; original = cap-off for the frozen PC base. KL direction is reference || cap. ES99 is the fractional average of the worst 1% positive ΔNLL including zeros; maximum ties use first window/position. Positive-harm half mass is undefined if total harm is zero. No tail-family or independent-token inference.\n\n"
    )
    rows = []
    for c in report["cells"]:
        s = c["readout"]["summary"]["original"]
        loss = s["loss"]
        exc = loss["exceedance"]
        rows.append(
            [
                c["dataset"],
                c["realization"],
                c["order"],
                c["arm"],
                s["kl"]["mean_signed"],
                loss["mean_signed"],
                loss["es99_positive"],
                loss["maximum_signed"],
                loss["maximum_location"],
                *[exc[str(t)]["fraction"] for t in (0.01, 0.1, 1.0)],
                loss["half_mass_positions"],
            ]
        )
    text += table(
        [
            "Dataset",
            "r",
            "order",
            "arm",
            "mean KL",
            "signed ΔNLL",
            "ES99+",
            "max ΔNLL",
            "location",
            "P(>.01)",
            "P(>.1)",
            "P(>1)",
            "half-mass positions",
        ],
        rows,
    )
    text += "\nSE-E − SE-A at identical positions (positive = additional harm from SE-E); no token-level confidence intervals.\n\n"
    text += table(
        [
            "Dataset",
            "r",
            "order",
            "paired mean KL change",
            "paired mean ΔNLL change",
            "ES99+ of paired ΔNLL",
            "difference of arm ES99+",
        ],
        [
            [
                p["dataset"],
                p["realization"],
                p["order"],
                p["positionwise"]["original"]["kl"]["mean_signed"],
                p["positionwise"]["original"]["loss"]["mean_signed"],
                p["positionwise"]["original"]["loss"]["es99_positive"],
                p["difference_of_arm_es99"]["original"],
            ]
            for p in report["pairs"]
        ],
    )
    text += "\nReadout costs are saved per arm in cost.json and at run level in cost.json; add them to the shared 8-hour readout budget, not the replication budget.\n"
    return text


def run(group, output, *, smoke=False, wall_seconds=28800, batch_size=16):
    out = Path(output).resolve()
    if not out.is_relative_to(OUTPUT) or out == OUTPUT:
        raise ValueError(f"new output must be below {OUTPUT}")
    if not 0 < wall_seconds <= 28800 or not 1 <= batch_size <= 32:
        raise ValueError("readout allowance must fit shared 8-hour ceiling; batch size 1..32")
    bindings = {}
    rows = load_group(group, bindings, smoke=smoke)
    expected = json.loads((Path(group) / "plan.json").read_bytes())["cells"]
    _, pairs, _ = compare(rows, expected)  # same paired initial state, stream, calibration and base
    if not rows or any(r["status"] != "complete" for r in rows):
        raise ValueError("readout requires a completed group; no partial-prefix substitution")
    if any(p["status"] != "complete" for p in pairs):
        raise ValueError("both completed arms required before readout")
    import jax

    if smoke:
        if jax.default_backend() != "cpu":
            raise ValueError("smoke is CPU only")
        from aw.pc_harm_smoke import TinyBatchEPC

        base = TinyBatchEPC()
        windows = np.int32([[4, 11, 17, 9], [4, 12, 17, 7]])
        meta = dict(
            mode="cpu_smoke",
            positions=6,
            windows_sha256=window_hash(windows),
            description="Synthetic preselected 64-token-vocabulary fixture, not legacy S5",
        )
        context = nullcontext()
    else:
        from pccap.harness.lease import gpu_lease

        context = gpu_lease(
            "PC-5", stage="additional_work", projected_seconds=wall_seconds, exclusive=True
        )
        windows, meta = selection("v0")
        if any(
            {k: r["pair_identity"]["drift"][k] for k in ("path", "sha256")} != meta["source"]
            for r in rows
        ):
            raise ValueError("readout source differs from acquisition drift source")
    out.mkdir(parents=True, exist_ok=False)
    started = time.monotonic()
    cost = dict(
        status="failed", smoke=smoke, cost_scope="readout only", shared_ceiling_seconds=28800
    )
    report = dict(smoke=smoke, selection=meta, cells=[], pairs=[], sources_sha256=bindings)
    try:
        allowance = min(wall_seconds, CUTOFF - time.time())
        if allowance <= 0:
            raise ValueError("experimental cutoff reached")
        with context as lease, wall_limit(allowance):
            if not smoke:
                if lease.other_cuda_processes() or not any(
                    d.platform == "gpu" for d in jax.devices()
                ):
                    raise RuntimeError("owner needs released CUDA device")
                from pccap.bases.epc import EPCBase

                base = EPCBase.from_npz(archive()["base_checkpoints"]["epc"]["path"], error_lr=0.1)
            paired = {}
            for row in rows:
                cap = restore_v0(base, row, bindings, smoke=smoke)
                reader = V0PositionBatchReader(
                    CellAdapter(cap, "v0_live_C1"), batch_size=batch_size
                )
                name = f"{row['dataset']}-r{row['realization']}-o{row['order']}-{row['arm']}"
                result = read_arm(reader, windows, meta, out / name)
                report["cells"].append(
                    {k: row[k] for k in ("dataset", "realization", "order", "arm", "directory")}
                    | dict(readout=result)
                )
                key = (row["dataset"], row["realization"], row["order"])
                paired.setdefault(key, {})[row["arm"]] = result
            for (ds, r, o), arms in paired.items():
                if set(arms) != {"SE-A", "SE-E"}:
                    raise ValueError("both completed arms required")
                report["pairs"].append(
                    dict(
                        dataset=ds,
                        realization=r,
                        order=o,
                        **pair(arms["SE-A"], arms["SE-E"], out / f"{ds}-r{r}-o{o}-paired.npz"),
                    )
                )
            for path, digest in bindings.items():
                if sha(path) != digest:
                    raise ValueError("input changed during readout")
            if not smoke and selection("v0")[1] != meta:
                raise ValueError("position source changed during readout")
            for path in (
                Path(__file__),
                ROOT / "aw/scoring.py",
                ROOT / "scripts/r1_68f_full_validation.py",
                ROOT / "scripts/r1_68e_batched_drift_v0.py",
            ):
                bindings[str(path)] = sha(path)
            dump(out / "report.json", report)
            (out / "table.md").write_text(table_block(report))
            cost["status"] = "complete"
    finally:
        cost.update(
            elapsed_process_seconds=time.monotonic() - started, completed_arms=len(report["cells"])
        )
        dump(out / "cost.json", cost)
    return report


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--execute", action="store_true")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--wall-seconds", type=float, default=28800)
    p.add_argument("--batch-size", type=int, default=16)
    a = p.parse_args()
    if not a.execute:
        p.error("--execute required; production GPU dispatch belongs to the orchestrator")
    r = run(a.run, a.output, smoke=a.smoke, wall_seconds=a.wall_seconds, batch_size=a.batch_size)
    print(json.dumps(dict(cells=len(r["cells"]), pairs=len(r["pairs"]), smoke=r["smoke"])))


if __name__ == "__main__":
    main()
