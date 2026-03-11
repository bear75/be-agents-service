# Overnight Campaign Status

**Started:** 2026-03-11 20:54
**Status:** Running in background
**Background Task ID:** b61427e

---

## What's Running

Submitting **20 campaign variants** to Timefold with **2-minute delays** between each submission:

- 18 pool variants (pool 5, 8, 10 with different strategies)
- 2 roster variants (ESS integration test)

**Why the delay?** The Timefold queue has a limit of 50 concurrent jobs. With delays, submissions queue gradually as existing jobs complete.

**Total submission time:** ~40 minutes (20 variants × 2 min delay)
**Solving time:** Each variant takes ~30-60 minutes to solve
**Expected completion:** Morning (all should be done by ~7-8 AM)

---

## Check Progress

### Monitor live submissions
```bash
tail -f /private/tmp/claude/-Users-bjornevers-MacPro-HomeCare-be-agent-service/tasks/b61427e.output
```

### Check manifest (updated after each submission)
```bash
cat campaign_manifest_delayed.json
cat campaign_manifest_delayed.md
```

---

## Morning Workflow (Fetch Results)

Once all jobs are submitted and solved:

### 1. Review the manifest
```bash
cd recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity
cat campaign_manifest_delayed.md
```

This shows all route_plan_ids and which ones succeeded/failed.

### 2. Fetch all solutions
```bash
cd ~/HomeCare/be-agent-service/recurring-visits

# Create results directory
mkdir -p huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v2/continuity/results

# For each route_plan_id in the manifest, fetch the solution
# Example for one:
python3 scripts/fetch_timefold_solution.py <route_plan_id> \
  --save huddinge-package/.../continuity/results/<strategy_name>_output.json
```

### 3. Run metrics + continuity for all solutions
```bash
# For each solution, run combined metrics
python3 scripts/run_metrics_and_continuity.py \
  --input huddinge-package/.../continuity/variants/pool_5/input_preferred_vehicles_weight2.json \
  --output huddinge-package/.../continuity/results/preferred_2_pool5_output.json \
  --out-dir huddinge-package/.../continuity/results/preferred_2_pool5 \
  --only-kundnr
```

This creates `run_summary_<id>.json` and `.md` with:
- efficiency_pct
- unassigned_visits
- average_unique_count (continuity)
- average_cci

### 4. Compare results (Pareto analysis)

Create a comparison table:

| Strategy | Pool | Efficiency % | Unassigned | Avg Unique | Avg CCI |
|----------|------|--------------|------------|------------|---------|
| preferred_2_pool5 | 5 | 72.3 | 2 | 3.2 | 0.68 |
| preferred_2_pool8 | 8 | 74.1 | 0 | 4.1 | 0.61 |
| ... | ... | ... | ... | ... | ... |

**Find the Pareto frontier:** Strategies where no other strategy is better on both efficiency AND continuity.

**Target:** continuity ≤11, efficiency >70%, unassigned <1%

---

## Campaign Variants Submitted

### Pool Size 5 (6 variants)
1. `preferred_2_pool5` - preferredVehicles weight 2
2. `preferred_10_pool5` - preferredVehicles weight 10
3. `preferred_20_pool5` - preferredVehicles weight 20
4. `wait_min_pool5` - minimizeWaitingTime weight 3
5. `combo_pool5` - both weights
6. `required_pool5` - requiredVehicles (hard constraint)

### Pool Size 8 (6 variants)
7-12. Same strategies as pool 5

### Pool Size 10 (6 variants)
13-18. Same strategies as pool 5

### Roster-based (2 variants)
19. `roster_preferred` - preferredVehicles from first-run roster
20. `roster_required` - requiredVehicles from first-run roster

---

## Files Generated

```
continuity/
├── variants/                         # Input files (already generated)
│   ├── pool_5/
│   ├── pool_8/
│   └── pool_10/
├── results/                          # Output files (fetch in morning)
│   ├── preferred_2_pool5/
│   │   ├── *_output.json
│   │   ├── run_summary_*.json
│   │   └── run_summary_*.md
│   └── ...
├── campaign_manifest_delayed.json    # Submission manifest (updating live)
├── campaign_manifest_delayed.md      # Human-readable summary
└── OVERNIGHT_CAMPAIGN_STATUS.md     # This file
```

---

## Troubleshooting

### If submissions are failing with 429 (rate limit)
The script will keep trying with 2-minute delays. Failed submissions are recorded in the manifest. You can re-run just the failed ones later.

### If background task stops
Check task status:
```bash
# View output
cat /private/tmp/claude/-Users-bjornevers-MacPro-HomeCare-be-agent-service/tasks/b61427e.output

# If stopped, restart from where it left off by checking manifest
# and submitting remaining variants manually
```

### Re-submit a single variant
```bash
cd recurring-visits/scripts
python3 submit_to_timefold.py solve \
  ../huddinge-package/.../continuity/variants/pool_5/input_preferred_vehicles_weight2.json \
  --skip-validate
```

---

## Expected Results (Based on Literature)

- **Pool 5:** Best continuity (fewest caregivers), may have higher unassigned or lower efficiency
- **Pool 8:** Balanced middle ground
- **Pool 10:** Best efficiency, slightly worse continuity
- **Weight 20 vs 2:** Stronger weight = better continuity, marginally higher cost
- **Wait-min:** Best efficiency, continuity not prioritized
- **Combo:** Balanced - good continuity with small efficiency cost

Research shows high continuity achievable with only **marginal** cost increase when using integrated routing and rostering.

---

**Good night! Check results in the morning. 🌙**
