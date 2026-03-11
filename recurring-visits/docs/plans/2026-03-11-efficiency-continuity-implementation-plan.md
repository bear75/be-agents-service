# Implementation plan: Efficiency and continuity optimization (Approach A + B)

**Source:** [2026-03-11-efficiency-continuity-optimization brainstorm](../brainstorms/2026-03-11-efficiency-continuity-optimization-brainstorm.md)  
**Resolved:** CCI in scripts/metrics first (dashboard later); pool size 5–10; ESS later; run Approach A and B in parallel with subagents.

---

## Overview

| Track | Scope | Owner (subagent) |
|-------|--------|------------------|
| **A** | Weight and pool tuning + CCI in scripts/metrics | timefold-specialist / script-focused agent |
| **B** | ESS→FSR integration design + orchestration layer | timefold-specialist / integration-focused agent |

Both tracks produce artifacts in `recurring-visits/` (scripts, docs, optional `optimization-research-scripts/`). Dashboard changes are out of scope for this plan; user will upload optimized JSONs and show key metrics manually for now.

---

## Track A: Weight and pool tuning + CCI

### A1. Add CCI to continuity scripts and metrics

**Goal:** Report Continuity of Care Index (or simplified CCI) alongside unique-count in scripts so we can compare strategies scientifically.

**Tasks:**

1. **Define CCI formula** (docs)
   - Document in `docs/CONTINUITY_METRICS.md`: unique-count (current KOLADA) and CCI. CCI = sum over caregivers of (n_i / N)^2 where n_i = visits from caregiver i, N = total visits for client; higher = better. Simplified option: proportion of visits from top-1 (primary) caregiver.
   - Decide which variant to implement first (full CCI vs primary-caregiver proportion).

2. **Implement CCI in `continuity_report.py`**
   - From existing per-person assignment data (visit → vehicle), compute per client: (a) unique_count (current), (b) CCI or primary proportion.
   - Add `--cci` flag (default on) to output CCI column; add summary line (e.g. average CCI, average unique-count).
   - Output: same CSV plus optional `continuity_cci.csv` or extra columns in existing report.

3. **Add CCI to metrics pipeline**
   - Ensure `metrics.py` output (or a small wrapper) can be joined with continuity report so one summary file contains: efficiency (wait, travel), unassigned, unique_count, CCI. Option: script `run_metrics_and_continuity.py` that runs both and writes `run_summary_<id>.json` / `run_summary_<id>.md`.

**Acceptance:** Running `continuity_report.py` on a solution outputs both unique-count and CCI (or primary proportion); doc describes the metric.

**Files:** `recurring-visits/scripts/continuity_report.py`, `recurring-visits/docs/CONTINUITY_METRICS.md`, optionally `recurring-visits/scripts/run_metrics_and_continuity.py`.

---

### A2. Pool size 5–10 and variant generation

**Goal:** Support pool caps 5–10 (max 10); run campaigns with multiple pool sizes and weight variants.

**Tasks:**

1. **Use existing `--max-per-client`**
   - `build_continuity_pools.py` already has `--max-per-client` (default 15). No code change required; document and use 5, 8, 10 in campaign commands.

2. **Generate variants for pool sizes 5, 8, 10**
   - For each pool size: run `build_continuity_pools.py --source first-run ... --max-per-client 5|8|10`, then patch FSR input, then run `prepare_continuity_test_variants.py` to get preferred/wait-min/combo (and optionally preferred weight 10, 20).
   - Add a small script or shell workflow: `run_pool_campaign.sh` or `prepare_pool_variants.py` that, given base input/output, produces variant inputs for max_per_client in {5, 8, 10} and writes to `continuity/variants/pool_5/`, `pool_8/`, `pool_10/` (or single dir with naming like `input_preferred_weight2_pool8.json`).

3. **Document campaign matrix**
   - In `docs/CONTINUITY_STRATEGIES.md` or new `docs/plans/2026-03-11-campaign-matrix.md`: table of (pool size, weight set, strategy name) and how to run each. Example: pool 8, preferred weight 10, combo; pool 10, required vehicles, no weight override.

**Acceptance:** User (or subagent) can run first-run → build pools with --max-per-client 5/8/10 → patch input → generate preferred/combo variants → submit and compare.

**Files:** `recurring-visits/scripts/` (new helper script or shell), `recurring-visits/docs/` (campaign matrix).

---

### A3. Run Pareto-style campaign and compare

**Goal:** Execute a small set of strategies (e.g. pool 8 and 10; preferred 2, 10, 20; combo; required with pool 8) and record efficiency vs continuity (unique-count and CCI).

**Tasks:**

1. **Baseline**
   - Use existing v2 input (e.g. Huddinge 2-week) and existing first-run output. Build pools with --max-per-client 8 and 10; produce patched inputs.

2. **Submit strategies**
   - Submit 6–10 variants (e.g. preferred_2_pool8, preferred_10_pool8, preferred_20_pool8, combo_pool8, required_pool8; same for pool10). Use `submit_to_timefold.py solve` without --configuration-id (payload config only).

3. **When solves complete: fetch, metrics, continuity**
   - For each route_plan_id: `fetch_timefold_solution.py <id> --save output_<strategy>.json`; run `metrics.py` (wait efficiency, unassigned); run `continuity_report.py` (unique_count, CCI).

4. **Summary report**
   - One markdown or JSON summarizing: strategy, unassigned, wait_efficiency_pct, continuity_avg (unique), CCI_avg. Optionally plot or table for Pareto (efficiency vs continuity).

