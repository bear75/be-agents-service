#!/usr/bin/env python3
"""One-off: run metrics + build from-patch for solve/23 feb f506797a. Uses absolute paths."""
import json
import subprocess
import sys
from pathlib import Path

_PKG = Path(__file__).resolve().parent.parent
_OUT = _PKG / "solve" / "23 feb" / "export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json"
_IN = _PKG / "solve" / "23 feb" / "export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json"
_METRICS_DIR = _PKG / "solve" / "23 feb" / "metrics"
_PAYLOAD_PATH = _PKG / "solve" / "23 feb" / "from-patch" / "payload_f506797a.json"


def main():
    if not _OUT.exists() or not _IN.exists():
        print("Error: output or input file not found", file=sys.stderr)
        return 1

    scripts = _PKG / "scripts"

    # 1. solve_report
    print("Running solve_report (metrics + unassigned + empty-shifts)...")
    r1 = subprocess.run(
        [sys.executable, str(scripts / "solve_report.py"), str(_OUT), "--input", str(_IN), "--save", str(_METRICS_DIR)],
        cwd=str(_PKG),
    )
    if r1.returncode != 0:
        print("solve_report failed", file=sys.stderr)
        return r1.returncode

    # 2. build_from_patch
    _PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    print("Building from-patch payload...")
    r2 = subprocess.run(
        [sys.executable, str(scripts / "build_from_patch.py"), "--output", str(_OUT), "--input", str(_IN), "--out", str(_PAYLOAD_PATH), "--no-timestamp"],
        cwd=str(_PKG),
    )
    if r2.returncode != 0:
        print("build_from_patch failed", file=sys.stderr)
        return r2.returncode

    print(f"Metrics dir: {_METRICS_DIR}")
    print(f"From-patch payload: {_PAYLOAD_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
