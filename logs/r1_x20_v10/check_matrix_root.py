"""Independent check of every non-cell final-matrix field against D.5."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
bindings = {}


def read(path):
    p = Path(path).resolve()
    raw = p.read_bytes()
    bindings[str(p)] = hashlib.sha256(raw).hexdigest()
    return json.loads(raw)


def same(left, right):
    if left != right:
        keys = sorted(k for k in set(left) | set(right) if left.get(k) != right.get(k))
        raise ValueError("matrix fields differ: " + str(keys))


candidate = read(ROOT / "manifests/revision_v1/freeze_candidate_v15.json")
declaration = read(candidate["matrix"]["path"])
same({"sha256": bindings[candidate["matrix"]["path"]]}, {"sha256": candidate["matrix"]["sha256"]})
final = read(ROOT / "manifests/revision_v1/run_matrix_final.json")
frozen_path = ROOT / "manifests/revision_v1/frozen_stage4.json"
frozen = read(frozen_path)
expected = {k:v for k,v in declaration.items() if k not in ("cells", "extension")}
# The sole publication-time root updates in the pinned producer. All other
# fields, including inference interpretation and implementations, stay exact.
expected.update(scope="confirmatory",
                queue_ceiling_contract="solo_whole_cell_process_wall_seconds; two-worker multiplier once; retry the same seed/order at most once; failures consume shared cap",
                source_matrix=candidate["matrix"], fidelity_watch=frozen["fidelity_watch"],
                freeze=dict(path=str(frozen_path), sha256=bindings[str(frozen_path)]),
                shared_process_hours=750, cost_admission=frozen["cost_admission"],
                endpoint_contract_version=1, full_validation=candidate["full_validation"])
# Read the exact contract constant from source AST, without importing JAX or
# allowing the published matrix to supply its own expected contract.
import ast
source_path = ROOT / "scripts/r1_77f_scheduler.py"
raw = source_path.read_bytes()
bindings[str(source_path)] = hashlib.sha256(raw).hexdigest()
module = ast.parse(raw)
assignment = next(n for n in module.body if isinstance(n, ast.Assign) and
                  any(isinstance(t, ast.Name) and t.id == "CEILING_DEFINITION" for t in n.targets))
expected["queue_ceiling_contract"] = ast.literal_eval(assignment.value)
actual = {k:v for k,v in final.items() if k not in ("cells", "extension")}
same(actual, expected)
extension = {k:v for k,v in declaration["extension"].items() if k != "cells"}
extension["allocation_approved"] = True
same({k:v for k,v in final["extension"].items() if k != "cells"}, extension)
bad = dict(actual, accepted_primary_intervals=-1)
try:
    same(bad, expected)
except ValueError:
    rejected = True
else:
    raise AssertionError("changed inference/design field accepted")
for path, sha in bindings.items():
    with Path(path).open("rb") as stream:
        same({"sha": hashlib.file_digest(stream, "sha256").hexdigest()}, {"sha": sha})
report = dict(status="passed", final_root_fields=len(actual), exact_unchanged_design_fields=True,
              extension_metadata_exact=True, tampered_design_field_rejected=rejected,
              source_bindings_sha256=bindings)
with (Path(__file__).parent / "matrix-root-verification.json").open("x") as stream:
    json.dump(report, stream, indent=2, sort_keys=True)
    stream.write("\n")
print(json.dumps(report, sort_keys=True))
