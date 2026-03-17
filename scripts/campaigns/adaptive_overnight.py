#!/usr/bin/env python3
"""
Adaptive overnight campaign: submit → monitor → evaluate → double down or cancel.

Loop:
  1. Submit next pending campaign (retry hourly if queue full)
  2. Poll all running campaigns for completion
  3. On completion: fetch solution, run metrics + continuity
     - GOOD (sliding scale: cont 5→eff≥75%, cont 11→eff≥80%, unassigned ≤2%):
       → Mark as promising, create follow-up with pushed settings
     - BAD (efficiency <70% or unassigned >5%):
       → Cancel similar pending campaigns, document as no-good
     - OK (in between): keep, no follow-up
  4. Sleep 1 hour, repeat

All campaigns use preferredVehicles (soft constraint, not required).

Usage:
  # Full adaptive run (overnight)
  TIMEFOLD_API_KEY=... python3 adaptive_overnight.py --configuration-id <ID>

  # Dry run (build inputs, no submission)
  python3 adaptive_overnight.py --dry-run
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

SCRIPTS_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = SCRIPTS_ROOT.parent
CONTINUITY_SCRIPTS = SCRIPTS_ROOT / "continuity"
TIMEFOLD_SCRIPTS = SCRIPTS_ROOT / "timefold"

BASE_INPUT = REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "input" / "input_huddinge-v3_FIXED.json"
FIRST_RUN_OUTPUT = REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "research_output" / "exp_1773675529_iter1" / "output_20260316_164057.json"

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"

# Thresholds: efficiency vs continuity sliding scale
# Low continuity (few caregivers) is good → can accept 75% efficiency
# High continuity (many caregivers) is bad → must compensate with ≥80% efficiency
#   continuity 5  (good) → efficiency ≥75%
#   continuity 8         → efficiency ≥77.5%
#   continuity 11 (bad)  → efficiency ≥80%
# Linear interpolation: required_eff = 75 + (continuity - 5) * (5/6)
# Below 70% efficiency or above 5% unassigned = always bad
GOOD_UNASSIGNED = 2.0      # % — max for "good"
BAD_EFFICIENCY = 70.0      # below this = always bad regardless of continuity
BAD_UNASSIGNED = 5.0       # above this = always bad

import functools
print = functools.partial(print, flush=True)


def log(msg: str) -> None:
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")


def api_key() -> str:
    k = os.environ.get("TIMEFOLD_API_KEY", "").strip()
    if not k:
        env_file = Path.home() / ".config" / "caire" / "env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                m = re.match(r"^(?:export\s+)?TIMEFOLD_API_KEY=['\"]?([^'\"]+)", line.strip())
                if m:
                    return m.group(1).strip()
    return k


def headers() -> dict:
    return {"Content-Type": "application/json", "X-API-KEY": api_key()}


def build_pools(pool_size: int, out_dir: Path) -> Path | None:
    pool_dir = out_dir / f"pool_{pool_size}"
    pool_dir.mkdir(parents=True, exist_ok=True)
    pools_json = pool_dir / "pools.json"
    patched = pool_dir / f"input_pool{pool_size}_preferred.json"
    cmd = [
        sys.executable, str(CONTINUITY_SCRIPTS / "build_pools.py"),
        "--source", "first-run",
        "--input", str(BASE_INPUT),
        "--output", str(FIRST_RUN_OUTPUT),
        "--out", str(pools_json),
        "--max-per-client", str(pool_size),
        "--patch-fsr-input", str(BASE_INPUT),
        "--patched-input", str(patched),
        "--use-preferred",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return patched if r.returncode == 0 and patched.exists() else None


def apply_overrides(source: Path, out_path: Path, overrides: dict) -> bool:
    with open(source) as f:
        payload = json.load(f)
    config = payload.setdefault("config", {})
    model = config.setdefault("model", {})
    existing = model.setdefault("overrides", {})
    existing.update(overrides)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return True


def make_baseline(out_dir: Path) -> Path:
    baseline_dir = out_dir / "baseline"
    baseline_dir.mkdir(parents=True, exist_ok=True)
    out_path = baseline_dir / "input_baseline.json"
    with open(BASE_INPUT) as f:
        payload = json.load(f)
    mi = payload.get("modelInput") or payload
    for v in mi.get("visits") or []:
        v.pop("requiredVehicles", None)
        v.pop("preferredVehicles", None)
    for g in mi.get("visitGroups") or []:
        for v in g.get("visits") or []:
            v.pop("requiredVehicles", None)
            v.pop("preferredVehicles", None)
    with open(out_path, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    return out_path


def submit_solve(input_path: Path, config_id: str = "") -> str | None:
    """Submit a solve. Returns route_plan_id or None."""
    import requests
    with open(input_path) as f:
        payload = json.load(f)
    params = {}
    if config_id:
        params["configurationId"] = config_id
    try:
        r = requests.post(TIMEFOLD_BASE, headers=headers(), json=payload,
                          params=params or None, timeout=300)
    except Exception as e:
        log(f"  Submit error: {e}")
        return None
    if r.status_code == 429:
        data = r.json()
        queued = re.search(r"currently queued:\s*(\d+)", data.get("message", ""))
        log(f"  Queue full ({queued.group(1) if queued else '?'}/50)")
        return None
    if r.status_code not in (200, 201, 202):
        log(f"  HTTP {r.status_code}: {r.text[:200]}")
        return None
    resp = r.json()
    return resp.get("id") or resp.get("parentId") or resp.get("originId")


def check_status(plan_id: str) -> dict | None:
    """Check status of a route plan. Returns dict with solverStatus, score."""
    import requests
    try:
        r = requests.get(f"{TIMEFOLD_BASE}/{plan_id}", headers=headers(), timeout=30)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None


def cancel_solve(plan_id: str) -> bool:
    """Cancel a running/scheduled solve."""
    import requests
    try:
        r = requests.delete(f"{TIMEFOLD_BASE}/{plan_id}", headers=headers(), timeout=30)
        return r.status_code in (200, 204, 202)
    except Exception:
        return False


def quick_metrics_from_output(data: dict) -> dict:
    """Extract quick metrics from a completed solve response including continuity."""
    mo = data.get("modelOutput") or {}
    unassigned = mo.get("unassignedVisits") or []

    total_visits = 0
    total_travel_sec = 0
    total_visit_sec = 0
    total_wait_sec = 0
    vehicles_used = 0

    # Track client → set of vehicle IDs for continuity
    client_vehicles: dict[str, set[str]] = {}

    for veh in mo.get("vehicles") or []:
        veh_id = veh.get("id", "?")
        veh_has_visits = False
        for shift in veh.get("shifts") or []:
            metrics = shift.get("metrics") or {}
            travel = _parse_dur(metrics.get("totalTravelTime", "PT0S"))
            visit_time = 0
            for it in shift.get("itinerary") or []:
                if (it.get("kind") or "").upper() == "VISIT":
                    total_visits += 1
                    veh_has_visits = True
                    visit_time += _parse_dur(it.get("serviceDuration", "PT0S"))
                    # Derive client from visit name: "H026_24 - Bad/Dusch" → "H026"
                    name = (it.get("name") or "").strip()
                    client = _visit_name_to_client(name)
                    if client:
                        client_vehicles.setdefault(client, set()).add(veh_id)
            total_travel_sec += travel
            total_visit_sec += visit_time
            total_wait_sec += _parse_dur(metrics.get("totalWaitingTime", "PT0S"))
        if veh_has_visits:
            vehicles_used += 1

    field_eff = (total_visit_sec / (total_visit_sec + total_travel_sec) * 100) if (total_visit_sec + total_travel_sec) > 0 else 0
    unassigned_count = len(unassigned)
    total_all = total_visits + unassigned_count
    unassigned_pct = (unassigned_count / total_all * 100) if total_all > 0 else 0

    # Continuity: average distinct caregivers per client
    if client_vehicles:
        cont_values = [len(v) for v in client_vehicles.values()]
        continuity_avg = sum(cont_values) / len(cont_values)
        continuity_max = max(cont_values)
    else:
        continuity_avg = 0.0
        continuity_max = 0

    return {
        "visits_assigned": total_visits,
        "unassigned": unassigned_count,
        "unassigned_pct": round(unassigned_pct, 2),
        "field_efficiency_pct": round(field_eff, 1),
        "continuity_avg": round(continuity_avg, 1),
        "continuity_max": continuity_max,
        "travel_hours": round(total_travel_sec / 3600, 1),
        "wait_hours": round(total_wait_sec / 3600, 1),
        "visit_hours": round(total_visit_sec / 3600, 1),
        "vehicles_used": vehicles_used,
        "clients": len(client_vehicles),
        "score": (data.get("metadata") or {}).get("score", "?"),
    }


def _visit_name_to_client(name: str) -> str:
    """Derive client (Kundnr) from visit name. 'H026_24 - Bad/Dusch' → 'H026'."""
    if not name:
        return ""
    if " - " in name:
        prefix = name.split(" - ")[0].strip()
        # H026_24 → H026, H015_r1 → H015
        s = re.sub(r"_r\d+$", "", prefix)
        s = re.sub(r"_\d+$", "", s)
        return s
    m = re.match(r"^(H\d+)", name)
    return m.group(1) if m else ""


def _parse_dur(iso: str) -> float:
    if not iso or not iso.startswith("PT"):
        return 0.0
    total = 0.0
    for m in re.finditer(r"(\d+(?:\.\d+)?)([HMS])", iso):
        val, unit = float(m.group(1)), m.group(2)
        total += val * (3600 if unit == "H" else 60 if unit == "M" else 1)
    return total


def required_efficiency(continuity: float) -> float:
    """Sliding scale: what efficiency % is needed at a given continuity.
    
    Low continuity (good, few caregivers) = can accept lower efficiency:
      continuity 5  → need ≥75%
    High continuity (bad, many caregivers) = must have higher efficiency to compensate:
      continuity 11 → need ≥80%
    Linear: eff = 75 + (continuity - 5) * (5/6)
    Clamped to [75, 80].
    """
    return max(75.0, min(80.0, 75.0 + (continuity - 5.0) * (5.0 / 6.0)))


def evaluate(metrics: dict) -> str:
    """Returns 'good', 'bad', or 'ok'.
    
    Sliding scale: efficiency 75-80% for continuity 5-11.
    Lower continuity (fewer caregivers) demands higher efficiency.
    """
    eff = metrics.get("field_efficiency_pct", 0)
    unas = metrics.get("unassigned_pct", 100)
    cont = metrics.get("continuity_avg", 99)

    if eff < BAD_EFFICIENCY or unas > BAD_UNASSIGNED:
        return "bad"
    
    needed_eff = required_efficiency(cont)
    if eff >= needed_eff and unas <= GOOD_UNASSIGNED and cont <= 11.0:
        return "good"
    return "ok"


def create_follow_up(
    original: dict,
    metrics: dict,
    out_dir: Path,
    pool_size: int,
) -> dict | None:
    """Create a follow-up campaign pushing settings further from a good result."""
    name = original["name"]
    overrides = dict(original.get("overrides", {}))

    pref_weight = overrides.get("preferVisitVehicleMatchPreferredVehiclesWeight", 10)
    wait_weight = overrides.get("minimizeWaitingTimeWeight", 0)

    new_pref = min(pref_weight + 10, 40)
    new_wait = min(wait_weight + 3, 10) if wait_weight else 3

    follow_up_name = f"followup_{name}_pref{new_pref}_wait{new_wait}"
    new_overrides = dict(overrides)
    new_overrides["preferVisitVehicleMatchPreferredVehiclesWeight"] = new_pref
    new_overrides["minimizeWaitingTimeWeight"] = new_wait

    pool_base = out_dir / f"pool_{pool_size}" / f"input_pool{pool_size}_preferred.json"
    if not pool_base.exists():
        return None

    follow_up_path = out_dir / "follow_ups" / f"input_{follow_up_name}.json"
    apply_overrides(pool_base, follow_up_path, new_overrides)

    return {
        "name": follow_up_name,
        "input": str(follow_up_path),
        "pool_size": pool_size,
        "overrides": new_overrides,
        "parent": name,
        "status": "pending",
    }


def main():
    import argparse
    ap = argparse.ArgumentParser(description="Adaptive overnight campaign")
    ap.add_argument("--out-dir", type=Path,
                    default=REPO_ROOT / "recurring-visits" / "data" / "huddinge-v3" / "campaigns" / datetime.now().strftime("adaptive_%Y%m%d"))
    ap.add_argument("--configuration-id", type=str, default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--poll-interval", type=int, default=3600, help="Seconds between poll cycles (default 3600 = 1h)")
    ap.add_argument("--max-hours", type=int, default=11, help="Max hours to run (default 11)")
    args = ap.parse_args()

    if not api_key() and not args.dry_run:
        print("Error: TIMEFOLD_API_KEY required", file=sys.stderr)
        return 1

    args.out_dir.mkdir(parents=True, exist_ok=True)
    deadline = time.monotonic() + args.max_hours * 3600

    # --- Build initial campaigns ---
    log("Building initial campaign inputs...")
    POOL_SIZES = [8, 10, 12, 15]
    PROFILES = [
        {"name": "balanced", "overrides": {"preferVisitVehicleMatchPreferredVehiclesWeight": 10}},
        {"name": "continuity-heavy", "overrides": {"preferVisitVehicleMatchPreferredVehiclesWeight": 20}},
        {"name": "low-wait", "overrides": {"preferVisitVehicleMatchPreferredVehiclesWeight": 10, "minimizeWaitingTimeWeight": 5}},
    ]

    campaigns: list[dict] = []
    for size in POOL_SIZES:
        patched = build_pools(size, args.out_dir)
        if not patched:
            log(f"  WARN: Pool {size} failed")
            continue
        for profile in PROFILES:
            name = f"pool{size}_{profile['name']}"
            variant_path = args.out_dir / f"pool_{size}" / f"input_{name}.json"
            apply_overrides(patched, variant_path, profile["overrides"])
            campaigns.append({
                "name": name,
                "input": str(variant_path),
                "pool_size": size,
                "overrides": profile["overrides"],
                "status": "pending",
                "route_plan_id": None,
                "metrics": None,
                "verdict": None,
            })
            log(f"  {name}")

    baseline_path = make_baseline(args.out_dir)
    campaigns.append({
        "name": "baseline_no_pools",
        "input": str(baseline_path),
        "pool_size": 0,
        "overrides": {},
        "status": "pending",
        "route_plan_id": None,
        "metrics": None,
        "verdict": None,
    })
    log(f"  baseline_no_pools")
    log(f"Total initial campaigns: {len(campaigns)}")

    if args.dry_run:
        log("DRY RUN — not submitting")
        for c in campaigns:
            log(f"  {c['name']}: {c['input']}")
        _save_state(campaigns, args.out_dir)
        return 0

    # --- Adaptive loop ---
    cycle = 0
    while time.monotonic() < deadline:
        cycle += 1
        log(f"\n{'='*50}")
        log(f"CYCLE {cycle} — {sum(1 for c in campaigns if c['status']=='pending')} pending, "
            f"{sum(1 for c in campaigns if c['status']=='running')} running, "
            f"{sum(1 for c in campaigns if c['status']=='completed')} completed")
        log(f"{'='*50}")

        # 1. Submit pending campaigns (one at a time to be gentle on queue)
        pending = [c for c in campaigns if c["status"] == "pending"]
        if pending:
            c = pending[0]
            log(f"Submitting {c['name']}...")
            plan_id = submit_solve(Path(c["input"]), args.configuration_id)
            if plan_id:
                c["route_plan_id"] = plan_id
                c["status"] = "running"
                c["submitted_at"] = datetime.now().isoformat()
                log(f"  -> {plan_id}")
            else:
                log(f"  -> Queue full or error, will retry next cycle")

        # 2. Check running campaigns
        running = [c for c in campaigns if c["status"] == "running"]
        for c in running:
            data = check_status(c["route_plan_id"])
            if not data:
                continue
            status = data.get("solverStatus") or (data.get("metadata") or {}).get("solverStatus", "")
            if status.upper() in ("SOLVING_COMPLETED",):
                log(f"COMPLETED: {c['name']}")
                m = quick_metrics_from_output(data)
                c["metrics"] = m
                c["status"] = "completed"
                c["completed_at"] = datetime.now().isoformat()
                verdict = evaluate(m)
                c["verdict"] = verdict

                needed = required_efficiency(m.get("continuity_avg", 99))
                log(f"  Efficiency: {m['field_efficiency_pct']}% (need ≥{needed:.0f}%)  "
                    f"Continuity: {m.get('continuity_avg', '?')} avg  "
                    f"Unassigned: {m['unassigned_pct']}%  "
                    f"Travel: {m['travel_hours']}h  Wait: {m['wait_hours']}h")

                if verdict == "good":
                    log(f"  ✅ GOOD — creating follow-up with pushed settings")
                    follow = create_follow_up(c, m, args.out_dir, c["pool_size"])
                    if follow:
                        campaigns.append(follow)
                        log(f"  -> Follow-up: {follow['name']}")
                elif verdict == "bad":
                    log(f"  ❌ BAD — cancelling similar pending campaigns")
                    pool = c["pool_size"]
                    for other in campaigns:
                        if (other["status"] == "pending" and other["pool_size"] == pool
                                and other["name"] != c["name"]):
                            other["status"] = "cancelled"
                            other["verdict"] = f"cancelled: same pool {pool} as bad {c['name']}"
                            log(f"  Cancelled: {other['name']}")
                else:
                    log(f"  ⚠️  OK — keeping, no follow-up")

            elif status.upper() in ("SOLVING_FAILED", "SOLVING_INCOMPLETE"):
                log(f"FAILED: {c['name']} — status={status}")
                c["status"] = "failed"
                c["verdict"] = f"solver {status}"

        # 3. Save state
        _save_state(campaigns, args.out_dir)

        # 4. Check if all done
        still_active = [c for c in campaigns if c["status"] in ("pending", "running")]
        if not still_active:
            log("All campaigns complete!")
            break

        # 5. Sleep
        remaining = deadline - time.monotonic()
        sleep_time = min(args.poll_interval, remaining)
        if sleep_time <= 0:
            break
        log(f"Sleeping {int(sleep_time)}s until next cycle...")
        time.sleep(sleep_time)

    # --- Final summary ---
    log(f"\n{'='*60}")
    log("OVERNIGHT CAMPAIGN COMPLETE")
    log(f"{'='*60}")
    _print_summary(campaigns)
    _save_state(campaigns, args.out_dir)
    return 0


def _save_state(campaigns: list[dict], out_dir: Path):
    manifest_path = out_dir / "campaign_state.json"
    with open(manifest_path, "w") as f:
        json.dump(campaigns, f, indent=2, default=str)

    md_lines = [
        f"# Adaptive Overnight Campaign — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        "",
        "| # | Strategy | Pool | Verdict | Efficiency | Continuity | Unassigned | Travel | Wait | Route Plan ID |",
        "|---|----------|------|---------|-----------|-----------|-----------|--------|------|---------------|",
    ]
    for i, c in enumerate(campaigns):
        m = c.get("metrics") or {}
        eff = f"{m.get('field_efficiency_pct', '—')}%" if m else "—"
        cont = f"{m.get('continuity_avg', '—')}" if m else "—"
        unas = f"{m.get('unassigned_pct', '—')}%" if m else "—"
        travel = f"{m.get('travel_hours', '—')}h" if m else "—"
        wait = f"{m.get('wait_hours', '—')}h" if m else "—"
        verdict_icon = {"good": "✅", "bad": "❌", "ok": "⚠️"}.get(c.get("verdict", ""), "⏳")
        rid = f"`{c.get('route_plan_id', '—')[:12]}`" if c.get("route_plan_id") else "—"
        md_lines.append(f"| {i+1} | {c['name']} | {c.get('pool_size', '—')} | {verdict_icon} {c.get('verdict', c['status'])} | {eff} | {cont} | {unas} | {travel} | {wait} | {rid} |")
    md_lines.append("")

    md_path = out_dir / "CAMPAIGN_RESULTS.md"
    with open(md_path, "w") as f:
        f.write("\n".join(md_lines))


def _print_summary(campaigns: list[dict]):
    good = [c for c in campaigns if c.get("verdict") == "good"]
    bad = [c for c in campaigns if c.get("verdict") == "bad"]
    ok = [c for c in campaigns if c.get("verdict") == "ok"]
    cancelled = [c for c in campaigns if c["status"] == "cancelled"]
    pending = [c for c in campaigns if c["status"] == "pending"]
    failed = [c for c in campaigns if c["status"] == "failed"]

    log(f"  ✅ Good:      {len(good)}")
    log(f"  ⚠️  OK:       {len(ok)}")
    log(f"  ❌ Bad:       {len(bad)}")
    log(f"  🚫 Cancelled: {len(cancelled)}")
    log(f"  💥 Failed:    {len(failed)}")
    log(f"  ⏳ Pending:   {len(pending)}")

    if good:
        log("\nBest results (sweet spot = high efficiency + low continuity):")
        best = sorted(good, key=lambda c: -(c.get("metrics") or {}).get("field_efficiency_pct", 0))
        for c in best[:5]:
            m = c["metrics"]
            log(f"  {c['name']}: eff={m['field_efficiency_pct']}% cont={m.get('continuity_avg','?')} "
                f"unas={m['unassigned_pct']}% travel={m['travel_hours']}h wait={m['wait_hours']}h")


if __name__ == "__main__":
    sys.exit(main() or 0)
