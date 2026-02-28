import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_from_patch import build_patch

PKG = Path(__file__).resolve().parent.parent
out_data = json.loads((PKG / "solve/tf/export-field-service-routing-9789141a-f9b9-4dcb-aca6-9eb5c2dbe0eb-output.json").read_text())
in_data = json.loads((PKG / "solve/input_20260214_171612.json").read_text())
patch = build_patch(out_data, in_data, remove_empty_shifts=True, end_shifts_at_depot=True)
payload = {"config": {"run": {"name": "from-patch-trim-empty"}}, "patch": patch}
path = PKG / "from-patch" / "payload_9789141a.json"
path.parent.mkdir(parents=True, exist_ok=True)
path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
