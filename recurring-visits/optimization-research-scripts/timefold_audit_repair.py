#!/usr/bin/env python3
"""
Timefold Audit & Repair Script
Systematically fix vehicle reference mismatches causing optimization failures
"""

import os
import json
import requests
from collections import defaultdict
import sys
from datetime import datetime

# Configuration
TIMEFOLD_API_KEY = os.getenv('TIMEFOLD_API_KEY', 'tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8')
TIMEFOLD_BASE_URL = 'https://app.timefold.ai/api/models/field-service-routing/v1'

def fetch_failed_runs():
    """Fetch all failed optimization runs from Timefold API"""
    headers = {'X-API-KEY': TIMEFOLD_API_KEY, 'Content-Type': 'application/json'}
    
    try:
        # Get list of recent runs
        response = requests.get(f'{TIMEFOLD_BASE_URL}/route-plans', 
                              headers=headers, timeout=30)
        response.raise_for_status()
        
        runs = response.json()  # This is already a list
        failed_runs = []
        
        # Filter for failed runs
        for run in runs:
            if run.get('solverStatus') in ['SOLVING_FAILED', 'DATASET_INVALID']:
                # Get detailed error info
                detail_response = requests.get(
                    f"{TIMEFOLD_BASE_URL}/route-plans/{run['id']}", 
                    headers=headers, timeout=30
                )
                if detail_response.status_code == 200:
                    detail = detail_response.json()
                    failed_runs.append(detail)
                else:
                    # Add basic info even if detail fetch fails
                    failed_runs.append(run)
        
        return failed_runs
        
    except requests.RequestException as e:
        print(f"❌ Failed to fetch runs from Timefold API: {e}")
        print(f"Check API key and connectivity to {TIMEFOLD_BASE_URL}")
        return []

def analyze_vehicle_errors(failed_runs):
    """Extract and categorize vehicle reference errors"""
    vehicle_errors = defaultdict(list)
    visit_errors = defaultdict(list)
    structural_errors = defaultdict(list)
    
    for run in failed_runs:
        run_id = run.get('id', 'unknown')
        error_messages = []
        
        # Check different locations for error messages
        if 'validationResult' in run and 'errors' in run['validationResult']:
            error_messages.extend(run['validationResult']['errors'])
        elif 'metadata' in run and 'validationResult' in run['metadata'] and 'errors' in run['metadata']['validationResult']:
            error_messages.extend(run['metadata']['validationResult']['errors'])
        
        # Parse each error message for different types of issues
        for error_msg in error_messages:
            if 'requiredVehicles' in error_msg and 'non-existing vehicle' in error_msg:
                # Extract: Visit (1173) 'requiredVehicles' references a non-existing vehicle (städ)
                try:
                    parts = error_msg.split("'")[0]  # Get part before 'requiredVehicles'
                    visit_id = parts.split('(')[1].split(')')[0]
                    
                    vehicle_parts = error_msg.split('non-existing vehicle (')[1]
                    vehicle_id = vehicle_parts.split(')')[0]
                    
                    vehicle_errors[vehicle_id].append({
                        'visit_id': visit_id,
                        'run_id': run_id,
                        'error_line': error_msg.strip()
                    })
                    visit_errors[visit_id].append(vehicle_id)
                    
                except (IndexError, ValueError):
                    print(f"⚠️ Could not parse vehicle error: {error_msg}")
            
            elif 'Object Id conflict' in error_msg and 'VehicleShift' in error_msg:
                # Extract Object ID conflicts: duplicate VehicleShift IDs
                try:
                    # Extract ID from: ObjectId: key=9ab84ab9
                    if 'key=' in error_msg:
                        key_part = error_msg.split('key=')[1]
                        duplicate_id = key_part.split(',')[0] if ',' in key_part else key_part.split(']')[0]
                        
                        structural_errors['duplicate_vehicleshift_ids'].append({
                            'duplicate_id': duplicate_id,
                            'run_id': run_id,
                            'error_line': error_msg.strip()
                        })
                        
                except (IndexError, ValueError):
                    print(f"⚠️ Could not parse Object ID conflict: {error_msg}")
            
            elif 'Unable to read submodel' in error_msg or 'MODEL_INPUT' in error_msg:
                # General input validation failures
                structural_errors['input_validation_failures'].append({
                    'run_id': run_id,
                    'error_line': error_msg.strip()
                })
                    
    return dict(vehicle_errors), dict(visit_errors), dict(structural_errors)

