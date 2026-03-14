#!/usr/bin/env python3
"""
Generate a continuity improvement patch for Timefold FSR.

Takes an FSR output JSON and continuity analysis CSV, then generates a patch
that locks visits for high-continuity clients to their most common employees.

Strategy:
1. Identify clients with continuity above threshold (default: >5 employees)
2. For each high-continuity client:
   - Find which employees served them
   - Lock all their visits to the 2-3 most common employees
3. Generate patch JSON that can be submitted via from-patch

Usage:
  python3 generate_continuity_patch_fsr.py \\
    OUTPUT_JSON \\
    CONTINUITY_CSV \\
    -o patch.json \\
    --max-continuity 5

Example:
  python3 generate_continuity_patch_fsr.py \\
    output_FIXED/4cdfce61_output.json \\
    continuity_baseline.csv \\
    -o continuity_patch.json \\
    --max-continuity 5
"""

import argparse
import csv
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


def visit_name_to_client(name: str) -> str:
    """Extract client ID from visit name. E.g. 'H015 Morgon Dag...' -> 'H015'"""
    if not name:
        return ""
    # Match pattern like "H015" at start
    match = re.match(r"^(H\d+)", name)
    if match:
        return match.group(1)
    # Fallback: take first part before space
    return name.split()[0] if " " in name else name


def analyze_client_assignments(output_data: dict) -> Dict[str, Dict[str, List[str]]]:
    """
    Analyze which employees (vehicles) visited which clients.

    Returns: {client_id: {vehicle_id: [visit_ids]}}
    """
    client_assignments: Dict[str, Dict[str, List[str]]] = defaultdict(lambda: defaultdict(list))

    model_output = output_data.get("modelOutput", {})

    for vehicle in model_output.get("vehicles", []):
        vehicle_id = vehicle.get("id")
        if not vehicle_id:
            continue

        for shift in vehicle.get("shifts", []):
            for item in shift.get("itinerary", []):
                if not isinstance(item, dict) or item.get("kind") != "VISIT":
                    continue

                visit_id = item.get("visitId")
                visit_name = item.get("visitName", "")

                if not visit_id:
                    continue

                client_id = visit_name_to_client(visit_name)
                if client_id:
                    client_assignments[client_id][vehicle_id].append(visit_id)

    return client_assignments


def load_continuity_analysis(csv_path: Path) -> Dict[str, int]:
    """Load continuity CSV and return {client_id: continuity_count}"""
    continuity_map: Dict[str, int] = {}

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            client_id = row.get('client', '')
            continuity_str = row.get('continuity', '0')
            try:
                continuity_map[client_id] = int(continuity_str)
            except ValueError:
                continue

    return continuity_map


def select_primary_employees(
    vehicle_visits: Dict[str, List[str]],
    max_employees: int = 2
) -> List[str]:
    """
    Select the top N employees based on number of visits.

    Args:
        vehicle_visits: {vehicle_id: [visit_ids]}
        max_employees: Maximum number of employees to keep

    Returns:
        List of vehicle_ids to lock visits to
    """
    # Sort by number of visits (descending)
    sorted_vehicles = sorted(
        vehicle_visits.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )

    # Take top N
    return [vid for vid, _ in sorted_vehicles[:max_employees]]


