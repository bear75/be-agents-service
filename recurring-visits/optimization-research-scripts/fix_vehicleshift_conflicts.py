#!/usr/bin/env python3
"""
VehicleShift ID Conflict Repair Script
Fixes duplicate VehicleShift IDs that cause Object ID conflicts in Timefold
"""

import json
import uuid
from collections import defaultdict

def analyze_vehicleshift_ids(input_data):
    """Analyze VehicleShift IDs to find duplicates"""
    
    shift_id_usage = defaultdict(list)
    duplicates = {}
    
    vehicles = input_data.get('vehicles', [])
    
    for vehicle_idx, vehicle in enumerate(vehicles):
        shifts = vehicle.get('shifts', [])
        
        for shift_idx, shift in enumerate(shifts):
            shift_id = shift.get('id')
            if shift_id:
                shift_id_usage[shift_id].append({
                    'vehicle_idx': vehicle_idx,
                    'shift_idx': shift_idx,
                    'vehicle_id': vehicle.get('id', f'vehicle_{vehicle_idx}'),
                    'shift': shift
                })
    
    # Find duplicates
    for shift_id, usages in shift_id_usage.items():
        if len(usages) > 1:
            duplicates[shift_id] = usages
    
    return duplicates, shift_id_usage

def fix_duplicate_vehicleshift_ids(input_data, strategy='suffix'):
    """Fix duplicate VehicleShift IDs using specified strategy"""
    
    print("🔧 Analyzing VehicleShift ID conflicts...")
    
    duplicates, shift_id_usage = analyze_vehicleshift_ids(input_data)
    
    if not duplicates:
        print("✅ No VehicleShift ID conflicts found!")
        return input_data, 0
    
    print(f"⚠️ Found {len(duplicates)} duplicate VehicleShift IDs:")
    for shift_id, usages in duplicates.items():
        print(f"  - ID '{shift_id}' used {len(usages)} times")
    
    fixes_applied = 0
    
    for shift_id, usages in duplicates.items():
        print(f"\n🛠️ Fixing duplicate ID: {shift_id}")
        
        # Keep first usage unchanged, modify others
        for i, usage in enumerate(usages[1:], 1):  # Skip first usage
            vehicle_idx = usage['vehicle_idx']
            shift_idx = usage['shift_idx']
            
            if strategy == 'suffix':
                new_id = f"{shift_id}_v{i+1}"
            elif strategy == 'uuid':
                new_id = str(uuid.uuid4())
            elif strategy == 'increment':
                new_id = f"{shift_id}_{i:03d}"
            else:
                # Default: suffix
                new_id = f"{shift_id}_dup_{i}"
            
            # Update the shift ID in the data structure
            input_data['vehicles'][vehicle_idx]['shifts'][shift_idx]['id'] = new_id
            
            print(f"  - Vehicle {usage['vehicle_id']} shift {shift_idx}: {shift_id} → {new_id}")
            fixes_applied += 1
    
    print(f"\n✅ Applied {fixes_applied} VehicleShift ID fixes")
    return input_data, fixes_applied

def validate_vehicleshift_ids(input_data):
    """Validate that all VehicleShift IDs are now unique"""
    
    duplicates, shift_id_usage = analyze_vehicleshift_ids(input_data)
    
    if duplicates:
        print(f"\n❌ Validation failed: Still have {len(duplicates)} duplicate IDs")
        for shift_id, usages in duplicates.items():
            print(f"  - '{shift_id}' still used {len(usages)} times")
        return False
    else:
        total_shifts = sum(len(usages) for usages in shift_id_usage.values())
        print(f"\n✅ Validation passed: All {total_shifts} VehicleShift IDs are unique")
        return True

def fix_other_structural_issues(input_data):
    """Fix other common structural issues"""
    
    fixes_applied = 0
    
    # Ensure all required fields exist
    vehicles = input_data.get('vehicles', [])
    
    for vehicle_idx, vehicle in enumerate(vehicles):
        # Ensure vehicle has required fields
        if 'id' not in vehicle:
            vehicle['id'] = f"vehicle_{vehicle_idx}"
            fixes_applied += 1
        
        shifts = vehicle.get('shifts', [])
        for shift_idx, shift in enumerate(shifts):
            # Ensure shift has required fields
            if 'id' not in shift or shift['id'] is None:
                shift['id'] = f"{vehicle.get('id', f'vehicle_{vehicle_idx}')}_shift_{shift_idx}"
                fixes_applied += 1
    
    if fixes_applied > 0:
        print(f"✅ Applied {fixes_applied} structural fixes")
    
    return input_data, fixes_applied

def main():
    print("🧬 **VEHICLESHIFT ID CONFLICT REPAIR**")
    print("Fixing Object ID conflicts in Timefold input data\n")
    
    # Example usage - replace with your actual file loading
    print("To use this script:")
    print("1. Load your Timefold input JSON:")
    print("   with open('your_timefold_input.json', 'r') as f:")
    print("       input_data = json.load(f)")
    print()
    print("2. Apply fixes:")
    print("   fixed_data, vehicleshift_fixes = fix_duplicate_vehicleshift_ids(input_data)")
    print("   fixed_data, structural_fixes = fix_other_structural_issues(fixed_data)")
    print()
    print("3. Validate and save:")
    print("   if validate_vehicleshift_ids(fixed_data):")
    print("       with open('fixed_input.json', 'w') as f:")
    print("           json.dump(fixed_data, f, indent=2)")
    print("       print('Ready to resubmit to Timefold!')")
    
    print(f"\n🛠️ Available strategies:")
    print(f"- 'suffix': Add _v2, _v3 suffixes (recommended)")
    print(f"- 'uuid': Replace with UUID (ensures uniqueness)")
    print(f"- 'increment': Add _001, _002 suffixes")

if __name__ == '__main__':
    main()