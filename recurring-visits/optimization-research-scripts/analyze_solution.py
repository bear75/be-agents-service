#!/usr/bin/env python3
"""
Detailed Timefold Solution Analysis
Extracts efficiency, continuity, and assignment metrics from solution JSON
"""

import json
import sys
from pathlib import Path
from collections import defaultdict

def analyze_timefold_solution(solution_data: dict) -> dict:
    """Extract comprehensive metrics from Timefold solution"""
    
    try:
        model_output = solution_data.get('modelOutput', {})
        vehicles = model_output.get('vehicles', [])
        visits = model_output.get('visits', [])
        
        if not vehicles or not visits:
            return {'error': 'Missing vehicles or visits in solution'}
        
        # Basic counts
        total_visits = len(visits)
        assigned_visits = len([v for v in visits if v.get('vehicle')])
        unassigned_visits = total_visits - assigned_visits
        
        # Vehicle utilization analysis
        active_vehicles = 0
        total_visit_time = 0
        total_paid_time = 0
        idle_time = 0
        
        vehicle_stats = []
        
        for vehicle in vehicles:
            vehicle_visits = [v for v in visits if v.get('vehicle') == vehicle.get('id')]
            
            if vehicle_visits:
                active_vehicles += 1
                
                # Calculate times
                visit_duration = sum(v.get('serviceDuration', 0) for v in vehicle_visits)
                
                # Estimate travel time (simplified - in real implementation use actual travel times)
                travel_time = len(vehicle_visits) * 300 if len(vehicle_visits) > 1 else 0  # 5 min avg between visits
                
                # Paid time = total shift duration (simplified as work span + buffer)
                paid_time_seconds = visit_duration + travel_time + (len(vehicle_visits) * 600)  # 10 min buffer per visit
                
                total_visit_time += visit_duration
                total_paid_time += paid_time_seconds
                
                vehicle_stats.append({
                    'vehicle_id': vehicle.get('id'),
                    'visit_count': len(vehicle_visits),
                    'visit_duration': visit_duration,
                    'paid_time': paid_time_seconds,
                    'efficiency': visit_duration / paid_time_seconds * 100 if paid_time_seconds > 0 else 0
                })
            else:
                # Empty vehicle
                idle_time += 8 * 3600  # 8 hour shift
        
        # Overall efficiency calculation
        efficiency_percentage = (total_visit_time / total_paid_time * 100) if total_paid_time > 0 else 0
        
        # Continuity analysis
        client_caregiver_map = defaultdict(set)
        
        for visit in visits:
            if visit.get('vehicle'):
                client_id = visit.get('clientId', visit.get('client_id', 'unknown'))
                vehicle_id = visit.get('vehicle')
                client_caregiver_map[client_id].add(vehicle_id)
        
        # Count continuity failures (>15 caregivers per client)
        continuity_failures = 0
        continuity_details = []
        
        for client_id, caregivers in client_caregiver_map.items():
            caregiver_count = len(caregivers)
            if caregiver_count > 15:
                continuity_failures += 1
                continuity_details.append({
                    'client_id': client_id,
                    'caregiver_count': caregiver_count
                })
        
        # Visit distribution analysis
        visit_counts_per_client = defaultdict(int)
        for visit in visits:
            client_id = visit.get('clientId', visit.get('client_id', 'unknown'))
            visit_counts_per_client[client_id] += 1
        
        high_volume_clients = [(k, v) for k, v in visit_counts_per_client.items() if v >= 50]
        
        # Prepare comprehensive results
        results = {
            'timestamp': solution_data.get('metadata', {}).get('timestamp'),
            'status': solution_data.get('status'),
            'score': solution_data.get('score'),
            
            # Basic metrics
            'total_visits': total_visits,
            'assigned_visits': assigned_visits,
            'unassigned_visits': unassigned_visits,
            'assignment_rate': (assigned_visits / total_visits * 100) if total_visits > 0 else 0,
            
            # Efficiency metrics
            'efficiency_percentage': efficiency_percentage,
            'total_visit_time_hours': total_visit_time / 3600,
            'total_paid_time_hours': total_paid_time / 3600,
            'idle_time_hours': idle_time / 3600,
            
            # Vehicle metrics
            'total_vehicles': len(vehicles),
            'active_vehicles': active_vehicles,
            'empty_vehicles': len(vehicles) - active_vehicles,
            'empty_vehicle_ratio': (len(vehicles) - active_vehicles) / len(vehicles) if vehicles else 0,
            
            # Continuity metrics
            'total_clients': len(client_caregiver_map),
            'continuity_failure_count': continuity_failures,
            'continuity_failure_rate': (continuity_failures / len(client_caregiver_map) * 100) if client_caregiver_map else 0,
            'average_caregivers_per_client': sum(len(cg) for cg in client_caregiver_map.values()) / len(client_caregiver_map) if client_caregiver_map else 0,
            
            # Detailed breakdowns
            'continuity_failures_detail': continuity_details[:10],  # Top 10 worst cases
            'high_volume_clients': high_volume_clients[:10],
            'vehicle_efficiency_stats': {
                'min': min(vs['efficiency'] for vs in vehicle_stats) if vehicle_stats else 0,
                'max': max(vs['efficiency'] for vs in vehicle_stats) if vehicle_stats else 0,
                'avg': sum(vs['efficiency'] for vs in vehicle_stats) / len(vehicle_stats) if vehicle_stats else 0
            },
            
            # Target achievement
            'meets_efficiency_target': efficiency_percentage >= 70.0,
            'meets_continuity_target': continuity_failures <= 8,  # 10% of 81 clients
            'meets_unassigned_target': unassigned_visits <= 36,
            'meets_all_targets': efficiency_percentage >= 70.0 and continuity_failures <= 8 and unassigned_visits <= 36
        }
        
        return results
        
    except Exception as e:
        return {'error': f'Analysis failed: {str(e)}'}

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 analyze_solution.py <solution_file.json>", file=sys.stderr)
        sys.exit(1)
    
    solution_file = Path(sys.argv[1])
    
    if not solution_file.exists():
        print(f"Error: Solution file {solution_file} not found", file=sys.stderr)
        sys.exit(1)
    
    try:
        with open(solution_file) as f:
            solution_data = json.load(f)
        
        analysis = analyze_timefold_solution(solution_data)
        print(json.dumps(analysis, indent=2))
        
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()