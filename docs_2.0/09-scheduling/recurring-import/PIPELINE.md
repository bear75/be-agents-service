# Pipeline: CSV → Input JSON → Timefold solve → From-patch (iterate)

End-to-end flow from the original visit list (CSV) to a trimmed solution with no employees that have zero visits. Each step lists **file → script → output**.

**Directory structure:** Scripts live in `scripts/`, data in `data/`. Run commands from `local/test_data_import/` (or the repo root containing this folder).

---

## Step 1: Original data (CSV) → Input JSON

| Item             | Path                                                  |
| ---------------- | ----------------------------------------------------- |
| **Original CSV** | `data/anonymized/movable_visits_anonymized_v2.csv`    |
| **Output JSON**  | `data/anonymized/movable_visits_unplanned_input.json` |

Contains: visit list, `visit_id`, `double_id`, Slinga/route, skills, time windows, duration, location, etc. Anonymized format: header row 3 (0-indexed); Huddinge/Nova: header row 1.

**Script:** `scripts/csv_to_timefold_json.py` converts the CSV to Timefold FSR `modelInput` (visits + vehicleShifts/placeholder shifts).

```bash
python scripts/csv_to_timefold_json.py data/anonymized/movable_visits_anonymized_v2.csv -o data/anonymized/movable_visits_unplanned_input.json
# Auto-detects format. Use --format huddinge|nova for Swedish column names.
```

---

## Step 2: Input JSON (full FSR input)

| Item                        | Path                                                  |
| --------------------------- | ----------------------------------------------------- |
| **Input JSON** (modelInput) | `data/anonymized/movable_visits_unplanned_input.json` |

Contains: `modelInput.visits`, `modelInput.vehicles` (placeholder shifts). Optional: wrap with `config` from a reference request for API submission.

---

## Step 3: Timefold solve (first run)

| Item            | Path / command                                                                             |
| --------------- | ------------------------------------------------------------------------------------------ |
| **Script**      | `scripts/submit_to_timefold.py`                                                            |
| **Input**       | `data/anonymized/movable_visits_unplanned_input.json` (or any modelInput JSON).            |
| **Command**     | `python scripts/submit_to_timefold.py data/anonymized/movable_visits_unplanned_input.json` |
| **API**         | `POST /v1/route-plans` (create new route plan and solve).                                  |
| **Output JSON** | Save the response; route plan id is in the response. Download solution when complete.      |

**Output:** Save downloaded solution to e.g. `fixed/<route-plan-id>-output.json`.

---

## Step 4: Script builds patch (pin visits + remove empty vehicles)

| Item                                      | Path / command                                                                                                                                                         |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Script**                                | `scripts/run_from_patch.py`                                                                                                                                            |
| **Inputs**                                | Latest **solution output**; optional **full input** (to list all vehicle ids; if omitted, vehicle list is taken from the solution).                                    |
| **Command (first from-patch)**            | `python scripts/run_from_patch.py --solution fixed/<solution-output>.json --input data/anonymized/movable_visits_unplanned_input.json --route-plan-id <route-plan-id>` |
| **Command (next from-patch, no --input)** | `python scripts/run_from_patch.py --solution fixed/from-patch-reduced/<output>.json --route-plan-id <new-route-plan-id>`                                               |
| **Output**                                | Patch is built and POSTed; download the new solution when complete. Use `--dry-run` to only write the patch JSON without POSTing.                                      |

Patch contents: for each vehicle with **0 visits** → `remove /vehicles/[id=...]`; for each assigned visit → `add /visits/[id=...]/pinningRequested`, `add /visits/[id=...]/minStartTravelTime`. This preserves the assignment and trims employees with no visits.

---

## Step 5: Timefold from-patch

| Item        | Path / command                                                                                                              |
| ----------- | --------------------------------------------------------------------------------------------------------------------------- |
| **API**     | `POST /v1/route-plans/{route_plan_id}/from-patch` with body `{ "config": { "run": { "name": "..." } }, "patch": [ ... ] }`. |
| **Done by** | `scripts/run_from_patch.py` (unless `--dry-run`).                                                                           |
| **Output**  | New route plan id (new revision). Download solution when complete.                                                          |

**Output:** Save to `fixed/from-patch-reduced/<output>.json`.

---

## Step 6: Iterate until no employees with 0 visits

Repeat **Step 4** and **Step 5**:

