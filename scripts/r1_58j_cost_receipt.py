"""Typed cost revision 3: measured endpoints, provenance-labelled host peaks, gaps intact."""

from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path

from scripts import r1_58h_cost_receipt as prior
from scripts import r1_d9_receipts as d9
from scripts.r1_58j_validation_inventory import audit as validation_audit
from scripts.r1_d10a_review import ROOT, write_new


def host_measurement(row):
    method = row["method"]
    if method == "direct_gnu_time":
        return row["measured_peak_host_mib"], []
    if method == "monitor_temporal_match":
        return row["measured_peak_host_mib"], []
    if method == "extrapolated_proposal":
        return None, [
            "same-condition cross-dataset host extrapolation proposed, not admitted or measured"
        ]
    return None, ["host process peak unavailable"]


def validate_supplement(receipt):
    """Extra revision-3 checks invoked by the existing typed cost validator."""
    validation = d9.read_metadata(receipt["validation_inventory"])
    if validation["full_validation_evidence_status"] != "complete":
        raise ValueError("full validation split evidence pending (revision3)")
    hosts = d9.read_metadata(receipt["host_peak_evidence"])["rows"]
    for cell in receipt["cells"]:
        key = cell["condition"] + ":" + cell["dataset"]
        h = hosts[key]
        value, pending = host_measurement(h)
        if pending or value is None:
            raise ValueError("host attribution/transfer pending: " + key)
        if cell["peak_host_mib"] != value * 1.5:
            raise ValueError("host source ceiling differs: " + key)
        if h["method"] == "direct_gnu_time":
            for name in ("source", "snapshot"):
                b = h[name]
                if d9.sha(b["path"]) != b["sha256"]:
                    raise ValueError("direct host evidence changed")
        else:
            from scripts.r1_58i_host_peaks import match_monitor

            index = d9.read_metadata(h["monitor_excerpts"])
            matched = match_monitor(h["window"], index)
            if (
                matched.get("process_key") != h["process_key"]
                or matched.get("measured_peak_host_mib") != value
            ):
                raise ValueError("host monitor attribution differs")


def build(output, evidence_dir, host_path):
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=False)
    host_ref = d9.ref(host_path)
    hosts = d9.read_metadata(host_ref)
    validation_ref = write_new(evidence_dir / "validation-coverage.json", validation_audit())
    spec = d9.read_metadata(d9.ref(ROOT / "docs/tasks/R1-D9-inputs-v7.json"))
    previous = d9.read_metadata(spec["cost_admission_source_unsigned"])
    profiles = prior.completed_profiles()
    receipt = copy.deepcopy(previous)
    receipt.update(
        receipt_revision=3,
        task="R1-58j",
        host_peak_evidence=host_ref,
        validation_inventory=validation_ref,
        cells=[],
        pending_evidence=["full validation split cost/admission evidence pending"],
        prior_receipt=spec["cost_admission_source_unsigned"],
        lead_approved=False,
        status="pending_evidence",
        full_validation_evidence_status="pending",
    )
    receipt["bindings"].update(
        producer=d9.ref(__file__),
        measurement_parser=d9.ref(prior.__file__),
        validator=d9.ref(ROOT / "scripts/r1_58h_cost_contract.py"),
        host_peak_evidence=host_ref,
        host_producer=d9.ref(ROOT / "scripts/r1_58i_host_peaks.py"),
        host_excerpts=hosts["monitor_excerpts"],
        validation_inventory=validation_ref,
        validation_producer=d9.ref(ROOT / "scripts/r1_58j_validation_inventory.py"),
    )
    measured = {
        key: prior.measurements(profiles.get(tuple(key.split(":")), [])) for key in hosts["rows"]
    }
    for original in previous["cells"]:
        cell = copy.deepcopy(original)
        key = cell["condition"] + ":" + cell["dataset"]
        evidence = measured[key]
        h = hosts["rows"][key]
        peak, pending = host_measurement(h)
        evidence["pending"] = [p for p in evidence["pending"] if "host peak absent" not in p]
        evidence["pending"] += pending
        evidence.update(
            measured_peak_host_mib=peak,
            host_method=h["method"],
            host_evidence=host_ref,
            host_row_key=key,
            host_peak_extrapolation_proposal=h.get("proposed_peak_host_mib"),
        )
        evidence["source_bindings"] += [host_ref, hosts["monitor_excerpts"]]
        if h["method"] == "direct_gnu_time":
            evidence["source_bindings"] += [h["snapshot"], h["source"], h["recipe"], h["result"]]
        if evidence["full_endpoint_evidence_status"] != "complete":
            donors = [
                (k, m)
                for k, m in measured.items()
                if k.endswith(":" + cell["dataset"])
                and m["full_endpoint_evidence_status"] == "complete"
            ]
            if donors:
                donor_key, donor = max(donors, key=lambda kv: kv[1]["endpoint_phase_seconds_total"])
                evidence["endpoint_transfer_proposal"] = dict(
                    donor=donor_key,
                    seconds=donor["endpoint_phase_seconds_total"],
                    rule="maximum full-endpoint measurement in same dataset; condition transfer is not a measurement",
                    reviewed=False,
                )
        receipt["pending_evidence"] += [key + ": " + p for p in evidence["pending"]]
        cell.update(
            peak_host_mib=None if peak is None else peak * 1.5,
            peak_device_mib=None
            if evidence["measured_peak_device_mib"] is None
            else evidence["measured_peak_device_mib"] * 1.5,
            measurement=write_new(evidence_dir / (key.replace(":", "-") + ".json"), evidence),
        )
        receipt["cells"].append(cell)
    receipt["full_endpoint_cost_basis_reviewed"] = False
    receipt["authority_note"] = (
        "unsigned revision3; direct / temporally matched / extrapolated host values distinguished; no missing full-validation or endpoint measurements invented"
    )
    return write_new(Path(output), receipt)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--evidence-dir", type=Path, required=True)
    p.add_argument("--host-evidence", type=Path, required=True)
    a = p.parse_args()
    print(json.dumps(build(a.output, a.evidence_dir, a.host_evidence), indent=2))
