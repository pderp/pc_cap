"""Write the REV-2 pending reviewer tables, with explicit future source paths."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def table(headers, rows):
    return "\n".join("| " + " | ".join(map(str, row)) + " |"
                     for row in [headers, ["---"]*len(headers), *rows]) + "\n\n"


def render():
    register = ROOT / "docs/presentation/deck_v3/pc-result-sources.json"
    sources = json.loads(register.read_text())["sources"]
    text = """# Corrected predictive-coding results — PENDING scaffold

Prepared 2026-09-27 by Capex for charlie and Capstan; **no PC outcomes are populated**.
These are planned tables, not preliminary results. Capstan can fill them after the
complete paired experiments and readouts are verified. Paths below are configured
**future output locations**, not statements that files currently exist. If an
operator chooses another location, update the source register and this page together.

All relative paths below are from `/home/derp/cap/pc_cap/`. Each PENDING entry
contains a source alias and selector; the alias expands to the full path here.
Bracketed dataset, realization and arm values are row filters, not array indices
except `realizations[r]`. No incomplete cell is silently dropped or scored zero.
Use UNAVAILABLE with a reason for a completed but unscorable assay.

## Source register

"""
    aliases = dict(V0="v0_report", H0="v0_harm", V1="v1_run", H1="v1_harm")
    text += table(["Alias", "Configured future path"],
                  [[a, "`"+sources[key]["path"]+"`"] for a, key in aliases.items()])
    text += """V1 cell directories are `<dataset>-r0-o100-<arm>` beneath V1.
`cost.json` next to H0/H1 charges the readout once; nested per-arm costs are
breakdowns of that charge, not additional spend. V0 finish time includes startup,
whereas V1 `finish.json` is stream-engine time and `process.json` includes startup
and lease wait: those two V1 durations must never be added together.

## PC-v0 — primary paired behavior by realization

Exposed historical S5; zsRE 1,000 edits, CounterFact 300; three realizations,
five dependent orders each, 60 planned cells. Differences below are **SE-E − SE-A**;
higher favors SE-E for behavior. `V0:<metric>[dataset,r]` means
`aggregates[dataset,metric].realizations[r]`, the mean paired difference across
the five orders; the native `pairs` table retains every order.

"""
    groups = [(d, r) for d in ("zsre", "counterfact") for r in range(3)]
    metrics = ["ES", "RET-ES", "RET-GS", "LS"]
    text += table(["Dataset", "Realization", *metrics],
                  [[d,r,*[f"PENDING · V0:{m}[{d},{r}]" for m in metrics]] for d,r in groups])
    text += """### Bounded-text secondary behavior, kept separate

The same aggregate selector applies using the exact metric keys below; these
do not replace the legacy primary S5 scoring convention.

"""
    secondary = ["bounded_es_immediate", "bounded_ret_es_end", "bounded_ret_gs_end", "bounded_ls_end"]
    text += table(["Dataset", "Realization", *secondary],
                  [[d,r,*[f"PENDING · V0:{m}[{d},{r}]" for m in secondary]] for d,r in groups])
    text += """### Between-realization summary

Each cell selects `V0:aggregates[dataset,metric].<column>`; min/max are the range
of the three realization means, not a confidence interval.

"""
    text += table(["Dataset", "Metric", "Mean", "Minimum", "Maximum"],
                  [[d,m,*[f"PENDING · V0:aggregates[{d},{m}].{k}" for k in ("mean","minimum","maximum")]]
                   for d in ("zsre","counterfact") for m in metrics])
    text += """### Replication cost by realization

Each entry is the sum of `V0:cells[dataset,realization,arm].finish.elapsed_process_seconds`
over the five planned orders, retaining the ledger in the native report.

"""
    text += table(["Dataset", "Realization", "SE-A process seconds", "SE-E process seconds"],
                  [[d,r,*[f"PENDING · V0:cells[{d},{r},{a}].finish.elapsed_process_seconds (sum)" for a in ("SE-A","SE-E")]]
                   for d,r in groups])
    text += """## Fixed-v5 — the four planned cells

Post hoc transfer check on exposed R1 realization 0, order 100, first 300 edits;
the same BP-trained base and selected reader in both arms, fresh memory per cell.
These four cells are not three independent replications and do not test PC reader
training. Use R1's installed endpoint semantics, including semantic revision.

