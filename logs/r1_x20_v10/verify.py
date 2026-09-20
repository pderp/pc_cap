"""Read-only X20 replay. Run with repo root on PYTHONPATH, CPU-only JAX.

Writes exclusively to a NEW output directory beneath this script's directory.
No producer execute/prepare/run, model, payload loader, or publication is called.
Sealed payload and reservation copies are hashed, never parsed. Replay uses the
explicitly bound unsealed sources and retains no experiment text in its reports.
"""
from __future__ import annotations

import argparse
import copy
import gc
import hashlib
import json
import resource
import sys
import time
import traceback
from collections import Counter
from contextlib import ExitStack
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import pccap  # noqa: E402,F401 -- initialize before JAX-dependent modules
import numpy as np  # noqa: E402
from scripts import r1_58g_operator as op  # noqa: E402
from scripts import r1_63n_assembly_inputs as gates  # noqa: E402
from scripts import r1_63o_live_audit as lock  # noqa: E402
from scripts import r1_d10c_endpoints as ep  # noqa: E402
from scripts import r1_d9_receipts as d9  # noqa: E402

SESSION = ROOT / "logs/R1/operator_v10"
JOURNAL = SESSION / "receipts.jsonl"
SEED = 378462438976234321867
FREEZE_SHA = "60f2c09461330852f673bcc0a818bf6cc972bda02b68312dee11a474d04dcfcb"


def require(ok, message):
    if not ok:
        raise ValueError(message)


def equal(actual, expected, message):
    require(actual == expected, message)


def serialized_sha(value, *, compact=False):
    """D9 or endpoint byte format without a second large byte string."""
    h = hashlib.sha256()
    encoder = json.JSONEncoder(sort_keys=True, ensure_ascii=False, allow_nan=False,
                               **({"separators": (",", ":")} if compact else {"indent": 2}))
    for fragment in encoder.iterencode(value):
        h.update(fragment.encode())
    h.update(b"\n")
    return h.hexdigest()


class Snapshot:
    def __init__(self):
        self.bindings = {}

    def sha(self, path):
        path = str(Path(path).resolve())
        if path not in self.bindings:
            self.bindings[path] = d9.sha(path)
        return self.bindings[path]

    def ref(self, path):
        return dict(path=str(Path(path).resolve()), sha256=self.sha(path))

    def check(self, binding):
        equal(self.sha(binding["path"]), binding["sha256"],
              "bound file SHA mismatch: " + binding["path"])

    def read(self, binding, *, parse=True):
        self.check(binding)
        p = Path(binding["path"]).resolve()
        require("confirm" not in p.parts, "historical confirmation access refused")
        if parse:
            require(not (p.parent.name == "seal" and
                         ((p.name.startswith("payload-") and p.name != "payload-inventory.json")
                          or "reservations" in p.name)),
                    "sealed payload/reservation parsing refused")
        raw = p.read_bytes()
        equal(hashlib.sha256(raw).hexdigest(), binding["sha256"], "read changed: " + str(p))
        return json.loads(raw) if parse else raw

    def file(self, path, **kwargs):
        return self.read(self.ref(path), **kwargs)

    def verify(self):
        for path, expected in self.bindings.items():
            equal(d9.sha(path), expected, "review input changed: " + path)


def rejects(callback, name):
    try:
        callback()
    except (ValueError, PermissionError):
        return name
    raise AssertionError("tamper accepted: " + name)


