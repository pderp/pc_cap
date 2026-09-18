"""Final precommit repair: align candidate's display allocation reference with inputs.
No published/signed artifact may exist; only this lane's generated package files
can be refreshed. Not an operator command or permission to rebind a live session.
"""
import json
from pathlib import Path
from scripts import r1_63o_package as package
from scripts import r1_63o_graph as graph
r=package.ROOT
assert not (r/'logs/R1/operator_v10/receipts.jsonl').exists()
for name in ('clearance','draw','seal'):
 assert not (r/f'docs/tasks/R1-v15-{name}.receipt.json').exists()
c=json.loads((r/'manifests/revision_v1/freeze_candidate_v15.json').read_text())
assert all(c[k] is False for k in ('confirmation_protocol_frozen','draw_authorized','launch_authorized'))
original=graph.write
changes=[]
def put(path,value):
 p=Path(path).resolve()
 raw=value if isinstance(value,bytes) else (json.dumps(value,sort_keys=True,indent=2,allow_nan=False)+'\n').encode()
 if p.exists() and p.read_bytes()!=raw:
  assert p.is_relative_to(r/'docs/tasks') or p.is_relative_to(r/'manifests/revision_v1') or p.is_relative_to(r/'logs/r1_63o/final') or p.is_relative_to(r.parent/'assets/runs/pc_cap/R1/r1_63o/v15')
  changes.append(dict(path=str(p),previous_sha256=graph.sha(p)))
  p.write_bytes(raw)
 return original(p,value)
graph.write=put
proof=package.build()
graph.write=original
original(r/'logs/r1_63o/precommit-final-metadata-repair.json',dict(reason='Final review aligns candidate allocation reference with inputs and queue human-readable block labels with DEC-068 ordering. No scientific quantities or cell coordinates changed.',changes=changes,proof=proof))
print('refreshed',len(changes),'unreleased owned artifacts; no signatures existed')