"""
    v1cells = [(d,a) for d in ("zsre","counterfact") for a in ("SE-A","SE-E")]
    for cp in (100,300):
        text += f"### Checkpoint {cp}\n\n"
        text += table(["Dataset", "Arm", *metrics, "near_miss", "revision"],
                      [[d,a,*[f"PENDING · V1/{d}-r0-o100-{a}/checkpoint-{cp}.json:metrics.{m}.value"
                              for m in (*metrics,"near_miss","revision")]] for d,a in v1cells])
    text += "### Fixed-v5 cost\n\n"
    text += table(["Dataset","Arm","Stream-engine seconds","Whole-process seconds"],
                  [[d,a,*[f"PENDING · V1/{d}-r0-o100-{a}/{file}.json:elapsed_process_seconds"
                          for file in ("finish","process")]] for d,a in v1cells])
    text += """## Ordinary-text harm — per-arm and paired summaries

H0: final snapshots, 4,064 fixed target positions per cell; H1: final 300-edit
snapshots, 245,237 fixed target positions per cell. These inventories differ and
must not be pooled. Positive signed changes are worse. Both arms use identical
positions and the same original reference within each paired study.

For H0 realization rows, average the **five cell summaries**, and keep every
order in the native readout; do not recalculate a pooled tail and call it their
mean. H1 has one order per dataset. `S[dataset,r,arm]` expands to
`cells[dataset,realization,arm].readout.summary.original`; `P[dataset,r]` expands
to `pairs[dataset,realization]`. Every following entry identifies H0 or H1.
The maximum shown is a mean of cell maxima where five orders exist, not a pooled
maximum; the native report retains the actual maxima and position locations.

"""
    fields = ["kl.mean_signed", "loss.mean_signed", "loss.es99_positive", "loss.maximum_signed",
              "loss.exceedance['0.01'].fraction", "loss.exceedance['0.1'].fraction", "loss.exceedance['1.0'].fraction",
              "loss.half_mass_positions"]
    paired = ["positionwise.original.kl.mean_signed", "positionwise.original.loss.mean_signed",
              "positionwise.original.loss.es99_positive", "difference_of_arm_es99.original"]
    for alias, rows in (("H0",groups),("H1",[(d,0) for d in ("zsre","counterfact")])):
        text += f"### {alias} arm summaries\n\n"
        for selected in (fields[:4], fields[4:]):
            text += table(["Dataset","Realization","Arm",*selected],
                          [[d,r,a,*[f"PENDING · {alias}:S[{d},{r},{a}].{key}"
                                    for key in selected]] for d,r in rows for a in ("SE-A","SE-E")])
        text += f"### {alias} matched differences — SE-E minus SE-A\n\n"
        text += table(["Dataset","Realization",*paired],
                      [[d,r,*[f"PENDING · {alias}:P[{d},{r}].{key}" for key in paired]] for d,r in rows])
    text += """**Keep the last two paired columns distinct:** the ES99 of positive
positionwise loss differences is not the difference of arm ES99 values. The
latter is the efficacy–harm slide slot; the former is additional paired detail.
Retain zero positions and the fractional expected-shortfall boundary.

"""
    text += table(["Readout","Charged readout process seconds"],
                  [[a,f"PENDING · {a}:../cost.json:elapsed_process_seconds"] for a in ("H0","H1")])
    text += """## Completion notes for Capstan

Require all 60 v0 and all four fixed-v5 cells, both final readouts, matching
source/model/data/position identities and complete cost receipts before filling
their respective result tables. Record the actual source file hashes and report
locations; no CPU-smoke outputs or partial-run effects belong here. Preserve
every unfavorable, null and unavailable result. Present effect sizes and the
three v0 realization values before choosing the spoken interpretation.

The claim ledger and timed talk scripts remain pending at their PC slots until
these complete reports exist. The supplied streams are exposed; token positions
and five orders are not independent experimental replicates. Empirical severe
loss and concentration do not establish a power law, a heavy-tail family,
autonomous active inference, or robustness to unseen extremes.
"""
    return text


def main():
    content = render()
    paths = [ROOT / "docs/presentation/review-results-pending.md",
             ROOT.parent / "assets/presentation-materials/review-data/results.md"]
    for path in paths:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("x") as f:
            f.write(content)
    print(json.dumps(dict(paths=list(map(str,paths)), sha256=hashlib.sha256(content.encode()).hexdigest())))


if __name__ == "__main__":
    main()
