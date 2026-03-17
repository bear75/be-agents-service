# Tight goals: unassigned <1%, field efficiency >75%, continuity <8

**Target:** Unassigned **<1%** (<76 of 7,653), field efficiency **>75%**, continuity avg **<8**.

---

## 1. Current results vs target

| Metric        | Target   | Best current                    | Gap                          |
|---------------|----------|----------------------------------|------------------------------|
| Unassigned %  | <1%      | 1.4% (pool10_from_patch, 105)   | Need ~30 more assigned       |
| Field eff.    | >75%     | 73.82% (pool8_required)         | +1.2–2 pp                    |
| Continuity    | <8       | 9.78–9.84 (pool10); 3.69 (pool8)| pool10 over; pool8 already OK|

**Observation:** Pool8 has best efficiency (73.82%) and best continuity (3.69) but 162 unassigned (2.1%). Pool10 has fewest unassigned (105–129) but continuity ~9.8 and efficiency 72–73%. No single run yet meets all three tight goals.

---

## 2. Strategy hypotheses

| Strategy               | Rationale                                                                 | Expectation |
|------------------------|----------------------------------------------------------------------------|-------------|
| **pool8_required PT3H**| Long solve may assign more of the 162; keep eff and continuity.             | Unassigned ↓, eff/cont similar |
| **pool8_from_patch**   | From-patch on pool8 (pin, trim, remove empty) with PT3H.                   | Fewer empty shifts, possibly more assigned |
| **pool10_from_patch_v2** | Second from-patch on best solution (4b5536f2) with PT3H.                | Slight unassigned ↓, eff ↑ |
| **pool10_eff**         | Pool10 required + minimizeTravelTimeWeight=5 + minimizeWaitingTimeWeight=5.| Push efficiency toward 75%. |
| **pool8_preferred_w10**| Pool8 as *preferred* (soft) with weight 10; PT3H.                          | Fewer unassigned than pool8 required, continuity still <8. |

---

## 3. Runs submitted (tight-goals campaign)

All runs use **runConfiguration.termination**: spentLimit=**PT3H**, unimprovedSpentLimit=**PT15M**.

| Variant                | Type        | Seed / input                         | Route plan ID |
|------------------------|------------|--------------------------------------|---------------|
| pool8_required_3h      | solve      | variants/input_pool8_required.json   | 76b02f06-a74f-4ff6-a95e-fbf87d6e6d07 |
| pool8_from_patch_3h    | from-patch | pool8_required (5e55bf3a)            | 769f8146-b250-43ad-ab03-201a2442612b |
| pool10_from_patch_v2_3h | from-patch | pool10_from_patch (4b5536f2)       | 17db45c7-985b-43ef-9e8e-77a3352509f4 |
| pool10_eff_3h          | solve      | pool10 required + travel 5 + wait 5  | 709eaa15-2bd6-47bd-b9b6-a7e1ad14ea18 |
| pool8_preferred_w10_3h | solve      | variants/input_pool8_preferred.json + overrides | c52a3d44-0141-4b10-8f33-b4fc942e8f15 |

After completion: run `scripts/analytics/campaign_analysis/fetch_tight_goals_campaign.sh` (create it to fetch these 5 IDs into campaign_analysis/<variant>), then `build_campaign_summary.py` to regenerate SUMMARY.md. VARIANTS already includes these five.

---

## 4. How to run

From **be-agent-service** root:

```bash
./recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/run_tight_goals_campaign.sh
```

Requires: `TIMEFOLD_API_KEY`. Optional: `TIMEFOLD_CAMPAIGN_SPENT_LIMIT=PT3H`, `TIMEFOLD_CAMPAIGN_UNIMPROVED=PT15M`.