1. Use the **latest from-patch output** as `--solution`.
2. Use that output’s route plan id as `--route-plan-id`.
3. Omit `--input` (script infers vehicle list from the solution and removes any vehicle with 0 visits).
4. Run `scripts/run_from_patch.py` → patch is built and POSTed.
5. Download the new solution.
6. If the solution still has vehicles with 0 visits, go to 1. Otherwise stop.

**Limitation:** We only send remove for **whole vehicles**. Whether the API supports removing individual shifts (e.g. `remove /vehicles/[id=X]/shifts/[id=Y]`) is unknown. So once every remaining vehicle has at least one visit, there are no more vehicles to remove; the 167 “empty” empty slots were break-only shifts. To try removing those shifts in the patch, use `--remove-empty-shifts` (see **docs/WHY_TRIM_EMPLOYEES_DILEMMA.md**).

---

## File and script reference

| Step | File / artifact                                       | Script                             | Output / next file                                    |
| ---- | ----------------------------------------------------- | ---------------------------------- | ----------------------------------------------------- |
| 1    | `data/anonymized/movable_visits_anonymized_v2.csv`    | `scripts/csv_to_timefold_json.py`  | `data/anonymized/movable_visits_unplanned_input.json` |
| 2    | `data/anonymized/movable_visits_unplanned_input.json` | —                                  | Input for Step 3                                      |
| 3    | Input JSON                                            | `scripts/submit_to_timefold.py`    | Timefold solve → **output JSON** (save to `fixed/`)   |
| 4    | Output JSON + (optional) full input                   | `scripts/run_from_patch.py`        | Patch built and POSTed                                |
| 5    | (same)                                                | `scripts/run_from_patch.py` (POST) | Timefold from-patch → **output JSON**                 |
| 6    | Latest output JSON                                    | `scripts/run_from_patch.py`        | Repeat until no vehicles with 0 visits                |

---

## Other scripts and files

| Script / file                               | Purpose                                                                                                                                                                                                                                                                                                                                                                         |
| ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `scripts/build_reduced_input.py`            | Builds a **reduced input** (only used vehicles and used shifts) from a solution. Outputs e.g. `movable_visits_unplanned_input_reduced.json` or `fixed/from-patch-reduced/input-only-used-shifts.json`. Use for reference or for a reduced input; **do not** submit that as a new route plan if you want to keep the current assignment (see `APPROACH_FROM_SOLUTION_PATCH.md`). |
| `scripts/compare_full_vs_from_patch.py`     | Compares two solution outputs: shift time (excl. breaks), visit time, travel, wait, efficiency %.                                                                                                                                                                                                                                                                               |
| `scripts/count_doubles_and_reduce_input.py` | Counts distinct `double_id` in the input (from CSV); optionally builds the trimmed input (only used shifts) from the from-patch solution.                                                                                                                                                                                                                                       |
| `scripts/run_per_day_workaround.py`         | Per-day efficiency check and workaround.                                                                                                                                                                                                                                                                                                                                        |
| `scripts/upstream/`                         | Data prep: transform_visits_v2.py, geocode_addresses.py, anonymize-visits-csv.mjs (raw Excel → geocoded CSV).                                                                                                                                                                                                                                                                   |
| `README_REDUCED_INPUT.md`                   | Where files are stored, working process (pin + trim via from-patch), when to use from-patch vs new route plan.                                                                                                                                                                                                                                                                  |
| `APPROACH_FROM_SOLUTION_PATCH.md`           | Why from-patch (pin + remove) is used; why “reduce input and re-solve” is avoided.                                                                                                                                                                                                                                                                                              |

---

## Quick command sequence

```bash
# 1. CSV → JSON (from data/anonymized/)
python scripts/csv_to_timefold_json.py data/anonymized/movable_visits_anonymized_v2.csv -o data/anonymized/movable_visits_unplanned_input.json

# 2. Submit to Timefold
python scripts/submit_to_timefold.py data/anonymized/movable_visits_unplanned_input.json
# → Download solution, save to fixed/, note route_plan_id

# 3. First from-patch (from full solution)
python scripts/run_from_patch.py \
  --solution fixed/<solution-output>.json \
  --input data/anonymized/movable_visits_unplanned_input.json \
  --route-plan-id <route-plan-id>
# → Download new solution, note new route_plan_id

# 4. Next from-patch (no --input)
python scripts/run_from_patch.py \
  --solution fixed/from-patch-reduced/<output>.json \
  --route-plan-id <new-route-plan-id>
# → Repeat until no vehicles with 0 visits remain
```