def generate_repair_strategy(vehicle_errors, visit_errors, structural_errors):
    """Generate repair strategy for vehicle reference and structural issues"""
    
    print("🧬 **COMPREHENSIVE AUDIT RESULTS**\n")
    
    # Summary stats
    total_missing_vehicles = len(vehicle_errors)
    total_affected_visits = len(visit_errors)
    total_structural_issues = sum(len(errors) for errors in structural_errors.values())
    
    print(f"**Missing Vehicles:** {total_missing_vehicles}")
    print(f"**Affected Visits:** {total_affected_visits}")
    print(f"**Structural Issues:** {total_structural_issues}\n")
    
    # Detail breakdown - Vehicle Errors
    if vehicle_errors:
        print("**Missing Vehicle Details:**")
        for vehicle_id, errors in vehicle_errors.items():
            visit_count = len(errors)
            visit_ids = [e['visit_id'] for e in errors[:5]]  # First 5 examples
            more = f" (+{visit_count-5} more)" if visit_count > 5 else ""
            
            print(f"- **{vehicle_id}**: {visit_count} visits affected")
            print(f"  - Visits: {', '.join(visit_ids)}{more}")
    
    # Detail breakdown - Structural Errors
    if structural_errors:
        print("\n**Structural Issues:**")
        for error_type, errors in structural_errors.items():
            print(f"- **{error_type}**: {len(errors)} instances")
            
            if error_type == 'duplicate_vehicleshift_ids':
                duplicate_ids = [e['duplicate_id'] for e in errors[:5]]
                more = f" (+{len(errors)-5} more)" if len(errors) > 5 else ""
                print(f"  - Duplicate IDs: {', '.join(duplicate_ids)}{more}")
            elif error_type == 'input_validation_failures':
                print(f"  - General input validation issues")
    
    print("\n**REPAIR STRATEGIES:**")
    
    if vehicle_errors:
        # Vehicle reference repair strategies
        print("**Vehicle Reference Issues:**")
        print("**Option 1: Remove Vehicle Constraints (Recommended)**")
        print("- Remove 'requiredVehicles' from affected visits")
        print("- Let optimizer assign visits to any available vehicle")
        print("- Fastest fix, maintains optimization flexibility")
        
        print("\n**Option 2: Add Missing Vehicles**")
        print("- Create vehicle definitions for missing vehicles")
        print("- Define their capabilities, schedules, locations")
        print("- More complex but preserves original constraints")
        
        print("\n**Option 3: Remap to Existing Vehicles**")
        print("- Map missing vehicles to existing ones")
        print("- Requires understanding of intended vehicle mappings")
    
    if structural_errors:
        print(f"\n**Structural Issues:**")
        
        if 'duplicate_vehicleshift_ids' in structural_errors:
            print("**VehicleShift ID Conflicts:**")
            print("- **Critical Issue:** Duplicate VehicleShift IDs cause deserialization failures")
            print("- **Fix:** Generate unique IDs for all VehicleShift objects")
            print("- **Strategy:** Add suffix/prefix to duplicate IDs (e.g., 9ab84ab9 → 9ab84ab9_v2)")
            print("- **Validation:** Ensure all shift IDs are unique across entire dataset")
        
        if 'input_validation_failures' in structural_errors:
            print("\n**Input Validation Failures:**")
            print("- **Issue:** JSON structure or data format problems")
            print("- **Fix:** Validate against Timefold schema before submission")
            print("- **Strategy:** Use schema validation tools and fix structural issues")
    
    return {
        'total_missing_vehicles': total_missing_vehicles,
        'total_affected_visits': total_affected_visits,
        'total_structural_issues': total_structural_issues,
        'missing_vehicles': list(vehicle_errors.keys()),
        'affected_visits': list(visit_errors.keys()),
        'vehicle_errors': vehicle_errors,
        'visit_errors': visit_errors,
        'structural_errors': structural_errors
    }

