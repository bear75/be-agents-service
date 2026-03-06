#!/usr/bin/env python3
"""
Analyze whether visitDependencies (precedingVisit + minDelay) are physically feasible
given the two visits' time windows. Reports infeasible, tight, or OK per dependency.
Focus: customers with many unassigned (H034, H053, H035, H026, H038).
"""

import argparse
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

TIMEZONE = "+01:00"


def _iso_duration_to_minutes(d: str) -> int:
    if not d:
        return 0
    m = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?", d)
    if not m:
        return 0
    return int(m.group(1) or 0) * 60 + int(m.group(2) or 0)


def _parse_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace(TIMEZONE, "+01:00"))
    except (ValueError, TypeError):
        return None


def _all_visits(model: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    out = {}
    for v in model.get("visits") or []:
        out[v["id"]] = v
    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            out[v["id"]] = v
    return out


def _tw_date(t: Dict[str, Any]) -> Optional[str]:
    """Get date (YYYY-MM-DD) from a time window's minStartTime."""
    s = t.get("minStartTime") or t.get("maxEndTime") or ""
    if not s:
        return None
    return s.split("T")[0] if "T" in s else None


def _tw_bounds(t: Dict[str, Any]) -> Tuple[Optional[datetime], Optional[datetime]]:
    min_s = _parse_dt(t.get("minStartTime"))
    max_e = _parse_dt(t.get("maxEndTime"))
    return (min_s, max_e)


def _check_feasibility(
    prev_visit: Dict[str, Any],
    dep_visit: Dict[str, Any],
    delay_min: int,
) -> Tuple[str, str]:
    """
    Check if dependency is physically feasible: dep must start >= prev_end + delay.
    Checks per same-day window pair (or consecutive day if delay >= 24h).
    Returns ("infeasible"|"tight"|"ok", reason).
    """
    prev_tws = prev_visit.get("timeWindows") or []
    dep_tws = dep_visit.get("timeWindows") or []
    prev_dur = _iso_duration_to_minutes(prev_visit.get("serviceDuration") or "PT0M")
    dep_dur = _iso_duration_to_minutes(dep_visit.get("serviceDuration") or "PT0M")
    if not prev_tws or not dep_tws:
        return ("unknown", "missing time window")

    # Build (date, maxEnd) for prev and (date, minStart, latestStart) for dep
    prev_by_date: Dict[str, datetime] = {}
    for t in prev_tws:
        d = _tw_date(t)
        if not d:
            continue
        _, max_e = _tw_bounds(t)
        if max_e and (d not in prev_by_date or max_e > prev_by_date.get(d, max_e)):
            prev_by_date[d] = max_e

    dep_by_date: Dict[str, Tuple[datetime, datetime]] = {}
    for t in dep_tws:
        d = _tw_date(t)
        if not d:
            continue
        min_s, max_e = _tw_bounds(t)
        if not min_s or not max_e:
            continue
        latest_start = max_e - timedelta(minutes=dep_dur)
        if d not in dep_by_date:
            dep_by_date[d] = (min_s, latest_start)
        else:
            old_min, old_latest = dep_by_date[d]
            dep_by_date[d] = (min(min_s, old_min), max(latest_start, old_latest))

    # Same-day: prev_end + delay <= dep_latest_start
    # Cross-day (delay >= 18h): prev on D, dep on D+1: prev_end + delay <= dep_latest_start (dep next day)
    feasible_any = False
    best_slack = -1.0
    for dep_date, (dep_min_start, dep_latest_start) in dep_by_date.items():
        # Same day
        if dep_date in prev_by_date:
            prev_max_end = prev_by_date[dep_date]
            required = prev_max_end + timedelta(minutes=delay_min)
            if required <= dep_latest_start:
                feasible_any = True
                slack = (dep_latest_start - required).total_seconds() / 60
                if slack > best_slack:
                    best_slack = slack
        # Prev previous day (for 24h+ delay)
        try:
            prev_dt = datetime.fromisoformat(dep_date + "T00:00:00+01:00") - timedelta(days=1)
            prev_date_str = prev_dt.strftime("%Y-%m-%d")
            if prev_date_str in prev_by_date and delay_min >= 18 * 60:
                prev_max_end = prev_by_date[prev_date_str]
                required = prev_max_end + timedelta(minutes=delay_min)
                if required <= dep_latest_start:
                    feasible_any = True
                    slack = (dep_latest_start - required).total_seconds() / 60
                    if slack > best_slack:
                        best_slack = slack
        except Exception:
            pass

    if not feasible_any:
        # Report why: e.g. for first dep window, required vs latest
        d0 = next(iter(dep_by_date.keys()), None)
        p0 = next(iter(prev_by_date.keys()), None)
        if d0 and p0 and d0 in dep_by_date and p0 in prev_by_date:
            dep_lt = dep_by_date[d0][1]
            prev_end = prev_by_date.get(d0) or prev_by_date.get(p0)
            if prev_end:
                req = prev_end + timedelta(minutes=delay_min)
                return ("infeasible", f"required {req.strftime('%H:%M')} > dep latest start {dep_lt.strftime('%H:%M')} (date {d0})")
        return ("infeasible", "no same-day or next-day window pair satisfies prev_end+delay <= dep_latest_start")

    if best_slack < 15:
        return ("tight", f"slack {best_slack:.0f} min")
    return ("ok", f"slack {best_slack:.0f} min")


def analyze(input_path: Path, focus_kundnr: Optional[List[str]] = None) -> Dict[str, Any]:
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    mi = data.get("modelInput") or data
    visits = _all_visits(mi)

    results = []
    for vid, visit in visits.items():
        kundnr = vid.split("_")[0] if "_" in vid else ""
        if focus_kundnr and kundnr not in focus_kundnr:
            continue
        for dep in visit.get("visitDependencies") or []:
            if not isinstance(dep, dict):
                continue
            pred_id = dep.get("precedingVisit")
            delay_str = dep.get("minDelay", "PT0M")
            if not pred_id:
                continue
            delay_min = _iso_duration_to_minutes(delay_str)
            pred = visits.get(pred_id)
            if not pred:
                results.append({"dependent": vid, "preceding": pred_id, "delay": delay_str, "status": "unknown", "reason": "preceding visit not found"})
                continue
            status, reason = _check_feasibility(pred, visit, delay_min)
            results.append({
                "dependent": vid,
                "preceding": pred_id,
                "delay": delay_str,
                "delay_min": delay_min,
                "status": status,
                "reason": reason,
                "kundnr": kundnr,
            })

    return {"dependencies": results, "focus": focus_kundnr}


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze visit dependency feasibility (time windows vs minDelay)")
    parser.add_argument("input", type=Path, help="FSR input JSON")
    parser.add_argument("--focus", default="H034,H053,H035,H026,H038", help="Comma-separated kundnr to report (default: unassigned customers)")
    parser.add_argument("--all", action="store_true", help="Analyze all visits, not just focus")
    parser.add_argument("-o", "--output", type=Path, help="Write JSON report here")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=__import__("sys").stderr)
        return 1

    focus = None if args.all else [k.strip() for k in args.focus.split(",") if k.strip()]
    out = analyze(args.input, focus_kundnr=focus)
    deps = out["dependencies"]

    infeasible = [d for d in deps if d["status"] == "infeasible"]
    tight = [d for d in deps if d["status"] == "tight"]
    ok = [d for d in deps if d["status"] == "ok"]
    unknown = [d for d in deps if d["status"] == "unknown"]

    print("Dependency feasibility (physical: prev_end + minDelay <= dep latest start)")
    print(f"  Total analyzed: {len(deps)}")
    print(f"  Infeasible:     {len(infeasible)}  (cannot be satisfied with current windows)")
    print(f"  Tight:          {len(tight)}  (slack < 15 min)")
    print(f"  OK:             {len(ok)}")
    print(f"  Unknown:        {len(unknown)}")
    if infeasible:
        print("\n--- Infeasible (first 20) ---")
        for d in infeasible[:20]:
            print(f"  {d['dependent']} ← {d['preceding']}  delay={d['delay']}  {d['reason']}")
    if tight and len(tight) <= 30:
        print("\n--- Tight ---")
        for d in tight[:30]:
            print(f"  {d['dependent']} ← {d['preceding']}  delay={d['delay']}  {d['reason']}")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(out, f, indent=2, ensure_ascii=False)
        print(f"\nWrote {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
