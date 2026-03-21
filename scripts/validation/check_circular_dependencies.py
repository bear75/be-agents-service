#!/usr/bin/env python3
"""
Check for circular dependencies in Timefold FSR input JSON.

Detects cycles in visitDependencies that could cause Timefold shadow variable loops.
"""

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set, Tuple


def find_cycles(visit_dependencies: List[Dict]) -> List[List[str]]:
    """
    Find all circular dependencies in visitDependencies.
    
    Returns list of cycles, where each cycle is a list of visit IDs.
    """
    # Build dependency graph: visit_id -> preceding_visit_id
    graph: Dict[str, str] = {}
    for dep in visit_dependencies:
        visit_id = dep.get("visitId")
        preceding_id = dep.get("precedingVisitId")
        if visit_id and preceding_id:
            graph[visit_id] = preceding_id
    
    cycles: List[List[str]] = []
    visited: Set[str] = set()
    
    def dfs(visit_id: str, path: List[str]) -> None:
        """Depth-first search to find cycles."""
        if visit_id in visited:
            return
        
        if visit_id in path:
            # Found a cycle
            cycle_start = path.index(visit_id)
            cycle = path[cycle_start:] + [visit_id]
            cycles.append(cycle)
            return
        
        if visit_id not in graph:
            visited.add(visit_id)
            return
        
        path.append(visit_id)
        dfs(graph[visit_id], path)
        path.pop()
        visited.add(visit_id)
    
    for visit_id in graph:
        if visit_id not in visited:
            dfs(visit_id, [])
    
    return cycles


def check_visit_structure(model_input: Dict) -> List[str]:
    """
    Check that standalone visits don't have group-related properties.
    
    Returns list of warnings/issues found.
    """
    issues: List[str] = []
    
    standalone_visits = model_input.get("visits", [])
    visit_groups = model_input.get("visitGroups", [])
    
    # Collect all visit IDs that are in groups
    group_visit_ids: Set[str] = set()
    for group in visit_groups:
        for visit in group.get("visits", []):
            visit_id = visit.get("id")
            if visit_id:
                group_visit_ids.add(visit_id)
    
    # Check standalone visits
    for visit in standalone_visits:
        visit_id = visit.get("id", "")
        
        # Check if visit has visitGroup property (should not)
        if "visitGroup" in visit:
            issues.append(f"Standalone visit {visit_id} has 'visitGroup' property (should be omitted)")
        
        # Check if visit ID conflicts with group visit
        if visit_id in group_visit_ids:
            issues.append(f"Visit {visit_id} appears in both standalone visits and visit groups")
    
    return issues


def main():
    parser = argparse.ArgumentParser(
        description="Check for circular dependencies in Timefold FSR input JSON"
    )
    parser.add_argument(
        "input_json",
        type=Path,
        help="Path to Timefold FSR input JSON file",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show detailed cycle information",
    )
    args = parser.parse_args()
    
    if not args.input_json.exists():
        print(f"Error: File not found: {args.input_json}", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(args.input_json, "r", encoding="utf-8") as f:
            payload = json.load(f)
        # Handle both wrapped (modelInput) and unwrapped JSON
        model_input = payload.get("modelInput") or payload
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Check for circular dependencies
    visit_dependencies = model_input.get("visitDependencies", [])
    cycles = find_cycles(visit_dependencies)
    
    # Check visit structure
    structure_issues = check_visit_structure(model_input)
    
    # Report results
    has_errors = False
    
    if cycles:
        has_errors = True
        print(f"❌ Found {len(cycles)} circular dependency cycle(s):\n", file=sys.stderr)
        for i, cycle in enumerate(cycles, 1):
            cycle_str = " -> ".join(cycle)
            print(f"  Cycle {i}: {cycle_str}", file=sys.stderr)
            if args.verbose:
                # Show dependency details
                for j in range(len(cycle) - 1):
                    visit_id = cycle[j]
                    preceding_id = cycle[j + 1]
                    dep = next(
                        (d for d in visit_dependencies 
                         if d.get("visitId") == visit_id and d.get("precedingVisitId") == preceding_id),
                        None
                    )
                    if dep:
                        delay = dep.get("minDelay", "N/A")
                        print(f"    {visit_id} depends on {preceding_id} (delay: {delay})", file=sys.stderr)
    else:
        print("✅ No circular dependencies found")
    
    if structure_issues:
        has_errors = True
        print(f"\n⚠️  Found {len(structure_issues)} visit structure issue(s):\n", file=sys.stderr)
        for issue in structure_issues:
            print(f"  - {issue}", file=sys.stderr)
    else:
        print("✅ Visit structure is valid")
    
    # Summary
    total_deps = len(visit_dependencies)
    standalone_visits = len(model_input.get("visits", []))
    visit_groups = len(model_input.get("visitGroups", []))
    
    print(f"\nSummary:")
    print(f"  - Total dependencies: {total_deps}")
    print(f"  - Standalone visits: {standalone_visits}")
    print(f"  - Visit groups: {visit_groups}")
    
    if has_errors:
        print("\n❌ Input JSON has issues that may cause Timefold errors", file=sys.stderr)
        sys.exit(1)
    else:
        print("\n✅ Input JSON appears valid")
        sys.exit(0)


if __name__ == "__main__":
    main()
