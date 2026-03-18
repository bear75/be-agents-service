# v3 campaign – fetch & analyze all jobs

**Priorities:** Lower continuity = better (1 = ideal). Higher efficiency = better (100% = ideal). Unassigned low. Never cap continuity or efficiency.

| Variant | Plan ID | Assigned | Unassigned | Unassigned % | Field eff. | Continuity avg |
| --- | --- | --- | --- | --- | --- | --- |
| **baseline_data_final** | cf407218 | 7,562 | 91 | 1.2% | 65.88% | 21.32 |
| **pool3_required** | c1ea12a5 | 2,865 | 967 | 12.6% | 73.32% | 1.74 |
| **pool5_required** | d87e9a1a | 3,463 | 369 | 4.8% | 73.25% | 2.56 |
| **pool8_required** | 5e55bf3a | 3,670 | 162 | 2.1% | 73.82% | 3.69 |
| **pool10_required** | 08e70f70 | 7,524 | 129 | 1.7% | 72.83% | 9.78 |
| **pool10_preferred_w2** | 2f8ff28c | 7,534 | 119 | 1.6% | 71.32% | 11.88 |
| **pool10_preferred_w10** | 2b2fef45 | 7,515 | 138 | 1.8% | 67.52% | 16.26 |
| **pool10_preferred_w20** | 67ab318e | 6,281 | 1,372 | 17.9% | 69.42% | 3.51 |
| **pool10_wait_min** | f2fac40b | 6,269 | 1,384 | 18.1% | 69.25% | 3.50 |
| **pool10_combo** | 1391e3d9 | 6,275 | 1,378 | 18.0% | 69.40% | 3.49 |
| **pool10_travel** | b7ba5473 | 7,521 | 132 | 1.7% | 66.50% | 18.57 |
| **pool10_from_patch** | 4b5536f2 | 7,548 | 105 | 1.4% | 72.88% | 9.84 |
| **pool8_required_3h** | 76b02f06 | 3,770 | 62 | 0.8% | 73.43% | 8.90 |
| **pool8_preferred_w10_3h** | c52a3d44 | 3,694 | 138 | 1.8% | 76.52% | 3.70 |
| **pool10_eff_3h** | 709eaa15 | 6,379 | 1,274 | 16.6% | 70.00% | 3.45 |
| **pool8_from_patch_3h** | — | — | — | — | — | — |
| **pool10_from_patch_v2_3h** | 17db45c7 | 7,548 | 105 | 1.4% | 72.88% | 9.84 |
| **pool10_p5_w3_t3** | 53cbd25e | 7,566 | 87 | 1.1% | 66.12% | 20.38 |
| **pool10_p10_w3_t3** | — | — | — | — | — | — |
| **pool10_p5_w5_t3** | — | — | — | — | — | — |
| **pool10_p5_w3_t5** | — | — | — | — | — | — |
| **pool10_p10_w5_t5** | 97fae8b5 | 7,566 | 87 | 1.1% | 65.96% | 19.77 |
| **pool8_p5_w3_t3** | — | — | — | — | — | — |
| **pool8_p10_w3_t3** | — | — | — | — | — | — |
| **pool8_p5_w5_t5** | — | — | — | — | — | — |
| **pool10_p8_w4_t4** | — | — | — | — | — | — |
| **pool10_p15_w2_t5** | 4ded68f6 | 7,564 | 89 | 1.2% | 65.34% | 19.14 |
| **pool8_p8_w4_t4** | — | — | — | — | — | — |
| **pool10_p3_w5_t5** | cf34c075 | 7,566 | 87 | 1.1% | 66.19% | 20.58 |
| **pool10_p20_w2_t2** | 0e7b7300 | 7,566 | 87 | 1.1% | 64.69% | 19.35 |
| **pool8_p15_w2_t5** | — | — | — | — | — | — |
| **pool8_p10_w5_t5** | — | — | — | — | — | — |

## Best variants (highest eff, lowest continuity, lowest unassigned)

- **pool8_preferred_w10_3h**: 76.52% eff, 3.70 continuity, 1.8% unassigned
- **pool8_required**: 73.82% eff, 3.69 continuity, 2.1% unassigned
- **pool8_required_3h**: 73.43% eff, 8.90 continuity, 0.8% unassigned
- **pool3_required**: 73.32% eff, 1.74 continuity, 12.6% unassigned
- **pool5_required**: 73.25% eff, 2.56 continuity, 4.8% unassigned

**Notes:**
- Per-job outputs: `baseline_data_final/`, `pool3_required/`, etc. (output.json, metrics_*.json, continuity.csv).
- Re-fetch: `fetch_all_campaign_runs.sh`, `fetch_pool10_campaign_runs.sh`, `fetch_tight_goals_campaign.sh`, `fetch_overnight_campaigns.sh` (requires TIMEFOLD_API_KEY).
