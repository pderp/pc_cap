"""SD-22: grammar paraphrases are identical across processes (no per-process hash salt in the seed)."""

import json
import subprocess
import sys

CODE = """
import json
from pccap.data import grammar_streams as gs
from pccap.fixtures.grammar_eval import with_paraphrases
items = with_paraphrases(gs.load_task_items(3, 0, 4))
print(json.dumps([[it.item_id, it.paraphrases] for it in items]))
"""


def test_paraphrases_identical_across_processes():
    runs = []
    for salt in ("1", "2"):
        out = subprocess.run([sys.executable, "-c", CODE], capture_output=True, text=True, env={"PYTHONHASHSEED": salt, "JAX_PLATFORMS": "cpu", "PATH": "/usr/bin:/bin"}, check=True)
        runs.append(json.loads(out.stdout.strip().splitlines()[-1]))
    assert runs[0] == runs[1]
    assert all(len(p) >= 1 for _, p in runs[0])
