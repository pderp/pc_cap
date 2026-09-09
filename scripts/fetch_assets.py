"""DATA-00: fetch and hash public assets into /home/derp/cap/assets (PA-9; DEC-004).

Records URL, revision, licence and per-file SHA-256 in ``manifests/datasets.json`` and
``data/raw/SHA256SUMS``. A failed download is recorded as ``unavailable`` with the HTTP status;
no substitute source is used (plan DATA-00). ``--verify`` re-hashes every recorded file.

    python scripts/fetch_assets.py            # fetch everything missing, then hash
    python scripts/fetch_assets.py --verify   # re-hash and compare
    python scripts/fetch_assets.py --only zsre counterfact
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
ASSETS = Path(os.environ.get("PCCAP_ASSETS", "/home/derp/cap/assets"))
RAW = ASSETS / "data" / "raw"
MANIFEST = ROOT / "manifests" / "datasets.json"
SUMS = ROOT / "data" / "raw" / "SHA256SUMS"
GPT2_REV = "607a30d783dfa663caf39e06633721c8d4cfcd7e"
os.environ.setdefault("HF_HOME", str(ASSETS / "hf_cache"))

SOURCES = {
    "gpt2": {
        "kind": "hf_snapshot", "repo": "openai-community/gpt2", "revision": GPT2_REV,
        "licence": "MIT (modified; model card)", "target": ASSETS / "models" / "gpt2",
        "allow": ["*.json", "*.txt", "model.safetensors"],
    },
    "zsre": {
        "kind": "http", "licence": "as distributed by ROME (MIT repository); record",
        "files": {
            "zsre_mend_eval.json": "https://rome.baulab.info/data/dsets/zsre_mend_eval.json",
            "zsre_mend_train.json": "https://rome.baulab.info/data/dsets/zsre_mend_train.json",
        },
        "fields": ["src", "rephrase", "answers", "alt", "loc", "loc_ans", "subject"],
    },
    "counterfact": {
        "kind": "http", "licence": "MIT (ROME)",
        "files": {"counterfact.json": "https://rome.baulab.info/data/dsets/counterfact.json"},
        "fields": ["case_id", "requested_rewrite", "paraphrase_prompts", "neighborhood_prompts",
                   "attribute_prompts", "generation_prompts"],
    },
    "wikitext103": {
        "kind": "hf_dataset", "repo": "Salesforce/wikitext", "config": "wikitext-103-raw-v1",
        "licence": "CC BY-SA 3.0", "splits": ["train", "validation", "test"],
    },
    "ud_ewt": {
        "kind": "github_release", "repo": "UniversalDependencies/UD_English-EWT",
        "licence": "CC BY-SA 4.0",
        "files": ["en_ewt-ud-train.conllu", "en_ewt-ud-dev.conllu", "en_ewt-ud-test.conllu"],
    },
    "grace": {
        "kind": "git", "url": "https://github.com/Thartvigsen/GRACE", "target": ASSETS / "third_party" / "GRACE",
        "licence": "see repository LICENSE (recorded)",
    },
    "openwebtext": {"kind": "deferred", "reason": "REG only; fetched by REG-00 through the sibling recipe"},
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def http_get(url: str, dest: Path) -> dict:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists() and dest.stat().st_size > 0:
        return {"status": "present", "cached": True}
    for attempt in range(3):
        try:
            with requests.get(url, stream=True, timeout=120) as r:
                if r.status_code != 200:
                    return {"status": "unavailable", "http_status": r.status_code}
                tmp = dest.with_suffix(dest.suffix + ".part")
                with open(tmp, "wb") as f:
                    for chunk in r.iter_content(1 << 20):
                        f.write(chunk)
                tmp.rename(dest)
                return {"status": "present", "cached": False}
        except requests.RequestException as e:
            err = str(e)
            time.sleep(2 * (attempt + 1))
    return {"status": "unavailable", "http_status": None, "error": err}


def fetch_gpt2(spec: dict) -> dict:
    from huggingface_hub import snapshot_download

    p = Path(snapshot_download(spec["repo"], revision=spec["revision"], allow_patterns=spec["allow"]))
    tgt = spec["target"]
    tgt.parent.mkdir(parents=True, exist_ok=True)
    if not tgt.exists():
        os.symlink(p, tgt)
    files = {str((tgt / f).relative_to(ASSETS)): sha256(p / f)
             for f in ["model.safetensors", "config.json", "tokenizer.json", "vocab.json", "merges.txt"]}
    return {"status": "present", "path": str(p), "revision": spec["revision"], "licence": spec["licence"], "files": files,
            "url": f"https://huggingface.co/{spec['repo']}/tree/{spec['revision']}"}


def fetch_http(name: str, spec: dict) -> dict:
    out = {"status": "present", "licence": spec["licence"], "url": list(spec["files"].values()), "files": {},
           "fields": spec.get("fields", []), "revision": None}
    for fname, url in spec["files"].items():
        dest = RAW / name / fname
        r = http_get(url, dest)
        if r["status"] != "present":
            out["status"] = "unavailable"
            out["reason"] = f"{fname}: HTTP {r.get('http_status')} {r.get('error', '')}"
            continue
        out["files"][str(dest.relative_to(ASSETS))] = sha256(dest)
    return out


def fetch_wikitext(spec: dict) -> dict:
    from huggingface_hub import HfApi, hf_hub_download

    api = HfApi()
    info = api.dataset_info(spec["repo"])
    rev = info.sha
    files = [s.rfilename for s in info.siblings if s.rfilename.startswith(spec["config"] + "/") and s.rfilename.endswith(".parquet")]
    out = {"status": "present", "licence": spec["licence"], "revision": rev, "files": {},
           "url": f"https://huggingface.co/datasets/{spec['repo']}/tree/{rev}/{spec['config']}"}
    for rf in sorted(files):
        p = Path(hf_hub_download(spec["repo"], rf, repo_type="dataset", revision=rev))
        dest = RAW / "wikitext103" / Path(rf).name
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            os.symlink(p, dest)
        out["files"][str(dest.relative_to(ASSETS))] = sha256(dest)
    return out


def _latest_ud_tag(repo: str) -> str:
    """Latest UD release tag ``rX.Y`` by numeric version (the repo has tags, not GitHub releases)."""
    import re

    tags: list[str] = []
    page = 1
    while page <= 10:
        r = requests.get(f"https://api.github.com/repos/{repo}/tags", params={"per_page": 100, "page": page}, timeout=60)
        if r.status_code != 200:
            break
        batch = [t["name"] for t in r.json()]
        if not batch:
            break
        tags += batch
        page += 1
    versions = []
    for t in tags:
        m = re.fullmatch(r"r(\d+)\.(\d+)", t)
        if m:
            versions.append(((int(m.group(1)), int(m.group(2))), t))
    return max(versions)[1] if versions else "master"


def fetch_ud_ewt(spec: dict) -> dict:
    tag = _latest_ud_tag(spec["repo"])
    out = {"status": "present", "licence": spec["licence"], "revision": tag, "files": {},
           "url": f"https://github.com/{spec['repo']}/tree/{tag}"}
    for f in spec["files"]:
        url = f"https://raw.githubusercontent.com/{spec['repo']}/{tag}/{f}"
        dest = RAW / "ud_ewt" / f
        r = http_get(url, dest)
        if r["status"] != "present":
            out["status"] = "unavailable"
            out["reason"] = f"{f}: HTTP {r.get('http_status')}"
            continue
        out["files"][str(dest.relative_to(ASSETS))] = sha256(dest)
    return out


def fetch_grace(spec: dict) -> dict:
    tgt = spec["target"]
    tgt.parent.mkdir(parents=True, exist_ok=True)
    if not (tgt / ".git").exists():
        r = subprocess.run(["git", "clone", "--quiet", spec["url"], str(tgt)], capture_output=True, text=True)
        if r.returncode != 0:
            return {"status": "unavailable", "reason": r.stderr.strip()[:300], "url": spec["url"]}
    head = subprocess.check_output(["git", "-C", str(tgt), "rev-parse", "HEAD"], text=True).strip()
    lic = next((c for c in ("LICENSE", "LICENSE.md", "LICENSE.txt", "COPYING") if (tgt / c).exists()), None)
    lic_text = (tgt / lic).read_text()[:200].replace("\n", " ") if lic else "no licence file"
    return {"status": "present", "url": spec["url"], "revision": head, "path": str(tgt),
            "licence": f"{lic}: {lic_text}" if lic else "unknown (no licence file)", "files": {}}


def wikitext_token_counts() -> dict:
    """SD-3: unique document and GPT-2 token counts per split (documents = blank-line separated)."""
    import pyarrow.parquet as pq
    from tokenizers import Tokenizer

    tok = Tokenizer.from_file(str(ASSETS / "models" / "gpt2" / "tokenizer.json"))
    out = {}
    for split in ["train", "validation", "test"]:
        parts = sorted((RAW / "wikitext103").glob(f"{split}-*.parquet"))
        n_lines = n_tok = 0
        docs = 0
        for part in parts:
            tbl = pq.read_table(part)
            texts = tbl.column("text").to_pylist()
            for t in texts:
                n_lines += 1
                if t.startswith(" = ") and not t.startswith(" = = "):
                    docs += 1
            enc = tok.encode_batch(texts)
            n_tok += sum(len(e.ids) for e in enc)
        out[split] = {"lines": n_lines, "documents_heading_heuristic": docs, "gpt2_tokens": n_tok, "parts": len(parts)}
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true")
    ap.add_argument("--only", nargs="*", default=None)
    ap.add_argument("--no-token-counts", action="store_true")
    args = ap.parse_args(argv)
    if args.verify:
        return verify()
    manifest = json.loads(MANIFEST.read_text()) if MANIFEST.exists() else {}
    names = args.only or list(SOURCES)
    for name in names:
        spec = SOURCES[name]
        print(f"[{name}] {spec['kind']} ...", flush=True)
        try:
            if spec["kind"] == "hf_snapshot":
                rec = fetch_gpt2(spec)
            elif spec["kind"] == "http":
                rec = fetch_http(name, spec)
            elif spec["kind"] == "hf_dataset":
                rec = fetch_wikitext(spec)
            elif spec["kind"] == "github_release":
                rec = fetch_ud_ewt(spec)
            elif spec["kind"] == "git":
                rec = fetch_grace(spec)
            else:
                rec = {"status": "deferred", "reason": spec["reason"]}
        except Exception as e:  # recorded, never substituted
            rec = {"status": "unavailable", "reason": f"{type(e).__name__}: {e}"[:300]}
        rec["fetched"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        manifest[name] = rec
        print(f"[{name}] {rec['status']}", flush=True)
    if not args.no_token_counts and manifest.get("wikitext103", {}).get("status") == "present":
        manifest["wikitext103"]["token_counts"] = wikitext_token_counts()
        print("[wikitext103] token counts", manifest["wikitext103"]["token_counts"], flush=True)
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
    write_sums(manifest)
    return 0


def write_sums(manifest: dict) -> None:
    SUMS.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    for _name, rec in sorted(manifest.items()):
        for rel, h in sorted(rec.get("files", {}).items()):
            lines.append(f"{h}  {rel}")
    SUMS.write_text("\n".join(lines) + "\n")


def verify() -> int:
    bad = 0
    n = 0
    for line in SUMS.read_text().splitlines():
        h, rel = line.split("  ", 1)
        p = ASSETS / rel if not rel.startswith("/") else Path(rel)
        n += 1
        if not p.exists():
            print(f"MISSING {rel}")
            bad += 1
            continue
        if sha256(p) != h:
            print(f"MISMATCH {rel}")
            bad += 1
    print(f"verified {n - bad}/{n} files")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
