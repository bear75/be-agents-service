# v3 campaign – fetch & analyze all jobs

**Goals:** Field efficiency **≥70%** (stretch 73%+), continuity avg ≤11, unassigned <5%.

| Variant | Plan ID | Assigned | Unassigned | Unassigned % | Field eff. | Continuity avg | ≤11 | Eff. ≥70% |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **baseline_data_final** | cf407218 | 7,562 | 91 | 1.2% | 65.88% | 21.32 | No | No |
| **pool3_required** | c1ea12a5 | 2,865 | 967 | 12.6% | 73.32% | 1.74 | Yes | Yes |
| **pool5_required** | d87e9a1a | 3,463 | 369 | 4.8% | 73.25% | 2.56 | Yes | Yes |
| **pool8_required** | 5e55bf3a | 3,670 | 162 | 2.1% | 73.82% | 3.69 | Yes | Yes |

**Analysis:**
- **Baseline:** No continuity constraints; 7,562 assigned, 65.88% field efficiency, 21.32 avg continuity. Many empty shifts → efficiency and continuity goals not met.
- **Pool 3 (required):** Best continuity (1.74 avg) and 73.32% field efficiency, but 967 unassigned (12.6%) — strict pool reduces coverage.
- **Pool 5 (required):** Balanced — 2.56 continuity, 73.25% efficiency, 4.8% unassigned. Meets both goals.
- **Pool 8 (required):** Best coverage (162 unassigned, 2.1%) and 73.82% efficiency; 3.69 continuity. Strong trade-off between continuity and assignment rate.

**Notes:**
- Per-job outputs: `baseline_data_final/`, `pool3_required/`, `pool5_required/`, `pool8_required/` (output.json, metrics_*.json, continuity.csv, empty_shifts.txt).
- To re-fetch: `./scripts/analytics/campaign_analysis/fetch_all_campaign_runs.sh` (requires TIMEFOLD_API_KEY).
