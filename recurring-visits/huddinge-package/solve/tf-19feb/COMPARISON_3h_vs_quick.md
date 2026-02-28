# Run comparison: 3h run vs quick run (tf-19feb)

## Summary

| | **3h run** (073f6280) | **Quick run** (5f8eae79) |
|---|------------------------|---------------------------|
| **Route plan ID** | `073f6280-9da5-44ca-8184-e1e00c97cd33` | `5f8eae79-809a-4f46-96d2-aed444403c3f` |
| **Profile** | huddinge-test-long | huddinge-test-long |
| **Type** | from-request | from-input (child of 073f6280) |
| **Start** | 2026-02-15 10:24:48Z | 2026-02-19 14:17:18Z |
| **Complete** | 2026-02-15 12:59:26Z | 2026-02-19 14:26:19Z |
| **Wall-clock duration** | **~2 h 35 min** | **~9 min** |
| **Unassigned visits** | **2** | **22** |
| **Assigned visits** | 3,620 | 3,600 |
| **Score** | 0hard/-20000medium/-1902544soft | 0hard/-220000medium/-5453163soft |
| **Avg travel per visit** | PT2M53S | PT7M59S |

Same dataset size (3,622 visits), same profile (Huddinge-test-long, 5h max duration). The quick run stopped after ~9 minutes with 22 unassigned and much worse medium score.

---

## Config (identical)

Both runs used **Huddinge-test-long**:

- **spentLimit:** 5 hours
- **unimprovedSpentLimit:** (not set in the exported config text; likely default “diminished returns” or a short value)
- Constraint weights: identical (preferred visit time window 1, minimize travel 3, etc.)
- 4 threads, 4096 MB memory, Sweden (Car)

So the **only** difference in configuration is how long the solver actually ran before terminating.

---

## Why the quick run stopped after 9 minutes

With the **same** 5h `spentLimit`, the solver would normally be allowed to run up to 5 hours. That it stopped after ~9 minutes means another termination condition was hit first:

1. **Unimproved termination** – Most likely. If `unimprovedSpentLimit` (or the platform default “diminished returns”) is in effect, the solver stops after a period of **no score improvement**. The quick run may have reached a solution with 22 unassigned and then not improved for that period → stop.
2. **Re-solve / from-input** – The quick run has `parentId: 073f6280` and `system.type: from-input`. So it was started as a re-solve (e.g. “Re-solve with new input” in the UI). Some re-solve flows might use different termination or a shorter default; if so, that would explain the 9 min stop.

So: **same config** in the profile, but **earlier termination** in practice (unimproved or re-solve default), not because the problem is “easier”.

---

## Inputs

- **3h input:** `export-field-service-routing-v1-073f6280-9da5-44ca-8184-e1e00c97cd33-input.json`  
  Breaks: FLOATING, no `location` (break can be anywhere in the time window).

- **Quick input:** `quick/export-field-service-routing-v1-5f8eae79-809a-4f46-96d2-aed444403c3f-input.json`  
  Breaks: same FLOATING structure in the sampled shifts (no `location` in break object).  
  Quick output shows **BREAK** in the itinerary (e.g. `c46a48bc_break` 10:00–10:30), so breaks are scheduled in both runs.

So in the files we have, the **break definition** (FLOATING, no location) is the same; the main difference is **runtime and termination**, not a different “break location” input.

---

## Takeaways

1. **Same profile (5h limit)** but **quick run ran ~9 min** → termination was driven by **unimproved** (or re-solve) logic, not by `spentLimit`.
2. **22 unassigned** in the quick run vs **2** in the 3h run → giving the solver more time (and/or turning off or relaxing unimproved termination) should reduce unassigned when re-running with the same input.
3. **Average travel per visit** is much higher in the quick run (PT7M59S vs PT2M53S), consistent with a less optimized solution and more unassigned.

**Recommendation:** For the same (or break-location) input, run with the **same profile** and ensure the solver can use the full **spentLimit** (e.g. increase or disable `unimprovedSpentLimit` in the profile, or start as a normal “from-request” solve rather than a short re-solve path).
