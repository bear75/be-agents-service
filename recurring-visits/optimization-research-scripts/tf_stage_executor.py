#!/usr/bin/env python3
"""
Timefold Stage Executor
Systematic execution of repairs and optimization campaign resumption
"""

import json
import os
import requests
import time
from datetime import datetime

# Import our repair modules
from fix_vehicleshift_conflicts import fix_duplicate_vehicleshift_ids, validate_vehicleshift_ids
from comprehensive_vehicle_fix import fix_vehicle_references, validate_fix

TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def load_dataset(file_path):
    """Load Timefold input dataset"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Dataset file not found: {file_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Invalid JSON in {file_path}: {e}")
        return None

def apply_comprehensive_repairs(input_data):
    """Apply all identified repairs to the dataset"""
    
    print("🔧 **APPLYING COMPREHENSIVE REPAIRS**\n")
    
    total_fixes = 0
    
    # Step 1: Fix VehicleShift ID conflicts
    print("1. 🆔 Fixing VehicleShift ID conflicts...")
    fixed_data, vehicleshift_fixes = fix_duplicate_vehicleshift_ids(input_data, strategy='suffix')
    total_fixes += vehicleshift_fixes
    
    # Step 2: Fix vehicle reference issues
    print("\n2. 🚗 Fixing vehicle reference issues...")
    fixed_data, vehicle_fixes = fix_vehicle_references(fixed_data)
    total_fixes += vehicle_fixes
    
    # Step 3: Validate all repairs
    print("\n3. ✅ Validating repairs...")
    vehicleshift_valid = validate_vehicleshift_ids(fixed_data)
    vehicle_valid = validate_fix(fixed_data)
    
    if vehicleshift_valid and vehicle_valid:
        print(f"\n🎉 **ALL REPAIRS SUCCESSFUL!**")
        print(f"- Total fixes applied: {total_fixes}")
        print(f"- Dataset ready for Timefold submission")
        return fixed_data, True
    else:
        print(f"\n❌ **VALIDATION FAILED**")
        print(f"- VehicleShift validation: {'✅' if vehicleshift_valid else '❌'}")
        print(f"- Vehicle reference validation: {'✅' if vehicle_valid else '❌'}")
        return fixed_data, False

def submit_to_timefold(input_data, job_name="Huddinge Fixed Dataset"):
    """Submit repaired dataset to Timefold"""
    
    headers = {
        'X-API-KEY': TIMEFOLD_API_KEY,
        'Content-Type': 'application/json'
    }
    
    # Add metadata to the submission
    submission_payload = {
        **input_data,
        'metadata': {
            'name': job_name,
            'timestamp': datetime.now().isoformat(),
            'repaired': True,
            'campaign': '45-job-binary-tree-optimization'
        }
    }
    
    try:
        print(f"🚀 Submitting to Timefold: {job_name}")
        response = requests.post(
            f'{TIMEFOLD_BASE_URL}/route-plans',
            headers=headers,
            json=submission_payload,
            timeout=60
        )
        
        if response.status_code == 200 or response.status_code == 201:
            result = response.json()
            run_id = result.get('id', 'unknown')
            print(f"✅ Submission successful! Run ID: {run_id}")
            return run_id, True
        else:
            print(f"❌ Submission failed: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return None, False
            
    except requests.RequestException as e:
        print(f"❌ Network error during submission: {e}")
        return None, False

def monitor_optimization_run(run_id, max_wait_minutes=30):
    """Monitor an optimization run until completion"""
    
    headers = {'X-API-KEY': TIMEFOLD_API_KEY}
    start_time = time.time()
    max_wait_seconds = max_wait_minutes * 60
    
    print(f"📊 Monitoring run {run_id}...")
    
    while True:
        try:
            response = requests.get(
                f'{TIMEFOLD_BASE_URL}/route-plans/{run_id}',
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                run_data = response.json()
                
                # Extract status from the nested structure
                status = None
                if 'metadata' in run_data:
                    status = run_data['metadata'].get('solverStatus')
                elif 'run' in run_data:
                    status = run_data['run'].get('solverStatus')
                else:
                    status = run_data.get('solverStatus')
                
                print(f"Status: {status}")
                
                if status == 'SOLVING_COMPLETED':
                    print("🎉 Optimization completed successfully!")
                    return analyze_optimization_results(run_data)
                    
                elif status == 'SOLVING_FAILED' or status == 'DATASET_INVALID':
                    print("❌ Optimization failed")
                    
                    # Extract error details
                    error_msg = "Unknown error"
                    if 'metadata' in run_data and 'validationResult' in run_data['metadata']:
                        errors = run_data['metadata']['validationResult'].get('errors', [])
                        if errors:
                            error_msg = '; '.join(errors[:3])  # First 3 errors
                    
                    print(f"Error: {error_msg}")
                    return None
                    
                elif status in ['SOLVING_ACTIVE', 'SOLVING_SCHEDULED']:
                    # Still running - continue monitoring
                    if time.time() - start_time > max_wait_seconds:
                        print(f"⏰ Timeout after {max_wait_minutes} minutes")
                        return None
                    
                    time.sleep(30)  # Wait 30 seconds before next check
                    continue
                else:
                    print(f"⚠️ Unknown status: {status}")
                    time.sleep(10)
                    continue
            else:
                print(f"❌ API error: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"❌ Network error: {e}")
            time.sleep(10)
            continue

def analyze_optimization_results(run_data):
    """Analyze optimization results against our targets"""
    
    print("\n📈 **OPTIMIZATION RESULTS ANALYSIS**\n")
    
    # Extract key metrics (structure may vary)
    # This is a simplified extraction - adapt based on actual Timefold response structure
    
    score = None
    if 'metadata' in run_data:
        score = run_data['metadata'].get('score')
    elif 'run' in run_data:
        score = run_data['run'].get('score')
    
    print(f"Raw Score: {score}")
    
    # TODO: Extract specific metrics when we have the actual response structure
    # For now, return basic success indicator
    
    results = {
        'success': True,
        'run_id': run_data.get('id', 'unknown'),
        'score': score,
        'timestamp': datetime.now().isoformat()
    }
    
    return results

def execute_tf_stage(input_file_path):
    """Main execution function for Timefold stage"""
    
    print("🧬 **TIMEFOLD STAGE EXECUTION**")
    print("="*50)
    
    # Step 1: Load dataset
    print(f"\n📂 Loading dataset: {input_file_path}")
    input_data = load_dataset(input_file_path)
    if not input_data:
        return False
    
    print(f"✅ Dataset loaded: {len(input_data.get('vehicles', []))} vehicles, {len(input_data.get('visits', []))} visits")
    
    # Step 2: Apply comprehensive repairs
    print(f"\n🔧 Applying repairs...")
    repaired_data, repair_success = apply_comprehensive_repairs(input_data)
    
    if not repair_success:
        print("❌ Repair validation failed - cannot proceed")
        return False
    
    # Step 3: Save repaired dataset
    repaired_file = input_file_path.replace('.json', '_repaired.json')
    print(f"\n💾 Saving repaired dataset: {repaired_file}")
    with open(repaired_file, 'w') as f:
        json.dump(repaired_data, f, indent=2)
    
    # Step 4: Submit to Timefold
    print(f"\n🚀 Submitting to Timefold...")
    run_id, submit_success = submit_to_timefold(repaired_data)
    
    if not submit_success:
        print("❌ Submission failed - manual intervention required")
        return False
    
    # Step 5: Monitor optimization
    print(f"\n📊 Monitoring optimization...")
    results = monitor_optimization_run(run_id)
    
    if results:
        print(f"\n🎯 **OPTIMIZATION COMPLETE**")
        print(f"- Run ID: {results['run_id']}")
        print(f"- Score: {results['score']}")
        print(f"- Ready for metrics analysis")
        return True
    else:
        print(f"\n❌ Optimization monitoring failed")
        return False

def main():
    print("🧬 **TIMEFOLD STAGE EXECUTOR READY**")
    print("\nTo proceed with Timefold stage:")
    print("1. Place your Timefold input JSON file in current directory")
    print("2. Run: execute_tf_stage('your_input_file.json')")
    print("\nExample:")
    print("  python3 tf_stage_executor.py")
    print("  # Then in Python:")
    print("  execute_tf_stage('huddinge_timefold_input.json')")
    
    # Check if we have a likely input file
    json_files = [f for f in os.listdir('.') if f.endswith('.json') and 'timefold' in f.lower()]
    if json_files:
        print(f"\nFound potential input files:")
        for f in json_files:
            print(f"- {f}")
        
        # Auto-execute if only one candidate
        if len(json_files) == 1:
            auto_file = json_files[0]
            print(f"\n🚀 Auto-executing with: {auto_file}")
            success = execute_tf_stage(auto_file)
            print(f"\nExecution result: {'✅ SUCCESS' if success else '❌ FAILED'}")

if __name__ == '__main__':
    main()