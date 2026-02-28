# How continuity is calculated from the FSR solution

## Definition

**Continuity** = number of **distinct caregivers (vehicles)** that serve a client over the 2-week schedule.  
**Lower is better** (fewer different faces for the client).

- **Client** = person id, e.g. `H015`, `H026` (derived from visit names; one row per person, 81 clients).
- **Caregiver** = **vehicle** in the FSR model: we use **vehicle.id** only (e.g. `Dag_01_Central_1`). One vehicle = one caregiver. The same vehicle may have many **shifts** in the output (e.g. one per day); we do **not** count shifts—so it’s **vehicle (caregiver) n:1 client**, not “shifts n:1 client”. The script reports both “Caregivers (vehicles)” and “Shifts in output” so you can verify (e.g. 42 caregivers, 311 shifts).

---

## Which files are used

Continuity is computed from **exactly two files**:

| Role | File | Used for |
|------|------|----------|
| **Input** | FSR input JSON (request or patch input) | Visit id → client. The script reads `modelInput.visits[]` and `modelInput.visitGroups[].visits[]`: for each visit it takes `name` (e.g. `"H026_24 - Bad/Dusch, ..."`), splits on `" - "`, takes the prefix (`H026_24`), then strips trailing `_NN` to get **person** `H026`. So: visit id → person client. |
| **Output** | FSR output JSON (solution) | Visit id → caregiver. The script reads `modelOutput.vehicles[]`: for each vehicle (caregiver) and each shift, it walks `itinerary[]`; for each item with `kind: "VISIT"` it records (visit id, vehicle id). So: each visit occurrence → which vehicle did it. |

**Not used for continuity:**

- **patch-request.json** – Describes the *delta* sent to the solver (what to change). It does not contain the full visit list or the final assignment; the **output** is what we need.
- **CSV (huddinge_2wk_expanded_...)** – Used for **manual** schedule continuity only (script `continuity_manual_from_csv.py` with `client_externalId` and `external_slinga_shiftName`), not for FSR solution continuity.

---

## Which input + output to use

Use the **input and output that belong to the same run** (same visit set and IDs).

| Run | Input | Output | Use case |
|-----|--------|--------|----------|
| **Original (baseline)** | `req_export-field-service-routing-v1-c87d58dd-...-input.json` | `req_export-field-service-routing-c87d58dd-...-output.json` | Continuity of the first solution (no continuity constraints). |
| **Patch (continuity run)** | `patch_export-field-service-routing-v1-fa713a0d-...-input (2).json` | `patch_export-field-service-routing-fa713a0d-...-output (1).json` | Continuity of the re-optimized solution (e.g. with continuity constraints). |

Rule: **continuity is always measured from the OUTPUT** (the solution). The INPUT is only used to map visit id → client. So:

- To report continuity for the **patch solution** → use **patch input** + **patch output**.
- To report continuity for the **original solution** → use **req input** + **req output**.

---

## Calculation steps (continuity_report.py)

1. **Load input**  
   Build `visit_id → client` from `modelInput.visits` and `modelInput.visitGroups`:  
   `client = name.split(" - ")[0].strip()` then person = strip trailing `_\d+` (e.g. `H026_24` → `H026`).

2. **Load output**  
   Build list of `(visit_id, vehicle_id)` from `modelOutput.vehicles[].shifts[].itinerary[]` where `kind == "VISIT"`.

3. **Aggregate by person**  
   For each (visit_id, vehicle_id), resolve client from input, then person; group all (visit_id, vehicle_id) by person.

4. **Per-person metrics**  
   For each person:  
   - **nr_visits** = number of (visit_id, vehicle_id) pairs.  
   - **continuity** = number of distinct `vehicle_id` (distinct caregivers).

5. **Report**  
   One row per person: `client, nr_visits, continuity` (81 rows).

---

## Quick reference

```bash
# Continuity for PATCH (continuity-optimized) solution
python3 docs_2.0/recurring-visits/scripts/continuity_report.py \
  --input "docs_2.0/recurring-visits/huddinge-package/solve/24feb-conti/patch_export-field-service-routing-v1-fa713a0d-f4e7-4c56-a019-65f41042e336-input (2).json" \
  --output "docs_2.0/recurring-visits/huddinge-package/solve/24feb-conti/patch_export-field-service-routing-fa713a0d-f4e7-4c56-a019-65f41042e336-output (1).json" \
  --report docs_2.0/recurring-visits/huddinge-package/metrics/continuity_24feb_conti.csv

# Continuity for ORIGINAL (baseline) solution
python3 docs_2.0/recurring-visits/scripts/continuity_report.py \
  --input docs_2.0/recurring-visits/huddinge-package/solve/24feb-conti/req_export-field-service-routing-v1-c87d58dd-5200-41a9-a334-e075c54a7d94-input.json \
  --output docs_2.0/recurring-visits/huddinge-package/solve/24feb-conti/req_export-field-service-routing-c87d58dd-5200-41a9-a334-e075c54a7d94-output.json \
  --report docs_2.0/recurring-visits/huddinge-package/metrics/continuity_24feb_baseline.csv
```

Manual schedule continuity (from expanded CSV, different script):

```bash
python3 docs_2.0/recurring-visits/scripts/continuity_manual_from_csv.py \
  --csv docs_2.0/recurring-visits/huddinge-package/solve/24feb-conti/huddinge_2wk_expanded_20260224_043456.csv \
  --report docs_2.0/recurring-visits/huddinge-package/metrics/continuity_manual_24feb.csv
```
