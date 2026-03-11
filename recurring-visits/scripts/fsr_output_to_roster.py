#!/usr/bin/env python3
"""
Build roster JSON (client → top-K vehicle IDs) from first-run FSR output.

Reuses logic from build_continuity_pools first-run: for each person (KOLADA
client from visit name), count visits per vehicle and take top max_per_client
vehicles. Output is roster format consumable by apply_roster_to_fsr_input.py.

Usage:
  python fsr_output_to_roster.py --output fsr_output.json --input fsr_input.json \\
    --out roster.json [--max-per-client 10]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_scripts_dir = Path(__file__).resolve().parent
if str(_scripts_dir) not in sys.path:
    sys.path.insert(0, str(_scripts_dir))

from build_continuity_pools import pools_from_first_run


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert FSR output to roster JSON (client → top-K vehicles by visit count)",
    )
    parser.add_argument("--output", type=Path, required=True, help="FSR output JSON (visit → vehicle assignments)")
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="FSR input JSON (for visit → client via visit name)",
    )
    parser.add_argument("--out", type=Path, required=True, help="Output roster JSON path")
    parser.add_argument(
        "--max-per-client",
        type=int,
        default=10,
        help="Max vehicles per client (default 10)",
    )
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: input not found: {args.input}", file=sys.stderr)
        return 1
    if not args.output.exists():
        print(f"Error: output not found: {args.output}", file=sys.stderr)
        return 1

    pools = pools_from_first_run(
        args.input,
        args.output,
        max_per_client=args.max_per_client,
    )
    if not pools:
        print("Warning: no client assignments from FSR output", file=sys.stderr)

    payload = {
        "source": "stub",
        "assignments": pools,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"Wrote roster for {len(pools)} clients to {args.out} (source=stub, max_per_client={args.max_per_client})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
