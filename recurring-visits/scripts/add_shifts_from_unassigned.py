#!/usr/bin/env python3
"""
Add shifts to input JSON from unassigned analysis (supply vs demand).

Runs analyze_unassigned on input + output to find dates where unassigned visits
have no overlapping shift (supply issue). Adds placeholder day and/or evening
shifts on those dates so the next solve can assign them.

Goal (PRIORITIES.md): 0 unassigned → add shifts where demand exceeds supply,
then re-solve. Use this script after analyzing output; then regenerate/solve.

Usage:
  python add_shifts_from_unassigned.py solve/input.json solve/output.json --out solve/input_with_shifts.json
  python add_shifts_from_unassigned.py solve/input.json solve/output.json --day-only --no-timestamp
"""

import argparse
import hashlib
import json
import sys
from pathlib import Path

# Same directory as this script
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from analyze_unassigned import run_analysis as run_unassigned_analysis

DEPOT = [59.2368721, 17.9942601]
TZ = "+01:00"
# Weekend = Sat/Sun: day shift ends 14:30. Weekday: 15:00.


def _is_weekend(date_str: str) -> bool:
    from datetime import datetime
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.weekday() >= 5  # 5=Saturday, 6=Sunday
    except Exception:
        return False


def _make_day_shift(day: str, shift_idx: int) -> dict:
    """Day shift: 07:00–15:00 (weekday) or 07:00–14:30 (weekend), 30m break."""
    base = f"{day}T"
    end = "14:30:00" if _is_weekend(day) else "15:00:00"
    h = hashlib.md5(f"placeholder_day_{day}_{shift_idx}".encode()).hexdigest()[:5]
    sid = f"psd{h}"  # prefix avoids collision with existing 8-char hex shift IDs
    return {
        "id": sid,
        "startLocation": DEPOT,
        "minStartTime": f"{base}07:00:00{TZ}",
        "maxEndTime": f"{base}{end}{TZ}",
        "tags": [],
        "itinerary": [],
        "requiredBreaks": [
            {
                "id": f"{sid}_break",
                "minStartTime": f"{base}10:00:00{TZ}",
                "maxEndTime": f"{base}14:00:00{TZ}",
                "duration": "PT30M",
                "costImpact": "PAID",
                "type": "FLOATING",
                "location": DEPOT,
            }
        ],
    }


