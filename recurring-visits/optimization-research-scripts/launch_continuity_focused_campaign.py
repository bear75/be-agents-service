#!/usr/bin/env python3
"""
Continuity-Focused Campaign Launch
Strategic variations to improve continuity distribution based on 41ce610c analysis
"""

import json
import os
import requests
import time
from datetime import datetime

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def analyze_continuity_gaps():
    """Analyze the continuity performance gap from run 41ce610c"""
    
    print("🔬 **CONTINUITY GAP ANALYSIS**")
    print("Based on run 41ce610c detailed metrics\n")
    
    current_metrics = {
        'avg_continuity': 12.9,
        'max_continuity': 28,
        'clients_over_target': 30,
        'total_clients': 81,
        'target': 15,
        'failure_rate': 37  # 30/81 = 37%
    }
    
    print(f"**Current Performance (41ce610c):**")
    print(f"- Average continuity: {current_metrics['avg_continuity']} (target ≤{current_metrics['target']})")
    print(f"- Maximum continuity: {current_metrics['max_continuity']} (target ≤{current_metrics['target']})")
    print(f"- Clients over target: {current_metrics['clients_over_target']}/{current_metrics['total_clients']} ({current_metrics['failure_rate']}%)")
    print(f"- Medium penalty: 420,000")
    
    print(f"\n**Required Improvements:**")
    print(f"- Reduce failure rate from 37% to <10% (target: <8 clients over ≤15)")
    print(f"- Reduce maximum from 28 to ≤20 (eliminate worst cases)")
    print(f"- Maintain average around 10-12 (currently 12.9 is acceptable)")
    
    return current_metrics

def design_continuity_focused_variations():
    """Design specific parameter variations to improve continuity"""
    
    print("\n🎯 **CONTINUITY-FOCUSED STRATEGIC VARIATIONS**\n")
    
    variations = [
        {
            'name': 'Strict Continuity (N=5)',
            'description': 'Very tight continuity constraints, accept lower efficiency',
            'n_value': 5,
            'continuity_weight': 'very_high',
            'expected_avg_continuity': '8-10',
            'expected_over_target': '<5 clients (6%)',
            'expected_efficiency_tradeoff': '-5-8%',
            'priority': 'high',
            'rationale': 'Force maximum caregiver consistency'
        },
        {
            'name': 'Moderate Continuity (N=7)',
            'description': 'Balance continuity improvement with efficiency',
            'n_value': 7,
            'continuity_weight': 'high',
            'expected_avg_continuity': '9-11',
            'expected_over_target': '<10 clients (12%)',
            'expected_efficiency_tradeoff': '-3-5%',
            'priority': 'highest',
            'rationale': 'Sweet spot between current and strict'
        },
        {
            'name': 'Client-Weighted Continuity',
            'description': 'Higher continuity weight for high-visit clients',
            'n_value': 8,
            'continuity_weight': 'adaptive',
            'expected_avg_continuity': '10-12',
            'expected_over_target': '<15 clients (18%)',
            'expected_efficiency_tradeoff': '-2-4%',
            'priority': 'high',
            'rationale': 'Protect clients with many visits from caregiver switching'
        },
        {
            'name': 'Continuity Cap (N=6)',
            'description': 'Hard cap on caregivers per client',
            'n_value': 6,
            'continuity_weight': 'capped',
            'expected_avg_continuity': '8-11',
            'expected_over_target': '0 clients (0%)',
            'expected_efficiency_tradeoff': '-6-10%',
            'priority': 'medium',
            'rationale': 'Guarantee no client exceeds 15 caregivers'
        },
        {
            'name': 'Hybrid Approach (N=8.5)',
            'description': 'Balanced improvement with minimal efficiency loss',
            'n_value': 8,
            'continuity_weight': 'medium_high',
            'expected_avg_continuity': '10-13',
            'expected_over_target': '<20 clients (25%)',
            'expected_efficiency_tradeoff': '-1-3%',
            'priority': 'high',
            'rationale': 'Incremental improvement from current best'
        }
    ]
    
    for i, var in enumerate(variations, 1):
        priority_icon = "⭐⭐⭐" if var['priority'] == 'highest' else "⭐⭐" if var['priority'] == 'high' else "⭐"
        
        print(f"**{i}. {var['name']}** {priority_icon}")
        print(f"   - {var['description']}")
        print(f"   - Expected avg continuity: {var['expected_avg_continuity']}")
        print(f"   - Expected over target: {var['expected_over_target']}")
        print(f"   - Efficiency tradeoff: {var['expected_efficiency_tradeoff']}")
        print(f"   - Rationale: {var['rationale']}")
        print()
    
    return variations

