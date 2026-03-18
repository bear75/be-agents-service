# Tight goals: field efficiency >80%, continuity 6–10, unassigned manually manageable

**Target:** Field efficiency **>80%**; continuity avg **6–10**; unassigned visits kept low but **some can be manually managed**.

---

## 1. Current results vs target

| Metric        | Target      | Best current                    | Gap / note |
|---------------|-------------|----------------------------------|------------|
| Field eff.    | **>80%**    | 73.82% (pool8_required)         | +6+ pp; focus of new runs    |
| Continuity    | **6–10**    | 9.78–9.84 (pool10); 3.69 (pool8)| pool10 in range; pool8 below (tighter) |
| Unassigned    | Low; manual OK | 1.4% (pool10_from_patch, 105)  | Some unassigned acceptable for manual handling |

**Observation:** We should be able to get **over 80%** efficiency and continuity **between 6–10**. Pool8 has best efficiency (73.82%) and very tight continuity (3.69). Pool10 sits in the 6–10 continuity band but efficiency is 72–73%. New strategies (PT3H solves, from-patch, eff weights) aim to push efficiency toward 80%+ while keeping continuity in 6–10.

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

After completion: run `fetch_tight_goals_campaign.sh`, then `build_campaign_summary.py`. **Success:** eff >80%, continuity 6–10; some unassigned can be manually managed.

---

## 4. How to run

From **be-agent-service** root:

```bash
./recurring-visits/huddinge-package/huddinge-4mars-csv/full-csv/10-mars-new-attendo/v3/continuity/run_tight_goals_campaign.sh
```

Requires: `TIMEFOLD_API_KEY`. Optional: `TIMEFOLD_CAMPAIGN_SPENT_LIMIT=PT3H`, `TIMEFOLD_CAMPAIGN_UNIMPROVED=PT15M`.
