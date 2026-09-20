"""Native scheduler tests with synthetic JSON executors; no model or GPU."""
import importlib.util
import json
import math
import os
import signal
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

SPEC = importlib.util.spec_from_file_location("r1_77g_consumer", Path(__file__).with_name("consumer.py"))
consumer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(consumer)
q = consumer.queue
scheduler = consumer.scheduler


def put(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, sort_keys=True)
    return consumer.ref(path)


@pytest.fixture
def fake(tmp_path):
    root = tmp_path
    out = root / "results"
    receipts = root / "logs/queue"
    watched = []
    cells = [dict(cell_id=str(i), condition="synthetic", dataset="synthetic", realization=0, order=i,
                  block_number=1 if i<2 else 2, within_block_order=i+1, checkpoints=[1],
                  result_dir=str(out/str(i)), ceilings=dict(wall_seconds=100.0)) for i in range(3)]
    for c in cells:
        c["cell_id"] = q.analysis.coordinate_id(c)
        c["result_dir"] = str(out/c["cell_id"])
    matrix = dict(scope="development", cells=cells, queue_ceiling_contract=scheduler.CEILING_DEFINITION)
    mp = put(root/"matrix.json",matrix)
    bp = put(root/"bindings.json",dict(matrix_sha256=mp["sha256"],recipes={c["cell_id"]:{} for c in cells}))
    vp = put(root/"bindings-v2.json",dict(format=consumer.FORMAT,base_bindings=bp))
    def read(path):
        return json.loads(Path(path).read_bytes())
    def observe(cell, *, receipt_root=None, matrix_hash=None):
        cost = q.charged_cost(cell, q.cell_cost(cell["result_dir"]),receipt_root,matrix_hash)
        done = (Path(cell["result_dir"])/"complete.json").exists()
        row = dict(cell_id=cell["cell_id"],block=cell["block_number"], observed=dict(status="complete" if done else "missing",artifact_complete=done),cost=cost)
        return row, {}
    ns = dict(__file__=q.__file__,ROOT=root,sha=q.sha,read=read,validate_watch=lambda m:False,
              ordered=q.ordered,worker_factor=q.worker_factor,launch=lambda *a,**k:pytest.fail("real executor called"),
              recipe_for=lambda cell,bindings,execute=False: (dict(path=cell["cell_id"],sha256="fake"),dict(mode="synthetic",cell=cell,cid=cell["cell_id"])),
              verify_resume=lambda *a:None,post_cell_watch=lambda m,c,b:watched.append(c["cell_id"]),
              sealed=SimpleNamespace(MODE="sealed"),
              driver=SimpleNamespace(OUTPUT_ROOT=out,RESOURCE_ROOT=root/"empty-resources",cell_name=lambda m,h:m["cid"]),
              durable_json=put,observe_cell=lambda m,c,**kw:observe(c,**kw))
    def inventory(m, *, stop_after=None, receipt_root=None,matrix_hash=None,workers=2,ceiling_hours=None):
        rows=[]
        for cell in q.ordered(m,stop_after):
            row,_=observe(cell,receipt_root=receipt_root,matrix_hash=matrix_hash)
            count=scheduler.failure_history(ns,cell["cell_id"],receipt_root,matrix_hash)
            row["retry"]=dict(failures=count,exhausted=count>=2 and not row["observed"]["artifact_complete"])
            rows.append(row)
        unknown=[p for r in rows for p in r["cost"]["unknown_attempts"]]
        return dict(queue=rows,cost=dict(known_attempt_hours=math.fsum(r["cost"]["known_attempt_wall_seconds"] for r in rows)/3600,
                    unknown_attempts=unknown,ceiling_hours=ceiling_hours,basis="synthetic native process envelopes",
                    remaining_cell_ceiling_multiplier=q.worker_factor(workers)))
    ns["inventory"]=inventory
    def execute(binding, manifest, *, resume, output):
        directory=Path(manifest["cell"]["result_dir"])
        number=len(list(directory.glob("attempt-*")))
        put(directory/f"attempt-{number:04}"/"result.json",dict(attempt_wall_seconds=0.001))
        put(directory/"complete.json",{})
        time.sleep(0.01)
        return 0
    def run(namespace=None, path=None, executor=None, **kwargs):
        args=dict(receipt_root=receipts,stop_after=2,min_memory_mib=6144,ceiling_hours=750,
                  executor=executor or execute,memory_reader=lambda:100000,workers=2,lease_reader=lambda:{"pid":"synthetic"})
        args.update(kwargs)
        return scheduler.run_workers(namespace or ns,mp["path"],(path or bp)["path"],**args)
    return dict(ns=ns,mp=mp,bp=bp,vp=vp,matrix=matrix,cells=cells,receipts=receipts,watched=watched,
                run=run,execute=execute,read=read)


def amended(f):
    return consumer.namespace(f["ns"],f["vp"],f["read"](f["bp"]["path"]),authorization={"synthetic":True})


