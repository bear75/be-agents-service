# Supply vs demand analysis

**Output:** `from_patch_output.json`
**Input:** `input.json`

## 1. Summary

| Metric | Value |
|--------|-------|
| Total visits (input) | 3622 |
| Assigned visits | 3586 |
| **Unassigned visits** | **36** |
| Total shifts (input) | 300 |
| Vehicles | 38 |
| Empty shifts (0 visits) | 0 |

---

## 2. Where supply is high vs low (by day)

Supply = shifts on that day. Demand = assigned visits on that day. Empty = shifts with 0 visits.

| Date | Shifts | Empty | Assigned visits | Visits/shift (avg) |
|------|--------|-------|-----------------|---------------------|
| 2026-02-16 | 300 | 0 | 3586 | 12.0 |

---

## 3. Empty shifts (remove or move)

**0 shifts** have no visits. These can be removed or moved to days with high demand.

---

## 4. Highest-load shifts (supply tight)

Shifts with the most visits — may need relief or more capacity on those days.

| Vehicle | Shift | Date | Visits |
|---------|-------|------|--------|
| Driver-35 | d952ac7c | 2026-02-16 | 21 |
| Driver-03 | 5dc17335 | 2026-02-16 | 18 |
| Driver-14 | 0581d418 | 2026-02-16 | 18 |
| Driver-14 | b07d007c | 2026-02-16 | 18 |
| Driver-15 | 96fda4da | 2026-02-16 | 18 |
| Driver-20 | ea85938f | 2026-02-16 | 18 |
| Driver-36 | f4008e26 | 2026-02-16 | 18 |
| Driver-05 | 28079f04 | 2026-02-16 | 17 |
| Driver-06 | 149a833c | 2026-02-16 | 17 |
| Driver-06 | 151dfe50 | 2026-02-16 | 17 |
| Driver-15 | 47e630c4 | 2026-02-16 | 17 |
| Driver-15 | d70b14af | 2026-02-16 | 17 |
| Driver-35 | 65daf104 | 2026-02-16 | 17 |
| Driver-36 | b177f974 | 2026-02-16 | 17 |
| Driver-36 | 4e5c2c5e | 2026-02-16 | 17 |
| Driver-03 | 0e180d7f | 2026-02-16 | 16 |
| Driver-03 | 92c47dd9 | 2026-02-16 | 16 |
| Driver-05 | d853ed1e | 2026-02-16 | 16 |
| Driver-06 | 8dec6286 | 2026-02-16 | 16 |
| Driver-15 | b4de1741 | 2026-02-16 | 16 |

---

## 5. Unassigned visit IDs

**36 visits** could not be assigned. To assign all:

1. **Add shifts** on days where demand exceeds supply (days with many unassigned time windows).
2. **Move shifts** from days with many empty shifts to days with high demand.
3. **Widen time windows** (if care rules allow) so more visits can fit on existing shifts.
4. **Run solver longer** so it can find feasible assignments for tight days.

Unassigned IDs:

```
147, 161, 149, 163, 151, 165, 365, 379, 153, 167, 367, 381, 2401, 2387, 155, 169, 369, 383, 2403, 2389, 150, 164, 152, 166, 366, 380, 180, 194, 154, 168, 368, 382, 156, 170, 370, 384
```

---

## 6. Recommendations

| Goal | Action |
|------|--------|
| Assign all visits | Add shifts on high-demand days, or move empty shifts from low-demand days; re-run solver. |
| Remove waste | Delete or deactivate the empty shifts listed in §3 (or move them to other days). |
| Balance load | Consider moving some shifts from days with many empty shifts to days with high visits/shift. |
