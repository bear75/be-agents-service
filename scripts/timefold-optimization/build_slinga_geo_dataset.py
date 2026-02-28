#!/usr/bin/env python3
"""
Build Slinga-Geo Structured Dataset for Continuity Optimization

This script implements Björn's breakthrough approach:
1. Define geographic polygons
2. Assign clients to polygons based on location
3. Create visit groups with mustUseSameVehicle constraints
4. Build polygon+slinga specific employee shortlists
"""

import json
import re
from collections import defaultdict
from datetime import datetime

def assign_client_to_polygon(lat, lon):
    """Assign client to geographic polygon based on coordinates"""
    # Huddinge geographic boundaries (simplified)
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

def build_geo_slinga_structure():
    """Define employee structure by polygon and slinga"""
    return {
        'North-Huddinge': {
            'DAG': ['DAG-North-01', 'DAG-North-02', 'DAG-North-03'],
            'KVÄLL': ['KVALL-North-01', 'KVALL-North-02'],
            'NATT': ['NATT-North-01']
        },
        'South-Huddinge': {
            'DAG': ['DAG-South-01', 'DAG-South-02', 'DAG-South-03', 'DAG-South-04'],
            'KVÄLL': ['KVALL-South-01', 'KVALL-South-02'],
            'NATT': ['NATT-South-01']
        },
        'Central-Huddinge': {
            'DAG': ['DAG-Central-01'],
            'KVÄLL': ['KVALL-Central-01'],
            'NATT': ['NATT-Central-01']
        },
        'East-Huddinge': {
            'DAG': ['DAG-East-01', 'DAG-East-02'],
            'KVÄLL': ['KVALL-East-01'],
            'NATT': ['NATT-East-01']
        }
    }

def main():
    # Load current dataset
    with open('strategic_capacity_input.json', 'r') as f:
        current_data = json.load(f)
    
    print("🏗️ Building Slinga-Geo Structured Dataset")
    print("==========================================")
    
    # Get employee structure
    geo_slinga_employees = build_geo_slinga_structure()
    
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
                    'location': [lat, lon]
                }
            
            # Group visits by client and slinga
            client_visits[client_id][slinga].append(visit)
    
    print(f"📊 Processed {len(client_info)} clients across {len(set(c['polygon'] for c in client_info.values()))} polygons")
    
    # Step 2: Build structured dataset
    structured_dataset = {
        'metadata': {
            'approach': 'continuity_by_design',
            'strategy': 'geo_slinga_clustering',
            'created': datetime.now().isoformat()
        },
        'vehicles': [],
        'visitGroups': [],
        'visits': []
    }
    
    # Step 3: Create vehicles for each polygon+slinga combination
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
                    'maxClients': 6
                }
                structured_dataset['vehicles'].append(vehicle)
    
    # Step 4: Create visit groups with continuity constraints
    visit_id_counter = 1
    
    for client_id, slingas in client_visits.items():
        client_polygon = client_info[client_id]['polygon']
        
        for slinga, visits in slingas.items():
            if not visits:
                continue
                
            # Get allowed employees for this client's polygon+slinga
            allowed_employees = geo_slinga_employees.get(client_polygon, {}).get(slinga, [])
            if not allowed_employees:
                print(f"⚠️ Warning: No employees defined for {client_polygon} {slinga}")
                continue
            
            # Limit to max 2-3 caregivers per client
            max_caregivers = min(3, len(allowed_employees))
            limited_employees = allowed_employees[:max_caregivers]
            
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
                new_visit['allowedVehicles'] = limited_employees
                
                structured_dataset['visits'].append(new_visit)
                visit_ids_in_group.append(str(visit_id_counter))
                visit_id_counter += 1
            
            # Create visit group with continuity constraints
            visit_group = {
                'id': visit_group_id,
                'name': f"{client_id} {slinga} visits in {client_polygon}",
                'clientId': client_id,
                'polygon': client_polygon,
                'slinga': slinga,
                'visits': visit_ids_in_group,
                'mustUseSameVehicle': True,  # HARD CONTINUITY CONSTRAINT
                'maxCaregivers': max_caregivers,
                'allowedVehicles': limited_employees
            }
            structured_dataset['visitGroups'].append(visit_group)
    
    # Step 5: Save structured dataset
    output_file = 'slinga_geo_structured_input.json'
    with open(output_file, 'w') as f:
        json.dump(structured_dataset, f, indent=2)
    
    print(f"✅ Structured dataset saved to {output_file}")
    print(f"📊 Summary:")
    print(f"   - Vehicles: {len(structured_dataset['vehicles'])}")
    print(f"   - Visit Groups: {len(structured_dataset['visitGroups'])}")
    print(f"   - Visits: {len(structured_dataset['visits'])}")
    
    # Show continuity guarantees
    print(f"\n🤝 CONTINUITY GUARANTEES:")
    polygon_stats = defaultdict(lambda: defaultdict(int))
    for vg in structured_dataset['visitGroups']:
        polygon = vg['polygon']
        slinga = vg['slinga']
        max_caregivers = vg['maxCaregivers']
        polygon_stats[polygon][slinga] = max(polygon_stats[polygon][slinga], max_caregivers)
    
    for polygon in sorted(polygon_stats.keys()):
        print(f"   {polygon}:")
        for slinga in sorted(polygon_stats[polygon].keys()):
            max_cg = polygon_stats[polygon][slinga]
            print(f"     - {slinga}: max {max_cg} caregivers per client")
    
    print(f"\n🎯 READY FOR OPTIMIZATION:")
    print(f"   - Continuity guaranteed by dataset structure")
    print(f"   - No cross-polygon assignments possible")
    print(f"   - No cross-slinga assignments possible")
    print(f"   - Solver optimizes routes within relationship boundaries")

if __name__ == '__main__':
    main()