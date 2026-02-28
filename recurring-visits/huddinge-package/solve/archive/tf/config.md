# Timefold FSR Configuration Profile

**Profile:** Caire (editable in Timefold Dashboard)  
**Usage:** Select this profile when solving — no need to edit input JSON.

## How to edit

1. Open **Timefold Dashboard** → your route plan
2. Go to **Configuration** → **Profiles**
3. Select "Caire" (or create a new profile)
4. Edit constraint weights and solve settings
5. Re-run solve — the same input will use the new profile

## Constraint weights

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
3
Priority visits and optional visits
Prefer scheduling optional visits
modelConfiguration.preferSchedulingOptionalVisitsWeight
Schedules as many optional visits as possible.
1
Minimize the visit completion risk
modelConfiguration.minimizeVisitCompletionRiskWeight
Schedules higher priority visits earlier in the day to avoid the risk of running out of time on the day.
2
Route optimization
Minimize travel time
modelConfiguration.minimizeTravelTimeWeight
Minimize the amount of time technicians spend traveling.
1
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
2
Service level agreements
Latest SLA end time
modelConfiguration.latestSlaEndTimeWeight
Minimize the number of visits that end after the max SLA end time.
1
Shift hours and overtime
Max shift end time (soft)
modelConfiguration.maxSoftShiftEndTimeWeight
Minimize the overtime technicians should work.
1
Max last visit departure time (soft)
modelConfiguration.maxSoftLastVisitDepartureTimeWeight
Avoid keeping technicians on jobs after the end of their shifts.
1
Skills
Minimize scheduling vehicles with unnecessary skill levels
modelConfiguration.minimizeUnnecessarySkillsWeight
Avoid assigning technicians with higher skill levels than are needed for visits.
1
Technician costs
Minimize shift costs
modelConfiguration.minimizeShiftCostsWeight
Minimize technician costs.
3
Technician rating
Maximize technician rating
modelConfiguration.maximizeTechnicianRatingWeight
Maximize the technician rating of the visit.
0
Visit requirements, area affinity and tags
Prefer visit vehicle match preferred vehicles
modelConfiguration.preferVisitVehicleMatchPreferredVehiclesWeight
Assign the preferred vehicles specified for visits.
1
Minimize scheduling visits outside the preferred area
modelConfiguration.minimizeVisitsOutsidePreferredArea
Minimize assigning visits outside of the preferred area of a shift.
1

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
1

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
Configuration profile used: Caire

---

## Profile suggestions (see docs/PRIORITIES.md)

| Profile focus        | Key weights to adjust                                                    |
| -------------------- | ------------------------------------------------------------------------ |
| Minimize travel      | `minimizeTravelTimeWeight` 2–3                                           |
| Maximize assignments | `preferSchedulingOptionalVisitsWeight` 2–3, `minimizeShiftCostsWeight` 1 |
| Minimize waiting     | `minimizeWaitingTimeWeight` 3                                            |
