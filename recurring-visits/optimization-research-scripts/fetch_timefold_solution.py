#!/usr/bin/env python3
"""
Fetch a Timefold FSR solution by route plan (dataset) ID.
Uses: GET .../v1/route-plans/<ID> -> solution (modelOutput, metadata, etc.)
      GET .../v1/route-plans/<ID>/input -> input dataset (modelInput)
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
import requests

TIMEFOLD_BASE = "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans"

def fetch_solution(route_plan_id: str, api_key: str) -> dict:
    """GET route plan by ID. Returns full response JSON (metadata, modelOutput, etc.)."""
    if not api_key:
        raise RuntimeError("TIMEFOLD_API_KEY environment variable is required")
    
    url = f"{TIMEFOLD_BASE}/{route_plan_id}"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}
    r = requests.get(url, headers=headers, timeout=60)
    
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    
    return r.json()

def fetch_input(route_plan_id: str, api_key: str) -> dict:
    """GET route plan input by ID. Returns input dataset (RoutePlanInput / modelInput)."""
    if not api_key:
        raise RuntimeError("TIMEFOLD_API_KEY environment variable is required")
    
    url = f"{TIMEFOLD_BASE}/{route_plan_id}/input"
    headers = {"Accept": "application/json", "X-API-KEY": api_key}
    r = requests.get(url, headers=headers, timeout=60)
    
    if r.status_code != 200:
        raise RuntimeError(f"HTTP {r.status_code}: {r.text[:800]}")
    
    return r.json()

def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch Timefold FSR solution by route plan ID")
    
    parser.add_argument("route_plan_id", help="Route plan (dataset) ID")
    parser.add_argument("--save", type=Path, default=None, help="Save full response JSON to this path")
    parser.add_argument("--input", type=Path, default=None, help="Save input dataset to this path")  
    parser.add_argument("--api-key", default=None, help="API key (default: TIMEFOLD_API_KEY env)")
    
    args = parser.parse_args()
    
    api_key = args.api_key or os.environ.get("TIMEFOLD_API_KEY", "")
    if not api_key:
        print("Error: Set TIMEFOLD_API_KEY or pass --api-key", file=sys.stderr)
        return 1
    
    try:
        # Fetch solution
        data = fetch_solution(args.route_plan_id.strip(), api_key)
        
        # Print summary
        meta = data.get("metadata") or data.get("run") or {}
        status = (meta.get("solverStatus") or data.get("solverStatus") or "?").upper()
        score = meta.get("score", "?")
        name = meta.get("name") or data.get("name") or "—"
        
        out = data.get("modelOutput") or {}
        n_vehicles = len(out.get("vehicles", []))
        unassigned = out.get("unassignedVisits") or []
        n_unassigned = len(unassigned)
        
        print(f"Route plan ID: {args.route_plan_id}")
        print(f"Name: {name}")
        print(f"Solver status: {status}")
        print(f"Score: {score}")
        print(f"Vehicles: {n_vehicles}")
        print(f"Unassigned: {n_unassigned}")
        
        # Save solution if requested
        if args.save:
            args.save.parent.mkdir(parents=True, exist_ok=True)
            with open(args.save, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"Saved solution: {args.save}")
        
        # Fetch and save input if requested
        if args.input:
            input_data = fetch_input(args.route_plan_id.strip(), api_key)
            
            args.input.parent.mkdir(parents=True, exist_ok=True)
            with open(args.input, "w", encoding="utf-8") as f:
                json.dump(input_data, f, indent=2, ensure_ascii=False)
            print(f"Saved input: {args.input}")
            
            # Print input summary
            model_input = input_data.get("modelInput", input_data)
            n_visits = len(model_input.get("visits", []))
            n_vehicles_input = len(model_input.get("vehicles", []))
            print(f"Input: {n_visits} visits, {n_vehicles_input} vehicles")
        
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())