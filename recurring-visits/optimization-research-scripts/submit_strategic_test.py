#!/usr/bin/env python3
"""
Submit Strategic Capacity Test to Timefold
"""

import json
import os
import requests
import time
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def submit_optimization(input_file="clean_strategic_input.json", job_name="Strategic Capacity Test (+15 vehicles)"):
    """Submit the strategic capacity test to Timefold"""
    
    print(f"🚀 **SUBMITTING STRATEGIC CAPACITY TEST**")
    print("="*60)
    
    # Load the modified input
    with open(input_file, 'r') as f:
        clean_model_input = json.load(f)
    
    # Validate input
    vehicles = clean_model_input.get('vehicles', [])
    visits = clean_model_input.get('visits', [])
    
    print(f"Submitting optimization:")
    print(f"  - Job name: {job_name}")
    print(f"  - Vehicles: {len(vehicles)}")
    print(f"  - Visits: {len(visits)}")
    print(f"  - Campaign: Strategic capacity increase for continuity optimization")
    
    # Prepare submission payload - wrap in modelInput
    submission_payload = {"modelInput": clean_model_input}
    
    # Submit to Timefold
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"\n🌐 Submitting to Timefold...")
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
            
            print(f"✅ **SUBMISSION SUCCESSFUL!**")
            print(f"Run ID: {run_id}")
            print(f"Status: {solver_status}")
            print(f"Expected completion: 4-6 hours")
            
            # Save run ID for monitoring
            run_info = {
                'run_id': run_id,
                'submission_time': datetime.now().isoformat(),
                'job_name': job_name,
                'vehicles': len(vehicles),
                'visits': len(visits),
                'baseline_run': '41ce610c-bd67-47b8-9e62-7820f87ffcdd',
                'expected_improvements': {
                    'poor_continuity_rate': 'from 37% to 12-15%',
                    'unassigned_visits': 'from 42 to 25-30',
                    'efficiency': 'from 62.2% to 56-58%'
                }
            }
            
            with open('strategic_test_run_info.json', 'w') as f:
                json.dump(run_info, f, indent=2)
            
            print(f"\n📊 **MONITORING:**")
            print(f"Run info saved: strategic_test_run_info.json")
            print(f"Monitor progress with: python3 monitor_strategic_test.py")
            print(f"Check status: curl -H 'X-API-KEY: {TIMEFOLD_API_KEY}' {TIMEFOLD_BASE_URL}/route-plans/{run_id}")
            
            return run_id, True
            
        else:
            print(f"❌ **SUBMISSION FAILED**")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None, False
            
    except requests.RequestException as e:
        print(f"❌ **NETWORK ERROR**")
        print(f"Error: {e}")
        return None, False

def main():
    print("🧬 **STRATEGIC CAPACITY OPTIMIZATION SUBMISSION**")
    print("Dataset: strategic_capacity_input.json (+15 vehicles)")
    print("Target: Solve continuity crisis (37% → 12% poor continuity)")
    print()
    
    run_id, success = submit_optimization('clean_strategic_input.json')
    
    if success:
        print(f"\n🎯 **CAMPAIGN LAUNCHED**")
        print(f"Strategic capacity test is now running.")
        print(f"Expected to solve both continuity and unassigned visit issues.")
        print(f"\nNext steps:")
        print(f"1. Monitor progress (optimization takes 4-6 hours)")
        print(f"2. Analyze results when complete")
        print(f"3. Compare with baseline 41ce610c")
    else:
        print(f"\n❌ **LAUNCH FAILED**")
        print(f"Check configuration and API access.")

if __name__ == '__main__':
    main()