---
date: 2026-03-03
topic: continuity-config-weights-balance
---

# Continuity vs efficiency: config weights and preferred/required combo

Brainstorm on using Timefold FSR **constraint weights** and **visit requirements** (required vs preferred vehicles, area affinity) to balance **continuity** (few caregivers per client) with **efficiency** (less wait, better staffing %).

## What we're optimizing for

- **Continuity**: each client served by a small, stable set of caregivers (e.g. ≤15 over 2 weeks).
- **Efficiency**: paid time used for visit + travel, not wait (staffing % = visit / (visit + travel + wait)).
- **Trade-off**: hard continuity (requiredVehicles, small pool) → less solver freedom → more wait; soft continuity (preferredVehicles) or larger pool → more freedom → less wait but possibly more distinct caregivers per client.

## Relevant FSR knobs

### 1. Visit requirements (input data)

| Attribute | Type | Effect |
|-----------|------|--------|
| **requiredVehicles** | Hard | Visit can **only** be assigned to vehicles in the list. Small pool → high continuity, risk of high wait. |
| **preferredVehicles** | Soft | Visit **prefers** those vehicles; solver can assign outside the list. Balances continuity (reward when match) vs freedom to reduce wait/travel. |
| **preferredVehiclesWeights** | Soft | Per-vehicle preference strength. |
| **prohibitedVehicles** | Hard | Visit must not be assigned to those vehicles. |

Ref: [Visit requirements (Timefold FSR)](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/visit-requirements-area-affinity-and-tags/visit-requirements).

### 2. Constraint weights (config profile)

From [Configuration parameters and profiles](https://docs.timefold.ai/timefold-platform/latest/how-tos/configuration-parameters-and-profiles#constraintWeights):

- Weights define **relative importance** of soft constraints. Higher weight = that constraint matters more in the score.
- Default is 1; 0 = constraint disabled. The solver minimizes a **weighted sum** of constraint penalties (multi-objective reduced to scalar).

Relevant for continuity vs wait/travel:

| Weight | Purpose | Use for |
|--------|---------|---------|
| **preferVisitVehicleMatchPreferredVehiclesWeight** | Soft reward when visit is assigned to a vehicle in its `preferredVehicles` list. | When using **preferredVehicles** (soft continuity): increase to favour continuity. |
| **minimizeVisitsOutsidePreferredArea** | Penalize assigning visits outside the shift’s preferred area. | When using **area affinity** on shifts: keep visits in “their” area. |
| **minimizeWaitingTimeWeight** | Penalize wait time. | **Wait-min**: increase (e.g. 2→3) to reduce paid wait. |
| **minimizeTravelTimeWeight** | Penalize travel time. | **Travel-min**: increase to reduce travel. |

Ref: [Constraints (FSR user guide)](https://docs.timefold.ai/field-service-routing/latest/user-guide/constraints), [Constraint weights (Platform)](https://docs.timefold.ai/timefold-platform/latest/how-tos/configuration-parameters-and-profiles#constraintWeights).

### 3. Area affinity

- **Preferred area** can be set on **shifts** (e.g. geographic or tag-based). Then **minimizeVisitsOutsidePreferredArea** penalizes assigning a visit to a shift whose preferred area doesn’t match.
- We currently build **client → vehicle pool** (manual / first-run / area). We do **not** yet set preferred area on shifts in the FSR input. So **minimizeVisitsOutsidePreferredArea** is 0 in our da2de902 input; turning it on would require adding preferred-area data to shifts and possibly to visits.

## Ideas: preferred vs required combo

**A. requiredVehicles only (current da2de902)**  
- Pool of 15 per client, hard constraint.  
- **Pro**: Strict cap on distinct caregivers. **Con**: High wait if pool is too tight.

**B. preferredVehicles only (soft continuity)**  
- Same pool (e.g. 15 or 25) but set **preferredVehicles** instead of requiredVehicles.  
- Solver can assign any vehicle; gets a **soft reward** when the assigned vehicle is in the preferred list.  
- **Pro**: Can assign outside pool to fill gaps and reduce wait. **Con**: Continuity only encouraged, not capped; distinct caregivers per client can exceed 15.

**C. Combo: requiredVehicles (larger pool) + preferVisitVehicleMatchPreferredVehiclesWeight**  
- Use **requiredVehicles** with a **larger** pool (e.g. 25–30) so the solver has room to reduce wait.  
- Optionally add **preferredVehicles** with a **subset** (e.g. top 10 from manual schedule) and set **preferVisitVehicleMatchPreferredVehiclesWeight** > 0 so the solver prefers that subset within the allowed set.  
- Balances: hard cap on max vehicles per client (e.g. 30), soft preference for “best” continuity subset (e.g. 10).

**D. preferredVehicles + high preferVisitVehicleMatchPreferredVehiclesWeight**  
- Use **preferredVehicles** only (no requiredVehicles).  
- Set **preferVisitVehicleMatchPreferredVehiclesWeight** relatively high so that breaking preference is costly.  
- Effect: “Soft cap” – solver can break continuity to reduce wait/travel only when the gain is large.  
- Tuning: weight vs minimizeWaitingTimeWeight / minimizeTravelTimeWeight defines the trade-off.

## Multi-objective nature

The solver uses a **scalarized** score (weighted sum of soft penalties). So we have:

- **Multi-objective** in the business sense: continuity vs wait vs travel vs shift cost vs …
- **Single score** in the solver: e.g.  
  `score = … − minimizeWaitingTimeWeight × wait − preferVisitVehicleMatchPreferredVehiclesWeight × (reward when preferred match) + …`

There is **no built-in Pareto exploration** or “target metric” in the Platform today. [Automated hyper-tuning / target metrics](https://feedback.timefold.ai/feature-requests/p/automated-hyper-tuning-of-constraint-weights-setting-targets-for-metrics) is a feature request. So we **tune by hand**: change weights → run → compare metrics (staffing %, continuity count, wait, travel).

Ref: [Constraints and Score (Timefold Solver)](https://docs.timefold.ai/timefold-solver/latest/constraints-and-score/overview), [Multi-objective optimization (Wikipedia)](https://en.wikipedia.org/wiki/Multi-objective_optimization).

## Suggested next steps

1. **Baseline**: Run with **preferredVehicles** (same pool as now, e.g. 15) and **preferVisitVehicleMatchPreferredVehiclesWeight = 1** (or 2). Compare to da2de902 (requiredVehicles, 15): expect lower wait, possibly more distinct caregivers per client.
2. **Wait-min config**: On the **same** da2de902 input (requiredVehicles, 15), run a config with **minimizeWaitingTimeWeight** raised (e.g. 2 or 3). Compare staffing % and wait hours.
3. **Larger pool**: Build input with **--continuity-max-per-client 25** (requiredVehicles), fresh solve. Compare wait and continuity.
4. **Combo**: preferredVehicles (pool 25) + **preferVisitVehicleMatchPreferredVehiclesWeight** 1–2 + **minimizeWaitingTimeWeight** 2. Compare.
5. **Area affinity** (later): If we add preferred area to shifts (and optionally visits), set **minimizeVisitsOutsidePreferredArea** = 1 and re-run.

## Open questions

- What is an acceptable **max distinct caregivers per client** if we relax to preferredVehicles? (e.g. 20? 25?)
- Do we want to **document** a small set of named profiles (e.g. “Continuity-first”, “Efficiency-first”, “Balanced”) with fixed weight sets for repeatability?

## Next

→ Use these ideas to define concrete config profiles and run a small experiment matrix (same dataset, different weights and preferred/required combinations), then compare metrics.
