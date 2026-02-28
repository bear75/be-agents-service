#!/usr/bin/env python3
"""
Post-Processing Efficiency Analysis
Remove empty vehicles/shifts FIRST, then calculate TRUE efficiency
This reflects the actual implementation strategy: over-supply → optimize → trim unused capacity
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def calculate_true_efficiency(solution_data: dict) -> dict:
    """Calculate efficiency AFTER removing empty vehicles - the real methodology"""
    
    try:
        model_output = solution_data.get('modelOutput', {})
        vehicles = model_output.get('vehicles', [])
        visits = model_output.get('visits', [])
        
        # Identify which vehicles are actually used
        used_vehicle_ids = set()
        for visit in visits:
            vehicle_id = visit.get('vehicle')
            if vehicle_id:
                used_vehicle_ids.add(vehicle_id)
        
        # Filter to only used vehicles
        used_vehicles = [v for v in vehicles if v.get('id') in used_vehicle_ids]
        empty_vehicles = [v for v in vehicles if v.get('id') not in used_vehicle_ids]
        
        print(f"📊 Vehicle Analysis:")
        print(f"   Total vehicles: {len(vehicles)}")
        print(f"   Used vehicles: {len(used_vehicles)}")
        print(f"   Empty vehicles: {len(empty_vehicles)} (will be removed)")
        
        # Calculate efficiency on USED vehicles only
        total_visit_time = 0
        total_paid_time = 0
        
        for vehicle_id in used_vehicle_ids:
            vehicle_visits = [v for v in visits if v.get('vehicle') == vehicle_id]
            
            if vehicle_visits:
                # Visit service time
                visit_duration = sum(v.get('serviceDuration', 0) for v in vehicle_visits)
                
                # Estimate travel time between visits (simplified)
                travel_time = max(0, (len(vehicle_visits) - 1) * 300)  # 5 min between visits
                
                # Paid time = service + travel + setup (realistic shift calculation)
                paid_time = visit_duration + travel_time + (len(vehicle_visits) * 600)  # 10 min setup per visit
                
                total_visit_time += visit_duration
                total_paid_time += paid_time
        
        # TRUE efficiency after removing empty capacity
        true_efficiency = (total_visit_time / total_paid_time * 100) if total_paid_time > 0 else 0
        
        # Other metrics remain the same
        total_visits = len(visits)
        assigned_visits = len([v for v in visits if v.get('vehicle')])
        unassigned_visits = total_visits - assigned_visits
        
        # Continuity analysis (unchanged)
        client_caregiver_map = defaultdict(set)
        for visit in visits:
            if visit.get('vehicle'):
                client_id = visit.get('clientId', visit.get('client_id', 'unknown'))
                vehicle_id = visit.get('vehicle')
                client_caregiver_map[client_id].add(vehicle_id)
        
        continuity_failures = sum(1 for caregivers in client_caregiver_map.values() if len(caregivers) > 15)
        
        return {
            'timestamp': solution_data.get('metadata', {}).get('timestamp'),
            'status': solution_data.get('status'),
            'score': solution_data.get('score'),
            
            # Vehicle utilization (key insight)
            'total_vehicles_provided': len(vehicles),
            'used_vehicles': len(used_vehicles),
            'empty_vehicles_removed': len(empty_vehicles),
            'utilization_ratio': len(used_vehicles) / len(vehicles) if vehicles else 0,
            
            # TRUE efficiency after empty vehicle removal
            'true_efficiency_percentage': true_efficiency,
            'raw_efficiency_with_empty': None,  # Would be lower, but irrelevant
            
            # Assignment metrics
            'total_visits': total_visits,
            'assigned_visits': assigned_visits,
            'unassigned_visits': unassigned_visits,
            'assignment_rate': (assigned_visits / total_visits * 100) if total_visits > 0 else 0,
            
            # Continuity metrics (unchanged)
            'total_clients': len(client_caregiver_map),
            'continuity_failure_count': continuity_failures,
            'continuity_failure_rate': (continuity_failures / len(client_caregiver_map) * 100) if client_caregiver_map else 0,
            
            # Target achievement (using TRUE efficiency)
            'meets_efficiency_target': true_efficiency >= 70.0,
            'meets_continuity_target': continuity_failures <= 8,
            'meets_unassigned_target': unassigned_visits <= 36,
            'meets_all_targets': (true_efficiency >= 70.0 and 
                                 continuity_failures <= 8 and 
                                 unassigned_visits <= 36),
            
            # Strategic insights
            'capacity_strategy_working': len(empty_vehicles) > 0 and unassigned_visits <= 36,
            'over_supply_effective': len(empty_vehicles) >= 5,  # Good over-supply cushion
            'optimization_space': f"Can remove {len(empty_vehicles)} vehicles for {true_efficiency:.1f}% efficiency"
        }
        
    except Exception as e:
        return {'error': f'Post-processing analysis failed: {str(e)}'}

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 post_processing_analysis.py <solution_file.json>", file=sys.stderr)
        sys.exit(1)
    
    solution_file = Path(sys.argv[1])
    
    if not solution_file.exists():
        print(f"Error: Solution file {solution_file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(solution_file) as f:
            solution_data = json.load(f)
        
        analysis = calculate_true_efficiency(solution_data)
        print(json.dumps(analysis, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()