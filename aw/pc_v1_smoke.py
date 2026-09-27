"""Persist the PC-7 two-arm tiny CPU fixture, never a research result."""

import pccap  # noqa: F401 # isort: skip

# isort: split

import argparse
from pathlib import Path

import jax

from aw import pc_v1_run as r
from aw.tests.test_pc_v1_run import adapter, fixture


def generate(output):
    if jax.default_backend() != "cpu":
        raise ValueError("tiny smoke requires CPU")
    out, resources = r.new_path(output)
    out.mkdir(parents=True)
    cells = [dict(dataset="zsre", realization=0, order=100, arm=a, items=2) for a in r.ARMS]
    r.dump(
        out / "plan.json",
        dict(
            population="cpu_smoke",
            cells=cells,
            sources=r.sources(),
            qualifications="64-token tiny base; one delta step; two generated tokens; checkpoints 1/2",
        ),
    )
    tok, items, endpoints = fixture()
    for c in cells:
        r.execute_stream(
            adapter(c["arm"]),
            tok,
            items,
            endpoints,
            [1, 2],
            out / r.cell_name(c),
            resources / r.cell_name(c),
            dict(cell=c, population="cpu_smoke", sources=r.sources()),
            max_new=2,
        )
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    print(generate(parser.parse_args().output))
