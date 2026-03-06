# Input dataset comparison (visits only)

Comparison of three input JSONs to verify whether the dataset is "the same except visit id/name".

## Summary

| File | Visits | visitGroups | Vehicles | Shifts | Visit id format | Visit name format |
|------|--------|-------------|----------|--------|-----------------|-------------------|
| **input_4mars_20260304_182033.json** | 425 | 120 | 26 | 224 | `v_1` | `H015 Morgon 2026-03-02` |
| **input_4mars_20260305_193758.json** | 1006 | 240 | 40 | 896 | `H015_r0_1` | `H015 Morgon Dag Tillsyn` |
| **e2e_pipeline_0cf9ea85/input.json** | 1006 | 232 | 48 | 1124 | `H015_1` | `H015 Morgon 2026-03-02` |

- **0403** is a different size (2w or older expansion); not comparable.
- **0503** = current script output (new id/name, 4w, 40 vehicles, 896 shifts).
- **e2e** = same visit count (1006), old id/name, more vehicles/shifts (48, 1124).

## Same semantics: one per date (mon–fri, 2 weekend, etc.)

For "one visit per allowed day" (e.g. mon–fri → 5 per week), the two encodings are **the same**:

- **0503 (new):** One time window per visit (one specific date per occurrence). Example: H025_r8_1 → 2026-03-02, H025_r8_2 → 2026-03-03, … (5 visits, 5 dates).
- **e2e (old):** Multiple time windows per visit (one window per allowed day in the period). Example: H025_2 has 5 windows (one per weekday) → solver places that one visit on one of the 5 days.

Both represent "visits mon–fri, one per date"; the difference is only 1 window per visit vs N windows per visit. What matters for behaviour is how **other occurrence patterns** are handled: 2, 3, 4 per week, varannan vecka, var 4:e vecka, and their **minDelay** (spread over days).

## Real difference: how 2, 3, 4 (and spread) are handled — minDelay

**0503** (current script, with "infeasible delay" capping):

- minDelay distribution: **PT3H30M** (156), **PT2H** (28), PT3H58M (12), PT1H30M (12), PT1H15M (12), PT5H49M (8), PT1H5M (4).
- Long spread delays (24h, 36h, 48h) are **capped or shortened** when they don't fit between time windows (script warnings: "delay PT48H infeasible, capped to PT35M" etc.). So many "Antal tim mellan besöken" constraints become same-day or short gaps.

**e2e** (older input):

- minDelay distribution: **PT3H30M** (160), **PT2H** (28), **PT36H** (24), **PT24H** (20), **PT48H** (4).
- **Full spread delays** (PT24H, PT36H, PT48H) are kept so that 2, 3, 4 occurrences per week (e.g. dusch) land on **different days**.

So for "other occurrences" (2, 3, 4 per week, varannan, var 4:e vecka):

- **e2e** enforces "min X hours between these visits" with 24h/36h/48h → strong spread over days.
- **0503** has many of those replaced by shorter/capped delays → weaker or same-day-only spread.

That is the **important** difference between the two inputs: not the 1 vs 5 time windows (same semantics for "one per date"), but **whether spread between 2, 3, 4 occurrences is 24/36/48h or capped**.

## Visit groups: same CSV and window → same count

For the **same CSV** and **same planning window**, visit group count is the same. Example: `input_4mars_20260304_182733.json` and `input_4mars_20260304_185455.json` both have **425 visits** and **120 visit groups** (2w window). The 240 vs 232 difference was between 4w inputs (0503 vs e2e) with different expansion/encoding, not between two runs with identical strategy and window.

## Other differences (0503 vs e2e)

- **Visit id and name:** 0503 = `H015_r0_1`, `H015 Morgon Dag Tillsyn`; e2e = `H015_1`, `H015 Morgon 2026-03-02`.
- **Visit groups:** 0503 = 240, e2e = 232 (8 fewer in e2e).
- **Capacity:** e2e has more (48 vehicles, 1124 shifts) than 0503 (40, 896). So many unassigned in e2e is not due to less capacity.
- **Dependencies:** Both use per-visit `visitDependencies`; no broken references in e2e.

## Conclusion

- **1 window vs 5 windows** for "one per weekday" = **same semantics** (both "one per date"); encoding only.
- The **meaningful** difference is **minDelay for 2, 3, 4 occurrences**: e2e keeps 24h/36h/48h spread; 0503 caps many of these to shorter/same-day. So the dataset is **not** "0503 with only id/name updated" — spread handling differs.
- If run **9bd4e531-1fd9-40b7-88a6-25f4a54d3ff0** used e2e, you are solving with **stronger** spread constraints (24/36/48h). Unassigned could be due to that, or to config; comparing with 0503 (capped delays) may behave differently.

**Recommendation:** To validate the new id/name and compare unassigned on a like-for-like basis, run solve with **input_4mars_20260305_193758.json** and the same config; then compare metrics and unassigned with the e2e run.
