#!/usr/bin/env python3
"""
Submit Conservative Capacity Test (+8 vehicles)
Parallel strategy to the +15 vehicle test
"""

import json
import os
import requests
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def submit_conservative_test():
    """Submit the conservative capacity test"""
    
    print("🚀 **SUBMITTING CONSERVATIVE CAPACITY TEST**")
    print("Parallel strategy: +8 vehicles (vs +15 in current test)")
    print("="*60)
    
    # Load conservative input
    with open('conservative_capacity_input.json', 'r') as f:
        conservative_input = json.load(f)
    
    vehicles = conservative_input.get('vehicles', [])
    visits = conservative_input.get('visits', [])
    
    print(f"Conservative configuration:")
    print(f"  - Vehicles: {len(vehicles)}")
    print(f"  - Visits: {len(visits)}")
    print(f"  - Strategy: Moderate capacity for efficiency balance")
    
    # Prepare submission
    submission_payload = {"modelInput": conservative_input}
    
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"\n🌐 Submitting conservative test...")
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=submission_payload,
            timeout=120
        )
        
        if response.status_code in [200, 201, 202]:
            result = response.json()
            run_id = result.get('id', 'unknown')
            solver_status = result.get('solverStatus', 'UNKNOWN')
            
            print(f"✅ **CONSERVATIVE TEST SUBMITTED!**")
            print(f"Run ID: {run_id}")
            print(f"Status: {solver_status}")
            
            # Save run info for tracking
            conservative_run_info = {
                'run_id': run_id,
                'submission_time': datetime.now().isoformat(),
                'job_name': 'Conservative Capacity Test (+8 vehicles)',
                'vehicles': len(vehicles),
                'visits': len(visits),
                'strategy': 'moderate_capacity_increase',
                'baseline_run': '41ce610c-bd67-47b8-9e62-7820f87ffcdd',
                'parallel_to': 'b69e582b-9321-4cfe-be40-92bc27287b5e',
                'expected_improvements': {
                    'vs_baseline': 'Better continuity + unassigned',
                    'vs_strategic': 'Better efficiency with moderate capacity'
                }
            }
            
            with open('conservative_test_run_info.json', 'w') as f:
                json.dump(conservative_run_info, f, indent=2)
            
            print(f"\n📊 **PARALLEL STRATEGY LAUNCHED:**")
            print(f"- Conservative test: {run_id[:8]} (46 vehicles)")
            print(f"- Strategic test: b69e582b (53 vehicles)")
            print(f"- Both will optimize for 4-6 hours")
            print(f"- Can compare results when complete")
            
            return run_id, True
            
        else:
            print(f"❌ **SUBMISSION FAILED**")
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:300]}")
            return None, False
            
    except requests.RequestException as e:
        print(f"❌ **NETWORK ERROR:** {e}")
        return None, False

def main():
    print("🧬 **PARALLEL OPTIMIZATION STRATEGY**")
    print("Launching conservative capacity test alongside strategic test")
    print()
    
    run_id, success = submit_conservative_test()
    
    if success:
        print(f"\n🎯 **PARALLEL CAMPAIGN ACTIVE**")
        print(f"Two strategies now running simultaneously:")
        print(f"1. Strategic (+15 vehicles) - solving unassigned, may hurt efficiency")
        print(f"2. Conservative (+8 vehicles) - balance of capacity and efficiency")
        print(f"\nBest of both worlds approach - compare when complete!")
    else:
        print(f"\n❌ **PARALLEL LAUNCH FAILED**")

if __name__ == '__main__':
    main()