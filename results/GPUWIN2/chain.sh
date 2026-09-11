#!/bin/bash
# GPU window 2 (2026-09-11): gpu test subset, then the real-artifact identity control. Sequential; fail-fast per step recorded.
cd /home/derp/cap/pc_cap
OUT=results/GPUWIN2
echo "start $(date -u +%FT%TZ)" > $OUT/status.txt
/home/derp/cap/venv/bin/python -m pytest -q -p no:cacheprovider tests -m gpu > $OUT/gpu_tests.log 2>&1
echo "gpu_tests exit $? $(tail -1 $OUT/gpu_tests.log)" >> $OUT/status.txt
/home/derp/cap/venv/bin/python - > $OUT/identity_control.json 2> $OUT/identity_control.err <<'PY'
import json
import pccap
from pccap.bases.bp import BPBase
from pccap.data.tokenize import GPT2Tokenizer
from pccap.harness.identity import PreflightRefusal, check_frozen_identity
from pccap.fixtures.grammar_model import WEIGHTS
frozen = json.load(open("manifests/frozen.draft.json"))
base, tok = BPBase(), GPT2Tokenizer()
out = {"positive": check_frozen_identity(frozen, base=base, base_kind="BP", tokenizer=tok)}
out["grammar"] = check_frozen_identity(frozen, base_kind="GRAM", weights_path=WEIGHTS)
out["epc"] = check_frozen_identity(frozen, base_kind="EPC")
bad = json.loads(json.dumps(frozen)); bad["base_checkpoints"]["bp"]["param_digest"] = "1" * 64
try:
    check_frozen_identity(bad, base=base, base_kind="BP", tokenizer=tok); out["negative_bp"] = "NOT REFUSED"
except PreflightRefusal as e:
    out["negative_bp"] = f"refused: {e}"
bad = json.loads(json.dumps(frozen)); bad["tokenizer_rev"]["tokenizer_json_sha256"] = "3" * 64
try:
    check_frozen_identity(bad, base=base, base_kind="BP", tokenizer=tok); out["negative_tok"] = "NOT REFUSED"
except PreflightRefusal as e:
    out["negative_tok"] = f"refused: {e}"
out["determinism"] = pccap.determinism_report()
print(json.dumps(out, indent=1, default=str))
PY
echo "identity_control exit $?" >> $OUT/status.txt
echo "end $(date -u +%FT%TZ)" >> $OUT/status.txt
