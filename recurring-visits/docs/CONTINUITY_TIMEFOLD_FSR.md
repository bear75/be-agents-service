# Continuity constraint with Timefold FSR

## What you want

- **Continuity**: each client (person) is served by **at most 15 distinct caregivers (vehicles)** over the 2-week window.
- **Solver freedom**: the solver should be able to choose **any** combination of up to 15 vehicles per client, not a fixed list decided in advance.

## What the FSR model offers

From [Visit requirements (Timefold FSR)](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/visit-requirements-area-affinity-and-tags/visit-requirements):

| Attribute                  | Type | Meaning                                                                |
| -------------------------- | ---- | ---------------------------------------------------------------------- |
| `requiredVehicles`         | Hard | Visit can **only** be assigned to vehicles in this list (vehicle IDs). |
| `preferredVehicles`        | Soft | Visit **prefers** to be assigned to vehicles in this list (reward).    |
| `preferredVehiclesWeights` | Soft | Same, with per-vehicle preference weights.                             |
| `prohibitedVehicles`       | Hard | Visit **must not** be assigned to vehicles in this list.               |

All of these take a **fixed list of vehicle IDs** per visit. They do **not** express:

- “This visit may be served by at most 15 **different** vehicles (in aggregate with other visits of the same client).”
- “Any combination of up to 15 vehicles per client.”

So:

- **requiredVehicles = [v1, v2, …, v15]**  
  → You fix **which** 15 vehicles. Solver has full flexibility **within** those 15, but not over “which 15” in the first place.

- **preferredVehicles**  
  → Only adds a soft reward for using certain vehicles; it does **not** cap how many distinct vehicles serve a client.

FSR does **not** expose a built-in constraint like “max distinct vehicles per client” or “max distinct vehicles per tag/group”. The public constraint list (vehicle resource constraints, visit service constraints, etc.) has no continuity/cardinality constraint.

## Can we use preferred/required vehicles to get “max 15”?

- **Preferred vehicles**  
  You could set `preferredVehicles` (or weights) to encourage re-use of certain vehicles, but:

  - You still have to choose **which** vehicles to prefer (e.g. from a prior solution or manual schedule).
  - There is no “prefer using at most 15 different vehicles in total for this client”; it’s per-visit preference only.
    So you don’t get “any combination of 15” and no hard cap of 15.

- **Required vehicles with a list of 15**  
  If for each client you set **all** that client’s visits to the same `requiredVehicles` list of (at most) 15 vehicle IDs:
  - You **do** get a hard cap: that client is never served by more than 15 vehicles.
  - But the **set** of 15 is fixed by you (or by a pre-processing step), not chosen freely by the solver across the whole fleet.

So: you can enforce “at most 15 vehicles per client” **only** by fixing a pool of 15 per client and using `requiredVehicles`. You cannot express “any combination of 15” with the current FSR visit-requirements API.

## Practical workaround: pool of 15 per client

To get **at most 15 vehicles per client** and **as much solver flexibility as possible** within that:

1. **Define a pool of (at most) 15 vehicles per client**  
   For each client (person), decide a set of up to 15 vehicle IDs that are allowed to serve that client. Options:

   - **From manual schedule**: use the distinct `external_slinga_shiftName` (mapped to FSR vehicle IDs) that already serve that client in the expanded CSV; take up to 15. Solver then optimizes within that known “continuity-friendly” set.
   - **From an unconstrained run**: run FSR once with no continuity restriction; for each client, take the 15 vehicles that served the most visits (or 15 that cover the most visits). Set **all** that client’s visits to `requiredVehicles = that list` and re-solve. Then the “which 15” is driven by the first solution; the second run only improves within that 15.

2. **Set `requiredVehicles` on every visit of that client**  
   In the FSR input, for each visit that belongs to client C, set:

   ```json
   "requiredVehicles": [ "Dag_01_Central_1", "Helg_06_Central", … ]
   ```

   with that client’s pool (size ≤ 15). Same client → same list for all visits of that client.

3. **Run the solver**  
   FSR will only assign those visits to vehicles in the list; you get at most 15 distinct vehicles per client and full flexibility within each pool.

So: you **can** use the FSR model to enforce “max 15 caregivers per client” by **precomputing** a pool of 15 per client and using `requiredVehicles`. You **cannot** get “any combination of 15” chosen entirely by the solver in one shot with the current API.

## If you need “any 15” chosen by the solver

- **Custom constraint (self-hosted / Timefold Solver)**  
  With the open-source Timefold Solver and Constraint Streams you could add a soft (or hard) constraint: e.g. “for each client, penalize when the number of distinct vehicles serving that client exceeds 15.” That would let the solver choose which vehicles serve each client under a cardinality cap. This is not available in the managed FSR API as a single built-in constraint.

- **Feature request**  
  You can ask Timefold for a first-class “max distinct vehicles per client/tag” (or per visit-group) constraint in FSR:  
  [Feature requests (FSR)](https://docs.timefold.ai/field-service-routing/latest/feature-requests).

## Model configuration: fairness and second-order effect on continuity

**Fairness (balance time utilization)** is a separate concern from continuity: it evens out **workload across technicians** (travel, wait, service, break time) so no one is over- or under-used. It does **not** directly cap how many distinct caregivers serve a client.

As a **second-order effect**, it can still help continuity:

- The FSR model configuration includes **`balanceTimeUtilizationWeight`** (see [Fairness](https://docs.timefold.ai/field-service-routing/latest/vehicle-resource-constraints/fairness)). Higher values push the solver to balance utilization across technicians.
- That can **consolidate** work onto fewer, fuller shifts (e.g. 5 full-day instead of 10 half-day): the solver prefers to use fewer technicians with fuller days rather than many with underused shifts.
- **Fewer vehicles used in the solution** ⇒ each client is served by a subset of a smaller overall set of caregivers ⇒ **max (and average) distinct caregivers per client can go down** even without any continuity constraint.

So `balanceTimeUtilizationWeight` does not enforce “max 15 per client,” but it can **indirectly** improve continuity by reducing the total number of active caregivers in the schedule. Worth testing in the prototype: increase the weight (e.g. 2 or higher), run the same input, then compare with `continuity_report.py` and metrics to see if distinct caregivers per client drop while efficiency stays acceptable.

## Summary

| Goal                                        | Possible with current FSR? | How                                                                                                                                                                         |
| ------------------------------------------- | -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Cap each client at 15 vehicles (fixed pool) | Yes                        | Set `requiredVehicles` to a list of ≤15 vehicle IDs for all visits of that client.                                                                                          |
| “Any combination of 15” in one solve        | No                         | No built-in cardinality constraint; only fixed lists per visit.                                                                                                             |
| Maximize flexibility for a given cap        | Partially                  | Use a pool of 15 derived from manual schedule or from a first unconstrained run, then `requiredVehicles` + re-solve.                                                        |
| Reduce distinct caregivers indirectly       | Partially                  | Increase `balanceTimeUtilizationWeight` (fairness): consolidates work onto fewer, fuller shifts → fewer active vehicles → lower max caregivers per client as a side effect. |

So: use **requiredVehicles** with a **list of max 15 vehicles per client** (chosen by you or by a pre-step) to see what happens when continuity is enforced; the solver will have full flexibility within that list, but not over the choice of the 15 themselves in the same run.
