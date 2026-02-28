#!/usr/bin/env python3
"""
Timefold Stage Monitor
Real-time monitoring of optimization campaigns and results analysis
"""

import json
import os
import requests
import time
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def get_recent_runs(limit=10):
    """Get recent Timefold optimization runs"""
    
    headers = {'X-API-KEY': TIMEFOLD_API_KEY}
    
    try:
        response = requests.get(f'{TIMEFOLD_BASE_URL}/route-plans', headers=headers, timeout=30)
        response.raise_for_status()
        
        runs = response.json()
        return runs[:limit]
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch runs: {e}")
        return []

def analyze_campaign_progress():
    """Analyze progress of the 45-job binary tree optimization campaign"""
    
    print("🧬 **45-JOB BINARY TREE OPTIMIZATION CAMPAIGN STATUS**\n")
    
    runs = get_recent_runs(20)
    
    if not runs:
        print("❌ No runs found")
        return
    
    # Categorize runs
    completed = [r for r in runs if r.get('solverStatus') == 'SOLVING_COMPLETED']
    failed = [r for r in runs if r.get('solverStatus') in ['SOLVING_FAILED', 'DATASET_INVALID']]
    active = [r for r in runs if r.get('solverStatus') in ['SOLVING_ACTIVE', 'SOLVING_SCHEDULED']]
    
    print(f"**Campaign Overview:**")
    print(f"- Total runs: {len(runs)}")
    print(f"- ✅ Completed: {len(completed)}")
    print(f"- ❌ Failed: {len(failed)}")
    print(f"- 🔄 Active: {len(active)}")
    
    # Analyze target metrics for completed runs
    if completed:
        print(f"\n**Completed Run Analysis:**")
        target_hits = 0
        
        for run in completed[:5]:  # Analyze top 5 completed runs
            run_id = run['id'][:8]
            score = run.get('score', 'unknown')
            
            # Extract efficiency/continuity/unassigned if available in score
            # For now, just report the raw score
            print(f"- {run_id}: Score = {score}")
            
            # TODO: Parse score for actual metrics once we know the format
            # Check if it hits our targets: 70-75% efficiency, ≤10 continuity, <36 unassigned
    
    # Show active runs
    if active:
        print(f"\n**Active Optimizations:**")
        for run in active:
            run_id = run['id'][:8]
            started = run.get('startDateTime', run.get('submitDateTime', 'unknown'))
            print(f"- {run_id}: Running since {started}")
    
    # Show recent failures with reasons
    if failed:
        print(f"\n**Recent Failures (for repair):**")
        for run in failed[:3]:
            run_id = run['id'][:8]
            status = run.get('solverStatus')
            print(f"- {run_id}: {status}")

def submit_test_job():
    """Submit a test job to verify the repair process works"""
    
    print("🧪 **SUBMITTING TEST JOB**")
    
    # Create minimal test data structure
    test_data = {
        "name": "Test Job - Repair Validation",
        "vehicles": [
            {
                "id": "test-vehicle-1",
                "shifts": [
                    {
                        "id": "test-shift-1",
                        "start": "2026-02-27T08:00:00",
                        "end": "2026-02-27T16:00:00",
                        "startLocation": {"latitude": 59.3293, "longitude": 18.0686},
                        "endLocation": {"latitude": 59.3293, "longitude": 18.0686}
                    }
                ]
            }
        ],
        "visits": [
            {
                "id": "test-visit-1",
                "name": "Test Visit",
                "location": {"latitude": 59.3293, "longitude": 18.0686},
                "serviceDuration": "PT30M",
                "minStartTime": "2026-02-27T09:00:00",
                "maxEndTime": "2026-02-27T15:00:00"
            }
        ]
    }
    
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            run_id = result.get('id', 'unknown')
            print(f"✅ Test job submitted successfully: {run_id}")
            return run_id
        else:
            print(f"❌ Test job failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def extract_optimization_metrics(run_data):
    """Extract efficiency, continuity, and unassigned metrics from run results"""
    
    # TODO: This needs to be implemented based on the actual Timefold response structure
    # For now, return placeholder structure
    
    score = run_data.get('score', '')
    
    # Try to parse score string if it contains our target metrics
    # Format might be like: "0hard/-680000medium/-2011536soft"
    
    metrics = {
        'efficiency_percent': None,
        'continuity_score': None, 
        'unassigned_count': None,
        'targets_met': 0,
        'raw_score': score
    }
    
    # Placeholder parsing - update when we have real score format
    if score and isinstance(score, str):
        # Look for patterns that might indicate our metrics
        if 'medium' in score:
            # Medium penalties might indicate continuity issues
            try:
                medium_part = score.split('medium')[0].split('/')[-1]
                metrics['continuity_score'] = abs(int(medium_part)) / 10000  # rough conversion
            except:
                pass
    
    return metrics

def monitor_campaign_targets():
    """Monitor campaign progress against specific targets"""
    
    print("🎯 **TARGET MONITORING**")
    print("Targets: 70-75% efficiency, ≤10 continuity, <36 unassigned\n")
    
    runs = get_recent_runs(20)
    completed_runs = [r for r in runs if r.get('solverStatus') == 'SOLVING_COMPLETED']
    
    if not completed_runs:
        print("⚠️ No completed runs to analyze")
        return
    
    target_hits = []
    
    for run in completed_runs:
        run_id = run['id'][:8]
        
        # Get detailed results
        try:
            headers = {'X-API-KEY': TIMEFOLD_API_KEY}
            response = requests.get(f'{TIMEFOLD_BASE_URL}/route-plans/{run["id"]}', headers=headers)
            
            if response.status_code == 200:
                detailed_run = response.json()
                metrics = extract_optimization_metrics(detailed_run)
                
                print(f"Run {run_id}:")
                print(f"  - Raw Score: {metrics['raw_score']}")
                print(f"  - Targets Met: {metrics['targets_met']}/3")
                
                if metrics['targets_met'] >= 2:
                    target_hits.append(run_id)
            
        except Exception as e:
            print(f"  - Error analyzing {run_id}: {e}")
    
    if target_hits:
        print(f"\n🎉 **PROMISING RUNS:** {', '.join(target_hits)}")
    else:
        print(f"\n🔄 **OPTIMIZATION CONTINUES:** No runs hit 2+ targets yet")

def main():
    print("🧬 **TIMEFOLD STAGE MONITOR**\n")
    
    # Step 1: Check current campaign status
    analyze_campaign_progress()
    
    print("\n" + "="*60 + "\n")
    
    # Step 2: Monitor targets
    monitor_campaign_targets()
    
    print("\n" + "="*60 + "\n")
    
    # Step 3: Offer next actions
    print("**NEXT ACTIONS:**")
    print("1. 🧪 Submit test job: submit_test_job()")
    print("2. 📊 Monitor targets: monitor_campaign_targets()")
    print("3. 🔄 Refresh status: analyze_campaign_progress()")
    print("4. 🚀 Submit new optimization job with repaired data")

if __name__ == '__main__':
    main()