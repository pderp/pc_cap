"""Size policy for the assets repository (lead, 2026-10-10): no committed file above 99 MB.

GitHub refuses single files at 100 MB, so 99 MB is the ceiling for a direct commit from assets/. The pc_cap repository keeps
its own 45 MB rule in scripts/repo_size_policy.py, which is bound by the Stage-4 content lock and is therefore not edited;
this module is the assets-side hook target (assets/.githooks/pre-commit) and reuses the splitter/joiner by import.

Usage (run from the assets working tree):
  python aw/assets_size_policy.py check                     # staged files; exit 1 if any exceeds 99 MB (pre-commit hook)
  python aw/assets_size_policy.py split FILE [--keep]       # FILE.part-NN.<ext> + FILE.index.json (byte parts, sha256-bound)
  python aw/assets_size_policy.py join FILE.index.json OUT  # reassemble; sha256 verified
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from repo_size_policy import join, split  # noqa: E402  (read-only reuse of the frozen helper)

LIMIT_MB = 99
LIMIT = LIMIT_MB * 1000 * 1000  # GitHub counts decimal megabytes; 100 MB = 100,000,000 bytes is refused


def check() -> int:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=AM", "-z"], capture_output=True, check=True).stdout
    names = [n for n in out.decode().split("\0") if n and Path(n).is_file()]
    bad = [(Path(n), Path(n).stat().st_size) for n in names if Path(n).stat().st_size > LIMIT]
    if not bad:
        return 0
    print(f"assets size policy: refusing to commit files larger than {LIMIT_MB} MB (GitHub refuses 100 MB):", file=sys.stderr)
    for p, s in bad:
        print(f"  {s / 1e6:7.1f} MB  {p}", file=sys.stderr)
    print("  split: /home/derp/cap/venv/bin/python /home/derp/cap/pc_cap/aw/assets_size_policy.py split FILE --keep", file=sys.stderr)
    print("  then: git add FILE.part-*.* FILE.index.json  and add the original to .gitignore", file=sys.stderr)
    return 1


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        raise SystemExit(check())
    if cmd == "split":
        raise SystemExit(split(Path(sys.argv[2]), keep="--keep" in sys.argv[3:]))
    if cmd == "join":
        raise SystemExit(join(Path(sys.argv[2]), Path(sys.argv[3])))
    raise SystemExit(__doc__)
