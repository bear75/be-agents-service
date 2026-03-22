# v3/22 campaign — submitted route plans (Timefold)

Recorded from dashboard export **2026-03-22**. Jobs show **Configuration profile: huddinge-wait-min** in the UI (not `Caire_prod_pilot_20min` — confirm in Timefold which profile ID was used at submit time).

## Why only ~10 jobs were accepted (concurrent capacity)

Timefold limits **total concurrent solver capacity** (often described as ~**50** slots). Each solve’s `runConfiguration.maxThreadCount` **reserves multiple slots** (typically **one slot per thread**). So **4 threads per job ≈ 4 slots** → only about **10–12** large jobs can run at once; extra submits stay **queued** or return **429** until capacity frees.

**Fix for future campaigns:** `v3_22_optimization_campaign.py` defaults to **`--max-thread-count 2`** (balance of speed vs queue). Use **`--max-thread-count 1`** if you need all **16** jobs to fit concurrent capacity more easily; **`4`** only when fewer parallel runs are OK.

Each prepared JSON also sets **`config.model.overrides`** (custom soft weights per profile: preferred vehicles, travel, wait, time windows, etc.) on top of the Timefold configuration profile.

## Validation (accepted dataset)

Rows that show **vehicles / shifts / visits** counts confirm the API accepted the payload:

| Field | Value (trimmed variants) |
|-------|----------------------------|
| Vehicles | 41 |
| Vehicle shifts | 548 |
| Visits | 3,840 |
| Visit groups | 162 |
| Visit dependencies | 2,194 |
| Movable visits | 566 |

This matches the **trimmed** campaign inputs (26 empty shifts removed from baseline 574).

## Route plan IDs (from your list)

| Strategy name | Route plan ID | Notes |
|---------------|---------------|--------|
| v3/22 trimmed — efficiency-first | `7fac0833-34e5-4c99-b453-474acc17189b` | Score/medium/soft populated |
| v3/22 trimmed — balanced | `3a91c23b-3da9-47a5-88be-f84433ba7310` | Completed row |
| v3/22 trimmed — continuity-heavy | `9374ba87-577e-4359-8cae-39db3f5153ca` | Completed row |
| v3/22 trimmed — combo | `9236a190-7603-4537-8574-05109bbfffff` | Submitted; metrics pending in paste |
| v3/22 pool8 — efficiency-first | `657aa402-914d-4390-9b54-fd0ad24d1861` | Submitted |
| v3/22 pool8 — balanced | `fbf04d7c-68bc-42fa-81fa-9823811628a0` | Submitted |
| v3/22 pool8 — continuity-heavy | `8b07f34c-9ae0-4393-9972-3e5eebaa86b4` | Submitted |
| v3/22 pool8 — combo | `25b51d75-ba79-4556-a503-c28f3682ff2f` | Submitted |
| v3/22 pool12 — efficiency-first | `f5bc4ea8-a3e7-43da-84b9-964672443d92` | Submitted |
| v3/22 pool12 — balanced | `fb58c0b8-a2fb-4cd1-9b56-d5b51a1ed9bd` | Submitted |

**Incomplete in paste:** `pool12` — continuity-heavy, combo; all **pool8_extra** variants; trailing ID `e06e4bf6-d825-4523-b51d-e5d7340f291d` (name cut off). Add those rows here when visible.

## Status interpretation

- **`--` in KPI columns:** solver not finished yet (queued / running), or UI not refreshed.
- **Filled medium/soft/travel/unassigned:** `SOLVING_COMPLETED` (or intermediate) for that plan — **valid solution artifact**.
- **Completed timestamps empty** on some rows: still solving or dashboard lag.

## Fetch when done

```bash
cd /path/to/be-agent-service
python3 scripts/timefold/fetch.py <ROUTE_PLAN_ID> \
  --save recurring-visits/huddinge-package/.../campaign_20260322/results/<strategy>/output.json \
  --metrics-dir recurring-visits/huddinge-package/.../campaign_20260322/results/<strategy>/metrics
```

Or batch: `scripts/campaigns/v3_22_fetch_campaign_results.py` after `campaign_manifest.json` lists all IDs.
