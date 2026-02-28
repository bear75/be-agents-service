#!/usr/bin/env python3
"""
Analyze Continuity Patterns in Dataset 41ce610c
Identify characteristics of clients with poor continuity (>15 caregivers)
"""

import json
import re
from collections import defaultdict
from datetime import datetime

def load_timefold_solution(filename):
    """Load the Timefold solution data"""
    with open(filename, 'r') as f:
        return json.load(f)

def extract_client_id(visit_name):
    """Extract client ID from visit name"""
    # Assuming visit names contain client identifiers
    # Pattern might be like "Client-001_visit_1" or similar
    match = re.search(r'Client-(\d+)', visit_name)
    if match:
        return f"Client-{match.group(1)}"
    
    # Try other patterns
    match = re.search(r'(\d+)', visit_name)
    if match:
        return f"Client-{match.group(1)}"
    
    return visit_name.split('_')[0] if '_' in visit_name else visit_name

def analyze_continuity_by_client(data):
    """Analyze continuity patterns by client"""
    
    model_output = data.get('modelOutput', {})
    vehicles = model_output.get('vehicles', [])
    
    # Track which vehicles serve which clients
    client_to_vehicles = defaultdict(set)
    client_visit_count = defaultdict(int)
    client_time_windows = defaultdict(list)
    client_locations = defaultdict(list)
    
    for vehicle in vehicles:
        vehicle_id = vehicle.get('id', 'unknown')
        visits = vehicle.get('visits', [])
        
        for visit in visits:
            visit_id = visit.get('id', '')
            visit_name = visit.get('name', '')
            client_id = extract_client_id(visit_name)
            
            # Track vehicle assignment
            client_to_vehicles[client_id].add(vehicle_id)
            client_visit_count[client_id] += 1
            
            # Extract time windows if available
            if 'arrivalTime' in visit:
                client_time_windows[client_id].append(visit['arrivalTime'])
            
            # Extract location if available
            if 'location' in visit:
                location = visit['location']
                if 'latitude' in location and 'longitude' in location:
                    client_locations[client_id].append((location['latitude'], location['longitude']))
    
    # Calculate continuity scores
    client_continuity = {}
    for client_id, vehicles_set in client_to_vehicles.items():
        continuity_score = len(vehicles_set)
        client_continuity[client_id] = {
            'continuity': continuity_score,
            'visit_count': client_visit_count[client_id],
            'vehicles': list(vehicles_set),
            'time_windows': client_time_windows.get(client_id, []),
            'locations': client_locations.get(client_id, [])
        }
    
    return client_continuity

def analyze_poor_continuity_patterns(client_continuity):
    """Analyze patterns in clients with poor continuity (>15)"""
    
    poor_continuity_clients = {
        client_id: data 
        for client_id, data in client_continuity.items() 
        if data['continuity'] > 15
    }
    
    good_continuity_clients = {
        client_id: data 
        for client_id, data in client_continuity.items() 
        if data['continuity'] <= 15
    }
    
    print(f"🔬 **CONTINUITY PATTERN ANALYSIS**\n")
    print(f"Total clients: {len(client_continuity)}")
    print(f"Poor continuity (>15): {len(poor_continuity_clients)} clients")
    print(f"Good continuity (≤15): {len(good_continuity_clients)} clients")
    print(f"Failure rate: {len(poor_continuity_clients)/len(client_continuity)*100:.1f}%")
    
    # Analyze visit count patterns
    print(f"\n**VISIT COUNT ANALYSIS:**")
    
    poor_visit_counts = [data['visit_count'] for data in poor_continuity_clients.values()]
    good_visit_counts = [data['visit_count'] for data in good_continuity_clients.values()]
    
    if poor_visit_counts:
        print(f"Poor continuity clients:")
        print(f"  - Visit count range: {min(poor_visit_counts)}-{max(poor_visit_counts)}")
        print(f"  - Average visits: {sum(poor_visit_counts)/len(poor_visit_counts):.1f}")
        
        # High visit count correlation
        high_visit_poor = sum(1 for count in poor_visit_counts if count >= 50)
        print(f"  - High visit clients (≥50): {high_visit_poor}/{len(poor_continuity_clients)} ({high_visit_poor/len(poor_continuity_clients)*100:.1f}%)")
    
    if good_visit_counts:
        print(f"Good continuity clients:")
        print(f"  - Visit count range: {min(good_visit_counts)}-{max(good_visit_counts)}")
        print(f"  - Average visits: {sum(good_visit_counts)/len(good_visit_counts):.1f}")
        
    # Analyze continuity vs visit count correlation
    print(f"\n**VISIT COUNT vs CONTINUITY CORRELATION:**")
    
    # Group by visit count ranges
    visit_ranges = [
        (1, 20, "Low (1-20)"),
        (21, 50, "Medium (21-50)"), 
        (51, 100, "High (51-100)"),
        (101, 200, "Very High (101+)")
    ]
    
    for min_visits, max_visits, label in visit_ranges:
        range_clients = [
            (client_id, data) 
            for client_id, data in client_continuity.items() 
            if min_visits <= data['visit_count'] <= max_visits
        ]
        
        if range_clients:
            range_poor = sum(1 for _, data in range_clients if data['continuity'] > 15)
            range_total = len(range_clients)
            
            print(f"{label}: {range_poor}/{range_total} poor continuity ({range_poor/range_total*100:.1f}%)")
    
    return poor_continuity_clients, good_continuity_clients