def test_factor_once_actual_budget_and_history_preserved(fake):
    one=fake["run"](stop_after=1)
    prior=one["inventory"]["cost"]["known_attempt_hours"]
    old_files={str(p):q.sha(p) for p in fake["receipts"].glob("*/*.json")}
    result=fake["run"](amended(fake),fake["vp"])
    assert result["status"]=="selected_blocks_complete"
    starts=[fake["read"](p) for p in fake["receipts"].glob("*/start.json")]
    assert len(starts)==3
    new=next(r for r in starts if r["cell_id"]==fake["cells"][2]["cell_id"])
    assert new["effective_wall_ceiling_seconds"]==170
    assert new["bindings_sha256"]==fake["vp"]["sha256"]
    assert new["admitted_prior_charged_seconds"]==pytest.approx(prior*3600)
    assert all(q.sha(p)==h for p,h in old_files.items())
    assert fake["read"](fake["mp"]["path"])["queue_ceiling_contract"]["workers_2_factor"]==1.15
    assert result["inventory"]["cost"]["remaining_cell_ceiling_multiplier"]==1.7
    assert not result["inventory"]["cost"]["unknown_attempts"]
    assert result["inventory"]["cost"]["known_attempt_hours"]>prior


def test_reservations_prevent_shared_cap_overrun(fake):
    result=fake["run"](amended(fake),fake["vp"],ceiling_hours=0.04,
                       executor=lambda *a,**k:pytest.fail("170s reservation cannot fit 144s cap"))
    assert result["status"]=="budget_stop"
    assert not list(fake["receipts"].glob("*/start.json"))


def test_unknown_costs_block_mixed_binding_resume(fake):
    put(fake["receipts"]/"lost"/"start.json",dict(cell_id=fake["cells"][0]["cell_id"],matrix_sha256=fake["mp"]["sha256"]))
    with pytest.raises(ValueError,match="unknown attempt costs"):
        fake["run"](amended(fake),fake["vp"],executor=lambda *a,**k:pytest.fail("unreconciled dispatch"))


def test_retry_count_survives_policy_version(fake):
    live=[True]
    def fail(*a,**kw):
        live[0]=False
        return 7
    fake["run"](executor=fail,workers=1,lease_reader=lambda:{"pid":1} if live[0] else None)
    result=fake["run"](amended(fake),fake["vp"])
    assert result["status"]=="selected_blocks_complete"
    starts=[fake["read"](p) for p in fake["receipts"].glob("*/start.json")]
    repeat=[r for r in starts if r["cell_id"]==fake["cells"][0]["cell_id"]]
    assert sorted(r["previous_cell_failures"] for r in repeat)==[0,1]
    assert repeat[0]["matrix_sha256"]==repeat[1]["matrix_sha256"]
    assert len([p for p in fake["receipts"].glob("*/finish.json")])==4


def test_parent_only_interrupt_drains_threads_without_killing_workers(fake):
    # Signals THIS test process only; never a live queue or process group.
    started=[]
    lock=threading.Lock()
    def execute(*a,**kw):
        with lock:
            started.append(a[1]["cid"])
            if len(started)==2:
                os.kill(os.getpid(),signal.SIGINT)
        time.sleep(0.1)
        return fake["execute"](*a,**kw)
    with pytest.raises(KeyboardInterrupt):
        fake["run"](executor=execute)
    assert set(started)=={c["cell_id"] for c in fake["cells"][:2]}
    assert len(list(fake["receipts"].glob("*/finish.json")))==2
    assert not list(fake["receipts"].glob("*/decision.json"))
    # Finishes are durable, but the interrupted parent's watch/decision callbacks
    # have not run. Resume must reconcile those before declaring a clean cutover.
    assert fake["watched"]==[]
    result=fake["run"](amended(fake),fake["vp"])
    assert result["status"]=="selected_blocks_complete"
    assert len(list(fake["receipts"].glob("*/start.json")))==3
    assert set(fake["watched"])=={c["cell_id"] for c in fake["cells"]}


def test_unknown_projection_remains_unknown(fake):
    inv=dict(queue=[],cost=dict(known_attempt_hours=1,unknown_attempts=["running"],ceiling_hours=750,basis="fixture"))
    projected=consumer.project(inv,fake["matrix"],2)
    assert projected["cost"]["projected_total_hours"] is None
    assert projected["cost"]["known_attempt_hours"]==1


def test_signature_bound_to_factor_and_consumer(fake):
    request=dict(step=consumer.STEP,factor=1.7,consumer=consumer.ref(consumer.__file__))
    form=dict(step=consumer.STEP,lead_approved=True,lead_signature=dict(name="synthetic CPU fixture",date="2026-09-20"),
              request_sha256=consumer.op.d9.core.content_digest(request))
    consumer.op.validate_signature(form,request)
    with pytest.raises(PermissionError):
        consumer.op.validate_signature(form,dict(request,factor=1.8))
    with pytest.raises(PermissionError):
        consumer.op.validate_signature(dict(form,lead_approved=False),request)