def build_patch(
    output_data: dict,
    continuity_csv_path: Path,
    max_continuity: int = 5,
    target_employees: int = 2
) -> dict:
    """
    Build a from-patch payload that locks high-continuity clients to fewer employees.

    Args:
        output_data: FSR output JSON
        continuity_csv_path: Path to continuity analysis CSV
        max_continuity: Only patch clients with continuity > this value
        target_employees: Target number of employees per client (default: 2)

    Returns:
        Patch JSON payload
    """
    # Load continuity analysis
    continuity_map = load_continuity_analysis(continuity_csv_path)

    # Analyze client assignments
    client_assignments = analyze_client_assignments(output_data)

    # Find route plan ID
    route_plan_id = output_data.get("routePlanId", "")

    # Build patch operations
    patch_operations = []
    patched_clients = []

    for client_id, vehicle_visits in client_assignments.items():
        continuity = continuity_map.get(client_id, 0)

        # Skip if continuity is acceptable
        if continuity <= max_continuity:
            continue

        # Select primary employees
        primary_vehicles = select_primary_employees(vehicle_visits, target_employees)

        if not primary_vehicles:
            continue

        # Assign all visits to primary employee (or distribute among top 2)
        all_visits = []
        for vid in vehicle_visits:
            all_visits.extend(vehicle_visits[vid])

        # Lock visits to primary vehicle(s)
        # Strategy: assign all to most common employee for simplicity
        primary_vehicle = primary_vehicles[0]

        for visit_id in all_visits:
            patch_operations.append({
                "op": "replace",
                "path": f"/visits/[id={visit_id}]/vehicleId",
                "value": primary_vehicle
            })

        patched_clients.append({
            "client_id": client_id,
            "original_continuity": continuity,
            "target_employees": len(primary_vehicles),
            "visits_locked": len(all_visits),
            "primary_vehicles": primary_vehicles
        })

    # Build patch payload
    patch = {
        "from": {
            "routePlanId": route_plan_id
        },
        "patch": patch_operations
    }

    return patch, patched_clients


def main():
    parser = argparse.ArgumentParser(
        description="Generate continuity improvement patch for Timefold FSR"
    )
    parser.add_argument(
        "output_json",
        type=Path,
        help="FSR output JSON file"
    )
    parser.add_argument(
        "continuity_csv",
        type=Path,
        help="Continuity analysis CSV file"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        required=True,
        help="Output patch JSON file"
    )
    parser.add_argument(
        "--max-continuity",
        type=int,
        default=5,
        help="Only patch clients with continuity > this value (default: 5)"
    )
    parser.add_argument(
        "--target-employees",
        type=int,
        default=2,
        help="Target number of employees per client (default: 2)"
    )

    args = parser.parse_args()

    # Load output JSON
    if not args.output_json.exists():
        print(f"Error: Output JSON not found: {args.output_json}", file=sys.stderr)
        sys.exit(1)

    with open(args.output_json, 'r', encoding='utf-8') as f:
        output_data = json.load(f)

    # Load continuity CSV
    if not args.continuity_csv.exists():
        print(f"Error: Continuity CSV not found: {args.continuity_csv}", file=sys.stderr)
        sys.exit(1)

    # Build patch
    print(f"Building continuity patch...")
    print(f"  Max continuity threshold: {args.max_continuity}")
    print(f"  Target employees per client: {args.target_employees}")

    patch, patched_clients = build_patch(
        output_data,
        args.continuity_csv,
        max_continuity=args.max_continuity,
        target_employees=args.target_employees
    )

    # Save patch
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(patch, f, indent=2)

    # Print summary
    print(f"\n✅ Patch generated: {args.output}")
    print(f"\nPatched {len(patched_clients)} high-continuity clients:")
    print(f"{'Client':<10} {'Original':<12} {'Target':<10} {'Visits':<10} {'Primary Employee':<20}")
    print("-" * 75)

    for client_info in sorted(patched_clients, key=lambda x: x['original_continuity'], reverse=True)[:20]:
        print(
            f"{client_info['client_id']:<10} "
            f"{client_info['original_continuity']:<12} "
            f"{client_info['target_employees']:<10} "
            f"{client_info['visits_locked']:<10} "
            f"{', '.join(client_info['primary_vehicles'][:2]):<20}"
        )

    if len(patched_clients) > 20:
        print(f"... and {len(patched_clients) - 20} more clients")

    print(f"\nTotal patch operations: {len(patch['patch'])}")
    print(f"\nNext step: Submit patch with from-patch command")


if __name__ == "__main__":
    main()
