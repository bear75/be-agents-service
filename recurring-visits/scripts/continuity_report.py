#!/usr/bin/env python3
"""
Compute per-client continuity over the 2-week schedule.

KOLADA (default): one row per person (Kundnr). v1 = 81 clients, v2 = 115 clients.
  - Visit names v1: "H026_24 - Bad/Dusch" -> person H026.
  - Visit names v2: "H015 Morgon Dag Tillsyn" -> person H015.

Uses:
  - FSR input JSON: visit id -> person (Kundnr) from visit name
  - FSR output JSON: visit id -> vehicle (caregiver) per occurrence in itinerary

Output: one row per person — client (Kundnr), nr_visits, continuity (distinct caregivers; lower is better),
optionally cci (Continuity of Care Index; higher is better). Use --no-cci to omit CCI.

Use --no-kolada for legacy aggregation by visit-name stream (more rows, lower average).

Usage:
  python continuity_report.py \\
    --input path/to/export-*-input.json \\
    --output path/to/export-*-output.json \\
    [--report path/to/continuity.csv]
    [--no-kolada]  # legacy: aggregate by visit-name (e.g. H026_r24) instead of person (H026)
    [--no-cci]     # omit CCI column and summary (default: include CCI)
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path


def visit_id_to_client(name: str, visit_id: str) -> str:
    """Derive client id from visit name. E.g. 'H026_24 - Bad/Dusch, ...' -> 'H026_24'."""
    if not name or " - " not in name:
        return visit_id
    return name.split(" - ")[0].strip()


def visit_name_client_to_person(visit_name_client: str) -> str:
    """Map visit-name client to person client. E.g. 'H026_24' -> 'H026', 'H015_r1' -> 'H015'."""
    if not visit_name_client:
        return visit_name_client
    # Strip _rNN (v2 recurrence) then _NN (v1 recurrence)
    s = re.sub(r"_r\d+$", "", visit_name_client)
    s = re.sub(r"_\d+$", "", s)
    return s or visit_name_client


def name_to_person_kolada(name: str, visit_id: str) -> str:
    """
    Derive person (Kundnr) for KOLADA continuity from visit name.
    v1: 'H026_24 - Bad/Dusch' -> H026; v2: 'H015 Morgon Dag Tillsyn' -> H015.
    """
    if not name:
        return visit_id
    name = name.strip()
    if " - " in name:
        prefix = name.split(" - ")[0].strip()
        return visit_name_client_to_person(prefix) or prefix
    # v2-style: "H015 Morgon ..." or "H026   Insats"
    m = re.match(r"^(H\d+)\s*", name)
    return m.group(1) if m else visit_id


def load_visit_to_client(input_path: Path) -> dict[str, str]:
    """Build visit_id -> client_id from FSR input (visits + visitGroups). Legacy: visit-name or vid."""
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    out: dict[str, str] = {}

    for v in model.get("visits") or []:
        vid = str(v.get("id") or "")
        name = (v.get("name") or "").strip()
        if vid:
            out[vid] = visit_id_to_client(name, vid)

    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = str(v.get("id") or "")
            name = (v.get("name") or "").strip()
            if vid:
                out[vid] = visit_id_to_client(name, vid)

    return out


def load_visit_to_person_kolada(input_path: Path) -> dict[str, str]:
    """Build visit_id -> person (Kundnr) for KOLADA continuity. v1 and v2 name formats supported."""
    with open(input_path, encoding="utf-8") as f:
        data = json.load(f)
    model = data.get("modelInput") or data
    out: dict[str, str] = {}

    for v in model.get("visits") or []:
        vid = str(v.get("id") or "")
        name = (v.get("name") or "").strip()
        if vid:
            out[vid] = name_to_person_kolada(name, vid)

    for g in model.get("visitGroups") or []:
        for v in g.get("visits") or []:
            vid = str(v.get("id") or "")
            name = (v.get("name") or "").strip()
            if vid:
                out[vid] = name_to_person_kolada(name, vid)

    return out


def load_visit_vehicle_assignments(
    output_path: Path,
) -> tuple[list[tuple[str, str]], int, int]:
    """
    From FSR output, list (visit_id, vehicle_id) for each visit in itinerary.

    Uses vehicle.id only (1 vehicle = 1 caregiver). Same vehicle across many shifts
    counts as 1 caregiver for continuity. Returns (assignments, n_vehicles, n_shifts).
    """
    with open(output_path, encoding="utf-8") as f:
        data = json.load(f)
    vehicles = (data.get("modelOutput") or {}).get("vehicles") or []
    out: list[tuple[str, str]] = []
    n_shifts = 0

    for veh in vehicles:
        vehicle_id = veh.get("id") or ""
        for shift in veh.get("shifts") or []:
            n_shifts += 1
            for it in shift.get("itinerary") or []:
                if (it.get("kind") or "").upper() == "VISIT":
                    vid = str(it.get("id") or "")
                    if vid and vehicle_id:
                        out.append((vid, vehicle_id))

    n_vehicles = len(vehicles)
    return out, n_vehicles, n_shifts


def _assignments_by_person(
    visit_to_person: dict[str, str],
    output_path: Path,
) -> dict[str, list[tuple[str, str]]]:
    """Group (visit_id, vehicle_id) by person (Kundnr) from output."""
    visit_vehicle_list, _, _ = load_visit_vehicle_assignments(output_path)
    person_assignments: dict[str, list[tuple[str, str]]] = {}
    for vid, vehicle_id in visit_vehicle_list:
        person = visit_to_person.get(vid, vid)
        person_assignments.setdefault(person, []).append((vid, vehicle_id))
    return person_assignments


def compute_cci(assignments: list[tuple[str, str]]) -> float:
    """
    Our CCI: sum over caregivers of (n_i/N)^2.
    n_i = visits from caregiver i, N = total visits. Higher = better.
    Returns 0.0 if no assignments.
    """
    if not assignments:
        return 0.0
    n = len(assignments)
    counts: dict[str, int] = {}
    for _, vehicle_id in assignments:
        counts[vehicle_id] = counts.get(vehicle_id, 0) + 1
    return sum((c / n) ** 2 for c in counts.values())


def compute_bice_cci(assignments: list[tuple[str, str]]) -> float | None:
    """
    Bice-Boxerman Continuity of Care Index (official formula):
    CCI = (sum(n_i^2) - N) / (N(N-1))
    n_i = visits to caregiver i, N = total visits. Range 0–1; 1 = same caregiver every time.
    Returns None if N < 2 (formula undefined).
    """
    if len(assignments) < 2:
        return None
    n_total = len(assignments)
    counts: dict[str, int] = {}
    for _, vehicle_id in assignments:
        counts[vehicle_id] = counts.get(vehicle_id, 0) + 1
    sum_sq = sum(c * c for c in counts.values())
    denom = n_total * (n_total - 1)
    return (sum_sq - n_total) / denom


def main() -> int:
    parser = argparse.ArgumentParser(description="Per-client continuity from FSR input + output")
    parser.add_argument("--input", type=Path, required=True, help="FSR input JSON (for visit -> client)")
    parser.add_argument("--output", type=Path, required=True, help="FSR output JSON (for visit -> vehicle)")
    parser.add_argument("--report", type=Path, default=None, help="Optional: write CSV to this path")
    parser.add_argument(
        "--kolada",
        action="store_true",
        default=True,
        help="Use KOLADA: aggregate by person (Kundnr). v2 = 115 clients (default: True)",
    )
    parser.add_argument(
        "--no-kolada",
        action="store_true",
        help="Legacy: aggregate by visit-name stream (e.g. H026_r24); more rows, lower avg.",
    )
    parser.add_argument(
        "--only-kundnr",
        action="store_true",
        default=False,
        help="KOLADA: include only clients matching Kundnr (H001, H002, ...). Use for 115 clients from DB/input.",
    )
    parser.add_argument(
        "--no-cci",
        action="store_true",
        default=False,
        help="Omit CCI column and CCI summary (default: include CCI).",
    )
    args = parser.parse_args()
    include_cci = not args.no_cci
    use_kolada = args.kolada and not args.no_kolada

    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1

    visit_to_person_map: dict[str, str] | None = None
    if use_kolada:
        visit_to_person_map = load_visit_to_person_kolada(args.input)
        person_assignments = _assignments_by_person(visit_to_person_map, args.output)
        if args.only_kundnr:
            # Restrict to DB clients: only H-prefixed Kundnr (115)
            person_assignments = {
                p: a for p, a in person_assignments.items()
                if re.match(r"^H\d+$", p)
            }
    else:
        visit_to_client = load_visit_to_client(args.input)
        visit_vehicle_list, n_vehicles, n_shifts = load_visit_vehicle_assignments(args.output)
        client_assignments = {}
        for vid, vehicle_id in visit_vehicle_list:
            client = visit_to_client.get(vid, vid)
            client_assignments.setdefault(client, []).append((vid, vehicle_id))
        person_assignments = {}
        for visit_name_client, assignments in client_assignments.items():
            person = visit_name_client_to_person(visit_name_client)
            person_assignments.setdefault(person, []).extend(assignments)

    visit_vehicle_list, n_vehicles, n_shifts = load_visit_vehicle_assignments(args.output)
    visit_to_client = load_visit_to_client(args.input)

    # Build rows: one per person — client, nr_visits, continuity (unique count), optional cci, bice_cci
    rows: list[tuple[str, int, int, float | None, float | None]] = []
    for person in sorted(person_assignments.keys()):
        assignments = person_assignments[person]
        nr_visits = len(assignments)
        nr_caregivers = len({v for _, v in assignments})
        cci = compute_cci(assignments) if include_cci else None
        bice_cci = compute_bice_cci(assignments) if include_cci else None
        rows.append((person, nr_visits, nr_caregivers, cci, bice_cci))

    # Print table
    if include_cci:
        print("client,nr_visits,continuity,cci,bice_cci")
        print("(continuity = distinct caregivers, lower better; cci = sum(n_i/N)^2; bice_cci = Bice-Boxerman (sum n_i^2-N)/(N(N-1)), higher better)")
    else:
        print("client,nr_visits,continuity")
        print("(continuity = number of distinct caregivers; lower is better)")
    print("-" * 50)
    for row in rows:
        client, nr_visits, continuity = row[0], row[1], row[2]
        if include_cci:
            cci_str = f"{row[3]:.4f}" if row[3] is not None else ""
            bice_str = f"{row[4]:.4f}" if row[4] is not None else ""
            print(f"{client},{nr_visits},{continuity},{cci_str},{bice_str}")
        else:
            print(f"{client},{nr_visits},{continuity}")

    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        with open(args.report, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            if include_cci:
                w.writerow(["client", "nr_visits", "continuity", "cci", "bice_cci"])
                w.writerows([
                    (r[0], r[1], r[2], f"{r[3]:.4f}" if r[3] is not None else "", f"{r[4]:.4f}" if r[4] is not None else "")
                    for r in rows
                ])
            else:
                w.writerow(["client", "nr_visits", "continuity"])
                w.writerows([(r[0], r[1], r[2]) for r in rows])
        print(f"\nWrote {args.report}")

    # Summary: average unique count and average CCI (ours + Bice-Boxerman)
    if rows:
        avg_continuity = sum(r[2] for r in rows) / len(rows)
        print("\n" + "=" * 50)
        print("Summary (continuity = unique caregivers per client)")
        print("=" * 50)
        print(f"  Clients:              {len(rows)}")
        print(f"  Average unique count:  {avg_continuity:.2f}")
        if include_cci and any(r[3] is not None for r in rows):
            cci_vals = [r[3] for r in rows if r[3] is not None]
            avg_cci = sum(cci_vals) / len(cci_vals) if cci_vals else 0.0
            print(f"  Average CCI (ours):    {avg_cci:.4f}  [sum (n_i/N)^2]")
        if include_cci and any(r[4] is not None for r in rows):
            bice_vals = [r[4] for r in rows if r[4] is not None]
            avg_bice = sum(bice_vals) / len(bice_vals) if bice_vals else 0.0
            print(f"  Average CCI (Bice):    {avg_bice:.4f}  [(sum n_i^2 - N) / (N(N-1))]")
        print("=" * 50)

    # Summary from vehicle.id and visits.name
    total_visits = len(visit_vehicle_list)
    vehicle_ids = {v_id for _, v_id in visit_vehicle_list}
    print("\n" + "=" * 50)
    print("Summary (from vehicle.id + visits.name)")
    print("=" * 50)
    print(f"  Total visits:          {total_visits}")
    print(f"  Clients (persons):     {len(rows)}")
    print(f"  Caregivers (vehicles): {n_vehicles}  (distinct vehicle.id; 1 vehicle = 1 caregiver)")
    print(f"  Shifts in output:      {n_shifts}  (not used for continuity; continuity = distinct vehicles per client)")
    vehicle_stats: list[tuple[str, int, int]] = []
    for v_id in sorted(vehicle_ids):
        v_assignments = [(vid, c) for vid, c in visit_vehicle_list if c == v_id]
        if visit_to_person_map is not None:
            v_persons = {visit_to_person_map.get(vid, vid) for vid, _ in v_assignments}
        else:
            v_clients = {visit_to_client.get(vid, vid) for vid, _ in v_assignments}
            v_persons = {visit_name_client_to_person(c) for c in v_clients}
        vehicle_stats.append((v_id, len(v_assignments), len(v_persons)))
    print("\n  Per vehicle (vehicle_id, visits, clients):")
    for v_id, n_visits, n_clients in vehicle_stats:
        print(f"    {v_id}: {n_visits} visits, {n_clients} clients")

    return 0


if __name__ == "__main__":
    sys.exit(main())
