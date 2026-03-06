#!/usr/bin/env python3
"""
Report exact mapping: time windows, visit groups, dependencies, and per-CSV-row details.

Each CSV row = one recurring pattern (logical "recurring group"). Output shows:
- Every distinct time-window pattern (minStart, maxStart, maxEnd) with visit count and examples
- Every visit group ID (VG_*) and its visit_ids
- Every visit dependency (precedingVisit -> visit_id, minDelay)
- Per row: every visit_id with time window, VG_id, and dependencies

Usage:
  python3 map_visits_time_windows.py <input_json> [csv_path] [--output report.txt]
  When input is under huddinge-4mars-csv, default --output is huddinge-4mars-csv/reports/map_visits_time_windows_report.txt
"""

import argparse
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))


def _time_only(iso_str: str) -> str:
    """Extract HH:MM from ISO datetime."""
    if not iso_str or "T" not in iso_str:
        return iso_str or ""
    return iso_str.split("T")[1][:5]  # HH:MM


def _date_only(iso_str: str) -> str:
    """Extract YYYY-MM-DD from ISO datetime."""
    if not iso_str or "T" not in iso_str:
        return iso_str or ""
    return iso_str.split("T")[0]


def main() -> int:
    ap = argparse.ArgumentParser(description="Map visits to time windows, groups, dependencies.")
    ap.add_argument("input_json", type=Path, help="FSR input JSON (with modelInput).")
    ap.add_argument("csv_path", type=Path, nargs="?", default=None, help="Optional CSV for per-row section.")
    ap.add_argument("-o", "--output", type=Path, default=None, help="Write report to file. Default: 4mars/reports/map_visits_time_windows_report.txt when input is under huddinge-4mars-csv.")
    args = ap.parse_args()
    json_path = args.input_json
    csv_path = args.csv_path
    if not json_path.exists():
        print(f"Error: JSON not found {json_path}", file=sys.stderr)
        return 1
    out_path = args.output
    if out_path is None and "huddinge-4mars-csv" in str(json_path.resolve()):
        for part in json_path.resolve().parents:
            if part.name == "huddinge-4mars-csv":
                out_path = part / "reports" / "map_visits_time_windows_report.txt"
                break
        else:
            out_path = None

    with open(json_path) as f:
        payload = json.load(f)
    mi = payload.get("modelInput") or payload

    # Collect all visits: id -> { name, date_iso, minStart, maxStart, maxEnd, duration, visit_group_id, deps }
    visit_info: dict = {}
    # Key by full ISO for per-visit; key by (time-only, time-only, time-only) for distinct patterns
    tw_signature_to_vids: dict = defaultdict(list)
    tw_time_only_to_vids: dict = defaultdict(list)  # (min_t, maxStart_t, maxEnd_t) -> [vids]

    for v in mi.get("visits") or []:
        vid = v.get("id")
        if not vid:
            continue
        tws = v.get("timeWindows") or []
        tw = tws[0] if tws else {}
        min_s = tw.get("minStartTime") or ""
        max_s = tw.get("maxStartTime") or ""
        max_e = tw.get("maxEndTime") or ""
        sig = (min_s, max_s, max_e)
        tw_signature_to_vids[sig].append(vid)
        sig_t = (_time_only(min_s), _time_only(max_s), _time_only(max_e))
        tw_time_only_to_vids[sig_t].append(vid)
        name = v.get("name") or ""
        date_iso = _date_only(min_s) or ""
        if not date_iso and " " in name:
            parts = name.split()
            for p in reversed(parts):
                if len(p) == 10 and p[4] == "-" and p[7] == "-":
                    date_iso = p
                    break
        visit_info[vid] = {
            "name": name,
            "date_iso": date_iso,
            "minStart": min_s,
            "maxStart": max_s,
            "maxEnd": max_e,
            "minStart_t": _time_only(min_s),
            "maxStart_t": _time_only(max_s),
            "maxEnd_t": _time_only(max_e),
            "duration": v.get("serviceDuration") or "",
            "visit_group_id": None,
            "dependencies": [],  # list of (precedingVisit, minDelay)
        }
        for dep in v.get("visitDependencies") or []:
            prev = dep.get("precedingVisit")
            delay = dep.get("minDelay")
            if prev:
                visit_info[vid]["dependencies"].append((prev, delay or ""))

    for g in mi.get("visitGroups") or []:
        gid = g.get("id")
        for v in g.get("visits") or []:
            vid = v.get("id")
            if not vid:
                continue
            tws = v.get("timeWindows") or []
            tw = tws[0] if tws else {}
            min_s = tw.get("minStartTime") or ""
            max_s = tw.get("maxStartTime") or ""
            max_e = tw.get("maxEndTime") or ""
            sig = (min_s, max_s, max_e)
            tw_signature_to_vids[sig].append(vid)
            sig_t = (_time_only(min_s), _time_only(max_s), _time_only(max_e))
            tw_time_only_to_vids[sig_t].append(vid)
            if vid not in visit_info:
                name = v.get("name") or ""
                date_iso = _date_only(min_s) or ""
                visit_info[vid] = {
                    "name": name,
                    "date_iso": date_iso,
                    "minStart": min_s,
                    "maxStart": max_s,
                    "maxEnd": max_e,
                    "minStart_t": _time_only(min_s),
                    "maxStart_t": _time_only(max_s),
                    "maxEnd_t": _time_only(max_e),
                    "duration": v.get("serviceDuration") or "",
                    "visit_group_id": gid,
                    "dependencies": [],
                }
            else:
                visit_info[vid]["visit_group_id"] = gid

    # Build VG_id -> [visit_ids]
    vg_to_vids: dict = defaultdict(list)
    for vid, info in visit_info.items():
        gid = info.get("visit_group_id")
        if gid:
            vg_to_vids[gid].append(vid)

    # --- Output ---
    lines = [
        "# Visit mapping: time windows, groups, dependencies",
        "",
        f"JSON: {json_path.name}",
        f"Total visits: {len(visit_info)}",
        f"Visit groups: {len(vg_to_vids)}",
        f"Unique time-window patterns (by time-of-day): {len(tw_time_only_to_vids)}",
        "",
        "--- 1. Every distinct time-window pattern (time-only: minStart, maxStart, maxEnd) ---",
        "",
    ]

    for sig_t, vids in sorted(tw_time_only_to_vids.items(), key=lambda x: (-len(x[1]), x[0][0])):
        t_min, t_max_s, t_max_e = sig_t
        lines.append(f"  [{t_min} .. {t_max_s} .. {t_max_e}]  count={len(vids)}  examples: {vids[:6]}{' ...' if len(vids) > 6 else ''}")
        lines.append("")

    lines.append("--- 2. Every visit group (VG_id -> visit_ids) ---")
    lines.append("")
    for gid in sorted(vg_to_vids.keys()):
        vids = vg_to_vids[gid]
        lines.append(f"  {gid}: {vids}")
        lines.append("")

    lines.append("--- 3. Every visit dependency (precedingVisit -> visit_id, minDelay) ---")
    lines.append("")
    deps_list = []
    for vid, info in visit_info.items():
        for prev, delay in info.get("dependencies") or []:
            deps_list.append((prev, vid, delay))
    for prev, vid, delay in sorted(deps_list):
        lines.append(f"  {prev} -> {vid}  minDelay={delay}")
    if not deps_list:
        lines.append("  (none)")
    lines.append("")

    lines.append("--- 4. Every visit: id | date | minStart | maxStart | maxEnd | duration | VG_id | dependencies ---")
    lines.append("")
    def _visit_sort_key(vid: str):
        parts = vid.split("_", 1)
        k, n = parts[0], parts[1] if len(parts) > 1 else "0"
        return (k, int(n) if n.isdigit() else 0)

    for vid in sorted(visit_info.keys(), key=_visit_sort_key):
        info = visit_info[vid]
        gid = info.get("visit_group_id") or "-"
        deps = "; ".join(f"{p}({d})" for p, d in info.get("dependencies") or [])
        if not deps:
            deps = "-"
        lines.append(f"  {vid} | {info['date_iso']} | {info['minStart_t']} | {info['maxStart_t']} | {info['maxEnd_t']} | {info['duration']} | {gid} | {deps}")
    lines.append("")

    # Per-CSV-row section (if CSV provided)
    if csv_path and csv_path.exists():
        from attendo_4mars_to_fsr import (
            PLANNING_START_DATE,
            PLANNING_END_DATE,
            _expand_row_to_occurrences,
            _assign_visit_ids_kundnr_lopnr,
        )
        from datetime import datetime
        start_date = datetime.strptime(PLANNING_START_DATE, "%Y-%m-%d")
        end_date = datetime.strptime(PLANNING_END_DATE, "%Y-%m-%d")
        with open(csv_path, "r", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f, delimiter=","))
        occurrences = []
        for i, row in enumerate(rows):
            occs = _expand_row_to_occurrences(row, i, start_date, end_date)
            for o in occs:
                o["_row"] = row
            occurrences.extend(occs)
        _assign_visit_ids_kundnr_lopnr(occurrences)
        row_to_occs = defaultdict(list)
        for o in occurrences:
            row_to_occs[o.get("row_index", -1)].append(o)

        lines.append("--- 5. Per CSV row (each row = one recurring group): visit_id | date | time window | duration | VG | deps ---")
        lines.append("")
        for ri in sorted(row_to_occs.keys()):
            occs = row_to_occs[ri]
            row = rows[ri] if 0 <= ri < len(rows) else {}
            kundnr = row.get("Kundnr", "?")
            nar = row.get("När på dagen", "?")
            dubbel = (row.get("Dubbel", "") or "").strip() or "-"
            aterk = (str(row.get("Återkommande", "")) or "")[:50]
            lines.append(f"=== Row {ri} | Kundnr={kundnr} | När={nar} | Dubbel={dubbel} | Återkommande={aterk}... ===")
            for o in occs:
                vid = o.get("visit_id")
                date_iso = o.get("date_iso", "")
                info = visit_info.get(vid) if vid else {}
                if not info:
                    lines.append(f"    {vid} (not in JSON - dropped?)")
                    continue
                gid = info.get("visit_group_id") or "-"
                deps = "; ".join(f"{p}({d})" for p, d in info.get("dependencies") or []) or "-"
                lines.append(f"    {vid} | {date_iso} | {info['minStart_t']}-{info['maxEnd_t']} | {info['duration']} | {gid} | {deps}")
            lines.append("")

    report_text = "\n".join(lines)
    if out_path:
        out_path = Path(out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(report_text, encoding="utf-8")
        print(f"Report written to {out_path}", file=sys.stderr)
    else:
        print(report_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
