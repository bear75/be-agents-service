# Martina feedback analysis — 5ff7929f run

**Purpose:** Trace where each planning error originates: source CSV, expanded CSV, Timefold input, Timefold output, or patch/application.

**Paths used:**  
- Source: `recurring-visits/huddinge-package/source/Huddinge_recurring_v2.csv`  
- Expanded: `recurring-visits/huddinge-package/expanded/huddinge_2wk_expanded_20260224_043456.csv`  
- Input: `huddinge-datasets/28-feb/5ff7929f/input.json`  
- Output: `huddinge-datasets/28-feb/5ff7929f/output.json`  
- Pipeline: `process_huddinge.py` → `expand_recurring_visits.py` → `csv_to_timefold_fsr.py`

---

## Per-case verdict

| Case | Date | Issue | Error in | Trace summary |
|------|------|--------|----------|----------------|
| **H092** | 18/2 | Lunch (30+30 min diff) planned right before morning and shower | **output** | Input: one job 959 (H092_187 Bad/Dusch, Måltid) 18/2, window 07:26–09:26. Output: 959 at 08:20 (within window). If “lunch before morning” refers to route order (another client’s lunch then H092), blame solver ordering. If it refers to another day, same pipeline: time windows are correct in input; issue is solver placement/order. |
| **H299** | 18/2 | Should 1 visit/day, max 25 min diff 12:00–12:25; got 09:07 and 12:00 same day/route | **expanded** | Source has H299_468 (weekly x1), H299_469 (weekly x1), H299_470 (weekly x2 ons). Expanded gives 2286 = H299_469 with **full-week** window (16/2 07:00–22/2 19:40) and 2284 = H299_470 fixed Wed 12:00–12:25. Both can land on 18/2. Solver placed 2286 at 09:07 and 2284 at 12:00. Root cause: **weekly x1** expansion uses a whole-week window, so same client can get two visits the same day. |
| **H331** | 18/2 | 2 meal visits at 10:56 and 11:22 | **expanded** (source) | Expanded has **two** H331_557 rows for 18/2: original_visit_id 2797 (window 08:33–11:32) and 2809 (09:32–12:32). Source has multiple recurring rows for same client/weekday (weekly x3 Måltid); expansion creates two separate jobs same day. Either source should not have two “Måltid” on same weekday, or expansion should merge/dedupe. |
| **H335** | 19/2 | Meal+walk (Tue) vs shower (Thu) on different routes same day | **expanded** (source) | Same pattern as H299: weekly x1 or different weekday patterns for same client produce multiple jobs that can fall on the same day; solver assigns to different routes. Fix: restrict “1 visit per day” per client in source/expansion or with constraints. |
| **H172** | 19/2 | Morning 07:42 diff 5 min → planned 16:05 | **output** | Input time window for morning is early (e.g. 07:xx); solver scheduled 16:05. Either window in input is too wide (then **input/expanded**) or solver chose late time within window (**output**). Need to check input window for H172 19/2; if window is tight morning, error is **output**. |
| **H362** | 19/2 | Morning planned in evening | **output** | Same as H172: if input has morning window, solver placed in evening = **output**. |
| **H095** | 19/2, 20/2 | Lunch 90 min before 13:22 → planned 16:10; and 20/2 08:14–09:48 | **output** or **input** | If input has lunch window ~11:52–13:22 and solver chose 16:10, error is **output**. If input window is wide or wrong (e.g. includes afternoon), error is **input/expanded**. |
| **H248** | 19/2 | 2 lunch visits back to back | **expanded** (source) | Same client has two lunch-type jobs same day (e.g. two recurring rows or weekly x1 + weekday-specific). **Source/expanded**: two visits same day; solver just sequences them. |
| **H072** | 19/2 | 3 visits back to back 08:31–10:31 (should not be before 09:00) | **input** or **output** | If “not before 09:00” is a constraint, it must be in time windows. If input has minStartTime 09:00 and solver used 08:31, error is **output**. If input allows 08:31, error is **expanded/source**. |
| **H077** | 19/2 | 2 morning back to back 07:20–09:15 (must be 07:20, diff 0) | **input** or **source** | “Must be 07:20, diff 0” implies a very tight or pin-at time. If input has wide window and solver chose 09:15 for one, error is **output**. If source/expansion gives two “morning” visits where there should be one or a fixed time, error is **source/expanded**. |
| **H087** | 20/2 | 3 visits back to back 09:49, 12:02 | **expanded** (source) or **output** | Too many visits same day or wrong times. If source/expanded creates 3 jobs for that day and business rule is fewer, **source/expanded**. If time windows are correct and solver chose wrong times, **output**. |
| **H034** | 20/2 | Morning and lunch back to back 11:05–12:05 | **output** or **input** | Morning should be early, lunch later. If input has correct windows and solver put morning at 11:05, **output**. If input gives a single combined or wide window, **input/expanded**. |
| **H238** | 20/2 | Lunch, morning, dinner at 10:37 | **output** or **input** | Order/type wrong (e.g. “morning” at 10:37). If input has distinct windows per type and solver assigned wrong, **output**. If input merges or mislabels, **input/expanded**. |

