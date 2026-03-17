# v3 Campaign Submissions

**Started**: 2026-03-13 18:21:47
**Baseline**: 4cdfce61-0d2d-46e0-9c16-674a7b9dab0f (avg continuity: 10.16)

| Variant | Route Plan ID | Status | Log |
|---------|---------------|--------|-----|
| baseline_data_final | cf407218-27c7-4603-b797-32e373b7e53c | SOLVING_COMPLETED | continuity/results/baseline_data_final/submit_stdout.txt |
| pool3_required | c1ea12a5-4507-4d9d-8d2c-3f70ac1e2685 | SOLVING_COMPLETED | continuity/results/pool3_required/submit_stdout.txt |
| pool5_required | d87e9a1a-ee5a-489a-bb07-f3c95cbe3b73 | SOLVING_COMPLETED | continuity/results/pool5_required/submit_stdout.txt |
| pool8_required | 5e55bf3a-9768-4ac8-9a98-d38b857926e4 | SOLVING_COMPLETED | continuity/results/pool8_required/submit_stdout.txt |

**Analyzed:** 2026-03-17 — full fetch + metrics + continuity + empty-shifts for all four jobs. Results: `be-agent-service/scripts/analytics/campaign_analysis/` (see SUMMARY.md).

**Pool10 weights campaign (submitted in parallel):** 2026-03-18

| Variant | Route plan ID | Status |
|---------|---------------|--------|
| pool10_required | 08e70f70-9113-4edc-9bbc-a2adef725950 | SOLVING_COMPLETED |
| pool10_preferred_w2 | 2f8ff28c-3ce5-4e00-9e8c-c09d50558d51 | SOLVING_COMPLETED |
| pool10_preferred_w10 | 2b2fef45-2e40-4dfd-b546-19ab0bcbef91 | SOLVING_COMPLETED |
| pool10_preferred_w20 | 67ab318e-e0d0-4982-9ae2-844d2e32635a | SOLVING_COMPLETED |
| pool10_wait_min | f2fac40b-f6d1-4103-97ee-d10cb22129da | SOLVING_COMPLETED |
| pool10_combo | 1391e3d9-aba6-45c9-8154-f0d609e64398 | SOLVING_COMPLETED |
| pool10_travel | b7ba5473-6701-4215-9487-28296c64a5e6 | SOLVING_COMPLETED |

*(ID ↔ variant may be reordered by parallel submit; verify via strategy in save dir or Timefold.)*

**Recommended:** **pool10_from_patch** — from-patch on pool10_required (long solve PT45M). Route plan ID: `4b5536f2-df02-431a-a7f4-d24fee45ed55`. Best balance: 1.4% unassigned, 72.88% field eff., 9.84 continuity.

| pool10_from_patch | 4b5536f2-df02-431a-a7f4-d24fee45ed55 | SOLVING_COMPLETED |

**Tight-goals campaign (unassigned <1%, eff >75%, continuity <8):** PT3H/PT15M. See `v3/continuity/TIGHT_GOALS_ANALYSIS.md`.

| pool8_required_3h | 76b02f06-a74f-4ff6-a95e-fbf87d6e6d07 | SOLVING_SCHEDULED |
| pool8_preferred_w10_3h | c52a3d44-0141-4b10-8f33-b4fc942e8f15 | SOLVING_SCHEDULED |
| pool10_eff_3h | 709eaa15-2bd6-47bd-b9b6-a7e1ad14ea18 | SOLVING_SCHEDULED |
| pool8_from_patch_3h | 769f8146-b250-43ad-ab03-201a2442612b | SOLVING_SCHEDULED |
| pool10_from_patch_v2_3h | 17db45c7-985b-43ef-9e8e-77a3352509f4 | SOLVING_SCHEDULED |

Fetch when completed: `scripts/analytics/campaign_analysis/fetch_tight_goals_campaign.sh`.

**Pool10 analyzed:** Fetched and metrics+continuity run; see `be-agent-service/scripts/analytics/campaign_analysis/SUMMARY.md`.

**Fetch + metrics + continuity:** Use **test tenant** API key. When status is `SOLVING_COMPLETED`, re-run fetch with `--metrics-dir` to run metrics and continuity. From `be-agent-service/recurring-visits/scripts`:

```bash
export TIMEFOLD_API_KEY=tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938
RES=../huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results
python3 fetch_timefold_solution.py cf407218-27c7-4603-b797-32e373b7e53c \
  --save "$RES/baseline_data_final/output.json" \
  --input ../huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json \
  --metrics-dir "$RES/baseline_data_final/metrics"
```
