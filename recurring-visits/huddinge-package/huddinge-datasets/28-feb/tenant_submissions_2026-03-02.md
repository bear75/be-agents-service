# Timefold tenant submissions — 2026-03-02

**Tenant API key:** `tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938`  
**Configuration ID:** `68b16a3f-b61c-47f7-a8e4-b85a0446ee22`

All 11 datasets from `28-feb` submitted in parallel (no `--wait`). Jobs are solving on Timefold.

| Dataset ID | Route plan ID | Strategy (from manifest) |
|------------|----------------|---------------------------|
| 203cf1d6 | `6a29a524-f41c-4263-a969-5e0fb76742f2` | Continuity pool (first-run style) |
| 5ff7929f | `bdbc1498-e360-4b1e-b562-c61e918079e3` | Base solve, no continuity constraint |
| 2b36ebdb | `b04ffa3e-4b2f-424d-addb-fda9c45bbb7a` | Continuity pool variant |
| 41ce610c | `d64a392a-a695-45df-aaef-3607fe557772` | Manual continuity pools (per-client cross-type) |
| 48b04930 | `5ee555ba-3796-4a3f-a5fe-1a817feead6e` | Tighter continuity pools |
| 7c002442 | `7571cf9b-d3cc-499b-8a18-7bf0249beafe` | from-patch trim-empty (variant) |
| 82a338b9 | `3be2fbc6-bdcb-46a0-b11e-00ba430476af` | from-patch trim-empty shifts |
| 8a2318b9 | `19dd051a-a5b1-4296-9785-7fd4c0e4135a` | from-patch trim-empty (variant) |
| a9664f39 | `6b2c9b12-4098-4ef5-90a1-2c21823974cc` | Area / first-run pool |
| b69e582b | `fd9c5c1c-e7fc-493b-94b2-5df25bf1aa93` | from-patch trim-empty (variant) |
| b8e58647 | `a768bb0a-6e1e-445b-abdd-f1304e7fab9b` | Continuity pool |

**Check status (metadata only):**
```bash
curl -s -H "X-API-KEY: tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" \
  "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans/<ROUTE_PLAN_ID>/metadata"
```

**Fetch full solution when SOLVING_COMPLETED:**
```bash
curl -s -H "X-API-KEY: tf_p_96b5507b-57be-4ab6-b0a6-08a9d3372938" \
  "https://app.timefold.ai/api/models/field-service-routing/v1/route-plans/<ROUTE_PLAN_ID>"
```

Darwin register warnings (localhost:3010) are expected when the Darwin dashboard is not running; Timefold submissions completed successfully.
