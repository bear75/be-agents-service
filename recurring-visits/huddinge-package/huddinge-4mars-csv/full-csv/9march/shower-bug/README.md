# 9 March solve runs: less-shifts vs xtra-shifts

## Which input is which

| Folder | Plan ID | Input | Vehicles | Shifts | Visits | Visits/shift |
|--------|----------|-------|----------|--------|--------|--------------|
| **less-shifts** | 5d66cc1c | `export-field-service-routing-v1-5d66cc1c-...-input.json` | 46 | 544 | 3,457 | **6.35** |
| **xtra-shifts** | cece06c0 | `export-field-service-routing-v1-cece06c0-...-input.json` | 46 | 448 | 3,457 | **7.72** |

Both runs use the **same base fleet (46 vehicles)**. “xtra-shifts” here means the run that **completed** (cece06c0) with 448 shifts in the input; “less-shifts” is 5d66cc1c with 544 shifts. So the **completed** run (cece06c0) actually has *fewer* shifts in the input (448) than the still-solving run (544).

## Visit count: 3,457 vs 3,697

- **modelInput.visits**: **3,457** (standalone visits only).
- **visitGroups[].visits**: **240** visit objects (only in groups; they do not appear in top-level `visits`).
- **Total in Timefold**: 3,457 + 240 = **3,697**. There is no double counting; group visits are unique and only in groups. See `full-csv/VISIT_COUNT_AND_H035.md`.

## Unassigned: why 2 with “enough” shifts? (H035 dusch, visit group 6)

**cece06c0** (SOLVING_COMPLETED): **2 unassigned** — the H035 **dusch** visit group (Dubbel 6): two overlapping visits (Snättringe 10:30, Central 2 10:35), “Varje vecka, mån tor”, 42 timmar. One logical job, two vehicles.

Attendo: **“H035 dusch måste vara dikt med morgonbesöket”** — shower must follow the morning visit on the same day. Two likely causes: (1) **Time window**: Morgon slot ends 10:30; a 20‑min visit starting 10:30 ends 10:50, so end time is outside “när på dagen”. (2) **Missing same-day dependency**: we need Morgon → Dusch with **minDelay PT0M** so the 10:15 20‑min morgon is followed directly by the 10:30 shower. The **42h** is between the two shower days (mån and tor), not between same-day different insats. Fix: add Morgon→Dusch PT0M and allow dusch window to 10:30 (or extend slot). See `full-csv/VISIT_COUNT_AND_H035.md`.

## The 3,612-shift file (not used for cece06c0)

The file **`export-field-service-routing-v1-9c6c78a8-d4ad-477e-a466-9e71eeb9d208-input.json`** in `full-csv/` has **272 vehicles, 3,612 shifts, 3,457 visits** (~0.96 visits per shift). That is **not** the input for the cece06c0 run in the UI. It is an over-provisioned dataset (base + 226 supplementary vehicles) and is **unrealistic** for planning: less than one visit per shift is ~10× too low. The **actual** cece06c0 run uses the input in **9march/xtra-shifts/** (46 vehicles, 448 shifts).

Use **less-shifts** (or our `fsr_input_81_2w.json`: 46 vehicles, 544 shifts) for realistic visit-per-shift ratios.
