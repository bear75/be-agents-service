# Schedule Research Loop — How It Works

## In one sentence

The loop runs **one dataset** for up to **N iterations**. Each iteration: the **mathematician** proposes a strategy (e.g. pool size 5), the **specialist** runs one Timefold FSR solve for that dataset, results are evaluated and registered; the loop stops when goals are met or max iterations is reached.

---

## Flow (per iteration)

1. **Get research state** — `GET /api/schedule-runs/research/state?dataset=<name>` (iteration count, best metrics, history).
2. **Check goals** — If continuity ≤11, unassigned <1%, efficiency >70% → exit success.
3. **Get strategy** — Call **optimization-mathematician** agent with state + iteration; it returns one experiment (e.g. `pool5_baseline`, `pool8`, `from_patch_continuity`).
4. **Execute strategy** — Call **timefold-specialist** with that strategy. Specialist:
   - Loads FSR input for the dataset (e.g. `recurring-visits/data/huddinge-v3/input/input_huddinge-v3_FIXED.json`),
   - Submits to Timefold with default config `c522a20a-89c9-4a5b-aca2-46887a254ac7`,
   - Waits for solve, saves solution to `.../research_output/<experiment_id>/output.json`,
   - Optionally runs metrics/continuity scripts, then outputs one JSON line with `job_id`, `status`, `metrics`.
5. **Register run** — `POST /api/schedule-runs/register` with job id, strategy name, metrics (so the run appears in the dashboard).
6. **Evaluate** — Compare new metrics to best; set decision: keep / double_down / kill / continue.
7. **Update state** — `POST /api/schedule-runs/research/state` with e.g. `iteration_count` (and later best_* when wired).
8. **Sleep 2s**, next iteration.

---

## How many iterations and datasets?

- **Datasets:** Exactly **one** per run. You choose it: `./schedule-research-loop.sh <dataset> [max_iterations]`.
  - Example: `huddinge-v3` → all solves use `recurring-visits/data/huddinge-v3/input/...`.
- **Iterations:** Up to **max_iterations** (default **50**). Each iteration = one FSR solve.
  - So with default 50 you get up to 50 Timefold solves for that single dataset.
  - You can pass a smaller number, e.g. `./schedule-research-loop.sh huddinge-v3 3` for 3 iterations.

---

## What result output you can review

| What | Where |
|------|--------|
| **Run log (timestamps, strategies, decisions)** | `be-agent-service/logs/research/<dataset>_<YYYYMMDD_HHMMSS>.log` — printed to terminal and appended to this file. |
| **Research state (best metrics, history)** | API: `GET http://localhost:3010/api/schedule-runs/research/state?dataset=huddinge-v3` (or Dashboard Schedule Research UI if available). |
| **Registered runs (dashboard)** | API: `GET http://localhost:3010/api/schedule-runs?dataset=huddinge-v3` — list of runs with strategy, metrics, status. |
| **Per-experiment solution + logs** | `be-agent-service/recurring-visits/data/<dataset>/research_output/<experiment_id>/`: `output.json` (Timefold solution), `timefold_submission.log`, optional `metrics_*.json`. |
| **End-of-run summary** | Printed at end of script: “Best result so far” with continuity, efficiency, unassigned %, best job ID (from state). |

---

## Quick start

```bash
# From be-agent-service root
# 1. Start the API (so loop can read/write state and register runs)
yarn workspace server start
# Or in another terminal: PORT=3010 yarn workspace server dev

# 2. Run loop for dataset huddinge-v3 with 3 iterations (quick test)
./scripts/compound/schedule-research-loop.sh huddinge-v3 3
```

Requires `TIMEFOLD_API_KEY` (e.g. in `~/.config/caire/env`) so the specialist can submit to Timefold.
