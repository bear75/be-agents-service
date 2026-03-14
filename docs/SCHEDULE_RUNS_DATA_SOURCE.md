# Schedule runs: what the page shows and where data lives

**Short answer:** The Schedules page **always** shows what’s in the **database** (`schedule_runs` in `.compound-state/agent-service.db`). It does not read run data directly from disk. “Refresh” **re-imports** from disk into the DB, so runs can reappear after “Clear all runs”.

---

## 1. What the page shows

- **Source:** The list is **always** from the SQLite table `schedule_runs` (DB file: `be-agents-service/.compound-state/agent-service.db`).
- **API:** `GET /api/schedule-runs` (and optional `?dataset=...`) returns rows from that table (plus augmented metrics from run folders when available).
- There is **no** separate “old data” source: if you see runs, they are in the DB.

---

## 2. What “Clear all runs” does

- **Clear** = `DELETE FROM schedule_runs` in that DB.
- Only the **database** is cleared. **Run folders on disk are not deleted.**

So after Clear:

- The list is empty because the DB is empty.
- The solve outputs (run folders) under `recurring-visits/.../huddinge-datasets/` are still there.

---

## 3. What “Refresh” does (why runs come back)

- **Refresh** calls `GET /api/schedule-runs/import-from-appcaire`.
- That endpoint **scans** a “huddinge-datasets” folder on disk and **inserts/updates** rows in `schedule_runs` from what it finds.

So:

- **Refresh** = “sync from disk into DB”, but **only from the `current` batch folder** (see §4).
- Old batches (e.g. 28-feb) are no longer imported, so they won’t reappear after Clear + Refresh.

---

## 4. Where solves are stored (on disk) — and what the dashboard uses

**Dashboard import uses only one batch folder:** `huddinge-datasets/current/`.  
Old batches (e.g. `28-feb`) are **not** imported, so they no longer reappear when you click Refresh.

The server finds the huddinge-datasets root in this order:

1. **Env:** `HUDDINGE_DATASETS_PATH` (if set and the path exists).
2. **Config:** `darwin.workspace.path` (or `darwin.path`) in `config/repos.yaml` → `../huddinge-datasets`.
3. **iCloud:** `~/Library/Mobile Documents/.../AgentWorkspace/huddinge-datasets`.
4. **Repo:** `be-agents-service/recurring-visits/huddinge-package/huddinge-datasets`.

**Import only reads:** `huddinge-datasets/current/` (or the folder name in `SCHEDULE_IMPORT_BATCH` if set).

**Structure:**

```
huddinge-datasets/
├── current/                   # ← only this batch is imported (new runs)
│   ├── manifest.json          # run ids + algorithm/strategy/hypothesis
│   ├── <run_id>/              # one run folder per solve
│   │   ├── input.json
│   │   ├── output.json
│   │   ├── metrics/           # metrics_*.json, continuity CSV, etc.
│   │   └── ...
│   └── ...
├── 28-feb/                    # old batch — not imported; safe to archive or delete
└── _archive/                  # optional: move old batches here
```

- **current** = the only batch scanned by Refresh. Put new run folders here.
- **28-feb** (and any other batch) = ignored by import. You can move them to `_archive/` or delete if you don’t need them.
- **manifest.json** in `current/` lists run ids and optional algorithm/strategy/hypothesis.

**Other folders (not used by the dashboard):**

- **recurring-visits/from-patch/** — payload JSONs (e.g. `payload_8a2318b9.json`). Not read by the Schedules page or import.
- **recurring-visits/huddinge-package/solve/** — mixed solve outputs (date-named dirs, input_*.json). Different layout; not used by the dashboard. Safe to archive or clean up separately.

---

## 5. Summary

| Action   | Effect |
|----------|--------|
| **Page load** | Shows runs from DB only. |
| **Clear all runs** | Empties `schedule_runs` in DB. Does **not** delete run folders on disk. |
| **Refresh** | Imports **only** from `huddinge-datasets/current/`. Old batches (e.g. 28-feb) are ignored. |

To have the dashboard show only new runs:

- Put new run folders (and their manifest entry) in **`huddinge-datasets/current/`**.
- Old batches like **28-feb** are no longer imported; you can move them to `_archive/` or delete them.
- **from-patch** and **solve** are not used by the dashboard; you can clean them up or keep them for other scripts.
