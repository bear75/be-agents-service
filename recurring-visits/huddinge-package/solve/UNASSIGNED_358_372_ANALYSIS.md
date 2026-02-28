# Why visits 358 & 372 are never assigned

## The two unassigned visits

| Field | Value |
|-------|--------|
| **Visit IDs** | 358, 372 |
| **Visit group** | `visitGroup_43_w1_2026-02-23` |
| **Client** | H035_53 (same location for both) |
| **Location** | 59.2399459, 17.9388306 |
| **Date** | 2026-02-23 (Monday) |
| **Time window** | 16:51–17:46 (358), 16:51–17:53 (372); maxStart 17:36 |
| **Services** | 358: Toalettbesök 10 min · 372: Förflyttning 17 min |

They are a **double-employee visit group**: two staff must be at the same address in the same time window (care rules require two people for this client at that time).

---

## What’s different vs other visits

1. **Visit group (two employees)**  
   Both visits must be done by **two different vehicles/shifts** at the same place and time. The solver must find a **pair** of shifts that can both:
   - overlap the window 16:51–17:53,
   - reach the location in time,
   - and have the group’s total service time (10+17 min) covered (one visit per vehicle).

2. **Evening-only window**  
   Day shifts on 2026-02-23 all end at **15:00**. The window starts at **16:51**, so only **evening** shifts (16:00–22:00) can serve this group.

3. **Supply on 2026-02-23**  
   There are **8 evening shifts** on 2026-02-23 (16:00–22:00). So there is capacity in the input. The unassigned analysis therefore classifies this as **config** (≥1 overlapping shift), not supply.

4. **Why the solver still leaves them unassigned**  
   - Every evening shift on that day is already filled with other visits.  
   - Inserting this group means **two** of those shifts must both detour to H035_53 in 16:51–17:53.  
   - That can imply:
     - High travel cost (detour, or awkward ordering),
     - Or no feasible insertion that respects time windows and visit order for both vehicles.  
   So the solver prefers to leave these two as unassigned (soft penalty) rather than worsen the rest of the solution.

---

## What to try

1. **Increase unassigned penalty**  
   Make the soft cost of “unassigned visit” higher so the solver tries harder to place 358 and 372 (e.g. in the Timefold profile or request).

2. **Add one dedicated evening shift for double-employee calls**  
   Add an evening shift on 2026-02-23 (and possibly other evenings) that is reserved or preferred for visit-group work, so the solver has a clear “slot” for the second employee.

3. **Widen the time window**  
   If care rules allow, slightly wider or slightly shifted window (e.g. 16:30–18:00) might allow a feasible insertion for both vehicles.

4. **Check visit-group modelling**  
   Confirm in Timefold FSR docs that visit groups are modelled as “two different vehicles at same place/time”. If the engine expects both visits on the same vehicle, the input or model may need to be changed.

5. **Manual assignment**  
   As a last resort: fix the rest of the schedule, then assign 358 and 372 to two chosen evening shifts (e.g. the two with shortest detour to H035_53) and lock those visits (e.g. via from-patch or pinning).

---

## Quick reference

- **Input (tf-16feb-0800):**  
  `visitGroup_43_w1_2026-02-23` with visits 358 and 372; window 2026-02-23 16:51–17:53.
- **Evening shifts on 2026-02-23:**  
  8 shifts (e.g. 167269bd, c57bac83, 3968996e, a2449127, e912cdb0, 7c7f0865, 8e291f2a, 6cc62483); all 16:00–22:00 and all already used in the solution.
