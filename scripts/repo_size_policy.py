"""Repository size policy: no committed file above 45 MB (GitHub warns at 50 MB, refuses at 100 MB).

Usage:
  python scripts/repo_size_policy.py check            # staged files; exit 1 if any exceeds the limit (pre-commit hook)
  python scripts/repo_size_policy.py split FILE.json  # split a large JSON file into FILE.part-NN.json + FILE.index.json, remove FILE
  python scripts/repo_size_policy.py join FILE.index.json OUT.json   # reassemble (byte-identical; sha256 checked)

Splitting is only for JSON that genuinely belongs in the repository (results, manifests). Synthetic test fixtures and
regenerable outputs belong in .gitignore'd directories or under assets/, never in git.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

LIMIT = 45 * 1024 * 1024
PART = 40 * 1024 * 1024


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check() -> int:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=AM", "-z"], capture_output=True, check=True).stdout
    bad = [(Path(n), Path(n).stat().st_size) for n in out.decode().split("\0") if n and Path(n).is_file() and Path(n).stat().st_size > LIMIT]
    if not bad:
        return 0
    print("repo size policy: refusing to commit files larger than 45 MB:", file=sys.stderr)
    for p, s in bad:
        print(f"  {s / 1e6:7.1f} MB  {p}", file=sys.stderr)
    print("  synthetic / regenerable outputs: move under assets/ or an ignored directory (.gitignore);", file=sys.stderr)
    print("  genuine JSON artifacts: python scripts/repo_size_policy.py split FILE.json  (then git add the parts + index)", file=sys.stderr)
    return 1


def split(path: Path) -> int:
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    parts = [raw[i:i + PART] for i in range(0, len(raw), PART)]
    names = []
    for i, chunk in enumerate(parts):
        q = path.with_name(f"{path.stem}.part-{i:02d}{path.suffix}")
        q.write_bytes(chunk)
        names.append({"path": q.name, "bytes": len(chunk), "sha256": hashlib.sha256(chunk).hexdigest()})
    index = path.with_name(f"{path.stem}.index.json")
    index.write_text(json.dumps({"policy": "scripts/repo_size_policy.py split (byte parts; concatenate in order)", "original": path.name, "bytes": len(raw), "sha256": digest, "parts": names}, indent=1))
    path.unlink()
    print(f"split {path} ({len(raw) / 1e6:.1f} MB) into {len(parts)} parts; index {index}")
    return 0


def join(index: Path, out: Path) -> int:
    meta = json.loads(index.read_text())
    data = b"".join((index.parent / p["path"]).read_bytes() for p in meta["parts"])
    if hashlib.sha256(data).hexdigest() != meta["sha256"]:
        raise SystemExit("reassembled bytes do not match the recorded sha256")
    out.write_bytes(data)
    print(f"wrote {out} ({len(data) / 1e6:.1f} MB), sha256 verified")
    return 0


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "check":
        raise SystemExit(check())
    if cmd == "split":
        raise SystemExit(split(Path(sys.argv[2])))
    if cmd == "join":
        raise SystemExit(join(Path(sys.argv[2]), Path(sys.argv[3])))
    raise SystemExit(__doc__)
