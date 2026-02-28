#!/usr/bin/env python3
"""
Monitor Parallel Optimization Campaign
Track both Strategic (+15) and Conservative (+8) vehicle tests
"""

import json
import os
import requests
import time
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def load_run_infos():
    """Load both run information files"""
    strategic_info = None
    conservative_info = None
    
    try:
        with open('strategic_test_run_info.json', 'r') as f:
            strategic_info = json.load(f)
    except FileNotFoundError:
        pass
        
    try:
        with open('conservative_test_run_info.json', 'r') as f:
            conservative_info = json.load(f)
    except FileNotFoundError:
        pass
    
    return strategic_info, conservative_info

def check_run_status(run_id):
    """Check status of a specific run"""
    headers = {'X-API-KEY': TIMEFOLD_API_KEY}
    
    try:
        response = requests.get(
            f'{TIMEFOLD_BASE_URL}/route-plans/{run_id}',
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return None
            
    except requests.RequestException:
        return None

def analyze_campaign_progress():
    """Analyze progress of both parallel tests"""
    
    print("🧬 **PARALLEL OPTIMIZATION CAMPAIGN PROGRESS**")
    print("="*70)
    
    strategic_info, conservative_info = load_run_infos()
    
    if not strategic_info or not conservative_info:
        print("❌ Missing run information files")
        return
    
    # Check status of both runs
    strategic_data = check_run_status(strategic_info['run_id'])
    conservative_data = check_run_status(conservative_info['run_id'])
    
    print(f"📊 **CAMPAIGN OVERVIEW:**")
    print(f"Strategic Test (+15 vehicles): {strategic_info['run_id'][:8]}")
    print(f"Conservative Test (+8 vehicles): {conservative_info['run_id'][:8]}")
    print()
    
    # Analyze strategic test
    if strategic_data:
        analyze_test_progress("Strategic (+15)", strategic_data, strategic_info)
    else:
        print("❌ Could not fetch strategic test data")
    
    print("\n" + "-"*50 + "\n")
    
    # Analyze conservative test  
    if conservative_data:
        analyze_test_progress("Conservative (+8)", conservative_data, conservative_info)
    else:
        print("❌ Could not fetch conservative test data")
    
    # Compare tests if both available
    if strategic_data and conservative_data:
        print("\n" + "="*70)
        compare_parallel_tests(strategic_data, conservative_data)

def analyze_test_progress(test_name, run_data, run_info):
    """Analyze progress of a single test"""
    
    print(f"🎯 **{test_name.upper()} TEST:**")
    
    # Extract basic info
    meta = run_data.get("metadata") or run_data.get("run") or {}
    status = meta.get("solverStatus", "UNKNOWN")
    score = meta.get("score", "no score")
    
    # Calculate elapsed time
    submit_time = datetime.fromisoformat(run_info['submission_time'].replace('Z', '+00:00'))
    elapsed = datetime.now() - submit_time.replace(tzinfo=None)
    elapsed_hours = elapsed.total_seconds() / 3600
    
    print(f"Status: {status}")
    print(f"Elapsed: {elapsed_hours:.1f} hours")
    print(f"Score: {score}")
    
    # Extract intermediate metrics if available
    if status == "SOLVING_ACTIVE":
        model_output = run_data.get("modelOutput", {})
        if model_output:
            vehicles = model_output.get("vehicles", [])
            unassigned = model_output.get("unassignedVisits", [])
            
            print(f"Vehicles: {len(vehicles)}")
            print(f"Unassigned: {len(unassigned)}")
            
            # Quick efficiency estimate
            if vehicles:
                total_visits = 0
                empty_shifts = 0
                total_shifts = 0
                
                for vehicle in vehicles:
                    shifts = vehicle.get('shifts', [])
                    for shift in shifts:
                        total_shifts += 1
                        itinerary = shift.get('itinerary', [])
                        visits_in_shift = [item for item in itinerary if item.get('kind') == 'VISIT']
                        if visits_in_shift:
                            total_visits += len(visits_in_shift)
                        else:
                            empty_shifts += 1
                
                if total_shifts > 0:
                    active_shifts = total_shifts - empty_shifts
                    visits_per_shift = total_visits / active_shifts if active_shifts > 0 else 0
                    empty_rate = empty_shifts / total_shifts * 100
                    
                    print(f"Visits/active shift: {visits_per_shift:.1f}")
                    print(f"Empty shifts: {empty_shifts}/{total_shifts} ({empty_rate:.1f}%)")
        
        # Remaining time estimate
        remaining_hours = 4.5 - elapsed_hours  # Average 4.5 hour completion
        print(f"Est. remaining: {remaining_hours:.1f} hours")
        
    elif status == "SOLVING_COMPLETED":
        print("🎉 OPTIMIZATION COMPLETE!")
        # Could extract final metrics here
    
    elif status == "SOLVING_FAILED":
        print("❌ OPTIMIZATION FAILED")
        if "failureMessage" in meta:
            print(f"Error: {meta['failureMessage']}")

def compare_parallel_tests(strategic_data, conservative_data):
    """Compare the two parallel tests"""
    
    print("⚖️ **PARALLEL TEST COMPARISON:**")
    
    # Extract basic comparison data
    strategic_meta = strategic_data.get("metadata") or strategic_data.get("run") or {}
    conservative_meta = conservative_data.get("metadata") or conservative_data.get("run") or {}
    
    strategic_status = strategic_meta.get("solverStatus", "UNKNOWN")
    conservative_status = conservative_meta.get("solverStatus", "UNKNOWN")
    
    strategic_output = strategic_data.get("modelOutput", {})
    conservative_output = conservative_data.get("modelOutput", {})
    
    print(f"Strategic Status: {strategic_status}")
    print(f"Conservative Status: {conservative_status}")
    
    if strategic_output and conservative_output:
        strategic_unassigned = len(strategic_output.get("unassignedVisits", []))
        conservative_unassigned = len(conservative_output.get("unassignedVisits", []))
        
        print(f"\nUnassigned Visits:")
        print(f"  Strategic (+15): {strategic_unassigned}")
        print(f"  Conservative (+8): {conservative_unassigned}")
        
        if strategic_unassigned != conservative_unassigned:
            better_unassigned = "Strategic" if strategic_unassigned < conservative_unassigned else "Conservative"
            print(f"  → {better_unassigned} handling unassigned better")
    
    # Score comparison if available
    strategic_score = strategic_meta.get("score", "")
    conservative_score = conservative_meta.get("score", "")
    
    if strategic_score and conservative_score:
        print(f"\nScore Comparison:")
        print(f"  Strategic: {strategic_score}")
        print(f"  Conservative: {conservative_score}")
    
    print(f"\n🎯 **STRATEGY STATUS:**")
    if strategic_status == "SOLVING_ACTIVE" and conservative_status == "SOLVING_ACTIVE":
        print("Both tests actively optimizing - wait for completion")
    elif strategic_status == "SOLVING_COMPLETED" or conservative_status == "SOLVING_COMPLETED":
        print("At least one test complete - detailed analysis possible")
    else:
        print("Mixed status - continue monitoring")

def main():
    analyze_campaign_progress()
    
    print(f"\n🔄 **NEXT ACTIONS:**")
    print(f"- Monitor both tests until completion")
    print(f"- Compare detailed results when both finish")
    print(f"- Select best approach or create hybrid strategy")
    print(f"- Run: python3 monitor_parallel_campaign.py (check progress)")

if __name__ == '__main__':
    main()