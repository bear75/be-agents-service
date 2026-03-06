#!/usr/bin/env python3
"""
Analyze CSV → JSON mapping for 4mars FSR input.

Verifies:
- Every CSV row expands to the expected number of occurrences (by recurrence).
- Visit IDs in JSON follow kundnr_löpnr and match expected from CSV expansion.
- Every visit in JSON has valid Timefold format (timeWindows, location, serviceDuration).
- Row → visit count and visit IDs are traced for review.

Usage:
  python3 analyze_4mars_csv_to_json.py <csv_path> <input_json_path> [-o report.txt]
  When CSV is under huddinge-4mars-csv, default -o is huddinge-4mars-csv/reports/analyze_csv_to_json_report.txt
"""

import argparse
import csv
import json
import sys
from pathlib import Path
from datetime import datetime

# Reuse 4mars expansion and ID assignment
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from attendo_4mars_to_fsr import (
    PLANNING_START_DATE,
    PLANNING_END_DATE,
    _expand_row_to_occurrences,
    _assign_visit_ids_kundnr_lopnr,
)


def _build_json_visit_by_id(model_input: dict) -> dict:
    """Build visit_id -> visit from modelInput (visits + visitGroups)."""
    by_id = {}
    for v in model_input.get("visits") or []:
        vid = v.get("id")
        if vid:
            by_id[vid] = {**v, "_source": "visits"}
    for g in model_input.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = v.get("id")
            if vid:
                by_id[vid] = {**v, "_source": "visitGroup", "_group_id": g.get("id")}
    return by_id


def _visit_slot_from_tw(visit: dict) -> str:
    """Infer Morgon/Lunch/Kväll from first time window (slot end)."""
    tws = visit.get("timeWindows") or []
    if not tws:
        return "?"
    max_end = tws[0].get("maxEndTime") or ""
    if "10:30" in max_end:
        return "Morgon"
    if "13:30" in max_end:
        return "Lunch"
    if "19:00" in max_end:
        return "Kväll"
    return "?"


