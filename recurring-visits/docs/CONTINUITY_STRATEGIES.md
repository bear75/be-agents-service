# Continuity strategies: pool selection and comparison

This doc describes ways to build a **pool of up to 15 vehicles per client** for use with FSR `requiredVehicles`, and how they relate to **area-based distribution** and the **ESS + FSR** integration. You can try different setups and compare continuity and efficiency.

## Goal

- Each client (person) is served by **at most 15 distinct caregivers (vehicles)** over the 2-week window.
- FSR only supports this via a **fixed list** per visit: `requiredVehicles = [id1, …, id15]`.
- So we must **choose the pool** per client in a pre-step, then run FSR with that pool.

## Strategy overview

| Strategy                  | How the pool is chosen                                                                                                                                | Pros                                                                                               | Cons                                                                          |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- |
| **1. Manual**             | From manual CSV: distinct `external_slinga_shiftName` per client, map to FSR vehicle IDs, cap at 15.                                                  | Uses real planner behavior; often already good continuity.                                         | Tied to current manual schedule; no improvement over manual.                  |
| **2. First-run**          | Run FSR once with no continuity; for each client take top-15 vehicles by visit count; set `requiredVehicles` and re-run.                              | “Which 15” is driven by unconstrained solution; second run improves within that 15.                | Depends on first solution; may lock in a suboptimal set.                      |
| **3. Area-based**         | Group clients by area (e.g. service area or geo grid); assign vehicles to areas (e.g. even split); per client, pool = vehicles in that area (cap 15). | Even distribution of vehicles across geography; can iterate with different area/group definitions. | Need area definition and vehicle–area assignment; may underuse some vehicles. |
| **4. ESS + FSR (future)** | ESS decides who works when; FSR routes; cross-iteration continuity: feed previous FSR assignment as `preferredVehicles` in next run.                  | Aligns staffing and routing; continuity refined each iteration.                                    | Requires full ESS–FSR loop (see plan); no hard cap of 15 in FSR alone.        |

## 1. Manual schedule pool

**Idea:** The manual schedule already assigns each client to a set of employees. Use that set (mapped to FSR vehicle IDs) as the pool.

**Steps:**

1. From expanded CSV: for each `client_externalId`, collect distinct `external_slinga_shiftName`.
2. Map shift names to FSR vehicle IDs (e.g. `"Dag 01 Central 1"` → `"Dag_01_Central_1"`: replace spaces with underscores).
3. For each client, take up to 15 of those vehicle IDs.
4. In FSR input, set `requiredVehicles` to this list for **every visit** of that client.

**When to use:** You want to preserve or formalize current manual continuity; comparison baseline.

**Compare:** Run FSR with this pool, then run `continuity_report.py` and `continuity_manual_from_csv.py` to compare Caire vs manual continuity and efficiency.

---

## 2. First FSR run (unconstrained) → top-15 pool

**Idea:** Let FSR choose assignments once without continuity; then restrict each client to the 15 vehicles that served them most in that solution.

**Steps:**

1. Run FSR **without** any `requiredVehicles` (or other continuity constraints).
2. From FSR output: for each **person client**, count visits per vehicle; take the **15 vehicles with most visits** (or fewer if the client had fewer caregivers).
3. Set `requiredVehicles` for all visits of that client to this list.
4. **Re-run FSR** with these requiredVehicles. Solver only reassigns within the 15.

**When to use:** You want continuity driven by an efficiency-first solution, then lock it to 15 and re-optimize.

**Compare:** Run continuity_report on the second run’s output; compare efficiency (e.g. from pilot report) and continuity vs manual and vs area-based.

---

## 3. Area-based even distribution

**Idea:** Partition the problem by geography so each “area” gets a fair share of vehicles; each client’s pool is the vehicles assigned to their area (cap 15). You can try different area definitions and vehicle–area assignments and iterate.

**Options:**

- **By service area:** Use `serviceArea_address` or similar from CSV; group clients by that; assign vehicles to areas (e.g. round-robin: vehicle 1→area A, 2→B, … so each area gets ~same count).
- **By grid:** Derive area from `client_lat` / `client_lon` (e.g. 0.01° grid or k-means clusters); assign vehicles to grid cells evenly (e.g. 10 vehicles per 25% of areas, 10 for next 25%, etc.); for each client, pool = vehicles for their cell, cap 15.
- **Iterate:** Try different groupings (e.g. 4 areas vs 8 areas), or different rules (e.g. “10 vehicles preferred for 25% of visits in area A, 10 for 25% in area B”), then run FSR with `requiredVehicles` from that assignment and compare.

