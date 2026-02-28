#!/usr/bin/env python3
"""Quick analysis of Strategic test results from Timefold solution structure"""

import json

# Load solution
with open('solution_strategic_complete.json') as f:
    solution = json.load(f)

# Extract key metrics from solution structure
model_output = solution.get('modelOutput', {})
kpis = solution.get('kpis', {})
total_unassigned = kpis.get('totalUnassignedVisits', 0)
total_assigned = kpis.get('totalAssignedVisits', 0)
total_vehicles = len(model_output.get('vehicles', []))
activated_vehicles = kpis.get('totalActivatedVehicles', 0)

print("🎯 STRATEGIC TEST RESULTS - QUICK ANALYSIS")
print("=" * 60)
print(f"📊 Assignment Metrics:")
print(f"   Total visits: {total_assigned + total_unassigned}")
print(f"   Assigned visits: {total_assigned}")
print(f"   Unassigned visits: {total_unassigned}")
print(f"   Assignment rate: {total_assigned / (total_assigned + total_unassigned) * 100:.1f}%")
print()
print(f"🚗 Vehicle Metrics:")
print(f"   Total vehicles provided: {total_vehicles}")
print(f"   Activated vehicles: {activated_vehicles}")
print(f"   Empty vehicles: {total_vehicles - activated_vehicles}")
print(f"   Vehicle utilization: {activated_vehicles / total_vehicles * 100:.1f}%")
print()

# Target assessment
meets_unassigned = total_unassigned <= 36
print(f"🎯 TARGET ASSESSMENT:")
print(f"   Unassigned target (<36): {total_unassigned} {'✅' if meets_unassigned else '❌'}")
print(f"   Empty vehicle removal: {total_vehicles - activated_vehicles} vehicles can be removed")

# For efficiency, we need to analyze the actual visit timings
# This requires parsing the itinerary structure
total_service_time = 0
visit_count = 0

vehicles = model_output.get('vehicles', [])
for vehicle in vehicles:
    shifts = vehicle.get('shifts', [])
    for shift in shifts:
        itinerary = shift.get('itinerary', [])
        for item in itinerary:
            if item.get('kind') == 'VISIT':
                # Parse duration (format: "PT23M" or "PT1H30M")
                duration_str = item.get('effectiveServiceDuration', 'PT0S')
                # Simple parsing - convert PT23M to minutes
                if 'H' in duration_str and 'M' in duration_str:
                    # Format like PT1H30M
                    parts = duration_str.replace('PT', '').split('H')
                    hours = int(parts[0])
                    minutes = int(parts[1].replace('M', ''))
                    duration_seconds = hours * 3600 + minutes * 60
                elif 'H' in duration_str:
                    # Format like PT2H
                    hours = int(duration_str.replace('PT', '').replace('H', ''))
                    duration_seconds = hours * 3600
                elif 'M' in duration_str:
                    # Format like PT23M
                    minutes = int(duration_str.replace('PT', '').replace('M', ''))
                    duration_seconds = minutes * 60
                else:
                    duration_seconds = 0
                
                total_service_time += duration_seconds
                visit_count += 1

# Calculate refined efficiency (remove empty vehicles, count working time only)
if activated_vehicles > 0:
    # Estimate working time: service + travel + setup (simplified)
    avg_visits_per_vehicle = visit_count / activated_vehicles
    travel_time_per_vehicle = max(0, (avg_visits_per_vehicle - 1) * 300)  # 5 min between visits
    setup_time_per_vehicle = avg_visits_per_vehicle * 600  # 10 min setup per visit
    travel_home_per_vehicle = 1800  # 30 min travel home
    
    working_time_per_vehicle = (total_service_time / activated_vehicles) + travel_time_per_vehicle + setup_time_per_vehicle + travel_home_per_vehicle
    total_working_time = working_time_per_vehicle * activated_vehicles
    
    refined_efficiency = (total_service_time / total_working_time * 100) if total_working_time > 0 else 0
    
    print()
    print(f"📈 REFINED EFFICIENCY ANALYSIS:")
    print(f"   Total service time: {total_service_time / 3600:.1f} hours")
    print(f"   Total visits processed: {visit_count}")
    print(f"   Avg visits per vehicle: {avg_visits_per_vehicle:.1f}")
    print(f"   Estimated working time: {total_working_time / 3600:.1f} hours")
    print(f"   REFINED EFFICIENCY: {refined_efficiency:.1f}%")
    
    meets_efficiency = refined_efficiency >= 70.0
    print(f"   Efficiency target (≥70%): {'✅' if meets_efficiency else '❌'}")
else:
    refined_efficiency = 0
    meets_efficiency = False

print()
print("🏆 OVERALL ASSESSMENT:")
if meets_unassigned and meets_efficiency:
    print("   ✅ ALL PRIMARY TARGETS LIKELY ACHIEVED!")
    print("   🎉 STRATEGIC APPROACH SUCCESS")
else:
    gaps = []
    if not meets_unassigned:
        gaps.append(f"unassigned ({total_unassigned} > 36)")
    if not meets_efficiency:
        gaps.append(f"efficiency ({refined_efficiency:.1f}% < 70%)")
    print(f"   ⚠️ Gaps remaining: {', '.join(gaps)}")
    print("   🔄 Next iteration needed")