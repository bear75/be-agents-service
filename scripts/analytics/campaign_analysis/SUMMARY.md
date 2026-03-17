# v3 campaign – fetch & analyze all jobs

**Goals:** Field efficiency **≥70%** (stretch 73%+), continuity avg ≤11, unassigned <5%.

| Variant | Plan ID | Assigned | Unassigned | Unassigned % | Field eff. | Continuity avg | ≤11 | Eff. ≥70% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **baseline_data_final** | cf407218 | 7,562 | 91 | 1.2% | 65.88% | 21.32 | No | No |
| **pool3_required** | c1ea12a5 | 2,865 | 967 | 12.6% | 73.32% | 1.74 | Yes | Yes |
| **pool5_required** | d87e9a1a | 3,463 | 369 | 4.8% | 73.25% | 2.56 | Yes | Yes |
| **pool8_required** | 5e55bf3a | 3,670 | 162 | 2.1% | 73.82% | 3.69 | Yes | Yes |
| **pool10_required** | 08e70f70 | 7,524 | 129 | 1.7% | 72.83% | 9.78 | Yes | Yes |
| **pool10_preferred_w2** | 2f8ff28c | 7,534 | 119 | 1.6% | 71.32% | 11.88 | No | Yes |
| **pool10_preferred_w10** | 2b2fef45 | 7,515 | 138 | 1.8% | 67.52% | 16.26 | No | No |
| **pool10_preferred_w20** | 67ab318e | 6,281 | 1,372 | 17.9% | 69.42% | 3.51 | Yes | No |
| **pool10_wait_min** | f2fac40b | 6,269 | 1,384 | 18.1% | 69.25% | 3.50 | Yes | No |
| **pool10_combo** | 1391e3d9 | 6,275 | 1,378 | 18.0% | 69.40% | 3.49 | Yes | No |
| **pool10_travel** | b7ba5473 | 7,521 | 132 | 1.7% | 66.50% | 18.57 | No | No |
| **pool10_from_patch** | 4b5536f2 | 7,548 | 105 | 1.4% | 72.88% | 9.84 | Yes | Yes |

**Recommended variant:** **pool10_from_patch** (from-patch on pool10_required with long solve). Best coverage (1.4% unassigned, 105), 72.88% field eff., 9.84 continuity; all goals met.

**Pool 10 from-patch:** Run `v3/continuity/run_pool10_from_patch.sh` (runConfiguration.termination: spentLimit=PT3H, unimprovedSpentLimit=PT15M). New route plan ID: 4b5536f2-df02-431a-a7f4-d24fee45ed55.

**Notes:**
- Per-job outputs: `baseline_data_final/`, `pool3_required/`, `pool5_required/`, `pool8_required/`, `pool10_*`, `pool10_from_patch/` (output.json, metrics_*.json, continuity.csv).
- Re-fetch: `fetch_all_campaign_runs.sh` (original 4); `fetch_pool10_campaign_runs.sh` (Pool 10). Requires TIMEFOLD_API_KEY.
