# Analyze route plan 450e1b8b (from-patch vs origin)

Use the **existing** fetch script and command. No extra scripts needed.

## Fetch and see from-patch / origin

**Scripts:** `be-agent-service/recurring-visits/scripts/`  
**Command doc:** `beta-appcaire/.cursor/commands/fetchtimefoldsolution.md`

From `be-agent-service/recurring-visits/scripts`:

```bash
TIMEFOLD_API_KEY=tf_p_1c3007a4-be8f-4ebc-aa0b-8304d8709bb8 \
  python3 fetch_timefold_solution.py 450e1b8b-ee6c-48b2-985c-21ae4dc4bc4f \
  --save ../huddinge-package/continuity\ -3march/450e1b8b-output.json
```

`fetch_timefold_solution.py` prints **Parent ID** and **Origin ID** when present, and **Tags** (e.g. `system.type:from-patch`). The saved JSON has full `metadata` (id, parentId, originId, tags, solverStatus, score).

## From-patch vs origin (concepts)

| Term | Meaning |
|------|--------|
| **Origin** | First route plan in the chain (fresh solve). Its `originId` equals its own `id`. |
| **From-patch** | Run created by POSTing a patch to an existing plan. `parentId` = plan that was patched; `originId` = first solve in the chain (same as origin of parent). |

If tags include `system.type:from-patch`, this run is a from-patch; **parentId** is the plan you patched, **originId** is the origin. To inspect the origin plan, fetch it with the same script using `originId` as the route plan ID.

## Full workflow (fetch → metrics / from-patch chain)

See `fetchtimefoldsolution.md`: optional `--input` and `--metrics-dir`, and `run_fetch_trim_patch_fetch_unmetrics.py` for fetch → trim → patch → fetch patch solution. Route plan IDs: `scripts/timefold_route_plan_ids.md`.
