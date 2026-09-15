"""DEC-049 companion: average the saved step checkpoints of a training run (uniform weight average of theta_step<N>.npz for the
listed steps) into theta_avg<first>-<last>.npz. Checkpoint trajectories show the null boundary oscillating between checkpoints
(unseen false fires 57 -> 6 -> 40 -> 51 -> 8 -> 19 over steps 50..300 for one seed); a weight average is a standard, cheap
stabiliser and enters the selection as one more candidate per run, evaluated on the same common populations.
    python scripts/r1_71_average_checkpoints.py --run r1_50_stream_sel4_text_s0 --steps 150,200,250,300"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path

import numpy as np

ASSETS = Path("/home/derp/cap/assets/runs/pc_cap/R1/pilot")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--steps", default="150,200,250,300")
    a = ap.parse_args()
    steps = [int(x) for x in a.steps.split(",")]
    files = [ASSETS / a.run / f"theta_step{s}.npz" for s in steps]
    for f in files:
        if not f.exists():
            raise SystemExit(f"missing checkpoint {f}")
    out = ASSETS / a.run / f"theta_avg{steps[0]}-{steps[-1]}.npz"
    if out.exists():
        raise SystemExit(f"{out} exists")
    arrs = [np.load(f) for f in files]
    keys = arrs[0].files
    avg = {k: np.mean(np.stack([np.asarray(z[k], np.float64) for z in arrs]), axis=0).astype(arrs[0][k].dtype) for k in keys}
    np.savez(out, **avg)
    print({"out": str(out), "sha256": hashlib.sha256(out.read_bytes()).hexdigest()[:16], "steps": steps, "sources": [hashlib.sha256(f.read_bytes()).hexdigest()[:12] for f in files]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
