#!/usr/bin/env python3
"""
COMPREHENSIVE VEHICLE REFERENCE FIX
Auto-generated fix for Timefold optimization data

Missing Vehicles: ['städ', 'Driver-38']
Affected Visits: 37 visits
"""

import json

def fix_vehicle_references(input_data):
    """
    Fix vehicle reference mismatches in Timefold input data
    Strategy: Remove missing vehicle constraints + Add basic vehicle definitions
    """
    
    missing_vehicles = {'städ', 'Driver-38'}
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
                print(f"Visit {visit_id}: {required} → {fixed_required}")
                
                if fixed_required:
                    visit['requiredVehicles'] = fixed_required
                else:
                    del visit['requiredVehicles']  # Remove empty constraint
                
                visits_fixed += 1
    
    # Step 2: Add basic vehicle definitions for missing vehicles
    existing_vehicles = {v['id'] for v in input_data.get('vehicles', [])}
    
    for vehicle_id in missing_vehicles:
        if vehicle_id not in existing_vehicles:
            
            # Default vehicle configuration
            new_vehicle = {
                'id': vehicle_id,
                'shifts': [{
                    'id': f'{vehicle_id}-shift-1',
                    'start': '2026-02-27T08:00:00',
                    'end': '2026-02-27T16:00:00', 
                    'startLocation': {'latitude': 59.3293, 'longitude': 18.0686},
                    'endLocation': {'latitude': 59.3293, 'longitude': 18.0686},
                }],
                'skillSet': [],
                'capacity': 100,
            }
            
            # Customize based on vehicle type
            if vehicle_id == 'städ':
                new_vehicle['skillSet'] = ['cleaning']
                new_vehicle['capacity'] = 50
            elif vehicle_id.startswith('Driver-'):
                new_vehicle['skillSet'] = ['driver', 'transport']
                new_vehicle['capacity'] = 100
            
            input_data.setdefault('vehicles', []).append(new_vehicle)
            vehicles_added += 1
            
            print(f"Added vehicle: {vehicle_id}")
    
    print(f"\n✅ **Fix Summary:**")
    print(f"- Visits updated: {visits_fixed}")
    print(f"- Vehicles added: {vehicles_added}")
    
    return input_data

def validate_fix(input_data):
    """Validate that all vehicle references are now valid"""
    
    vehicle_ids = {v['id'] for v in input_data.get('vehicles', [])}
    issues_found = []
    
    for visit in input_data.get('visits', []):
        if 'requiredVehicles' in visit:
            for req_vehicle in visit['requiredVehicles']:
                if req_vehicle not in vehicle_ids:
                    issues_found.append(f"Visit {visit['id']} still references missing vehicle: {req_vehicle}")
    
    if issues_found:
        print(f"\n⚠️ **Validation Issues Found:**")
        for issue in issues_found[:10]:  # Show first 10
            print(f"- {issue}")
        if len(issues_found) > 10:
            print(f"- ... and {len(issues_found) - 10} more")
        return False
    else:
        print(f"\n✅ **Validation Passed:** All vehicle references are valid")
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
    
    print("\n🧬 **Vehicle Reference Fix Script Ready**")
    print("Load your Timefold input JSON and run fix_vehicle_references(data)")
