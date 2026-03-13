#!/usr/bin/env python3
"""
Fetch all Timefold FSR jobs from both tenants (test + prod) and run metrics + continuity.
Produces per-job output and a combined ANALYSIS.md / analysis.json.

Usage:
  python3 fetch_all_jobs_and_analyze.py --api-key-test <key> --api-key-prod <key> --out-dir ../huddinge-package/.../v2/continuity/campaign_results

Route plan IDs can be passed via --ids or read from a file (--ids-file).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

# IDs from user paste: table 1 (huddinge-wait-min), table 2, baseline
DEFAULT_IDS = [
    "1aa5e0a0-fc68-4ef5-96a7-059824b696db",
    "6d2d0476-53f5-49ed-846d-bc505444eac3",
    "595e0754-a312-49b8-998a-e9c511e1bcc6",
    "0e90ced7-07e9-4c17-a6b0-3bca9c39f696",
    "73814740-d974-4b3b-b8a7-b944a38e68b7",
    "d12f37f3-ee96-4ba3-bdf1-d44bd48641d4",
    "14264697-510d-4716-9981-8801ccf92ed5",
    "eb063029-cd72-4ec7-9051-413ae3a76bac",
    "c01ea913-6a1e-404f-a6ba-98547336e7ea",
    "22a3d602-89e2-4c6f-b862-b8acba05069d",
    "a80bf065-9c56-48c2-a7be-c5fee68f35a9",
    "57c49c98-7786-4d0c-8cc4-34e29cdac339",
    "cdfbe510-093f-490e-8d9a-c8172e40710f",
    "3497d40d-73d6-4e50-912d-a8486a1c7950",
    "178ede96-2cf1-4e17-ac89-6e990216325c",
    "117a4aa3-a657-43ad-b8f4-e997bba39757",
    "6ce4509b-b27f-4547-8135-43f9f59f94ab",
    "9c89f76c-a6aa-467d-82a0-c392b04c18e0",
    "88d4fa41-22ec-4f36-a2b8-168c35832bae",
    "a17a8eab-478b-49fe-b994-0257527da786",
    "ec236968-e08c-47b4-be19-0553f0f7a7e4",
    "636a8aff-c846-48b1-a34f-3f09b978550a",
    "70eb56bf-933a-45b3-84a0-30eeae6838a5",
    "8092f87c-5b53-4424-9439-bb49d45aa700",
    "9cb752e2-0293-44f3-a054-1103d04185f1",
    "d2a6a01b-3309-4db5-ab4c-78ad1a218c19",
]


def fetch_solution(route_plan_id: str, api_key: str) -> dict:
    from fetch_timefold_solution import fetch_solution as _fetch

    return _fetch(route_plan_id, api_key)


def fetch_input(route_plan_id: str, api_key: str) -> dict:
    from fetch_timefold_solution import fetch_input as _fetch_input

    return _fetch_input(route_plan_id, api_key)


def fetch_one(
    route_plan_id: str,
    api_key_test: str,
    api_key_prod: str,
    out_dir: Path,
) -> tuple[str | None, str]:
    """Fetch solution and input for one ID. Try test then prod. Returns (tenant, error_msg)."""
    short = route_plan_id.split("-")[0] if route_plan_id else "unknown"
    job_dir = out_dir / short
    job_dir.mkdir(parents=True, exist_ok=True)
    output_path = job_dir / "output.json"
    input_path = job_dir / "input.json"

    for tenant, key in [("caire-test", api_key_test), ("caire-production", api_key_prod)]:
        if not key:
            continue
        try:
            data = fetch_solution(route_plan_id, key)
        except RuntimeError as e:
            err = str(e)
            if "404" in err or "403" in err:
                continue
            return None, err
        # Save full response
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Fetch input
        try:
            inp = fetch_input(route_plan_id, key)
            if "modelInput" not in inp and ("vehicles" in inp or "visits" in inp):
                inp = {"modelInput": inp}
            with open(input_path, "w", encoding="utf-8") as f:
                json.dump(inp, f, indent=2, ensure_ascii=False)
        except RuntimeError:
            pass  # input optional if we have output
        return tenant, ""
    return None, "Not found on test or prod"


def run_metrics_continuity(job_dir: Path, route_plan_id: str, only_kundnr: bool) -> bool:
    output_path = job_dir / "output.json"
    input_path = job_dir / "input.json"
    if not output_path.exists() or not input_path.exists():
        return False
    rid_safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in str(route_plan_id))[:32]
    cmd = [
        sys.executable,
        str(_SCRIPT_DIR / "run_metrics_and_continuity.py"),
        "--input",
        str(input_path.resolve()),
        "--output",
        str(output_path.resolve()),
        "--out-dir",
        str(job_dir.resolve()),
        "--id",
        rid_safe,
    ]
    if only_kundnr:
        cmd.append("--only-kundnr")
    r = subprocess.run(cmd, cwd=str(_SCRIPT_DIR))
    return r.returncode == 0


def extract_metadata(output_path: Path) -> dict:
    """Extract display fields from Timefold output.json."""
    out = {
        "name": "",
        "configuration_profile": "",
        "medium": None,
        "soft": None,
        "solver_status": "",
        "total_unassigned": 0,
        "total_activated_vehicles": 0,
        "visits": 0,
        "vehicle_shifts": 0,
        "total_travel_time_seconds": None,
        "total_travel_distance_meters": None,
        "avg_travel_time_per_visit_seconds": None,
    }
    if not output_path.exists():
        return out
    try:
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return out
    meta = data.get("metadata") or data.get("run") or {}
    out["name"] = meta.get("name") or data.get("name") or ""
    out["solver_status"] = (meta.get("solverStatus") or data.get("solverStatus") or "").upper()
    score = meta.get("score")
    if isinstance(score, dict):
        out["medium"] = score.get("medium")
        out["soft"] = score.get("soft")
    elif isinstance(score, (int, float)):
        out["medium"] = score
    tags = meta.get("tags") or []
    out["configuration_profile"] = (tags[0] if tags else "") or meta.get("configurationName") or ""

    mo = data.get("modelOutput") or {}
    out["total_unassigned"] = len(mo.get("unassignedVisits") or [])
    vehicles = mo.get("vehicles") or []
    out["total_activated_vehicles"] = len(vehicles)
    total_visits = 0
    total_travel_sec = 0
    total_dist_m = 0
    for v in vehicles:
        for shift in v.get("shifts") or []:
            out["vehicle_shifts"] += 1
            for dep in shift.get("depots") or []:
                for s in dep.get("stops") or []:
                    if s.get("visitId"):
                        total_visits += 1
                    total_travel_sec += s.get("driveDurationSeconds") or 0
                    total_dist_m += s.get("driveDistanceMeters") or 0
    out["visits"] = total_visits
    out["total_travel_time_seconds"] = int(total_travel_sec) if total_travel_sec else None
    out["total_travel_distance_meters"] = int(total_dist_m) if total_dist_m else None
    if total_visits and total_travel_sec:
        out["avg_travel_time_per_visit_seconds"] = int(total_travel_sec / total_visits)
    return out


def build_analysis_table(out_dir: Path) -> tuple[list[dict], str]:
    """Collect all run_summary_*.json and output.json metadata into one table. Returns (rows, markdown)."""
    rows = []
    for d in sorted(out_dir.iterdir()):
        if not d.is_dir():
            continue
        summaries = list(d.glob("run_summary_*.json"))
        output_json = d / "output.json"
        meta = extract_metadata(output_json)
        summary = {}
        if summaries:
            latest = max(summaries, key=lambda p: p.stat().st_mtime)
            with open(latest, encoding="utf-8") as f:
                summary = json.load(f)
        metrics_jsons = list(d.glob("metrics_*.json"))
        if metrics_jsons:
            latest_m = max(metrics_jsons, key=lambda p: p.stat().st_mtime)
            with open(latest_m, encoding="utf-8") as f:
                m = json.load(f)
            if meta.get("total_travel_time_seconds") is None and m.get("travel_time_h") is not None:
                meta["total_travel_time_seconds"] = int(m["travel_time_h"] * 3600)
            if meta.get("total_travel_distance_meters") is None and m.get("total_travel_distance_meters") is not None:
                meta["total_travel_distance_meters"] = m.get("total_travel_distance_meters")
        rows.append({
            "id": d.name,
            "route_plan_id": summary.get("route_plan_id") or d.name,
            "name": meta.get("name") or "",
            "configuration_profile": meta.get("configuration_profile") or "",
            "solver_status": meta.get("solver_status") or "",
            "medium": meta.get("medium"),
            "soft": meta.get("soft"),
            "total_unassigned": meta.get("total_unassigned", 0),
            "total_activated_vehicles": meta.get("total_activated_vehicles", 0),
            "visits": meta.get("visits", 0),
            "vehicle_shifts": meta.get("vehicle_shifts", 0),
            "total_travel_time_seconds": meta.get("total_travel_time_seconds"),
            "total_travel_distance_meters": meta.get("total_travel_distance_meters"),
            "avg_travel_time_per_visit_seconds": meta.get("avg_travel_time_per_visit_seconds"),
            "efficiency_pct": summary.get("efficiency_pct"),
            "field_efficiency_pct": summary.get("field_efficiency_pct"),
            "unassigned_visits": summary.get("unassigned_visits"),
            "average_unique_count": summary.get("average_unique_count"),
            "average_cci": summary.get("average_cci"),
        })
    # Sort by unassigned (asc), then by avg unique count (asc = better continuity)
    rows.sort(key=lambda r: (r.get("total_unassigned") or 999, r.get("average_unique_count") or 999))

    def fmt_sec(s):
        if s is None:
            return "—"
        h = int(s) // 3600
        m = (int(s) % 3600) // 60
        return f"{h}h {m}m"

    def fmt_km(m):
        if m is None:
            return "—"
        return f"{int(m) / 1000:.1f}km"

    md_lines = [
        "# Timefold jobs – analys",
        "",
        "| ID | NAME | CONFIG | UNASSIGNED | EFF (assignable, excl idle) % | FIELD (no wait) % | AVG UNIQUE | AVG CCI |",
        "|----|------|--------|------------|--------------------------------|-------------------|------------|--------|",
    ]
    for r in rows:
        cfg = (r.get("configuration_profile") or "").replace("system.profile:", "").replace("system.type:", "")[:18]
        md_lines.append(
            "| {} | {} | {} | {} | {} | {} | {} | {} |".format(
                r["id"],
                (r["name"] or "")[:20],
                cfg,
                r.get("total_unassigned", "—"),
                r.get("efficiency_pct") if r.get("efficiency_pct") is not None else "—",
                r.get("field_efficiency_pct") if r.get("field_efficiency_pct") is not None else "—",
                r.get("average_unique_count") if r.get("average_unique_count") is not None else "—",
                f"{r['average_cci']:.3f}" if r.get("average_cci") is not None else "—",
            )
        )
    return rows, "\n".join(md_lines)


def main() -> int:
    ap = argparse.ArgumentParser(description="Fetch all jobs from both APIs and analyze")
    ap.add_argument("--api-key-test", default=os.environ.get("TIMEFOLD_API_KEY_TEST"), help="Caire test tenant key")
    ap.add_argument("--api-key-prod", default=os.environ.get("TIMEFOLD_API_KEY_PROD"), help="Caire production tenant key")
    ap.add_argument("--out-dir", type=Path, required=True, help="Base dir for job outputs (e.g. campaign_results)")
    ap.add_argument("--ids", nargs="*", default=None, help="Route plan IDs (default: built-in list)")
    ap.add_argument("--ids-file", type=Path, default=None, help="One route plan ID per line")
    ap.add_argument("--only-kundnr", action="store_true", help="Pass --only-kundnr to continuity")
    ap.add_argument("--skip-fetch", action="store_true", help="Only run metrics+continuity and build analysis (output/input already present)")
    args = ap.parse_args()

    ids = list(args.ids) if args.ids else []
    if args.ids_file and args.ids_file.exists():
        ids.extend([line.strip() for line in args.ids_file.read_text().splitlines() if line.strip()])
    if not ids:
        ids = DEFAULT_IDS

    out_dir = args.out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    key_test = (args.api_key_test or "").strip()
    key_prod = (args.api_key_prod or "").strip()
    if not args.skip_fetch and (not key_test and not key_prod):
        print("Error: set --api-key-test and/or --api-key-prod (or TIMEFOLD_API_KEY_TEST / TIMEFOLD_API_KEY_PROD)", file=sys.stderr)
        return 1

    failed = []
    for i, rid in enumerate(ids):
        rid = rid.strip()
        if not rid:
            continue
        short = rid.split("-")[0]
        job_dir = out_dir / short
        print(f"[{i+1}/{len(ids)}] {short} ...", flush=True)
        if not args.skip_fetch:
            tenant, err = fetch_one(rid, key_test, key_prod, out_dir)
            if err:
                print(f"  Fetch failed: {err[:120]}", file=sys.stderr)
                failed.append((short, err))
                continue
            print(f"  Fetched ({tenant})")
        if not (job_dir / "output.json").exists():
            failed.append((short, "No output.json"))
            continue
        if not (job_dir / "input.json").exists():
            print(f"  Warning: no input.json for {short}, skipping metrics/continuity", file=sys.stderr)
            continue
        if run_metrics_continuity(job_dir, rid, args.only_kundnr):
            print("  Metrics + continuity OK")
        else:
            print("  Metrics/continuity failed", file=sys.stderr)

    rows, md = build_analysis_table(out_dir)
    analysis_json = out_dir / "analysis.json"
    with open(analysis_json, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)
    analysis_md = out_dir / "ANALYSIS.md"
    analysis_md.write_text(md, encoding="utf-8")
    print(f"\nWrote {analysis_json} and {analysis_md} ({len(rows)} jobs)")

    if failed:
        print(f"\nFailed: {len(failed)}", file=sys.stderr)
        for short, err in failed:
            print(f"  {short}: {err[:80]}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