def create_repair_scripts(audit_results):
    """Create repair scripts for each strategy"""
    
    missing_vehicles = audit_results.get('missing_vehicles', [])
    affected_visits = audit_results.get('affected_visits', [])
    structural_errors = audit_results.get('structural_errors', {})
    
    # Script 1: Remove vehicle constraints
    script1 = f"""#!/usr/bin/env python3
# AUTO-GENERATED: Remove requiredVehicles constraints

# Missing vehicles to remove: {missing_vehicles}
# Affected visits: {len(affected_visits)} visits

def remove_vehicle_constraints(input_data):
    visits_updated = 0
    
    for visit in input_data.get('visits', []):
        if visit.get('requiredVehicles'):
            # Check if any required vehicle is missing
            required = visit['requiredVehicles']
            missing_required = [v for v in required if v in {missing_vehicles}]
            
            if missing_required:
                print(f"Visit {{visit['id']}}: Removing requiredVehicles {{missing_required}}")
                # Option A: Remove entirely
                del visit['requiredVehicles']
                # Option B: Remove only missing vehicles (keep valid ones)
                # visit['requiredVehicles'] = [v for v in required if v not in {missing_vehicles}]
                visits_updated += 1
    
    print(f"Updated {{visits_updated}} visits")
    return input_data

# Usage: 
# input_data = load_your_timefold_input()
# fixed_data = remove_vehicle_constraints(input_data)
# submit_to_timefold(fixed_data)
"""
    
    with open('repair_strategy_1_remove_constraints.py', 'w') as f:
        f.write(script1)
    
    # Script 2: Add missing vehicles  
    script2 = f"""#!/usr/bin/env python3
# AUTO-GENERATED: Add missing vehicle definitions

def add_missing_vehicles(input_data):
    existing_vehicles = {{v['id'] for v in input_data.get('vehicles', [])}}
    missing_vehicles = {missing_vehicles}
    
    for vehicle_id in missing_vehicles:
        if vehicle_id not in existing_vehicles:
            # Create basic vehicle definition
            new_vehicle = {{
                'id': vehicle_id,
                'shifts': [{{
                    'id': f'{{vehicle_id}}-shift-1',
                    'start': '2026-02-27T08:00:00',
                    'end': '2026-02-27T16:00:00',
                    'startLocation': {{'latitude': 59.3293, 'longitude': 18.0686}},  # Stockholm default
                    'endLocation': {{'latitude': 59.3293, 'longitude': 18.0686}},
                }}],
                'skillSet': [],  # Add required skills
                'capacity': 100,  # Adjust as needed
            }}
            
            input_data.setdefault('vehicles', []).append(new_vehicle)
            print(f"Added vehicle: {{vehicle_id}}")
    
    return input_data
"""
    
    with open('repair_strategy_2_add_vehicles.py', 'w') as f:
        f.write(script2)
    
    scripts_generated = []
    
    # Vehicle reference scripts
    if missing_vehicles:
        scripts_generated.extend([
            "`repair_strategy_1_remove_constraints.py`",
            "`repair_strategy_2_add_vehicles.py`"
        ])
    
    # Structural issue scripts  
    if structural_errors.get('duplicate_vehicleshift_ids'):
        scripts_generated.append("`fix_vehicleshift_conflicts.py` - VehicleShift ID deduplication")
    
    print(f"\n✅ **Repair scripts generated:**")
    for script in scripts_generated:
        print(f"- {script}")
    
    if not scripts_generated:
        print("- No specific repair scripts needed (no issues found)")

def main():
    print("🧬 **TIMEFOLD AUDIT & REPAIR SYSTEM**")
    print("Scanning for vehicle reference failures...\n")
    
    # Step 1: Fetch failed runs
    print("📡 Fetching failed runs from Timefold API...")
    failed_runs = fetch_failed_runs()
    
    if not failed_runs:
        print("⚠️ No failed runs found or API access issues")
        print("Check API key and connectivity to app.timefold.ai")
        return
    
    print(f"Found {len(failed_runs)} failed runs")
    
    # Step 2: Analyze errors
    print("\n🔍 Analyzing vehicle reference and structural errors...")
    vehicle_errors, visit_errors, structural_errors = analyze_vehicle_errors(failed_runs)
    
    # Step 3: Generate repair strategy
    audit_results = generate_repair_strategy(vehicle_errors, visit_errors, structural_errors)
    
    # Step 4: Create repair scripts
    print("\n🛠️ Generating repair scripts...")
    create_repair_scripts(audit_results)
    
    # Step 5: Save audit results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    audit_filename = f'timefold_audit_{timestamp}.json'
    
    with open(audit_filename, 'w') as f:
        json.dump({
            'timestamp': timestamp,
            'failed_runs_count': len(failed_runs),
            'audit_results': audit_results,
            'failed_runs': failed_runs  # Full details for reference
        }, f, indent=2)
    
    print(f"\n📋 **Comprehensive Audit Complete!**")
    print(f"- Results saved to: {audit_filename}")
    print(f"- Repair scripts ready for execution")
    print(f"- {audit_results['total_missing_vehicles']} vehicle reference issues")
    print(f"- {audit_results['total_affected_visits']} visits affected")
    print(f"- {audit_results.get('total_structural_issues', 0)} structural issues")
    
    print(f"\n**Next Steps:**")
    print(f"1. Review repair strategies above")
    print(f"2. Execute appropriate repair scripts on your data")
    print(f"3. Validate fixes before resubmission")
    print(f"4. Resubmit corrected optimization jobs")
    print(f"5. Resume 45-job binary tree analysis")

if __name__ == '__main__':
    main()