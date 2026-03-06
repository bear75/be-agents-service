# Reducing wait and balancing continuity

High **wait** in continuity runs is paid time but not at the client, so it tanks **staffing** efficiency (e.g. ~63% vs ~90% field). This doc covers how to loosen continuity to reduce wait, how client–caregiver clustering works, and how to test new “travel/wait reduce” configs.

---

## FAQ

### Did pipeline_da2de902 use 15 per client?

**Yes.** The da2de902 continuity input was built when the pipeline used a fixed cap of **15** vehicles per client (manual pools). The `--continuity-max-per-client` option was added later; da2de902 effectively used 15.

### How does “15” work? Will a reduce-wait config fix efficiency?

- **15 = pool size, not “15 vehicles assigned per visit”.** Each visit is assigned to **one** vehicle/shift. For each client we set **requiredVehicles** = list of up to 15 vehicle IDs. So every visit of that client can **only** be served by one of those 15 vehicles. The solver picks one vehicle per visit from that pool.
- With a **small pool** (15), the solver has less flexibility to sequence visits and fill gaps → more **wait** (e.g. arrive early and wait for time window, or gaps between visits). So yes, **15 can still lead to high wait and low staffing efficiency**.
- A **reduce-wait config** (higher `minimizeWaitingTimeWeight`) on the **same** input makes the solver prefer solutions with less wait **within** the same requiredVehicles. It does **not** add more vehicles to the pool. So it can improve **order and timing** (less idle between visits) but cannot expand the choice set. For a big gain in efficiency you typically need **looser continuity** (larger pool or preferredVehicles) **and/or** a wait-min config.

### Why can a vehicle have wait 11–13 if we only restrict “who” can serve?

We only restrict **which vehicles can serve which clients** (the pool). We do **not** model or distribute **demand** (visit load over time). So:

- A vehicle might be in the pool for many clients in an area.
- The **visits** (demand) have fixed times (e.g. 10–11 and 13–14).
- The solver assigns those visits to that vehicle → the vehicle does 10–11 and 13–14 and has **nothing to do 11–13** → **wait**.
- So wait comes from **temporal spread**: the same vehicle is allowed to serve many clients, but the actual visit times don’t fill the shift. The pool doesn’t create demand; it only restricts who can serve. Reducing wait then needs either more assignment flexibility (larger pool / preferredVehicles), stronger penalty on wait (config), or both.

## 1. Fixing the wait: loosen continuity

**Options (in order of impact):**

| Approach | What it does | How to run |
|----------|----------------|------------|
| **Larger pool (more vehicles per client)** | Same hard constraint (requiredVehicles) but each client can be served by more vehicles → solver has more flexibility → less wait. | `process_huddinge.py --continuity --continuity-max-per-client 25` (or 30). Then **fresh solve** with that input. |
| **Soft continuity (preferredVehicles)** | Solver **prefers** the continuity pool but can assign **any** vehicle to reduce wait/travel. | `process_huddinge.py --continuity --continuity-preferred`. Then **fresh solve**. |
| **Config: higher wait/travel weights** | Same input; solver penalizes wait/travel more. | **Fresh solve** with a config that has higher `minimizeWaitingTimeWeight` (and optionally `minimizeTravelTimeWeight`). No dataset change. |

**Recommendation:** Try **larger pool** first (e.g. `--continuity-max-per-client 25`), then **preferredVehicles** (`--continuity-preferred`), then a **Wait-min** config (see PRIORITIES.md). Compare staffing % and continuity metrics.

## 2. Fresh run with “preferred vehicles, more per client”

- **More per client (requiredVehicles):**  
  Use the **same** pipeline (same expanded CSV, same base input if you use one), with a larger cap:  
  `--continuity --continuity-max-per-client 25` (or 30).  
  That produces a new continuity input (more vehicle IDs per visit). Run a **fresh solve** (not from-patch) with that input.

- **Preferred vehicles (soft):**  
  `--continuity --continuity-preferred`  
  builds pools the same way but writes **preferredVehicles** instead of **requiredVehicles**. Fresh solve with that input.

- **Combination:**  
  `--continuity --continuity-max-per-client 25 --continuity-preferred`  
  gives a larger preferred pool per client.

## 3. How we cluster clients with caregivers

**“Client visit area demand = employee shift?”**  
Not literally. Clustering is **client → set of vehicles (shifts)**, not “demand = one shift.”

- **Manual:** From expanded CSV: for each client, we take the **distinct caregiver shift names** that served them in the manual schedule → map to FSR vehicle IDs → cap at `max_per_client`. So “who served this client in the manual plan.”

- **First-run:** From an **unconstrained** FSR solution: for each client, we take the **top N vehicles by visit count** → cap at `max_per_client`. So “who served this client in the first optimization.”

- **Area:** Clients are grouped by **area** (e.g. `serviceArea_address` in CSV). Vehicles are **assigned to areas** (e.g. round-robin). For each client, pool = **vehicles assigned to that client’s area**, cap `max_per_client`. So “client’s area” → “vehicles serving that area.” Employee shifts (vehicles) come from the same FSR input; we do **not** map “demand” to a single shift, we map “client” → “set of vehicles (shifts) that can serve them.”

So: **client visit area (or manual/first-run history) → set of allowed/preferred vehicles (caregiver shifts).** Not “demand = one employee shift.”

## 4. Testing a new config for da2de902 (e.g. travel/wait reduce)

**Can you start from from-patch or do you need a fresh solve?**

- **From-patch with a new config:**  
  Yes. When you submit a from-patch you can pass a different `--configuration-id`. The **re-solve** step uses that config on the **patched** problem (trimmed shifts, no empty, assignments from the patch). So you can try a “travel/wait reduce” config on the **already-trimmed** solution. The solver may only refine timing/order within pinned assignments; it often **cannot** reassign visits to other vehicles, so **wait may not drop much**.

- **Fresh solve with new config:**  
  For the **same dataset** (e.g. original da2de902 continuity input), run a **new solve** with a config that has higher `minimizeWaitingTimeWeight` (and optionally `minimizeTravelTimeWeight`). The solver has **full** freedom to assign visits (within requiredVehicles). So for **reducing travel/wait**, a **fresh solve** with the new config is the right comparison.

**Does the travel/wait reduce config require a fresh dataset?**  
**No.** Same input JSON; only the **configuration ID** (and thus the weights) changes. No need to rebuild or re-export the dataset.

**Summary:**

| Goal | Use | Dataset |
|------|-----|--------|
| Try “wait-min” config on **full** problem (da2de902) | **Fresh solve** with new config on **original** da2de902 continuity input | Same JSON, no change |
| Try “wait-min” config on **trimmed** solution | **From-patch** with new config on da2de902 (or e5de3f5d) | Same patched input |

For meaningful **reduction in wait**, prefer **fresh solve** with the new config on the original continuity input.
