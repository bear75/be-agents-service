#!/usr/bin/env python3
"""
Compare time windows between old and new (fixed) input JSON files.

Shows specific examples of how the fixes change the time window calculations.
"""

import json
import sys
from pathlib import Path
from datetime import datetime


def parse_iso_time(iso_str):
    """Parse ISO datetime to HH:MM string."""
    try:
        dt = datetime.fromisoformat(iso_str.replace('+01:00', ''))
        return dt.strftime('%H:%M')
    except:
        return iso_str


def get_flex_minutes(time_window):
    """Calculate flex in minutes from time window."""
    try:
        min_start = datetime.fromisoformat(time_window['minStartTime'].replace('+01:00', ''))
        max_start = datetime.fromisoformat(time_window['maxStartTime'].replace('+01:00', ''))
        return int((max_start - min_start).total_seconds() / 60)
    except:
        return 0


def analyze_visit(visit, label):
    """Analyze and print visit time window details."""
    print(f"\n{label}:")
    print(f"  ID: {visit['id']}")
    print(f"  Name: {visit['name']}")

    if 'timeWindows' in visit and visit['timeWindows']:
        tw = visit['timeWindows'][0]  # First window
        min_time = parse_iso_time(tw['minStartTime'])
        max_time = parse_iso_time(tw['maxStartTime'])
        flex = get_flex_minutes(tw)

        print(f"  Time Window: {min_time} - {max_time}")
        print(f"  Flex: {flex} minutes")

        if flex == 0:
            print(f"  → EXACT TIME (zero flex)")
        elif flex <= 30:
            print(f"  → Small flex (±15 min)")
        elif flex >= 120:
            print(f"  → Full slot flex")


def compare_inputs(old_path, new_path):
    """Compare old and new input JSON files."""
    print("=" * 80)
    print("TIME WINDOW COMPARISON: Old vs New (Fixed)")
    print("=" * 80)

    # Load both files
    with open(old_path) as f:
        old_data = json.load(f)
    with open(new_path) as f:
        new_data = json.load(f)

    old_visits = {v['id']: v for v in old_data['modelInput'].get('visits', [])}
    new_visits = {v['id']: v for v in new_data['modelInput'].get('visits', [])}

    # Find interesting examples
    examples = []

    # Look for visits with "Exakt" in name
    for vid, new_v in new_visits.items():
        if 'exakt' in new_v['name'].lower() and vid in old_visits:
            examples.append(('Exakt dag/tid Example', vid))
            break

    # Look for visits that changed significantly
    for vid, new_v in new_visits.items():
        if vid not in old_visits:
            continue
        old_v = old_visits[vid]

        if 'timeWindows' in old_v and 'timeWindows' in new_v:
            old_flex = get_flex_minutes(old_v['timeWindows'][0])
            new_flex = get_flex_minutes(new_v['timeWindows'][0])

            # Big reduction in flex (e.g., 180 → 30)
            if old_flex > 60 and new_flex <= 30 and len(examples) < 5:
                examples.append(('Reduced Flex Example', vid))

    # Show examples
    for label, vid in examples[:3]:
        print(f"\n{'=' * 80}")
        print(f"{label}: {vid}")
        print('=' * 80)

        if vid in old_visits:
            analyze_visit(old_visits[vid], "OLD (Before Fix)")
        if vid in new_visits:
            analyze_visit(new_visits[vid], "NEW (After Fix)")

    # Summary statistics
    print(f"\n{'=' * 80}")
    print("SUMMARY STATISTICS")
    print('=' * 80)

    old_flex_dist = {'exact': 0, 'small': 0, 'medium': 0, 'large': 0}
    new_flex_dist = {'exact': 0, 'small': 0, 'medium': 0, 'large': 0}

    for vid in old_visits:
        if 'timeWindows' in old_visits[vid] and old_visits[vid]['timeWindows']:
            flex = get_flex_minutes(old_visits[vid]['timeWindows'][0])
            if flex == 0:
                old_flex_dist['exact'] += 1
            elif flex <= 30:
                old_flex_dist['small'] += 1
            elif flex <= 120:
                old_flex_dist['medium'] += 1
            else:
                old_flex_dist['large'] += 1

    for vid in new_visits:
        if 'timeWindows' in new_visits[vid] and new_visits[vid]['timeWindows']:
            flex = get_flex_minutes(new_visits[vid]['timeWindows'][0])
            if flex == 0:
                new_flex_dist['exact'] += 1
            elif flex <= 30:
                new_flex_dist['small'] += 1
            elif flex <= 120:
                new_flex_dist['medium'] += 1
            else:
                new_flex_dist['large'] += 1

    print("\nFlex Distribution (OLD):")
    print(f"  Exact (0 min):       {old_flex_dist['exact']:4d} visits")
    print(f"  Small (1-30 min):    {old_flex_dist['small']:4d} visits")
    print(f"  Medium (31-120 min): {old_flex_dist['medium']:4d} visits")
    print(f"  Large (>120 min):    {old_flex_dist['large']:4d} visits")

    print("\nFlex Distribution (NEW):")
    print(f"  Exact (0 min):       {new_flex_dist['exact']:4d} visits (+{new_flex_dist['exact'] - old_flex_dist['exact']})")
    print(f"  Small (1-30 min):    {new_flex_dist['small']:4d} visits (+{new_flex_dist['small'] - old_flex_dist['small']})")
    print(f"  Medium (31-120 min): {new_flex_dist['medium']:4d} visits ({new_flex_dist['medium'] - old_flex_dist['medium']:+d})")
    print(f"  Large (>120 min):    {new_flex_dist['large']:4d} visits ({new_flex_dist['large'] - old_flex_dist['large']:+d})")

    print("\nINTERPRETATION:")
    if new_flex_dist['exact'] > old_flex_dist['exact']:
        print(f"  ✓ More exact-time visits (critical visits now locked to exact times)")
    if new_flex_dist['small'] > old_flex_dist['small']:
        print(f"  ✓ More small-flex visits (specific times get ±15min instead of full slot)")
    if new_flex_dist['large'] < old_flex_dist['large']:
        print(f"  ✓ Fewer large-flex visits (better time precision overall)")

    print()


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python compare_time_windows.py <old_input.json> <new_input.json>")
        print()
        print("Example:")
        print("  python compare_time_windows.py \\")
        print("    ../full-csv/10-mars-new-attendo/v3/input_v3.json \\")
        print("    ../full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json")
        sys.exit(1)

    old_path = Path(sys.argv[1])
    new_path = Path(sys.argv[2])

    if not old_path.exists():
        print(f"Error: Old input file not found: {old_path}")
        sys.exit(1)
    if not new_path.exists():
        print(f"Error: New input file not found: {new_path}")
        sys.exit(1)

    compare_inputs(old_path, new_path)
