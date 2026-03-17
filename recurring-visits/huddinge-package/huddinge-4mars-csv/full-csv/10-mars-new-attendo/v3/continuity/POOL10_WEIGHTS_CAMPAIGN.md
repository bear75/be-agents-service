# Pool 10 + Weights Campaign: Preferred Pools, Wait, Travel, PreferredVehicles

**Goal:** Expand to pool size 10 (more flexibility, fewer unassigned) and test combinations of **preferred caregiver pools** with solver **weight tuning** for wait, travel, and preferredVehicles. Document, run, fetch, analyze, and compare.

---

## 1. Strategy

| Dimension | What we test |
|-----------|----------------|
| **Pool size** | 10 (per-client pool of up to 10 vehicles) — already built as `input_pool10_required.json`. |
| **Constraint type** | **Required** (hard) vs **Preferred** (soft; solver can use outside pool to reduce wait/travel). |
| **PreferredVehicles weight** | Soft penalty when a visit is assigned to a vehicle outside the preferred list: weight **2** (gentle), **10** (medium), **20** (strong). |
| **Wait** | `minimizeWaitingTimeWeight` — penalize idle time between visits. |
| **Travel** | `minimizeTravelTimeWeight` — penalize travel time (improves field efficiency). |
| **Combo** | Preferred (weight 2) + wait-min (weight 3) to balance continuity and efficiency. |

**Solver config:** We use **payload config** (`config.model.overrides` in the same JSON as `modelInput`) with `--configuration-id ""` so each variant file carries its own weights. Timefold FSR applies these overrides when no configurationId is passed.

**Solve time (campaign vs default):** The run script injects **runConfiguration.termination** into every payload (`config.run.termination`): **spentLimit=PT3H** (max solve time), **unimprovedSpentLimit=PT15M** (stop when score hasn’t improved for this long; ISO 8601). Overrides your default short test config. Reference config: `c522a20a-89c9-4a5b-aca2-46887a254ac7`. Env overrides: `TIMEFOLD_CAMPAIGN_SPENT_LIMIT`, `TIMEFOLD_CAMPAIGN_UNIMPROVED`.

**Recommended variant:** **pool10_from_patch** — from-patch on pool10_required (pin visits, trim shifts, remove empty) with long solve (PT3H spentLimit, PT15M unimprovedSpentLimit). Route plan ID: `4b5536f2-df02-431a-a7f4-d24fee45ed55`. Best balance: 1.4% unassigned, 72.88% field eff., 9.84 continuity. Run: `v3/continuity/run_pool10_from_patch.sh`.

---

## 2. Variants

| Variant | Pool | Constraint | Weights / focus | Input file (after generation) |
|---------|------|------------|-----------------|-------------------------------|
| **pool10_required** | 10 | required | (default) | `variants/input_pool10_required.json` (existing) |
| **pool10_preferred_w2** | 10 | preferred | preferVisitVehicleMatchPreferredVehiclesWeight=2 | `variants/pool10/input_preferred_vehicles_weight2.json` |
| **pool10_preferred_w10** | 10 | preferred | weight=10 | `variants/pool10/input_preferred_vehicles_weight10.json` |
| **pool10_preferred_w20** | 10 | preferred | weight=20 | `variants/pool10/input_preferred_vehicles_weight20.json` |
| **pool10_wait_min** | 10 | (unchanged) | minimizeWaitingTimeWeight=3 | `variants/pool10/input_wait_min_weight3.json` |
| **pool10_combo** | 10 | preferred | preferred weight 2 + minimizeWaitingTimeWeight=3 | `variants/pool10/input_combo_preferred_and_wait_min.json` |
| **pool10_travel** | 10 | (unchanged) | minimizeTravelTimeWeight=5 | `variants/pool10/input_travel_weight5.json` (see step 2b) |

---

## 3. Step 1: Generate variant inputs

From **be-agent-service** root. Paths relative to repo root.

```bash
V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3
POOL10_INPUT="$V3/continuity/variants/input_pool10_required.json"
OUT_DIR="$V3/continuity/variants/pool10"
mkdir -p "$OUT_DIR"

# Input must have modelInput (or be the FSR payload). If input_pool10_required has only modelInput, the script adds config.
python3 recurring-visits/scripts/prepare_continuity_test_variants.py \
  --input "$POOL10_INPUT" \
  --out-dir "$OUT_DIR" \
  --preferred-weights 2 10 20
```

