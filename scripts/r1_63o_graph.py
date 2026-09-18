"""Read-only recursive binding inventory, not a historical-provenance rewrite.

Walk explicit bindings and path-keyed SHA maps in JSON. Hash other resources as
opaque bytes; do not parse JSONL rows or open protected targets. A stale edge is
reported, not traversed as if current bytes were the expected historical bytes.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CAP = ROOT.parent
HEX = re.compile(r"^[0-9a-f]{64}$")
MAP_NAMES = {
    "bindings_sha256", "sources_sha256", "analysis_source_sha256",
    "source_bindings_sha256", "src_pccap_files",
}


def sha(path):
    with Path(path).open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def local(name):
    path = Path(name)
    path = (ROOT / path).resolve() if not path.is_absolute() else path.resolve()
    if not path.is_relative_to(CAP) or any(
        p in path.parts for p in ("confirm", "stage4_sealed_payloads")
    ):
        raise PermissionError("only unsealed workspace dependencies: " + str(path))
    return path


def pointer(key):
    return str(key).replace("~", "~0").replace("/", "~1")


def is_binding(value):
    return isinstance(value, dict) and isinstance(value.get("path"), str) and bool(
        HEX.fullmatch(str(value.get("sha256", "")))
    )


def is_path_key(name):
    # Named content identities (e.g. dev_v3) are not filesystem bindings.
    return "/" in name or Path(name).suffix in {".py", ".json", ".jsonl", ".md", ".pdf", ".npz", ".npy"}


def edges(value, where=""):
    """Explicit path/SHA records and path-keyed inventories, without opening targets."""
    if isinstance(value, dict):
        if is_binding(value):
            yield {"path": value["path"], "sha256": value["sha256"]}, where, "record"
        for key, child in value.items():
            if key in MAP_NAMES and isinstance(child, dict) and not is_binding(child):
                for name, digest in child.items():
                    if isinstance(digest, str) and HEX.fullmatch(digest) and is_path_key(name):
                        yield dict(path=name, sha256=digest), where + "/" + pointer(key) + "/" + pointer(name), "map"
                    elif isinstance(digest, (dict, list)):
                        yield from edges(digest, where + "/" + pointer(key) + "/" + pointer(name))
            else:
                yield from edges(child, where + "/" + pointer(key))
    elif isinstance(value, list):
        for i, child in enumerate(value):
            yield from edges(child, where + "/" + str(i))


def scan(bindings):
    pending = [(b, None, "") for b in bindings]
    seen, failures, inventory, count = set(), [], {}, 0
    while pending:
        binding, parent, location = pending.pop()
        try:
            path = local(binding["path"])
        except PermissionError as error:
            failures.append(dict(parent=parent, pointer=location, binding=binding,
                                 current=None, reason=str(error)))
            continue
        key = (str(path), binding["sha256"])
        count += 1
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            failures.append(dict(parent=parent, pointer=location, binding=binding, current=None))
            continue
        actual = sha(path)
        inventory[str(path)] = actual
        if actual != binding["sha256"]:
            failures.append(dict(parent=parent, pointer=location, binding=binding, current=actual))
            continue
        if path.suffix == ".json":
            value = json.loads(path.read_bytes())
            try:
                pending.extend((b, str(path), p) for b, p, _kind in edges(value))
            except PermissionError as error:
                failures.append(dict(parent=str(path), pointer="protected_metadata_edge",
                                     current=None, reason=str(error)))
    return dict(resources=len(inventory), references=count, stale=failures, bindings_sha256=inventory)


def write(path, value):
    path = Path(path)
    raw = value if isinstance(value, bytes) else (
        json.dumps(value, sort_keys=True, indent=2, allow_nan=False) + "\n"
    ).encode()
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != raw:
            raise FileExistsError("new version required: " + str(path))
    else:
        with path.open("xb") as f:
            f.write(raw)
    return ref(path)


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, action="append", required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    result = scan([ref(p) for p in args.root])
    write(args.output, result)
    print(json.dumps({k: v for k, v in result.items() if k != "bindings_sha256"}, indent=2))
    return int(bool(result["stale"]))


if __name__ == "__main__":
    raise SystemExit(main())
