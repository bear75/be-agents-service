#!/usr/bin/env python3
"""Fetch all completed Timefold jobs, run quick metrics, and rank against priorities."""

from __future__ import annotations

import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"


def headers():
    return {"Content-Type": "application/json", "X-API-KEY": os.environ["TIMEFOLD_API_KEY"]}


def parse_dur(iso: str) -> float:
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+(?:\.\d+)?)([HMS])", iso):
        val, unit = float(m.group(1)), m.group(2)
        total += val * (3600 if unit == "H" else 60 if unit == "M" else 1)
    return total


def visit_name_to_client(name: str) -> str:
    if not name:
        return ""
    if " - " in name:
        prefix = name.split(" - ")[0].strip()
        s = re.sub(r"_r\d+$", "", prefix)
        s = re.sub(r"_\d+$", "", s)
        return s
    m = re.match(r"^(H\d+)", name)
    return m.group(1) if m else ""


def quick_metrics(data: dict) -> dict | None:
    mo = data.get("modelOutput")
    if not mo:
        return None
    kpis = data.get("kpis") or {}
    input_metrics = data.get("inputMetrics") or {}
    unassigned = mo.get("unassignedVisits") or []

    total_visit_sec = 0.0
    total_travel_sec = 0.0
    total_wait_sec = 0.0
    total_visits = 0
    vehicles_used = 0
    client_vehicles: dict[str, set[str]] = {}

    for veh in mo.get("vehicles") or []:
        vid = veh.get("id", "?")
        has_visits = False
        for shift in veh.get("shifts") or []:
            metrics = shift.get("metrics") or {}
            total_travel_sec += parse_dur(metrics.get("totalTravelTime", "PT0S"))
            total_wait_sec += parse_dur(metrics.get("totalWaitingTime", "PT0S"))
            total_visit_sec += parse_dur(metrics.get("totalServiceDuration", "PT0S"))

            for it in shift.get("itinerary") or []:
                if (it.get("kind") or "").upper() == "VISIT":
                    total_visits += 1
                    has_visits = True
                    # Map visit ID to client for continuity
                    visit_id = it.get("id", "")
                    if visit_id:
                        client = visit_id_to_client(visit_id)
                        if client:
                            client_vehicles.setdefault(client, set()).add(vid)
        if has_visits:
            vehicles_used += 1

    # Also use KPIs as fallback/cross-check
    if total_visits == 0 and kpis.get("totalAssignedVisits"):
        total_visits = kpis["totalAssignedVisits"]

    field_eff = (total_visit_sec / (total_visit_sec + total_travel_sec) * 100) if (total_visit_sec + total_travel_sec) > 0 else 0
    unassigned_count = len(unassigned)
    total_all = total_visits + unassigned_count
    unassigned_pct = (unassigned_count / total_all * 100) if total_all > 0 else 0

    if client_vehicles:
        cont_values = [len(v) for v in client_vehicles.values()]
        continuity_avg = sum(cont_values) / len(cont_values)
        continuity_max = max(cont_values)
    else:
        continuity_avg = 0.0
        continuity_max = 0

    score = field_eff - continuity_avg * 2.0 - unassigned_pct * 5.0

    return {
        "visits": total_visits,
        "unassigned": unassigned_count,
        "unassigned_pct": round(unassigned_pct, 2),
        "field_eff": round(field_eff, 1),
        "score": round(score, 1),
        "cont_avg": round(continuity_avg, 1),
        "cont_max": continuity_max,
        "travel_h": round(total_travel_sec / 3600, 1),
        "wait_h": round(total_wait_sec / 3600, 1),
        "visit_h": round(total_visit_sec / 3600, 1),
        "vehicles": vehicles_used,
        "clients": len(client_vehicles),
    }


def visit_id_to_client(visit_id: str) -> str:
    """Derive client from visit ID. E.g. 'H026_24_2026-03-03_Morgon' → 'H026'."""
    if not visit_id:
        return ""
    m = re.match(r"^(H\d+)", visit_id)
    return m.group(1) if m else ""


def verdict(m: dict) -> str:
    eff = m["field_eff"]
    cont = m["cont_avg"]
    unas = m["unassigned_pct"]
    if eff < 70 or unas > 5:
        return "❌ BAD"
    if eff >= 75 and cont <= 11 and unas <= 2:
        return "✅ GOOD"
    return "⚠️  OK"