**Acceptance:** At least one campaign run with 5–10 variants; summary table with efficiency and continuity (unique + CCI) per strategy.

**Files:** `recurring-visits/huddinge-package/.../v2/continuity/` or `optimization-research-scripts/`; summary in `docs/` or same folder.

---

## Track B: ESS→FSR integration design and orchestration

**Note:** Full ESS API integration is “later.” This track delivers design + an orchestration layer that can accept roster/zone input (file or stub) and produce FSR input with preferred/required vehicles, so when ESS is added we only plug in the ESS client.

### B1. Design ESS→FSR data flow

**Goal:** Document how roster/zone output from ESS (or manual/stub) maps to FSR input (preferred/required vehicles per visit).

**Tasks:**

1. **Data flow doc**
   - Create `docs/ESS_FSR_INTEGRATION_DESIGN.md`: (a) ESS output shape (e.g. assignments of caregiver_id to zone or to client_ids per day); (b) FSR input: for each visit, set preferredVehicles or requiredVehicles from that assignment; (c) iteration: FSR output → continuity/metrics → optional feedback into next “roster” (e.g. preferred vehicles from last FSR run). Reference Timefold ESS API (shift templates, demand curves) at high level.

2. **Interface contract**
   - Define “roster provider” interface: e.g. JSON file or API that returns per client (or per zone) a list of caregiver/vehicle IDs for the planning period. Orchestrator reads this and patches FSR modelInput (visit → preferredVehicles or requiredVehicles).

**Acceptance:** Doc exists; a human or stub can produce the roster file and the next step (orchestrator) is clearly specified.

**Files:** `recurring-visits/docs/ESS_FSR_INTEGRATION_DESIGN.md`.

---

### B2. Orchestrator: roster file → FSR input

**Goal:** Implement a small script or module that takes (1) base FSR input, (2) roster file (client → list of vehicle IDs), (3) optional pool cap; outputs patched FSR input with preferredVehicles (or requiredVehicles) set per visit from roster.

**Tasks:**

1. **Roster file format**
   - Define JSON schema: e.g. `{ "client_id": [ "vehicle_id_1", ... ], ... }` with optional metadata (source: "ess" | "manual" | "stub"). Document in ESS_FSR_INTEGRATION_DESIGN.md.

2. **Patch script**
   - `scripts/apply_roster_to_fsr_input.py`: reads base FSR input + roster JSON; for each visit, derives client (KOLADA person from visit name); sets visit.preferredVehicles or visit.requiredVehicles from roster[client][:max_per_client]. Writes patched input. Reuse person resolution from continuity_report.py / build_continuity_pools.py.

3. **Integration point for ESS**
   - In doc, note: “When ESS is integrated, replace roster file with ESS API response adapter that writes the same JSON shape.”

**Acceptance:** Given base input and a roster JSON (e.g. from first-run FSR output converted to roster shape), script produces patched FSR input; running FSR on it uses roster as preferred/required vehicles.

**Files:** `recurring-visits/scripts/apply_roster_to_fsr_input.py`, update `docs/ESS_FSR_INTEGRATION_DESIGN.md`.

---

### B3. Stub roster from first-run FSR (for testing)

**Goal:** So we can test the orchestrator without ESS, add a small script that converts first-run FSR output into the roster JSON format (client → top-K vehicles).

**Tasks:**

1. **Script: FSR output → roster JSON**
   - `scripts/fsr_output_to_roster.py`: input = FSR output + (optional) FSR input for visit→client; output = roster JSON (client → list of vehicle IDs, e.g. top 10 by visit count). Reuse logic from build_continuity_pools first-run.

2. **E2E test**
   - Run: first-run output → fsr_output_to_roster.py → roster.json; apply_roster_to_fsr_input.py with roster.json → patched input; submit patched input. Compare continuity/efficiency vs first-run. Document in ESS_FSR_INTEGRATION_DESIGN or a short runbook.

**Acceptance:** Pipeline first-run → roster → patched input → solve runs end-to-end; results comparable to “first-run then build_continuity_pools then patch” but via generic roster interface.

**Files:** `recurring-visits/scripts/fsr_output_to_roster.py`, doc/runbook update.

---

## Sequencing and parallelization

- **Track A** and **Track B** can run in parallel (different subagents).
- Within Track A: A1 (CCI) first so A3 campaign has CCI in reports; A2 (pool 5–10 variants) can start once A1 design is agreed; A3 (run campaign) after A1 and A2.
- Within Track B: B1 (design) first; B2 (orchestrator) and B3 (stub) in parallel after B1.

## Deliverables summary

| Deliverable | Track | Location |
|-------------|--------|----------|
| CCI in continuity_report.py + CONTINUITY_METRICS.md | A | scripts/, docs/ |
| Pool 5–10 variant generation + campaign matrix doc | A | scripts/, docs/plans/ |
| Campaign run summary (efficiency + continuity + CCI) | A | continuity/ or optimization-research-scripts/ |
| ESS_FSR_INTEGRATION_DESIGN.md | B | docs/ |
| apply_roster_to_fsr_input.py | B | scripts/ |
| fsr_output_to_roster.py | B | scripts/ |

## Out of scope (this plan)

- Dashboard UI changes for CCI or new metrics (user uploads JSONs and checks metrics manually).
- Full Timefold ESS API integration (later).
- Jira ticket creation (optional; follow product-flow if needed).
