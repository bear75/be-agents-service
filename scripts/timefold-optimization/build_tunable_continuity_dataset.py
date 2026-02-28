#!/usr/bin/env python3
"""
Tunable Continuity Dataset Builder

Implements Björn's refined approach:
- Continuity = Σ(slingas) × (preferred_vehicles_per_slinga)
- Tunable parameter for efficiency/continuity trade-off
- Iterative optimization capability
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime

def build_geo_slinga_structure(preferred_vehicles_per_slinga):
    """
    Define employee structure with tunable preferred vehicles per slinga
    
    Args:
        preferred_vehicles_per_slinga (int): Number of preferred vehicles allowed per slinga
    """
    # Base structure with enough vehicles to support the preference level
    base_structure = {
        'North-Huddinge': {
            'DAG': ['DAG-North-01', 'DAG-North-02', 'DAG-North-03', 'DAG-North-04'],
            'KVÄLL': ['KVALL-North-01', 'KVALL-North-02', 'KVALL-North-03'],
            'NATT': ['NATT-North-01']
        },
        'South-Huddinge': {
            'DAG': ['DAG-South-01', 'DAG-South-02', 'DAG-South-03', 'DAG-South-04', 'DAG-South-05'],
            'KVÄLL': ['KVALL-South-01', 'KVALL-South-02', 'KVALL-South-03'],
            'NATT': ['NATT-South-01']
        },
        'Central-Huddinge': {
            'DAG': ['DAG-Central-01', 'DAG-Central-02'],
            'KVÄLL': ['KVALL-Central-01', 'KVALL-Central-02'],
            'NATT': ['NATT-Central-01']
        },
        'East-Huddinge': {
            'DAG': ['DAG-East-01', 'DAG-East-02', 'DAG-East-03'],
            'KVÄLL': ['KVALL-East-01', 'KVALL-East-02'],
            'NATT': ['NATT-East-01']
        }
    }
    
    # Limit each slinga to the preferred number of vehicles
    limited_structure = {}
    for polygon, slingas in base_structure.items():
        limited_structure[polygon] = {}
        for slinga, vehicles in slingas.items():
            # Take only the first N vehicles where N = preferred_vehicles_per_slinga
            limited_vehicles = vehicles[:preferred_vehicles_per_slinga]
            if limited_vehicles:  # Only include if we have vehicles for this slinga
                limited_structure[polygon][slinga] = limited_vehicles
    
    return limited_structure

def assign_client_to_polygon(lat, lon):
    """Assign client to geographic polygon based on coordinates"""
    if lat > 59.245:
        return 'North-Huddinge'
    elif lat < 59.235:
        return 'South-Huddinge'  
    elif lon > 17.985:
        return 'East-Huddinge'
    else:
        return 'Central-Huddinge'

def extract_slinga_from_time(time_str):
    """Extract slinga from visit time"""
    if not time_str or 'T' not in time_str:
        return 'UNKNOWN'
    
    hour = int(time_str.split('T')[1].split(':')[0])
    if 6 <= hour < 14:
        return 'DAG'
    elif 14 <= hour < 22:
        return 'KVÄLL'
    else:
        return 'NATT'

def calculate_client_continuity(client_slingas, preferred_vehicles_per_slinga):
    """Calculate total continuity for a client using Björn's formula"""
    return len(client_slingas) * preferred_vehicles_per_slinga

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 build_tunable_continuity_dataset.py <preferred_vehicles_per_slinga>")
        print("Example: python3 build_tunable_continuity_dataset.py 2")
        sys.exit(1)
    
    preferred_vehicles_per_slinga = int(sys.argv[1])
    
    print(f"🎛️ Building Dataset with preferred_vehicles_per_slinga = {preferred_vehicles_per_slinga}")
    print("=" * 70)
    
    # Load current dataset
    with open('strategic_capacity_input.json', 'r') as f:
        current_data = json.load(f)
    
    # Get employee structure with tunable parameter
    geo_slinga_employees = build_geo_slinga_structure(preferred_vehicles_per_slinga)
    
    # Step 1: Analyze current clients and assign to polygons
    client_info = {}
    client_visits = defaultdict(lambda: defaultdict(list))
    
    for visit in current_data['visits']:
        # Extract client name
        client_match = re.search(r'Client-(\d+)', visit['name'])
        if not client_match:
            continue
            
        client_id = f"Client-{client_match.group(1)}"
        
        # Get location and assign polygon
        if 'location' in visit and len(visit['location']) == 2:
            lat, lon = visit['location']
            polygon = assign_client_to_polygon(lat, lon)
            
            # Get slinga from visit time
            time_str = visit['timeWindows'][0]['minStartTime'] if visit.get('timeWindows') else ''
            slinga = extract_slinga_from_time(time_str)
            
            # Store client info
            if client_id not in client_info:
                client_info[client_id] = {
                    'polygon': polygon,
                    'location': [lat, lon],
                    'slingas': set()
                }
            
            client_info[client_id]['slingas'].add(slinga)
            
            # Group visits by client and slinga
            client_visits[client_id][slinga].append(visit)
    
    # Step 2: Calculate continuity statistics
    continuity_stats = defaultdict(list)
    
    for client_id, info in client_info.items():
        slingas = info['slingas']
        total_continuity = calculate_client_continuity(slingas, preferred_vehicles_per_slinga)
        continuity_stats[total_continuity].append(client_id)
    
    print(f"📊 CONTINUITY ANALYSIS:")
    print(f"Björn's Formula: Total Continuity = Σ(slingas) × {preferred_vehicles_per_slinga}")
    print()
    
    total_clients = len(client_info)
    for continuity_level in sorted(continuity_stats.keys()):
        client_count = len(continuity_stats[continuity_level])
        percentage = (client_count / total_clients) * 100
        print(f"- {continuity_level} max caregivers: {client_count} clients ({percentage:.1f}%)")
    
    # Check target compliance
    print(f"\\n🎯 TARGET COMPLIANCE:")
    clients_over_15 = sum(len(clients) for level, clients in continuity_stats.items() if level > 15)
    clients_over_5 = sum(len(clients) for level, clients in continuity_stats.items() if level > 5)
    clients_over_3 = sum(len(clients) for level, clients in continuity_stats.items() if level > 3)
    
    print(f"- Clients with >15 caregivers: {clients_over_15} ({(clients_over_15/total_clients)*100:.1f}%)")
    print(f"- Clients with >5 caregivers: {clients_over_5} ({(clients_over_5/total_clients)*100:.1f}%)")
    print(f"- Clients with >3 caregivers: {clients_over_3} ({(clients_over_3/total_clients)*100:.1f}%)")
    
    # Step 3: Build structured dataset (same logic as before, but with tuned parameters)
    structured_dataset = {
        'metadata': {
            'approach': 'tunable_continuity_by_design',
            'preferred_vehicles_per_slinga': preferred_vehicles_per_slinga,
            'continuity_formula': 'Σ(slingas) × preferred_vehicles_per_slinga',
            'created': datetime.now().isoformat()
        },
        'vehicles': [],
        'visitGroups': [],
        'visits': []
    }
    
    # Step 4: Create vehicles
    for polygon, slingas in geo_slinga_employees.items():
        for slinga, employee_ids in slingas.items():
            for employee_id in employee_ids:
                # Define shift times based on slinga
                if slinga == 'DAG':
                    start_time = '07:00:00'
                    end_time = '15:00:00'
                elif slinga == 'KVÄLL':
                    start_time = '14:00:00' 
                    end_time = '22:00:00'
                else:  # NATT
                    start_time = '22:00:00'
                    end_time = '06:00:00'
                
                # Create vehicle with 2-week shifts
                shifts = []
                for day in range(14):  # 2 weeks
                    date = f"2026-02-{17 + day:02d}"
                    shifts.append({
                        'id': f"{employee_id.lower()}-{date}",
                        'startTime': f"{date}T{start_time}+01:00",
                        'endTime': f"{date}T{end_time}+01:00",
                        'serviceArea': polygon
                    })
                
                vehicle = {
                    'id': employee_id,
                    'name': f"{employee_id.replace('-', ' ')} - {polygon}",
                    'serviceArea': polygon,
                    'slinga': slinga,
                    'shifts': shifts,
                    'maxClients': 8  # Slightly higher capacity for flexibility
                }
                structured_dataset['vehicles'].append(vehicle)
    
    # Step 5: Create visit groups with tuned continuity constraints
    visit_id_counter = 1
    
    for client_id, slingas in client_visits.items():
        client_polygon = client_info[client_id]['polygon']
        
        for slinga, visits in slingas.items():
            if not visits:
                continue
                
            # Get allowed employees for this client's polygon+slinga (using tuned parameter)
            allowed_employees = geo_slinga_employees.get(client_polygon, {}).get(slinga, [])
            if not allowed_employees:
                print(f"⚠️ Warning: No employees defined for {client_polygon} {slinga}")
                continue
            
            # Use all available employees (up to preferred_vehicles_per_slinga)
            # This gives the solver maximum flexibility within the continuity constraint
            
            # Create visit group
            visit_group_id = f"{client_id}-{slinga}-{client_polygon.replace('-', '')}"
            visit_ids_in_group = []
            
            # Process visits in this group
            for visit in visits:
                new_visit = visit.copy()
                new_visit['id'] = str(visit_id_counter)
                new_visit['clientId'] = client_id
                new_visit['polygon'] = client_polygon
                new_visit['slinga'] = slinga
                new_visit['groupId'] = visit_group_id
                new_visit['allowedVehicles'] = allowed_employees
                
                structured_dataset['visits'].append(new_visit)
                visit_ids_in_group.append(str(visit_id_counter))
                visit_id_counter += 1
            
            # Create visit group with tuned continuity constraints
            visit_group = {
                'id': visit_group_id,
                'name': f"{client_id} {slinga} visits in {client_polygon}",
                'clientId': client_id,
                'polygon': client_polygon,
                'slinga': slinga,
                'visits': visit_ids_in_group,
                'mustUseSameVehicle': True,  # HARD CONTINUITY CONSTRAINT
                'maxCaregivers': preferred_vehicles_per_slinga,
                'allowedVehicles': allowed_employees
            }
            structured_dataset['visitGroups'].append(visit_group)
    
    # Step 6: Save structured dataset
    output_file = f'tunable_continuity_input_p{preferred_vehicles_per_slinga}.json'
    with open(output_file, 'w') as f:
        json.dump(structured_dataset, f, indent=2)
    
    print(f"\\n✅ Tunable dataset saved to {output_file}")
    print(f"📊 Summary:")
    print(f"   - Vehicles: {len(structured_dataset['vehicles'])}")
    print(f"   - Visit Groups: {len(structured_dataset['visitGroups'])}")
    print(f"   - Visits: {len(structured_dataset['visits'])}")
    print(f"   - Continuity guaranteed by formula: Σ(slingas) × {preferred_vehicles_per_slinga}")
    
    print(f"\\n🎯 READY FOR ITERATIVE TESTING:")
    print(f"   - Test preferred_vehicles_per_slinga = [1, 2, 3, 4]")
    print(f"   - Measure efficiency vs continuity trade-offs")
    print(f"   - Find optimal balance for business objectives")

if __name__ == '__main__':
    main()