def main(out):
    started = time.monotonic()
    snap = Snapshot()
    report = dict(task="X20", session="operator_v10", verifier=snap.ref(__file__),
                  started_utc=datetime.now(timezone.utc).isoformat(),
                  checks={}, negative_checks=[], limitations=[
                      "Validates recorded DEC-067 delegated approvals; does not authenticate a human identity independently.",
                      "Replays admitted selection rules; does not re-judge semantic teacher/alias clearance.",
                      "Technical verification is not a new signature, GPU lease, launch, or experimental result."])
    def stage(name, value):
        report["checks"][name] = value
        print(name + ": " + json.dumps(value, sort_keys=True), flush=True)
    try:
        history_raw = JOURNAL.read_bytes()
        history = op.journal_read(JOURNAL)
        require(history_raw == JOURNAL.read_bytes(), "journal changed during initial read")
        complete = [r for r in history if r["status"] == "complete"]
        equal([r["step"] for r in complete[:8]], list(op.STEPS[:8]), "eight completed steps required")
        freeze_index = history.index(complete[7])
        signed_prefix = b"".join(history_raw.splitlines(keepends=True)[:freeze_index + 1])
        require(not any(r["status"] == "failed" for r in history[:freeze_index + 1]),
                "unreconciled failure before freeze")
        report["journal_prefix"] = dict(path=str(JOURNAL), rows=freeze_index + 1,
                                        sha256=hashlib.sha256(signed_prefix).hexdigest())
        candidate_binding = snap.ref(ROOT / "manifests/revision_v1/freeze_candidate_v15.json")
        cand = snap.read(candidate_binding)
        spec = snap.read(cand["d9_inputs"])
        previous = cand["d9_inputs"]
        op.verify_candidate(cand)
        for path, sha in cand["bindings_sha256"].items():
            snap.check(dict(path=path, sha256=sha))
        for key in ("matrix", "protocol", "register"):
            equal(cand[key], spec[key], "candidate/input differs: " + key)
        equal(spec["d9"]["clearance"]["configuration_bindings"]["execution_plan"],
              cand["execution_plan"], "execution plan differs")
        approvals, states, requests = {}, {}, {}
        for i, row in enumerate(complete[:8], 1):
            step = row["step"]
            signed, after = snap.read(row["receipt"]), snap.read(row["inputs"])
            form = snap.file(ROOT / f"docs/tasks/operator-v10/{i:02}-reviewed.json")
            request = gates.request_for(step, previous, spec, signed, candidate_binding, SESSION, snap)
            if step == "freeze":
                request["publication_bundle"] = request["fields"]["publication_bundle"]
            equal(request["fields"], form["fields"], "saved form fields differ: " + step)
            digest = op.validate_signature(form, request)
            equal(digest, row["request_sha256"], "journal request differs: " + step)
            equal(digest, signed["operator_request_sha256"], "signed receipt request differs: " + step)
            equal(signed["lead_signature"], form["lead_signature"], "signature receipt/form differs")
            equal(row["receipt"]["path"], request["receipt_output"], "receipt destination differs")
            equal(row["inputs"]["path"], request["next_inputs"], "state destination differs")
            require(any(r["status"] == "dry_run" and r["step"] == step and
                        r["request_sha256"] == digest and r["blocked"] == []
                        for r in history[:history.index(row)]), "matching clean preview missing: " + step)
            preview = snap.file(ROOT / f"docs/tasks/operator-v10/{i:02}-preview.json")
            # *-preview.json is the initial unsigned form, before fields were
            # completed. The clean revised preview is recorded in the journal.
            equal(preview["step"], step, "initial preview step differs")
            equal(preview["lead_approved"], False, "initial preview unexpectedly approved")
            expected = dict(op.common(spec), **form["fields"], status="closed", lead_approved=True,
                            lead_signature=form["lead_signature"], operator_request_sha256=digest)
            if step in ("protocol-admit", "rng-admit"):
                key = "protocol_admission" if step == "protocol-admit" else "rng_admission"
                if step == "protocol-admit":
                    expected["near_allocation_decision"] = signed["near_allocation_decision"]
                else:
                    expected["near_allocation_contract"] = op.CONTRACT
                expected = snap.read(spec["receipts"][key]) | expected
            elif step == "cost-admit":
                expected.update(failures_included=True, cost_admission_source=op.cost_binding(spec))
                expected = op.cost_source(spec) | expected
            elif step in d9.RECEIPT_NAMES:
                expected.update(operation=step, request_sha256=d9.contract(spec, step))
            elif step == "endpoints":
                endpoint_report = snap.file(SESSION / "endpoints-written.json")
                draw = snap.read(spec["receipts"]["draw_receipt"])
                expected.update(draw_receipt=spec["receipts"]["draw_receipt"], reservations=draw["reservations"],
                                bundle=endpoint_report["bundle"], independent_population=endpoint_report["independent_population"],
                                datasets=list(d9.core.DATASETS), all_roles_disjoint=True, composition_dependencies_closed=True)
            else:
                expected.update(operation="freeze", request_sha256=digest)
            equal(signed, expected, "receipt has unexpected content: " + step)
            if i <= 7:
                gates.transition(step, spec, after, signed, row["receipt"], request, snap)
            else:
                expected_state = copy.deepcopy(spec)
                expected_state["freeze_candidate"] = candidate_binding
                for k in ("september20_admission", "closed_gate_receipts"):
                    expected_state["receipts"][k] = form["fields"][k]
                expected_state["receipts"]["freeze_authorization"] = row["receipt"]
                bundle = snap.read(form["fields"]["publication_bundle"])
                expected_state["published_freeze"] = dict(freeze=snap.ref(ROOT / op.backend.FROZEN_RELATIVE),
                                                         matrix=bundle["matrix"], bindings=bundle["bindings"])
                equal(after, expected_state, "freeze input transition differs")
            approvals[step] = dict(receipt=row["receipt"], request_sha256=digest, lead_signature=form["lead_signature"])
            states[step] = after
            requests[step] = request
            previous, spec = row["inputs"], after
        stage("signed_requests", dict(count=8, exact_forms_receipts_previews_transitions=True,
                                      digests={k:v["request_sha256"] for k,v in approvals.items()}))
        bad_request = copy.deepcopy(requests["rng-admit"])
        bad_request["fields"]["master_seed"] += 1
        report["negative_checks"].append(rejects(lambda: op.validate_signature(
            snap.file(ROOT / "docs/tasks/operator-v10/04-reviewed.json"), bad_request), "changed signed seed"))

        closed = snap.read(spec["receipts"]["closed_gate_receipts"])
        journal_binding = closed["operator_journal"]
        gate_prefix = b"".join(history_raw.splitlines(keepends=True)[:journal_binding["rows"]])
        equal(hashlib.sha256(gate_prefix).hexdigest(), journal_binding["sha256"], "derived gate journal prefix differs")
        equal(history[journal_binding["rows"]-1], complete[6], "gates must derive after step 7")
        common = dict(op.common(states["seal"]), status="closed", lead_approved=True,
                      approval_basis="derived from verified exact signed requests; no new signature",
                      candidate=candidate_binding, operator_journal=journal_binding, source_inputs=complete[6]["inputs"],
                      producer=snap.ref(gates.__file__), publication_authorized=False, launch_authorized=False)
        equal(set(closed["gates"]), set(gates.GATES), "gate inventory differs")
        seven = {k:approvals[k] for k in op.STEPS[:7]}
        equal(closed, dict(common, gates=closed["gates"], inherited_approvals=seven), "closed-gates derivation differs")
        for gate, (steps, note) in gates.GATES.items():
            equal(snap.read(closed["gates"][gate]), dict(common, gate=gate, scope="prepublication admission dependencies",
                  qualification=note, inherited_approvals={s:approvals[s] for s in steps}, evidence_receipts=states["seal"]["receipts"]),
                  "derived gate differs: " + gate)
        schedule = snap.read(spec["receipts"]["september20_admission"])
        for key, expected in dict(experimental_completion_date="2026-10-09", shared_process_hours=750,
                                  execution_plan=cand["execution_plan"], full_scope_retained=True,
                                  signed_cost=spec["receipts"]["chain_i_cell_ceilings"],
                                  inherited_approvals={s:approvals[s] for s in ("protocol-admit", "cost-admit", "clearance")},
                                  **common).items():
            equal(schedule[key], expected, "schedule derivation differs: " + key)
        stage("derived_gates", dict(count=18, exact_inheritance=True, deadline="2026-10-09", process_hour_cap=750))
        stage("content_lock_initial", lock.verify_lock(ROOT / "logs/r1_63o/final/live-content-lock.json"))

        clearance_spec = states["clearance"]
        register = snap.read(spec["register"])
        d9.verify_register(register)
        evidence = snap.read(clearance_spec["d9"]["clearance"]["evidence"])
        for binding in evidence["evidence_bindings"]:
            snap.check(binding)
        clearance = d9.clearance_value(clearance_spec, register, evidence, d9.source_rows(register))
        clearance_receipt = snap.read(spec["receipts"]["joint_clearance"])
        snap.check(clearance_receipt["cleared_candidates"])
        equal(serialized_sha(clearance), clearance_receipt["cleared_candidates"]["sha256"], "replayed clearance bytes differ")
        stage("clearance", dict(usable_subjects={k:v["usable_subjects"] for k,v in clearance["counts"].items()},
                                exact_register_and_review_replay=True))
        del clearance, evidence, register
        gc.collect()
        draw_spec = states["draw"]
        draw_receipts = d9.admitted_receipts(draw_spec, "draw")
        equal(draw_spec["d9"]["draw"]["master_seed"], SEED, "seed is not lead's seed")
        reservations = d9.draw_value(draw_spec, draw_receipts)
        draw = snap.read(spec["receipts"]["draw_receipt"])
        snap.check(draw["reservations"])
        equal(serialized_sha(reservations), draw["reservations"]["sha256"], "replayed reservations/orders/RNG differ")
        stage("draw", dict(seed=SEED, exact_serialized_reservations=True, allocation_groups=len(reservations["allocations"]),
                           paired_orders=len(reservations["orders"]), near_allocation=reservations["near_allocation"]))
        bad_spec = copy.deepcopy(draw_spec)
        bad_spec["d9"]["draw"]["master_seed"] += 1
        report["negative_checks"].append(rejects(lambda: d9.draw_value(bad_spec, draw_receipts), "draw seed differs from admission"))

        construction = snap.file(ROOT / "docs/tasks/R1-58g-operator_v10/endpoints-request.json")
        declaration = snap.read(spec["matrix"])
        cells = d9.matrix_cells(dict(document=declaration, binding=spec["matrix"]), draw_receipts["protocol_admission"])
        plan, catalog = snap.read(construction["role_plan"]), snap.read(construction["catalog"])
        for binding in plan["evidence_bindings"] + [construction["drift"]]:
            snap.check(binding)
        tokens = np.load(construction["drift"]["path"], allow_pickle=False).reshape(-1)
        drift = dict(windows=tokens[:128*128].reshape(128,128).astype(int).tolist(), expected_positions=128*127)
        payloads, population, reconstruction = ep.construct(reservations, cells, catalog, plan, drift,
            layout=d9.layouts.from_matrix(declaration), full_validation=declaration["full_validation"], exclude_locality_overlaps=True)
        saved = snap.file(SESSION / "endpoints-written.json")
        for k,v in reconstruction.items():
            equal(saved[k], v, "endpoint construction replay differs: " + k)
        independent_binding = saved["independent_population"]
        snap.check(independent_binding)
        # Endpoint write_new uses compact JSON; D9 seal copies use indented JSON.
        equal(serialized_sha(population, compact=True), independent_binding["sha256"], "independent population differs from reconstructed endpoints")
        unsealed_bundle = snap.read(saved["bundle"])
        equal(set(unsealed_bundle["payloads"]), set(payloads), "endpoint cell inventory differs")
        payload_byte_shas, compact_payload_shas = {}, {}
        for cid, p in payloads.items():
            binding = unsealed_bundle["payloads"][cid]
            snap.check(binding)
            if id(p) not in payload_byte_shas:
                payload_byte_shas[id(p)] = serialized_sha(p)
                compact_payload_shas[id(p)] = serialized_sha(p, compact=True)
            equal(binding["sha256"], compact_payload_shas[id(p)], "constructed payload bytes differ: " + cid)
        # Independently scan the declared outside rows rather than trusting selection diagnostics.
        groups = d9.core.audit_reservations(reservations, layout=d9.layouts.from_matrix(declaration))
        summaries = []
        for ds in d9.core.DATASETS:
            for real in range(3):
                edits = groups[ds, str(real), "edits"]["records"]
                excluded = {s for r in edits for s in [r["prompt"], *r["paraphrases"]]}
                eligible, seen = [], set()
                for r in sorted(groups[ds,str(real),"outside"]["records"], key=lambda r:r["item_id"]):
                    for prompt in r.get("locality_prompts", []):
                        if prompt not in excluded and prompt not in seen:
                            seen.add(prompt)
                            eligible.append((prompt, r["item_id"]))
                c = next(c for c in cells if c["dataset"] == ds and c["realization"] == real)
                endpoints = payloads[d9.coordinate_id(c)]["endpoints"]
                actual = [(r["prompt"],r["source_outside_item_id"]) for r in endpoints["locality"]["rows"]]
                equal(actual, eligible[:50], "locality is not deterministic first distinct nonoverlapping 50")
                equal(len(actual), 50, "locality shortfall")
                equal(len(endpoints["near_miss"]["rows"]), 100, "near-miss shortfall")
                summaries.append(dict(dataset=ds, realization=real, locality=50, near_miss=100,
                                      revision=len(endpoints["revision"]["rows"]), composition=len(endpoints["composition"]["rows"])))
        equal(reconstruction["missing"], [], "unexpected endpoint shortfalls")
        stage("endpoints", dict(cells=len(cells), unique_payloads=len(payload_byte_shas),
                                exact_independent_population=True, groups=summaries, shortfalls=0))

        seal = snap.read(spec["receipts"]["seal_receipt"])
        seal_inventory = snap.read(seal["payload_inventory"])
        # Independently expected sealed bytes from the exact unsealed replay, without parsing sealed data.
        sealed_reservations = dict(reservations, mode="content_sealed_fact_reservations",
                                   seal_scope="exact reserved rows and constructed endpoints; launch needs final freeze")
        snap.check(seal["reservations"])
        equal(serialized_sha(sealed_reservations), seal["reservations"]["sha256"], "sealed reservations differ")
        snap.check(seal["analysis_population"])
        equal(seal["analysis_population"]["sha256"], serialized_sha(population), "sealed population differs")
        equal(set(seal_inventory["cells"]), set(payloads), "sealed inventory cell coverage differs")
        for cid, inv in seal_inventory["cells"].items():
            equal({k:v for k,v in inv.items() if k != "payload"}, reconstruction["identities"][cid], "sealed endpoint identity differs")
            snap.check(inv["payload"])
            equal(inv["payload"]["sha256"], payload_byte_shas[id(payloads[cid])], "sealed payload bytes differ")
        # A bad binding must fail before any sealed payload parser could run.
        bad_binding = dict(next(iter(seal_inventory["cells"].values()))["payload"], sha256="0"*64)
        report["negative_checks"].append(rejects(lambda: snap.check(bad_binding), "sealed payload digest mismatch"))
        sample_cid = next(iter(payloads))
        wrong_population = dict(population, cells=dict(population["cells"]))
        wrong_population["cells"][sample_cid] = dict(population["cells"][sample_cid])
        wrong_population["cells"][sample_cid]["item_ids"] = wrong_population["cells"][sample_cid]["item_ids"][1:]
        report["negative_checks"].append(rejects(lambda: d9.core.validate_seal(
            reservations, cells, payloads, wrong_population, layout=d9.layouts.from_matrix(declaration),
            full_validation=declaration["full_validation"]), "missing expected item"))
        stage("seal", dict(cells=len(seal_inventory["cells"]), sealed_payloads_hashed=len(payload_byte_shas),
                           sealed_payloads_parsed=0, exact_reservations_population_and_identities=True))
        del payloads, plan, catalog, reservations, sealed_reservations, groups, population, wrong_population, tokens
        gc.collect()

        bundle = snap.read(requests["freeze"]["publication_bundle"])
        assembly_spec = copy.deepcopy(states["seal"])
        assembly_spec["freeze_candidate"] = candidate_binding
        for key in ("september20_admission", "closed_gate_receipts"):
            assembly_spec["receipts"][key] = spec["receipts"][key]
        equal(assembly_spec, snap.file(ROOT / "docs/tasks/R1-63o-actual-assembly/assembly-inputs.json"),
              "staged assembly inputs differ from signed session")
        equal(bundle["source_inputs_sha256"], d9.core.content_digest(assembly_spec), "bundle source inputs differ")
        equal(gates.assembly.inspect(assembly_spec)["blocked"], [], "native assembly receipt checks failed")
        templates = snap.read(cand["runtime_templates"])
        equal(bundle["templates"], templates, "bundle templates differ from candidate v15")
        destinations = set()
        for artifact in bundle["artifacts"]:
            p = Path(artifact["destination"]).resolve()
            require(p not in destinations and any(p.is_relative_to(ROOT / d) for d in ("docs/tasks","manifests/revision_v1")),
                    "duplicate or external publication destination")
            destinations.add(p)
            snap.check(artifact["source"])
            equal(snap.sha(p), artifact["source"]["sha256"], "published bytes differ from reviewed stage: " + str(p))
        equal(len(destinations), 334, "publication artifact count differs")
        frozen_binding = snap.ref(ROOT / op.backend.FROZEN_RELATIVE)
        equal(frozen_binding["sha256"], FREEZE_SHA, "published freeze differs from DEC-071")
        frozen = snap.read(frozen_binding)
        for k,v in dict(protocol_admission=spec["receipts"]["protocol_admission"], cost_admission=spec["receipts"]["chain_i_cell_ceilings"],
                        seal_receipt=spec["receipts"]["seal_receipt"], reservations=seal["reservations"],
                        population=seal["analysis_population"], closed_gates=closed["gates"]).items():
            equal(frozen[k], v, "frozen identity differs: " + k)
        protocol = snap.read(frozen["protocol"])
        for key, value in dict(protocol_text=cand["protocol"], normative_closure=cand["normative_closure"],
                               matrix=cand["matrix"], full_validation=cand["full_validation"],
                               cap_fidelity_policy=declaration["cap_fidelity_policy"],
                               near_allocation_decision=spec["near_allocation_decision"], extension_admitted=True).items():
            equal(protocol[key], value, "final protocol differs from candidate/admission: " + key)
        stage("publication", dict(artifacts=334, byte_exact_copies=True, freeze_sha256=frozen_binding["sha256"]))
        matrix, bindings = snap.read(bundle["matrix"]), snap.read(bundle["bindings"])
        equal(bindings["matrix_sha256"], bundle["matrix"]["sha256"], "queue/matrix SHA differs")
        final_cells = op.queue.analysis.all_cells(matrix)
        equal([{k:c[k] for k in d9.COORDS} for c in final_cells], cells, "final coordinate order differs from declaration")
        counts = dict(Counter(c["block_number"] for c in final_cells))
        equal(list(counts.values()), [45,45,45,90,60,45], "DEC-068 block sizes/order differ")
        equal(set(bindings["recipes"]), set(frozen["recipe_contracts"]), "queue/freeze cell coverage differs")
        cost = snap.read(spec["receipts"]["chain_i_cell_ceilings"])
        equal((cost["cost_schema_version"], cost["receipt_revision"], cost["shared_process_hours"]),
              (2, 4, 750), "typed cost admission differs")
        costs = {(c["condition"], c["dataset"]): c for c in cost["cells"]}
        runtime = {key:snap.read(b) for key,b in templates.items()}
        calibration = snap.read(cand["calibration"])
        primary = snap.read(cand["primary_condition"])
        declared_cells = {c["cell_id"]:c for c in op.queue.analysis.all_cells(declaration)}
        changed_cell_fields = {"admitted", "launch_allowed", "recipe_template", "manifest_sha256", "payload_sha256",
                               "population", "ceilings", "adapter_identity", "code_sha256", "result_dir", "full_validation"}
        for c in final_cells:
            recipe = snap.read(bindings["recipes"][c["cell_id"]])
            equal(recipe["payload"], seal_inventory["cells"][c["cell_id"]]["payload"], "recipe seal payload differs")
            equal(op.backend.contract_digest(recipe), frozen["recipe_contracts"][c["cell_id"]], "recipe contract differs")
            key = c["condition"] + ":" + c["dataset"]
            equal(recipe["runtime_template"], templates[key], "recipe runtime template differs from candidate")
            equal({k:recipe[k] for k in gates.assembly.RUNTIME_KEYS if k in recipe},
                  {k:runtime[key][k] for k in gates.assembly.RUNTIME_KEYS if k in runtime[key]},
                  "recipe runtime fields changed from reviewed template")
            equal(recipe["ceilings"], costs[c["condition"],c["dataset"]], "recipe cost differs from signed admission")
            equal(recipe["calibration"], cand["calibration"], "recipe calibration binding differs")
            equal(recipe["construction"]["calibration"],
                  dict(bank_scales=calibration["calibration"]["BP"]["b_m"],
                       radii=calibration["calibration"]["BP"]["radii"][c["dataset"]]), "runtime calibration values differ")
            if c["condition"] == "R1_learned_ff":
                equal(recipe["construction"]["weights"], primary["weights"], "primary weights differ from selected v5")
            equal({k:v for k,v in c.items() if k not in changed_cell_fields},
                  {k:v for k,v in declared_cells[c["cell_id"]].items() if k not in changed_cell_fields},
                  "non-runtime matrix cell fields changed at publication")
        stage("candidate_runtime", dict(runtime_templates=len(templates), recipes=330,
                                         exact_runtime_cost_calibration_weights_and_cell_design=True))
        # Cache only stable, hash-checked metadata for the unmodified queue/backend validators.
        # No content overlay or replaced validation predicates. Rehash every cached source at end.
        cached = {}
        def read_bound(b):
            snap.check(b)
            key = (b["path"], b["sha256"])
            if key not in cached:
                cached[key] = snap.read(b)
            return cached[key]
        def metadata(b):
            p = Path(b["path"]).resolve()
            require("confirm" not in p.parts and any(p.is_relative_to(ROOT / s) for s in ("docs/tasks","manifests/revision_v1")),
                    "backend metadata namespace refused")
            return read_bound(b)
        with ExitStack() as stack:
            for obj,name,value in [(op.backend,"metadata",metadata), (op.backend,"read_binding",read_bound),
                                   (op.backend,"sha",snap.sha), (op.queue,"sha",snap.sha),
                                   (op.queue,"read",lambda p:read_bound(snap.ref(p))),
                                   (op.backend.core,"sha",snap.sha)]:
                stack.enter_context(patch.object(obj,name,value))
            op.queue.verify_sealed_matrix(matrix, bindings)
        cached.clear()
        gc.collect()
        stage("queue_backend", dict(cells=330, core=285, extension=45, blocks=counts,
                                    native_metadata_validation="passed", payload_loaders_called=0))
        bad = dict(bundle["matrix"], sha256="f"*64)
        report["negative_checks"].append(rejects(lambda:snap.check(bad), "queue matrix binding mismatch"))
        # Observe queue cost state without signing or invoking the operator's mutating preview.
        preview = op.queue.inventory(matrix, receipt_root=ROOT / "logs/R1/final_queue", matrix_hash=bundle["matrix"]["sha256"], workers=2, ceiling_hours=750)
        stage("queue_cost_snapshot", preview["cost"])
        report["limitations"].append("Live queue accounting is an observation; in-progress attempts may not yet have terminal cost receipts. It does not change verification of the immutable freeze.")
        launch_form_path = ROOT / "docs/tasks/operator-v10/09-reviewed.json"
        if launch_form_path.exists():
            launch_form = snap.file(launch_form_path)
            launch_request = dict(version=1, step="launch", inputs=complete[7]["inputs"], candidate=candidate_binding,
                cost_admission_source=op.cost_binding(spec), fields=launch_form["fields"],
                receipt_output=str(ROOT / "docs/tasks/R1-58g-operator_v10/09-launch.receipt.json"),
                next_inputs=str(ROOT / "docs/tasks/R1-58g-operator_v10/09-inputs.json"),
                producer=snap.ref(op.__file__), implementation=d9.implementation_bindings(),
                host_mem_available_floor_mib=cost.get("host_mem_available_floor_mib",4096.0))
            digest = op.validate_signature(launch_form, launch_request)
            equal(launch_form["fields"], dict(matrix=bundle["matrix"], bindings=bundle["bindings"],
                                             receipt_root=str(ROOT / "logs/R1/final_queue"), workers=2),
                  "recorded launch form differs from frozen queue")
            require(any(r["status"] == "dry_run" and r["step"] == "launch" and
                        r["request_sha256"] == digest and not r["blocked"] for r in op.journal_read(JOURNAL)),
                    "recorded launch lacks exact unblocked preview")
            stage("recorded_launch_form", dict(request_sha256=digest, matches_frozen_queue=True,
                                                authority="existing saved delegated/lead form, not granted by X20"))
        # Any concurrent step 9 is outside the immutable verified steps 1-8 prefix.
        end_raw = JOURNAL.read_bytes()
        end_history = op.journal_read(JOURNAL)
        require(end_raw == JOURNAL.read_bytes() and end_raw.startswith(history_raw), "operator journal changed or rewrote reviewed history")
        report["later_journal_rows"] = [{k:r[k] for k in ("step","status","request_sha256")}
                                        for r in end_history[freeze_index+1:]]
        report["reviewed_inputs_sha256"] = snap.bindings
        snap.verify()
        stage("content_lock_final", lock.verify_lock(ROOT / "logs/r1_63o/final/live-content-lock.json"))
        report.update(status="passed", technical_launch_verification="passed", launch_performed=False,
                      sealed_payloads_parsed=0, gpu_seconds=0, model_calls=0)
    except Exception as error:
        report.update(status="blocked", defect=str(error), traceback=traceback.format_exc(), launch_performed=False)
        print(report["traceback"], flush=True)
    report.update(elapsed_seconds=time.monotonic()-started,
                  peak_process_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
                  finished_utc=datetime.now(timezone.utc).isoformat())
    out.mkdir(parents=True, exist_ok=False)
    (out / "verification.json").write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n")
    print(json.dumps({k:report[k] for k in ("status","elapsed_seconds","peak_process_rss_mib")}), flush=True)
    return 0 if report["status"] == "passed" else 2


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    require(args.output.resolve().is_relative_to(Path(__file__).resolve().parent), "review output must stay in lane logs")
    require(not args.output.exists(), "new output directory required")
    raise SystemExit(main(args.output))
