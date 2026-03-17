# Recommendations to improve metrics and run new solutions

**Goals:** Field efficiency **>75%**, continuity avg ≤11, unassigned **<1%**.

Current best on v3: field eff. ~73.8% (pool8_required, job_70ac29c5); no run meets all three goals.

---

## 1. Recommendations to improve

### 1.1 Raise field efficiency (visit / (visit + travel))

- **Reduce travel:**  
  - Use **preferred depots** or area-based vehicle assignment so the same vehicles serve clustered clients.  
  - Tighten **continuity pools** (e.g. pool5/pool8) so routes are more compact; avoid baseline (all vehicles) which spreads assignments and increases travel.
- **Avoid “all vehicles” baseline for efficiency:**  
  Baseline (195 vehicles, 5260 shifts) has 65.88% field efficiency and 2974 empty shifts; it maximizes coverage but hurts efficiency. Prefer **restricted-pool** inputs (pool5/pool8) for efficiency-focused runs.
- **Soften pool constraint where it helps:**  
  **pool8_preferred** (72.81%) allows the solver to use vehicles outside the pool when it reduces travel; consider **pool5_preferred** or **pool8_preferred** with **longer solve time** to push toward >75%.
- **Longer solve time:**  
  Submit with a higher **terminationSpentLimit** (e.g. 30–60 min) so the solver can improve route compactness and travel.

### 1.2 Lower unassigned visits

- **Use pool8 or pool10 (required) for coverage:**  
  pool8_required has 162 unassigned (4.2%); pool10_required has 1273 (16.6%) on the **same** 7653-visit input but with more vehicles per client — the current pool10 run has very high wait (2347h) and many empty shifts, so the input or run may need tuning.
- **Include empty-shift vehicles in client pools:**  
  For clients with unassigned visits, add vehicles that have **empty shifts overlapping** those visit windows to the client’s pool (see `empty_shifts.txt` and `WHERE_TIME_AND_FIX.md` for pool8).
- **Slightly relax pool size for worst-affected clients:**  
  For clients that still have many unassigned after the above, try pool 9 or 10 **only for those clients** to avoid blowing continuity for the rest.
- **Check time windows and dependencies:**  
  Inspect unassigned visits in the FSR input: wide time windows and relaxed dependencies can help; some may need more capacity (pool/vehicles).

### 1.3 Continuity (≤11)

- **Tight pools (pool3/pool5)** already give excellent continuity (1.74 / 2.56) but poor coverage.  
- **pool8_required** (3.69) and **job_70ac29c5** (10.30) meet ≤11.  
- To **improve efficiency without hurting continuity**, prefer **pool8_preferred** or **pool5_preferred** (soft pool) so the solver can optimize travel while still favoring the same caregivers.

---

## 2. Suggested new runs (to aim for >75% and <1% unassigned)

| Run | Description | How |
|-----|-------------|-----|
| **pool8_preferred_long** | Same as pool8_preferred but **longer solve** (e.g. 45 min) to improve routes and field efficiency. | Build input from pool8, set preferredVehicles, strip tags, submit with `terminationSpentLimit`. |
| **pool5_preferred** | Soft pool of 5 per client; balance continuity and efficiency. | `./scripts/analytics/submit_pool5_preferred.sh` (builds + submits). |
| **pool8_from_70ac29c5** | Use **70ac29c5** solution as **from-patch** seed: fix unassigned and improve routes. | Export 70ac29c5 output, build patch payload for unassigned visits, submit from-patch. |
| **Pilot input (41 vehicles) with longer solve** | Same input as job_70ac29c5 (4126 visits, 41 vehicles); run with 45–60 min limit. | Use tf17march input (no tags), submit solve with custom termination. |

---

## 3. How to run new solutions

### 3.1 Submit a new solve (existing script)

```bash
cd be-agent-service
TIMEFOLD_API_KEY="tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938"

# Efficiency-oriented runs (pool8_preferred, pool10 already submitted)
./scripts/analytics/submit_v3_efficiency_runs.sh   # pool10 + pool8_preferred (already done)

# Custom: submit any FSR input (strip tags first)
python3 recurring-visits/scripts/submit_to_timefold.py solve path/to/input_no_tags.json \
  --api-key "$TIMEFOLD_API_KEY" --skip-validate --no-register-darwin
```

### 3.2 Build pool5_preferred input (new run)

```bash
cd be-agent-service
# 1) Pools from baseline, max 5 per client
python3 scripts/continuity/build_pools.py --source first-run \
  --input recurring-visits/.../v3/input_v3_from_Data_final_no_tags.json \
  --output scripts/analytics/campaign_analysis/baseline_data_final/output.json \
  --out recurring-visits/.../v3/continuity/variants/pools_5.json \
  --max-per-client 5

# 2) Patch base input with preferredVehicles (and write patched input)
# Use build_pools.py --patch-fsr-input and --patched-input with --use-preferred;
# then strip tags and submit via submit_to_timefold.py solve.
```

### 3.3 Longer solve time

If your Timefold configuration supports it, set a higher **terminationSpentLimit** in the solve request (or in the configuration profile) so the solver runs 30–60 minutes. Then fetch and run:

```bash
./scripts/analytics/analyze_job.sh <new_plan_id> --input <input.json> --out-dir scripts/analytics/campaign_analysis/<name>
```

### 3.4 After each new run

1. Wait for **SOLVING_COMPLETED**.  
2. Run **analyze_job.sh** (by plan ID or `--output` with saved JSON).  
3. Read **field_efficiency_pct** from the visit-span `metrics_*.json`; check **continuity_summary.txt** and **unassigned_visits**.  
4. Add the run to **ALL_JOBS_REPORT.md** and, if useful, to **efficiency_runs_manifest.md**.

---

## 4. Quick reference

- **All metric report locations:** `scripts/analytics/METRIC_REPORTS_INDEX.md`  
- **This report:** `scripts/analytics/campaign_analysis/ALL_JOBS_REPORT.md`  
- **Efficiency runs manifest:** `scripts/analytics/campaign_analysis/efficiency_runs_manifest.md`  
- **Submit script (pool10 + pool8_preferred):** `scripts/analytics/submit_v3_efficiency_runs.sh`  
- **Single-job full analytics:** `scripts/analytics/analyze_job.sh`
