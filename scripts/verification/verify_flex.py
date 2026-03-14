#!/usr/bin/env python3
"""
Verify that EVERY visit in a Timefold FSR input JSON has flex (time or day).

Rule: ALLA BESÖK HAR FLEX — antingen för en dag (tid-flex: minStartTime != maxStartTime)
eller för flera dagar/veckor (dag-flex: flera time windows eller ett fönster som spänner flera dagar).

Usage:
  python3 verify_all_visits_have_flex.py export-field-service-routing-v1-4mars-2v-input.json
  python3 verify_all_visits_have_flex.py path/to/any-input.json

Exit code: 0 if all visits have flex, 1 if any violation (and list them).
"""

import json
import sys
from pathlib import Path


def verify(model_input: dict) -> tuple[bool, list[tuple[str, str]]]:
    violations: list[tuple[str, str]] = []
    visits: list[dict] = list(model_input.get("visits") or [])
    for g in model_input.get("visitGroups") or []:
        visits.extend(g.get("visits") or [])

    for v in visits:
        vid = v.get("id", "")
        tws = v.get("timeWindows") or []
        if not tws:
            violations.append((vid, "no time windows"))
            continue
        if len(tws) > 1:
            continue
        tw = tws[0]
        min_s = (tw.get("minStartTime") or "").strip()
        max_s = (tw.get("maxStartTime") or "").strip()
        if not min_s or not max_s:
            violations.append((vid, "missing min/max start"))
            continue
        if min_s == max_s:
            violations.append((vid, f"0 flex: minStartTime==maxStartTime ({min_s[:19]})"))
            continue
        min_date = min_s.split("T")[0]
        max_date = max_s.split("T")[0]
        if min_date != max_date:
            continue
    return (len(violations) == 0, violations)


def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: verify_all_visits_have_flex.py <input.json>", file=sys.stderr)
        return 1
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: not found: {path}", file=sys.stderr)
        return 1
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    model_input = data.get("modelInput") or data
    ok, violations = verify(model_input)
    if ok:
        total = len(list(model_input.get("visits") or [])) + sum(
            len(g.get("visits") or []) for g in model_input.get("visitGroups") or []
        )
        print(f"OK: All {total} visits have flex (time or day).")
        return 0
    print(f"FLEX VIOLATIONS: {len(violations)} visit(s) have 0 flex.", file=sys.stderr)
    for vid, reason in violations:
        print(f"  {vid}: {reason}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
