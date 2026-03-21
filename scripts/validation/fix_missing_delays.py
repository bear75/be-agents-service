#!/usr/bin/env python3
"""
Fix visit dependencies missing minDelay in Timefold FSR input JSON.

Removes dependencies that are missing minDelay (invalid) or adds a default delay.
Also converts P1DT10H format to PT34H (time-only) for Timefold compatibility.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Any


def convert_duration_to_time_only(duration: str) -> str:
    """
    Convert ISO 8601 duration with days (P1DT10H) to time-only (PT34H).
    
    Examples:
    - P1DT10H -> PT34H (1 day = 24h, so 24+10=34h)
    - P1DT9H -> PT33H
    - P1DT20H21M -> PT44H21M
    - PT10H -> PT10H (already time-only, no change)
    """
    if not duration or not isinstance(duration, str):
        return duration
    
    # Already time-only format
    if duration.startswith("PT"):
        return duration
    
    # Parse period format (P[n]DT[n]H[n]M)
    # P1DT10H -> days=1, hours=10, minutes=0
    match = re.match(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?", duration)
    if not match:
        return duration
    
    days = int(match.group(1) or 0)
    hours = int(match.group(2) or 0)
    minutes = int(match.group(3) or 0)
    
    # Convert days to hours
    total_hours = days * 24 + hours
    
    # Build PT format
    parts = []
    if total_hours > 0:
        parts.append(f"{total_hours}H")
    if minutes > 0:
        parts.append(f"{minutes}M")
    
    if not parts:
        return "PT0M"
    
    return "PT" + "".join(parts)


def fix_dependencies(model_input: Dict[str, Any], remove_invalid: bool = True) -> tuple[int, int]:
    """
    Fix visit dependencies missing minDelay.
    
    Returns: (fixed_count, removed_count)
    """
    fixed = 0
    removed = 0
    
    # Check standalone visits
    for visit in model_input.get("visits", []):
        deps = visit.get("visitDependencies", [])
        if not deps:
            continue
        
        valid_deps = []
        for dep in deps:
            delay = dep.get("minDelay")
            if not delay:
                if remove_invalid:
                    removed += 1
                    continue
                else:
                    # Add default delay (PT0M for same-day, PT18H for spread)
                    dep["minDelay"] = "PT18H"
                    fixed += 1
            else:
                # Convert P1DT10H format to PT34H if needed
                converted = convert_duration_to_time_only(delay)
                if converted != delay:
                    dep["minDelay"] = converted
                    fixed += 1
            valid_deps.append(dep)
        
        if len(valid_deps) != len(deps):
            visit["visitDependencies"] = valid_deps if valid_deps else None
    
    # Check visits in groups
    for group in model_input.get("visitGroups", []):
        for visit in group.get("visits", []):
            deps = visit.get("visitDependencies", [])
            if not deps:
                continue
            
            valid_deps = []
            for dep in deps:
                delay = dep.get("minDelay")
                if not delay:
                    if remove_invalid:
                        removed += 1
                        continue
                    else:
                        dep["minDelay"] = "PT18H"
                        fixed += 1
                else:
                    # Convert P1DT10H format to PT34H if needed
                    converted = convert_duration_to_time_only(delay)
                    if converted != delay:
                        dep["minDelay"] = converted
                        fixed += 1
                valid_deps.append(dep)
            
            if len(valid_deps) != len(deps):
                visit["visitDependencies"] = valid_deps if valid_deps else None
    
    return fixed, removed


def main():
    parser = argparse.ArgumentParser(
        description="Fix visit dependencies missing minDelay in Timefold FSR input JSON"
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to input JSON file",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output file path (default: input file with _fixed suffix)",
    )
    parser.add_argument(
        "--add-default",
        action="store_true",
        help="Add default delay (PT18H) instead of removing invalid dependencies",
    )
    args = parser.parse_args()
    
    if not args.input_json.exists():
        print(f"Error: File not found: {args.input_json}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(args.input_json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Handle both wrapped and unwrapped JSON
    model_input = payload.get("modelInput") or payload
    if "modelInput" in payload:
        payload["modelInput"] = model_input
    
    # Fix dependencies
    fixed, removed = fix_dependencies(model_input, remove_invalid=not args.add_default)
    
    # Determine output path
    if args.output:
        output_path = args.output
    else:
        output_path = args.input_json.parent / f"{args.input_json.stem}_fixed{args.input_json.suffix}"
    
    # Save fixed file
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Report results
    action = "Added default delay to" if args.add_default else "Removed"
    print(f"✅ {action} {fixed + removed} invalid dependency/dependencies")
    if fixed > 0:
        print(f"   - Fixed: {fixed}")
    if removed > 0:
        print(f"   - Removed: {removed}")
    print(f"✅ Fixed file saved to: {output_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