def analyze_geographical_patterns(poor_continuity_clients, good_continuity_clients):
    """Analyze geographical patterns in continuity"""
    
    print(f"\n**GEOGRAPHICAL ANALYSIS:**")
    
    # Calculate location spread for each client
    def calculate_location_spread(locations):
        if len(locations) < 2:
            return 0
        
        lats = [loc[0] for loc in locations]
        lons = [loc[1] for loc in locations]
        
        lat_range = max(lats) - min(lats)
        lon_range = max(lons) - min(lons)
        
        return (lat_range**2 + lon_range**2)**0.5  # Simple distance metric
    
    poor_spreads = []
    good_spreads = []
    
    for data in poor_continuity_clients.values():
        if data['locations']:
            spread = calculate_location_spread(data['locations'])
            poor_spreads.append(spread)
    
    for data in good_continuity_clients.values():
        if data['locations']:
            spread = calculate_location_spread(data['locations'])
            good_spreads.append(spread)
    
    if poor_spreads:
        print(f"Poor continuity clients:")
        print(f"  - Average location spread: {sum(poor_spreads)/len(poor_spreads):.4f}")
        print(f"  - Max spread: {max(poor_spreads):.4f}")
    
    if good_spreads:
        print(f"Good continuity clients:")
        print(f"  - Average location spread: {sum(good_spreads)/len(good_spreads):.4f}")
        print(f"  - Max spread: {max(good_spreads):.4f}")

def analyze_time_patterns(poor_continuity_clients, good_continuity_clients):
    """Analyze time window patterns"""
    
    print(f"\n**TIME PATTERN ANALYSIS:**")
    
    def extract_hour(time_str):
        try:
            # Parse various time formats
            if 'T' in time_str:
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.hour
        except:
            pass
        return None
    
    def analyze_time_distribution(clients, label):
        all_hours = []
        for data in clients.values():
            for time_str in data['time_windows']:
                hour = extract_hour(time_str)
                if hour is not None:
                    all_hours.append(hour)
        
        if all_hours:
            print(f"{label}:")
            print(f"  - Time range: {min(all_hours):02d}:00 - {max(all_hours):02d}:00")
            print(f"  - Average hour: {sum(all_hours)/len(all_hours):.1f}")
            
            # Distribution
            hour_counts = defaultdict(int)
            for hour in all_hours:
                hour_counts[hour] += 1
            
            peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
            print(f"  - Peak hours: {', '.join([f'{h:02d}:00({c})' for h, c in peak_hours])}")
    
    analyze_time_distribution(poor_continuity_clients, "Poor continuity clients")
    analyze_time_distribution(good_continuity_clients, "Good continuity clients")