def create_immediate_test_batch():
    """Create immediate high-priority test batch"""
    
    print("🚀 **IMMEDIATE TEST BATCH**")
    print("Launching 3 highest-priority variations\n")
    
    immediate_tests = [
        {
            'name': 'Moderate Continuity (N=7)',
            'job_name': 'Huddinge Continuity Focus N7',
            'expected_improvement': 'Major continuity improvement',
            'timeline': '3-5 hours'
        },
        {
            'name': 'Strict Continuity (N=5)', 
            'job_name': 'Huddinge Strict Continuity N5',
            'expected_improvement': 'Maximum continuity control',
            'timeline': '2-4 hours'
        },
        {
            'name': 'Client-Weighted Continuity',
            'job_name': 'Huddinge Adaptive Continuity N8',
            'expected_improvement': 'Smart continuity targeting',
            'timeline': '3-5 hours'
        }
    ]
    
    for i, test in enumerate(immediate_tests, 1):
        print(f"**Test {i}: {test['name']}**")
        print(f"- Job name: {test['job_name']}")
        print(f"- Expected: {test['expected_improvement']}")
        print(f"- Timeline: {test['timeline']}")
        print()
    
    return immediate_tests

def launch_continuity_test(base_input_data, variation_name):
    """Launch a specific continuity-focused test"""
    
    if not base_input_data:
        print("⚠️ No input data provided")
        return None
    
    print(f"🚀 **LAUNCHING: {variation_name}**\n")
    
    # Clone and modify input data based on variation
    job_data = json.loads(json.dumps(base_input_data))  # Deep copy
    
    # Add metadata for tracking
    job_data['metadata'] = {
        'name': f'Huddinge Continuity Focus - {variation_name}',
        'campaign': 'continuity-optimization',
        'baseline_run': '41ce610c',
        'baseline_metrics': {
            'avg_continuity': 12.9,
            'over_target': 30,
            'failure_rate': 37
        },
        'variation': variation_name,
        'timestamp': datetime.now().isoformat()
    }
    
    # Submit to Timefold
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=job_data,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            run_id = result.get('id', 'unknown')
            print(f"✅ **{variation_name}** submitted: {run_id}")
            return run_id
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"Error: {response.text[:300]}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def execute_immediate_campaign():
    """Execute the immediate continuity-focused campaign"""
    
    print("🧬 **CONTINUITY-FOCUSED CAMPAIGN EXECUTION**")
    print("="*60)
    
    # Step 1: Analyze current gaps
    current_metrics = analyze_continuity_gaps()
    
    print("\n" + "="*60)
    
    # Step 2: Design variations
    variations = design_continuity_focused_variations()
    
    print("="*60)
    
    # Step 3: Create immediate batch
    immediate_tests = create_immediate_test_batch()
    
    print("="*60 + "\n")
    
    print("🎯 **CAMPAIGN GOALS:**")
    print("- Reduce clients over ≤15 target from 37% to <10%")
    print("- Reduce maximum continuity from 28 to ≤20")
    print("- Accept 2-5% efficiency loss for major continuity improvement")
    print("- Find sweet spot configuration for Huddinge presentation")
    
    print(f"\n📋 **TO PROCEED:**")
    print(f"1. Load your Huddinge dataset:")
    print(f"   with open('huddinge_input.json', 'r') as f:")
    print(f"       data = json.load(f)")
    
    print(f"\n2. Launch priority tests:")
    print(f"   launch_continuity_test(data, 'Moderate Continuity (N=7)')")
    print(f"   launch_continuity_test(data, 'Strict Continuity (N=5)')")
    print(f"   launch_continuity_test(data, 'Client-Weighted Continuity')")
    
    print(f"\n3. Monitor results in 3-5 hours")
    print(f"   python3 tf_stage_monitor.py")

def main():
    execute_immediate_campaign()

if __name__ == '__main__':
    main()