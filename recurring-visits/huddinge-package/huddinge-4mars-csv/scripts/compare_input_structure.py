#!/usr/bin/env python3
"""
Compare two FSR input JSONs structurally (ignoring visit id and name).
Reports same/diff counts and any structural differences.
Use to verify "same input except names" after rewriting visit ids.
"""

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple


def _visit_signature(v: Dict[str, Any]) -> Dict[str, Any]:
    """Copy of visit excluding id and name for comparison."""
    out = {}
    for k, val in v.items():
        if k in ("id", "name"):
            continue
        if k in ("dependencies", "visitDependencies") and isinstance(val, list):
            # Compare dependency structure (minDelay, etc.) but not visit refs
            out[k] = [
                {kk: vv for kk, vv in d.items() if kk not in ("visitId", "precedingVisit", "id")}
                for d in val
                if isinstance(d, dict)
            ]
            continue
        out[k] = val
    return out


def _all_visits(model: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = list(model.get("visits") or [])
    for g in model.get("visitGroups") or []:
        out.extend(g.get("visits") or [])
    return out


def compare(
    path_a: Path, path_b: Path
) -> Tuple[bool, List[str], Dict[str, int], Dict[str, int]]:
    """
    Compare two FSR input files. Returns (ok, messages, counts_a, counts_b).
    ok is False if structure differs (excluding id/name).
    """
    with open(path_a, "r", encoding="utf-8") as f:
        data_a = json.load(f)
    with open(path_b, "r", encoding="utf-8") as f:
        data_b = json.load(f)

    mi_a = data_a.get("modelInput") or data_a
    mi_b = data_b.get("modelInput") or data_b

    messages: List[str] = []
    counts_a: Dict[str, int] = {}
    counts_b: Dict[str, int] = {}

    # Counts
    visits_a = mi_a.get("visits") or []
    visits_b = mi_b.get("visits") or []
    groups_a = mi_a.get("visitGroups") or []
    groups_b = mi_b.get("visitGroups") or []
    in_groups_a = sum(len(g.get("visits") or []) for g in groups_a)
    in_groups_b = sum(len(g.get("visits") or []) for g in groups_b)
    vehicles_a = len(mi_a.get("vehicles") or [])
    vehicles_b = len(mi_b.get("vehicles") or [])
    shifts_a = sum(len(v.get("shifts") or []) for v in (mi_a.get("vehicles") or []))
    shifts_b = sum(len(v.get("shifts") or []) for v in (mi_b.get("vehicles") or []))

    counts_a = {
        "standalone": len(visits_a),
        "groups": len(groups_a),
        "in_groups": in_groups_a,
        "vehicles": vehicles_a,
        "shifts": shifts_a,
    }
    counts_b = {
        "standalone": len(visits_b),
        "groups": len(groups_b),
        "in_groups": in_groups_b,
        "vehicles": vehicles_b,
        "shifts": shifts_b,
    }

    # Planning window
    pw_a = mi_a.get("planningWindow") or {}
    pw_b = mi_b.get("planningWindow") or {}
    if pw_a.get("startDate") != pw_b.get("startDate") or pw_a.get("endDate") != pw_b.get("endDate"):
        messages.append(
            f"Planning window differs: A {pw_a.get('startDate')}–{pw_a.get('endDate')} vs B {pw_b.get('startDate')}–{pw_b.get('endDate')}"
        )

    # Structural equality (counts)
    if counts_a["standalone"] != counts_b["standalone"]:
        messages.append(f"Standalone visits: A={counts_a['standalone']} B={counts_b['standalone']}")
    if counts_a["groups"] != counts_b["groups"]:
        messages.append(f"Visit groups: A={counts_a['groups']} B={counts_b['groups']}")
    if counts_a["in_groups"] != counts_b["in_groups"]:
        messages.append(f"Visits in groups: A={counts_a['in_groups']} B={counts_b['in_groups']}")
    if counts_a["vehicles"] != counts_b["vehicles"]:
        messages.append(f"Vehicles: A={counts_a['vehicles']} B={counts_b['vehicles']}")
    if counts_a["shifts"] != counts_b["shifts"]:
        messages.append(f"Shifts: A={counts_a['shifts']} B={counts_b['shifts']}")

    # Visit signatures (by index): same order => same structure
    all_a = _all_visits(mi_a)
    all_b = _all_visits(mi_b)
    if len(all_a) != len(all_b):
        messages.append(f"Total visits: A={len(all_a)} B={len(all_b)}")
    else:
        for i, (va, vb) in enumerate(zip(all_a, all_b)):
            sig_a = _visit_signature(va)
            sig_b = _visit_signature(vb)
            if sig_a != sig_b:
                messages.append(f"Visit index {i} structure differs (id A={va.get('id')} B={vb.get('id')})")
                if len(messages) > 20:
                    messages.append("... (further diffs omitted)")
                    break

    ok = len(messages) == 0
    return (ok, messages, counts_a, counts_b)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare two FSR input JSONs (structure, exclude id/name)")
    parser.add_argument("reference", type=Path, help="Reference input (e.g. solve_2v_output/input.json)")
    parser.add_argument("candidate", type=Path, help="Candidate input (e.g. input_4mars_2w_newids.json)")
    args = parser.parse_args()

    for p in (args.reference, args.candidate):
        if not p.exists():
            print(f"Error: not found: {p}", file=__import__("sys").stderr)
            return 1

    ok, messages, ca, cb = compare(args.reference, args.candidate)

    print("Counts:")
    print(f"  Reference: standalone={ca['standalone']} groups={ca['groups']} in_groups={ca['in_groups']} vehicles={ca['vehicles']} shifts={ca['shifts']}")
    print(f"  Candidate: standalone={cb['standalone']} groups={cb['groups']} in_groups={cb['in_groups']} vehicles={cb['vehicles']} shifts={cb['shifts']}")
    print()
    if ok:
        print("Structure: IDENTICAL (only id/name differ).")
        return 0
    print("Structure: DIFFERS")
    for m in messages:
        print(f"  - {m}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
