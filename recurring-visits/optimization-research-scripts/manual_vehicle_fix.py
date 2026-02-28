#!/usr/bin/env python3
"""
Manual Vehicle Reference Fix
Based on reported Timefold errors - fixes without API access
"""

import json
import re
from collections import defaultdict

def analyze_error_text(error_text):
    """Parse the error text provided by user to extract vehicle issues"""
    
    vehicle_errors = defaultdict(list)
    
    # Split by lines and find vehicle reference errors
    lines = error_text.split('.')
    
    for line in lines:
        if 'requiredVehicles' in line and 'non-existing vehicle' in line:
            # Extract visit and vehicle info
            # Pattern: Visit (1173) 'requiredVehicles' references a non-existing vehicle (städ)
            
            visit_match = re.search(r'Visit \((\d+)\)', line)
            vehicle_match = re.search(r'non-existing vehicle \(([^)]+)\)', line)
            
            if visit_match and vehicle_match:
                visit_id = visit_match.group(1)
                vehicle_id = vehicle_match.group(1)
                
                vehicle_errors[vehicle_id].append(visit_id)
    
    return dict(vehicle_errors)

def generate_fix_strategy(vehicle_errors):
    """Generate repair strategy based on identified issues"""
    
    print("🧬 **MANUAL VEHICLE REFERENCE FIX**\n")
    
    print("**Identified Issues:**")
    for vehicle_id, visit_ids in vehicle_errors.items():
        print(f"- **{vehicle_id}**: {len(visit_ids)} visits affected")
        if len(visit_ids) <= 10:
            print(f"  - Visits: {', '.join(visit_ids)}")
        else:
            print(f"  - Visits: {', '.join(visit_ids[:10])} (+{len(visit_ids)-10} more)")
    
    print(f"\n**Total missing vehicles:** {len(vehicle_errors)}")
    print(f"**Total affected visits:** {sum(len(visits) for visits in vehicle_errors.values())}")
    
    # Generate specific fixes
    print("\n**RECOMMENDED FIX STRATEGY:**")
    
    for vehicle_id, visit_ids in vehicle_errors.items():
        print(f"\n### Fix for '{vehicle_id}':")
        
        if vehicle_id == 'städ':
            print("```python")
            print("# Option 1: Remove cleaning vehicle constraint")
            print(f"visit_ids_to_fix = {visit_ids}")
            print("for visit in input_data['visits']:")
            print("    if str(visit['id']) in visit_ids_to_fix:")
            print("        if 'requiredVehicles' in visit:")
            print("            visit['requiredVehicles'] = [v for v in visit['requiredVehicles'] if v != 'städ']")
            print("            if not visit['requiredVehicles']:  # Empty list")
            print("                del visit['requiredVehicles']")
            print()
            print("# Option 2: Add cleaning vehicle definition")
            print("cleaning_vehicle = {")
            print("    'id': 'städ',")
            print("    'shifts': [{")
            print("        'id': 'städ-shift-1',")
            print("        'start': '2026-02-27T08:00:00',")
            print("        'end': '2026-02-27T16:00:00',")
            print("        'startLocation': {'latitude': 59.3293, 'longitude': 18.0686},")
            print("        'endLocation': {'latitude': 59.3293, 'longitude': 18.0686},")
            print("    }],")
            print("    'skillSet': ['cleaning'],")
            print("    'capacity': 50,")
            print("}")
            print("input_data.setdefault('vehicles', []).append(cleaning_vehicle)")
            print("```")
            
        elif vehicle_id.startswith('Driver-'):
            driver_num = vehicle_id.split('-')[1]
            print("```python")
            print("# Option 1: Remove specific driver constraint")
            print(f"visit_ids_to_fix = {visit_ids}")
            print("for visit in input_data['visits']:")
            print("    if str(visit['id']) in visit_ids_to_fix:")
            print("        if 'requiredVehicles' in visit:")
            print(f"            visit['requiredVehicles'] = [v for v in visit['requiredVehicles'] if v != '{vehicle_id}']")
            print("            if not visit['requiredVehicles']:")
            print("                del visit['requiredVehicles']")
            print()
            print("# Option 2: Add driver vehicle definition") 
            print(f"driver_vehicle = {{")
            print(f"    'id': '{vehicle_id}',")
            print(f"    'shifts': [{{")
            print(f"        'id': '{vehicle_id}-shift-1',")
            print("        'start': '2026-02-27T08:00:00',")
            print("        'end': '2026-02-27T16:00:00',")
            print("        'startLocation': {'latitude': 59.3293, 'longitude': 18.0686},")
            print("        'endLocation': {'latitude': 59.3293, 'longitude': 18.0686},")
            print("    }],")
            print("    'skillSet': ['driver', 'transport'],")
            print("    'capacity': 100,")
            print("}")
            print("input_data.setdefault('vehicles', []).append(driver_vehicle)")
            print("```")
    
    return vehicle_errors

