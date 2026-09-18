"""Ingest completed chain R and list actual receipt-v4 prerequisites; no admission."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from scripts import r1_68f_full_validation as full
from scripts.r1_d10a_review import write_new

ROOT = full.ROOT


def read(binding):
    return json.loads(full.checked(binding).read_text())


def audit():
    cost_ref = full.ref(ROOT / "docs/tasks/R1-cost-after-chain-R.json")
    host_ref = full.ref(ROOT / "docs/tasks/R1-host-peaks-after-chain-R.json")
    cost, hosts = read(cost_ref), read(host_ref)
    rows = []
    for key, host in sorted(hosts["rows"].items()):
        if host["method"] != "direct_gnu_time":
            continue
        recipe, result = read(host["recipe"]), read(host["result"])
        if result["status"] != "complete" or result["manifest_sha256"] != host["recipe"]["sha256"]:
            raise ValueError("completed chain R recipe/result mismatch")
        receipt_ref = full.ref(Path(result["attempt_dir"]) / "checkpoint-300.receipt.json")
        receipt = read(receipt_ref)
        if (
            receipt["manifest_sha256"] != host["recipe"]["sha256"]
            or receipt["receipt_sha256"] != result["last_receipt_sha256"]
        ):
            raise ValueError("chain R final receipt differs")
        cp = read(receipt["report"])
        if cp["checkpoint"] != 300 or cp["state_sha256"] != receipt["state_sha256"]:
            raise ValueError("chain R checkpoint/state differs")
        ep = cp["endpoints"]
        for name, count in (("near_miss", 100), ("revision", 50)):
            if len(ep[name]["expected_ids"]) != count or len(ep[name]["rows"]) != count:
                raise ValueError("chain R incomplete challenge population")
        for name in ("source", "snapshot"):
            full.checked(host[name])
        timers = result["phase_timer_summary"]
        rows.append(
            dict(
                key=key,
                recipe=host["recipe"],
                result=host["result"],
                checkpoint_receipt=receipt_ref,
                report=receipt["report"],
                status="complete_300_edit_development_profile",
                sample_positions=ep["drift"]["scored_positions"],
                full_validation_measured="full_validation" in ep,
                attempt_wall_seconds=result["attempt_wall_seconds"],
                sampled_drift_operation_seconds=timers["drift"]["operation_seconds"],
                sampled_drift_phase_count=timers["drift"]["count"],
                challenge_operation_seconds=sum(
                    timers[k]["operation_seconds"] for k in ("near_miss", "revision")
                ),
                measured_peak_host_mib=host["measured_peak_host_mib"],
                retention=dict(
                    n=len(cp["retention"]["rows"]),
                    ret_es=sum(r["es"] for r in cp["retention"]["rows"])
                    / len(cp["retention"]["rows"]),
                    ret_gs=sum(r["gs"] for r in cp["retention"]["rows"])
                    / len(cp["retention"]["rows"]),
                ),
                host_evidence={k: host[k] for k in ("method", "source", "snapshot")},
                near_miss_summary=ep["near_miss"].get("summary"),
                revision_summary=ep["revision"].get("summary"),
                source_code_sha256=recipe["code_sha256"],
            )
        )
    expected = {f"{c}:{d}" for c in ("R1_learned_ff", "v0_stable") for d in ("zsre", "mquake")}
    if {r["key"] for r in rows} != expected:
        raise ValueError("all four chain R profiles required")
    transfers = []
    for cell in cost["cells"]:
        evidence = read(cell["measurement"])
        if evidence.get("endpoint_transfer_proposal"):
            transfers.append(
                dict(
                    key=f"{cell['condition']}:{cell['dataset']}",
                    proposal=evidence["endpoint_transfer_proposal"],
                )
            )
    return dict(
        task="R1-58k",
        status="preparation_only_not_receipt_v4",
        lead_approved=False,
        producer=full.ref(__file__),
        cost_receipt_v3=cost_ref,
        host_evidence=host_ref,
        host_methods=dict(Counter(r["method"] for r in hosts["rows"].values())),
        chain_R=rows,
        existing_pending_evidence=cost["pending_evidence"],
        existing_endpoint_transfer_proposals=transfers,
        DEC063_population=full.make_spec(),
        remaining_non_signature_dependencies=[
            "Owner applies reviewed R1-68f driver and sealed-fork hooks, rebuilds identities and runs four R1-64g cells.",
            "Use full_validation outer phase wall (not only model-operation time), lifetime host/JAX peaks and exact finite NPZ coverage from those runs.",
            "Budget the newly required sampled phase at intermediate checkpoints too: chain R contains only one sampled drift phase per cell.",
            "The v3 receipt still lists 14 missing full near/revision condition-by-dataset measurements; its class transfer proposals are unreviewed.",
            "CounterFact full-validation transfer and other unmeasured-class transfers require explicit measured basis and a typed validator policy. S1 uses an additional distinct original-base forward, absent from these four measurements.",
            "Refresh wall ceilings, expected process-hours and concurrency schedule including DEC-063; the old 254.7825-hour estimate omits this endpoint.",
            "Production runtime/assembler must retain and require full_validation: R1-63j RUNTIME_KEYS currently discards it. Reconcile frozen population and analysis to report it separately from the sampled talk statistics.",
            "Rebuild candidate v14/forms v9/sheet v8 after source and cost evidence stabilize. A real unsigned preview must disclose missing draw/seal/signatures; no forged inputs to force a successful assembly.",
        ],
        downstream=dict(
            R1_63k="waiting_for_real_inputs_v9",
            X19="waiting_for_candidate_v14",
            HT_4f="waiting_for_signed_cost_receipt_v4",
        ),
        gpu_seconds=0,
        actual_draws=0,
        seals=0,
        signatures=0,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(write_new(args.output, audit()), indent=2))