def identify_worst_cases(poor_continuity_clients):
    """Identify the worst continuity cases for detailed analysis"""
    
    print(f"\n**WORST CONTINUITY CASES:**")
    
    # Sort by continuity score (worst first)
    worst_cases = sorted(
        poor_continuity_clients.items(),
        key=lambda x: x[1]['continuity'],
        reverse=True
    )
    
    print(f"Top 10 worst cases:")
    for i, (client_id, data) in enumerate(worst_cases[:10], 1):
        print(f"{i:2d}. {client_id}: {data['continuity']} caregivers, {data['visit_count']} visits")
        
        # Show some vehicle IDs
        vehicles_sample = data['vehicles'][:5]
        if len(data['vehicles']) > 5:
            vehicles_sample.append(f"...+{len(data['vehicles'])-5} more")
        print(f"    Vehicles: {', '.join(vehicles_sample)}")

def generate_targeted_solutions(poor_continuity_clients, good_continuity_clients):
    """Generate targeted solutions based on analysis"""
    
    print(f"\n🎯 **TARGETED SOLUTIONS:**")
    
    # Analyze visit count correlation
    high_visit_poor = sum(1 for data in poor_continuity_clients.values() if data['visit_count'] >= 50)
    total_poor = len(poor_continuity_clients)
    
    if high_visit_poor / total_poor > 0.6:
        print(f"\n**Strategy 1: High-Visit Client Protection**")
        print(f"- {high_visit_poor}/{total_poor} poor continuity clients have ≥50 visits")
        print(f"- Solution: Add dedicated vehicles for high-volume clients")
        print(f"- Approach: Create client-specific vehicle pools")
        print(f"- Expected impact: Major continuity improvement for worst cases")
    
    print(f"\n**Strategy 2: Additional Capacity Analysis**")
    
    # Calculate current capacity vs demand
    total_visits = sum(data['visit_count'] for data in poor_continuity_clients.values())
    avg_visits_per_vehicle = total_visits / len(set().union(*[set(data['vehicles']) for data in poor_continuity_clients.values()]))
    
    print(f"- Poor continuity clients: {total_poor} clients, {total_visits} total visits")
    print(f"- Current vehicles serving them: ~{len(set().union(*[set(data['vehicles']) for data in poor_continuity_clients.values()]))} vehicles")
    print(f"- Average visits per vehicle: {avg_visits_per_vehicle:.1f}")
    
    # Estimate additional vehicles needed
    target_continuity = 12  # Target average
    estimated_additional_vehicles = max(0, int(total_visits / target_continuity) - len(set().union(*[set(data['vehicles']) for data in poor_continuity_clients.values()])))
    
    print(f"- Estimated additional vehicles needed: {estimated_additional_vehicles}")
    print(f"- This should reduce continuity by distributing workload")
    
    print(f"\n**Strategy 3: Time Window Optimization**")
    print(f"- Analyze if poor continuity correlates with specific time slots")
    print(f"- Consider dedicated vehicles for peak time periods")
    print(f"- May improve both continuity and unassigned visit issues")

def main():
    print("🧬 **DEEP CONTINUITY PATTERN ANALYSIS**")
    print("Dataset: 41ce610c-bd67-47b8-9e62-7820f87ffcdd")
    print("="*60)
    
    # Load and analyze data
    data = load_timefold_solution('dataset_41ce610c_full.json')
    client_continuity = analyze_continuity_by_client(data)
    
    # Analyze patterns
    poor_continuity_clients, good_continuity_clients = analyze_poor_continuity_patterns(client_continuity)
    
    # Detailed analysis
    analyze_geographical_patterns(poor_continuity_clients, good_continuity_clients)
    analyze_time_patterns(poor_continuity_clients, good_continuity_clients)
    identify_worst_cases(poor_continuity_clients)
    
    # Generate solutions
    generate_targeted_solutions(poor_continuity_clients, good_continuity_clients)
    
    print(f"\n" + "="*60)
    print(f"🎯 **SUMMARY:**")
    print(f"Analysis complete. Key patterns identified for targeted optimization.")

if __name__ == '__main__':
    main()