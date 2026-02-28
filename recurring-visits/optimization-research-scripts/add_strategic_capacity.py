#!/usr/bin/env python3
"""
Add Strategic Capacity - Modify input to add 15 vehicles for continuity optimization
"""

import json
import copy
import uuid
from datetime import datetime

def generate_unique_shift_id():
    """Generate a unique shift ID"""
    return str(uuid.uuid4())[:8]

def create_additional_vehicles(original_vehicles, num_to_add=15):
    """Create additional vehicles based on existing patterns"""
    
    additional_vehicles = []
    base_vehicle_count = len(original_vehicles)
    
    for i in range(num_to_add):
        # Use modulo to cycle through existing vehicle patterns
        template_vehicle = original_vehicles[i % len(original_vehicles)]
        
        new_vehicle_id = f"Driver-{base_vehicle_count + i + 1:02d}"
        
        # Deep copy the template vehicle
        new_vehicle = copy.deepcopy(template_vehicle)
        new_vehicle['id'] = new_vehicle_id
        
        # Generate new unique shift IDs for all shifts
        for shift in new_vehicle.get('shifts', []):
            shift['id'] = generate_unique_shift_id()
            
            # Update required breaks with new IDs
            for break_item in shift.get('requiredBreaks', []):
                break_item['id'] = f"{shift['id']}_break"
        
        additional_vehicles.append(new_vehicle)
        print(f"Created vehicle: {new_vehicle_id} with {len(new_vehicle.get('shifts', []))} shifts")
    
    return additional_vehicles

def modify_input_for_capacity_test(input_file, output_file, additional_vehicles=15):
    """Modify input dataset to add strategic capacity for continuity testing"""
    
    print(f"🧬 **ADDING STRATEGIC CAPACITY (+{additional_vehicles} vehicles)**")
    print("="*60)
    
    # Load original input
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    model_input = data.get('modelInput', data)
    
    original_vehicles = model_input.get('vehicles', [])
    original_visits = model_input.get('visits', [])
    
    print(f"Original configuration:")
    print(f"  - Vehicles: {len(original_vehicles)}")
    print(f"  - Visits: {len(original_visits)}")
    
    # Create additional vehicles
    print(f"\nCreating {additional_vehicles} additional vehicles...")
    new_vehicles = create_additional_vehicles(original_vehicles, additional_vehicles)
    
    # Combine original + new vehicles
    all_vehicles = original_vehicles + new_vehicles
    
    print(f"\nNew configuration:")
    print(f"  - Vehicles: {len(all_vehicles)} (+{len(new_vehicles)})")
    print(f"  - Visits: {len(original_visits)} (unchanged)")
    print(f"  - Expected impact: Better continuity control with additional capacity")
    
    # Update the model input
    modified_data = copy.deepcopy(data)
    if 'modelInput' in modified_data:
        modified_data['modelInput']['vehicles'] = all_vehicles
    else:
        modified_data['vehicles'] = all_vehicles
    
    # Add metadata about the modification
    if 'metadata' not in modified_data:
        modified_data['metadata'] = {}
    
    modified_data['metadata'].update({
        'modification': 'strategic_capacity_increase',
        'vehicles_added': additional_vehicles,
        'original_vehicles': len(original_vehicles),
        'total_vehicles': len(all_vehicles),
        'campaign': 'continuity_optimization',
        'timestamp': datetime.now().isoformat(),
        'baseline_run': '41ce610c-bd67-47b8-9e62-7820f87ffcdd',
        'expected_improvements': {
            'poor_continuity_rate': 'from 37% to 12-15%',
            'unassigned_visits': 'from 42 to 25-30',
            'worst_case_continuity': 'from 28 to ≤20 caregivers'
        }
    })
    
    # Save modified input
    with open(output_file, 'w') as f:
        json.dump(modified_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Modified input saved: {output_file}")
    print(f"Ready for Timefold submission!")
    
    return modified_data

def main():
    input_file = 'baseline_input.json'
    output_file = 'strategic_capacity_input.json'
    
    modify_input_for_capacity_test(input_file, output_file, additional_vehicles=15)

if __name__ == '__main__':
    main()