# Analysis: 26 unassigned visits (0cf4a744)

## Conclusion: **All 26 are impossible** — contradictory constraints in the input

The unassigned visits are **infeasible by construction**: they have a **minDelay of 18h** between morning and lunch on the **same day**, so no assignment can satisfy both the dependency and the time window.

---

## Who is unassigned?

| Client | Visit types (row) | Count | Pattern |
|--------|-------------------|-------|---------|
| **H034** | r38 (Morgon), r39 (Lunch Bad/Dusch), r41 (Lunch Måltid) | 18 | Chain: r38 → r39 (PT18H) → r41 (PT0S) |
| **H038** | r65 (Morgon), r71 (Lunch Promenad) | 8 | Chain: r65 → r71 (PT18H) |

---

## Why they are impossible

### H034 (example: r38_1 → r39_1 → r41_1)

- **r38_1** (Morgon): time window **2026-03-02** 08:12–09:57.
- **r39_1** (Lunch Bad/Dusch): time window **2026-03-02** 11:25–12:55, **visitDependencies**: precedingVisit = r38_1, **minDelay = PT18H**.
- **r41_1** (Lunch Måltid): same day 11:40–13:40, depends on r39_1 (PT0S).

So r39_1 must start **≥ 18h after r38_1 ends** → earliest 2026-03-02 09:57 + 18h = **2026-03-03 03:57**.  
But r39_1’s time window is **only on 2026-03-02** 11:25–12:55. So there is **no feasible start time** for r39_1: the dependency forces “next day”, the window forces “same day”. Same contradiction for every (r38, r39, r41) pair per day.

### H038 (example: r65_2 → r71_1)

- **r65_2** (Morgon): **2026-03-03** 08:05–09:30.
- **r71_1** (Lunch Promenad): **2026-03-03** 10:34–14:44, **precedingVisit = r65_2**, **minDelay = PT18H**.

r71_1 must start ≥ 18h after r65_2 ends → earliest **2026-03-04** 03:30.  
r71_1’s window is only on **2026-03-03**. Again **impossible**.

---

## Root cause in the pipeline

Same-day chains (Morgon → Lunch) have been given **minDelay = PT18H**. The 18h value is intended for **spread** (flexible_day, different days); it must **not** be applied to **same-day** chains (Morgon → Lunch on the same date).

For H034 the docs (CSV_TO_INPUT_VERIFICATION.md) already describe capping: “H034 capped from 3h30 to ~1h20” when the gap doesn’t fit. So either:

1. This input was built from a run where the **cap** was not applied for these rows (e.g. they were given 18h from “Antal tim mellan” or default), or  
2. Same-day dependency logic is using the **spread default (18h)** instead of a same-day gap (e.g. from CSV “Antal tim mellan” or no gap).

**Required fix:** In `attendo_4mars_to_fsr.py`, ensure **same-day** dependencies (pinned Morgon → Lunch/Kväll on the same client/date) never get the 18h default. Use either the CSV “Antal tim mellan besöken” value (capped to feasible) or no gap; 18h must only be used for **spread** (flexible_day between occurrences).

---

## Recommendation

1. **Short term:** Treat these 26 as **known bad input** for this run; the solver is correct to leave them unassigned.
2. **Fix the script:** Same-day chain dependencies must not use PT18H. Apply the existing “gap that doesn’t fit” cap (or remove dependency) when the requested delay is larger than what fits between the two visits’ windows on the same day.
3. **Re-run:** After the fix, regenerate input and solve again; H034 and H038 same-day chains should then be assignable (or removed if still infeasible).
