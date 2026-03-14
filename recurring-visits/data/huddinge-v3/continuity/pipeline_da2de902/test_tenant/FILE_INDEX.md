# test_tenant — one folder per test

**Base path:** `be-agent-service/recurring-visits/huddinge-package/continuity -3march/pipeline_da2de902/test_tenant/`

**5 tests total.** Each test has its own folder; inside: `input.json` or `payload.json`, `output.json`, `continuity.csv`, `metrics/` (report + JSON).

---

## Test folders (datasets)

| # | Folder | Description | Contents |
|---|--------|-------------|----------|
| 1 | **preferred_688faece/** | Preferred (pool 15, soft) | input.json, output.json, continuity.csv, metrics/ |
| 2 | **wait_min_a4be8810/** | Wait-min (pool 15, required) | input.json, output.json, continuity.csv, metrics/ |
| 3 | **combo_8e07450d/** | Combo (preferred + wait-min) | input.json, output.json, continuity.csv, metrics/ |
| 4 | **from_patch_preferred_963c3aa9/** | From-patch preferred (trimmed shifts) | payload.json, route_plan_id.txt, output.json, continuity.csv, metrics/ |
| 5 | **from_patch_combo/** | From-patch combo (trimmed shifts) | payload.json, route_plan_id.txt, input.json, output.json, continuity.csv, metrics/ |

---

## Root files

- **route_plan_ids.txt** — all route plan IDs
- **FILE_INDEX.md** (this file)
- **ANALYSIS_VS_GOAL.md** — metrics/continuity vs brainstorm goal
- **README.md** — how to run fetch, metrics, continuity, from-patch
- **ANALYSIS_combo_vs_wait_min.md** — combo vs wait-min

---

## Archived

- **test_tenant/_archive/** — one-day input, pool25 inputs, duplicate from_patch output
- See **../FOLDERS_AND_ARCHIVE.md** for parent-level archive
