"""Apply explicit, hash-verified legacy-name aliases to the HT-3d inventory.

The ordinary seed2 reader was already evaluated under v5_rare1_n100. Only two
declared unseen-summary aliases are permitted; neither values nor IDs are filled.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts import ht3d_pilot_aggregate as core

ROOT = core.ROOT
ALIASES = ROOT / "docs/tasks/HT-3d-ordinary-seed2-unseen-aliases.json"


def verify_alias(inputs, entry):
    if (
        entry["arm"] != "ordinary"
        or entry["seed"] != 2
        or entry["dataset"] not in ("counterfact", "mquake")
    ):
        raise ValueError("only the two declared ordinary seed2 aliases are allowed")
    expected = f"results/R1/endpoints/r1_50_stream_sel6_text_s2_stepavg_rare1_n100_unseen_{entry['dataset']}/summary.json"
    if entry["requested_path"] != expected:
        raise ValueError("wrong requested alias")
    actual = inputs.read(entry["observed_path"])
    if inputs.bindings[entry["observed_path"]] != entry["observed_sha256"]:
        raise ValueError("alias file hash mismatch")
    reference = inputs.read(entry["population_reference"]["path"])
    if (
        inputs.bindings[entry["population_reference"]["path"]]
        != entry["population_reference"]["sha256"]
    ):
        raise ValueError("population-reference hash mismatch")
    if (
        actual["theta"] != entry["theta"]
        or core.sha(entry["theta"]["path"]) != entry["theta"]["sha256"]
    ):
        raise ValueError("alias checkpoint mismatch")
    if (
        actual["tag"] != "v5_rare1_n100"
        or actual["dataset"] != entry["dataset"]
        or actual["n_edits"] != 100
    ):
        raise ValueError("alias evaluation configuration mismatch")
    for field in ("edited_item_ids", "outside_item_ids"):
        if len(actual[field]) != 100 or actual[field] != reference[field]:
            raise ValueError("alias population mismatch")
    return actual


class AliasedInputs(core.Inputs):
    def __init__(self, root, entries):
        super().__init__(root)
        self.aliases = {e["requested_path"]: e for e in entries}
        if len(entries) != len(self.aliases):
            raise ValueError("duplicate aliases")
        self.used = []

    def read(self, relative):
        if relative not in self.aliases or (self.root / relative).exists():
            return super().read(relative)
        entry = self.aliases[relative]
        value = verify_alias(self, entry)
        self.used.append(entry)
        return value


def aggregate():
    report = core.aggregate()
    aliases = core.Inputs(ROOT)
    entries = aliases.read(str(ALIASES.relative_to(ROOT)))["aliases"]
    inputs = AliasedInputs(ROOT, entries)
    for i, row in enumerate(report["rows"]):
        if (
            row["arm"] == "ordinary"
            and row["seed"] == 2
            and row["dataset"] in ("counterfact", "mquake")
        ):
            try:
                replacement = core.extract_row(inputs, row["arm"], row["seed"], row["dataset"])
                # Preserve a training-abort status even if endpoint aliases exist.
                if any(f["run"] == row["run"] for f in report["failures"]):
                    replacement["status"] = "charged_failure"
                report["rows"][i] = replacement
            except (OSError, ValueError, KeyError, TypeError) as exc:
                report["source_errors"].append("alias validation failed: " + str(exc))
    report["input_bindings"].update(aliases.bindings)
    report["input_bindings"].update(inputs.bindings)
    report["source_errors"] += ["changed during alias resolution: " + p for p in inputs.unchanged()]
    report["arms"] = core.summarize(report["rows"])
    report["comparisons"] = core.comparisons(
        report["arms"], report["rows"], report["failures"], report["source_errors"]
    )
    report["complete_rows"] = sum(r["status"] == "complete" for r in report["rows"])
    report["legacy_name_aliases"] = inputs.used
    report["alias_policy"] = (
        "Measured files reused only after checkpoint SHA, evaluator tag, occupancy and exact ordered edit/outside populations verify. Raw source names and hashes are retained."
    )
    report["alias_producer"] = {"path": str(Path(__file__).resolve()), "sha256": core.sha(__file__)}
    # Audit the whole assembled snapshot again, including original input files.
    for path, h in report["input_bindings"].items():
        if core.sha(ROOT / path) != h:
            raise ValueError("input changed during combined report")
    return report


def markdown(report):
    return (
        core.markdown(report)
        + "\n## Verified historical-name aliases\n\n"
        + report["alias_policy"]
        + "\n\n"
        + "\n".join(
            f"- Requested {e['requested_path']}; measured source {e['observed_path']} (SHA-256 {e['observed_sha256']})."
            for e in report["legacy_name_aliases"]
        )
        + "\n"
    )


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output-prefix", type=Path, required=True)
    a = p.parse_args(argv)
    base = a.output_prefix.resolve()
    paths = [Path(str(base) + s) for s in (".json", ".md")]
    if not base.is_relative_to(ROOT / "logs/r1_round18") or any(p.exists() for p in paths):
        p.error("new output prefix under logs/r1_round18 required")
    r = aggregate()
    base.parent.mkdir(parents=True, exist_ok=True)
    for path, text in zip(
        paths, [json.dumps(r, indent=2, allow_nan=False) + "\n", markdown(r)], strict=True
    ):
        with path.open("x") as f:
            f.write(text)
    print(
        json.dumps(
            {
                "complete_rows": r["complete_rows"],
                "verdicts": {k: v["verdict"] for k, v in r["comparisons"].items()},
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
