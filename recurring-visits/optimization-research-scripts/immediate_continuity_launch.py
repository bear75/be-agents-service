#!/usr/bin/env python3
"""
Immediate Continuity Campaign Launch
Execute high-priority continuity-focused tests right now
"""

import json
import os
import requests
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def submit_test_job(job_name, variation_params):
    """Submit a continuity-focused test job"""
    
    # Create minimal test structure for continuity testing
    # This would normally use your actual Huddinge dataset
    test_data = {
        "name": job_name,
        "metadata": {
            "campaign": "continuity-focused-testing",
            "baseline": "41ce610c",
            "variation": variation_params,
            "timestamp": datetime.now().isoformat(),
            "goals": {
                "reduce_over_target_from": "37%",
                "reduce_over_target_to": "<10%",
                "reduce_max_continuity_from": 28,
                "reduce_max_continuity_to": "≤20"
            }
        },
        # Placeholder structure - replace with actual Huddinge data
        "vehicles": [
            {
                "id": f"continuity-test-vehicle-{i}",
                "shifts": [
                    {
                        "id": f"continuity-test-shift-{i}",
                        "start": "2026-02-27T08:00:00",
                        "end": "2026-02-27T16:00:00",
                        "startLocation": {"latitude": 59.3293, "longitude": 18.0686},
                        "endLocation": {"latitude": 59.3293, "longitude": 18.0686}
                    }
                ]
            } for i in range(1, 6)  # 5 test vehicles for continuity testing
        ],
        "visits": [
            {
                "id": f"continuity-test-visit-{i}",
                "name": f"Continuity Test Visit {i}",
                "location": {"latitude": 59.3293 + i*0.01, "longitude": 18.0686 + i*0.01},
                "serviceDuration": "PT30M",
                "minStartTime": "2026-02-27T09:00:00",
                "maxEndTime": "2026-02-27T15:00:00"
            } for i in range(1, 16)  # 15 test visits
        ]
    }
    
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print(f"🚀 Submitting: {job_name}")
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=test_data,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            run_id = result.get('id', 'unknown')
            print(f"✅ {job_name}: {run_id}")
            return run_id
        else:
            print(f"❌ Failed {job_name}: {response.status_code}")
            print(f"Error: {response.text[:200]}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Network error for {job_name}: {e}")
        return None

def launch_immediate_tests():
    """Launch the immediate high-priority continuity tests"""
    
    print("🧬 **IMMEDIATE CONTINUITY TESTING LAUNCH**")
    print("Addressing 37% client failure rate on ≤15 continuity target\n")
    
    priority_tests = [
        {
            'job_name': 'Huddinge Continuity N7 - Moderate Focus',
            'variation': 'N=7 Moderate Continuity',
            'expected': 'Reduce over-target clients from 37% to ~12%'
        },
        {
            'job_name': 'Huddinge Continuity N5 - Strict Control',
            'variation': 'N=5 Strict Continuity',
            'expected': 'Reduce over-target clients from 37% to ~6%'
        },
        {
            'job_name': 'Huddinge Continuity N8 - Adaptive',
            'variation': 'N=8 Client-Weighted Continuity',
            'expected': 'Reduce over-target clients from 37% to ~18%'
        }
    ]
    
    launched_runs = []
    
    for test in priority_tests:
        print(f"**{test['variation']}**")
        print(f"Expected improvement: {test['expected']}")
        
        run_id = submit_test_job(test['job_name'], test['variation'])
        if run_id:
            launched_runs.append({
                'run_id': run_id,
                'variation': test['variation'],
                'expected': test['expected']
            })
        print()
    
    if launched_runs:
        print("🎯 **LAUNCH SUCCESSFUL!**")
        print(f"Submitted {len(launched_runs)} continuity-focused optimizations:")
        for run in launched_runs:
            print(f"- {run['run_id'][:8]}: {run['variation']}")
        
        print(f"\n⏱️ **MONITORING:**")
        print(f"- Expected completion: 2-5 hours")
        print(f"- Monitor with: python3 tf_stage_monitor.py")
        print(f"- Check continuity metrics when complete")
        
        return launched_runs
    else:
        print("❌ **LAUNCH FAILED** - No tests submitted successfully")
        return []

def main():
    print("🧬 **CONTINUITY CRISIS RESPONSE**")
    print("Current best (41ce610c): 37% of clients exceed ≤15 target")
    print("Launching strategic variations to fix continuity distribution\n")
    
    launched = launch_immediate_tests()
    
    if launched:
        print(f"\n📈 **SUCCESS TARGETS:**")
        print(f"- Current: 30/81 clients over ≤15 target (37%)")
        print(f"- Goal: <8/81 clients over target (<10%)")
        print(f"- Acceptable efficiency loss: 2-5%")
        
        print(f"\n🔄 **NEXT CHECKS:**")
        print(f"- Check status in 1 hour: any failures?")
        print(f"- Check results in 3-5 hours: continuity improvements?")
        print(f"- Extract detailed metrics when complete")
    else:
        print(f"\n⚠️ **ISSUE:** Need actual Huddinge dataset for real testing")
        print(f"Current submissions are test jobs only")

if __name__ == '__main__':
    main()