def main():
    print("Fetching all route plans...", flush=True)
    r = requests.get(TIMEFOLD_BASE, headers=headers(), params={"limit": 100}, timeout=30)
    plans = r.json()

    completed = [p for p in plans if p.get("solverStatus") == "SOLVING_COMPLETED"]
    print(f"Found {len(completed)} completed jobs. Fetching solutions + metrics...\n", flush=True)

    results = []
    for i, p in enumerate(sorted(completed, key=lambda x: x.get("submitDateTime", ""), reverse=True)):
        pid = p["id"]
        name = (p.get("name") or "?")[:50]
        submitted = (p.get("submitDateTime") or "")[:19]
        score = p.get("score") or ""

        print(f"[{i+1}/{len(completed)}] {pid[:12]} {name}...", end=" ", flush=True)

        try:
            r2 = requests.get(f"{TIMEFOLD_BASE}/{pid}", headers=headers(), timeout=60)
            if r2.status_code != 200:
                print(f"HTTP {r2.status_code}")
                continue
            data = r2.json()
        except Exception as e:
            print(f"Error: {e}")
            continue

        m = quick_metrics(data)
        if not m:
            print("no modelOutput")
            continue

        v = verdict(m)
        print(f"eff={m['field_eff']}% cont={m['cont_avg']} unas={m['unassigned_pct']}% → {v}")

        results.append({
            "id": pid,
            "name": name,
            "submitted": submitted,
            "score": score[:40],
            **m,
            "verdict": v,
        })

        time.sleep(0.5)

    # Sort by score descending (eff↑, cont↓, unas↓)
    results.sort(key=lambda x: -x["score"])

    # Print summary table
    print(f"\n{'='*160}")
    print(f"ALL COMPLETED JOBS — RANKED BY SCORE (eff↑, cont↓, unas↓)")
    print(f"{'='*160}")
    print(f"{'#':>3} {'Verdict':<10} {'Score':>6} {'Eff%':>5} {'Cont':>5} {'Unas%':>6} {'Visits':>6} {'Travel':>7} {'Wait':>6} {'Visit':>7} {'Vehs':>5} {'Name':<45} {'Submitted':<20} {'ID':<14}")
    print("-" * 165)
    for i, r in enumerate(results):
        icon = r["verdict"][:2]
        print(f"{i+1:>3} {icon:<10} {r['score']:>6.1f} {r['field_eff']:>5.1f} {r['cont_avg']:>5.1f} {r['unassigned_pct']:>6.2f} {r['visits']:>6} {r['travel_h']:>6.1f}h {r['wait_h']:>5.1f}h {r['visit_h']:>6.1f}h {r['vehicles']:>5} {r['name']:<45} {r['submitted']:<20} {r['id'][:12]:<14}")

    # Sweet spot analysis
    print(f"\n{'='*80}")
    print("SWEET SPOT ANALYSIS")
    print("Lower continuity = better (1 = ideal)")
    print("Higher efficiency = better (100% = ideal)")
    print("Score = eff - cont×2 - unas×5")
    print(f"{'='*80}")
    sweet = [r for r in results if r["verdict"].startswith("✅")]
    ok = [r for r in results if r["verdict"].startswith("⚠️")]
    bad = [r for r in results if r["verdict"].startswith("❌")]

    print(f"\n✅ GOOD (eff≥75%, cont≤11, unas≤2%): {len(sweet)}")
    for r in sweet[:10]:
        print(f"   score={r['score']:.1f} eff={r['field_eff']}% cont={r['cont_avg']} unas={r['unassigned_pct']}% — {r['name']} ({r['id'][:12]})")

    print(f"\n⚠️  OK: {len(ok)}")
    for r in sorted(ok, key=lambda x: -x['score'])[:10]:
        print(f"   score={r['score']:.1f} eff={r['field_eff']}% cont={r['cont_avg']} unas={r['unassigned_pct']}% — {r['name']} ({r['id'][:12]})")

    print(f"\n❌ BAD (eff<70% or unas>5%): {len(bad)}")
    for r in bad[:5]:
        print(f"   score={r['score']:.1f} eff={r['field_eff']}% cont={r['cont_avg']} unas={r['unassigned_pct']}% — {r['name']} ({r['id'][:12]})")

    # Save results
    out_dir = Path("/workspace/recurring-visits/data/huddinge-v3/campaigns")
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "all_jobs_analysis.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    md_lines = [
        f"# All Jobs Analysis — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        f"**{len(results)} completed jobs analyzed** | ✅ {len(sweet)} good | ⚠️ {len(ok)} ok | ❌ {len(bad)} bad",
        "",
        "Lower continuity = better (1 = ideal). Higher efficiency = better (100% = ideal).",
        "Score = eff - cont×2 - unas×5. Ranked by score descending.",
        "",
        "| # | Verdict | Score | Eff% ↑ | Cont ↓ | Unas% ↓ | Visits | Travel | Wait | Name | ID |",
        "|---|---------|-------|--------|--------|---------|--------|--------|------|------|-----|",
    ]
    for i, r in enumerate(results):
        md_lines.append(
            f"| {i+1} | {r['verdict']} | {r['score']} | {r['field_eff']} | {r['cont_avg']} | {r['unassigned_pct']} | {r['visits']} | {r['travel_h']}h | {r['wait_h']}h | {r['name'][:40]} | `{r['id'][:12]}` |"
        )
    md_lines.append("")
    with open(out_dir / "ALL_JOBS_ANALYSIS.md", "w") as f:
        f.write("\n".join(md_lines))
    print(f"\nSaved: {out_dir / 'ALL_JOBS_ANALYSIS.md'}")
    print(f"Saved: {out_dir / 'all_jobs_analysis.json'}")


if __name__ == "__main__":
    main()
