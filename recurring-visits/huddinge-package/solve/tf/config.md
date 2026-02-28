Re-solve
Overview
Visualization
Input
Output
Configuration
Log

## 2dbe0eb

22 minutes ago
request

Constraint weights
Define the relative importance of the soft constraints of a model. Give a constraint a weight of 0 to not optimize for it, and a higher weight to increase its relative importance. The combination of constraint weights will define the optimization goal.

Time windows and opening hours
Preferred visit time window
modelConfiguration.preferredVisitTimeWindowWeight
Assign the preferred time windows to visits.
1
Fairness
Balance time utilization
modelConfiguration.balanceTimeUtilizationWeight
Ensure fairness across technicians' workloads, balancing travel times, wait times, service times, and break times.
0
Movable visits and multi-day schedules
Prefer visits scheduled to the earliest day
modelConfiguration.preferVisitsScheduledToEarliestDayWeight
Schedules visits to the earliest day possible.
0
Priority visits and optional visits
Prefer scheduling optional visits
modelConfiguration.preferSchedulingOptionalVisitsWeight
Schedules as many optional visits as possible.
0
Minimize the visit completion risk
modelConfiguration.minimizeVisitCompletionRiskWeight
Schedules higher priority visits earlier in the day to avoid the risk of running out of time on the day.
1
Route optimization
Minimize travel time
modelConfiguration.minimizeTravelTimeWeight
Minimize the amount of time technicians spend traveling.
3
Minimize travel distance
modelConfiguration.minimizeTravelDistanceWeight
Minimize the distance technicians travel on the road.
0
Max shift travel time (soft)
modelConfiguration.maxSoftShiftTravelTimeWeight
Limit the time a technician spends by traveling.
1
Minimize waiting time
modelConfiguration.minimizeWaitingTimeWeight
Minimize the amount of time technicians spend waiting before starting a visit.
1
Service level agreements
Latest SLA end time
modelConfiguration.latestSlaEndTimeWeight
Minimize the number of visits that end after the max SLA end time.
0
Shift hours and overtime
Max shift end time (soft)
modelConfiguration.maxSoftShiftEndTimeWeight
Minimize the overtime technicians should work.
0
Max last visit departure time (soft)
modelConfiguration.maxSoftLastVisitDepartureTimeWeight
Avoid keeping technicians on jobs after the end of their shifts.
0
Skills
Minimize scheduling vehicles with unnecessary skill levels
modelConfiguration.minimizeUnnecessarySkillsWeight
Avoid assigning technicians with higher skill levels than are needed for visits.
0
Technician costs
Minimize shift costs
modelConfiguration.minimizeShiftCostsWeight
Minimize technician costs.
0
Technician rating
Maximize technician rating
modelConfiguration.maximizeTechnicianRatingWeight
Maximize the technician rating of the visit.
0
Visit requirements, area affinity and tags
Prefer visit vehicle match preferred vehicles
modelConfiguration.preferVisitVehicleMatchPreferredVehiclesWeight
Assign the preferred vehicles specified for visits.
0
Minimize scheduling visits outside the preferred area
modelConfiguration.minimizeVisitsOutsidePreferredArea
Minimize assigning visits outside of the preferred area of a shift.
0

Model configuration
visitCompletionRiskMinimalTimeToShiftEnd
modelConfiguration.visitCompletionRiskMinimalTimeToShiftEnd
The minimal time "buffer" (ISO 8601 duration) before the end time of a vehicle shift. Every visit with a scheduled completion before that moment is considered completable without any risk.
0

seconds
visitCompletionRiskMinimalPriority
modelConfiguration.visitCompletionRiskMinimalPriority
The minimal priority level for considering the visit completion risk.

LOW
defaultTechnicianRating
modelConfiguration.defaultTechnicianRating
The default technician rating used for technicians without a rating.
0

Solve settings
Define specific values to be used when solving a dataset with this profile.

Max solve duration
runConfiguration.termination.spentLimit
When the solver has spent the given amount of time (ISO 8601 duration), it will stop.
2

hours
Smart Terminations
See documentation

Default
Terminate solving when improvements are minimal.

Unimproved termination
runConfiguration.termination.unimprovedSpentLimit
When score hasn't improved for the given amount of time (ISO 8601 duration), the solver will stop

seconds

After initial solution
Terminate solving right after the construction heuristic.

Step count termination
runConfiguration.termination.stepCountLimit
Maximum solver step count. The solver will stop solving after a pre-determined amount of steps. Use this termination if you want to benchmark your models, not recommended for production use.
Thread count
runConfiguration.maxThreadCount
Number of simultaneous threads to be used for solving (maximum 4).
4
Memory
resourcesConfiguration.memory
Amount of memory allocated per thread for a run.
4096
MB
Maps provider

osrm
Maps location
Don't see the map you need? Contact us.

Sweden (Car)
Configuration profile used:
Huddinge-test-long

---

## Recommended next steps (19 unassigned, all evening / config)

Analysis: all 19 unassigned have ≥1 overlapping shift (config), all evening. So try **config first** to push the solver to assign them; if still unassigned, **add evening shifts** then re-solve.

### Option A: New config profile — **not recommended** (tried: solution got worse)

Run 4f788253 with profile "huddinge-test-long-update" (Huddinge-assign-evening weights) gave **88 unassigned** (vs 19 with original). Use **Option B with original profile** instead.

_(Original suggestion:)_ Create a copy of **Huddinge-test-long** (e.g. "Huddinge-assign-evening") and change:

| Setting                                 | Current | Recommended | Reason                                         |
| --------------------------------------- | ------- | ----------- | ---------------------------------------------- |
| Balance time utilization                | 0       | **1**       | Spread load so evening shifts take more visits |
| Prefer visits scheduled to earliest day | 0       | **1**       | Pack movable visits into available days        |
| Minimize travel time                    | 3       | **2**       | Slightly allow more travel to fit the 19       |
| Max soft shift travel time              | 1       | **0**       | Don’t penalize longer travel per shift         |
| Minimize visit completion risk          | 1       | **2**       | Schedule mandatory visits earlier in shift     |

Keep: Preferred visit time window 1, Minimize waiting time 1. Max solve duration 2h, 4 threads.

Re-solve with the **same input** and the new profile. Then run `solve_report.py` on the new output. If unassigned > 0, use Option B.

### Option B: Add evening shifts (if config alone doesn’t clear 19)

All unassigned are evening; peak days 2026-02-27 and 2026-02-28 have 3 each. Add 1–2 extra evening vehicles (14–28 shifts):

```bash
cd docs_2.0/recurring-visits/huddinge-package
python3 scripts/add_evening_vehicles.py solve/input_20260214_171612.json --count 1 --out solve/input_evening.json --no-timestamp
```

Re-solve with the **new input** (e.g. `solve/input_evening.json`) and the **original profile (Huddinge-test-long)**. Then from-patch to trim empty shifts if needed. See [new-config/NEW_CONFIG_ANALYSIS_4f788253.md](new-config/NEW_CONFIG_ANALYSIS_4f788253.md) for the add-shifts run plan.
