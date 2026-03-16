# Reduced input (no oversupply) for Timefold FSR

**Full pipeline (CSV → input JSON → solve → from-patch, iterate):** see [PIPELINE.md](PIPELINE.md).

## Where files are stored

| What                                                                | Path                                                                    |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Original CSV** (visit list, double_id, etc.)                      | `movable_visits_anonymized_v2.csv` (or `movable_visits_anonymized.csv`) |
| **Original JSON** (full FSR input: all visits, all vehicles/shifts) | `movable_visits_unplanned_input.json`                                   |
| **Trimmed JSON (only used shifts)**                                 | `fixed/from-patch-reduced/input-only-used-shifts.json`                  |
| **Earlier reduced (from full fixed solution)**                      | `movable_visits_unplanned_input_reduced.json`                           |

Other outputs: `fixed/` has solution outputs; `hourly/` has full inputs with config (e.g. 1h termination); `fixed/from-patch-reduced/` has the from-patch solution, patch request, and the trimmed input we submit.

## Working process: pin visits + trim (from-patch), don’t re-solve from scratch

The **intended process** is:

1. **Pin** all assigned visits (so they stay on the same employee/shift).
2. **Trim** by removing employees (vehicles) that have no visits.
3. Use **from-patch** to do both: patch = “add pinning for every assigned visit” + “remove vehicles with 0 visits”. That way the **solution is preserved** — same assignment, fewer vehicles in the input.
4. Repeat from-patch if you trim again (e.g. after more capacity is removed, again pin + remove empty vehicles).

**Important:** The API only supports removing **whole vehicles** in a patch, not individual shifts. So after the first from-patch we had 31 vehicles left (all with ≥1 visit); there were no more _vehicles_ to remove. The 167 “empty” slots were break-only _shifts_ inside those 31 vehicles, which cannot be removed via patch.

**What we did by mistake:** We also built a **trimmed input file** (only 31 vehicles, 143 shifts) and sent it with `submit_to_timefold.py` as a **new** route plan (POST create). That runs the solver **from scratch with no pinning**, so the solution can change and visits can end up assigned differently (or unassigned; see `APPROACH_FROM_SOLUTION_PATCH.md` — re-solve on reduced input gave 29 unassigned visits). So that submit was **not** following the working process. The **correct** way to trim is from-patch (pin + remove vehicles), not “new route plan with trimmed input”.

## Why we reduce input

We **must not send oversupply** to Timefold. If we send 39 vehicles and 342 shifts, the solver still tends to **activate many of them** even when we minimize technician cost (e.g. hourly). So we **remove** the extra employees and shifts from the payload: we send only the employees and shifts we actually need.

**Flow:**

1. **Phase 1:** Run TF with full input and **fixed** shift cost so the solver is charged for every shift → it uses fewer shifts (e.g. 31 vehicles, 143 shifts with visits).
2. **Phase 2:** From that **solution**, build a **reduced input** that contains only those 31 vehicles and only those 143 shifts (visits unchanged). Submit this reduced input to TF (e.g. with hourly cost). TF then has no oversupply to activate.

## Script

- **`build_reduced_input.py`** – Reads a solution output and a full input JSON; writes a new input with only vehicles and shifts that had ≥1 visit in the solution. **Use the fixed-cost input as source** so the reduced file has fixed costs (1375 per shift, no hourly rates).

```bash
# Default: uses fixed-cost input (eb827631) → reduced output has fixed costs
python build_reduced_input.py

# Or explicitly (same result)
python build_reduced_input.py \
  --solution fixed/export-field-service-routing-eb827631-6657-4c4f-948f-0c8aeceacd62-output.json \
  --input hourly/export-field-service-routing-v1-eb827631-6657-4c4f-948f-0c8aeceacd62-input.json \
  --output movable_visits_unplanned_input_reduced.json
```

Result: **1816 visits, 31 vehicles, 143 shifts**, **fixed cost** (fixedCost: 1375, rates: []) — no oversupply, no hourly rates.

## Process summary

| Step                                            | Tool                                          | What it does                                                                                                                                    |
| ----------------------------------------------- | --------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **First run** (full input)                      | `submit_to_timefold.py` or your submit script | POST full or reduced input → new route plan, solver runs from scratch.                                                                          |
| **Trim and keep assignment**                    | `run_from_patch.py`                           | POST **from-patch** with patch = pin all assigned visits + remove vehicles with 0 visits. Solution stays the same; input loses unused vehicles. |
| **Re-solve on trimmed input** (not recommended) | `submit_to_timefold.py`                       | POST trimmed input as **new** route plan. No pinning → solver may assign differently or leave visits unassigned.                                |

Use **from-patch** whenever you want to “keep the current solution and just remove employees that have no visits”. Use **submit (new route plan)** only for the first run or when you explicitly want a fresh solve.

## Submitting

**Preferred (trim and keep assignment):** use from-patch with pin + remove:

```bash
# Build patch from solution: remove vehicles with 0 visits, pin all 1816 visits
python run_from_patch.py --solution fixed/...-output.json --input hourly/...-input.json --route-plan-id <id>
# Or from a previous from-patch output (no --input): remove empty vehicles, pin visits
python run_from_patch.py --solution fixed/from-patch-reduced/...-output.json --route-plan-id 5ff46c3d-...
```

**New route plan (first run or intentional re-solve):**

```bash
python submit_to_timefold.py movable_visits_unplanned_input.json
```

The trimmed file `fixed/from-patch-reduced/input-only-used-shifts.json` is mainly for reference or for building a fresh input; submitting it as a new plan re-solves without pinning (see above).
