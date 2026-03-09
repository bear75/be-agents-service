#!/usr/bin/env python3
"""
Submit a Timefold FSR request: either a fresh solve (modelInput) or a from-patch.

Modes:
  1. Fresh solve: POST modelInput to create a new route plan
  2. From-patch:  POST patch payload to an existing route plan

With --wait, polls until solve completes and saves the output JSON.

Usage:
  # Fresh solve
  python3 submit_to_timefold.py solve ../tf/step2-input-trimmed.json --wait --save ../tf/step2-output.json

  # From-patch
  python3 submit_to_timefold.py from-patch ../tf/step2-from-patch-payload.json \
    --route-plan-id eb1af587-f316-42b2-94e0-a099b2f8e833 \
    --wait --save ../tf/step2-output.json
"""

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import functools

import requests

# Ensure all prints flush immediately (important for background execution)
print = functools.partial(print, flush=True)

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"
SOLVER_TERMINAL = {"SOLVING_COMPLETED", "SOLVING_FAILED", "SOLVING_INCOMPLETE"}
POLL_INTERVAL_SEC = 10
POLL_TIMEOUT_SEC = 7200  # 2 hours
_DEFAULT_ENV_FILE = Path.home() / ".config" / "caire" / "env"


def _load_env_file(env_file: Path) -> None:
    """Load simple KEY=VALUE or export KEY=VALUE pairs into os.environ."""
    if not env_file.exists():
        return
    pattern = re.compile(r"^(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=(.*)$")
    for raw_line in env_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = pattern.match(line)
        if not match:
            continue
        key, value = match.groups()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        os.environ.setdefault(key, value)


def _bootstrap_env() -> None:
    """Load env: CAIRE_ENV_FILE override, else ~/.config/caire/env, else scripts/.env if no TIMEFOLD_API_KEY yet."""
    override = os.environ.get("CAIRE_ENV_FILE", "").strip()
    if override:
        _load_env_file(Path(override).expanduser())
        return
    _load_env_file(_DEFAULT_ENV_FILE)
    if not os.environ.get("TIMEFOLD_API_KEY", "").strip():
        script_env = Path(__file__).resolve().parent / ".env"
        _load_env_file(script_env)


def _headers(api_key: str) -> dict[str, str]:
    return {"Content-Type": "application/json", "X-API-KEY": api_key}


def validate_shifts(model_input: dict) -> list[tuple[str, str]]:
    """Return (vehicle_id, shift_id) for shifts with zero or negative work time."""
    bad = []
    for vehicle in model_input.get("vehicles", []):
        vid = vehicle.get("id", "?")
        for shift in vehicle.get("shifts", []):
            sid = shift.get("id", "?")
            start = shift.get("minStartTime", "")
            end = shift.get("maxEndTime", "")
            if not start or not end or start >= end:
                bad.append((vid, sid))
    return bad


def validate_visit_time_windows(model_input: dict) -> list[str]:
    """
    Check every visit (standalone + in visitGroups) has valid time windows:
    minStartTime <= maxStartTime <= maxEndTime for each time window.
    Returns list of error messages (same style as Timefold validation).
    """
    errors: list[str] = []

    def check_visit(visit: dict) -> None:
        vid = visit.get("id", "?")
        for tw in visit.get("timeWindows") or []:
            min_start = tw.get("minStartTime") or ""
            max_start = tw.get("maxStartTime") or ""
            max_end = tw.get("maxEndTime") or ""
            if not min_start or not max_end:
                continue
            if max_start and not (min_start <= max_start <= max_end):
                errors.append(
                    f"The visit ({vid}) time window does not have "
                    f"minStartTime ({min_start}) <= maxStartTime ({max_start}) <= maxEndTime ({max_end})."
                )
            elif not (min_start <= max_end):
                errors.append(
                    f"The visit ({vid}) time window does not have "
                    f"minStartTime ({min_start}) <= maxEndTime ({max_end})."
                )

    for v in model_input.get("visits") or []:
        check_visit(v)
    for g in model_input.get("visitGroups") or []:
        for v in g.get("visits") or []:
            check_visit(v)

    return errors


