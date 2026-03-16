# Schedule Research Loop — How It Works

## In one sentence

The loop runs **one dataset** for up to **N iterations**. Each iteration: the **mathematician** proposes a strategy (e.g. pool size 5), the **specialist** runs one Timefold FSR solve, results are evaluated and registered; the loop stops when **goals are met** or max iterations is reached.

---

## Goals

- **Quick-win (exit success):** continuity ≤11, unassigned <1%, **field efficiency** >70%.
- **Ultimate (stretch):** continuity ≤8, unassigned <1%, field efficiency >75%.

Efficiency is **field efficiency** (visit / (visit + travel), no wait, no idle) from `scripts/analytics/metrics.py`. The Timefold config (e.g. `c522a20a-89c9-4a5b-aca2-46887a254ac7`) already enforces a **3h max solve** per job; the script does not add a wall-clock cap.

---

## Flow (per iteration)

1. **Get research state** — `GET /api/schedule-runs/research/state?dataset=<name>` (iteration count, best metrics, goals).
2. **Check goals** — If continuity ≤11, unassigned <1%, field efficiency >70% → **exit success**.
3. **Get strategy** — Call **optimization-mathematician** with state + iteration; returns one experiment (e.g. `pool5_baseline`, `pool8`).
4. **Execute strategy** — Call **timefold-specialist**. Specialist:
   - Loads FSR input for the dataset (e.g. `recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json`, or `*_trimmed.json` if trim was used),
   - Submits to Timefold with config `c522a20a-89c9-4a5b-aca2-46887a254ac7` (3h max solve in config),
   - **Default:** waits for solve (`--wait`), saves solution to `.../research_output/<experiment_id>/output.json`, runs metrics, returns `job_id`, `status`, `metrics`.
   - **With `--no-wait`:** returns immediately with `job_id` and `status: "running"`; you can fetch output anytime with `python3 recurring-visits/scripts/submit_to_timefold.py fetch <plan_id> --save <dir>`.
5. **Register run** — `POST /api/schedule-runs/register` with job id, strategy, metrics (field + routing efficiency).
6. **Evaluate** — Compare new metrics to best (using field efficiency); decision: keep / double_down / kill / continue.
7. **Update state** — `POST /api/schedule-runs/research/state` with e.g. `iteration_count` (and best_* when improved).
8. **Sleep 2s**, next iteration.

---

## How many iterations and datasets?

- **Datasets:** **One** per run. You choose it: `./schedule-research-loop.sh <dataset> [max_iterations]`.
  - Example: `huddinge-v3` → all solves use `recurring-visits/data/huddinge-v3/input/...`.
- **Iterations:** Up to **max_iterations** (default **50**). Each iteration = one FSR solve (one strategy, one Timefold job).
  - Example: `./schedule-research-loop.sh huddinge-v3 20` → up to 20 solves for that dataset.
- **Parallel:** `PARALLEL_SOLVES` (default 4) is reserved for future use (multiple solves per round). Today the loop runs one solve per iteration.

---

## What result output you can review

| What | Where |
|------|--------|
| **Run log (timestamps, strategies, decisions)** | `be-agent-service/logs/research/<dataset>_<YYYYMMDD_HHMMSS>.log` — also printed to terminal. |
| **Research state (best metrics, goals)** | `GET http://localhost:3010/api/schedule-runs/research/state?dataset=huddinge-v3` (or Schedule Research UI if available). |
| **Registered runs** | `GET http://localhost:3010/api/schedule-runs?dataset=huddinge-v3` — list of runs with strategy, metrics, status. |
| **Per-experiment solution + metrics** | `be-agent-service/recurring-visits/data/<dataset>/research_output/<experiment_id>/`: `output.json`, `timefold_submission.log`, `metrics_*.json` (field_efficiency_pct, continuity, etc.). |
| **End-of-run summary** | Printed at end: “Best result so far” with continuity, efficiency (field), unassigned %, best job ID. |

---

## How to start the research

**Prerequisites**

- Agent server running (e.g. `http://localhost:3010`) so the loop can read/write research state and register runs.
- `TIMEFOLD_API_KEY` set (e.g. in `~/.config/caire/env` or in the shell).

**Run the loop**

```bash
cd ~/HomeCare/be-agent-service

# Default dataset (huddinge-v3), default max iterations (50)
./scripts/compound/schedule-research-loop.sh

# Dataset + max iterations (e.g. 20)
./scripts/compound/schedule-research-loop.sh huddinge-v3 20
```

**Optional env overrides**

```bash
# Quick test with fewer iterations
MAX_ITERATIONS=5 ./scripts/compound/schedule-research-loop.sh huddinge-v3

# Dry run (no real Timefold or register calls)
DRY_RUN=true ./scripts/compound/schedule-research-loop.sh huddinge-v3 3

# Trim shifts before loop (smaller/faster solves; specialist uses *_trimmed.json)
TRIM_SHIFTS_FROM_INPUT=1 ./scripts/compound/schedule-research-loop.sh huddinge-v3 10
```

**Start server (if needed)**

```bash
# From be-agent-service root
yarn workspace server start
# Or dev: PORT=3010 yarn workspace server dev
```

---

## Testing (does it work?)

**1. Dashboard (UI)**  
Open **http://localhost:3010/schedule-research**. You should see the Research page; use it to view state, trigger a run, or cancel. The server must be running on port 3010.

**2. Scripts (no browser)**  
- **API only (health + research state):**  
  `./scripts/openclaw/test-schedule-research.sh`  
- **Trigger from CLI:**  
  `./scripts/openclaw/test-schedule-research.sh --trigger`  
- **Dry-run loop (no Timefold, 1 iteration):**  
  `DRY_RUN=true MAX_ITERATIONS=1 ./scripts/compound/schedule-research-loop.sh huddinge-v3`  

**3. Real run (one solve)**  
`MAX_ITERATIONS=1 ./scripts/compound/schedule-research-loop.sh huddinge-v3`  
Requires `TIMEFOLD_API_KEY` and input at `recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json` (or `*_trimmed.json`).

---

## Input has too many shifts (e.g. 195 vehicles, 2600+ shifts)

The specialist uses **`*_trimmed.json`** if present, otherwise `*_FIXED.json`. To force fewer vehicles and shifts for all new runs:

**Option A – Trim existing input (no CSV):**  
From repo root:
```bash
./scripts/compound/prepare-huddinge-v3-input.sh 40 10
```
This trims `input_huddinge-v3_FIXED.json` to **40 vehicles, 10 shifts per vehicle** (~400 shifts) and writes `input_huddinge-v3_FIXED_trimmed.json`. The specialist will use it on the next run. You can pass other numbers: `./prepare-huddinge-v3-input.sh 50 8`.

**Option B – Regenerate from CSV with caps:**  
If you prefer to regenerate from the Huddinge CSV with caps (e.g. 40 vehicles, 8 shifts/vehicle), run csv_to_fsr.py with `--max-vehicles` and `--max-shifts-per-vehicle`, then copy the output to `recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json` or `*_trimmed.json`.
