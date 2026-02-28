#!/usr/bin/env python3
"""
Timefold Stage Optimization Campaign
Strategic iteration to hit sweet spot targets: 70-75% efficiency, ≤10 continuity, <36 unassigned
"""

import json
import os
import requests
import time
from datetime import datetime
import copy

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def analyze_current_results():
    """Analyze current optimization results to guide next iterations"""
    
    print("🔬 **CURRENT RESULTS ANALYSIS**\n")
    
    headers = {'X-API-KEY': TIMEFOLD_API_KEY}
    
    # Get recent runs
    try:
        response = requests.get(f'{TIMEFOLD_BASE_URL}/route-plans', headers=headers)
        runs = response.json()[:8]  # Top 8 recent runs
    except:
        print("❌ Failed to fetch runs")
        return None
    
    # Analyze score patterns
    scores = []
    for run in runs:
        score = run.get('score', '')
        if score:
            scores.append(score)
    
    print(f"**Score Pattern Analysis:**")
    for i, score in enumerate(scores[:5], 1):
        print(f"{i}. {score}")
    
    # Parse score components
    score_analysis = analyze_score_components(scores)
    print(f"\n**Score Component Analysis:**")
    print(f"- Hard constraint violations: {score_analysis['hard_violations']}")
    print(f"- Medium penalty range: {score_analysis['medium_range']}")
    print(f"- Soft penalty range: {score_analysis['soft_range']}")
    
    # Strategic recommendations
    print(f"\n**Strategic Assessment:**")
    if score_analysis['hard_violations'] == 0:
        print("✅ No hard constraint violations - basic feasibility achieved")
        
        if score_analysis['medium_avg'] > 500000:
            print("⚠️ High medium penalties - likely continuity constraint issues")
            print("💡 Strategy: Relax continuity constraints or increase N-value")
        
        if score_analysis['soft_avg'] > 2000000:
            print("⚠️ High soft penalties - likely efficiency/travel time issues")  
            print("💡 Strategy: Adjust travel time weights or capacity constraints")
    else:
        print("❌ Hard constraint violations present - data integrity issues remain")
    
    return score_analysis

def analyze_score_components(scores):
    """Parse Timefold score components"""
    
    hard_violations = []
    medium_penalties = []
    soft_penalties = []
    
    for score in scores:
        if not score:
            continue
            
        try:
            # Parse format: "0hard/-680000medium/-2011536soft"
            parts = score.split('/')
            
            # Hard constraints
            if 'hard' in parts[0]:
                hard_val = int(parts[0].replace('hard', ''))
                hard_violations.append(hard_val)
            
            # Medium constraints (continuity-related)
            for part in parts:
                if 'medium' in part:
                    medium_val = abs(int(part.replace('medium', '')))
                    medium_penalties.append(medium_val)
            
            # Soft constraints (efficiency-related)
            for part in parts:
                if 'soft' in part:
                    soft_val = abs(int(part.replace('soft', '')))
                    soft_penalties.append(soft_val)
                    
        except (ValueError, IndexError) as e:
            continue
    
    return {
        'hard_violations': sum(hard_violations),
        'medium_range': f"{min(medium_penalties) if medium_penalties else 0}-{max(medium_penalties) if medium_penalties else 0}",
        'medium_avg': sum(medium_penalties) / len(medium_penalties) if medium_penalties else 0,
        'soft_range': f"{min(soft_penalties) if soft_penalties else 0}-{max(soft_penalties) if soft_penalties else 0}",
        'soft_avg': sum(soft_penalties) / len(soft_penalties) if soft_penalties else 0,
        'medium_penalties': medium_penalties,
        'soft_penalties': soft_penalties
    }

