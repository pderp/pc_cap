"""R1-X3: CPU controls for R1-26, including remaining boundary conditions."""
from __future__ import annotations

import ast
import hashlib
import json
import os
from dataclasses import replace
from pathlib import Path
from types import SimpleNamespace

os.environ["JAX_PLATFORMS"] = "cpu"
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import numpy as np  # noqa: E402
from tests.revision_v1.test_learner_cpu import _cfg, _support  # noqa: E402
from tests.revision_v1.tiny_base import TinyBase  # noqa: E402

import pccap  # noqa: E402,F401
from pccap.harness.ledger import Ledger  # noqa: E402
from pccap.harness.snapshot import ItemGuard  # noqa: E402
from pccap.revision_v1.adapt import FastConfig, adapt_record  # noqa: E402
from pccap.revision_v1.contracts import MemoryRecord  # noqa: E402
from pccap.revision_v1.learner import RevisionCap  # noqa: E402
from pccap.revision_v1.memory import RecordStore  # noqa: E402
from pccap.revision_v1.reader import pair_scores  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def path_admission_function():
    """Extract actual tag/path/refusal statements without evaluating the GPU main."""
    tree = ast.parse((ROOT / "scripts/r1_13_stream_eval.py").read_text())
    main = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == "main")
    statements = []
    for node in main.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "tag" for t in node.targets):
            statements.append(node)
        if isinstance(node, ast.With):
            for part in node.body:
                if isinstance(part, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "rd" for t in part.targets):
                    statements.append(part)
                if isinstance(part, ast.If) and ast.unparse(part.test) == "rd.exists()":
                    statements.append(part)
    if len(statements) != 4:
        raise ValueError("driver admission shape changed; inspect before adapting control")
    fn = ast.parse("def admission(args, OUT):\n    return tag, rd\n").body[0]
    fn.body = statements + fn.body
    module = ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[]))
    scope = {"Path": Path}
    exec(compile(module, "<actual-driver-admission>", "exec"), scope)
    return scope["admission"]


def controls(path_fixture):
    cfg = _cfg(null_threshold=1.01)
    cap = RevisionCap(TinyBase(), cfg, Ledger())
    adapt_record(cap, _support(0), FastConfig(steps=0))
    cap.store.ceiling_bytes = cap.store.bytes()["total"] + 213
    before = cap.state_hash()
    before_bytes = cap.store.bytes()
    trace, cost = adapt_record(cap, _support(1, fact="f0", rev=2), FastConfig(steps=0, delta_steps=5, delta_lr=.1))
    out = {"delta_capacity": {"reason": trace.rolled_back_reason, "same_hash": before == cap.state_hash(),
        "same_bytes": before_bytes == cap.store.bytes(), "old_active": cap.store.get("s0").active,
        "replacement_removed": "s1" not in cap.store._by_id, "failed_full_forwards_charged": cost.full_forwards}}
    calls = cap.base.calls["forward"]
    try:
        adapt_record(cap, _support(2, fact="f0", rev=2), FastConfig(steps=1, delta_steps=5))
        rejected = False
    except NotImplementedError:
        rejected = True
    out["mixed_steps"] = {"rejected": rejected, "same_hash": before == cap.state_hash(),
        "same_bytes": before_bytes == cap.store.bytes(), "base_forward_calls_before_refusal": cap.base.calls["forward"]-calls}
    # The generic rollback now preserves the reusable-weight accounting.
    with ItemGuard(cap, cap.ledger):
        cap.store.remove("s0")
    out["itemguard_restore"] = {"same_hash": before == cap.state_hash(), "same_bytes": before_bytes == cap.store.bytes()}
    st = cap.export_state()
    other = RevisionCap(cap.base, replace(cfg, ceiling_bytes=1), Ledger(), params=cap.params)
    requested = other.cfg.ceiling_bytes
    other.import_state(st)
    out["different_requested_ceiling_import"] = {"requested_ceiling": requested, "restored_store_ceiling": other.store.ceiling_bytes,
        "reported_bytes": other.store.bytes()["total"], "accepted": True}
    forged = st.clone()
    forged.scalars["ceiling_bytes"] = 1
    restored = RecordStore.from_state(forged)
    out["over_ceiling_store_import"] = {"ceiling": restored.ceiling_bytes, "reported_bytes": restored.bytes()["total"], "accepted": True}
    # Non-cosine config is still accepted without wiring store.metric.
    q = np.zeros(8,np.float32)
    q[:2] = [1,1]
    k1,k2 = np.zeros(8,np.float32),np.zeros(8,np.float32)
    k1[0],k2[0],k2[1] = 10,1,.1
    c = RevisionCap(TinyBase(), replace(cfg, reader=replace(cfg.reader, cosine=False)), Ledger())
    for rid,k in (("large",k1),("aligned",k2)):
        c.store.add(MemoryRecord(rid,rid,1,-1,k,np.zeros(6,np.float32)))
    scores = np.asarray(pair_scores(c.cfg.reader,q,np.stack([k1,k2])))
    out["noncosine_configuration"] = {"reader_cosine": c.cfg.reader.cosine,"store_metric":c.store.metric,
        "training_best":["large","aligned"][int(scores.argmax())],"retrieved":c.store.retrieve(q,1)[0].record_id}
    admission = path_admission_function()
    output = path_fixture / "results"
    a = SimpleNamespace(tag="fixture",dataset="zsre",theta="unused/theta.npz")
    ztag,zpath = admission(a,output)
    ctag,cpath = admission(SimpleNamespace(**{**vars(a),"dataset":"counterfact"}),output)
    zpath.mkdir(parents=True,exist_ok=False)
    with (zpath/"sentinel.txt").open("x") as f:
        f.write("existing fixture result")
    try:
        admission(a,output)
        refuses = False
    except SystemExit:
        refuses = True
    # An orphan top-level summary remains unguarded by the exact admission code.
    orphan = SimpleNamespace(tag="orphan",dataset="zsre",theta="unused/theta.npz")
    with (output/"stream_eval_orphan.json").open("x") as f:
        f.write('{"fixture":true}')
    orphan_tag,orphan_path = admission(orphan,output)
    out["driver_paths"] = {"zsre_tag":ztag,"counterfact_tag":ctag,"dataset_paths_differ":zpath!=cpath,
        "existing_root_refused":refuses,"orphan_summary_admitted":orphan_tag=="orphan" and not orphan_path.exists(),
        "scope":"actual driver admission AST, no model load/lease/GPU or writes by the extracted code"}
    return out


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,required=True)
    ap.add_argument("--fixture-root",type=Path,required=True)
    a=ap.parse_args()
    if a.output.exists() or a.fixture_root.exists() or not a.output.resolve().is_relative_to(ROOT) or not a.fixture_root.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output and fixture directory required")
    files=list((ROOT/"src/pccap/revision_v1").glob("*.py"))+[ROOT/"scripts/r1_13_stream_eval.py"]
    def hashes():
        return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    before=hashes()
    a.fixture_root.mkdir(parents=True,exist_ok=False)
    result={"task":"R1-X3","controls":controls(a.fixture_root),"sources_before":before,"sources_after":hashes(),"gpu_seconds":0}
    assert result["sources_before"]==result["sources_after"]
    with a.output.open("x") as f:
        json.dump(result,f,indent=2,allow_nan=False)
        f.write("\n")
    print(json.dumps(result["controls"],indent=2))


if __name__=="__main__":
    main()
