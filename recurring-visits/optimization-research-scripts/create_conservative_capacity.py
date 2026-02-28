#!/usr/bin/env python3
"""
Create Conservative Capacity Strategy (+8 vehicles)
Based on analysis that +15 vehicles uses all capacity
"""

import json
import copy
import uuid
from datetime import datetime

def create_conservative_strategy():
    """Create conservative capacity increase strategy"""
    
    print("🧬 **CONSERVATIVE CAPACITY STRATEGY (+8 vehicles)**")
    print("Based on current test showing efficiency concerns with +15")
    print("="*60)
    
    # Load original baseline input
    with open('baseline_input.json', 'r') as f:
        data = json.load(f)
    
    model_input = data.get('modelInput', data)
    original_vehicles = model_input.get('vehicles', [])
    
    print(f"Original configuration: {len(original_vehicles)} vehicles")
    
    # Create 8 additional vehicles (conservative approach)
    additional_vehicles = []
    base_vehicle_count = len(original_vehicles)
    
    for i in range(8):  # Conservative: +8 instead of +15
        template_vehicle = original_vehicles[i % len(original_vehicles)]
        new_vehicle_id = f"Driver-{base_vehicle_count + i + 1:02d}"
        
        new_vehicle = copy.deepcopy(template_vehicle)
        new_vehicle['id'] = new_vehicle_id
        
        # Generate unique shift IDs
        for shift in new_vehicle.get('shifts', []):
            shift['id'] = str(uuid.uuid4())[:8]
            
            for break_item in shift.get('requiredBreaks', []):
                break_item['id'] = f"{shift['id']}_break"
        
        additional_vehicles.append(new_vehicle)
        print(f"Created vehicle: {new_vehicle_id}")
    
    # Combine vehicles
    all_vehicles = original_vehicles + additional_vehicles
    
    # Create clean input
    clean_input = {
        'vehicles': all_vehicles,
        'visits': model_input.get('visits', []),
        'visitGroups': model_input.get('visitGroups', [])
    }
    
    print(f"\nConservative configuration:")
    print(f"  - Vehicles: {len(all_vehicles)} (+{len(additional_vehicles)})")
    print(f"  - Visits: {len(clean_input['visits'])} (unchanged)")
    print(f"  - Strategy: Moderate capacity increase")
    print(f"  - Expected: Better efficiency than +15 vehicle test")
    
    # Save conservative input
    with open('conservative_capacity_input.json', 'w') as f:
        json.dump(clean_input, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Conservative input saved: conservative_capacity_input.json")
    print(f"Ready for parallel submission!")
    
    return clean_input

if __name__ == '__main__':
    create_conservative_strategy()