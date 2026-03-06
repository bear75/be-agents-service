# Continuity run 57b3a619 – input confirmation and goal

## Inputs are the same (except continuity)

| | 5ff7929f base (export) | Continuity submission 57b3a619 |
|---|------------------------|--------------------------------|
| **Vehicles** | 42 | 42 (same) |
| **Shifts** | 412 | 412 (same) |
| **Standalone visits** | 3334 | 3334 (same) |
| **Visit groups** | 144 (288 visits) | 144 (288 visits) (same) |
| **Total visits** | 3622 | 3622 (same) |
| **Vehicle IDs** | Dag_00_Central_1, … | Identical |
| **Visit IDs** | Same scheme (occ_id from expanded CSV) | Same scheme |
| **requiredVehicles** | 0 | 2218 visits (51 clients with continuity pools) |

So: same capacity (42 vehicles, 412 shifts), same visits and client naming. The only change is that 2218 visits have `requiredVehicles` set so the solver prefers the same caregivers for each client.

**Why only 51 of 81 clients?** The CSV uses caregiver names like "Dag 12 ⭐ Segeltorp 1" and "Kväll 03 ⭐ Visättra"; the base input’s vehicle IDs have no ⭐ and use Swedish letters (e.g. Visättra). The mapping in `build_continuity_pools.csv_shift_name_to_fsr_vehicle_id` was updated to strip symbols (e.g. ⭐) and keep å/ä/ö, so **future runs** get **80 of 81** clients with a non-empty pool (the 81st, H113, has only "städ", which is not in the vehicle set). Run 57b3a619 was submitted with the previous logic (51 clients).

## How this solve achieves the goal

1. **Continuity** – For 51 clients we built manual pools (up to 15 preferred vehicles per client) and set `requiredVehicles` on their visits. Timefold will try to assign those visits to vehicles in the pool, so the same caregivers tend to see the same clients.
2. **Efficiency** – Same 412 shifts and 3622 visits as the base run; the solver still minimizes travel/time and uses the same capacity, so route quality and utilization stay in line with the base.
3. **Client visit IDs** – Visits are built from the same expanded CSV; visit `id` is stable (`original_visit_id`) and `name` carries client id (e.g. H015_1, H026_24) and inset type. No anonymization; IDs and names match the Huddinge source.

**Route plan ID:** `57b3a619-5b9f-43c3-bb43-18a4bc756b81`  
**Continuity input file:** `solve/input_continuity_20260303_161714.json`
