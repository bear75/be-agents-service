# Input comparison: cece06c0 (2 unassigned) vs 02a93fcf (1340 unassigned)

## Problem

- **cece06c0** (baseline): same config, **2 unassigned** (H035 dusch visit group).
- **02a93fcf** (shower fix): intended as "exactly the same + 1 visit group (2 CSV rows)" for the dusch fix, **1340 unassigned**.

That gap is too large to be explained by adding one visit group. So the **02a93fcf input** is likely not structurally "cece06c0 + 1 group" at the JSON level.

## How to compare the two inputs

You need the **input JSON that was actually sent** for the 02a93fcf run.

1. **If you have the file** (e.g. saved when submitting):
   ```bash
   cd be-agent-service/recurring-visits/scripts
   python3 compare_fsr_inputs.py \
     ../huddinge-package/huddinge-4mars-csv/full-csv/9march/shower-bug/export-field-service-routing-v1-cece06c0-5ce7-4898-bb52-069cb17a5cbe-input.json \
     /path/to/02a93fcf-input.json
   ```
   Optionally save report: add `--report ../huddinge-package/.../9march/shower-bug/COMPARE_cece06c0_02a93fcf.txt`

2. **If 02a93fcf was submitted with the same API key** that can read the route plan:
   ```bash
   # Fetch input from API (requires TIMEFOLD_API_KEY that has access to 02a93fcf)
   python3 fetch_timefold_solution.py 02a93fcf-e7e9-4c63-aab8-7624af4d4cbe --save /tmp/02a93fcf.json
   # Input is saved next to output; or GET .../route-plans/02a93fcf.../input and save as 02a93fcf-input.json
   ```
   Then run `compare_fsr_inputs.py` with that input path.

3. **If the “shower fix” was built by re-running the CSV pipeline** (e.g. same CSV + 2 extra rows, then `attendo_4mars_to_fsr.py` again):
   - The new run can produce **different visit IDs** or **different occurrence counts** (e.g. r47_1..4 in cece06c0 vs r47_1..14 in the new run).
   - Any **visitDependencies** that reference preceding visits (e.g. dusch → morgon) must use **IDs that exist** in the same input. The doc `INPUT_COMPARISON_cece06c0_vs_16f53762.md` describes an invalid fix that referenced H035_r47_5..14 while only r47_1..4 existed → validate fails or solver leaves many visits unassigned.
   - So: use the **same** cece06c0 input and **patch it** (add one visit group + dependencies that reference existing morgon IDs) instead of re-running the full pipeline from CSV, unless you guarantee the pipeline output is identical except for the extra group.

## What the comparison script reports

- **Counts**: standalone visits, visit groups, visits in groups, total visits, vehicles, shifts.
- **Visit ID diff**: IDs only in reference, only in candidate, common. If “only in candidate” is huge or “only in reference” is huge, the two inputs are not “same + 1 group”.
- **visitDependencies**: every `precedingVisit` ref; **missing refs** = dependency points to a visit ID that does not exist in that input. Missing refs can cause the solver to leave those visits (and possibly others) unassigned.
- **Vehicles**: vehicle IDs only in one input; visits that reference non-existent requiredVehicles/preferredVehicles.

## Likely causes of 1340 unassigned

1. **Broken precedingVisit refs**  
   The “shower fix” adds dusch-after-morgon dependencies, but the morgon visit IDs in the fix input (e.g. H035_r47_*) don’t match the occurrence set (e.g. only r47_1..4 exist but deps reference r47_5..14). Validate with `submit_to_timefold.py validate <input.json>` before submit.

2. **Different input source**  
   The 02a93fcf input might come from a different CSV run (e.g. different date range or expansion), so it has different total visits, different IDs, or fewer shifts/vehicles → many visits can’t be placed.

3. **Fewer vehicles/shifts in candidate**  
   If the candidate has fewer shifts or different vehicle IDs, capacity or requiredVehicles constraints can force a large number of unassigned visits.

Run the comparison and fix any missing dependency refs or structural differences so the fix input is truly “cece06c0 + 1 visit group” before re-submitting.