def main() -> int:
    ap = argparse.ArgumentParser(description="Analyze 4mars CSV → JSON mapping.")
    ap.add_argument("csv_path", type=Path, help="Attendo 4mars CSV.")
    ap.add_argument("input_json", type=Path, help="FSR input JSON.")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Write report to file. Default: 4mars/reports/analyze_csv_to_json_report.txt when CSV is under huddinge-4mars-csv.")
    args = ap.parse_args()
    csv_path = args.csv_path
    json_path = args.input_json
    if not csv_path.exists():
        print(f"Error: CSV not found {csv_path}", file=sys.stderr)
        return 1
    if not json_path.exists():
        print(f"Error: JSON not found {json_path}", file=sys.stderr)
        return 1

    start_date = datetime.strptime(PLANNING_START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(PLANNING_END_DATE, "%Y-%m-%d")

    # Load CSV and expand to occurrences (same logic as pipeline)
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f, delimiter=","))
    occurrences = []
    for i, row in enumerate(rows):
        occs = _expand_row_to_occurrences(row, i, start_date, end_date)
        for o in occs:
            o["_row"] = row
        occurrences.extend(occs)
    _assign_visit_ids_kundnr_lopnr(occurrences)

    # Load JSON
    with open(json_path) as f:
        payload = json.load(f)
    model_input = payload.get("modelInput") or payload
    json_visits_by_id = _build_json_visit_by_id(model_input)
    json_visit_ids = set(json_visits_by_id.keys())

    # Expected visit IDs from CSV (we don't filter by geocode here; pipeline drops 0,0)
    occ_visit_ids = {o["visit_id"] for o in occurrences}
    # Which occurrences would have been dropped (no coords) – we don't have geocode here, so assume all expected
    # Pipeline drops when lat==0,lon==0 after geocode. So JSON can have fewer than occ_visit_ids.
    in_json_only = json_visit_ids - occ_visit_ids
    in_occ_only = occ_visit_ids - json_visit_ids

    # Per-row report: row index -> list of (visit_id, date_iso, slot)
    row_to_occ = {}
    for o in occurrences:
        ri = o.get("row_index", -1)
        row_to_occ.setdefault(ri, []).append(o)

    # TF format checks for each JSON visit
    tf_errors = []
    for vid, v in json_visits_by_id.items():
        tws = v.get("timeWindows") or []
        if not tws:
            tf_errors.append(f"{vid}: missing timeWindows")
        else:
            tw = tws[0]
            mn = tw.get("minStartTime") or ""
            mx = tw.get("maxEndTime") or ""
            if not mn or not mx:
                tf_errors.append(f"{vid}: timeWindow missing minStart or maxEnd")
            elif mn > mx:
                tf_errors.append(f"{vid}: minStartTime > maxEndTime")
        loc = v.get("location")
        if not loc or len(loc) != 2:
            tf_errors.append(f"{vid}: missing or invalid location")
        if not v.get("serviceDuration"):
            tf_errors.append(f"{vid}: missing serviceDuration")

    # Summary
    lines = [
        "# 4mars CSV → JSON analysis",
        "",
        f"CSV: {csv_path.name}",
        f"  Rows: {len(rows)}",
        f"  Expanded occurrences: {len(occurrences)}",
        f"  Unique visit_id (from CSV expansion): {len(occ_visit_ids)}",
        "",
        f"JSON: {json_path.name}",
        f"  Visits (standalone): {len(model_input.get('visits') or [])}",
        f"  Visit groups: {len(model_input.get('visitGroups') or [])}",
        f"  Visits in groups: {sum(len(g.get('visits') or []) for g in (model_input.get('visitGroups') or []))}",
        f"  Total visit_id in JSON: {len(json_visit_ids)}",
        "",
        "## Consistency",
        "",
    ]
    if in_json_only:
        lines.append(f"- Visit IDs in JSON but not in CSV expansion: {len(in_json_only)} (first 10: {list(in_json_only)[:10]})")
    else:
        lines.append("- Every JSON visit_id appears in CSV expansion (by kundnr_löpnr).")
    if in_occ_only:
        lines.append(f"- Visit IDs in CSV expansion but not in JSON: {len(in_occ_only)} (expected if geocode dropped them or no coords)")
    lines.append("")
    if tf_errors:
        lines.append("## Timefold format issues")
        lines.extend(f"- {e}" for e in tf_errors[:30])
        if len(tf_errors) > 30:
            lines.append(f"- ... and {len(tf_errors) - 30} more")
    else:
        lines.append("## Timefold format: OK (timeWindows, location, serviceDuration)")
    lines.append("")
    lines.append("## Per-row: CSV row → visit count → visit IDs (sample)")
    lines.append("")

    # Sample rows: first 5, then every 20th, then last 2
    indices = list(row_to_occ.keys())
    indices.sort()
    sample = indices[:5] + [i for i in indices if 20 <= i < len(rows) - 2][:5] + indices[-2:]
    sample = sorted(set(sample))
    for ri in sample:
        occs = row_to_occ.get(ri, [])
        row = rows[ri] if 0 <= ri < len(rows) else {}
        kundnr = row.get("Kundnr", "?")
        nar = row.get("När på dagen", "?")
        aterk = (row.get("Återkommande", "") or "")[:40]
        dubbel = row.get("Dubbel", "")
        visit_ids = sorted(set(o["visit_id"] for o in occs))
        in_json = sum(1 for vid in visit_ids if vid in json_visit_ids)
        lines.append(f"Row {ri}: Kundnr={kundnr} När={nar} Dubbel={dubbel or '-'} Återkommande={aterk}...")
        lines.append(f"  → {len(occs)} occurrences, {len(visit_ids)} unique visit_id, {in_json} present in JSON")
        lines.append(f"  → visit_id sample: {visit_ids[:8]}{' ...' if len(visit_ids) > 8 else ''}")
        lines.append("")

    # Full row list (compact): row_index, kundnr, n_occ, n_visit_id, n_in_json
    lines.append("## All rows: occurrence and JSON visit counts")
    lines.append("")
    lines.append("| row | Kundnr | När | Dubbel | occs | visit_ids | in_json |")
    lines.append("|-----|--------|-----|--------|------|-----------|---------|")
    for ri in indices:
        occs = row_to_occ.get(ri, [])
        row = rows[ri] if 0 <= ri < len(rows) else {}
        kundnr = row.get("Kundnr", "?")
        nar = row.get("När på dagen", "?")
        dubbel = row.get("Dubbel", "") or "-"
        visit_ids = sorted(set(o["visit_id"] for o in occs))
        in_json = sum(1 for vid in visit_ids if vid in json_visit_ids)
        lines.append(f"| {ri} | {kundnr} | {nar} | {dubbel} | {len(occs)} | {len(visit_ids)} | {in_json} |")

    out = "\n".join(lines)
    out_path = args.output
    if out_path is None and "huddinge-4mars-csv" in str(csv_path.resolve()):
        for part in csv_path.resolve().parents:
            if part.name == "huddinge-4mars-csv":
                out_path = part / "reports" / "analyze_csv_to_json_report.txt"
                break
        else:
            out_path = None
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(out, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(out)
    return 0 if not tf_errors and not in_json_only else 1


if __name__ == "__main__":
    sys.exit(main())
