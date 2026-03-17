# All jobs – fetch, metrics, and analysis

**Generated:** 2026-03-17  
**Goal:** Field efficiency (Reseffektivitet) **>75%**, continuity avg ≤11, unassigned <1%.

All jobs below were fetched (or used local output) and run through `analyze_job.sh`: metrics (visit-span + full), continuity report, empty-shifts analysis.  
Report locations: `scripts/analytics/METRIC_REPORTS_INDEX.md`.

---

## Summary table

| Job | Plan ID | Input | Assigned | Unassigned | Unassigned % | Field eff. | Continuity avg | Goal >75% | Goal ≤11 | Goal unassigned <1% |
|-----|---------|-------|----------|------------|--------------|------------|----------------|-----------|----------|----------------------|
| **baseline_data_final** | cf407218 | v3 (7653) | 7 562 | 91 | 1.2% | **65.88%** | 21.32 | No | No | Yes |
| **pool3_required** | c1ea12a5 | v3 (7653) | 2 865 | 967 | 25.2% | **73.32%** | **1.74** | No | Yes | No |
| **pool5_required** | d87e9a1a | v3 (7653) | 3 463 | 369 | 9.6% | **73.25%** | **2.56** | No | Yes | No |
| **pool8_required** | 5e55bf3a | v3 (7653) | 3 670 | 162 | 4.2% | **73.82%** | **3.69** | No | Yes | No |
| **pool10_required** | c6040e8b | v3 (7653) | 6 380 | 1 273 | 16.6% | **69.89%** | — | No | — | No |
| **pool8_preferred** | ebbd8f66 | v3 (3832)* | 3 760 | 72 | 1.9% | **72.81%** | — | No | — | No |
| **job_70ac29c5** (17 Mar) | 70ac29c5 | tf17march (4126) | 3 744 | 382 | 9.3% | **73.85%** | **10.30** | No | Yes | No |

\* pool8_preferred: 41 vehicles, 3832 visits (subset input).

**Findings:**
- **No job reaches >75%** field efficiency on the v3/tf17march datasets. Best: pool8_required and job_70ac29c5 at ~73.8%.
- **Best continuity:** pool3 (1.74) and pool5 (2.56), but with high unassigned.
- **Best coverage (low unassigned):** baseline (1.2%), pool8_preferred (1.9%), then pool8_required (4.2%).
- **pool10_required** (69.89%) is worse than pool8 on efficiency and has 16.6% unassigned; many empty shifts (2974) and high wait.

---

## Per-job outputs (paths under `campaign_analysis/`)

| Job | output.json | metrics (visit-span) | continuity.csv | empty_shifts.txt |
|-----|-------------|----------------------|----------------|------------------|
| baseline_data_final | ✓ | metrics_*_cf407218.json | ✓ | ✓ |
| pool3_required | ✓ | metrics_*_c1ea12a5.json | ✓ | ✓ |
| pool5_required | ✓ | metrics_*_d87e9a1a.json | ✓ | ✓ |
| pool8_required | ✓ | metrics_*_5e55bf3a.json | ✓ | ✓ |
| pool10_required | ✓ | metrics_*_c6040e8b.json | — | ✓ |
| pool8_preferred | ✓ | metrics_*_ebbd8f66.json | — | ✓ |
| job_70ac29c5 | (local file) | metrics_*_70ac29c5.json | ✓ | ✓ |

---

## How to re-run metrics for one job

From **be-agent-service**:

```bash
export TIMEFOLD_API_KEY="tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938"   # test tenant

# By plan ID (fetch + metrics + continuity + empty-shifts)
./scripts/analytics/analyze_job.sh <plan_id> \
  --input recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json \
  --out-dir scripts/analytics/campaign_analysis/<variant>

# From local output (e.g. 17 March export)
./scripts/analytics/analyze_job.sh --output "path/to/output.json" --input "path/to/input.json" \
  --out-dir scripts/analytics/campaign_analysis/job_<id>
```