This creates:

- `pool10/input_preferred_vehicles_weight2.json`
- `pool10/input_preferred_vehicles_weight10.json`
- `pool10/input_preferred_vehicles_weight20.json`
- `pool10/input_wait_min_weight3.json`
- `pool10/input_combo_preferred_and_wait_min.json`

### 3b. Travel-focused variant (optional)

The script does not emit a travel-only variant. Add it by copying the wait_min JSON and setting `minimizeTravelTimeWeight` in `config.model.overrides`:

```bash
# From be-agent-service root; OUT_DIR set from step 1
python3 -c "
import json
from pathlib import Path
out_dir = Path('$V3/continuity/variants/pool10')
p = out_dir / 'input_wait_min_weight3.json'
d = json.loads(p.read_text())
overrides = d.setdefault('config', {}).setdefault('model', {}).setdefault('overrides', {})
overrides['minimizeWaitingTimeWeight'] = 1
overrides['minimizeTravelTimeWeight'] = 5
(out_dir / 'input_travel_weight5.json').write_text(json.dumps(d, indent=2, ensure_ascii=False))
print('Wrote input_travel_weight5.json')
"
```

Run with `V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3` set. Or manually edit a copy of `input_pool10_required.json`: add `"config": { "model": { "overrides": { "minimizeTravelTimeWeight": 5 } } }`.

---

## 4. Step 2: Submit all variants

From **be-agent-service** root. Use `--configuration-id ""` so the payload’s `config.model.overrides` are used. **The run script injects runConfiguration.termination: spentLimit=PT3H, unimprovedSpentLimit=PT15M** into every payload so campaign runs use a long solve instead of the default short test config. Submits run in parallel; record each route plan ID.

```bash
V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3
RES="$V3/continuity/results"

# Pool10 required (existing)
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/input_pool10_required.json" \
  --configuration-id "" --strategy "pool10_required" --dataset huddinge-v3 \
  --save "$RES/pool10_required"

# Pool10 preferred weights
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_preferred_vehicles_weight2.json" \
  --configuration-id "" --strategy "pool10_preferred_w2" --dataset huddinge-v3 \
  --save "$RES/pool10_preferred_w2"
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_preferred_vehicles_weight10.json" \
  --configuration-id "" --strategy "pool10_preferred_w10" --dataset huddinge-v3 \
  --save "$RES/pool10_preferred_w10"
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_preferred_vehicles_weight20.json" \
  --configuration-id "" --strategy "pool10_preferred_w20" --dataset huddinge-v3 \
  --save "$RES/pool10_preferred_w20"

# Wait-min and combo
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_wait_min_weight3.json" \
  --configuration-id "" --strategy "pool10_wait_min" --dataset huddinge-v3 \
  --save "$RES/pool10_wait_min"
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_combo_preferred_and_wait_min.json" \
  --configuration-id "" --strategy "pool10_combo" --dataset huddinge-v3 \
  --save "$RES/pool10_combo"

# Travel (if created)
python3 scripts/timefold/submit.py solve "$V3/continuity/variants/pool10/input_travel_weight5.json" \
  --configuration-id "" --strategy "pool10_travel" --dataset huddinge-v3 \
  --save "$RES/pool10_travel"
```

Record each **Route plan ID** in the table below (update after each run).

---

## 5. Step 3: Fetch and run metrics + continuity

When status is `SOLVING_COMPLETED`, fetch each route plan and run metrics and continuity (same pattern as the v3 campaign). From **be-agent-service**:

```bash
V3=recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3
INPUT="$V3/input_v3_from_Data_final_no_tags.json"
cd recurring-visits/scripts
export TIMEFOLD_API_KEY="<test-tenant-key>"

# Example for one variant (repeat for each route plan ID and result dir)
python3 fetch_timefold_solution.py <ROUTE_PLAN_ID> \
  --save "../../scripts/analytics/campaign_analysis/pool10_<variant>/output.json" \
  --input "$INPUT" \
  --metrics-dir "../../scripts/analytics/campaign_analysis/pool10_<variant>"
```