def _is_offset_datetime(s: str) -> bool:
    """True if s looks like ISO 8601 datetime with offset (e.g. 2026-03-02T07:00:00+01:00)."""
    if not s or not isinstance(s, str):
        return False
    return "+" in s or (s.count("-") >= 2 and "T" in s)


def _is_duration(s: str) -> bool:
    """True if s looks like ISO 8601 duration (e.g. PT30M, PT1H30M)."""
    if not s or not isinstance(s, str):
        return False
    return s.startswith("PT") and len(s) > 2


def validate_fsr_format(model_input: dict) -> list[str]:
    """
    Validate modelInput against Timefold FSR schema (RoutePlanInput, Visit, Vehicle, VehicleShift, TimeWindow).
    Returns list of all format errors so caller can fix and re-run until clean.
    """
    err: list[str] = []
    visit_ids: set[str] = set()

    def check_location(loc: object, ctx: str) -> None:
        if not isinstance(loc, list) or len(loc) != 2:
            err.append(f"FSR {ctx}: location must be [lat, lon] (array of 2 numbers), got {type(loc).__name__}")
            return
        try:
            a, b = float(loc[0]), float(loc[1])
            if not (-90 <= a <= 90) or not (-180 <= b <= 180):
                err.append(f"FSR {ctx}: location lat/lon out of range: [{a}, {b}]")
            elif a == 0 and b == 0:
                err.append(f"FSR {ctx}: geo koordinater missing (location is 0,0)")
        except (TypeError, ValueError):
            err.append(f"FSR {ctx}: location elements must be numbers, got {loc}")

    def check_time_window(tw: dict, ctx: str) -> None:
        min_s = tw.get("minStartTime")
        max_s = tw.get("maxStartTime")
        max_e = tw.get("maxEndTime")
        if not min_s or not _is_offset_datetime(str(min_s)):
            err.append(f"FSR {ctx}: timeWindow missing or invalid minStartTime (ISO 8601 with offset)")
        if not max_e or not _is_offset_datetime(str(max_e)):
            err.append(f"FSR {ctx}: timeWindow missing or invalid maxEndTime (ISO 8601 with offset)")
        if min_s and max_e and str(min_s) > str(max_e):
            err.append(f"FSR {ctx}: timeWindow minStartTime > maxEndTime")
        if max_s and _is_offset_datetime(str(max_s)) and min_s and max_e:
            if not (str(min_s) <= str(max_s) <= str(max_e)):
                err.append(f"FSR {ctx}: timeWindow minStartTime <= maxStartTime <= maxEndTime required")

    def check_visit(visit: dict, ctx: str) -> None:
        vid = visit.get("id")
        if not vid or not isinstance(vid, str) or not vid.strip():
            err.append(f"FSR {ctx}: visit missing or empty id")
        elif vid in visit_ids:
            err.append(f"FSR {ctx}: duplicate visit id '{vid}'")
        elif vid:
            visit_ids.add(vid)
        check_location(visit.get("location"), f"{ctx} visit id={visit.get('id', '?')}")
        sd = visit.get("serviceDuration")
        if not sd or not isinstance(sd, str) or not _is_duration(sd):
            err.append(f"FSR {ctx}: visit id={visit.get('id', '?')} missing or invalid serviceDuration (e.g. PT30M)")
        for i, tw in enumerate(visit.get("timeWindows") or []):
            check_time_window(tw, f"{ctx} visit id={visit.get('id', '?')} timeWindow[{i}]")

    for v in model_input.get("visits") or []:
        check_visit(v, "visits")
    for g in model_input.get("visitGroups") or []:
        gid = g.get("id", "?")
        for v in g.get("visits") or []:
            check_visit(v, f"visitGroups id={gid}")

    for veh in model_input.get("vehicles") or []:
        vid = veh.get("id", "?")
        shifts = veh.get("shifts") or []
        if not shifts:
            err.append(f"FSR vehicles: vehicle id={vid} has no shifts (minItems 1)")
        for sh in shifts:
            sid = sh.get("id", "?")
            check_location(sh.get("startLocation"), f"vehicle id={vid} shift id={sid} startLocation")
            min_start = sh.get("minStartTime")
            max_end = sh.get("maxEndTime")
            if not min_start or not _is_offset_datetime(str(min_start)):
                err.append(f"FSR vehicles: vehicle id={vid} shift id={sid} missing or invalid minStartTime")
            if not max_end or not _is_offset_datetime(str(max_end)):
                err.append(f"FSR vehicles: vehicle id={vid} shift id={sid} missing or invalid maxEndTime")
            if min_start and max_end and str(min_start) >= str(max_end):
                err.append(f"FSR vehicles: vehicle id={vid} shift id={sid} minStartTime must be before maxEndTime")

    def check_dep(dep: dict, visit_id: str) -> None:
        pred = dep.get("precedingVisit")
        if not pred or pred not in visit_ids:
            if pred:
                err.append(f"FSR visit id={visit_id}: visitDependencies precedingVisit '{pred}' not found in visits or visitGroups")
            else:
                err.append(f"FSR visit id={visit_id}: visitDependency missing precedingVisit")
        delay = dep.get("minDelay")
        if not delay or not isinstance(delay, str) or not _is_duration(delay):
            err.append(f"FSR visit id={visit_id}: visitDependency (precedingVisit={pred or '?'}) delay fel: missing or invalid minDelay (ISO 8601 e.g. PT3H30M)")

    for v in model_input.get("visits") or []:
        for dep in v.get("visitDependencies") or []:
            check_dep(dep, v.get("id", "?"))
    for g in model_input.get("visitGroups") or []:
        for v in g.get("visits") or []:
            for dep in v.get("visitDependencies") or []:
                check_dep(dep, v.get("id", "?"))

    return err


