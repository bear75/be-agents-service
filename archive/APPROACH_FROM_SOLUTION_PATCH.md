# Approach: From full solution → from-patch (pin + remove unused)

## Why not “reduce input and re-solve”

We tried sending a **reduced** input (31 vehicles, 143 shifts, fixed cost) as a **new** route plan. The solver ran from scratch on that reduced set and produced **29 unassigned visits** (run `db25f561`; see `reduced-fixed/export-field-service-routing-db25f561-*-output.json`, `unassignedVisits`). So **reducing capacity and re-solving does not preserve the original assignment** and can leave visits unassigned. We need an approach that **keeps the existing solution** and only changes the model (remove unused employees).

## Correct approach: from-patch (preview)

Timefold provides a **from-patch** endpoint (preview) for real-time planning:

- **Endpoint:** `POST /v1/route-plans/{id}/from-patch`
- **Body:** `{ "config": { ... }, "patch": [ { "op": "add"|"remove"|..., "path": "...", "value": ... } ] }`
- **Patch:** JSON Patch operations applied to the **modelInput** of the latest revision (path is relative to modelInput, e.g. `/visits/[id=Visit E]/pinningRequested`, `/freezeTime`, `/vehicles/-`).

**References:**

- [Real-time planning (preview)](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/preview/real-time-planning) – Patch feature overview
- [Real-time planning: pinning visits (preview)](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/preview/real-time-planning-pinning-visits) – Pinning with from-patch and example `patch` payloads

**Access:** The Patch feature is **preview only**. For early access, [contact Timefold](https://timefold.ai/contact).

## Working process (pin + trim via from-patch)

1. **First run:** POST full (or reduced) input to create a route plan → get solution.
2. **Trim and keep assignment:** Build a patch that **pins** all assigned visits and **removes** vehicles that have no visits. POST to `from-patch`. Same assignment, fewer vehicles.
3. **Repeat** when you trim again: from the latest solution, build patch (pin + remove empty vehicles), from-patch again.

**Limitation:** The API only supports removing **whole vehicles** in a patch, not individual shifts (e.g. break-only shifts cannot be removed via patch).

**Do not** submit a trimmed input as a **new** route plan if you want to keep the assignment — that re-solves from scratch with no pinning and can give a different solution or unassigned visits (we saw 29 unassigned).

## Intended flow

1. **POST** full fixed-cost JSON to `POST /v1/route-plans` → get `route_plan_id` and solution (e.g. 31 vehicles used, 143 shifts with visits, 1816 visits assigned).
2. **Build a patch** that:
   - **Pins** all assigned visits: for each visit in the solution’s itineraries, add (or set) `pinningRequested: true` and include `minStartTravelTime` from the solution (patch path like `/visits/[id=<visitId>]/pinningRequested`, `/visits/[id=<visitId>]/minStartTravelTime`).
   - **Ends shifts at depot arrival**: for each shift with at least one visit, set `maxEndTime` to `metrics.endLocationArrivalTime` (path `/vehicles/[id=X]/shifts/[id=Y]/maxEndTime`), removing idle time after the last visit.
   - **Removes** shifts with empty itinerary (no assigned visits): `remove` ops on `/vehicles/[id=X]/shifts/[id=Y]`.
   - **Removes** unused vehicles (and their shifts): use `remove` ops on `/vehicles/[id=<vehicleId>]` for each vehicle that has **no** shift with at least one visit in the solution.
3. **POST** that patch to `POST /v1/route-plans/{route_plan_id}/from-patch`. Timefold creates a **new revision** from the previous solution and applies the patch; with all assigned visits pinned, the assignment stays the same and the plan no longer contains the removed employees/shifts.

Result: same assignment, no oversupply, no second full solve (and no 29 unassigned visits).

## Example patch (from Timefold docs)

Adding freeze time, pinning one visit, and adding a new visit:

```json
{
  "config": { "run": { "name": "Real-time planning: pinning" } },
  "patch": [
    { "op": "add", "path": "/freezeTime", "value": "2027-02-01T12:00:00Z" },
    { "op": "add", "path": "/visits/[id=Visit E]/pinningRequested", "value": true },
    { "op": "add", "path": "/visits/-", "value": { "id": "Visit M", "location": [...], "serviceDuration": "PT1H30M", "priority": "1" } }
  ]
}
```

For “remove unused employees”, add **remove** operations for each unused vehicle (and optionally for each unused shift under kept vehicles). Exact path syntax (e.g. `/vehicles/[id=Route A2]`) is in the [preview pinning guide](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/preview/real-time-planning-pinning-visits).

## Summary

| Approach                                                                         | Result                                                                            |
| -------------------------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| **Reduce input and re-solve** (POST new route plan with 31 vehicles, 143 shifts) | ❌ 29 unassigned visits (solver finds a different, worse allocation).             |
| **from-patch** (pin visits, end shifts at depot, remove empty shifts/vehicles)   | ✅ Same assignment, no oversupply, less idle time; requires Patch preview access. |

See also:

- [PIPELINE.md](PIPELINE.md) – step-by-step from CSV to from-patch iteration.
- [PINNED_VISITS_GUIDE.md](../../docs/docs_2.0/09-scheduling/PINNED_VISITS_GUIDE.md) – pinning and the from-patch flow.
