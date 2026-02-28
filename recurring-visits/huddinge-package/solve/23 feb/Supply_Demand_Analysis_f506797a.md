# Supply vs demand analysis

**Output:** `export-field-service-routing-f506797a-9f51-4022-ad90-1965ba9db788-output.json`
**Input:** `export-field-service-routing-v1-f506797a-9f51-4022-ad90-1965ba9db788-input.json`

## 1. Summary

| Metric | Value |
|--------|-------|
| Total visits (input) | 3622 |
| Assigned visits | 3559 |
| **Unassigned visits** | **63** |
| Total shifts (input) | 340 |
| Vehicles | 38 |
| Empty shifts (0 visits) | 23 |

---

## 2. Where supply is high vs low (by day)

Supply = shifts on that day. Demand = assigned visits on that day. Empty = shifts with 0 visits.

| Date | Shifts | Empty | Assigned visits | Visits/shift (avg) |
|------|--------|-------|-----------------|---------------------|
| 2026-02-16 | 27 | 2 | 263 | 9.7 |
| 2026-02-17 | 27 | 3 | 266 | 9.9 |
| 2026-02-18 | 27 | 3 | 262 | 9.7 |
| 2026-02-19 | 27 | 2 | 247 | 9.1 |
| 2026-02-20 | 26 | 3 | 259 | 10.0 |
| 2026-02-21 | 18 | 0 | 239 | 13.3 |
| 2026-02-22 | 18 | 0 | 241 | 13.4 |
| 2026-02-23 | 27 | 3 | 257 | 9.5 |
| 2026-02-24 | 27 | 1 | 270 | 10.0 |
| 2026-02-25 | 27 | 3 | 254 | 9.4 |
| 2026-02-26 | 27 | 2 | 251 | 9.3 |
| 2026-02-27 | 26 | 1 | 268 | 10.3 |
| 2026-02-28 | 18 | 0 | 242 | 13.4 |
| 2026-03-01 | 18 | 0 | 240 | 13.3 |

**Interpretation — where supply is low vs high**

- **Supply high (slack):** Weekdays (Mon–Fri) have **26–27 shifts** and **2–3 empty shifts** each. Average 9–10 visits/shift. These days have spare capacity; empty shifts are candidates to remove or move.
- **Supply tight:** **Weekends** (Sat–Sun: 21, 22, 28 Feb; 1 Mar) have **18 shifts**, **0 empty**, and **13.3–13.4 visits/shift**. No slack; adding visits would require more shifts or longer solve.
- **63 unassigned** visits could not be placed. They may cluster on days that are already full (e.g. weekends) or have time windows that don’t fit remaining capacity. Cross-reference unassigned IDs with input visit time windows to see which days need extra supply.

---

## 3. Empty shifts (remove or move)

**23 shifts** have no visits. These can be removed or moved to days with high demand.

### 2026-02-16 (2 empty)

- `Dag_02_Central_2` shift `b8496e5b`
- `Dag_04_Visättra_2` shift `7703710d`

### 2026-02-17 (3 empty)

- `Dag_04_Visättra_2` shift `10ada161`
- `Dag_14_Stuvsta_2` shift `8b9e6dcd`
- `Dag_17_Vårby_2_Janet` shift `d40e0056`

### 2026-02-18 (3 empty)

- `Dag_13_Stuvsta_1` shift `ba4a2385`
- `Dag_14_Stuvsta_2` shift `22a9abcd`
- `Dag_15_Stuvsta_3` shift `a4047bed`

### 2026-02-19 (2 empty)

- `Dag_15_Stuvsta_3` shift `bb2de087`
- `Dag_18_Masmo` shift `0e3c57b5`

### 2026-02-20 (3 empty)

- `Dag_04_Visättra_2` shift `8fee8886`
- `Dag_05_Flemingsberg_1` shift `d8c8a550`
- `Dag_12_Segeltorp_1` shift `796706a4`

### 2026-02-23 (3 empty)