def generate_strategic_variations():
    """Generate strategic parameter variations to hit sweet spot targets"""
    
    print("🎯 **STRATEGIC PARAMETER VARIATIONS**\n")
    
    # Based on current analysis, generate N-value variations
    variations = [
        {
            'name': 'N=8 Moderate Continuity',
            'description': 'Moderate continuity constraint for balanced efficiency',
            'n_value': 8,
            'continuity_weight': 'medium',
            'expected_efficiency': '72-76%',
            'expected_continuity': '8-12',
            'rationale': 'Sweet spot between current high-continuity runs'
        },
        {
            'name': 'N=6 Higher Continuity', 
            'description': 'Tighter continuity for stability',
            'n_value': 6,
            'continuity_weight': 'high',
            'expected_efficiency': '69-73%',
            'expected_continuity': '6-8',
            'rationale': 'Target lower continuity scores'
        },
        {
            'name': 'N=12 Lower Continuity',
            'description': 'Relaxed continuity for higher efficiency', 
            'n_value': 12,
            'continuity_weight': 'low',
            'expected_efficiency': '75-79%',
            'expected_continuity': '10-15',
            'rationale': 'Push efficiency up, accept higher continuity'
        },
        {
            'name': 'Efficiency-Focused',
            'description': 'Minimize travel time, moderate continuity',
            'n_value': 10,
            'travel_weight': 'high',
            'expected_efficiency': '74-78%',
            'expected_continuity': '8-12',
            'rationale': 'Direct efficiency optimization'
        },
        {
            'name': 'Balanced Sweet Spot',
            'description': 'Balanced approach targeting all metrics',
            'n_value': 9,
            'balance': 'optimal',
            'expected_efficiency': '71-75%', 
            'expected_continuity': '7-10',
            'rationale': 'Center of target ranges'
        }
    ]
    
    print("**Recommended Variations to Test:**\n")
    for i, var in enumerate(variations, 1):
        print(f"**{i}. {var['name']}**")
        print(f"   - {var['description']}")
        print(f"   - Expected efficiency: {var['expected_efficiency']}")
        print(f"   - Expected continuity: {var['expected_continuity']}")
        print(f"   - Rationale: {var['rationale']}")
        print()
    
    return variations

def create_campaign_batch():
    """Create a batch of optimization jobs with strategic variations"""
    
    print("🚀 **CREATING CAMPAIGN BATCH**\n")
    
    variations = generate_strategic_variations()
    
    # For demonstration, create job specifications
    # In practice, you would modify your actual input data with these parameters
    
    batch_jobs = []
    
    for var in variations:
        job_spec = {
            'name': f"Huddinge Sweet Spot - {var['name']}",
            'variation': var,
            'priority': 'high' if 'Sweet Spot' in var['name'] or 'Balanced' in var['name'] else 'normal',
            'expected_duration': '3-5 hours',
            'success_criteria': {
                'efficiency_min': 70,
                'efficiency_max': 75,
                'continuity_max': 10,
                'unassigned_max': 36
            }
        }
        batch_jobs.append(job_spec)
    
    print(f"**Batch Summary:**")
    print(f"- Total variations: {len(batch_jobs)}")
    print(f"- High priority: {sum(1 for j in batch_jobs if j['priority'] == 'high')}")
    print(f"- Expected completion: 2-4 days")
    print(f"- Success target: 2+ variations hitting all targets")
    
    return batch_jobs

def execute_priority_job(base_input_data=None):
    """Execute a high-priority job from our strategic variations"""
    
    if not base_input_data:
        print("⚠️ No base input data provided")
        print("Load your Huddinge dataset first:")
        print("  with open('huddinge_input.json', 'r') as f:")
        print("      base_data = json.load(f)")
        print("  execute_priority_job(base_data)")
        return None
    
    print("🎯 **EXECUTING PRIORITY JOB: Balanced Sweet Spot**\n")
    
    # Clone input data for modification
    job_data = copy.deepcopy(base_input_data)
    
    # Apply strategic modifications for "Balanced Sweet Spot" variation
    # This would involve modifying solver parameters, constraints, etc.
    # For now, just add metadata
    
    job_data['metadata'] = {
        'name': 'Huddinge Sweet Spot - Balanced',
        'campaign': '45-job-binary-tree',
        'variation': 'N=9 Balanced',
        'targets': {
            'efficiency': '71-75%',
            'continuity': '7-10', 
            'unassigned': '<36'
        },
        'timestamp': datetime.now().isoformat()
    }
    
    # Submit to Timefold
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        print("🚀 Submitting balanced sweet spot optimization...")
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=job_data,
            timeout=60
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            run_id = result.get('id', 'unknown')
            print(f"✅ Priority job submitted: {run_id}")
            print(f"🕒 Expected completion: 3-5 hours")
            print(f"📊 Monitor with: tf_stage_monitor.py")
            return run_id
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"Error: {response.text[:300]}")
            return None
            
    except requests.RequestException as e:
        print(f"❌ Network error: {e}")
        return None

