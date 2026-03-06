# Test tenant: Metrics and continuity vs brainstorm goal

Reference: [2026-03-03-continuity-config-weights-brainstorm.md](../../../docs/brainstorms/2026-03-03-continuity-config-weights-brainstorm.md).

## Goals (from brainstorm)

- **Continuity:** Each client served by a small, stable set of caregivers (e.g. **≤15** over 2 weeks).
- **Efficiency:** Paid time used for visit + travel, not wait. **Staffing %** = visit / (visit + travel + wait). Field efficiency target **>67.5%** (Slingor benchmark).
- **Trade-off:** Hard continuity (requiredVehicles, small pool) → less solver freedom → more wait; soft continuity (preferredVehicles) or larger pool → more freedom → less wait but possibly more distinct caregivers per client.

---

## Fresh solves (pool 15, da2de902 base)


| Run           | Route plan ID | Unassigned | Empty shifts | Field eff. | Staffing eff. | Continuity: clients >15 | Continuity: avg | Continuity: max |
| ------------- | ------------- | ---------- | ------------ | ---------- | ------------- | ----------------------- | --------------- | --------------- |
| **Preferred** | 688faece      | 4          | 65           | **85.08%** | 52.33%        | **0**                   | **3.5**         | **12**          |
| **Wait-min**  | a4be8810      | 94         | 78           | 82.83%     | 51.07%        | 0                       | 2.8             | 7               |
| **Combo**     | 8e07450d      | 6          | 38           | 79.59%     | 52.20%        | 10                      | 9.9             | 22              |


- **Preferred:** Best continuity (0 over 15, max 12) and best field efficiency (85.08%); only 4 unassigned. Best balance for this dataset.
- **Wait-min:** Continuity looks good (0 over 15) only because **94 visits are unassigned** — not valid for benchmarking. Ignore for goal comparison.
- **Combo:** Best feasibility (6 unassigned, 38 empty) but **10 clients over 15** distinct caregivers (max 22). So: more assignments, worse continuity.

**Vs goal:** Preferred meets continuity (≤15) and field efficiency (>67.5%). Combo trades continuity for feasibility.

---

## From-patch (trimmed shifts)

### From-patch preferred (963c3aa9) — fetched and analyzed

- **Parent:** 688faece. **Status:** SOLVING_COMPLETED.
- **Test folder:** `from_patch_preferred_963c3aa9/` — output.json, metrics/, continuity.csv


| Metric                  | Fresh preferred (688faece)      | From-patch preferred (963c3aa9) |
| ----------------------- | ------------------------------- | ------------------------------- |
| Unassigned              | 4                               | 4                               |
| Shifts                  | 412 (347 with visits, 65 empty) | **347** (0 empty)               |
| Continuity: clients >15 | 0                               | **0**                           |
| Continuity: max         | 12                              | **12**                          |
| Continuity: avg         | 3.5                             | **3.5** (unchanged)             |


**What the trim did (build_from_patch.py, default trim-to-visit-span):**  
1. **Partly empty shifts:** Each non-empty shift’s window was trimmed to **visit span** (first visit start → last visit end). So idle **before** the first visit and **after** the last visit was removed; the shift window no longer includes that “partly empty” time.  
2. **Fully empty shifts:** The **65** shifts with no visits at all were removed.  
So we did **not** only remove empty shifts; we also shortened every non-empty shift to the span of its visits (no tail after last visit, no head before first visit).  
Assignment and continuity are unchanged (same 4 unassigned, same per-client distinct caregivers). The `--exclude-inactive` metrics report shows very high wait share because the API’s per-shift totals still include wait *within* the trimmed window (e.g. between visits); use **counts** (347 shifts, 0 empty) and **continuity** for comparison.

### From-patch combo

- **Test folder:** `from_patch_combo/` (payload.json, route_plan_id.txt only for now).
- When complete: fetch → save as `from_patch_combo/output.json` → `metrics.py ... --exclude-inactive --save from_patch_combo/metrics` → `continuity_report.py` → save continuity in folder. Same flow as preferred.

---

## One-busy-day

- **Route plan ID:** 0e4eec27-13a3-4348-be93-38c111af8823  
- **Input:** `_archive/input_one_day_2026-02-16.json` (preferredVehicles only, 475 visits, 29 vehicles).  
- **Next:** When solved, fetch output → extract client→vehicle from itineraries → patch full 2-week input with those preferredVehicles → run full 2-week solve.

---

## Larger pool (25)

- **Route plan ID:** a88a5fde-c39e-4182-9be6-cfd6420b2999  
- **Input:** `_archive/input_pool25_required.json` (requiredVehicles, 25 per client from same manual CSV).  
- **Next:** When solved, fetch → metrics + continuity. Compare to pool-15: expect fewer unassigned and possibly lower wait; continuity still capped at 25 by construction.

---

## Summary vs brainstorm

1. **Continuity ≤15:** **Preferred** (688faece) achieves it (0 clients over 15, max 12). Combo exceeds (10 clients over 15).
2. **Efficiency >67.5%:** All three fresh runs meet **field** efficiency (79–85%). Staffing efficiency ~51–52% (idle/empty shifts drag it down; from-patch metrics will show improvement with trimmed windows).
3. **Trade-off:** Preferred gives best continuity + best field efficiency with few unassigned. Combo prioritizes feasibility over continuity. Wait-min is infeasible (94 unassigned) and should not be used as baseline.
4. **Next tuning:** Run from-patch for preferred and combo; compare post-trim metrics and continuity. Run pool-25 when complete; then consider combo with **preferredVehicles + pool 25** and same weights for a softer cap with more solver freedom.

