#!/usr/bin/env python3
# AUTO-GENERATED: Add missing vehicle definitions

def add_missing_vehicles(input_data):
    existing_vehicles = {v['id'] for v in input_data.get('vehicles', [])}
    missing_vehicles = ['städ']
    
    for vehicle_id in missing_vehicles:
        if vehicle_id not in existing_vehicles:
            # Create basic vehicle definition
            new_vehicle = {
                'id': vehicle_id,
                'shifts': [{
                    'id': f'{vehicle_id}-shift-1',
                    'start': '2026-02-27T08:00:00',
                    'end': '2026-02-27T16:00:00',
                    'startLocation': {'latitude': 59.3293, 'longitude': 18.0686},  # Stockholm default
                    'endLocation': {'latitude': 59.3293, 'longitude': 18.0686},
                }],
                'skillSet': [],  # Add required skills
                'capacity': 100,  # Adjust as needed
            }
            
            input_data.setdefault('vehicles', []).append(new_vehicle)
            print(f"Added vehicle: {vehicle_id}")
    
    return input_data