def _make_evening_shift(day: str, shift_idx: int) -> dict:
    """Evening shift: 16:00–22:00, no break (matches add_evening_vehicles)."""
    base = f"{day}T"
    h = hashlib.md5(f"placeholder_evening_{day}_{shift_idx}".encode()).hexdigest()[:5]
    sid = f"pse{h}"  # prefix avoids collision with existing 8-char hex shift IDs
    return {
        "id": sid,
        "startLocation": DEPOT,
        "minStartTime": f"{base}16:00:00{TZ}",
        "maxEndTime": f"{base}22:00:00{TZ}",
        "tags": [],
        "itinerary": [],
    }


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Add placeholder shifts for dates with unassigned supply issues (from analyze_unassigned).",
    )
    ap.add_argument("input", type=Path, help="Timefold input JSON.")
    ap.add_argument("output", type=Path, help="Timefold output JSON (solved).")
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: input_plus_shifts_<ts>.json).")
    ap.add_argument(
        "--day-only",
        action="store_true",
        help="Add only day shifts (no evening).",
    )
    ap.add_argument(
        "--evening-only",
        action="store_true",
        help="Add only evening shifts (no day).",
    )
    ap.add_argument(
        "--per-date",
        type=int,
        default=1,
        help="Number of day and evening placeholder shifts to add per date (default: 1).",
    )
    ap.add_argument("--no-timestamp", action="store_true", help="Use exact --out path.")
    ap.add_argument(
        "--add-anyway",
        action="store_true",
        help="Add shifts on dates with any unassigned (even if config-only), to get an output file for re-solve.",
    )
    args = ap.parse_args()

    if not args.input.exists():
        print(f"Error: not found {args.input}", file=sys.stderr)
        return 1
    if not args.output.exists():
        print(f"Error: not found {args.output}", file=sys.stderr)
        return 1

    with open(args.input) as f:
        data = json.load(f)
    with open(args.output) as f:
        out_data = json.load(f)

    mi = data.get("modelInput") or data
    mo = out_data.get("modelOutput") or out_data

    report, rows_for_csv = run_unassigned_analysis(mi, mo)
    # Parse by_date from report or re-run to get structure. run_analysis returns report string and rows.
    # Rebuild by_date from unassigned rows: which dates have supply issues (no overlapping shift).
    from collections import defaultdict
    by_date = defaultdict(lambda: {"supply": 0, "config": 0, "day": 0, "evening": 0, "both": 0})
    for row in rows_for_csv:
        d = row["date"]
        if row["issue"] == "supply":
            by_date[d]["supply"] += 1
        else:
            by_date[d]["config"] += 1
        b = row.get("demand_bucket", "both")
        by_date[d][b] += 1

    dates_with_supply = sorted([d for d, rec in by_date.items() if rec["supply"] > 0])
    dates_with_unassigned = sorted([d for d, rec in by_date.items() if (rec["supply"] + rec["config"]) > 0])
    if not dates_with_supply and not args.add_anyway:
        print("No dates with supply issues (all unassigned have overlapping shifts → config/tune, not add shifts).")
        print("Use --add-anyway to add shifts on dates with unassigned anyway (more capacity for re-solve).")
        print(report)
        return 0

    print(report)
    if not dates_with_supply and args.add_anyway:
        dates_with_supply = dates_with_unassigned
        print(f"\n--add-anyway: adding placeholder shifts on {len(dates_with_supply)} dates with unassigned (config): {dates_with_supply}")
    print(f"\nAdding placeholder shifts for {len(dates_with_supply)} dates with supply issues: {dates_with_supply}")

    vehicles = list(mi.get("vehicles", []))
    add_day = not args.evening_only
    add_evening = not args.day_only
    n_per = max(1, args.per_date)

    # Unique placeholder IDs when re-running (input may already have Placeholder_Supply_Day / _Evening)
    existing_day = sum(1 for v in vehicles if (v.get("id") or "").startswith("Placeholder_Supply_Day"))
    existing_evening = sum(1 for v in vehicles if (v.get("id") or "").startswith("Placeholder_Supply_Evening"))
    day_suffix = f"_{existing_day + 1}" if existing_day else ""
    evening_suffix = f"_{existing_evening + 1}" if existing_evening else ""

    if add_day:
        day_shifts = []
        for day in dates_with_supply:
            for i in range(n_per):
                day_shifts.append(_make_day_shift(day, i))
        vehicles.append({
            "id": f"Placeholder_Supply_Day{day_suffix}",
            "vehicleType": "VAN",
            "shifts": day_shifts,
        })
    if add_evening:
        evening_shifts = []
        for day in dates_with_supply:
            for i in range(n_per):
                evening_shifts.append(_make_evening_shift(day, i))
        vehicles.append({
            "id": f"Placeholder_Supply_Evening{evening_suffix}",
            "vehicleType": "VAN",
            "shifts": evening_shifts,
        })

    mi["vehicles"] = vehicles

    out_path = args.out
    if out_path is None:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = args.input.parent / f"input_plus_shifts_{ts}.json"
    elif not args.no_timestamp:
        from datetime import datetime
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = out_path.parent / f"{out_path.stem}_{ts}{out_path.suffix}"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    n_vehicles = len(vehicles)
    n_shifts = sum(len(v.get("shifts", [])) for v in vehicles)
    print(f"\nAdded placeholder vehicles: {n_vehicles} total, {n_shifts} shifts")
    print(f"Wrote {out_path}")
    print("Next: re-solve with this input to aim for 0 unassigned; then run from-patch to trim empty shifts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
