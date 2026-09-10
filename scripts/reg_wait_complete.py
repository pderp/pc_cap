"""Wait for the REG-02 run to reach a terminal state (R2-01 repair: never key on a historical log substring).

Polls ``results/REG/<run>/summary.json`` (written at the end of every chunk) until its ``status`` is
terminal. Exit 0 only for ``completed`` with the final checkpoint present (``kind == "final"``,
``global_step == total_steps``); exit 1 for an abort status; keeps waiting on ``paused_*``.
Prints one line per state change. ``--once`` reports the current state and exits 3 if not terminal.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERMINAL_ABORT = {"prompt_kl_abort", "relaxation_divergence", "unreachable_terminal_tau"}


def state(run: str) -> tuple[str, dict]:
    p = ROOT / "results" / "REG" / run / "summary.json"
    if not p.exists():
        return "absent", {}
    s = json.loads(p.read_text())
    st = s.get("status", "?")
    if st == "completed":
        ck = Path(s["checkpoint_dir"]) / f"final-{int(s['total_steps']):06d}"
        if not (ck / "state.json").exists():
            return "completed_missing_checkpoint", s
        meta = json.loads((ck / "state.json").read_text())
        if meta.get("kind") != "final" or int(meta.get("global_step", -1)) != int(s["total_steps"]):
            return "completed_bad_checkpoint", s
        return "completed", s | {"final_checkpoint": str(ck)}
    return st, s


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", default="epc-50m")
    ap.add_argument("--poll", type=float, default=60.0)
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args(argv)
    last = None
    while True:
        st, s = state(a.run)
        if st != last:
            print(time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "REG state:", st, "step", s.get("global_step"), flush=True)
            last = st
        if st == "completed":
            print("FINAL_CHECKPOINT", s["final_checkpoint"], flush=True)
            return 0
        if st in TERMINAL_ABORT or st.startswith("completed_"):
            print("ABORT_OR_INVALID", st, s.get("abort_reason", ""), flush=True)
            return 1
        if a.once:
            return 3
        time.sleep(a.poll)


if __name__ == "__main__":
    sys.exit(main())
