#!/usr/bin/env python3
"""
Fetch Timefold input + full solution for a **dashboard** solution row.

Important: The UUID shown in the dashboard as "solution id" is usually **Solution.id**
in PostgreSQL. The Timefold API expects **route plan id** = `metadata.timefoldJobId`
(stored when optimization started). They are normally **different** UUIDs.

This script:
  1) Looks up `timefoldJobId` via `psql` + DATABASE_URL, OR you pass `--route-plan-id`
  2) Calls `scripts/timefold/fetch.py` to save full JSON + input + optional metrics
  3) Runs `verify_unassigned.py` and `analyze_dependency_feasibility.py` on the saved files

Usage:
  export DATABASE_URL="postgresql://..."   # dashboard-server DB
  python3 scripts/verification/fetch_dashboard_solution_bundle.py aaf9d57f-c03a-494b-afa1-f8d07a6de66e

  # If you already know the Timefold route plan id:
  python3 scripts/verification/fetch_dashboard_solution_bundle.py --route-plan-id <uuid> -o ./out

  # Load DB URL from beta-appcaire dashboard-server .env:
  python3 scripts/verification/fetch_dashboard_solution_bundle.py aaf9d57f-... \\
    --env-file /path/to/beta-appcaire/apps/dashboard-server/.env
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def _parse_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.exists():
        return out
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k:
            out[k] = v
    return out


def _is_uuid(s: str) -> bool:
    return bool(
        re.match(
            r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
            s,
            re.I,
        )
    )


def _resolve_database_url(args: argparse.Namespace) -> str | None:
    if args.database_url:
        return args.database_url.strip()
    u = os.environ.get("DATABASE_URL") or os.environ.get("DASHBOARD_DATABASE_URL")
    if u:
        return u.strip()
    if args.env_file:
        env = _parse_env_file(Path(args.env_file).expanduser().resolve())
        return (env.get("DATABASE_URL") or "").strip() or None
    return None


def _lookup_timefold_job_id(solution_id: str, database_url: str) -> str:
    """Return metadata.timefoldJobId for Solution.id."""
    if not _is_uuid(solution_id):
        raise SystemExit(f"Invalid solution UUID: {solution_id!r}")
    # Safe: solution_id validated as UUID hex
    sql = (
        "SELECT COALESCE(metadata->>'timefoldJobId','') "
        f"FROM \"Solution\" WHERE id = '{solution_id}'::uuid;"
    )
    try:
        r = subprocess.run(
            ["psql", database_url, "-Atq", "-c", sql],
            capture_output=True,
            text=True,
            timeout=60,
        )
    except FileNotFoundError:
        raise SystemExit(
            "psql not found. Install PostgreSQL client tools, or pass --route-plan-id "
            "with metadata.timefoldJobId from the dashboard DB / Prisma Studio.",
        ) from None
    if r.returncode != 0:
        raise SystemExit(f"psql failed: {r.stderr or r.stdout}")
    job_id = (r.stdout or "").strip()
    if not job_id or not _is_uuid(job_id):
        raise SystemExit(
            f"No timefoldJobId for Solution {solution_id}. "
            "Is this UUID the dashboard solution id? Try --route-plan-id with Timefold id."
        )
    return job_id


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Fetch Timefold bundle for a dashboard solution UUID",
    )
    ap.add_argument(
        "solution_id",
        nargs="?",
        help="Dashboard Solution.id (UUID)",
    )
    ap.add_argument(
        "--route-plan-id",
        help="Skip DB: Timefold route plan id (= timefoldJobId)",
    )
    ap.add_argument(
        "-o",
        "--out-dir",
        type=Path,
        help="Output directory (default: recurring-visits/data/dashboard-solutions/<id>/)",
    )
    ap.add_argument(
        "--database-url",
        help="PostgreSQL URL for dashboard-server (or set DATABASE_URL)",
    )
    ap.add_argument(
        "--env-file",
        type=Path,
        help="Load DATABASE_URL from this .env (e.g. beta-appcaire/apps/dashboard-server/.env)",
    )
    ap.add_argument(
        "--skip-verify",
        action="store_true",
        help="Do not run verify_unassigned / analyze_dependency_feasibility",
    )
    ap.add_argument(
        "--no-metrics",
        action="store_true",
        help="Pass to fetch.py: do not use --metrics-dir (skips input.json auto-fetch unless fetch saves it)",
    )
    args = ap.parse_args()

    if args.route_plan_id:
        job_id = args.route_plan_id.strip()
        if not _is_uuid(job_id):
            raise SystemExit(f"Invalid --route-plan-id: {job_id!r}")
        folder_name = job_id
    else:
        if not args.solution_id:
            raise SystemExit("Provide solution_id or --route-plan-id")
        db_url = _resolve_database_url(args)
        if not db_url:
            raise SystemExit(
                "Set DATABASE_URL or DASHBOARD_DATABASE_URL, or use --database-url / --env-file, "
                "or pass --route-plan-id",
            )
        job_id = _lookup_timefold_job_id(args.solution_id.strip(), db_url)
        folder_name = args.solution_id.strip()

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = _REPO_ROOT / "recurring-visits" / "data" / "dashboard-solutions" / folder_name
    out_dir = out_dir.resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    save_path = out_dir / "solution_full.json"
    metrics_dir = out_dir / "metrics" if not args.no_metrics else None

    fetch_py = _REPO_ROOT / "scripts" / "timefold" / "fetch.py"
    if not fetch_py.exists():
        raise SystemExit(f"Missing {fetch_py}")

    cmd = [
        sys.executable,
        str(fetch_py),
        job_id,
        "--save",
        str(save_path),
    ]
    if metrics_dir is not None:
        cmd.extend(["--metrics-dir", str(metrics_dir)])

    print(f"Timefold route plan id: {job_id}")
    print(f"Output directory:       {out_dir}")
    print(f"Running: {' '.join(cmd)}")
    r = subprocess.run(cmd, cwd=str(_REPO_ROOT))
    if r.returncode != 0:
        return r.returncode

    input_path = out_dir / "input.json"
    if not input_path.exists():
        print(
            f"Note: {input_path} missing (solve may not be completed, or use --metrics-dir).",
            file=sys.stderr,
        )

    if args.skip_verify:
        return 0

    vu = _REPO_ROOT / "scripts" / "verification" / "verify_unassigned.py"
    if save_path.exists():
        print("\n--- verify_unassigned ---")
        subprocess.run([sys.executable, str(vu), str(save_path)], cwd=str(_REPO_ROOT))

    if input_path.exists():
        dep = _REPO_ROOT / "scripts" / "verification" / "analyze_dependency_feasibility.py"
        report = out_dir / "dependency_feasibility.json"
        print("\n--- analyze_dependency_feasibility --all ---")
        subprocess.run(
            [
                sys.executable,
                str(dep),
                str(input_path),
                "--all",
                "-o",
                str(report),
            ],
            cwd=str(_REPO_ROOT),
        )

    print("\nDone. Re-run solve locally with same input:")
    print(f"  python3 scripts/timefold/submit.py solve {input_path} --wait --save {out_dir / 'resubmit_output.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
