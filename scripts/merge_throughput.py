"""Merge a partial throughput profile (e.g. the baseline arms) into results/S2/throughput.json."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
main = ROOT / "results" / "S2" / "throughput.json"
extra = Path(sys.argv[1])
a, b = json.loads(main.read_text()), json.loads(extra.read_text())
a["runs"].update(b["runs"])
for k in list(a.get("unavailable", {})):
    if any(key.split("/")[0] == k for key in b["runs"]):
        a["unavailable"].pop(k)
a.setdefault("merged", []).append({"from": str(extra.resolve().relative_to(ROOT)), "runs": sorted(b["runs"]), "timestamp": b.get("timestamp")})
main.write_text(json.dumps(a, indent=1, default=float))
print("merged", sorted(b["runs"]), "unavailable now", a["unavailable"])
