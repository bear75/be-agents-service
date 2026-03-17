# Pool8 (job 4): where time is spent & how to fix 162 unassigned

Efficiency and continuity are OK (73.82% field, 3.69 continuity avg). The remaining issue is **162 unassigned visits** (4.2%).

---

## Where time is spent (41 vehicles, 474 shifts in solution)

| Category   | Hours    | % of total shift | Note                    |
|-----------|----------|-------------------|-------------------------|
| **Visit** | 1612 h 48 min | **63.5%** | Care delivery / revenue |
| **Travel**| 571 h 52 min | 22.5%  | Minimize to free capacity |
| **Wait**  | 168 h 33 min | 6.6%   | Between visits           |
| **Break** | 188 h 0 min  | 7.4%   | Non-assignable           |
| **Empty shifts** | 78 shifts, 0 visit | — | **Unused capacity** |

So: most time is already visit (63.5%); travel is the next big chunk. The main “slack” is **78 shifts with no visits at all** — time that could in principle be used for the unassigned.

---

## Why are 162 still unassigned?

- **78 empty shifts** overlap in time with **some** of the unassigned visit windows. So there is capacity in the roster; the solver did not assign those visits to those shifts.
- In pool8, each client can only be served by **at most 8 vehicles**. So the empty-shift vehicles (e.g. Dag_10_Abbe, Dag_13_Stuvsta_1, Helg_*) are likely **not in the pool** for the clients whose unassigned visits overlap those shifts. If they were, the solver would tend to use them.
- The overlaps in `empty_shifts.txt` involve mainly **4 unassigned visit slots** (windows): **H039_r80_1**, **H037_r65_1**, **H034_r44_3**, **H034_r44_6** (clients H039, H037, H034). The other unassigned visits don’t have an overlapping empty shift in the list — they may be constrained by time windows, dependencies, or pool/skills elsewhere.

---

## Easiest levers to fix unassigned (pool8)

1. **Include empty-shift vehicles in client pools where it’s feasible**  
   For clients with unassigned visits (especially H034, H037, H039), allow the vehicles that have empty shifts overlapping those visit windows to be in the pool for that client (if roster/skills allow). That uses the 78 empty shifts where they already match time and (after pool change) eligibility.

2. **Slightly relax pool size for worst-affected clients**  
   For clients that still have many unassigned after (1), consider pool 9 or 10 only for them so the solver can use a few more vehicles without blowing continuity for the rest.

3. **Reduce travel (and wait) to free capacity**  
   Travel is 22.5% of shift time. Any reduction (clustering, preferred depots, or reordering) frees time that can be used for more visits and can help assign a few more of the 162.

4. **Inspect the 162 in the input**  
   Check in the FSR input which visits are unassigned: time windows, dependencies (e.g. same-day or spacing), and required skills. Some may be fixable by widening time windows or adjusting dependencies; others will need more capacity (1–2).

---

## Summary

- **Where time is spent:** Visit 63.5%, travel 22.5%, wait 6.6%, break 7.4%; 78 shifts are empty (0 visit).
- **Easiest fix:** Use the empty shifts by letting those vehicles into the client pools for H034, H037, H039 (and any other clients with unassigned visits that overlap empty shifts). Then, if needed, small pool increase for remaining problem clients and/or travel reduction.