Or use the campaign fetch script pattern: for each variant, run fetch with `--save` and `--metrics-dir` pointing to `scripts/analytics/campaign_analysis/pool10_<variant>/`.

---

## 6. Step 4: Compare results

After all jobs are fetched and metrics/continuity are run, fill the comparison table. Use the same metrics as in `scripts/analytics/campaign_analysis/SUMMARY.md`: assigned, unassigned %, field efficiency, continuity avg, goals (≤11 continuity, ≥70% eff).

### Results table (fill after fetch)

| Variant | Route plan ID | Assigned | Unassigned % | Field eff. | Continuity avg | ≤11 | Eff. ≥70% |
|---------|---------------|----------|--------------|------------|----------------|-----|-----------|
| pool10_required | | | | | | | |
| pool10_preferred_w2 | | | | | | | |
| pool10_preferred_w10 | | | | | | | |
| pool10_preferred_w20 | | | | | | | |
| pool10_wait_min | | | | | | | |
| pool10_combo | | | | | | | |
| pool10_travel | | | | | | | |

### How to fill the table

- **Assigned / Unassigned %:** From each variant’s `metrics_*.json`: `total_visits_assigned`, `unassigned_visits`; unassigned % = 100 * unassigned_visits / total_visits (e.g. 7653).
- **Field eff.:** `field_efficiency_pct` from `metrics_*.json`.
- **Continuity avg:** From `continuity.csv` or `continuity_summary.txt` in that variant’s folder (average of the `continuity` column).

You can extend `scripts/analytics/campaign_analysis/build_campaign_summary.py` to include the `pool10_*` variant dirs so it regenerates a single SUMMARY that includes these rows, or maintain this table manually in this doc.

---

## 7. Analysis and recommendations

After the table is filled:

1. **Preferred weight:** Compare pool10_preferred_w2 vs w10 vs w20 — higher weight should improve continuity but may increase unassigned or hurt efficiency; pick the best trade-off.
2. **Wait-min vs travel:** Compare pool10_wait_min and pool10_travel vs pool10_required — which improves field efficiency more without hurting continuity or unassigned?
3. **Combo:** pool10_combo (preferred 2 + wait-min 3) should balance continuity and efficiency; check if it dominates others on both.
4. **vs pool 8:** Compare pool10_* to existing pool8_required / pool8_preferred — does expanding to 10 reduce unassigned while keeping continuity and efficiency acceptable?

Document conclusions and recommended variant(s) at the end of this file or in `scripts/analytics/campaign_analysis/SUMMARY.md`.

---

## 8. Reference: override keys (Timefold FSR)

| Override | Effect |
|----------|--------|
| `preferVisitVehicleMatchPreferredVehiclesWeight` | Soft penalty when visit is assigned to a vehicle not in the visit’s `preferredVehicles` list. |
| `minimizeWaitingTimeWeight` | Penalize waiting time between visits. |
| `minimizeTravelTimeWeight` | Penalize travel time (reduces travel, improves field efficiency). |

All are applied via `config.model.overrides` in the same JSON as `modelInput`, with `--configuration-id ""`.

---

## 9. One-shot: generate + submit

From **be-agent-service** root:

```bash
bash recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/run_pool10_weights_campaign.sh
```

This generates all variant inputs (including travel), then submits each with `--no-wait`. Record the route plan IDs from the output, then run fetch + metrics + continuity for each (step 3) and fill the comparison table (step 4).

---

## 10. File locations

- **Pool 10 required input:** `v3/continuity/variants/input_pool10_required.json`
- **Pool 10 pool file:** `v3/continuity/variants/pools_10.json` (if used for building)
- **Generated weight variants:** `v3/continuity/variants/pool10/*.json`
- **Submit script:** `be-agent-service/scripts/timefold/submit.py`
- **Variant generator:** `be-agent-service/recurring-visits/scripts/prepare_continuity_test_variants.py`
- **Fetch + metrics:** `be-agent-service/recurring-visits/scripts/fetch_timefold_solution.py` (or campaign fetch script)
- **Comparison / summary:** `be-agent-service/scripts/analytics/campaign_analysis/` (per-variant dirs + SUMMARY or this doc)
- **Run script:** `v3/continuity/run_pool10_weights_campaign.sh`
