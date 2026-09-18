"""DEC-063 production metadata and independent vector analysis; no model/JAX imports."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np
from scripts.ht_audit_existing import statistics, tail_sum

ROOT = Path(__file__).resolve().parents[1]
POLICY = "DEC-063-complete-windows-final-both-references-v1"
FIELDS = ["loss_cap", "loss_capoff", "loss_original", "kl_capoff_to_cap", "kl_original_to_cap"]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def ref(path):
    path = Path(path).resolve()
    return dict(path=str(path), sha256=sha(path))


def digest(value):
    # Execution's analysis.digest uses the default ASCII JSON convention.
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
    ).hexdigest()


def read(binding):
    path = Path(binding["path"]).resolve()
    if "confirm" in path.parts or sha(path) != binding["sha256"]:
        raise ValueError("full-validation binding changed or forbidden path")
    return path


def production_contract():
    inventory = ROOT / "manifests/dev/lm_sets.json"
    source = json.loads(inventory.read_text())["files"]["drift_tokens"]
    tokens = np.load(read(source), mmap_mode="r", allow_pickle=False)
    if (
        tokens.ndim != 1
        or tokens.dtype.kind not in "iu"
        or len(tokens) != 247289
        or source["shape"] != [247289]
    ):
        raise ValueError("DEC-063 source shape/type changed")
    windows = tokens[: 1931 * 128].reshape(1931, 128)
    return dict(
        schema_version=1,
        policy=POLICY,
        source_inventory=ref(inventory),
        source={k: source[k] for k in ("path", "sha256")},
        source_tokens=247289,
        window_tokens=128,
        complete_windows=1931,
        expected_positions=245237,
        trailing_tokens_dropped=121,
        windows_int64le_sha256=hashlib.sha256(
            np.asarray(windows, dtype="<i8").tobytes()
        ).hexdigest(),
        tail_policy="drop_incomplete_trailing_window",
        context_policy="reset_every_window",
        checkpoint_policy="final_only_plus_sample_at_every_checkpoint",
        references=["own_capoff", "original_base"],
        kl_direction="reference || cap",
        sample_windows=128,
    )


def validate(contract):
    if not isinstance(contract, dict) or digest(contract) != digest(production_contract()):
        raise ValueError("required DEC-063 full-validation contract missing or altered")
    return contract


def sample(contract, definition):
    validate(contract)
    source = np.load(read(contract["source"]), mmap_mode="r", allow_pickle=False)
    n, width = contract["sample_windows"] or len(definition["windows"]), contract["window_tokens"]
    rows = np.asarray(definition["windows"])
    if (
        rows.dtype.kind not in "iu"
        or rows.shape != (n, width)
        or not np.array_equal(rows, source[: n * width].reshape(n, width))
        or definition["expected_positions"] != n * (width - 1)
    ):
        raise ValueError("sampled drift must be the bound full-validation prefix")


def admit(manifest, protocol, frozen):
    """Called by the proposed backend after normal signed-freeze admission."""
    if protocol.get("schema_version") == 1 and "full_validation" not in manifest:
        return  # Explicitly retained historical protocol, not DEC-063 admission.
    contract = validate(manifest.get("full_validation"))
    implementation = ref(__file__)
    for name, value in (("protocol", protocol), ("freeze", frozen)):
        if (
            digest(value.get("full_validation")) != digest(contract)
            or value.get("full_validation_implementation") != implementation
        ):
            raise ValueError("full-validation recipe/" + name + "/implementation mismatch")
    if manifest.get("full_validation_implementation") != implementation:
        raise ValueError("full-validation recipe implementation mismatch")
    if frozen.get("bindings_sha256", {}).get(implementation["path"]) != implementation["sha256"]:
        raise ValueError("full-validation implementation absent from frozen bindings")


def summary(
    section,
    contract,
    report,
    report_path,
    manifest_sha256,
    adapter_identity,
    sources,
    *,
    sampled_population=None,
):
    """Recompute metrics from exact bound NPZ bytes; absence never becomes a pass."""
    validate(contract)
    planned = contract["expected_positions"]
    absent = dict(
        status="missing_full_validation",
        planned=planned,
        scored=0,
        complete=False,
        fidelity=None,
        references={},
        population="full_validation_DEC063",
    )
    if section is None:
        return absent
    if section.get("status") != "complete":
        return dict(absent, status="incomplete_full_validation")
    if (
        section.get("policy") != POLICY
        or section.get("checkpoint") != report["checkpoint"]
        or section.get("state_sha256") != report["state_sha256"]
        or section.get("manifest_sha256") != manifest_sha256
        or section.get("contract_sha256") != digest(contract)
        or section.get("source") != contract["source"]
        or section.get("source_inventory") != contract["source_inventory"]
    ):
        raise ValueError("full-validation report identity/contract mismatch")
    coverage = {
        k: contract[k]
        for k in (
            "source_tokens",
            "window_tokens",
            "complete_windows",
            "expected_positions",
            "trailing_tokens_dropped",
            "windows_int64le_sha256",
        )
    }
    if section.get("coverage") != coverage or section.get("scored_positions") != planned:
        raise ValueError("full-validation coverage differs from independent population")
    expected_refs = dict(
        own_capoff=adapter_identity["base_sha256"],
        original_base=adapter_identity["locality_base_sha256"],
    )
    if section.get("reference_base_sha256") != expected_refs:
        raise ValueError("full-validation original/own cap-off base identity differs")
    binding = section["vectors"]
    original = Path(binding["path"]).resolve()
    report_path = Path(report_path).resolve()
    path = report_path.parent / f"full-validation-{report['checkpoint']}.npz"
    if original.name != path.name or original.parent.name != path.parent.name:
        raise ValueError("full-validation vector attempt/location mismatch")
    if not path.is_relative_to(ROOT / "results"):
        raise PermissionError("analysis vector must be in the declared repo result attempt")
    if not path.is_file():
        return dict(absent, status="missing_full_validation_vectors")
    h = sha(path)
    if h != binding["sha256"] or (str(path) in sources and sources[str(path)] != h):
        raise ValueError("full-validation vector hash changed")
    shape = (contract["complete_windows"], contract["window_tokens"] - 1, 5)
    with np.load(path, allow_pickle=False) as archive:
        if archive.files != ["values"]:
            raise ValueError("unexpected full-validation array inventory")
        values = archive["values"]
        if (
            values.shape != shape
            or values.dtype != np.float64
            or not np.isfinite(values).all()
            or binding.get("fields") != FIELDS
            or binding.get("shape") != list(shape)
            or binding.get("dtype") != "float64"
            or np.any(values < 0)
        ):
            raise ValueError("full-validation vector shape/type/finiteness differs")
    if sha(path) != h:
        raise ValueError("full-validation vectors changed during read")
    sources[str(path)] = h
    # Verify overlap independently of the producer's claimed pass flag.
    rows = report.get("endpoints", {}).get("drift", {}).get("rows", [])
    n_sample = (
        contract["sample_windows"] * (contract["window_tokens"] - 1)
        if contract["sample_windows"] is not None
        else sampled_population["expected_positions"]
    )
    ids = [f"w{i // shape[1]}:p{1 + i % shape[1]}" for i in range(n_sample)]
    if len(rows) != n_sample or [r["item_id"] for r in rows] != ids:
        raise ValueError("full-validation overlap sample incomplete or reordered")
    other = np.asarray([[r[k] for k in ("cap", "capoff", "original")] for r in rows])
    overlap = values.reshape(-1, 5)[:n_sample, :3]
    if not np.isfinite(other).all() or np.max(np.abs(other - overlap)) > 1e-3:
        raise ValueError("full-validation overlap losses differ")
    for index in (1, 2):
        for threshold in (0.01, 0.1, 1.0):
            if np.count_nonzero(other[:, 0] - other[:, index] > threshold) != np.count_nonzero(
                overlap[:, 0] - overlap[:, index] > threshold
            ):
                raise ValueError("full-validation overlap exceedances differ")
    locations = [f"w{i // shape[1]}:p{1 + i % shape[1]}" for i in range(planned)]
    references = {}
    for name, loss_index, kl_index in (("capoff", 1, 3), ("original", 2, 4)):
        loss = (values[:, :, 0] - values[:, :, loss_index]).ravel()
        kl = values[:, :, kl_index].ravel()
        harm, divergence = statistics(loss.tolist(), locations), statistics(kl.tolist(), locations)
        for stats, values_vector in ((harm, loss), (divergence, kl)):
            stats["ES99_positive"] = tail_sum(np.maximum(values_vector, 0).tolist(), 0.01) / (
                0.01 * planned
            )
        harm["exp_mean_signed"] = (
            math.exp(harm["mean_signed"]) if harm["mean_signed"] < 709 else None
        )
        harm["exp_mean_signed_overflow"] = harm["mean_signed"] >= 709
        # These fields are common to the R1-68f producer and independent HT-1 audit.
        for key, observed in (("loss_delta_" + name, harm), ("kl_" + name + "_to_cap", divergence)):
            saved = section["statistics"][key]
            for field in ("n", "maximum_location", "maximum_tie_count", "exceedances_nats"):
                if saved[field] != observed[field]:
                    raise ValueError("full-validation stored tail summary differs")
            for field in (
                "mean_signed",
                "mean_positive",
                "ES95_positive",
                "maximum_signed",
                "maximum_positive",
            ):
                if not np.isclose(saved[field], observed[field], rtol=1e-12, atol=1e-12):
                    raise ValueError("full-validation stored numerical summary differs")
        references[name] = dict(
            loss=harm,
            kl=divergence,
            mean_reference_loss_nats=float(values[:, :, loss_index].mean()),
            mean_cap_loss_nats=float(values[:, :, 0].mean()),
        )
    fidelity = dict(
        mean_kl_ceiling_nats=0.001,
        mean_loss_increase_ceiling_nats=0.01,
        references={
            name: dict(
                mean_kl_pass=value["kl"]["mean_signed"] <= 0.001,
                mean_loss_pass=value["loss"]["mean_signed"] <= 0.01,
            )
            for name, value in references.items()
        },
    )
    fidelity["passes"] = all(all(v.values()) for v in fidelity["references"].values())
    return dict(
        status="complete",
        complete=True,
        planned=planned,
        scored=planned,
        fidelity=fidelity,
        population="full_validation_DEC063",
        contract_sha256=digest(contract),
        coverage=coverage,
        vectors=dict(path=str(path), sha256=h),
        references=references,
        overlap_gate="independently_verified",
        fidelity_role="registered secondary fidelity endpoint; not part of the 63 primary intervals",
        interpretation="finite complete fixed-validation population; tail statistics descriptive, not evidence of a power-law distribution",
    )


def report_lines(cells):
    if not any(
        "sampled_drift" in cp.get("secondary", {}) or "full_validation" in cp.get("secondary", {})
        for cell in cells
        for cp in cell.get("checkpoints", {}).values()
    ):
        return []
    lines = [
        "",
        "DEC-063 full validation at the final checkpoint (separate from the descriptive 128-window sample):",
        "",
        "| Cell | Population | Scored / planned | Reference | Mean loss change | Mean KL | ES95 positive loss harm | Max positive loss harm | > .1 nat | Status |",
        "|---|---|---|---|---:|---:|---:|---:|---:|---|",
    ]
    for cell in cells:
        for n, cp in cell.get("checkpoints", {}).items():
            secondary = cp.get("secondary", {})
            sample = secondary.get("sampled_drift")
            if sample is not None:
                refs = sample.get("references", {})
                for name in ("capoff", "original"):
                    value = refs.get(name)
                    if value is None:
                        metrics = "— | — | — | — | —"
                    else:
                        metrics = (
                            f"{value['mean_signed_nats']:.8g} | unavailable | "
                            f"{value['ES95_positive_nats']:.8g} | "
                            f"{value['max_positive_nats']:.8g} | {value['count_above_0_1_nats']}"
                        )
                    lines.append(
                        f"| {cell['cell_id']} @ {n} | 128-window sample (descriptive) | "
                        f"{sample['scored_positions']} / {sample['planned_positions']} | "
                        f"{name} | {metrics} | {sample['status']} |"
                    )
            full = secondary.get("full_validation")
            if full is None:
                continue
            refs = full.get("references", {})
            if not refs:
                lines.append(
                    f"| {cell['cell_id']} @ {n} | full validation | {full['scored']} / {full['planned']} | both | — | — | — | — | — | {full['status']} |"
                )
            for name, value in refs.items():
                loss, kl = value["loss"], value["kl"]
                lines.append(
                    f"| {cell['cell_id']} @ {n} | full validation | {full['scored']} / {full['planned']} | {name} | {loss['mean_signed']:.8g} | {kl['mean_signed']:.8g} | {loss['ES95_positive']:.8g} | {loss['maximum_positive']:.8g} | {loss['exceedances_nats']['0.1']['count']} | {full['status']} |"
                )
    lines += [
        "",
        "Sampled and full populations are separate; KL is retained only for the full assay. "
        "JSON includes ES99 and all .01/.1/1-nat exceedances for both populations. "
        "Full-validation absence or invalid vectors do not acquire scientific admission.",
    ]
    return lines
