#!/usr/bin/env python3
"""
Monitor Strategic Capacity Test Progress
"""

import json
import os
import requests
import time
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def load_run_info():
    """Load the saved run information"""
    try:
        with open('strategic_test_run_info.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def check_run_status(run_id):
    """Check the current status of a run"""
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

def analyze_progress(run_data, run_info):
    """Analyze the current progress"""
    
    print("🧬 **STRATEGIC CAPACITY TEST PROGRESS**")
    print("="*60)
    
    # Extract status information
    meta = run_data.get("metadata") or run_data.get("run") or {}
    status = meta.get("solverStatus", "UNKNOWN")
    
    print(f"Run ID: {run_info['run_id']}")
    print(f"Job Name: {run_info['job_name']}")
    print(f"Submission: {run_info['submission_time']}")
    print(f"Current Status: {status}")
    
    # Calculate elapsed time
    submit_time = datetime.fromisoformat(run_info['submission_time'].replace('Z', '+00:00'))
    elapsed = datetime.now() - submit_time.replace(tzinfo=None)
    elapsed_hours = elapsed.total_seconds() / 3600
    
    print(f"Elapsed Time: {elapsed_hours:.1f} hours")
    
    # Status-specific information
    if status == "SOLVING_SCHEDULED":
        print(f"📅 Status: Queued for optimization")
        print(f"⏱️ Waiting to start processing...")
        
    elif status == "SOLVING_ACTIVE":
        print(f"🔄 Status: Actively optimizing")
        print(f"⏱️ Expected completion: {4 - elapsed_hours:.1f} - {6 - elapsed_hours:.1f} hours remaining")
        
        # Show any intermediate metrics if available
        if "score" in meta:
            print(f"Current score: {meta['score']}")
            
    elif status == "SOLVING_COMPLETED":
        print(f"✅ Status: OPTIMIZATION COMPLETE!")
        
        # Extract results
        model_output = run_data.get("modelOutput", {})
        vehicles = model_output.get("vehicles", [])
        unassigned = model_output.get("unassignedVisits", [])
        
        print(f"\n🎯 **INITIAL RESULTS:**")
        print(f"Vehicles: {len(vehicles)}")
        print(f"Unassigned visits: {len(unassigned)}")
        
        if "score" in meta:
            score = meta["score"]
            print(f"Score: {score}")
            
            # Parse score components
            if isinstance(score, str) and 'hard' in score:
                try:
                    parts = score.split('/')
                    hard = parts[0].replace('hard', '') if 'hard' in parts[0] else '0'
                    medium = parts[1].replace('medium', '') if len(parts) > 1 and 'medium' in parts[1] else '0'
                    soft = parts[2].replace('soft', '') if len(parts) > 2 and 'soft' in parts[2] else '0'
                    
                    print(f"\n📊 **SCORE ANALYSIS:**")
                    print(f"Hard violations: {hard} (feasibility)")
                    print(f"Medium penalties: {medium} (continuity)")
                    print(f"Soft penalties: {soft} (efficiency)")
                    
                    # Compare with baseline (41ce610c)
                    baseline_medium = 420000  # From previous analysis
                    baseline_unassigned = 42
                    
                    medium_val = abs(int(medium)) if medium != '0' else 0
                    
                    print(f"\n🔄 **COMPARISON WITH BASELINE:**")
                    print(f"Unassigned: {baseline_unassigned} → {len(unassigned)} ({len(unassigned) - baseline_unassigned:+d})")
                    print(f"Medium penalty: {baseline_medium:,} → {medium_val:,} ({medium_val - baseline_medium:+,})")
                    
                except (IndexError, ValueError):
                    print(f"Score format not recognized: {score}")
        
        print(f"\n📋 **NEXT STEPS:**")
        print(f"1. Run detailed analysis: python3 fetch_timefold_solution.py {run_info['run_id']} --save results/strategic_test.json --input results/strategic_input.json")
        print(f"2. Generate continuity report")
        print(f"3. Compare with baseline 41ce610c")
        
    elif status == "SOLVING_FAILED":
        print(f"❌ Status: OPTIMIZATION FAILED")
        
        if "failureMessage" in meta:
            print(f"Error: {meta['failureMessage']}")
        elif "error" in run_data:
            print(f"Error: {run_data['error']}")
        
        print(f"\n🔧 **TROUBLESHOOTING:**")
        print(f"1. Check for data validation issues")
        print(f"2. Verify vehicle/visit configuration")
        print(f"3. Consider reducing scope or adjusting constraints")
        
    else:
        print(f"⚠️ Status: {status}")
        print(f"Unknown status - check Timefold documentation")
    
    return status

def main():
    # Load run information
    run_info = load_run_info()
    
    if not run_info:
        print("❌ No run information found. Make sure strategic_test_run_info.json exists.")
        return
    
    # Check current status
    run_data = check_run_status(run_info['run_id'])
    
    if not run_data:
        print("❌ Could not fetch run status. Check API connectivity.")
        return
    
    # Analyze progress
    status = analyze_progress(run_data, run_info)
    
    # Provide monitoring recommendations
    print(f"\n🔄 **MONITORING RECOMMENDATIONS:**")
    
    if status in ["SOLVING_SCHEDULED", "SOLVING_ACTIVE"]:
        print(f"- Check back in 1 hour for progress updates")
        print(f"- Full completion expected in 4-6 hours total")
        print(f"- Run this script periodically: python3 monitor_strategic_test.py")
        
    elif status == "SOLVING_COMPLETED":
        print(f"- Ready for detailed analysis!")
        print(f"- Expected: Major continuity improvement (37% → 12% poor rate)")
        print(f"- Expected: Unassigned reduction (42 → 25-30 visits)")
        
    elif status == "SOLVING_FAILED":
        print(f"- Investigate failure cause")
        print(f"- Consider alternative approach or parameter adjustment")
        print(f"- May need to submit revised configuration")

if __name__ == '__main__':
    main()