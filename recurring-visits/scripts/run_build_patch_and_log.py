#!/usr/bin/env python3
"""Run build_from_patch and write log to solve/23 feb/run_log.txt."""
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent.parent
_LOG = Path(__file__).resolve().parent / "run_log_23feb.txt"
_OUT = _PKG / "solve" / "23 feb" / "export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json"
_IN = _PKG / "solve" / "23 feb" / "export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json"
_PAYLOAD = _PKG / "solve" / "from-patch-23feb-payload.json"


def main():
    _LOG.parent.mkdir(parents=True, exist_ok=True)
    log_lines = []

    def log(msg):
        log_lines.append(msg)
        print(msg, flush=True)

    try:
        log("Loading output...")
        import json
        with open(_OUT) as f:
            output_data = json.load(f)
        log(f"Output loaded, keys: {list(output_data.keys())}")

        log("Loading input...")
        with open(_IN) as f:
            input_data = json.load(f)
        log("Input loaded.")

        log("Running build_patch...")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from build_from_patch import build_patch
        patch = build_patch(output_data, input_data, remove_empty_shifts=True, end_shifts_at_depot=True)
        log(f"Patch has {len(patch)} operations.")

        _PAYLOAD.parent.mkdir(parents=True, exist_ok=True)
        payload = {"config": {"run": {"name": "from-patch-trim-empty"}}, "patch": patch}
        with open(_PAYLOAD, "w") as f:
            json.dump(payload, f, indent=2)
        log(f"Wrote {_PAYLOAD}")

    except Exception as e:
        log(f"Error: {e}")
        import traceback
        log(traceback.format_exc())
    finally:
        with open(_LOG, "w") as f:
            f.write("\n".join(log_lines))


if __name__ == "__main__":
    main()
