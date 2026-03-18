# Overnight campaigns: 10–15 runs for morning analysis

**Purpose:** Queue 10–15 campaigns overnight (PT3H/PT15M) so you can analyze results in the morning. All use **preferred** caregiver pools (no required); balance weights on **travel**, **wait**, and **preferred caregivers** for the best efficiency vs continuity trade-off.

**Principle:** In homecare, **preferred is better than required** for efficiency; required is a hard constraint and tends to increase unassigned. Larger employee pools with **preferred** vehicles + tuned weights give the ultimate balance.

**Future pool-building:** Clients/visits that are **close geographically** and have **aligned time windows** should share the same employee pool (as preferred). That implies zone- or cluster-based pool building (e.g. by area + time band) so nearby, time-aligned clients get overlapping preferred vehicles. Current overnight runs use per-client pools (pool8, pool10) as preferred with varied weights.

---

## Variants (15)

All runs: **PT3H** spentLimit, **PT15M** unimprovedSpentLimit. Weights: **P** = preferVisitVehicleMatchPreferredVehiclesWeight, **W** = minimizeWaitingTimeWeight, **T** = minimizeTravelTimeWeight.

| # | Strategy name       | Pool | P  | W | T | Rationale |
|---|---------------------|------|----|---|---|------------|
| 1 | pool10_p5_w3_t3    | 10   | 5  | 3 | 3 | Mild balance |
| 2 | pool10_p10_w3_t3   | 10   | 10 | 3 | 3 | Stronger preferred |
| 3 | pool10_p5_w5_t3   | 10   | 5  | 5 | 3 | Wait + preferred |
| 4 | pool10_p5_w3_t5   | 10   | 5  | 3 | 5 | Travel + preferred |
| 5 | pool10_p10_w5_t5   | 10   | 10 | 5 | 5 | Full balance |
| 6 | pool8_p5_w3_t3    | 8    | 5  | 3 | 3 | Tighter pool, mild weights |
| 7 | pool8_p10_w3_t3   | 8    | 10 | 3 | 3 | Tighter pool, stronger preferred |
| 8 | pool8_p5_w5_t5   | 8    | 5  | 5 | 5 | Tighter pool, full balance |
| 9 | pool10_p8_w4_t4   | 10   | 8  | 4 | 4 | Symmetric balance |
|10 | pool10_p15_w2_t5  | 10   | 15 | 2 | 5 | Preferred + travel focus |
|11 | pool8_p8_w4_t4   | 8    | 8  | 4 | 4 | Tighter, symmetric |
|12 | pool10_p3_w5_t5   | 10   | 3  | 5 | 5 | Efficiency (wait+travel) over continuity |
|13 | pool10_p20_w2_t2  | 10   | 20 | 2 | 2 | Strong preferred, light wait/travel |
|14 | pool8_p15_w2_t5   | 8    | 15 | 2 | 5 | Tighter pool, preferred + travel |
|15 | pool8_p10_w5_t5   | 8    | 10 | 5 | 5 | Tighter pool, full balance |

---

## How to run

From **be-agent-service** root:

```bash
./recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/run_overnight_campaigns.sh
```

- Generates 15 variant JSONs under `v3/continuity/variants/overnight/`.
- Submits each to Timefold **without --wait** so they queue; run before bed and analyze in the morning.
- Records strategy name and route plan ID in `v3/continuity/overnight_manifest.md`. If some IDs show "—" (e.g. from parallel output), get them from the save dir `v3/continuity/results/<strategy>/` or from the Timefold dashboard.

Requires: **TIMEFOLD_API_KEY**. Termination is PT3H/PT15M (override with env if needed).

---

## Morning: fetch and analyze

When all are **SOLVING_COMPLETED**:

```bash
# From be-agent-service root
./recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/fetch_overnight_campaigns.sh
python3 scripts/analytics/campaign_analysis/build_campaign_summary.py
```

Fetch script reads `overnight_manifest.md` and fetches each route plan ID into `campaign_analysis/<strategy_name>/` with metrics + continuity. Summary includes all overnight strategies; compare field efficiency (>80%), continuity (6–10), and unassigned; pick the best weight balance for production.
