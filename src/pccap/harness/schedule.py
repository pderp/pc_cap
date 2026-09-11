"""S4-03: the confirmatory job list (plan §6.10 S4-03; PDF S4).

``python -m pccap.harness.schedule [--manifest manifests/frozen.json] [--out results/S4/jobs.json]``
writes the fixed job order — realization-major, then dataset, then arm-minor, then the five orders —
from the frozen manifest: zsRE and CounterFact C1/C2/CR/B3/B4 × (3 realizations × 5 orders), C0 × 15
at the initial scope 300, grammar C0/C1/C2/CR × 15 (when the grammar dataset id exists); arms marked
`unavailable` in the manifest are listed with status ``unavailable`` and are never run. Each job is a
``pccap run --stage S4 --mode confirm`` invocation; the order is fixed before any result is seen and
``pccap status`` reports completed pairs. The sealed manifest directory comes from the frozen manifest's ``confirm_dir`` field (§4.5 rule 4 firewall: only ``pccap.data.confirm`` names it). The draft manifest may be used to preview the list; running
requires ``manifests/frozen.json`` (§4.5 rule 4).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EDIT_ARMS = ("C1", "C2", "CR", "B3", "B4")


def jobs_from_manifest(man: dict) -> list[dict]:
    avail = man.get("arm_availability", {})
    jobs = []
    grammar_ok = man["dataset_ids"].get("grammar") is not None
    for r in man["realizations"]:
        for ds in ("zsre", "counterfact", "grammar"):
            if ds == "grammar" and not grammar_ok:
                continue
            arms = ("C0", "C1", "C2", "CR") if ds == "grammar" else ("C0",) + EDIT_ARMS
            for arm in arms:
                n = man["stream_lengths"]["c0_initial"] if (arm == "C0" and ds != "grammar") else man["stream_lengths"]["zsre" if ds == "zsre" else "counterfact" if ds == "counterfact" else "grammar_train_count"]
                for perm, oseed in enumerate(man["order_seeds"]):
                    status = "scheduled"
                    if arm in avail and "unavailable" in avail[arm]:
                        status = "unavailable"
                    mpath = f"{man['confirm_dir']}/{ds}_r{r}.json" if ds != "grammar" else "manifests/grammar/streams.json"
                    base = "GRAM" if ds == "grammar" else "BP"
                    jobs.append({"stage": "S4", "dataset": ds, "arm": arm, "base": base, "read": "h", "realization": r, "perm": perm,
                                 "order_seed": oseed, "n_items": n, "status": status, "manifest": mpath,
                                 "cmd": f"pccap run --stage S4 --mode confirm --dataset {ds} --arm {arm} --base {base} --read h --realization {r} --perm {perm} --manifest {mpath}"})
    return jobs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=str(ROOT / "manifests" / "frozen.json"))
    ap.add_argument("--out", default=str(ROOT / "results" / "S4" / "jobs.json"))
    args = ap.parse_args(argv)
    mp = Path(args.manifest)
    if not mp.exists():
        mp = ROOT / "manifests" / "frozen.draft.json"
        print("frozen.json absent: previewing from the draft (not runnable)")
    man = json.loads(mp.read_text())
    jobs = jobs_from_manifest(man)
    out = {"written": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "manifest": str(mp.relative_to(ROOT)),
           "manifest_sha256": hashlib.sha256(mp.read_bytes()).hexdigest(), "draft": bool(man.get("draft")),
           "order_rule": "realization-major, dataset, arm-minor, then the five committed orders; fixed before any result",
           "counts": {"scheduled": sum(j["status"] == "scheduled" for j in jobs), "unavailable": sum(j["status"] == "unavailable" for j in jobs)},
           "jobs": jobs}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out).write_text(json.dumps(out, indent=1))
    print(json.dumps(out["counts"]), "->", args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
