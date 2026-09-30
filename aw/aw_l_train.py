"""AW-L5: shared v5 training recipe with the approved upper-read/full-write factorial."""

from __future__ import annotations

import json

from aw.interface import ALL
from aw.pc_reader_train import ROOT, execute_training, parser, recipe, source_hashes
from aw.trained_reader_eval import execute_evaluation

OUTPUT = ROOT / "results/additional_work/AW-L"


def plan():
    return dict(
        recipe=recipe(),
        sources_sha256=source_hashes(),
        model_execution=False,
        trainings=[
            dict(rule="bp", seed=seed, read_taps=read)
            for seed in (0, 1, 2)
            for read in (ALL, (2, 3))
        ],
        evaluations=[
            dict(
                seed=seed,
                read_taps=read,
                write_sites=write,
                dataset=ds,
                realization=0,
                order=100,
                checkpoints=[100, 300],
                acquisition="adjoint",
            )
            for seed in (0, 1, 2)
            for read in (ALL, (2, 3))
            for write in (ALL, (3,))
            for ds in ("zsre", "counterfact")
        ],
        training_write_sites=ALL,
        checkpoint_policy="fixed mean of steps150/200/250/300",
        read_initialization="same full parameter tree per seed, then remove tap1 only",
        write_pairing="same trained reader in both write arms; reacquire fresh memory and keys",
        ceiling_seconds=48 * 3600,
        profile_required=True,
        optional_read_sets_admitted=False,
    )


def main():
    p = parser()
    p.add_argument("--read", choices=("all", "upper"), default="all")
    p.add_argument("--write", choices=("all", "last"), default="all")
    a = p.parse_args()
    if a.rule != "bp":
        raise ValueError("AW-L uses BP training; PC training is the separate PC-15 comparison")
    taps = ALL if a.read == "all" else (2, 3)
    sites = ALL if a.write == "all" else (3,)
    if a.command == "plan":
        print(json.dumps(plan(), indent=2))
    elif a.command == "evaluate":
        execute_evaluation(a, write_sites=sites, output_root=OUTPUT)
    else:
        if sites != ALL:
            raise ValueError(
                "training uses the same full-write objective; masks vary only in evaluation"
            )
        execute_training(a, read_taps=taps, output_root=OUTPUT)


if __name__ == "__main__":
    main()
