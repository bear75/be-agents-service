# Metric reports index

**Goal:** Field efficiency (Reseffektivitet) **> 75%** — from `metrics.py --visit-span-only` → `field_efficiency_pct`.

All paths below are under `be-agent-service/` (root = repo root).

---

## Campaign analysis (v3 continuity)

**Input:** `recurring-visits/.../v3/input_v3_from_Data_final.json`  
**Reports:** `scripts/analytics/campaign_analysis/`

| Variant                 | Field eff. | Goal >75% | Metrics JSON | Text report |
|-------------------------|------------|-----------|--------------|-------------|
| baseline_data_final     | 65.88%     | No        | campaign_analysis/baseline_data_final/metrics_*_cf407218.json | metrics_report_cf407218.txt |
| pool3_required          | 73.32%     | No        | campaign_analysis/pool3_required/metrics_*_c1ea12a5.json      | metrics_report_c1ea12a5.txt |
| pool5_required          | 73.25%     | No        | campaign_analysis/pool5_required/metrics_*_d87e9a1a.json      | metrics_report_d87e9a1a.txt |
| pool8_required          | 73.82%     | No        | campaign_analysis/pool8_required/metrics_*_5e55bf3a.json       | metrics_report_5e55bf3a.txt |

**Summary:** `campaign_analysis/SUMMARY.md`  
**New runs for >75%:** `scripts/analytics/submit_v3_efficiency_runs.sh` (builds pool10_required, pool8_preferred; submits with test tenant key). Plan IDs: `campaign_analysis/efficiency_runs_manifest.md`.  
**Per-job:** each variant folder has `output.json`, `metrics_*.json`, `continuity.csv`, `continuity_summary.txt`, `empty_shifts.txt`.

---

## Other runs

| Run / dataset           | Field eff. | Goal >75% | Metrics JSON | Text report |
|-------------------------|------------|-----------|--------------|-------------|
| 77de8407 (prod, huddinge-v3) | **76.54%** | Yes | analyze_77de8407_downloads/metrics_*_77de8407.json | metrics_report_77de8407.txt |
| a4d33cab (analyze_latest)    | (check file) | — | analyze_latest/metrics_*_a4d33cab.json | metrics_report_a4d33cab.txt |

---

## How to (re)run metrics

```bash
# Single job (by plan ID)
./scripts/analytics/analyze_job.sh <plan_id> --input <input.json> [--out-dir DIR]

# From existing output file
./scripts/analytics/analyze_job.sh --output <path/to/output.json> --input <input.json> [--out-dir DIR]
```

Field efficiency is in the generated `metrics_*.json` as `field_efficiency_pct` (visit-span run).
