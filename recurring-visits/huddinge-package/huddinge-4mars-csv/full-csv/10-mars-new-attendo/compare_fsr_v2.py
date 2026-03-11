#!/usr/bin/env python3
"""Compare dashboard FSR vs script FSR - detailed visit-by-visit analysis."""
import json
from datetime import datetime, timedelta
from collections import defaultdict

SCRIPT = "script_fsr.json"
DASH = "dashboard_fsr_new.json"

def load(path):
    with open(path) as f:
        data = json.load(f)
    return data.get("modelInput", data)

def parse_dt(s):
    if not s: return None
    for fmt in ["%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%S.%f%z", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f"]:
        try:
            return datetime.strptime(s, fmt)
        except:
            pass
    return None

def to_cet(dt):
    """Normalize to CET (UTC+1)."""
    if dt is None: return None
    if dt.tzinfo:
        utc_offset = dt.utcoffset()
        if utc_offset is not None and utc_offset.total_seconds() == 0:
            dt = dt + timedelta(hours=1)
    return dt.replace(tzinfo=None)

def fmt_time(dt):
    if dt is None: return "?"
    return dt.strftime("%H:%M")

def parse_dur(d):
    """ISO 8601 duration to minutes."""
    if not d: return 0
    d = d.replace("PT","").replace("H","h").replace("M","m").replace("S","s")
    mins = 0
    if "h" in d:
        h, d = d.split("h",1)
        mins += int(h)*60
    if "m" in d:
        m, d = d.split("m",1)
        mins += int(m)
    return mins

def visit_key(v):
    """Create a composite key: clientId + visitDate + duration + approximate time."""
    tws = v.get("timeWindows", [])
    if not tws:
        return None
    first = tws[0]
    min_start = to_cet(parse_dt(first.get("minStartTime")))
    dur = parse_dur(v.get("serviceDuration", ""))
    date_str = min_start.strftime("%Y-%m-%d") if min_start else "?"
    time_approx = min_start.strftime("%H:%M") if min_start else "?"
    
    # Extract client from visit group or ID
    group = v.get("visitGroup", "")
    vid = v.get("id", "")
    
    return f"{date_str}_{dur}_{time_approx}"

def extract_client_id_script(vid):
    """Extract client ID from script visit ID like H015_r0_1."""
    parts = vid.split("_r")
    return parts[0] if parts else vid

def get_visit_signature(v):
    """Get a unique signature for matching visits across systems."""
    tws = v.get("timeWindows", [])
    dur = parse_dur(v.get("serviceDuration", ""))
    if not tws:
        return None
    
    dates = set()
    for tw in tws:
        ms = to_cet(parse_dt(tw.get("minStartTime")))
        if ms:
            dates.add(ms.strftime("%Y-%m-%d"))
    
    first = tws[0]
    min_start = to_cet(parse_dt(first.get("minStartTime")))
    time_str = min_start.strftime("%H:%M") if min_start else "?"
    
    return (frozenset(dates), dur, time_str)

def main():
    script_mi = load(SCRIPT)
    dash_mi = load(DASH)
    
    sv = script_mi["visits"]
    dv = dash_mi["visits"]
    sg = script_mi.get("visitGroups", [])
    dg = dash_mi.get("visitGroups", [])
    
    print(f"=== FSR COMPARISON ===")
    print(f"Script: {len(sv)} visits, {len(sg)} groups")
    print(f"Dashboard: {len(dv)} visits, {len(dg)} groups")
    
    # Count deps
    s_deps = sum(len(v.get("visitDependencies",[])) for v in sv)
    d_deps = sum(len(v.get("visitDependencies",[])) for v in dv)
    print(f"Script deps: {s_deps}, Dashboard deps: {d_deps}")
    
    # Group visits by client
    s_by_client = defaultdict(list)
    for v in sv:
        client = extract_client_id_script(v["id"])
        s_by_client[client].append(v)
    
    # For dashboard, we need to figure out the client mapping
    # Dashboard visits have IDs like "att-0-2026-03-01" - need to check visitGroup or other fields
    # Let's check the visit group structure
    d_group_map = {}
    for g in dg:
        for vobj in g.get("visits", []):
            vid = vobj["id"] if isinstance(vobj, dict) else vobj
            d_group_map[vid] = g["id"]
    
    # Check a sample dashboard visit for fields
    sample = dv[0] if dv else {}
    print(f"\nDashboard visit sample keys: {list(sample.keys())}")
    
    # Check if there's a tag or metadata field
    # Look for clientId-like info
    d_by_date_dur = defaultdict(list)
    for v in dv:
        tws = v.get("timeWindows", [])
        dur = parse_dur(v.get("serviceDuration", ""))
        for tw in tws:
            ms = to_cet(parse_dt(tw.get("minStartTime")))
            if ms:
                date = ms.strftime("%Y-%m-%d")
                d_by_date_dur[(date, dur)].append(v)
                break
    
    # Compare per-client visit counts
    print(f"\n=== VISIT COUNT PER CLIENT (Script) ===")
    total_s = 0
    total_d = 0
    
    # We need to match script clients to dashboard clients
    # Let's compare by visit group IDs
    s_group_map = defaultdict(list)
    for v in sv:
        grp = v.get("visitGroup", "")
        if grp:
            s_group_map[grp].append(v)
    
    d_group_map2 = defaultdict(list)
    for v in dv:
        grp = v.get("visitGroup", "")
        if grp:
            d_group_map2[grp].append(v)
    
    # Let's look at how many visits have TW counts matching
    s_tw_counts = defaultdict(int)
    d_tw_counts = defaultdict(int)
    for v in sv:
        n = len(v.get("timeWindows", []))
        s_tw_counts[n] += 1
    for v in dv:
        n = len(v.get("timeWindows", []))
        d_tw_counts[n] += 1
    
    print(f"\n=== TIME WINDOW COUNT DISTRIBUTION ===")
    all_tw = sorted(set(list(s_tw_counts.keys()) + list(d_tw_counts.keys())))
    for n in all_tw:
        s = s_tw_counts.get(n, 0)
        d = d_tw_counts.get(n, 0)
        diff = d - s
        marker = " ⚠️" if diff != 0 else ""
        print(f"  {n:3d} TWs: Script={s:5d}  Dashboard={d:5d}  diff={diff:+4d}{marker}")
    
    # Duration distribution
    s_dur_counts = defaultdict(int)
    d_dur_counts = defaultdict(int)
    for v in sv:
        d2 = parse_dur(v.get("serviceDuration", ""))
        s_dur_counts[d2] += 1
    for v in dv:
        d2 = parse_dur(v.get("serviceDuration", ""))
        d_dur_counts[d2] += 1
    
    print(f"\n=== DURATION DISTRIBUTION ===")
    all_dur = sorted(set(list(s_dur_counts.keys()) + list(d_dur_counts.keys())))
    for d in all_dur:
        s = s_dur_counts.get(d, 0)
        dd = d_dur_counts.get(d, 0)
        diff = dd - s
        if abs(diff) > 0:
            print(f"  PT{d}M: Script={s:5d}  Dashboard={dd:5d}  diff={diff:+4d}")
    
    # Flexible visits (multi-TW) analysis
    s_flex = [v for v in sv if len(v.get("timeWindows",[])) > 1]
    d_flex = [v for v in dv if len(v.get("timeWindows",[])) > 1]
    print(f"\n=== FLEXIBLE VISITS ===")
    print(f"Script: {len(s_flex)} flexible visits")
    print(f"Dashboard: {len(d_flex)} flexible visits")
    
    # Group flexible by TW count
    s_flex_by_tw = defaultdict(list)
    d_flex_by_tw = defaultdict(list)
    for v in s_flex:
        n = len(v["timeWindows"])
        s_flex_by_tw[n].append(v)
    for v in d_flex:
        n = len(v["timeWindows"])
        d_flex_by_tw[n].append(v)
    
    print(f"\nFlexible visits by TW count:")
    for n in sorted(set(list(s_flex_by_tw.keys()) + list(d_flex_by_tw.keys()))):
        sc = len(s_flex_by_tw.get(n, []))
        dc = len(d_flex_by_tw.get(n, []))
        if sc != dc:
            print(f"  {n:3d} TWs: Script={sc:3d}  Dashboard={dc:3d}  diff={dc-sc:+3d}")

    # Check planning window
    s_pw = script_mi.get("planningWindow", {})
    d_pw = dash_mi.get("planningWindow", {})
    print(f"\n=== PLANNING WINDOW ===")
    print(f"Script:    {s_pw}")
    print(f"Dashboard: {d_pw}")
    
    # Dependency analysis
    print(f"\n=== DEPENDENCY ANALYSIS ===")
    s_dep_visits = [(v["id"], d) for v in sv for d in v.get("visitDependencies",[])]
    d_dep_visits = [(v["id"], d) for v in dv for d in v.get("visitDependencies",[])]
    
    # Count by type
    s_same_day = sum(1 for _,d in s_dep_visits if d.get("id","").startswith("sameday_"))
    s_spread = sum(1 for _,d in s_dep_visits if d.get("id","").startswith("spread_"))
    d_same_day = sum(1 for _,d in d_dep_visits if d.get("id","").startswith("sameday_"))
    d_spread = sum(1 for _,d in d_dep_visits if d.get("id","").startswith("spread_"))
    
    print(f"Same-day deps: Script={s_same_day}, Dashboard={d_same_day}")
    print(f"Spread deps: Script={s_spread}, Dashboard={d_spread}")
    
    # Per-date visit count comparison
    s_by_date = defaultdict(int)
    d_by_date = defaultdict(int)
    for v in sv:
        for tw in v.get("timeWindows", []):
            ms = to_cet(parse_dt(tw.get("minStartTime")))
            if ms:
                s_by_date[ms.strftime("%Y-%m-%d")] += 1
    for v in dv:
        for tw in v.get("timeWindows", []):
            ms = to_cet(parse_dt(tw.get("minStartTime")))
            if ms:
                d_by_date[ms.strftime("%Y-%m-%d")] += 1
    
    print(f"\n=== VISIT TIME WINDOWS PER DATE ===")
    all_dates = sorted(set(list(s_by_date.keys()) + list(d_by_date.keys())))
    for date in all_dates:
        s = s_by_date.get(date, 0)
        d = d_by_date.get(date, 0)
        diff = d - s
        marker = " ⚠️" if abs(diff) > 5 else ""
        print(f"  {date}: Script={s:4d}  Dashboard={d:4d}  diff={diff:+4d}{marker}")
    
    # Compare visit groups
    print(f"\n=== VISIT GROUP COMPARISON ===")
    print(f"Script groups: {len(sg)}")
    print(f"Dashboard groups: {len(dg)}")
    
    s_group_sizes = defaultdict(int)
    d_group_sizes = defaultdict(int)
    for g in sg:
        n = len(g.get("visits", []))
        s_group_sizes[n] += 1
    for g in dg:
        n = len(g.get("visits", []))
        d_group_sizes[n] += 1
    
    print(f"Group size distribution:")
    for n in sorted(set(list(s_group_sizes.keys()) + list(d_group_sizes.keys()))):
        s = s_group_sizes.get(n, 0)
        d = d_group_sizes.get(n, 0)
        if s != d:
            print(f"  Size {n}: Script={s}, Dashboard={d}")

if __name__ == "__main__":
    main()
