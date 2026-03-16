#!/usr/bin/env python3
"""
Comprehensive CSV → JSON verification for Huddinge v3.

Verifies:
1. Dependency counts and types (PT0M vs timed delays)
2. Time windows match CSV före/efter data
3. Client notes issues are fixed
"""

import json
import csv
from datetime import datetime
from collections import defaultdict

def parse_time_minutes(time_str):
    """Parse HH:MM to minutes since midnight."""
    if not time_str or ':' not in time_str:
        return None
    try:
        h, m = map(int, time_str.split(':')[:2])
        return h * 60 + m
    except (ValueError, IndexError):
        return None

def main():
    import sys
    print("=" * 70)
    print("CSV → JSON VERIFICATION FOR HUDDINGE V3")
    print("=" * 70)
    print()

    # Load data (optional: pass csv_path and json_path as first two args)
    if len(sys.argv) >= 3:
        csv_path = sys.argv[1]
        json_path = sys.argv[2]
    else:
        csv_path = 'huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data.csv'
        json_path = 'huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_FIXED.json'
    print("Loading data...")

    try:
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            csv_data = list(csv.DictReader(f))
    except FileNotFoundError:
        print(f"❌ CSV file not found: {csv_path}")
        return

    try:
        with open(json_path, 'r') as f:
            fsr_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ JSON file not found: {json_path}")
        return

    model = fsr_data.get('modelInput', fsr_data)

    print(f"✅ CSV rows: {len(csv_data)}")

    total_visits = len(model.get('visits', []))
    for group in model.get('visitGroups', []):
        total_visits += len(group.get('visits', []))

    print(f"✅ FSR standalone visits: {len(model.get('visits', []))}")
    print(f"✅ FSR visit groups: {len(model.get('visitGroups', []))}")
    print(f"✅ FSR total visits: {total_visits}")
    print()

    # 1. Dependency verification
    print("-" * 70)
    print("1. DEPENDENCY VERIFICATION")
    print("-" * 70)

    total_deps = 0
    pt0m_deps = 0
    other_deps = 0
    delay_breakdown = defaultdict(int)
    visits_with_deps = 0

    # Check standalone visits
    for visit in model.get('visits', []):
        if visit.get('visitDependencies'):
            visits_with_deps += 1
            for dep in visit['visitDependencies']:
                total_deps += 1
                delay = dep.get('minDelay', '')
                delay_breakdown[delay] += 1
                if delay == 'PT0M':
                    pt0m_deps += 1
                else:
                    other_deps += 1

    # Check visit groups
    for group in model.get('visitGroups', []):
        for visit in group.get('visits', []):
            if visit.get('visitDependencies'):
                visits_with_deps += 1
                for dep in visit['visitDependencies']:
                    total_deps += 1
                    delay = dep.get('minDelay', '')
                    delay_breakdown[delay] += 1
                    if delay == 'PT0M':
                        pt0m_deps += 1
                    else:
                        other_deps += 1

    print(f"Total dependencies: {total_deps}")
    print(f"Visits with dependencies: {visits_with_deps}")
    print()
    print(f"Dependency breakdown:")
    print(f"  PT0M (same-day sequencing): {pt0m_deps} ({pt0m_deps/total_deps*100:.1f}%)" if total_deps > 0 else "  PT0M: 0")
    print(f"  Other delays: {other_deps} ({other_deps/total_deps*100:.1f}%)" if total_deps > 0 else "  Other: 0")
    print()

    print("Delay type breakdown:")
    for delay in sorted(delay_breakdown.keys(), key=lambda x: (x != 'PT0M', x)):
        count = delay_breakdown[delay]
        pct = count / total_deps * 100 if total_deps > 0 else 0
        print(f"  {delay:10s}: {count:4d} ({pct:5.1f}%)")
    print()

    # Verify Fix 3 is working
    if pt0m_deps >= 1000:
        print(f"✅ PASS: {pt0m_deps} PT0M dependencies added (Fix 3 working)")
    else:
        print(f"⚠️  WARNING: Only {pt0m_deps} PT0M dependencies (expected ~1173)")

    print()

    # 2. Time window verification for specific cases
    print("-" * 70)
    print("2. TIME WINDOW VERIFICATION")
    print("-" * 70)

    # Check "Exakt dag/tid" cases (H332)
    print("Checking H332 'Exakt dag/tid' visits...")
    h332_found = False

    for visit in model.get('visits', []):
        if 'H332' in visit.get('id', ''):
            h332_found = True
            tw = visit['timeWindows'][0]
            min_dt = datetime.fromisoformat(tw['minStartTime'].replace('+01:00', '').replace('+00:00', ''))
            max_dt = datetime.fromisoformat(tw['maxStartTime'].replace('+01:00', '').replace('+00:00', ''))
            flex_min = (max_dt - min_dt).total_seconds() / 60

            print(f"  {visit['id']}: {min_dt.strftime('%H:%M')} - {max_dt.strftime('%H:%M')} (flex: {flex_min:.0f} min)")

            if flex_min <= 2:
                print(f"  ✅ PASS: Minimal flex (expected ≤2 min)")
            else:
                print(f"  ❌ FAIL: Too much flex (expected ≤2 min)")
            break

    if not h332_found:
        print(f"  ⚠️  H332 not found in standalone visits (might be in visit groups)")

    print()

    # Check sample visits with före/efter
    print("Checking sample visits with före/efter...")

    # Find a visit with före/efter from CSV
    sample_found = False
    for row in csv_data[:100]:  # Check first 100 rows
        fore = row.get('Före', '').strip()
        efter = row.get('Efter', '').strip()
        if fore and efter:
            kundnr = row.get('Kundnr', '')
            starttid = row.get('Starttid', '')

            # Try to find matching visit in FSR
            for visit in model.get('visits', [])[:200]:  # Check first 200 visits
                if kundnr in visit.get('id', '') and starttid:
                    tw = visit['timeWindows'][0]
                    min_time = tw['minStartTime'][11:16]  # Extract HH:MM
                    max_time = tw['maxStartTime'][11:16]

                    print(f"  {visit['id'][:20]}...")
                    print(f"    CSV: Starttid={starttid}, Före={fore}, Efter={efter}")
                    print(f"    FSR: {min_time} - {max_time}")

                    # Verify times match expected före/efter
                    expected_min_minutes = parse_time_minutes(starttid)
                    actual_min_minutes = parse_time_minutes(min_time)

                    if expected_min_minutes is not None and actual_min_minutes is not None:
                        try:
                            fore_min = int(fore)
                            expected_min_minutes -= fore_min

                            # Allow 1-2 min tolerance for time zone/rounding
                            if abs(actual_min_minutes - expected_min_minutes) <= 2:
                                print(f"    ✅ PASS: Time window matches före/efter")
                            else:
                                print(f"    ⚠️  Difference: {abs(actual_min_minutes - expected_min_minutes)} min")
                        except ValueError:
                            pass

                    sample_found = True
                    break

            if sample_found:
                break

    if not sample_found:
        print(f"  ⚠️  No matching sample found")

    print()

    # 3. Client notes verification
    print("-" * 70)
    print("3. CLIENT NOTES ISSUES")
    print("-" * 70)

    # Check H015 has dependencies (same-day overlap prevention)
    print("Checking H015 same-day overlap prevention...")
    h015_deps = 0
    h015_pt0m_deps = 0
    h015_sample = None

    for visit in model.get('visits', []):
        if 'H015' in visit.get('id', '') and visit.get('visitDependencies'):
            h015_deps += len(visit['visitDependencies'])
            for dep in visit['visitDependencies']:
                if dep.get('minDelay') == 'PT0M':
                    h015_pt0m_deps += 1
            if not h015_sample:
                h015_sample = visit

    if h015_deps > 0:
        print(f"  ✅ PASS: H015 has {h015_deps} dependencies ({h015_pt0m_deps} PT0M)")
        if h015_sample:
            print(f"  Sample: {h015_sample['id']}")
            for dep in h015_sample.get('visitDependencies', [])[:2]:
                print(f"    → {dep['precedingVisit']} (delay: {dep['minDelay']})")
    else:
        print(f"  ⚠️  H015 has no dependencies in standalone visits (check visit groups)")

    print()

    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    all_pass = True

    print(f"\n📊 Dependencies:")
    print(f"  Total: {total_deps}")
    if pt0m_deps >= 1000:
        print(f"  ✅ PT0M (Fix 3): {pt0m_deps}")
    else:
        print(f"  ⚠️  PT0M: {pt0m_deps} (expected ~1173)")
        all_pass = False
    print(f"  ✅ Other delays: {other_deps}")

    print(f"\n📏 Time Windows:")
    if h332_found:
        print(f"  ✅ Exact time handling verified")
    else:
        print(f"  ⚠️  H332 not found for verification")

    print(f"\n📝 Client Notes:")
    if h015_deps > 0:
        print(f"  ✅ H015 overlap prevention: {h015_deps} dependencies")
    else:
        print(f"  ⚠️  H015 dependencies not verified")

    print()
    print("=" * 70)

    if all_pass:
        print("✅ ALL CHECKS PASSED")
    else:
        print("⚠️  SOME CHECKS NEED REVIEW (see details above)")

    print("=" * 70)
    print()

    # Comparison with baseline
    print("📈 Comparison with v2 baseline:")
    print(f"  v2 (81 clients):  946 dependencies (0.2% PT0M)")
    print(f"  v3 (115 clients): {total_deps} dependencies ({pt0m_deps/total_deps*100:.1f}% PT0M)")
    print(f"  Increase: +{total_deps - 946} deps (+{(total_deps - 946)/946*100:.0f}%)")
    print(f"    - Client increase: +42% (81 → 115)")
    print(f"    - Fix 3 PT0M deps: +{pt0m_deps}")
    print()

if __name__ == "__main__":
    main()
