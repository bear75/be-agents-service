#!/usr/bin/env python3
"""
Build per-client continuity pools (up to 15 vehicle IDs per client) for FSR requiredVehicles.

Strategies:
  - manual: From expanded CSV; distinct external_slinga_shiftName per client_externalId,
            mapped to FSR vehicle IDs (spaces -> underscores), cap 15.
  - first-run: From first FSR output; for each person client, top-15 vehicles by visit count;
               cap 15. Requires FSR input (visit -> client) and output (visit -> vehicle).
  - area: Group clients by service area; assign vehicles evenly to areas; per client,
          pool = vehicles for that area, cap 15. Requires CSV + FSR input for vehicle list.

Output: JSON file mapping client_id -> list of vehicle IDs (max 15). Optionally patch
FSR input to add requiredVehicles to each visit.

Usage:
  # Manual pool from expanded CSV
  python build_continuity_pools.py --source manual --csv path/to/huddinge_2wk_expanded_*.csv \\
    --out client_pools_manual.json [--fsr-input path/to/input.json]

  # First-run pool from unconstrained FSR solution
  python build_continuity_pools.py --source first-run --input path/to/fsr-input.json \\
    --output path/to/fsr-output.json --out client_pools_firstrun.json

  # Area-based pool (service area from CSV, vehicles from FSR input)
  python build_continuity_pools.py --source area --csv path/to/expanded.csv \\
    --fsr-input path/to/input.json --out client_pools_area.json

  # Patch FSR input with requiredVehicles from pool (any source)
  python build_continuity_pools.py ... --out pools.json --patch-fsr-input path/to/input.json \\
    --patched-input path/to/input_with_required_vehicles.json
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def csv_shift_name_to_fsr_vehicle_id(shift_name: str) -> str:
    """Map CSV external_slinga_shiftName to FSR vehicle id. E.g. 'Dag 01 Central 1' -> 'Dag_01_Central_1'."""
    if not shift_name:
        return ""
    return shift_name.strip().replace(" ", "_")


def visit_id_to_client(name: str, visit_id: str) -> str:
    """Derive client id from visit name. E.g. 'H026_24 - Bad/Dusch' -> 'H026_24'."""
    if not name or " - " not in name:
        return visit_id
    return name.split(" - ")[0].strip()


def visit_name_client_to_person(visit_name_client: str) -> str:
    """Map visit-name client to person. E.g. 'H026_24' -> 'H026'."""
    if not visit_name_client:
        return visit_name_client
    return re.sub(r"_\d+$", "", visit_name_client)


def load_fsr_vehicle_ids(fsr_input_path: Path) -> set[str]:
    """Extract all vehicle IDs from FSR input."""
    with open(fsr_input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    vehicles = model.get("vehicles") or []
    return {str(v.get("id") or "") for v in vehicles if v.get("id")}


def visit_to_person_from_model(model: dict) -> dict[str, str]:
    """Build visit_id -> person client from model dict (visits + visitGroups)."""
    out: dict[str, str] = {}
    for v in model.get("visits") or []:
        vid = str(v.get("id") or "")
        name = (v.get("name") or "").strip()
        if vid:
            out[vid] = visit_name_client_to_person(visit_id_to_client(name, vid))
    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = str(v.get("id") or "")
            name = (v.get("name") or "").strip()
            if vid:
                out[vid] = visit_name_client_to_person(visit_id_to_client(name, vid))
    return out


def load_visit_to_person(fsr_input_path: Path) -> dict[str, str]:
    """Build visit_id -> person client from FSR input file (visits + visitGroups)."""
    with open(fsr_input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    return visit_to_person_from_model(model)


def load_visit_vehicle_list(fsr_output_path: Path) -> list[tuple[str, str]]:
    """From FSR output, list (visit_id, vehicle_id) for each visit in itinerary."""
    with open(fsr_output_path, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = (data.get("modelOutput") or {}).get("vehicles") or []
    out: list[tuple[str, str]] = []
    for veh in vehicles:
        vehicle_id = veh.get("id") or ""
        for shift in veh.get("shifts") or []:
            for it in shift.get("itinerary") or []:
                if (it.get("kind") or "").upper() == "VISIT":
                    vid = str(it.get("id") or "")
                    if vid and vehicle_id:
                        out.append((vid, vehicle_id))
    return out


def pools_from_manual(
    csv_path: Path,
    max_per_client: int = 15,
    valid_vehicle_ids: set[str] | None = None,
) -> dict[str, list[str]]:
    """
    Build client -> list of vehicle IDs from manual expanded CSV.
    Uses client_externalId and external_slinga_shiftName; maps shift names to FSR vehicle IDs.
    """
    client_employees: dict[str, set[str]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "client_externalId" not in (reader.fieldnames or []) or "external_slinga_shiftName" not in (reader.fieldnames or []):
            raise ValueError("CSV must have client_externalId and external_slinga_shiftName")
        for row in reader:
            client = (row.get("client_externalId") or "").strip()
            employee = (row.get("external_slinga_shiftName") or "").strip()
            if not client:
                continue
            if employee:
                client_employees.setdefault(client, set()).add(employee)

    pools: dict[str, list[str]] = {}
    for client in sorted(client_employees.keys()):
        vehicle_ids = [csv_shift_name_to_fsr_vehicle_id(s) for s in client_employees[client]]
        if valid_vehicle_ids is not None:
            vehicle_ids = [v for v in vehicle_ids if v in valid_vehicle_ids]
        # Preserve order, deduplicate, cap
        seen: set[str] = set()
        limited: list[str] = []
        for v in vehicle_ids:
            if v and v not in seen and len(limited) < max_per_client:
                seen.add(v)
                limited.append(v)
        pools[client] = limited
    return pools


def pools_from_first_run(
    fsr_input_path: Path,
    fsr_output_path: Path,
    max_per_client: int = 15,
) -> dict[str, list[str]]:
    """
    Build client -> list of vehicle IDs from first FSR run.
    For each person client, take top max_per_client vehicles by visit count.
    """
    visit_to_person = load_visit_to_person(fsr_input_path)
    visit_vehicle_list = load_visit_vehicle_list(fsr_output_path)

    # person -> list of (visit_id, vehicle_id)
    person_assignments: dict[str, list[tuple[str, str]]] = {}
    for vid, vehicle_id in visit_vehicle_list:
        person = visit_to_person.get(vid)
        if not person:
            continue
        person_assignments.setdefault(person, []).append((vid, vehicle_id))

    pools: dict[str, list[str]] = {}
    for person in sorted(person_assignments.keys()):
        assignments = person_assignments[person]
        # Count visits per vehicle
        vehicle_counts: list[tuple[str, int]] = []
        counts: dict[str, int] = {}
        for _, v_id in assignments:
            counts[v_id] = counts.get(v_id, 0) + 1
        for v_id, count in sorted(counts.items(), key=lambda x: -x[1]):
            vehicle_counts.append((v_id, count))
        top_vehicles = [v_id for v_id, _ in vehicle_counts[:max_per_client]]
        pools[person] = top_vehicles
    return pools


def pools_from_area(
    csv_path: Path,
    fsr_input_path: Path,
    max_per_client: int = 15,
    area_column: str = "serviceArea_address",
) -> dict[str, list[str]]:
    """
    Build client -> list of vehicle IDs by area. Clients grouped by area_column;
    vehicles assigned evenly to areas; each client gets vehicles for their area (cap max_per_client).
    """
    valid_vehicle_ids = list(load_fsr_vehicle_ids(fsr_input_path))
    if not valid_vehicle_ids:
        raise ValueError("FSR input has no vehicles")

    # client -> area
    client_area: dict[str, str] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if "client_externalId" not in (reader.fieldnames or []):
            raise ValueError("CSV must have client_externalId")
        area_col = area_column
        if area_col not in (reader.fieldnames or []):
            area_col = "serviceArea_address"
        if area_col not in (reader.fieldnames or []):
            raise ValueError(f"CSV must have {area_column} or serviceArea_address for area-based pools")
        for row in reader:
            client = (row.get("client_externalId") or "").strip()
            area = (row.get(area_col) or "").strip() or "default"
            if client:
                client_area[client] = area

    # area -> list of client
    area_clients: dict[str, list[str]] = {}
    for c, a in client_area.items():
        area_clients.setdefault(a, []).append(c)
    areas = sorted(area_clients.keys())

    # Assign vehicles evenly to areas (round-robin)
    area_vehicles: dict[str, list[str]] = {a: [] for a in areas}
    for i, v_id in enumerate(valid_vehicle_ids):
        area = areas[i % len(areas)]
        area_vehicles[area].append(v_id)

    pools: dict[str, list[str]] = {}
    for client in sorted(client_area.keys()):
        area = client_area[client]
        vehicle_list = area_vehicles.get(area, [])
        pools[client] = vehicle_list[:max_per_client]
    return pools


def _set_required_vehicles_on_visits(
    model: dict,
    client_pools: dict[str, list[str]],
    visit_to_person: dict[str, str],
) -> None:
    """Set requiredVehicles on visits in model (mutates in place)."""
    def set_required_on_visit(v: dict) -> None:
        vid = str(v.get("id") or "")
        person = visit_to_person.get(vid)
        if not person:
            return
        pool = client_pools.get(person)
        if not pool:
            return
        v["requiredVehicles"] = pool

    for v in model.get("visits") or []:
        set_required_on_visit(v)
    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            set_required_on_visit(v)


def patch_payload_with_pools(
    payload: dict,
    client_pools: dict[str, list[str]],
    visit_to_person: dict[str, str],
) -> None:
    """
    Set requiredVehicles on each visit in payload (mutates in place).
    payload must have modelInput with visits and optionally visitGroups.
    """
    model = payload.get("modelInput") or payload
    _set_required_vehicles_on_visits(model, client_pools, visit_to_person)


def patch_fsr_input_with_pools(
    fsr_input_path: Path,
    client_pools: dict[str, list[str]],
    visit_to_person: dict[str, str],
    patched_path: Path,
) -> None:
    """
    Read FSR input, set requiredVehicles on each visit from client_pools (by person), write to patched_path.
    Visits without a pool (or empty pool) are left without requiredVehicles.
    """
    with open(fsr_input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    _set_required_vehicles_on_visits(model, client_pools, visit_to_person)
    patched_path.parent.mkdir(parents=True, exist_ok=True)
    with open(patched_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build per-client continuity pools for FSR requiredVehicles",
    )
    parser.add_argument("--source", choices=["manual", "first-run", "area"], required=True)
    parser.add_argument("--csv", type=Path, help="Expanded CSV (manual, area)")
    parser.add_argument("--input", type=Path, help="FSR input JSON (first-run, and for patch)")
    parser.add_argument("--output", type=Path, help="FSR output JSON (first-run only)")
    parser.add_argument("--fsr-input", type=Path, help="FSR input (for vehicle list validation or area vehicle list)")
    parser.add_argument("--out", type=Path, required=True, help="Output JSON: client_id -> list of vehicle IDs")
    parser.add_argument("--max-per-client", type=int, default=15, help="Max vehicles per client (default 15)")
    parser.add_argument("--patch-fsr-input", type=Path, help="If set, patch this FSR input with requiredVehicles")
    parser.add_argument("--patched-input", type=Path, help="Path to write patched FSR input (requires --patch-fsr-input)")
    parser.add_argument("--area-column", type=str, default="serviceArea_address", help="CSV column for area (area source)")
    args = parser.parse_args()

    valid_vehicle_ids: set[str] | None = None
    if args.fsr_input and args.fsr_input.exists():
        valid_vehicle_ids = load_fsr_vehicle_ids(args.fsr_input)

    if args.source == "manual":
        if not args.csv or not args.csv.exists():
            print("Error: --csv required and must exist for source=manual", file=sys.stderr)
            return 1
        pools = pools_from_manual(args.csv, max_per_client=args.max_per_client, valid_vehicle_ids=valid_vehicle_ids)
    elif args.source == "first-run":
        if not args.input or not args.input.exists() or not args.output or not args.output.exists():
            print("Error: --input and --output required and must exist for source=first-run", file=sys.stderr)
            return 1
        pools = pools_from_first_run(args.input, args.output, max_per_client=args.max_per_client)
    else:
        if not args.csv or not args.csv.exists() or not args.fsr_input or not args.fsr_input.exists():
            print("Error: --csv and --fsr-input required for source=area", file=sys.stderr)
            return 1
        pools = pools_from_area(
            args.csv,
            args.fsr_input,
            max_per_client=args.max_per_client,
            area_column=args.area_column,
        )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(pools, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(pools)} client pools to {args.out}")

    if args.patch_fsr_input and args.patched_input:
        if not args.patch_fsr_input.exists():
            print(f"Error: FSR input not found: {args.patch_fsr_input}", file=sys.stderr)
            return 1
        visit_to_person = load_visit_to_person(args.patch_fsr_input)
        patch_fsr_input_with_pools(args.patch_fsr_input, pools, visit_to_person, args.patched_input)
        print(f"Patched FSR input written to {args.patched_input}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
