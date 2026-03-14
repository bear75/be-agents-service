#!/usr/bin/env python3
"""
Compare two FSR input JSONs in detail: counts, visit IDs, visitDependencies (precedingVisit),
and requiredVehicles. Use to find why one run (e.g. shower-fix 02a93fcf) has many more
unassigned visits than the baseline (cece06c0) when the only intended change is 1 extra visit group.

Usage:
  python3 compare_fsr_inputs.py path/to/cece06c0-input.json path/to/02a93fcf-input.json
  python3 compare_fsr_inputs.py path/to/cece06c0-input.json path/to/02a93fcf-input.json --report report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _all_visit_ids(mi: dict) -> set[str]:
    """All visit IDs from visits + visitGroups."""
    out: set[str] = set()
    for v in mi.get("visits") or []:
        vid = v.get("id")
        if vid:
            out.add(vid)
    for g in mi.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = v.get("id")
            if vid:
                out.add(vid)
    return out


def _all_preceding_refs(mi: dict) -> list[tuple[str, str]]:
    """(visit_id, preceding_visit_id) for every visitDependency."""
    refs: list[tuple[str, str]] = []
    for v in mi.get("visits") or []:
        vid = v.get("id", "")
        for dep in v.get("visitDependencies") or []:
            prec = dep.get("precedingVisit") or dep.get("precedingVisitId")
            if prec:
                refs.append((vid, prec))
    for g in mi.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = v.get("id", "")
            for dep in v.get("visitDependencies") or []:
                prec = dep.get("precedingVisit") or dep.get("precedingVisitId")
                if prec:
                    refs.append((vid, prec))
    return refs


def _vehicle_ids(mi: dict) -> set[str]:
    return {v.get("id", "") for v in (mi.get("vehicles") or []) if v.get("id")}


def compare(path_ref: Path, path_cand: Path) -> dict:
    """Compare two FSR input files. Returns a dict of findings."""
    with open(path_ref, encoding="utf-8") as f:
        data_ref = json.load(f)
    with open(path_cand, encoding="utf-8") as f:
        data_cand = json.load(f)

    mi_ref = data_ref.get("modelInput") or data_ref
    mi_cand = data_cand.get("modelInput") or data_cand

    visits_ref = mi_ref.get("visits") or []
    visits_cand = mi_cand.get("visits") or []
    groups_ref = mi_ref.get("visitGroups") or []
    groups_cand = mi_cand.get("visitGroups") or []
    in_groups_ref = sum(len(g.get("visits") or []) for g in groups_ref)
    in_groups_cand = sum(len(g.get("visits") or []) for g in groups_cand)
    vehicles_ref = mi_ref.get("vehicles") or []
    vehicles_cand = mi_cand.get("vehicles") or []
    shifts_ref = sum(len(v.get("shifts") or []) for v in vehicles_ref)
    shifts_cand = sum(len(v.get("shifts") or []) for v in vehicles_cand)

    ids_ref = _all_visit_ids(mi_ref)
    ids_cand = _all_visit_ids(mi_cand)
    only_ref = ids_ref - ids_cand
    only_cand = ids_cand - ids_ref
    common = ids_ref & ids_cand

    refs_ref = _all_preceding_refs(mi_ref)
    refs_cand = _all_preceding_refs(mi_cand)
    missing_in_ref = [(vid, prec) for vid, prec in refs_ref if prec not in ids_ref]
    missing_in_cand = [(vid, prec) for vid, prec in refs_cand if prec not in ids_cand]

    veh_ref = _vehicle_ids(mi_ref)
    veh_cand = _vehicle_ids(mi_cand)
    only_veh_ref = veh_ref - veh_cand
    only_veh_cand = veh_cand - veh_ref

    # requiredVehicles: sample a few visits and check refs exist in vehicles
    def _check_vehicle_refs(mi: dict, veh_ids: set[str], label: str) -> list[str]:
        bad: list[str] = []
        for v in (mi.get("visits") or []) + [
            vi for g in (mi.get("visitGroups") or []) for vi in (g.get("visits") or [])
        ]:
            vid = v.get("id", "")
            for r in (v.get("requiredVehicles") or []) + (v.get("preferredVehicles") or []):
                if r and r not in veh_ids:
                    bad.append(f"{label} visit {vid} refs vehicle {r}")
                    if len(bad) >= 20:
                        bad.append("... (more)")
                        return bad
        return bad

    bad_veh_ref = _check_vehicle_refs(mi_ref, veh_ref, "ref")
    bad_veh_cand = _check_vehicle_refs(mi_cand, veh_cand, "cand")

    return {
        "path_ref": str(path_ref),
        "path_cand": str(path_cand),
        "counts_ref": {
            "standalone_visits": len(visits_ref),
            "visit_groups": len(groups_ref),
            "visits_in_groups": in_groups_ref,
            "total_visits": len(visits_ref) + in_groups_ref,
            "vehicles": len(vehicles_ref),
            "shifts": shifts_ref,
        },
        "counts_cand": {
            "standalone_visits": len(visits_cand),
            "visit_groups": len(groups_cand),
            "visits_in_groups": in_groups_cand,
            "total_visits": len(visits_cand) + in_groups_cand,
            "vehicles": len(vehicles_cand),
            "shifts": shifts_cand,
        },
        "visit_ids_only_in_ref": sorted(only_ref),
        "visit_ids_only_in_cand": sorted(only_cand),
        "visit_ids_common": len(common),
        "preceding_refs_ref": len(refs_ref),
        "preceding_refs_cand": len(refs_cand),
        "missing_preceding_in_ref": missing_in_ref,
        "missing_preceding_in_cand": missing_in_cand,
        "vehicle_ids_only_in_ref": sorted(only_veh_ref),
        "vehicle_ids_only_in_cand": sorted(only_veh_cand),
        "bad_vehicle_refs_ref": bad_veh_ref,
        "bad_vehicle_refs_cand": bad_veh_cand,
        "planning_window_ref": mi_ref.get("planningWindow"),
        "planning_window_cand": mi_cand.get("planningWindow"),
    }


def report_text(findings: dict) -> list[str]:
    """Produce a text report from compare() output."""
    lines: list[str] = []
    r = findings["counts_ref"]
    c = findings["counts_cand"]
    lines.append("=== FSR input comparison ===")
    lines.append(f"Reference: {findings['path_ref']}")
    lines.append(f"Candidate: {findings['path_cand']}")
    lines.append("")
    lines.append("--- Counts ---")
    lines.append(
        f"  Reference: visits={r['standalone_visits']} standalone + {r['visits_in_groups']} in {r['visit_groups']} groups "
        f"=> {r['total_visits']} total | vehicles={r['vehicles']} shifts={r['shifts']}"
    )
    lines.append(
        f"  Candidate: visits={c['standalone_visits']} standalone + {c['visits_in_groups']} in {c['visit_groups']} groups "
        f"=> {c['total_visits']} total | vehicles={c['vehicles']} shifts={c['shifts']}"
    )
    lines.append("")
    lines.append("--- Visit ID diff ---")
    only_ref = findings["visit_ids_only_in_ref"]
    only_cand = findings["visit_ids_only_in_cand"]
    lines.append(f"  Only in reference: {len(only_ref)} (sample: {only_ref[:5]}{'...' if len(only_ref) > 5 else ''})")
    lines.append(f"  Only in candidate: {len(only_cand)} (sample: {only_cand[:5]}{'...' if len(only_cand) > 5 else ''})")
    lines.append(f"  Common: {findings['visit_ids_common']}")
    lines.append("")
    lines.append("--- visitDependencies (precedingVisit) ---")
    lines.append(f"  Reference: {findings['preceding_refs_ref']} deps, {len(findings['missing_preceding_in_ref'])} missing refs")
    if findings["missing_preceding_in_ref"]:
        for vid, prec in findings["missing_preceding_in_ref"][:15]:
            lines.append(f"    MISSING: visit {vid} -> precedingVisit {prec}")
        if len(findings["missing_preceding_in_ref"]) > 15:
            lines.append(f"    ... and {len(findings['missing_preceding_in_ref']) - 15} more")
    lines.append(f"  Candidate: {findings['preceding_refs_cand']} deps, {len(findings['missing_preceding_in_cand'])} missing refs")
    if findings["missing_preceding_in_cand"]:
        for vid, prec in findings["missing_preceding_in_cand"][:15]:
            lines.append(f"    MISSING: visit {vid} -> precedingVisit {prec}")
        if len(findings["missing_preceding_in_cand"]) > 15:
            lines.append(f"    ... and {len(findings['missing_preceding_in_cand']) - 15} more")
    lines.append("")
    lines.append("--- Vehicles ---")
    if findings["vehicle_ids_only_in_ref"]:
        lines.append(f"  Only in reference: {findings['vehicle_ids_only_in_ref'][:10]}{'...' if len(findings['vehicle_ids_only_in_ref']) > 10 else ''}")
    if findings["vehicle_ids_only_in_cand"]:
        lines.append(f"  Only in candidate: {findings['vehicle_ids_only_in_cand'][:10]}{'...' if len(findings['vehicle_ids_only_in_cand']) > 10 else ''}")
    if findings["bad_vehicle_refs_ref"]:
        lines.append("  Reference: visits reference non-existent vehicles:")
        for x in findings["bad_vehicle_refs_ref"][:10]:
            lines.append(f"    {x}")
    if findings["bad_vehicle_refs_cand"]:
        lines.append("  Candidate: visits reference non-existent vehicles:")
        for x in findings["bad_vehicle_refs_cand"][:10]:
            lines.append(f"    {x}")
    lines.append("")
    if findings.get("planning_window_ref") != findings.get("planning_window_cand"):
        lines.append("--- Planning window ---")
        lines.append(f"  Reference: {findings.get('planning_window_ref')}")
        lines.append(f"  Candidate: {findings.get('planning_window_cand')}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Compare two FSR input JSONs (counts, visit IDs, precedingVisit refs, vehicles)"
    )
    parser.add_argument("reference", type=Path, help="Reference input (e.g. cece06c0 input)")
    parser.add_argument("candidate", type=Path, help="Candidate input (e.g. 02a93fcf / shower-fix input)")
    parser.add_argument("--report", type=Path, default=None, help="Write report to this file")
    parser.add_argument("--json", action="store_true", help="Print findings as JSON only")
    args = parser.parse_args()

    for p in (args.reference, args.candidate):
        if not p.exists():
            print(f"Error: not found: {p}", file=sys.stderr)
            return 1

    findings = compare(args.reference, args.candidate)
    if args.json:
        # Strip long lists for JSON output
        out = {k: v for k, v in findings.items() if k not in ("visit_ids_only_in_ref", "visit_ids_only_in_cand")}
        out["visit_ids_only_in_ref_count"] = len(findings["visit_ids_only_in_ref"])
        out["visit_ids_only_in_cand_count"] = len(findings["visit_ids_only_in_cand"])
        out["visit_ids_only_in_ref_sample"] = findings["visit_ids_only_in_ref"][:20]
        out["visit_ids_only_in_cand_sample"] = findings["visit_ids_only_in_cand"][:20]
        print(json.dumps(out, indent=2))
        return 0

    lines = report_text(findings)
    text = "\n".join(lines)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(text, encoding="utf-8")
        print(f"Wrote {args.report}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
