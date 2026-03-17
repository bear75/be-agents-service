# Efficiency runs (goal >75% field efficiency)

| Variant | Route Plan ID | Status |
|---------|---------------|--------|
| pool10_required | c6040e8b-86af-45af-a062-81d1c46494f6 | SUBMITTED |
| pool8_preferred | ebbd8f66-5ee7-48eb-8f50-8b3e0cc8f828 | SUBMITTED |

After SOLVING_COMPLETED, run (from be-agent-service, with test tenant key):

```bash
export TIMEFOLD_API_KEY="tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938"

./scripts/analytics/analyze_job.sh c6040e8b-86af-45af-a062-81d1c46494f6 \
  --input recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json \
  --out-dir scripts/analytics/campaign_analysis/pool10_required

./scripts/analytics/analyze_job.sh ebbd8f66-5ee7-48eb-8f50-8b3e0cc8f828 \
  --input recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/input_v3_from_Data_final.json \
  --out-dir scripts/analytics/campaign_analysis/pool8_preferred
```

Then check `field_efficiency_pct` in each `metrics_*.json`; goal is **>75%**.