- `Dag_05_Flemingsberg_1` shift `aaacd8fe`
- `Dag_09_Kvarnbergsplan_2` shift `358f497a`
- `Dag_13_Stuvsta_1` shift `7297568d`

### 2026-02-24 (1 empty)

- `Dag_05_Flemingsberg_1` shift `4eb22b26`

### 2026-02-25 (3 empty)

- `Dag_04_Visättra_2` shift `a791147a`
- `Dag_10_Abbe` shift `6ae43d52`
- `Dag_17_Vårby_2_Janet` shift `3e63f131`

### 2026-02-26 (2 empty)

- `Dag_07_Flemingsberg_3` shift `8f667faa`
- `Dag_12_Segeltorp_1` shift `f8665e4a`

### 2026-02-27 (1 empty)

- `Dag_02_Central_2` shift `0b408114`

---

## 4. Highest-load shifts (supply tight)

Shifts with the most visits — may need relief or more capacity on those days.

| Vehicle | Shift | Date | Visits |
|---------|-------|------|--------|
| Helg_07_Visättra_TJEJ | e9f19d1d | 2026-02-22 | 18 |
| Helg_04_Snättringe | 622af37a | 2026-02-28 | 17 |
| Dag_16_Vårby_1 | b26b94be | 2026-02-25 | 16 |
| Helg_06_Central | 0e4d748f | 2026-02-21 | 16 |
| Kväll_01_Fullersta | cf037b4e | 2026-02-22 | 16 |
| Kväll_01_Fullersta | 853b4896 | 2026-02-26 | 16 |
| Kväll_07_Vårby | d2f83af9 | 2026-02-16 | 16 |
| Dag_04_Visättra | 52759d0d | 2026-02-26 | 15 |
| Dag_05_Flemingsberg_1 | d1960b2a | 2026-02-26 | 15 |
| Dag_09_Kvarnbergsplan_2 | f2d6c0af | 2026-02-26 | 15 |
| Helg_04_Snättringe | e7158b34 | 2026-02-21 | 15 |
| Helg_05_Kvarnen_1 | 32605163 | 2026-03-01 | 15 |
| Helg_06_Central | 7799f43d | 2026-02-22 | 15 |
| Helg_08_Stuvsta_1_Tjej | 3857513f | 2026-02-21 | 15 |
| Helg_08_Stuvsta_1_Tjej | 3c8c863f | 2026-03-01 | 15 |
| Helg_10_Segeltorp | 4c8b0ff3 | 2026-02-28 | 15 |
| Helg_10_Segeltorp | 560b1fad | 2026-03-01 | 15 |
| Helg_11_Masmo | 57ce79a7 | 2026-02-21 | 15 |
| Kväll_01_Fullersta | efd37820 | 2026-02-24 | 15 |
| Kväll_01_Fullersta | cfa22ba3 | 2026-02-27 | 15 |

---

## 5. Unassigned visit IDs

**63 visits** could not be assigned. To assign all:

1. **Add shifts** on days where demand exceeds supply (days with many unassigned time windows).
2. **Move shifts** from days with many empty shifts to days with high demand.
3. **Widen time windows** (if care rules allow) so more visits can fit on existing shifts.
4. **Run solver longer** so it can find feasible assignments for tight days.

Unassigned IDs:

```
143, 157, 357, 371, 145, 159, 359, 373, 361, 375, 363, 377, 151, 165, 2975, 179, 193, 107, 111, 2367, 2363, 2875, 153, 167, 367, 381, 109, 113, 2369, 2365, 2877, 155, 169, 369, 383, 358, 372, 360, 374, 148, 162, 362, 376, 364, 378, 366, 380, 180, 194, 108, 112, 302, 306, 2876, 368, 382, 110, 114, 304, 308, 2878, 370, 384
```

---

## 6. Recommendations

| Goal | Action |
|------|--------|
| Assign all visits | Add shifts on high-demand days, or move empty shifts from low-demand days; re-run solver. |
| Remove waste | Delete or deactivate the empty shifts listed in §3 (or move them to other days). |
| Balance load | Consider moving some shifts from days with many empty shifts to days with high visits/shift. |
