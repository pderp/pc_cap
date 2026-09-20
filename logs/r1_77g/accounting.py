"""Supplement a canonical D11 report with explicitly versioned ceiling forecasts.

D11/D13 remain unchanged and continue to report their frozen 1.15 forecast.
This file never relabels that forecast as the amended live allowance. Actual
charged process time and unknown costs are identical in both views.
"""
import argparse
import importlib.util
import json
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("r1_77g_accounting_consumer", Path(__file__).with_name("consumer.py"))
consumer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(consumer)


def supplement(proposal_binding, proposal, matrix, source_binding, authorization=None):
    report = consumer.read_ref(source_binding)
    consumer.require(report["task"] == "R1-D11" and report["report_sha256"] == consumer.reprice.digest(
        {k:v for k,v in report.items() if k != "report_sha256"}), "D11 digest differs")
    consumer.require(report["identity"]["matrix"] == proposal["matrix"] and
                     report["identity"]["receipt_root"] == proposal["receipt_root"] and
                     report["identity"]["workers"] == 2 and report["identity"]["ceiling_hours"] == 750,
                     "D11 identity differs from proposed continuation")
    if authorization is not None:
        admission = consumer.read_ref(authorization)
        request = admission["request"]
        consumer.require(admission["status"] == "authorized" and request["step"] == consumer.STEP
                         and request["bindings"] == proposal_binding and request["matrix"] == proposal["matrix"]
                         and request["receipt_root"] == proposal["receipt_root"] and request["workers"] == 2
                         and request["workers_2_factor"] == 1.7 and request["ceiling_hours"] == 750,
                         "different resume authorization")
        consumer.op.validate_signature(consumer.read_ref(admission["form"]), request)
    cost = consumer.project(report["inventory"], matrix, 2)["cost"]
    return dict(task="R1-77g-accounting",schema_version=1,
                status="authorized_amendment_view" if authorization else "unsigned_scenario_only",
                d11_report=source_binding,amendment=proposal_binding,resume_authorization=authorization,
                producer=consumer.ref(__file__),consumer=consumer.ref(consumer.__file__),
                frozen_v1_projection=report["inventory"]["cost"],amended_v2_projection=cost,
                actual_costs_changed=False,canonical_D11_modified=False,
                note="Use the v2 projection with its explicit authorization/snapshot date; canonical D11/D13 remain the frozen v1 forecast. Unknown live cost remains unknown. This is not an experimental result or a launch.")


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bindings",type=Path,required=True)
    parser.add_argument("--d11",type=Path,required=True)
    parser.add_argument("--authorization",type=Path)
    parser.add_argument("--output",type=Path,required=True)
    args=parser.parse_args()
    binding,proposal,_,matrix=consumer.load_policy(args.bindings)
    output=args.output.resolve()
    consumer.require(output.is_relative_to(consumer.ROOT/"logs") and not output.exists(),"new logs file required")
    value=supplement(binding,proposal,matrix,consumer.ref(args.d11),
                     consumer.ref(args.authorization) if args.authorization else None)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open("x") as stream:
        json.dump(value,stream,indent=2,sort_keys=True,allow_nan=False)
        stream.write("\n")
    print(json.dumps(dict(status=value["status"],output=str(output),actual_costs_changed=False)))