def test_changed_amendment_rejected_before_dispatch(fake):
    ns=amended(fake)
    Path(fake["vp"]["path"]).write_text('{"tampered":true}')
    with pytest.raises(ValueError,match="amendment bytes changed"):
        fake["run"](ns,fake["vp"],executor=lambda *a,**k:pytest.fail("changed amendment executed"))


def test_effective_factor_reaches_native_executor_timeout(fake):
    observed=[]
    def execute(binding, manifest, *, resume, output, max_wall_seconds):
        observed.append(max_wall_seconds)
        return fake["execute"](binding,manifest,resume=resume,output=output)
    ns=amended(fake)
    ns["launch"]=execute
    result=fake["run"](ns,fake["vp"],executor=execute)
    assert result["status"]=="selected_blocks_complete"
    assert observed==[170.0,170.0,170.0]


def test_single_worker_factor_preserved_and_invalid_worker_refused(fake):
    ns=amended(fake)
    assert ns["worker_factor"](1)==1.0
    with pytest.raises(ValueError):
        ns["worker_factor"](True)
    with pytest.raises(ValueError):
        ns["worker_factor"](3)


def test_real_proposal_consumer_verifies_and_legacy_queue_refuses():
    path=consumer.ROOT/"docs/tasks/R1-final-queue-bindings-v2.json"
    binding,proposal,base,matrix=consumer.load_policy(path)
    assert len(base["recipes"])==330 and proposal["lead_approved"] is False
    assert proposal["matrix_sha256"]==base["matrix_sha256"]
    with pytest.raises(ValueError,match="recipe not bound"):
        q.recipe_for(matrix["cells"][0],proposal)
    assert binding==consumer.ref(path)


def test_real_historical_report_is_not_idle_cutover_authority():
    _,proposal,_,matrix=consumer.load_policy(consumer.ROOT/"docs/tasks/R1-final-queue-bindings-v2.json")
    path=consumer.ROOT/"logs/R1/operator_reports/20260919-block1-try1/report.json"
    with pytest.raises(ValueError,match="globally reconciled|queue changed"):
        consumer.check_cutover(consumer.ref(path),proposal,matrix)


def test_original_launch_signature_cannot_approve_new_request():
    _,proposal,_,_=consumer.load_policy(consumer.ROOT/"docs/tasks/R1-final-queue-bindings-v2.json")
    binding=consumer.ref(consumer.ROOT/"docs/tasks/R1-final-queue-bindings-v2.json")
    req=consumer.request(binding,proposal,{"synthetic":"not an execution request"},2)
    old=q.read(consumer.ROOT/"docs/tasks/operator-v10/09-reviewed.json")
    with pytest.raises(PermissionError):
        consumer.op.validate_signature(old,req)


def test_accounting_supplement_preserves_v1_and_unknown_costs():
    spec=importlib.util.spec_from_file_location("r1_77g_test_accounting",Path(__file__).with_name("accounting.py"))
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    binding,proposal,_,matrix=consumer.load_policy(consumer.ROOT/"docs/tasks/R1-final-queue-bindings-v2.json")
    source=consumer.ref(consumer.ROOT/"logs/R1/operator_reports/20260919-block1-try1/report.json")
    value=module.supplement(binding,proposal,matrix,source)
    assert value["status"]=="unsigned_scenario_only"
    assert value["resume_authorization"] is None and value["actual_costs_changed"] is False
    old,new=value["frozen_v1_projection"],value["amended_v2_projection"]
    assert old["remaining_cell_ceiling_multiplier"]==1.15
    assert new["remaining_cell_ceiling_multiplier"]==1.7
    assert new["unknown_attempts"]==old["unknown_attempts"]
    assert new["projected_total_hours"] is old["projected_total_hours"] is None
    assert new["known_attempt_hours"]==old["known_attempt_hours"]
    assert consumer.ref(source["path"])==source


def test_exhausted_failures_cannot_reset_through_new_bindings(fake):
    # Both old-policy failures count after an amendment; no extra retry appears.
    fake["run"](stop_after=1,executor=lambda *a,**k:7)
    prior=len(list(fake["receipts"].glob("*/start.json")))
    assert prior==4
    result=fake["run"](amended(fake),fake["vp"],stop_after=1,
                       executor=lambda *a,**k:pytest.fail("exhausted retry reset"))
    assert result["status"]=="selected_blocks_processed_with_incomplete"
    assert len(list(fake["receipts"].glob("*/start.json")))==prior


def test_exact_bound_read_rejects_replaced_bytes_before_parsing(fake):
    path=Path(fake["vp"]["path"])
    path.write_text('{"different_complete_json":true}')
    with pytest.raises(ValueError,match="input hash differs"):
        consumer.read_ref(fake["vp"])
