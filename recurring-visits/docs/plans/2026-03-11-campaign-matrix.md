# Campaign matrix: pool size and weight strategies

**Purpose:** Table of (pool size, weight set, strategy name) and exact commands to run each variant for efficiency–continuity campaigns (Track A). Use with Huddinge 2-week or similar base input and first-run output.

**Prerequisites:**
- Base FSR input (e.g. Huddinge 2-week).
- First-run FSR output (unconstrained solve) to build continuity pools from.

---

## One-shot: generate all variants

From `recurring-visits/scripts/` (or with paths adjusted):

```bash
python run_pool_campaign.py \
  --base-input path/to/fsr-input.json \
  --first-run-output path/to/first-run-output.json \
  --out-dir continuity/variants \
  --preferred-weights 2 10 20
```

This creates `continuity/variants/pool_5/`, `pool_8/`, `pool_10/` with patched inputs and preferred (weight 2, 10, 20), wait-min, and combo payloads in each.

---

## Campaign matrix (pool size × strategy)

| Pool size | Weight / strategy        | Strategy name (label)   | Input file (after run_pool_campaign) |
|-----------|---------------------------|--------------------------|--------------------------------------|
| 5         | preferred weight 2       | preferred_2_pool5       | `continuity/variants/pool_5/input_preferred_vehicles_weight2.json` |
| 5         | preferred weight 10     | preferred_10_pool5      | `continuity/variants/pool_5/input_preferred_vehicles_weight10.json` |
| 5         | preferred weight 20     | preferred_20_pool5      | `continuity/variants/pool_5/input_preferred_vehicles_weight20.json` |
| 5         | wait-min                 | wait_min_pool5           | `continuity/variants/pool_5/input_wait_min_weight3.json` |
| 5         | combo                    | combo_pool5              | `continuity/variants/pool_5/input_combo_preferred_and_wait_min.json` |
| 5         | required (no override)   | required_pool5          | `continuity/variants/pool_5/input_pool5.json` (patched with requiredVehicles) |
| 8         | preferred weight 2       | preferred_2_pool8       | `continuity/variants/pool_8/input_preferred_vehicles_weight2.json` |
| 8         | preferred weight 10     | preferred_10_pool8      | `continuity/variants/pool_8/input_preferred_vehicles_weight10.json` |
| 8         | preferred weight 20     | preferred_20_pool8      | `continuity/variants/pool_8/input_preferred_vehicles_weight20.json` |
| 8         | wait-min                 | wait_min_pool8           | `continuity/variants/pool_8/input_wait_min_weight3.json` |
| 8         | combo                    | combo_pool8              | `continuity/variants/pool_8/input_combo_preferred_and_wait_min.json` |
| 8         | required                 | required_pool8          | `continuity/variants/pool_8/input_pool8.json` |
| 10        | preferred weight 2      | preferred_2_pool10      | `continuity/variants/pool_10/input_preferred_vehicles_weight2.json` |
| 10        | preferred weight 10     | preferred_10_pool10     | `continuity/variants/pool_10/input_preferred_vehicles_weight10.json` |
| 10        | preferred weight 20     | preferred_20_pool10     | `continuity/variants/pool_10/input_preferred_vehicles_weight20.json` |
| 10        | wait-min                 | wait_min_pool10          | `continuity/variants/pool_10/input_wait_min_weight3.json` |
| 10        | combo                    | combo_pool10             | `continuity/variants/pool_10/input_combo_preferred_and_wait_min.json` |
| 10        | required                 | required_pool10         | `continuity/variants/pool_10/input_pool10.json` |

**Required** = patched input with `requiredVehicles` (hard constraint); no weight overrides. **Preferred** = soft constraint with given weight. **Combo** = preferred + wait-min weight.

---

## Manual steps (per pool size)

If you prefer to run steps manually instead of `run_pool_campaign.py`:

### 1. Build pools (e.g. pool size 8)

```bash
python build_continuity_pools.py --source first-run \
  --input path/to/fsr-input.json \
  --output path/to/first-run-output.json \
  --out continuity/variants/pool_8/pools.json \
  --max-per-client 8 \
  --patch-fsr-input path/to/fsr-input.json \
  --patched-input continuity/variants/pool_8/input_pool8.json
```

### 2. Generate preferred / wait-min / combo variants for that pool

```bash
python prepare_continuity_test_variants.py \
  --input continuity/variants/pool_8/input_pool8.json \
  --out-dir continuity/variants/pool_8 \
  --preferred-weights 2 10 20
```

Repeat for `--max-per-client 5` and `10` with corresponding `pool_5/` and `pool_10/` paths.

---

## Submit and compare (A3)

After generating variants, submit each input with `submit_to_timefold.py solve` (no `--configuration-id`; payload config only). When solves complete:

1. Fetch solution: `fetch_timefold_solution.py <route_plan_id> --save output_<strategy>.json`
2. Metrics: `python metrics.py output_<strategy>.json --input <same-input>.json --save metrics_dir/`
3. Continuity: `python continuity_report.py --input <same-input>.json --output output_<strategy>.json --report continuity.csv`
4. Or combined: `python run_metrics_and_continuity.py --input <same-input>.json --output output_<strategy>.json --out-dir out_<strategy>/`

Summarize per strategy: unassigned, wait_efficiency_pct, average unique_count, average CCI (see `docs/CONTINUITY_METRICS.md`).
