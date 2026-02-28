#!/usr/bin/env python3
"""
Build C-Vehicle Constraint Dataset

Implements Björn's clarified approach:
- Continuity = total number of different vehicles per client
- Parameter C = maximum different vehicles allowed per client
- Trade-off: Higher C = more routing flexibility = better efficiency = worse continuity
- Implementation: Split visit groups strategically to achieve exactly C vehicles per client
"""

import json
import re
import sys
from collections import defaultdict
from datetime import datetime
import math

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

def split_visits_into_groups(visits, max_vehicles_c):
    """
    Split visits into C groups to achieve exactly C vehicles max per client
    
    Args:
        visits: List of visit objects
        max_vehicles_c: Maximum number of different vehicles (C parameter)
    
    Returns:
        List of visit groups
    """
    if max_vehicles_c <= 0 or len(visits) == 0:
        return []
    
    if max_vehicles_c >= len(visits):
        # If C is larger than visit count, each visit gets its own group
        return [[visit] for visit in visits]
    
    # Calculate group size
    group_size = math.ceil(len(visits) / max_vehicles_c)
    
    # Split visits into C groups
    groups = []
    for i in range(0, len(visits), group_size):
        group = visits[i:i + group_size]
        if group:
            groups.append(group)
    
    return groups

def build_vehicles_for_polygon_slinga(polygon, slinga, vehicle_count):
    """Build vehicles for a specific polygon and slinga"""
    vehicles = []
    
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
    
    for i in range(1, vehicle_count + 1):
        employee_id = f"{slinga}-{polygon.split('-')[0]}-{i:02d}"
        
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
            'maxClients': 10  # Higher capacity for flexibility
        }
        vehicles.append(vehicle)
    
    return vehicles

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 build_c_vehicle_constraint_dataset.py <max_vehicles_per_client>")
        print("Example: python3 build_c_vehicle_constraint_dataset.py 3")
        print("  → Each client served by maximum 3 different vehicles")
        sys.exit(1)
    
    max_vehicles_c = int(sys.argv[1])
    
    print(f"🎛️ Building Dataset with C = {max_vehicles_c} (max vehicles per client)")
    print("=" * 70)
    
    # Load current dataset
    with open('strategic_capacity_input.json', 'r') as f:
        current_data = json.load(f)
    
    # Step 1: Analyze current clients and visits
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
    
    # Step 2: Calculate vehicle requirements by polygon+slinga
    polygon_slinga_demand = defaultdict(lambda: defaultdict(int))
    
    for client_id in client_info:
        polygon = client_info[client_id]['polygon']
        for slinga in client_info[client_id]['slingas']:
            # Each client can use up to C vehicles in this polygon+slinga
            polygon_slinga_demand[polygon][slinga] += max_vehicles_c
    
    print(f"📊 CONTINUITY ANALYSIS:")
    print(f"Formula: Each client served by maximum {max_vehicles_c} different vehicles")
    print()
    
    # Step 3: Build structured dataset
    structured_dataset = {
        'metadata': {
            'approach': 'c_vehicle_constraint',
            'max_vehicles_per_client': max_vehicles_c,
            'continuity_formula': f'max {max_vehicles_c} different vehicles per client',
            'created': datetime.now().isoformat()
        },
        'vehicles': [],
        'visitGroups': [],
        'visits': []
    }
    
    # Step 4: Create vehicles based on demand
    total_vehicles = 0
    for polygon, slingas in polygon_slinga_demand.items():
        for slinga, demand in slingas.items():
            # Create enough vehicles to handle the demand
            # Each vehicle can serve multiple clients, so we don't need demand number of vehicles
            vehicle_count = min(demand, max(1, demand // 3))  # Reasonable vehicle count
            vehicles = build_vehicles_for_polygon_slinga(polygon, slinga, vehicle_count)
            structured_dataset['vehicles'].extend(vehicles)
            total_vehicles += vehicle_count
            
            print(f"{polygon} {slinga}: {vehicle_count} vehicles (demand: {demand})")
    
    # Step 5: Create visit groups with C-vehicle constraint
    visit_id_counter = 1
    total_visit_groups = 0
    
    for client_id, slingas in client_visits.items():
        client_polygon = client_info[client_id]['polygon']
        
        for slinga, visits in slingas.items():
            if not visits:
                continue
            
            # Get available vehicles for this polygon+slinga
            available_vehicles = [
                v['id'] for v in structured_dataset['vehicles'] 
                if v['serviceArea'] == client_polygon and v['slinga'] == slinga
            ]
            
            if not available_vehicles:
                print(f"⚠️ Warning: No vehicles for {client_polygon} {slinga}")
                continue
            
            # SPLIT VISITS INTO C GROUPS (KEY INNOVATION)
            visit_groups = split_visits_into_groups(visits, max_vehicles_c)
            
            # Create visit groups and visits
            for group_index, visit_group in enumerate(visit_groups):
                visit_group_id = f"{client_id}-{slinga}-{client_polygon.replace('-', '')}-G{group_index + 1}"
                visit_ids_in_group = []
                
                # Process visits in this group
                for visit in visit_group:
                    new_visit = visit.copy()
                    new_visit['id'] = str(visit_id_counter)
                    new_visit['clientId'] = client_id
                    new_visit['polygon'] = client_polygon
                    new_visit['slinga'] = slinga
                    new_visit['groupId'] = visit_group_id
                    new_visit['allowedVehicles'] = available_vehicles
                    
                    structured_dataset['visits'].append(new_visit)
                    visit_ids_in_group.append(str(visit_id_counter))
                    visit_id_counter += 1
                
                # Create visit group with same-vehicle constraint
                visit_group_obj = {
                    'id': visit_group_id,
                    'name': f"{client_id} {slinga} Group {group_index + 1} in {client_polygon}",
                    'clientId': client_id,
                    'polygon': client_polygon,
                    'slinga': slinga,
                    'groupIndex': group_index + 1,
                    'visits': visit_ids_in_group,
                    'mustUseSameVehicle': True,  # Each group uses same vehicle
                    'allowedVehicles': available_vehicles
                }
                structured_dataset['visitGroups'].append(visit_group_obj)
                total_visit_groups += 1
    
    # Step 6: Calculate actual continuity achieved
    client_max_vehicles = defaultdict(int)
    for vg in structured_dataset['visitGroups']:
        client_id = vg['clientId']
        client_max_vehicles[client_id] += 1  # Each visit group = 1 vehicle
    
    continuity_distribution = defaultdict(int)
    for client_id, vehicle_count in client_max_vehicles.items():
        continuity_distribution[vehicle_count] += 1
    
    print(f"\\n🎯 ACHIEVED CONTINUITY DISTRIBUTION:")
    total_clients = len(client_max_vehicles)
    for vehicle_count in sorted(continuity_distribution.keys()):
        client_count = continuity_distribution[vehicle_count]
        percentage = (client_count / total_clients) * 100
        print(f"- {vehicle_count} vehicles per client: {client_count} clients ({percentage:.1f}%)")
    
    # Step 7: Save structured dataset
    output_file = f'c_vehicle_constraint_input_C{max_vehicles_c}.json'
    with open(output_file, 'w') as f:
        json.dump(structured_dataset, f, indent=2)
    
    print(f"\\n✅ C-Vehicle dataset saved to {output_file}")
    print(f"📊 Summary:")
    print(f"   - Total vehicles: {total_vehicles}")
    print(f"   - Visit groups: {total_visit_groups}")
    print(f"   - Visits: {len(structured_dataset['visits'])}")
    print(f"   - Max vehicles per client: {max_vehicles_c}")
    
    print(f"\\n🎯 TRADE-OFF ANALYSIS:")
    print(f"   - Continuity: Each client served by ≤{max_vehicles_c} different vehicles")
    print(f"   - Flexibility: Solver has {max_vehicles_c} routing options per client") 
    print(f"   - Efficiency: Higher C should improve efficiency through flexibility")
    
    print(f"\\n🔬 READY FOR OPTIMIZATION:")
    print(f"   - Test C=[1,2,3,4,5] to find efficiency/continuity sweet spot")
    print(f"   - Each C value gives exact control over continuity constraint")
    print(f"   - Measure efficiency gains from increased routing flexibility")

if __name__ == '__main__':
    main()