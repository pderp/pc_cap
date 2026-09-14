"""R1-40: reproducible CPU run-matrix draft. No launch or freeze operations."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

from r1_d1_exclusions import ROOT, sha, write_json

COUNTERS = ("full_forwards", "partial_forwards", "reverses", "tokens", "accel_seconds")


def identity(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:24]


def validate_matrix(m):
    cells = m["cells"]
    ids = [c["cell_id"] for c in cells]
    paths = [c["result_path_template"] for c in cells]
    if len(ids) != len(set(ids)) or len(paths) != len(set(paths)):
        raise ValueError("duplicate cell or result path")
    core = [c for c in cells if c["scope"] == "core"]
    if len(core) != 180 or len(m["profiling_jobs"]) != 2:
        raise ValueError("six core conditions x two datasets x three realizations x five orders; two profiling jobs")
    for c in cells:
        if c["launch_allowed"] or c["ceilings"]["frozen"] or c["stream_length"] != 1000:
            raise ValueError("draft must not launch/freeze or shorten streams")
        if c["ceilings"]["failure_reserve_seconds"] < .2*c["ceilings"]["proposed_seconds"]:
            raise ValueError("failure reserve missing")
        if c["checkpoint_ids"] != m["conditions"][c["condition_id"]]["checkpoint_ids"]:
            raise ValueError("checkpoint alias mismatch")
    for row in m["contrasts"]:
        if not set(row["conditions"]) <= m["conditions"].keys():
            raise ValueError("missing contrast condition")
    return m


def build():
    sources = {}
    def bind(path):
        p = Path(path)
        if not p.is_absolute():
            p = ROOT/p
        sources[str(p)] = sha(p)
        return {"path": str(p), "sha256": sources[str(p)]}
    def load(path):
        return json.loads(Path(bind(path)["path"]).read_text())
    frozen = load("manifests/frozen.json")
    ref = load("manifests/reference.json")
    candidate = load("manifests/revision_v1/zsre_fresh_candidates_v1.json")
    namespace = load("manifests/revision_v1/synthetic_final_namespace_v2.json")
    for p in ("manifests/revision_v1/exclusions_v2.json", "manifests/revision_v1/train_pool_counterfact_v1.json",
              "docs/updated_plan9.md", "docs/decisions.md", "docs/R1_stage2_notes.md", "docs/lead_queue.md",
              "scripts/r1_40_matrix.py", "scripts/r1_d1_exclusions.py"):
        bind(p)
    evidence = {}
    for arm in ("C1", "C2"):
        path = f"results/R1/diagnostics_{arm}.json"
        obj = load(path)
        a, b = obj["ledger"]["after_stream"], obj["ledger"]["before_stream"]
        ledger = {phase: {k: a[phase][k]-b[phase][k] for k in COUNTERS} for phase in ("learning", "query")}
        evidence["live_"+arm+":zsre"] = {"path":path,"n":obj["n_items"],"ledger":ledger,
            "wall_seconds":a["elapsed_wall_seconds"]-b["elapsed_wall_seconds"],"scope":"stream delta before separate oracle diagnostics"}
    for family, folder in (("stable", "streams_stable"), ("matched", "streams_matched")):
        path = f"results/R1/{folder}/C1/cost.json"
        obj = load(path)
        evidence[family+":zsre"] = {"path":path,"n":100,"ledger":obj,"wall_seconds":obj["elapsed_wall_seconds"],
            "scope":"100-edit development stream; matched historical rule has THREE steps, draft proposes FIVE"}
    for family, tag in (("random", "random_tied_cos_min0.93"), ("learned", "pairown_delta5_null0.5")):
        for ds in ("zsre", "counterfact"):
            path = f"results/R1/stream_eval_{tag}{'@counterfact' if ds=='counterfact' else ''}.json"
            obj = load(path)
            evidence[family+":"+ds] = {"path":path,"n":obj["args"]["n"],"ledger":obj["ledger"],"wall_seconds":obj["wall_seconds"],
                "runtime_args":obj["args"],"scope":"per-dataset summary; old detailed paths may have X25-06 collision; phase counts unreconciled"}
    for e in evidence.values():
        e["per_edit"] = {phase:{k:e["ledger"][phase][k]/e["n"] for k in COUNTERS} for phase in ("learning","query")}
        e["wall_per_edit"] = e["wall_seconds"]/e["n"]
    pilots = []
    for p in sorted((ROOT/"results/R1/pilot").glob("*/summary.json")):
        obj = load(p)
        if obj.get("args",{}).get("steps",0) <= 0:
            continue
        pilots.append({"path":str(p),"sha256":sources[str(p)],"tag":obj["args"].get("tag", p.parent.name),"steps":obj["args"]["steps"],
            "reported_learning_tokens":obj["ledger"]["learning"]["tokens"],"exact_training_pass_tokens":None,
            "train_wall_seconds":obj.get("train_wall_s"),"bill_once_not_per_eval_cell":True})
    own = load("results/R1/pilot/cf_pool3k_pair_own_400/summary.json")
    checkpoints = {
        "base_original":{**bind(ref["inputs"]["model.safetensors"]["path"]),"status":"available_BP","training_job":None},
        "reader_random":{**bind(ROOT.parent/"assets/runs/pc_cap/R1/pilot/random_tied/theta.npz"),"status":"development_reference_seed0","training_job":None},
        "reader_original":{**bind(own["theta_path"]),"status":"development_candidate_not_final_selection","training_job":"reader_original"}}
    jobs = {"reader_original":{"status":"selection_pending","historical_wall_seconds":own["train_wall_s"],
        "reported_learning_tokens":own["ledger"]["learning"]["tokens"],"exact_training_pass_tokens":None,"count_once":True}}
    for key in ("base_bp","base_epc","reader_bp","reader_epc","reader_unroll","cap_settled","cap_parameter","cap_recurrent","base_self","base_lm"):
        checkpoints[key] = {"path":None,"sha256":None,"status":"not_implemented_or_not_selected","training_job":key}
        jobs[key] = {"status":"profile_and_implementation_or_selection_pending","seconds_ceiling":None,"exact_training_pass_tokens":None,"count_once":True}
    definitions = [
        ("v0_live_C1","core","base_original",None,"live_C1",{"family":"Cap","arm":"C1","rule":"v0 search"}),
        ("v0_live_C2","core","base_original",None,"live_C2",{"family":"Cap","arm":"C2","rule":"v0 search"}),
        ("v0_stable","core","base_original",None,"stable",{"family":"StableCap","arm":"C1","rule":"v0 search"}),
        ("matched_update","core","base_original",None,"matched",{"family":"MatchedUpdateCap","arm":"C1","steps":5,"lr":.1,"historical_steps":3}),
        ("R1_nonlearned","core","base_original","reader_random","random",{"family":"RevisionCap","delta_steps":5,"delta_lr":.1,"min_score":.93,"null_threshold":1.01,"pairwise_null":False,"hard_top1":True,"binary_mass":True}),
        ("R1_learned_ff","core","base_original","reader_original","learned",{"family":"RevisionCap","delta_steps":5,"delta_lr":.1,"min_score":None,"null_threshold":"development selection pending","pairwise_null":True,"hard_top1":True,"binary_mass":True}),
        ("episode_bp_old","conditional_base","base_bp",None,"live_C1",{"family":"Cap","arm":"C1","training_mask":"pending matched mask"}),
        ("episode_bp_ff","conditional_base","base_bp","reader_bp","learned",{"family":"RevisionCap","retrained_cap_equal_budget":True}),
        ("episode_epc_old","conditional_base","base_epc",None,"live_C1",{"family":"Cap","arm":"C1","training_mask":"pending matched mask"}),
        ("episode_epc_ff","conditional_base","base_epc","reader_epc","learned",{"family":"RevisionCap","retrained_cap_equal_budget":True}),
        ("unroll_reference_ff","conditional_reference","base_original","reader_unroll","learned",{"objective":"normalized fixed-fast-unroll reference, not yet implemented"}),
        ("settled_selected","conditional_stage3","base_epc","cap_settled","learned",{"steps":"ONE development-selected value from 1/4/8","base_choice":"illustrative ePC binding, replace if selected base differs","zero_step_alias":"episode_epc_ff ONLY after exact cap architecture/checkpoint equivalence"}),
        ("parameter_matched_ff","conditional_stage3","base_epc","cap_parameter","learned",{"parameters":"pending matched parameter count"}),
        ("recurrent_matched","conditional_stage3","base_epc","cap_recurrent","learned",{"steps":"pending measured compute match"}),
        ("continuation_self_stable","conditional_continuation","base_self",None,"stable",{"treatment":"literal KD numerical negative control"}),
        ("continuation_self_learned","conditional_continuation","base_self","reader_original","learned",{"treatment":"literal KD numerical negative control","cap_retrained":False}),
        ("continuation_lm_stable","conditional_continuation","base_lm",None,"stable",{"treatment":"LM continuation proposed in lead queue; no DEC entry yet"}),
        ("continuation_lm_learned","conditional_continuation","base_lm","reader_original","learned",{"treatment":"LM continuation proposed in lead queue; no DEC entry yet","cap_retrained":False}),
        ("R1_learned_v0_memory","conditional_memory","base_original","reader_original","learned",{"persistent_bytes":frozen["byte_ceiling"],"purpose":"matched total-memory frontier"})]
    conditions = {key:{"scope":scope,"checkpoint_ids":[base]+([cap] if cap else []),"profile_family":profile,"settings":settings,
        "model_seed":0,"training_job_ids":sorted({checkpoints[c]["training_job"] for c in [base]+([cap] if cap else []) if checkpoints[c]["training_job"]})} for key,scope,base,cap,profile,settings in definitions}
    comparisons = {
        "stable_observations":["v0_stable","v0_live_C1"],"matched_updates":["matched_update","v0_stable"],
        "nonlearned_geometry":["R1_nonlearned","matched_update"],"learned_component":["R1_learned_ff","R1_nonlearned"],
        "v0_routing":["v0_live_C2","v0_live_C1"],
        "BP_2x2":["v0_live_C1","R1_learned_ff","episode_bp_old","episode_bp_ff"],
        "ePC_2x2":["v0_live_C1","R1_learned_ff","episode_epc_old","episode_epc_ff"],
        "base_estimator":["episode_epc_ff","episode_bp_ff"],"reference":["unroll_reference_ff","R1_learned_ff"],
        "settling":["settled_selected","episode_epc_ff","parameter_matched_ff","recurrent_matched"],
        "self_continuation":["continuation_self_stable","continuation_self_learned","v0_stable","R1_learned_ff"],
        "LM_continuation":["continuation_lm_stable","continuation_lm_learned","v0_stable","R1_learned_ff"],
        "memory_frontier":["R1_learned_v0_memory","v0_stable","matched_update"]}
    cf = load("manifests/dev/counterfact_dev.json")["items"]
    stats = {"zsre":candidate["clear_candidate_token_summary"],"counterfact":{"prompt":{"mean":sum(len(x["prompt_ids"]) for x in cf)/len(cf)},"answer_including_newline":{"mean":sum(len(x["answer_ids"]) for x in cf)/len(cf)}}}
    synthetic = {"R1_nonlearned","R1_learned_ff","episode_bp_ff","episode_epc_ff","unroll_reference_ff","settled_selected"}
    cells = []
    for cid,c in conditions.items():
        datasets = ["zsre","counterfact"]+(["synthetic_composition"] if cid in synthetic else [])
        for ds,r,order in itertools.product(datasets,[0,1,2],[100,101,102,103,104]):
            scope = c["scope"] if ds != "synthetic_composition" else "conditional_composition"
            key = c["profile_family"]+":"+ds
            borrowed = key not in evidence
            if borrowed:
                key = c["profile_family"]+":zsre"
            e = evidence[key]
            rates = e["per_edit"]
            # Explicit linear proxy plus checkpoint and full-drift overhead. These
            # quantities are deliberately not represented as measured final costs.
            update = 1000*rates["learning"]["accel_seconds"]
            query = 1400*max(0,e["wall_per_edit"]-rates["learning"]["accel_seconds"])
            challenge = 200*e["wall_per_edit"]
            raw_seconds = update+query+challenge+780
            proposed = 60*math.ceil(1.25*raw_seconds/60) if scope=="core" or cid=="R1_learned_v0_memory" else 7200
            memory = c["settings"].get("persistent_bytes",64*1024*1024 if len(c["checkpoint_ids"])>1 else frozen["byte_ceiling"])
            cell = {"condition_id":cid,"dataset":ds,"realization_seed":r,"order_seed":order,"model_seed":0,"scope":scope,
                "checkpoint_ids":c["checkpoint_ids"],"stream_length":1000,"pairing_key":f"{ds}/r{r}/o{order}","launch_allowed":False,
                "tokens":{"exact_final_stream_tokens":None,"support_sequence_positions_estimate":1000*sum(stats[ds][k]["mean"] for k in ("prompt","answer_including_newline")) if ds in stats else None,
                    "learning_ledger_input_tokens_proxy":1000*rates["learning"]["tokens"],"query_ledger_input_tokens_proxy":1000*rates["query"]["tokens"],"exact_training_pass_tokens":None},
                "expected_base_calls_per_edit":{phase:{k:rates[phase][k] for k in ("full_forwards","partial_forwards","reverses")} for phase in ("learning","query")},
                "cost_evidence":{"id":key,"borrowed":borrowed or scope!="core","point_seconds_proxy":raw_seconds,"full_split_drift_proxy_seconds":780,
                    "limitations":"historical 100-edit scaling; query/memory occupancy differ; conditional configs unprofiled; partial and full passes not interchangeable; direct outer-pass ledger incomplete"},
                "ceilings":{"proposed_seconds":proposed,"failure_reserve_seconds":math.ceil(.2*proposed),"persistent_bytes":memory,"frozen":False,"source":"replace from P1/P2 before any admission"},
                "checkpoint_schedule":[100,300,1000],"endpoints":["ES","RET-ES","RET-GS","LS","100 near-miss queries","50 revision cases on independent clones","full-split endpoint drift"],
                "profile_dependencies":["P1-edit-memory","P2-outer-endpoint"],"admission":"fresh eligible sealed data + selected checkpoints + repaired gates + measured phase costs + lead freeze"}
            cell["cell_id"] = identity({k:cell[k] for k in ("condition_id","dataset","realization_seed","order_seed","model_seed")})
            suffix = f"<freeze-id>/{cid}/{ds}/r{r}/o{order}/{cell['cell_id']}"
            cell["result_path_template"] = "results/R1/confirm_draft/"+suffix
            cell["checkpoint_path_template"] = "assets/runs/R1/confirm_draft/"+suffix
            cells.append(cell)
    profiles = [
        {"id":"P1-edit-memory","owner":"orchestrator","status":"not_run","gpu_lease_required":True,"proposed_seconds":1800,
         "scope":"one profiling job with six current conditions x BOTH datasets x ten edits; empty and occupied-memory cases",
         "occupancies":[0,100,300,1000],"inputs":"existing development data only; at sizes above unique dev capacity use labelled duplicate-key stress fixtures, not fresh candidate/final examples",
         "measure":["cold compilation separately","warm per-edit p50/p95/max","full/partial/reverse valid-token counts","rejected edits/rollback billed","memory logical bytes/RSS/device peak","restore hash/byte equality","returned cost versus ledger versus instrumented base-call delta","answer-length buckets"],
         "gate":"profile exact five-step matched control and exact selected deployment configs; extend job for later conditional implementations"},
        {"id":"P2-outer-endpoint","owner":"orchestrator","status":"not_run","gpu_lease_required":True,"proposed_seconds":3600,
         "scope":"one profiling job with two matched outer steps on four episodes plus endpoint query/drift/challenge workloads",
         "estimators":["BP cap objective","ePC-credit cap surrogate"],"conditional_extensions":["fixed fast-unroll reference","matched base BP/ePC phases","self/LM continuation","settling/parameter/recurrent controls"],
         "shared_examples_masks_seed":True,"endpoint_occupancies":[100,300,1000],"near_miss_queries":100,"revision_clones":50,"decode_limit":32,
         "drift":{"window_tokens":128,"per_run_windows":128,"per_run_scored_positions":16256,"endpoint":"all complete declared validation windows; report dropped-tail rule and exact targets"},
         "measure":["passes inside JIT/unroll, failed work and compilation","actual phase token counts and warm device times","declared base leaf-change masks","independent query reset boundaries","full-split drift time per checkpoint","maximum in-flight overshoot and endpoint reserve"],
         "gate":"no profile/ceiling inferred for an unimplemented condition; match forward/reverse/relaxation conventions before compute claims"}]
    def reserved_cost(rows):
        return sum(c["ceilings"]["proposed_seconds"]+c["ceilings"]["failure_reserve_seconds"] for c in rows)
    core = [c for c in cells if c["scope"]=="core"]
    m = {"schema_version":1,"task":"R1-40","name":"run_matrix_draft","status":"draft_not_frozen_not_launchable","sources_sha256":sources,
        "axes":{"realization_seeds":[0,1,2],"order_seeds":[100,101,102,103,104],"model_training_seed":0,
            "interpretation":"three seeds are DATA realization seeds, not three independent trained models; lead must confirm this axis before freeze",
            "alternative":"cross three independent model seeds with three realizations if requested; varying random/learned model seeds while reusing fixed v0 controls gives 300 core cells, not 180"},
        "conditions":conditions,"checkpoint_registry":checkpoints,"shared_training_jobs":jobs,
        "contrasts":[{"id":k,"conditions":v,"reuse_existing_cells":True} for k,v in comparisons.items()],"cells":cells,
        "deduplication":{"rule":"one physical condition/checkpoint/dataset/realization/order cell used by every contrast; original controls reused for both 2x2 and continuation contrasts",
            "zero_settling":"alias to feedforward only after exact architecture/parameter/config identity; if different add a separate zero-step cell before freeze",
            "historical_v0":"cannot replace fresh-data baseline cells with historical scores"},
        "profiling_jobs":profiles,"cost_evidence":evidence,"pilot_training_inventory":pilots,
        "budget":{"core_cells":len(core),"all_conditional_inclusive_cells":len(cells),"core_draft_seconds_including_20pct_reserve":reserved_cost(core),
            "all_draft_seconds_including_reserve":reserved_cost(cells),"confirmatory_envelope_seconds":54000,"core_fits_15h_at_draft_ceilings":reserved_cost(core)<=54000,
            "shared_training_billed_once_outside_cells":True,"training_job_ceilings_unpriced":list(jobs),"profile_job_proposed_seconds":5400,
            "completed_pilot_training_wall_seconds_not_gpu_total":sum(p["train_wall_seconds"] or 0 for p in pilots),
            "failure_policy":"20 percent reserve per cell; correctness failure stops queue; every retry has fresh ID and remains billed; do not silently drop realizations or shorten endpoints"},
        "data_gates":{"zsre":"R1-D1c clear candidates then E.2 and contextual/entity review, lead draw 3 x 1000; candidates not final",
            "counterfact":"fresh source or remainder decision pending; whole old eligible pool is excluded by v2, so remainder needs a versioned exception for old-pool-only reasons, never for training/development/other exposure",
            "synthetic":"lead-emitted new physical namespace; not legacy seed-only extension; model compatibility pending","namespace_sha256":namespace["namespace_sha256"]},
        "analysis":{"pairing":"same item/order/checkpoint; cluster by realization with orders together; preliminary intervals at three clusters",
            "margins":{"ret_gs":.05,"es":-.02,"ls":-.01,"ordinary_kl_nats":.001,"nll_increase":.01},
            "multiplicity":"primary contrast and multiplicity policy must be decided before freeze",
            "missing_implementation":"not a negative scientific test of unroll/base learning/settling"},
        "unresolved":["R1-X3 residual resource/query/cost gates","learned checkpoint/null selection","data versus model seed axis","data policy/E.2 capacity","3-step historical matched control must be reprofiled at 5","normalized unroll/base objectives or plan amendment","LM continuation decision/implementation","settling zero-step identity","measured full-split endpoint cost","reprice scope or increase budget; do not assume 15h fits"],
        "gpu_seconds":0,"final_examples_emitted":0,"sealed_payloads_opened":0}
    for p,h in sources.items():
        if sha(Path(p)) != h:
            raise RuntimeError("source changed during draft: "+p)
    return validate_matrix(m)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output",type=Path,required=True)
    a = ap.parse_args()
    if a.output.exists() or not a.output.resolve().is_relative_to(ROOT):
        raise ValueError("new repository output required")
    m = build()
    write_json(a.output,m)
    print(json.dumps({"manifest":str(a.output),"conditions":len(m["conditions"]),"budget":m["budget"]},indent=2))


if __name__ == "__main__":
    main()