def submit_solve(payload: dict, api_key: str, configuration_id: str | None = None) -> dict:
    """POST a fresh solve request. Returns response JSON."""
    params = {}
    if configuration_id:
        params["configurationId"] = configuration_id
    r = requests.post(
        TIMEFOLD_BASE,
        headers=_headers(api_key),
        json=payload,
        params=params or None,
        timeout=300,
    )
    if r.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def submit_from_patch(
    payload: dict,
    route_plan_id: str,
    api_key: str,
    configuration_id: str | None = None,
) -> dict:
    """POST a from-patch request. Returns response JSON."""
    url = f"{TIMEFOLD_BASE}/{route_plan_id}/from-patch"
    params = {"select": "SOLVED", "operation": "SOLVE"}
    if configuration_id:
        params["configurationId"] = configuration_id
    r = requests.post(
        url,
        headers=_headers(api_key),
        params=params,
        json=payload,
        timeout=60,
    )
    if r.status_code not in (200, 201, 202):
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    return r.json()


def poll_until_done(plan_id: str, api_key: str) -> dict:
    """Poll route plan until terminal status. Returns final response."""
    url = f"{TIMEFOLD_BASE}/{plan_id}"
    deadline = time.monotonic() + POLL_TIMEOUT_SEC
    last_status = ""
    while time.monotonic() < deadline:
        r = requests.get(url, headers=_headers(api_key), timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Poll error: HTTP {r.status_code}: {r.text[:500]}")
        data = r.json()
        meta = data.get("metadata") or data.get("run") or {}
        status = meta.get("solverStatus", "").upper() or data.get("solverStatus", "").upper()
        if status != last_status:
            score = meta.get("score", "")
            print(f"  [{time.strftime('%H:%M:%S')}] Status: {status}  Score: {score}")
            last_status = status
        if status in SOLVER_TERMINAL:
            return data
        time.sleep(POLL_INTERVAL_SEC)
    raise RuntimeError("Timeout waiting for solve to complete.")


def _short_run_id(raw_id: str) -> str:
    if "-" in raw_id:
        return raw_id.split("-", 1)[0]
    return raw_id[:8]


def _map_solver_status_to_run_status(solver_status: str | None) -> str:
    status = (solver_status or "").upper().strip()
    if status in {"SOLVING_COMPLETED", "COMPLETED"}:
        return "completed"
    if status in {"SOLVING_FAILED", "SOLVING_INCOMPLETE", "FAILED", "INCOMPLETE"}:
        return "failed"
    if status in {"CANCELLED", "CANCELED"}:
        return "cancelled"
    if status in {"SOLVING_SCHEDULED", "SCHEDULED", "QUEUED", "PENDING"}:
        return "queued"
    if status in {"SOLVING_ACTIVE", "ACTIVE", "RUNNING"}:
        return "running"
    return "running"


def _register_run_in_darwin(
    args: argparse.Namespace,
    plan_id: str,
    status: str,
    score: str | None = None,
) -> None:
    if getattr(args, "no_register_darwin", False):
        return
    darwin_api = (getattr(args, "darwin_api", None) or "").strip()
    if not darwin_api:
        return
    run_id = _short_run_id(plan_id)
    payload = {
        "id": run_id,
        "route_plan_id": plan_id,
        "dataset": getattr(args, "dataset", None) or "huddinge-2w-expanded",
        "batch": getattr(args, "batch", None) or datetime.now().strftime("%d-%b").lower(),
        "algorithm": getattr(args, "algorithm", None) or run_id,
        "strategy": getattr(args, "strategy", None)
        or ("from-patch" if args.mode == "from-patch" else "fresh-solve"),
        "hypothesis": getattr(args, "hypothesis", None),
        "status": status,
        "timefold_score": score,
        "output_path": str(args.save) if getattr(args, "save", None) else None,
        "notes": getattr(args, "notes", None),
    }
    url = f"{darwin_api.rstrip('/')}/api/schedule-runs/register"
    try:
        r = requests.post(url, headers={"Content-Type": "application/json"}, json=payload, timeout=10)
        if r.status_code >= 400:
            print(
                f"Warning: Darwin register failed ({r.status_code}): {r.text[:220]}",
                file=sys.stderr,
            )
            return
        print(f"Darwin run synced: {run_id} ({status})")
    except requests.RequestException as e:
        print(f"Warning: Darwin register request failed: {e}", file=sys.stderr)


def main() -> int:
    _bootstrap_env()

    ap = argparse.ArgumentParser(description="Submit to Timefold FSR API.")
    sub = ap.add_subparsers(dest="mode", required=True)

    # Validate-only mode (no API key needed; same checks as pre-submit)
    validate_p = sub.add_parser("validate", help="Validate input JSON (time windows, shifts). No submit.")
    validate_p.add_argument("input", type=Path, help="Input JSON with modelInput.")

    # Solve mode
    solve_p = sub.add_parser("solve", help="Submit fresh solve (modelInput).")
    solve_p.add_argument("input", type=Path, help="Input JSON with modelInput.")
    solve_p.add_argument(
        "--configuration-id",
        default=os.environ.get("TIMEFOLD_CONFIGURATION_ID", "6a4e6b5f-8767-48f8-9365-7091f7e74a37"),
        help="Timefold configuration profile ID (or set TIMEFOLD_CONFIGURATION_ID). Default: 6a4e6b5f-8767-48f8-9365-7091f7e74a37",
    )
    solve_p.add_argument("--skip-validate", action="store_true")

    # From-patch mode
    patch_p = sub.add_parser("from-patch", help="Submit from-patch to existing route plan.")
    patch_p.add_argument("payload", type=Path, help="From-patch payload JSON.")
    patch_p.add_argument("--route-plan-id", required=True, help="Route plan ID to patch.")
    patch_p.add_argument(
        "--configuration-id",
        default=os.environ.get("TIMEFOLD_CONFIGURATION_ID", "6a4e6b5f-8767-48f8-9365-7091f7e74a37"),
        help="Timefold configuration profile ID (or set TIMEFOLD_CONFIGURATION_ID).",
    )

    # Common args
    for p in [solve_p, patch_p]:
        p.add_argument("--wait", action="store_true", help="Poll until solve completes.")
        p.add_argument("--save", type=Path, default=None, help="Save output JSON to file (timestamp inserted: output_YYYYMMDD_HHMMSS.json).")
        p.add_argument("--no-timestamp", action="store_true", help="Use exact --save path (no timestamp).")
        p.add_argument(
            "--api-key",
            default=None,
            help="Timefold API key (default: TIMEFOLD_API_KEY env or ~/.config/caire/env).",
        )
        p.add_argument(
            "--dataset",
            default=os.environ.get("TIMEFOLD_DATASET", "huddinge-2w-expanded"),
            help="Schedule dataset label for Darwin dashboard row.",
        )
        p.add_argument(
            "--batch",
            default=os.environ.get("TIMEFOLD_BATCH", datetime.now().strftime("%d-%b").lower()),
            help="Batch label for Darwin dashboard row (e.g. 28-feb).",
        )
        p.add_argument("--algorithm", default=None, help="Algorithm label for Darwin schedule run row.")
        p.add_argument("--strategy", default=None, help="Strategy label for Darwin schedule run row.")
        p.add_argument("--hypothesis", default=None, help="Hypothesis text for Darwin schedule run row.")
        p.add_argument("--notes", default=None, help="Optional notes for Darwin schedule run row.")
        p.add_argument(
            "--darwin-api",
            default=os.environ.get("DARWIN_API", "http://localhost:3010"),
            help="Darwin dashboard base URL for run registration.",
        )
        p.add_argument(
            "--no-register-darwin",
            action="store_true",
            help="Do not POST run state to Darwin /api/schedule-runs/register.",
        )
    patch_p.add_argument("--save-id", type=Path, default=None, help="Write new route plan ID to this file (from-patch only).")

    args = ap.parse_args()

    if args.mode == "validate":
        if not args.input.exists():
            print(f"Error: not found {args.input}", file=sys.stderr)
            return 1
        with open(args.input) as f:
            payload = json.load(f)
        mi = payload.get("modelInput") or payload
        bad_shifts = validate_shifts(mi)
        tw_errors = validate_visit_time_windows(mi)
        fsr_errors = validate_fsr_format(mi)
        if bad_shifts:
            print(f"Validation failed: {len(bad_shifts)} shift(s) with invalid minStartTime/maxEndTime.", file=sys.stderr)
            for vid, sid in bad_shifts[:15]:
                print(f"  vehicle={vid} shift={sid}", file=sys.stderr)
            if len(bad_shifts) > 15:
                print(f"  ... and {len(bad_shifts) - 15} more.", file=sys.stderr)
            return 1
        if tw_errors:
            print(f"Validation failed: {len(tw_errors)} visit time window issue(s).", file=sys.stderr)
            for msg in tw_errors[:20]:
                print(f"  {msg}", file=sys.stderr)
            if len(tw_errors) > 20:
                print(f"  ... and {len(tw_errors) - 20} more.", file=sys.stderr)
            return 1
        if fsr_errors:
            print(f"Validation failed: {len(fsr_errors)} FSR format error(s).", file=sys.stderr)
            for msg in fsr_errors[:50]:
                print(f"  {msg}", file=sys.stderr)
            if len(fsr_errors) > 50:
                print(f"  ... and {len(fsr_errors) - 50} more.", file=sys.stderr)
            return 1
        print("Validation OK (shifts, visit time windows, FSR schema).")
        return 0

    api_key = getattr(args, "api_key", None) or os.environ.get("TIMEFOLD_API_KEY", "")
    if not api_key:
        print(
            "Error: Set TIMEFOLD_API_KEY, pass --api-key, create ~/.config/caire/env, or recurring-visits/scripts/.env (see .env.example)",
            file=sys.stderr,
        )
        return 1

    if args.mode == "solve":
        if not args.input.exists():
            print(f"Error: not found {args.input}", file=sys.stderr)
            return 1
        with open(args.input) as f:
            payload = json.load(f)
        mi = payload.get("modelInput") or payload
        n_visits = len(mi.get("visits", []))
        n_vehicles = len(mi.get("vehicles", []))
        n_shifts = sum(len(v.get("shifts", [])) for v in mi.get("vehicles", []))
        print(f"Solve: {n_visits} visits, {n_vehicles} vehicles, {n_shifts} shifts")

        if not args.skip_validate:
            bad = validate_shifts(mi)
            if bad:
                print(f"Error: {len(bad)} shifts with zero/negative work time.", file=sys.stderr)
                for vid, sid in bad[:10]:
                    print(f"  vehicle={vid} shift={sid}", file=sys.stderr)
                return 1
            tw_errors = validate_visit_time_windows(mi)
            if tw_errors:
                print(f"Error: {len(tw_errors)} visit time window validation issue(s).", file=sys.stderr)
                for msg in tw_errors[:20]:
                    print(f"  {msg}", file=sys.stderr)
                if len(tw_errors) > 20:
                    print(f"  ... and {len(tw_errors) - 20} more.", file=sys.stderr)
                return 1

        if getattr(args, "configuration_id", None):
            print(f"Using configuration profile: {args.configuration_id}")
        try:
            resp = submit_solve(
                payload,
                api_key,
                getattr(args, "configuration_id", None),
            )
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        print(f"Submitted. Route plan ID: {plan_id}")

    elif args.mode == "from-patch":
        if not args.payload.exists():
            print(f"Error: not found {args.payload}", file=sys.stderr)
            return 1
        with open(args.payload) as f:
            payload = json.load(f)
        n_ops = len(payload.get("patch", []))
        print(f"From-patch: {n_ops} operations -> route plan {args.route_plan_id}")

        if getattr(args, "configuration_id", None):
            print(f"Using configuration profile: {args.configuration_id}")
        try:
            resp = submit_from_patch(
                payload,
                args.route_plan_id,
                api_key,
                getattr(args, "configuration_id", None),
            )
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1
        plan_id = resp.get("id") or resp.get("parentId") or resp.get("originId") or "?"
        print(f"Submitted. New route plan ID: {plan_id}")
        if getattr(args, "save_id", None):
            args.save_id.parent.mkdir(parents=True, exist_ok=True)
            args.save_id.write_text(plan_id.strip() + "\n")
            print(f"Saved route plan ID to {args.save_id}")

    else:
        ap.print_help()
        return 1

    initial_solver_status = (
        (resp.get("metadata") or {}).get("solverStatus")
        or resp.get("solverStatus")
        or "SOLVING_SCHEDULED"
    )
    _register_run_in_darwin(
        args,
        plan_id,
        _map_solver_status_to_run_status(initial_solver_status),
    )

    if args.wait:
        print(f"\nPolling for completion (route plan: {plan_id})...")
        try:
            result = poll_until_done(plan_id, api_key)
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        meta = result.get("metadata") or result.get("run") or {}
        status = meta.get("solverStatus", "?")
        score = meta.get("score", "?")
        print(f"\nDone. Status: {status}, Score: {score}")
        _register_run_in_darwin(
            args,
            plan_id,
            _map_solver_status_to_run_status(status),
            str(score) if score is not None else None,
        )

        if args.save:
            if args.save.exists() and args.save.is_dir() or args.save.suffix == "":
                save_path = args.save / f"{plan_id}_output.json"
            elif getattr(args, "no_timestamp", False):
                save_path = args.save
            else:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_path = args.save.parent / f"{args.save.stem}_{ts}{args.save.suffix}"
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "w") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"Output saved to {save_path}")

        if "COMPLETED" not in status.upper():
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