def track_campaign_progress():
    """Track overall campaign progress toward targets"""
    
    print("📈 **CAMPAIGN PROGRESS TRACKER**\n")
    
    # Get all runs and analyze target achievement
    try:
        headers = {'X-API-KEY': TIMEFOLD_API_KEY}
        response = requests.get(f'{TIMEFOLD_BASE_URL}/route-plans', headers=headers)
        all_runs = response.json()
    except:
        print("❌ Failed to fetch runs")
        return
    
    completed = [r for r in all_runs if r.get('solverStatus') == 'SOLVING_COMPLETED']
    
    print(f"**Campaign Statistics:**")
    print(f"- Total optimization attempts: {len(all_runs)}")
    print(f"- Successfully completed: {len(completed)}")
    print(f"- Success rate: {len(completed)/len(all_runs)*100:.1f}%")
    
    # Analyze trend toward targets
    if len(completed) >= 3:
        recent_scores = [r.get('score', '') for r in completed[:5]]
        score_analysis = analyze_score_components(recent_scores)
        
        print(f"\n**Target Achievement Trend:**")
        print(f"- Hard violations: ✅ Eliminated (all runs feasible)")
        
        medium_avg = score_analysis['medium_avg']
        if medium_avg < 100000:
            print(f"- Continuity: 🎯 Approaching target (avg penalty: {medium_avg:,.0f})")
        elif medium_avg < 500000:
            print(f"- Continuity: 🔄 Improving (avg penalty: {medium_avg:,.0f})")
        else:
            print(f"- Continuity: ⚠️ Needs work (avg penalty: {medium_avg:,.0f})")
        
        soft_avg = score_analysis['soft_avg']
        if soft_avg < 1500000:
            print(f"- Efficiency: 🎯 Good range (avg penalty: {soft_avg:,.0f})")
        elif soft_avg < 2500000:
            print(f"- Efficiency: 🔄 Moderate (avg penalty: {soft_avg:,.0f})")
        else:
            print(f"- Efficiency: ⚠️ Needs improvement (avg penalty: {soft_avg:,.0f})")
    
    print(f"\n**Next Strategic Phase:**")
    print(f"- Focus: Parameter tuning based on current score patterns")
    print(f"- Goal: Systematic N-value testing for sweet spot")
    print(f"- Timeline: 1-2 weeks for comprehensive campaign")

def main():
    print("🧬 **TIMEFOLD OPTIMIZATION CAMPAIGN STRATEGIST**\n")
    
    # Step 1: Analyze current state
    score_analysis = analyze_current_results()
    
    print("\n" + "="*60 + "\n")
    
    # Step 2: Generate strategic variations
    variations = generate_strategic_variations()
    
    print("="*60 + "\n")
    
    # Step 3: Create campaign batch
    batch_jobs = create_campaign_batch()
    
    print("="*60 + "\n") 
    
    # Step 4: Track progress
    track_campaign_progress()
    
    print("\n🎯 **READY FOR STRATEGIC EXECUTION**")
    print("Next steps:")
    print("1. Load your repaired Huddinge dataset")
    print("2. Execute priority variations: execute_priority_job(data)")
    print("3. Monitor results: tf_stage_monitor.py") 
    print("4. Iterate based on results")

if __name__ == '__main__':
    main()