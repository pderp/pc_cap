"""New supplemental evaluation (family EXT): the six saved PC-reader caps on the sealed MQuAKE stream.

    python -m aw.extremes.mquake_eval --rule bp --seed 0 --execute

Reuses the frozen study's engine unchanged (``aw.trained_reader_eval.run_stream``: installed R1 semantics, fresh
acquisition, checkpoints 100 and 300, locality / near-miss / revision / unseen endpoints, strict restoration) plus the
registered composition endpoint (``CellAssays.composition`` with the declared fresh start state, as the Stage-4 backend
ran it) and the full 245,237-position harm assay (``aw.pc_harm_readout.read_arm``). The population is the sealed
R1_learned_ff MQuAKE recipe, realization 0, order 100, 300 edits (the same realization/order as the zsRE and
CounterFact PC-reader evaluations). Outputs: results/extremes_analysis/ext-20261009/mquake_eval/eval-<rule>-s<seed>-mquake/
(stream/, composition.json, harm/, report.json, cost.json) and snapshots under assets/extremes_analysis/ext-20261009/checkpoints/.

This is not a registered Stage-4 cell and it does not retroactively fill any unavailable registered contrast.
The frozen study's evaluator is not called because it binds the 9 October 17:00 EDT cutoff and requires a development
profile that MQuAKE never had; the shared engine functions it wraps are called directly.
"""

from __future__ import annotations

import pccap  # noqa: F401  # isort: skip

import argparse
import json
import resource
import time

import numpy as np

from aw.extremes import models as M
from aw.extremes.common import DATA, OUT, RUN_ID, Status, atomic_json, git_head, log_line, now, sha
from aw.extremes.probes import build_probes  # noqa: F401  (import keeps probe/payload identities in one place)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rule", required=True, choices=["bp", "epc"])
    ap.add_argument("--seed", required=True, type=int, choices=[0, 1, 2])
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--execute", action="store_true")
    a = ap.parse_args(argv)
    if not a.execute:
        raise SystemExit("GPU evaluation requires --execute")
    from aw.interface_readout import InterfacePositionBatchReader
    from aw.pc_harm_readout import read_arm, selection
    from aw.pc_reader_train import memory_guard, device_memory
    from aw.pc_v0 import blocking_cuda_processes
    from aw.pc_v1_run import metrics
    from aw.trained_reader_eval import run_stream, sources
    from pccap.harness.lease import gpu_lease
    from pccap.revision_v1.endpoints_composition import as_edit
    from pccap.revision_v1.stage4_assays import CellAssays

    out = OUT / "mquake_eval" / f"eval-{a.rule}-s{a.seed}-mquake"
    resources = DATA / "checkpoints" / "mquake_eval" / f"eval-{a.rule}-s{a.seed}-mquake"
    if out.exists() or resources.exists():
        raise FileExistsError(f"new output required: {out}")
    out.mkdir(parents=True)
    resources.mkdir(parents=True)
    t0 = time.monotonic()
    receipt = dict(status="failed", run_id=RUN_ID, family="EXT", scope="construction + acquisition/endpoints + composition + harm; components are subsets", code_sha=git_head(), started=now())
    try:
        with gpu_lease(f"{RUN_ID} mquake_eval {a.rule} s{a.seed}", stage="extremes", projected_seconds=4 * 3600, exclusive=True) as lease:
            others = lease.other_cuda_processes()
            if blocking_cuda_processes(others):
                raise RuntimeError("another project process holds the GPU: " + json.dumps(others))
            memory_guard()
            adapter, cap, tok, identity = M.load_reader(a.rule, a.seed, "mquake")
            pay, pay_binding = M.payload("mquake")
            if len(pay["items"]) != 300:
                raise ValueError("sealed MQuAKE stream must hold 300 items")
            for kind, expected in (("locality", 50), ("near_miss", 100), ("revision", 50), ("unseen", 100), ("composition", 80)):
                ep = pay["endpoints"][kind]
                ids = ep["expected_ids"]
                if len(ids) != expected or len(set(ids)) != expected or [r.get("item_id", r.get("composition_id")) for r in ep["rows"]] != ids:
                    raise ValueError("endpoint coverage/order differs: " + kind)
            context = dict(training=identity["training"], dataset="mquake", rule=a.rule, seed=a.seed, development=False,
                           population="new supplemental (ext-20261009): sealed R1_learned_ff MQuAKE realization 0 order 100, 300 edits",
                           source_recipe=identity["recipe"], payload_recipe=identity["recipe"], payload=pay_binding, sources_sha256=sources(), run_id=RUN_ID, family="EXT")
            fresh_state = cap.export_state().clone()
            stream = run_stream(adapter, tok, pay, [100, 300], out / "stream", resources / "stream", context)
            # Registered composition endpoint, as the Stage-4 backend ran it: independent fresh start state per case.
            assays = CellAssays(adapter, tok, max_new=32)
            state_before = cap.state_hash()
            items = [as_edit(r, tok) for r in pay["items"]]
            t1 = time.monotonic()
            comp = assays.composition(pay["endpoints"]["composition"], items, fresh_state)
            if cap.state_hash() != state_before:
                raise RuntimeError("composition changed the stream memory")
            comp["elapsed_process_seconds"] = time.monotonic() - t1
            atomic_json(out / "composition.json", comp)
            adapter.reset_queries()
            windows, meta = selection("v5")
            reader = InterfacePositionBatchReader(adapter, batch_size=a.batch_size, guard=memory_guard,
                                                  treatment=dict(reader_rule=a.rule, seed=a.seed, read_taps=list(cap.interface.read_taps), write_sites=list(cap.interface.write_sites), acquisition="adjoint"))
            harm = read_arm(reader, windows, meta, out / "harm")
            with np.load(harm["vectors"]["path"], allow_pickle=False) as f:
                changed = float((f["values"][:, :, 3] > 1e-9).mean())
            cp300 = json.loads((out / "stream" / "checkpoint-300.json").read_bytes())
            report = dict(context, status="complete", read_taps=list(cap.interface.read_taps), write_sites=list(cap.interface.write_sites), stream=stream,
                          composition_summary=comp["summary"], metrics_300=cp300["metrics"], harm=harm, changed_distribution_fraction=changed,
                          gate_telemetry=reader.telemetry, interface_accounting=cap.interface_accounting(), device_memory=device_memory(), other_cuda_processes=others)
            if sources() != context["sources_sha256"]:
                raise ValueError("evaluation sources changed during execution")
            atomic_json(out / "report.json", report)
            receipt["status"] = "complete"
    except BaseException as exc:
        receipt["error"] = repr(exc)
        raise
    finally:
        receipt.update(elapsed_process_seconds=time.monotonic() - t0, peak_host_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024, finished=now())
        atomic_json(out / "cost.json", receipt)
        log_line("mquake_eval", f"{a.rule} s{a.seed} {receipt['status']} {receipt['elapsed_process_seconds']:.0f}s")
    Status().artifact(f"mquake_eval/{a.rule}_s{a.seed}", out / "report.json", rule=a.rule, seed=a.seed, seconds=receipt["elapsed_process_seconds"])
    print(json.dumps(dict(status=receipt["status"], seconds=receipt["elapsed_process_seconds"], metrics={k: v["value"] for k, v in report["metrics_300"].items()}, composition=comp["summary"]["evaluated_fraction"])))


if __name__ == "__main__":
    main()