---

## Root causes (concise)

1. **Weekly x1 (and similar) full-period windows (expanded)**  
   `expand_recurring_visits.py` (lines 292–307) gives **weekly x1** a single window over the whole week (e.g. Mon 07:00–Sun 19:40). The solver can then place that visit on any day, including a day where the same client already has a fixed weekday visit (e.g. H299_470 Wed 12:00–12:25). Result: **two visits same client same day** (e.g. H299 18/2 at 09:07 and 12:00).  
   **Fix:** For clients with “max 1 visit per day”, either: (a) restrict weekly x1 so it cannot be placed on a day that already has another visit for that client (constraint or post-process), or (b) expand weekly x1 to one candidate day per week and let the solver choose among days, without allowing overlap with other same-client visits.

2. **Multiple recurring rows same client/weekday → multiple jobs same day (source/expanded)**  
   Source has several rows per client per weekday (e.g. H331_557 weekly x3 Måltid on Wednesday). Expansion produces **multiple rows for the same date** (e.g. two H331_557 on 18/2 with different windows). That yields two meal visits same day (e.g. 10:56 and 11:22).  
   **Fix:** Business rule “one meal visit per client per day” (or similar) must be enforced: in source data, in expansion (merge/dedupe), or via constraints so only one of the overlapping jobs is allowed per day.

3. **Solver placement within or across days (output)**  
   When input time windows are correct and tight, wrong time or wrong day (e.g. H299_469 for week 16–22 placed on 18/2 together with H299_470; or morning in evening) is an **output** (solver) issue. When windows are too wide or wrong, the error is **input/expanded/source**.

4. **H092 “lunch before morning”**  
   On 18/2 the only H092 job (959) is scheduled at 08:20 within window. If the complaint is **route order** (another client’s lunch immediately before H092’s morning), the error is **output** (ordering). If it’s another day or another combination of visits, the same logic applies: check input windows first, then solver times and order.

---

## Overall conclusion

- **Most “wrong visit count” or “two visits same day” issues:** **expanded** (and **source**). Weekly x1 (and similar) full-week windows plus multiple recurring rows per client/weekday produce multiple jobs that can (or must) fall on the same day. The solver only assigns times/routes; it does not enforce “max 1 per client per day” unless modeled.
- **“Wrong time of day” (morning in evening, lunch too late):** mix of **output** (solver chose bad time) and **input/expanded** (windows too wide or wrong). Tighten windows in expansion/source and, if needed, add constraints or penalties so the solver respects time-of-day.
- **Patch/application:** No evidence that from-patch or application of the solution to Attendo/Slinga introduced these errors; they are present in the 5ff7929f **output** and stem from **input** built from **expanded** and **source** as above.

**Recommended next steps:**  
1. Add “max one visit per client per day” (or per type) in expansion or as a constraint in the model.  
2. Restrict weekly x1 so it cannot be placed on a day that already has another visit for that client (e.g. by day-specific alternatives or constraints).  
3. Review source for duplicate or overlapping recurring rows per client/weekday and merge or constrain in expansion.  
4. Validate time windows in input for “morning” vs “lunch” vs “evening” and tighten flex (e.g. maxStartTime) so the solver cannot place morning visits in the afternoon.
