# Testing the Schedule Optimization Dashboard and API

How to run and verify the new schedule optimization code: dashboard UI, schedule-runs API, and optimization loop.

**Relevant repos:** `be-agent-service` (dashboard + API + agents/scripts), `caire-platform/appcaire` (data and Timefold scripts). No `beta-appcaire` or `bryntum-prototype` involved.

**Research handoff (2026-02-28):** Deep research on ESS/FSR best practices and open source solvers was handed to the **Timefold agent team** for analysis and a “how to test” proposal. See **[TIMEFOLD_RESEARCH_HANDOFF.md](TIMEFOLD_RESEARCH_HANDOFF.md)** and the full report at repo root: `timefold-ess-fsr-best-practices.md`.

**Agents page:** The **Timefold Specialist** and **Optimization Mathematician** appear in the dashboard under **Agents** (team: Schedule optimization). They are used for Timefold optimization research: the specialist submits/monitors/cancels FSR jobs and records metrics; the mathematician analyses runs and proposes next strategies. If you don’t see them, run `sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-optimization-agents.sql`.

---

## Quick start: view Schedules and run agents / submit TF jobs

1. **Start the server (dashboard + API on port 3010)**  
   From repo root:
   ```bash
   cd ~/HomeCare/be-agents-service
   yarn dev
   ```
   Then open **http://localhost:3010/schedules**. You’ll see the pipeline, scatter plot, and runs table. Use **Refresh** to reload; click a run to cancel it if it’s queued/running.

2. **Optional: seed sample runs**  
   If the page is empty, seed the DB so you have data to inspect:
   ```bash
   sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-runs.sql
   ```
   Refresh http://localhost:3010/schedules.

