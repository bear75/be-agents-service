#!/usr/bin/env python3
"""
Apply a roster file (client → vehicle IDs) to base FSR input.

Sets preferredVehicles or requiredVehicles on each visit from the roster, using
KOLADA person derived from visit name (same logic as continuity_report.py /
build_continuity_pools.py). Used by the ESS→FSR orchestration layer; roster
can come from ESS (future), manual edit, or stub from fsr_output_to_roster.py.

Usage:
  python apply_roster_to_fsr_input.py --input base_input.json --roster roster.json \\
    --out patched_input.json [--max-per-client 10] [--use-required]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from build_continuity_pools import (
    load_visit_to_person,
    patch_fsr_input_with_pools,
)

ROSTER_RESERVED_KEYS = frozenset({"source", "_meta", "assignments"})


def load_roster(roster_path: Path) -> dict[str, list[str]]:
    """
    Load roster JSON and return client_id → list of vehicle IDs.
    Supports (1) top-level "assignments": { client_id: [vehicle_ids] }, or
    (2) flat object with client_id keys and optional metadata (source, _meta).
    """
    with open(roster_path, encoding="utf-8") as f:
        data = json.load(f)

    if "assignments" in data and isinstance(data["assignments"], dict):
        raw = data["assignments"]
    else:
        raw = {k: v for k, v in data.items() if k not in ROSTER_RESERVED_KEYS and isinstance(v, list)}

    out: dict[str, list[str]] = {}
    for client_id, vehicle_list in raw.items():
        if not isinstance(client_id, str):
            continue
        ids = [str(x) for x in vehicle_list if x]
        out[client_id] = ids
    return out


def cap_roster(roster: dict[str, list[str]], max_per_client: int) -> dict[str, list[str]]:
    """Cap each client's vehicle list to max_per_client (in place)."""
    return {client: vehicles[:max_per_client] for client, vehicles in roster.items()}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply roster (client → vehicle IDs) to FSR input as preferred/required vehicles",
    )
    parser.add_argument("--input", type=Path, required=True, help="Base FSR input JSON (with modelInput)")
    parser.add_argument("--roster", type=Path, required=True, help="Roster JSON (client_id → list of vehicle IDs)")
    parser.add_argument("--out", type=Path, required=True, help="Output patched FSR input path")
    parser.add_argument(
        "--max-per-client",
        type=int,
        default=10,
        help="Max vehicles per client from roster (default 10)",
    )
    parser.add_argument(
        "--use-required",
        action="store_true",
        help="Set requiredVehicles (hard); default is preferredVehicles (soft)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not args.roster.exists():
        print(f"Error: roster not found: {args.roster}", file=sys.stderr)
        return 1

    roster = load_roster(args.roster)
    roster = cap_roster(roster, args.max_per_client)
    if not roster:
        print("Error: roster has no client assignments", file=sys.stderr)
        return 1

    visit_to_person = load_visit_to_person(args.input)
    use_preferred = not args.use_required

    patch_fsr_input_with_pools(
        args.input,
        roster,
        visit_to_person,
        args.out,
        use_preferred=use_preferred,
    )
    kind = "requiredVehicles" if args.use_required else "preferredVehicles"
    print(f"Patched FSR input written to {args.out} ({kind}, {len(roster)} clients, max {args.max_per_client} per client)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
