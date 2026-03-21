#!/usr/bin/env python3
"""
Submit continuity-focused campaign variants without waiting for completion.

Creates and submits multiple variants with different continuity strategies:
- Baseline (no continuity constraints)
- Pool size 5 with high continuity weight
- Pool size 7 with balanced weights
- Pool size 8 with preferred vehicles
- Pool size 10 with continuity-heavy profile

All variants use PT3H termination (already configured in input file).
Returns immediately with route plan IDs stored in manifest.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# Ensure prints flush immediately
import builtins
_print = builtins.print
def print(*args, **kwargs):
    kwargs.setdefault('flush', True)
    _print(*args, **kwargs)


def submit_variant(
    input_file: Path,
    variant_name: str,
    strategy: str,
    algorithm: str,
    hypothesis: str,
    configuration_id: str = "",
    script_path: Path = None,
) -> dict:
    """Submit a variant and return route plan ID immediately (no wait)."""
    if script_path is None:
        # Find submit_to_timefold.py - try multiple strategies
        current_file = Path(__file__).resolve()
        
        # Strategy 1: Find be-agent-service root by looking for recurring-visits/scripts/
        script_path = None
        search_path = current_file.parent
        max_depth = 10
        depth = 0
        while depth < max_depth and search_path != search_path.parent:
            candidate = search_path / "recurring-visits" / "scripts" / "submit_to_timefold.py"
            if candidate.exists():
                script_path = candidate
                break
            search_path = search_path.parent
            depth += 1
        
        # Strategy 2: Use absolute path from known location
        if script_path is None or not script_path.exists():
            # Try from /Users/bjornevers_MacPro/HomeCare/be-agent-service
            known_base = Path("/Users/bjornevers_MacPro/HomeCare/be-agent-service")
            candidate = known_base / "recurring-visits" / "scripts" / "submit_to_timefold.py"
            if candidate.exists():
                script_path = candidate
        
        # Strategy 3: Try relative to current working directory
        if script_path is None or not script_path.exists():
            candidate = Path("recurring-visits/scripts/submit_to_timefold.py")
            if candidate.exists():
                script_path = candidate.resolve()
        
        if script_path is None or not script_path.exists():
            raise FileNotFoundError(
                f"Could not find submit_to_timefold.py. "
                f"Tried searching from {current_file.parent} up to {search_path}. "
                f"Please provide --script-path argument."
            )
    
    cmd = [
        sys.executable,
        str(script_path),
        "solve",
        str(input_file),
        "--configuration-id", configuration_id,
        "--strategy", strategy,
        "--algorithm", algorithm,
        "--hypothesis", hypothesis,
        "--dataset", "huddinge-v3-19",
        "--batch", datetime.now().strftime("%d-%b").lower(),
    ]
    
    print(f"\n📤 Submitting {variant_name}...")
    print(f"   Strategy: {strategy}")
    print(f"   Algorithm: {algorithm}")
    print(f"   Command: {' '.join(cmd)}")
    
    try:
        # Run submit command and capture output
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=60,  # 60 second timeout for submission
        )
        
        if result.returncode != 0:
            print(f"   ❌ Submission failed:")
            print(f"   {result.stderr}")
            return {
                "variant_name": variant_name,
                "status": "failed",
                "error": result.stderr[:500],
                "route_plan_id": None,
            }
        
        # Parse route plan ID from output
        # Expected format: "plan_id: <uuid>" or similar
        output_lines = result.stdout.split("\n")
        route_plan_id = None
        
        for line in output_lines:
            if "plan_id:" in line.lower() or "route_plan_id:" in line.lower():
                # Extract UUID
                parts = line.split(":")
                if len(parts) >= 2:
                    route_plan_id = parts[-1].strip()
                    break
            # Also check for UUID pattern directly
            if len(line.strip()) == 36 and "-" in line:
                route_plan_id = line.strip()
                break
        
        if not route_plan_id:
            # Try to extract from stderr or full output
            full_output = result.stdout + result.stderr
            import re
            uuid_pattern = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
            matches = re.findall(uuid_pattern, full_output, re.IGNORECASE)
            if matches:
                route_plan_id = matches[0]
        
        if route_plan_id:
            print(f"   ✅ Submitted successfully")
            print(f"   Route Plan ID: {route_plan_id}")
            return {
                "variant_name": variant_name,
                "status": "submitted",
                "route_plan_id": route_plan_id,
                "strategy": strategy,
                "algorithm": algorithm,
                "hypothesis": hypothesis,
                "submitted_at": datetime.now().isoformat(),
            }
        else:
            print(f"   ⚠️  Submission may have succeeded but route plan ID not found")
            print(f"   Output: {result.stdout[:500]}")
            return {
                "variant_name": variant_name,
                "status": "unknown",
                "route_plan_id": None,
                "output": result.stdout[:500],
            }
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ Submission timeout (60s)")
        return {
            "variant_name": variant_name,
            "status": "timeout",
            "route_plan_id": None,
        }
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return {
            "variant_name": variant_name,
            "status": "error",
            "error": str(e),
            "route_plan_id": None,
        }


def main():
    parser = argparse.ArgumentParser(
        description="Submit continuity campaign variants without waiting"
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Input JSON file (already has PT3H termination configured)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory for manifest (default: same as input file directory)",
    )
    parser.add_argument(
        "--script-path",
        type=Path,
        default=None,
        help="Path to submit_to_timefold.py script (auto-detected if not provided)",
    )
    
    args = parser.parse_args()
    
    input_file = args.input_file.resolve()
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        return 1
    
    # Determine output directory
    if args.output_dir:
        output_dir = Path(args.output_dir).resolve()
    else:
        output_dir = input_file.parent
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define campaign variants
    variants = [
        {
            "variant_name": "baseline",
            "strategy": "baseline",
            "algorithm": "baseline-no-continuity",
            "hypothesis": "Baseline solve without continuity constraints for comparison",
            "configuration_id": "",  # Use tenant default
        },
        {
            "variant_name": "pool5_high_continuity",
            "strategy": "pool5-required-vehicles",
            "algorithm": "continuity-pool5-high-weight",
            "hypothesis": "Pool size 5 with requiredVehicles constraint (high continuity priority)",
            "configuration_id": "",  # Use tenant default
        },
        {
            "variant_name": "pool7_balanced",
            "strategy": "pool7-required-vehicles",
            "algorithm": "continuity-pool7-balanced",
            "hypothesis": "Pool size 7 with requiredVehicles constraint (balanced continuity vs coverage)",
            "configuration_id": "",  # Use tenant default
        },
        {
            "variant_name": "pool8_preferred",
            "strategy": "pool8-preferred-vehicles",
            "algorithm": "continuity-pool8-preferred",
            "hypothesis": "Pool size 8 with preferredVehicles soft constraint (flexible continuity)",
            "configuration_id": "",  # Use tenant default
        },
        {
            "variant_name": "pool10_continuity_heavy",
            "strategy": "pool10-required-vehicles",
            "algorithm": "continuity-pool10-heavy",
            "hypothesis": "Pool size 10 with requiredVehicles constraint (conservative continuity)",
            "configuration_id": "",  # Use tenant default
        },
    ]
    
    print("=" * 60)
    print("CONTINUITY CAMPAIGN - IMMEDIATE SUBMISSION")
    print("=" * 60)
    print(f"\nInput file: {input_file}")
    print(f"Output directory: {output_dir}")
    print(f"\nVariants to submit: {len(variants)}")
    print("\nVariants:")
    for v in variants:
        print(f"  - {v['variant_name']}: {v['strategy']}")
    print("\n" + "=" * 60)
    
    # Submit all variants
    results = []
    for variant in variants:
        result = submit_variant(
            input_file=input_file,
            variant_name=variant["variant_name"],
            strategy=variant["strategy"],
            algorithm=variant["algorithm"],
            hypothesis=variant["hypothesis"],
            configuration_id=variant["configuration_id"],
            script_path=args.script_path,
        )
        results.append(result)
    
    # Create manifest
    manifest = {
        "campaign": "continuity-focused-v3-19",
        "input_file": str(input_file),
        "submitted_at": datetime.now().isoformat(),
        "termination": "PT3H",
        "variants": results,
    }
    
    manifest_file = output_dir / "campaign_manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Create human-readable summary
    summary_file = output_dir / "campaign_summary.md"
    with open(summary_file, "w") as f:
        f.write("# Continuity Campaign Summary\n\n")
        f.write(f"**Campaign**: continuity-focused-v3-19\n")
        f.write(f"**Input File**: `{input_file.name}`\n")
        f.write(f"**Submitted**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Termination**: PT3H (3 hours max)\n\n")
        f.write("## Variants\n\n")
        f.write("| Variant | Strategy | Route Plan ID | Status |\n")
        f.write("|---------|----------|---------------|--------|\n")
        
        for result in results:
            route_id = result.get("route_plan_id") or "N/A"
            status = result.get("status", "unknown")
            variant_name = result.get("variant_name", "unknown")
            strategy = result.get("strategy", "N/A")
            f.write(f"| {variant_name} | {strategy} | `{route_id}` | {status} |\n")
        
        f.write("\n## Fetch Commands\n\n")
        f.write("To fetch solutions after completion:\n\n")
        f.write("```bash\n")
        for result in results:
            route_id = result.get("route_plan_id")
            if route_id:
                variant_name = result.get("variant_name", "unknown")
                f.write(f"# {variant_name}\n")
                f.write(f"python3 recurring-visits/scripts/submit_to_timefold.py fetch {route_id} \\\n")
                f.write(f"  --save {output_dir}/{variant_name}_output.json\n\n")
        f.write("```\n")
    
    # Print summary
    print("\n" + "=" * 60)
    print("CAMPAIGN SUBMISSION COMPLETE")
    print("=" * 60)
    print(f"\n✅ Submitted {len([r for r in results if r.get('route_plan_id')])} variants")
    print(f"❌ Failed {len([r for r in results if not r.get('route_plan_id')])} variants")
    print(f"\n📄 Manifest: {manifest_file}")
    print(f"📄 Summary: {summary_file}")
    print("\nRoute Plan IDs:")
    for result in results:
        route_id = result.get("route_plan_id")
        if route_id:
            print(f"  - {result.get('variant_name', 'unknown')}: {route_id}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Monitor solve progress:")
    print("   python3 recurring-visits/scripts/submit_to_timefold.py fetch <route_plan_id>")
    print("\n2. After completion, fetch all solutions:")
    print(f"   See {summary_file} for fetch commands")
    print("\n3. Analyze results:")
    print("   python3 recurring-visits/scripts/continuity_report.py --input <input> --output <output>")
    print("   python3 recurring-visits/scripts/metrics.py <output.json>")
    print("\n" + "=" * 60)
    
    return 0 if all(r.get("route_plan_id") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
