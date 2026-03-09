# Solve comparison: 5d66cc1c vs cece06c0

## Datasets (canonical: 9march inputs)

| Plan ID | Input (in 9march) | Vehicles | Shifts | Visits | Visits/shift |
|--------|--------------------|----------|--------|--------|--------------|
| **5d66cc1c** | `less-shifts/export-field-service-routing-v1-5d66cc1c-...-input.json` | 46 | 544 | 3,457 | **6.35** |
| **cece06c0** | `xtra-shifts/export-field-service-routing-v1-cece06c0-...-input.json` | 46 | 448 | 3,457 | **7.72** |

Same planning window (2026-03-02 → 2026-03-15). Both use the **base fleet (46 vehicles)**. The Timefold UI for cece06c0 may show “3,697” visits — that’s a different count or payload; our files have **3,457**.

**Important:** The file `export-field-service-routing-v1-9c6c78a8-...-input.json` (272 vehicles, **3,612 shifts**) is **not** the input for cece06c0. It has ~0.96 visits per shift and is unrealistic for planning; the actual cece06c0 run uses 46 vehicles and 448 shifts. See `9march/README.md`.

---

## Fetched artifacts

- **5d66cc1c**
  - Output: `solve_5d66cc1c/output.json`
  - Input (from API): `solve_5d66cc1c/input_from_api.json`
- **cece06c0**
  - Output: `9march/xtra-shifts/export-field-service-routing-cece06c0-...-output.json`
  - Input: `9march/xtra-shifts/export-field-service-routing-v1-cece06c0-...-input.json` (46 vehicles, 448 shifts).

---

## 5d66cc1c (46 vehicles – fewer shifts)

**Status (at fetch time):** `SOLVING_ACTIVE`  
**Score:** `0hard/-13360000medium/-2535780soft`

### Unassigned visits

| Metric | Value |
|--------|--------|
| **Unassigned count** | **1,336** |
| Assigned (implied) | 3,457 − 1,336 = **2,121** |

**Unassigned by client (top 15):**

| Client | Unassigned |
|--------|------------|
| H026 | 56 |
| H035 | 56 |
| H322 | 28 |
| H039 | 28 |
| H097 | 28 |
| H363 | 28 |
| H086 | 28 |
| H041 | 28 |
| H361 | 28 |
| H087 | 28 |
| H216 | 28 |
| HN13 | 28 |
| H145 | 28 |
| H172 | 28 |
| H238 | 28 |

**First 25 unassigned visit IDs:**  
`H322_r716_1`, `H039_r77_1`, `H097_r262_1`, `H363_r944_1`, `H026_r23_1`, `H026_r24_1`, `H086_r165_1`, `H041_r87_1`, `H361_r917_1`, `H087_r187_1`, `H087_r187_2`, `H216_r424_1`, `HN13_r967_1`, `H114_r273_1`, `H055_r113_1`, `H145_r298_1`, `H145_r298_2`, `H172_r356_1`, `H238_r459_1`, `H324_r750_1`, `H248_r516_1`, `H332_r799_1`, `H337_r821_1`, `H029_r34_1`, `H331_r779_1`.

### Aggregated metrics (all shifts)

| Metric | Value |
|--------|--------|
| Shifts with ≥1 visit | 207 |
| Total service (min) | 66,797 |
| Total break (min) | 5,760 |
| Total waiting (min) | 1,793 |
| Total travel (min) | 9,668.8 |
| Total travel distance (m) | 4,911,767 |

---

## cece06c0 (46 vehicles, 448 shifts – completed run)

**Status:** SOLVING_COMPLETED  
**Score:** `0hard/-20000medium/-6007242soft`  
**Output:** `9march/xtra-shifts/export-field-service-routing-cece06c0-...-output.json`

### Unassigned visits: 2 (not 4)

| Unassigned ID   | Client |
|-----------------|--------|
| H035_r53_5      | H035   |
| H035_r54_5      | H035   |

With 46 vehicles and 448 shifts there is plenty of capacity. These 2 are unassigned because they are **infeasible**: no shift can legally serve them (time windows, visit dependencies, or other hard constraints). Adding more shifts would not fix them.

### Why 3,457 in our files vs 3,697 in the UI?

Our input JSON files have **3,457** visits. The Timefold Overview for cece06c0 may show **3,697**. That can be (1) a different submitted payload, or (2) the UI counting visits differently (e.g. including optional/dummy). For local analysis we use 3,457.

### Why 3,612 shifts is wrong for this run

The file `export-field-service-routing-v1-9c6c78a8-...-input.json` has **272 vehicles and 3,612 shifts** (~0.96 visits per shift). That dataset is **not** what cece06c0 was solved with and is unrealistic (less than 1 visit per shift). The actual cece06c0 run uses **46 vehicles, 448 shifts** (see 9march/xtra-shifts input). See `9march/README.md`.