def create_comprehensive_fix_script(vehicle_errors):
    """Create a comprehensive fix script"""
    
    all_vehicle_ids = list(vehicle_errors.keys())
    all_visit_ids = []
    for visits in vehicle_errors.values():
        all_visit_ids.extend(visits)
    
    script = f'''#!/usr/bin/env python3
"""
COMPREHENSIVE VEHICLE REFERENCE FIX
Auto-generated fix for Timefold optimization data

Missing Vehicles: {all_vehicle_ids}
Affected Visits: {len(all_visit_ids)} visits
"""

import json

def fix_vehicle_references(input_data):
    """
    Fix vehicle reference mismatches in Timefold input data
    Strategy: Remove missing vehicle constraints + Add basic vehicle definitions
    """
    
    missing_vehicles = {set(all_vehicle_ids)}
    visits_fixed = 0
    vehicles_added = 0
    
    print("🔧 Fixing vehicle reference issues...")
    
    # Step 1: Fix affected visits
    for visit in input_data.get('visits', []):
        visit_id = str(visit.get('id', ''))
        
        if 'requiredVehicles' in visit:
            required = visit['requiredVehicles']
            
            # Remove missing vehicles from requirements
            fixed_required = [v for v in required if v not in missing_vehicles]
            
            if len(fixed_required) != len(required):
                print(f"Visit {{visit_id}}: {{required}} → {{fixed_required}}")
                
                if fixed_required:
                    visit['requiredVehicles'] = fixed_required
                else:
                    del visit['requiredVehicles']  # Remove empty constraint
                
                visits_fixed += 1
    
    # Step 2: Add basic vehicle definitions for missing vehicles
    existing_vehicles = {{v['id'] for v in input_data.get('vehicles', [])}}
    
    for vehicle_id in missing_vehicles:
        if vehicle_id not in existing_vehicles:
            
            # Default vehicle configuration
            new_vehicle = {{
                'id': vehicle_id,
                'shifts': [{{
                    'id': f'{{vehicle_id}}-shift-1',
                    'start': '2026-02-27T08:00:00',
                    'end': '2026-02-27T16:00:00', 
                    'startLocation': {{'latitude': 59.3293, 'longitude': 18.0686}},
                    'endLocation': {{'latitude': 59.3293, 'longitude': 18.0686}},
                }}],
                'skillSet': [],
                'capacity': 100,
            }}
            
            # Customize based on vehicle type
            if vehicle_id == 'städ':
                new_vehicle['skillSet'] = ['cleaning']
                new_vehicle['capacity'] = 50
            elif vehicle_id.startswith('Driver-'):
                new_vehicle['skillSet'] = ['driver', 'transport']
                new_vehicle['capacity'] = 100
            
            input_data.setdefault('vehicles', []).append(new_vehicle)
            vehicles_added += 1
            
            print(f"Added vehicle: {{vehicle_id}}")
    
    print(f"\\n✅ **Fix Summary:**")
    print(f"- Visits updated: {{visits_fixed}}")
    print(f"- Vehicles added: {{vehicles_added}}")
    
    return input_data

def validate_fix(input_data):
    """Validate that all vehicle references are now valid"""
    
    vehicle_ids = {{v['id'] for v in input_data.get('vehicles', [])}}
    issues_found = []
    
    for visit in input_data.get('visits', []):
        if 'requiredVehicles' in visit:
            for req_vehicle in visit['requiredVehicles']:
                if req_vehicle not in vehicle_ids:
                    issues_found.append(f"Visit {{visit['id']}} still references missing vehicle: {{req_vehicle}}")
    
    if issues_found:
        print(f"\\n⚠️ **Validation Issues Found:**")
        for issue in issues_found[:10]:  # Show first 10
            print(f"- {{issue}}")
        if len(issues_found) > 10:
            print(f"- ... and {{len(issues_found) - 10}} more")
        return False
    else:
        print(f"\\n✅ **Validation Passed:** All vehicle references are valid")
        return True

# Usage Example:
if __name__ == '__main__':
    # Load your Timefold input data
    # with open('your_timefold_input.json', 'r') as f:
    #     input_data = json.load(f)
    
    # Apply fixes
    # fixed_data = fix_vehicle_references(input_data)
    
    # Validate fixes
    # if validate_fix(fixed_data):
    #     print("Ready to submit to Timefold!")
    #     # Save fixed data
    #     # with open('fixed_timefold_input.json', 'w') as f:
    #     #     json.dump(fixed_data, f, indent=2)
    
    print("\\n🧬 **Vehicle Reference Fix Script Ready**")
    print("Load your Timefold input JSON and run fix_vehicle_references(data)")
'''
    
    with open('comprehensive_vehicle_fix.py', 'w') as f:
        f.write(script)
    
    print(f"\n✅ **Comprehensive fix script created: `comprehensive_vehicle_fix.py`**")

def main():
    # The error text from user's message
    error_text = """Visit (1173) 'requiredVehicles' references a non-existing vehicle (städ). Visit (1174) 'requiredVehicles' references a non-existing vehicle (städ). Visit (2911) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2912) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2913) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2914) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2915) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2916) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2917) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2918) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2919) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2920) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2921) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2922) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2923) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2924) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2925) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2926) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2927) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2928) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2991) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2992) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2993) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2994) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2995) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2996) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2997) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2998) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (2999) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3000) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3001) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3002) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3003) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3004) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3005) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3006) 'requiredVehicles' references a non-existing vehicle (Driver-38). Visit (3007) 'requiredVehicles' references a non-existing vehicle (Driver-38)."""
    
    vehicle_errors = analyze_error_text(error_text)
    generate_fix_strategy(vehicle_errors)
    create_comprehensive_fix_script(vehicle_errors)
    
    print(f"\n📋 **MANUAL FIX SUMMARY:**")
    print(f"- **Network blocked:** Cannot fetch runs directly from Timefold API")
    print(f"- **Errors identified:** {len(vehicle_errors)} missing vehicles")
    print(f"- **Fix script ready:** Run on your Timefold input data")
    print(f"- **Next:** Apply fix → Resubmit jobs → Resume optimization")

if __name__ == '__main__':
    main()