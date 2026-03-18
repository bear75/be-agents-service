# Pool8 preferred baseline campaign

**Baseline:** pool8_preferred_w10_3h — 76.52% eff, 3.70 continuity, 1.8% unassigned (best so far).

**Goal:** Double down on this config. New variants start from pool8_preferred + preferVisitVehicleMatchPreferredVehiclesWeight=10 + PT3H/PT15M termination.

## Variants

| Strategy | Description | Input |
|----------|-------------|-------|
| pool8_preferred_w15_3h | Preferred weight 15 (stronger continuity) | input_pool8_preferred.json + overrides |
| pool8_preferred_w20_3h | Preferred weight 20 | input_pool8_preferred.json + overrides |
| pool8_preferred_w10_eff_3h | Add travel+wait weights (5,5) for efficiency | input_pool8_preferred.json + overrides |
| pool8_preferred_w10_from_patch_3h | From-patch from pool8_preferred_w10_3h output | patch from c52a3d44 output |

## Run

```bash
cd ~/HomeCare/be-agent-service
./recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/run_pool8_preferred_baseline_campaign.sh
```

## Fetch

After runs complete, update `pool8_preferred_baseline_manifest.md` with route plan IDs from submit output or Timefold dashboard, then:

```bash
./scripts/analytics/campaign_analysis/fetch_pool8_preferred_baseline.sh
python3 scripts/analytics/campaign_analysis/build_campaign_summary.py
```

Requires TIMEFOLD_API_KEY.