**Steps (generic):**

1. Define areas (from CSV: service area, or lat/lon grid/cluster).
2. List all FSR vehicle IDs (from FSR input).
3. Assign vehicles to areas (e.g. even split: 10 vehicles per area, or by area size).
4. For each client, get their area; pool = vehicles assigned to that area, cap at 15.
5. Set `requiredVehicles` for all visits of that client to this pool.
6. Run FSR.

**When to use:** You want continuity that respects geography and spreads caregivers evenly across regions; you’re willing to tune area definitions and compare.

**Compare:** Run FSR with area-based pools; compare continuity and efficiency vs manual and first-run pool. If a client’s area has &lt;15 vehicles, pool is smaller (stricter); if more, cap at 15.

---

## 4. ESS + FSR (from integration plan)

**Idea:** Use the TF ESS + FSR integration plan (in this repo or docs): ESS decides shifts, FSR routes; in the iterative loop, **continuity** is improved by feeding previous FSR assignment back as `preferredVehicles` in the next FSR run. Target: &lt;10–15 different caregivers per client per 14 days.

**Relevance:**

- ESS + FSR does **not** by itself enforce a hard “max 15” in one FSR call; it **refines** who serves whom across iterations via preferences.
- To get a **hard cap of 15**, you still need a **pool** (manual, first-run, or area-based) and `requiredVehicles` in FSR.
- You can **combine**: e.g. use manual or first-run pool for `requiredVehicles`, and in a future ESS–FSR loop use previous solution as `preferredVehicles` inside that pool for the next iteration.

So: ESS + FSR is a **combo** for staffing + routing + continuity refinement; the “pool of 15” remains a pre-step (manual / first-run / area-based) unless Timefold adds a native “max distinct vehicles per client” constraint.

---

## How to compare setups

**One-shot:** From `huddinge-package/`, run all strategies in parallel:

```bash
cd huddinge-package
# All 4 (base + manual + area + first-run)
python3 run_continuity_compare.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod --first-run-output solve/24feb/trimmed/export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output.json
# Only 3 (no first-run) if you omit --first-run-output
python3 run_continuity_compare.py --expanded-csv expanded/huddinge_2wk_expanded_20260224_043456.csv --weeks 2 --env prod
```

**Step-by-step:**

1. **Generate pools** (one or more):

   - Manual: `build_continuity_pools.py --source manual --csv ... --out client_pools_manual.json`
   - First-run: run FSR once, then `build_continuity_pools.py --source first-run --input ... --output ... --out client_pools_firstrun.json`
   - Area-based: `build_continuity_pools.py --source area --csv ... --fsr-input ... --out client_pools_area.json`

2. **Patch FSR input** with `requiredVehicles` from the chosen pool (script can output patched input or a mapping visit_id → requiredVehicles).

3. **Run FSR** on the patched input.

4. **Measure**:

   - `continuity_report.py` on FSR output → per-client continuity (and summary).
   - Pilot report / metrics → efficiency, travel, margin.

5. **Compare** manual vs first-run vs area-based (and, later, ESS+FSR with preferredVehicles) on continuity and efficiency; iterate on area definition or pool source as needed.

**Config tuning (second-order effect on continuity):** Increasing **`balanceTimeUtilizationWeight`** (fairness) in the Timefold profile can consolidate work onto fewer, fuller shifts → fewer active vehicles in the solution → lower max distinct caregivers per client. See `CONTINUITY_TIMEFOLD_FSR.md` (§ Model configuration: fairness and second-order effect on continuity).

---

## Summary

- **Simple and comparable:** Use **manual** or **first-run** pool + `requiredVehicles`; run FSR; compare with continuity_report and pilot metrics.
- **Even distribution by area:** Use **area-based** pools (service area or grid), assign vehicles to areas, cap 15 per client; try different groupings and compare.
- **ESS + FSR:** Use for staffing and cross-iteration continuity refinement; combine with a pool (manual/first-run/area) if you need a hard cap of 15 in FSR today.

Script: `scripts/build_continuity_pools.py` (manual, first-run, and area-based). See that script’s docstring and `CONTINUITY_TIMEFOLD_FSR.md` for FSR details.

**Empty pools:** If a client has an empty pool (e.g. no matching shift names in manual), the script still includes that client with an empty list. When patching FSR input, empty pools are skipped: no `requiredVehicles` is set for those visits, so the solver can assign any vehicle. Use `--fsr-input` with manual/area to restrict pool IDs to vehicles that exist in your FSR input.
