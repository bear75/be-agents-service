# Supply vs demand analysis

**Output:** `output.json`
**Input:** `input.json`

## 1. Summary

| Metric | Value |
|--------|-------|
| Total visits (input) | 3622 |
| Assigned visits | 3554 |
| **Unassigned visits** | **68** |
| Total shifts (input) | 340 |
| Vehicles | 38 |
| Empty shifts (0 visits) | 40 |

---

## 2. Where supply is high vs low (by day)

Supply = shifts on that day. Demand = assigned visits on that day. Empty = shifts with 0 visits.

| Date | Shifts | Empty | Assigned visits | Visits/shift (avg) |
|------|--------|-------|-----------------|---------------------|
| 2026-02-16 | 27 | 2 | 293 | 10.9 |
| 2026-02-17 | 27 | 5 | 252 | 9.3 |
| 2026-02-18 | 27 | 4 | 262 | 9.7 |
| 2026-02-19 | 27 | 5 | 240 | 8.9 |
| 2026-02-20 | 26 | 1 | 295 | 11.3 |
| 2026-02-21 | 18 | 1 | 217 | 12.1 |
| 2026-02-22 | 18 | 2 | 220 | 12.2 |
| 2026-02-23 | 27 | 4 | 242 | 9.0 |
| 2026-02-24 | 27 | 3 | 276 | 10.2 |
| 2026-02-25 | 27 | 4 | 264 | 9.8 |
| 2026-02-26 | 27 | 4 | 265 | 9.8 |
| 2026-02-27 | 26 | 2 | 281 | 10.8 |
| 2026-02-28 | 18 | 1 | 228 | 12.7 |
| 2026-03-01 | 18 | 2 | 219 | 12.2 |

---

## 3. Empty shifts (remove or move)

**40 shifts** have no visits. These can be removed or moved to days with high demand.

### 2026-02-16 (2 empty)

- `Driver-23` shift `46102ee9`
- `Driver-37` shift `9fee6f78`

### 2026-02-17 (5 empty)

- `Driver-07` shift `4bad9bd2`
- `Driver-12` shift `bbb98d8d`
- `Driver-23` shift `f4cf1970`
- `Driver-32` shift `5bbc6897`
- `Driver-37` shift `873b6806`

### 2026-02-18 (4 empty)

- `Driver-18` shift `a9697952`
- `Driver-20` shift `3cd900ad`
- `Driver-23` shift `61fd64f7`
- `Driver-32` shift `afc41d16`

### 2026-02-19 (5 empty)

- `Driver-06` shift `f4ef1661`
- `Driver-07` shift `1f7c8211`
- `Driver-15` shift `5c3c85ae`
- `Driver-23` shift `27d7d7d4`
- `Driver-37` shift `572b9db2`

### 2026-02-20 (1 empty)

- `Driver-32` shift `2149d41b`

### 2026-02-21 (1 empty)

- `Driver-08` shift `ee20df6e`

### 2026-02-22 (2 empty)

- `Driver-13` shift `2f38095e`
- `Driver-19` shift `90cbfc8d`

### 2026-02-23 (4 empty)

- `Driver-12` shift `b34c12b8`
- `Driver-18` shift `7985b006`
- `Driver-20` shift `9390bddb`
- `Driver-23` shift `5782c128`

### 2026-02-24 (3 empty)

- `Driver-12` shift `b1d2a45f`
- `Driver-23` shift `6f0ae988`
- `Driver-37` shift `8ada4afd`

### 2026-02-25 (4 empty)

- `Driver-07` shift `232116c8`
- `Driver-15` shift `55a72880`
- `Driver-32` shift `11e330bc`
- `Driver-37` shift `6d2d3b0d`

### 2026-02-26 (4 empty)

- `Driver-18` shift `ec3100df`
- `Driver-20` shift `10c8ac5a`
- `Driver-32` shift `20fba977`
- `Driver-37` shift `51220315`

### 2026-02-27 (2 empty)

- `Driver-23` shift `faa8e2ee`
- `Driver-32` shift `90650df5`

### 2026-02-28 (1 empty)

- `Driver-19` shift `73398ce6`

### 2026-03-01 (2 empty)

- `Driver-08` shift `b9a008d0`
- `Driver-19` shift `de645137`

---

## 4. Highest-load shifts (supply tight)

Shifts with the most visits — may need relief or more capacity on those days.

| Vehicle | Shift | Date | Visits |
|---------|-------|------|--------|
| Driver-35 | d952ac7c | 2026-02-27 | 21 |
| Driver-03 | 5dc17335 | 2026-03-01 | 18 |
| Driver-14 | 0581d418 | 2026-02-21 | 18 |
| Driver-14 | b07d007c | 2026-03-01 | 18 |
| Driver-15 | 96fda4da | 2026-02-17 | 18 |
| Driver-20 | ea85938f | 2026-02-24 | 18 |
| Driver-36 | f4008e26 | 2026-03-01 | 18 |
| Driver-05 | 28079f04 | 2026-02-25 | 17 |
| Driver-06 | 149a833c | 2026-02-16 | 17 |
| Driver-15 | 47e630c4 | 2026-02-20 | 17 |
| Driver-15 | d70b14af | 2026-02-27 | 17 |
| Driver-35 | 65daf104 | 2026-02-18 | 17 |
| Driver-36 | b177f974 | 2026-02-22 | 17 |
| Driver-36 | 4e5c2c5e | 2026-02-28 | 17 |
| Driver-03 | 0e180d7f | 2026-02-18 | 16 |
| Driver-03 | 92c47dd9 | 2026-02-20 | 16 |
| Driver-05 | d853ed1e | 2026-02-20 | 16 |
| Driver-15 | b4de1741 | 2026-02-24 | 16 |
| Driver-16 | c6c7ee7b | 2026-02-18 | 16 |
| Driver-16 | 47b96b27 | 2026-02-19 | 16 |

---

## 5. Unassigned visit IDs

**68 visits** could not be assigned. To assign all:

1. **Add shifts** on days where demand exceeds supply (days with many unassigned time windows).
2. **Move shifts** from days with many empty shifts to days with high demand.
3. **Widen time windows** (if care rules allow) so more visits can fit on existing shifts.
4. **Run solver longer** so it can find feasible assignments for tight days.

Unassigned IDs:

```
357, 371, 145, 159, 359, 373, 173, 187, 147, 161, 361, 375, 149, 163, 363, 377, 151, 165, 365, 379, 153, 167, 367, 381, 2401, 2387, 155, 169, 369, 383, 2403, 2389, 144, 158, 358, 372, 172, 186, 360, 374, 2394, 2380, 148, 162, 362, 376, 2396, 2382, 150, 164, 364, 378, 152, 166, 366, 380, 180, 194, 2400, 2386, 154, 168, 368, 382, 156, 170, 370, 384
```

---

## 6. Recommendations

| Goal | Action |
|------|--------|
| Assign all visits | Add shifts on high-demand days, or move empty shifts from low-demand days; re-run solver. |
| Remove waste | Delete or deactivate the empty shifts listed in §3 (or move them to other days). |
| Balance load | Consider moving some shifts from days with many empty shifts to days with high visits/shift. |
