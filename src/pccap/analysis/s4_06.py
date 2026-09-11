"""S4-06: frozen paired analysis over the confirmatory runs (plan §6.10 S4-06; PDF D.11; ANA-01).

Collects every ``results/S4/<arm>/<base>/<read>/<realization>/<perm>/`` run of one dataset into the
item-level table ``pccap.analysis.paired.analyze_paired`` expects — ``arm, realization, order, item_id,
ret_gs, es, ls`` — where RET-GS and RET-ES per item come from the endpoint rescoring rows
(``checkpoints.json`` tag ``end``), ES from ``items.jsonl`` (immediate), and LS is the run's
endpoint complete-answer locality agreement repeated on every row of that run (LS is a stream-level
quantity; its per-run mean is what the constraint reads). ``expected_items`` comes from the sealed
realization manifests through the loader (never read directly here). Writes
``results/S4/paired_<dataset>.json`` and a markdown summary with the classification (DEC-009 policy).

    python -m pccap.analysis.s4_06 --dataset zsre [--root results/S4] [--seed 0]
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from pccap.analysis.paired import analyze_paired

ROOT = Path(__file__).resolve().parents[3]


def collect_rows(root: Path, dataset: str, experiment_id: str | None = None) -> tuple[list[dict], list[str]]:
    """Endpoint rows of the runs of one dataset. With ``experiment_id`` only runs carrying exactly that id are
    collected (a run with no id is unknown provenance: listed in the notes, never included — V2-02). Without a filter,
    the discovered runs must all belong to one experiment; several ids are an error, never a silent merge (V2-03)."""
    rows, notes = [], []
    seen_ids: set = set()
    for mp in sorted(root.rglob("metrics.json")):
        if ".superseded-" in str(mp):
            continue  # archived attempt (V-03): never collected
        d = mp.parent
        m = json.loads(mp.read_text())
        cfg = m.get("config", {})
        if cfg.get("dataset") != dataset:
            continue
        run_id = cfg.get("experiment_id")
        if experiment_id is not None and run_id != experiment_id:
            if run_id is None:
                notes.append(f"{d}: no experiment_id in its config (unknown provenance); excluded from experiment {experiment_id}")
            continue
        seen_ids.add(run_id)
        if experiment_id is None and len(seen_ids) > 1:
            raise ValueError(f"runs under {root} belong to several experiments {sorted(map(str, seen_ids))}; pass experiment_id (V2-03)")
        arm, r, o = m["arm"], int(cfg["realization"]), int(cfg["perm"])
        items = {json.loads(line)["item_id"]: json.loads(line) for line in (d / "items.jsonl").read_text().splitlines() if line.strip()}
        ck = json.loads((d / "checkpoints.json").read_text())
        end = next((c for c in ck if c["tag"] == "end"), None)
        if end is None:
            notes.append(f"{d}: no endpoint rescoring (status {m.get('status')}); rows omitted → incomplete pair")
            continue
        ls = end["locality"]["ls_complete_answer"]
        for row in end["rows"]:
            it = items.get(row["item_id"], {})
            rows.append({"arm": arm, "realization": r, "order": o, "item_id": row["item_id"], "ret_gs": row["ret_gs"], "es": it.get("es"), "ls": ls,
                         "ret_es": row["ret_es"], "stream_id": dataset})
        if m.get("status") != "complete":
            notes.append(f"{d}: status {m.get('status')} — completed prefix only ({len(end['rows'])} items)")
    return rows, notes


def expected_from_loader(dataset: str) -> dict | None:
    try:
        from pccap.data.confirm import load as load_confirm
    except Exception:
        return None
    frozen = ROOT / "manifests" / "frozen.json"
    if not frozen.exists():
        return None
    fz = json.loads(frozen.read_text())
    exp = {}
    for r in fz["realizations"]:
        man = load_confirm(Path(fz["confirm_dir"]) / f"{dataset}_r{r}.json", frozen=frozen)
        from pccap.data.selection import subset_ids

        exp[r] = subset_ids(man, int(fz["stream_lengths"][dataset]))  # the same subset every order edits (selection rule)
    return exp


def render(rep: dict, dataset: str, notes: list[str]) -> str:
    L = [f"# Frozen paired analysis — {dataset} (S4-06)", "", f"Rendered {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}; policy DEC-009; `pccap.analysis.paired` (ANA-01).", "",
         f"**Classification: {rep.get('classification')}**", ""]
    for c, v in rep.get("contrasts", {}).items():
        L.append(f"- {c}: " + json.dumps({k: v[k] for k in v if k in ("ret_gs", "es", "ls", "status")}, default=float)[:600])
    if notes:
        L += ["", "Notes:", *[f"- {n}" for n in notes]]
    return "\n".join(L) + "\n"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", required=True)
    ap.add_argument("--root", default=str(ROOT / "results" / "S4"))
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None)
    ap.add_argument("--experiment-id", default=None, help="collect only runs of this frozen experiment id (V-03)")
    args = ap.parse_args(argv)
    rows, notes = collect_rows(Path(args.root), args.dataset, args.experiment_id)
    exp = expected_from_loader(args.dataset)
    rep = analyze_paired(rows, seed=args.seed, stream_id=args.dataset, expected_items=exp)
    out = Path(args.out) if args.out else ROOT / "results" / "S4" / f"paired_{args.dataset}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"dataset": args.dataset, "rows": len(rows), "expected_items_from_loader": exp is not None, "notes": notes, "report": rep}, indent=1, allow_nan=False) + "\n")
    out.with_suffix(".md").write_text(render(rep, args.dataset, notes))
    print(args.dataset, "rows", len(rows), "classification", rep.get("classification"), "->", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