3. **Run the optimization loop (agents + research)**  
   The **agents** (Timefold Specialist, Optimization Mathematician) are not started from the Schedules page — they are invoked by the **schedule-optimization loop** from the command line. The loop fetches strategies from the Optimization Mathematician and (in production) would dispatch FSR jobs via appcaire scripts.
   ```bash
   # Dry run: no real Timefold calls, only GET /api/schedule-runs and log flow
   ./scripts/compound/schedule-optimization-loop.sh huddinge-2w-expanded --dry-run
   ```
   For **real** TF job submission you need:
   - `TIMEFOLD_API_KEY` set (Timefold API).
   - `APPCAIRE_PATH` set to the appcaire repo (or `appcaire.path` in `config/repos.yaml`).
   - Run without `--dry-run`; actual submit is done by appcaire (e.g. `submit_to_timefold.py`). The loop then uses the dashboard API to list runs and cancel non‑promising ones (`DARWIN_API` defaults to http://localhost:3010).

4. **Summary**  
   | Goal | Action |
   |------|--------|
   | View Schedules at 3010 | `yarn dev` → open http://localhost:3010/schedules |
   | See sample runs | `sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-runs.sql` then refresh |
   | Run agents (research + loop) | `./scripts/compound/schedule-optimization-loop.sh huddinge-2w-expanded [--dry-run]` |
   | Submit real TF jobs | Use appcaire’s Timefold submit script; server must be running so loop/dashboard can list and cancel runs |

---

## 1. Prerequisites

- Node.js 20+ and Yarn (from repo root: `yarn install`)
- SQLite3 CLI (for seeding; optional if DB is fresh)

---

## 2. Database: ensure `schedule_runs` exists

The server creates the DB from `schema.sql` **only when** `.compound-state/agent-service.db` does not exist. If you already had a DB before the schedule feature was added, add the table and indexes manually.

**Option A – New DB (table will exist):**  
Remove the existing DB so the server re-initializes it on next start (this wipes all agent/session state):

```bash
cd ~/HomeCare/be-agent-service
rm -f .compound-state/agent-service.db
```

**Option B – Keep existing DB, add table:**  
If the DB already exists and you don’t want to wipe it, run the schedule block from `schema.sql`:

```bash
cd ~/HomeCare/be-agent-service
sqlite3 .compound-state/agent-service.db "
CREATE TABLE IF NOT EXISTS schedule_runs (
    id TEXT PRIMARY KEY,
    dataset TEXT NOT NULL,
    batch TEXT NOT NULL,
    algorithm TEXT NOT NULL,
    strategy TEXT NOT NULL,
    hypothesis TEXT,
    status TEXT NOT NULL DEFAULT 'queued'
        CHECK(status IN ('queued', 'running', 'completed', 'cancelled', 'failed')),
    decision TEXT CHECK(decision IN ('keep', 'kill', 'double_down', 'continue')),
    decision_reason TEXT,
    timefold_score TEXT,
    routing_efficiency_pct REAL,
    unassigned_visits INTEGER,
    total_visits INTEGER,
    unassigned_pct REAL,
    continuity_avg REAL,
    continuity_max INTEGER,
    continuity_over_target INTEGER,
    continuity_target INTEGER DEFAULT 11,
    submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME,
    completed_at DATETIME,
    cancelled_at DATETIME,
    duration_seconds INTEGER,
    output_path TEXT,
    notes TEXT,
    iteration INTEGER DEFAULT 1
);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_dataset ON schedule_runs(dataset);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_status ON schedule_runs(status);
CREATE INDEX IF NOT EXISTS idx_schedule_runs_submitted ON schedule_runs(submitted_at DESC);
"
```

---

## 3. Seed sample runs (optional but recommended)

To see the Schedules page with data (11 Huddinge 2w runs), seed the table:

```bash
cd ~/HomeCare/be-agent-service
sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-runs.sql
```

Verify:

```bash
sqlite3 .compound-state/agent-service.db "SELECT id, dataset, status, routing_efficiency_pct, unassigned_pct, continuity_avg FROM schedule_runs LIMIT 5;"
```

---

## 4. Start the server and dashboard

From repo root:

```bash
cd ~/HomeCare/be-agent-service
yarn dev
```

This builds the dashboard, copies assets into the server, and starts the unified server on **port 3010** with hot reload.

- **Dashboard:** http://localhost:3010/
- **Schedules page:** http://localhost:3010/schedules
- **Health:** http://localhost:3010/health

**Open from another device on the same WiFi:** The server binds to `0.0.0.0` so it accepts LAN connections. On the machine running the server, get its IP (e.g. `ifconfig | grep "inet "` on macOS, or `ip addr` on Linux). On the remote device (phone, laptop), open `http://<that-IP>:3010` (e.g. `http://192.168.1.42:3010`). Ensure the host firewall allows incoming TCP on port 3010 if needed.

---

## 5. What to test in the browser

1. **Navigation**  
   Open http://localhost:3010 → click **Schedules** in the nav (or go directly to http://localhost:3010/schedules).

2. **Schedules page**
   - **Dataset tabs:** Switch between datasets (e.g. Huddinge 2w). If you seeded, you should see runs.
   - **Pipeline board:** Queued / Running / Completed / Cancelled columns with run cards.
   - **Scatter plot:** X = continuity (avg), Y = unassigned %; points colored by routing efficiency; goal zone visible.
   - **Table:** List of runs with algorithm, status, metrics (efficiency, unassigned %, continuity).
   - **Run detail:** Click a run → detail panel with hypothesis, metrics, and “Cancel run” (for running/queued).

3. **Refresh**  
   Use the refresh control to reload runs from the API.

4. **Cancel (optional)**  
   If you have a run in `queued` or `running`, use “Cancel run” in the detail panel and confirm; the run should move to Cancelled and the list/board update after refresh.

---

## 6. Test the API directly

With the server running (port 3010):

**List all schedule runs**

```bash
curl -s http://localhost:3010/api/schedule-runs | jq .
```

**List runs for a dataset** (seed uses `huddinge-2w-expanded`)

```bash
curl -s "http://localhost:3010/api/schedule-runs?dataset=huddinge-2w-expanded" | jq .
```

**Cancel a run (replace RUN_ID with a real id, e.g. from seed)**

```bash
curl -s -X POST "http://localhost:3010/api/schedule-runs/RUN_ID/cancel" \
  -H "Content-Type: application/json" \
  -d '{"reason":"Testing cancel"}' | jq .
```

Expected: `success: true` and the run’s `status` becomes `cancelled`.

---

## 7. Test the optimization loop (dry run)

The loop script talks to the same API and expects the server to be running. Dry run only prints steps and does not submit real Timefold jobs:

```bash
cd ~/HomeCare/be-agent-service
./scripts/compound/schedule-optimization-loop.sh huddinge-2w-expanded --dry-run
```

You should see it:

- Resolving `APPCAIRE_PATH` from `config/repos.yaml` (appcaire entry).
- Calling `GET /api/schedule-runs?dataset=huddinge-2w-expanded` (or similar).
- Printing dry-run messages (no actual dispatch).

Full runs (without `--dry-run`) require:

- `config/repos.yaml` with a valid `appcaire.path` (e.g. `~/HomeCare/caire-platform/appcaire`).
- Timefold submission logic in appcaire (e.g. `submit_to_timefold.py`) and optional Darwin API `POST /api/schedule-runs` to create runs.

---

## 8. Quick checklist

| Step | Action |
|------|--------|
| 1 | Ensure `schedule_runs` table exists (new DB or run CREATE TABLE block). |
| 2 | Seed: `sqlite3 .compound-state/agent-service.db < scripts/seed-schedule-runs.sql` |
| 3 | Start: `yarn dev` (port 3010). |
| 4 | Open http://localhost:3010/schedules and check pipeline, scatter plot, table, detail panel. |
| 5 | Optional: `curl` list and cancel; run `schedule-optimization-loop.sh huddinge-2w-expanded --dry-run`. |

---

## 9. Troubleshooting

- **Schedules page empty / no runs**  
  Seed the DB (step 3) and refresh the page. Confirm with `curl http://localhost:3010/api/schedule-runs`.

- **404 on /schedules**  
  Ensure you ran `yarn dev` (or `yarn start`) so the latest dashboard build is served. The React app serves `/schedules` client-side; the server must serve `index.html` for that path.

- **Port in use**  
  Use another port: `PORT=3011 yarn dev`. Then open http://localhost:3011/schedules.

- **API returns 500 or “table not found”**  
  Add the `schedule_runs` table (step 2, Option B) and restart the server.

- **Loop script “DARWIN_API” or connection errors**  
  The loop defaults to `http://localhost:3010`. Start the server first or set `DARWIN_API` to your server URL.
