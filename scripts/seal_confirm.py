"""Seal DATA-02 realizations with hashes and metadata-only sidecars.

This explicit preparation writer reads item contents; do not run it on sealed study
data before the lead's freeze. Existing outputs are refused unless --replace is
explicitly authorized. The aggregate DATA-02.meta.json is always preserved.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pccap.data.confirmation_integrity import manifest_metadata

ROOT = Path(__file__).resolve().parents[1]


def seal(directory: str | Path, *, replace: bool = False) -> list[Path]:
    """Validate all inputs before writing sidecars, then publish SHA256SUMS last."""
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(directory)
    manifests = sorted(
        path for path in directory.glob("*.json") if not path.name.endswith(".meta.json")
    )
    if not manifests:
        raise ValueError("no realization JSON files found")
    sidecars = [path.with_suffix(".meta.json") for path in manifests]
    sums_path = directory / "SHA256SUMS"
    outputs = [*sidecars, sums_path]
    # Check every destination before opening any item payload or creating any output.
    for path in outputs:
        if path.is_symlink() or (path.exists() and (not replace or not path.is_file())):
            raise FileExistsError(f"refusing existing seal output: {path.name}")
    metadata = [manifest_metadata(path.read_bytes(), path.name) for path in manifests]
    texts = [json.dumps(meta, indent=1, ensure_ascii=False) + "\n" for meta in metadata]
    texts.append("".join(f"{meta['sha256']}  {meta['file']}\n" for meta in metadata))
    for path, content in zip(outputs, texts, strict=True):
        with path.open("w" if replace else "x", encoding="utf-8") as handle:
            handle.write(content)
    return outputs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--directory", type=Path, default=ROOT / "manifests" / "confirm")
    parser.add_argument(
        "--replace", action="store_true",
        help="overwrite seal outputs only; requires approval under the current repository protocol",
    )
    args = parser.parse_args(argv)
    outputs = seal(args.directory, replace=args.replace)
    # Names only: item contents are never printed.
    print(json.dumps({"outputs": [path.name for path in outputs]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
