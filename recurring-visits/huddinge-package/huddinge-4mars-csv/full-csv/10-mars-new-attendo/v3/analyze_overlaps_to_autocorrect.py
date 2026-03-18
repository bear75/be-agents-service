#!/usr/bin/env python3
"""
Analyze Huddinge-v3 Data_final.csv for expected overlaps to auto-correct with PT0M.

Rules (per user clarification):
- Only overlaps that are NOT visit groups (Dubbel column empty)
- Overlaps that DON'T have dependencies → auto-add PT0M between them

Uses same logic as attendo_4mars_to_fsr.py for expansion and time windows.
"""
import csv
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path

# Add scripts dir to path for attendo_4mars_to_fsr import
SCRIPT_DIR = Path(__file__).resolve().parent
# v3 -> 10-mars-new-attendo -> full-csv -> huddinge-4mars-csv
HUDDINGE_DIR = SCRIPT_DIR.parent.parent.parent
sys.path.insert(0, str(HUDDINGE_DIR / "scripts"))

from attendo_4mars_to_fsr import (
    _expand_row_to_occurrences,
    _compute_slot_bounds,
    _parse_time_minutes,
)

CSV_PATH = SCRIPT_DIR / "Huddinge-v3 - Data_final.csv"
SCHEDULE_START = datetime(2026, 3, 2)
SCHEDULE_DAYS = 14


def main():
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    # Expand to occurrences (same as attendo_4mars_to_fsr)
    occurrences = []
    occ_counter = 0
    for row_idx, row in enumerate(rows):
        if not row.get("Återkommande"):
            continue
        occs = _expand_row_to_occurrences(
            row,
            row_idx,
            SCHEDULE_START,
            SCHEDULE_START + timedelta(days=SCHEDULE_DAYS - 1),
        )
        for occ in occs:
            occ["row_index"] = row_idx
            occ["dubbel"] = str(row.get("Dubbel", "") or "").strip()
            occ["antal_tim_mellan"] = str(row.get("Antal tim mellan besöken", "") or "").strip()
            occ_counter += 1
            occ["visit_id"] = f"occ_{occ_counter}"
        occurrences.extend(occs)

    # Build visit groups (same key as attendo: kundnr_dateStr_dubbel)
    groups_by_key = defaultdict(list)
    for occ in occurrences:
        d = occ.get("dubbel")
        if not d:
            continue
        k = occ.get("kundnr", "")
        gk = f"{k}_{occ['date_iso']}_{d}"
        groups_by_key[gk].append(occ["visit_id"])

    visit_id_to_group = {}
    for gk, vids in groups_by_key.items():
        if len(vids) >= 2:
            for vid in vids:
                visit_id_to_group[vid] = gk

    # Spread deps chain visits from same ROW across different DATES. Same-date pairs are from
    # different rows, so we don't exclude them here.

    # Group by (client, date)
    per_client_date = defaultdict(list)
    for occ in occurrences:
        k = occ.get("kundnr", "")
        if not k:
            continue
        key = (k, occ["date_iso"])
        per_client_date[key].append(occ)

    # Find overlaps to auto-correct
    overlaps_to_add = []
    for (kundnr, date_iso), occs in per_client_date.items():
        for i, occ_a in enumerate(occs):
            for occ_b in occs[i + 1 :]:
                # Skip if both in same visit group (dubbel)
                g_a = visit_id_to_group.get(occ_a["visit_id"])
                g_b = visit_id_to_group.get(occ_b["visit_id"])
                if g_a and g_b and g_a == g_b:
                    continue

                # Check time window overlap
                min_a, max_a, _ = _compute_slot_bounds(occ_a)
                min_b, max_b, _ = _compute_slot_bounds(occ_b)
                längd_a = occ_a.get("längd", 0)
                längd_b = occ_b.get("längd", 0)
                max_end_a = max_a + längd_a
                max_end_b = max_b + längd_b
                if not (min_a < max_end_b and min_b < max_end_a):
                    continue

                # Skip if same start time (ordering ambiguous)
                start_a = _parse_time_minutes(occ_a.get("starttid", "08:00"))
                start_b = _parse_time_minutes(occ_b.get("starttid", "08:00"))
                if start_a == start_b:
                    continue

                # This pair needs PT0M (no existing spread dep; same-date pairs are from different rows)
                prev = occ_a if start_a < start_b else occ_b
                succ = occ_b if start_a < start_b else occ_a
                overlaps_to_add.append(
                    (prev["visit_id"], succ["visit_id"], kundnr, date_iso, prev.get("insatser", ""), succ.get("insatser", ""))
                )

    print("=" * 80)
    print("Expected overlaps to auto-correct (PT0M) from Huddinge-v3 - Data_final.csv")
    print("Planning window: 2026-03-02 to 2026-03-15 (14 days)")
    print("=" * 80)
    print()
    print("Rules applied:")
    print("  - Excluded: visit groups (Dubbel) - intentional overlaps")
    print("  - Included: same client, same date, overlapping time windows (no dep)")
    print()
    print(f"Total PT0M dependencies to add: {len(overlaps_to_add)}")
    print()
    if overlaps_to_add:
        print("Sample (first 20):")
        for prev_id, succ_id, kundnr, date_iso, ins_a, ins_b in overlaps_to_add[:20]:
            print(f"  {prev_id} -> {succ_id}  ({kundnr} {date_iso})")
            print(f"    {ins_a[:50]}... | {ins_b[:50]}...")
        if len(overlaps_to_add) > 20:
            print(f"  ... and {len(overlaps_to_add) - 20} more")
    print()
    print("By client:")
    by_client = defaultdict(int)
    for _, _, k, _, _, _ in overlaps_to_add:
        by_client[k] += 1
    for k in sorted(by_client.keys()):
        print(f"  {k}: {by_client[k]} PT0M deps")


if __name__ == "__main__":
    main()
