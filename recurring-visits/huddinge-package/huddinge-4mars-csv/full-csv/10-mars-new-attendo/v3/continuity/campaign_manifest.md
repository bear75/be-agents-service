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

**Fetch + metrics + continuity:** Use **test tenant** API key. When status is `SOLVING_COMPLETED`, re-run fetch with `--metrics-dir` to run metrics and continuity. From `be-agent-service/recurring-visits/scripts`:

```bash
export TIMEFOLD_API_KEY=tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938
RES=../huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/results
python3 fetch_timefold_solution.py cf407218-27c7-4603-b797-32e373b7e53c \
  --save "$RES/baseline_data_final/output.json" \
  --input ../huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json \
  --metrics-dir "$RES/baseline_data_final/metrics"
```
