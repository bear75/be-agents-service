# Revision & Solution Storage Strategy

> **Status:** Design  
> **Last Updated:** 2026-02-17  
> **Related:** `SCHEDULE_SOLUTION_ARCHITECTURE.md`, `SCHEDULING_MASTER_PRD.md`, Jira C0-281 (Revision & Solution Storage), C0-24 (Metrics – event-level storage, every second accounted for)

---

## 1. Problem Statement

At scale (100s of orgs × 100s of schedules × many revisions), storage grows fast if every change persists a full new solution:

- **Input**: Large JSON per problem (vehicles, visits, time windows, constraints).
- **Output**: Assignments, events, metrics per solution revision.
- **Revisions**: Only created on **Save** or **Run optimization**; **Cancel** must not persist.

We need a backend strategy that:

1. Keeps revision history without duplicating full input/output per revision.
2. Preferentially uses **deltas** to limit size where possible.
3. Supports **retention/cleanup** (e.g. when a schedule is archived, keep only published + original).
4. Retains **enough data for future RL** (demand/supply forecasting, learning loops).

---

## 2. Current State (Backend)

| Entity                       | What is stored                                                                             | Growth driver                                                                                    |
| ---------------------------- | ------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------ |
| **Schedule**                 | Metadata, version, status; links to one Problem.                                           | One row per schedule (bounded).                                                                  |
| **Problem**                  | `problemData` (JSON) = full model input for one run.                                       | **One new Problem per optimization run** in current code (startOptimization / timefold.service). |
| **Solution**                 | Normalized: SolutionAssignment, SolutionEvent, SolutionMetric. No full `modelOutput` JSON. | One Solution + N assignments + M events + 1 metric set **per revision**.                         |
| **Visit / ScheduleEmployee** | Normalized rows.                                                                           | Per schedule (bounded).                                                                          |

**Findings:**

- **Input**: Stored once per **Problem**. Today we create a **new Problem** on every optimization run, so `problemData` is duplicated per run → high storage if we keep all runs.
- **Output**: We do **not** store full route-plan JSON per solution; we normalize into assignments/events/metrics. So output storage is row-based, not “100k JSON files” per se, but row count still scales with revisions.
- **Revision semantics**: Not yet explicit (e.g. no `revisionNumber` on Solution, or “published” vs “draft” solution pointer on Schedule).

---

## 3. Recommended Model

### 3.1 When a Revision Is Created

- **User saves** (applies current state to the schedule) → create new revision.
- **User runs optimization** and result is accepted/saved → new revision.
- **User cancels** (discard changes) → **no** new revision; nothing persisted.

So: one logical “revision” = one persisted snapshot of the solution state (assignments + metrics, and optionally a pointer to which problem input it was based on).

### 3.2 One Problem per Schedule Snapshot (Avoid Input Duplication)

- **Do not** create a new Problem for every optimization run. Reuse **one Problem per Schedule** (or per “schedule snapshot” when input actually changes).
- **Problem** = “current input for this schedule.” When visits/employees/constraints change (e.g. after import or manual edit), then **update** the existing Problem’s `problemData` in place, or introduce a “snapshot” policy (e.g. new Problem only when we explicitly snapshot for optimization).
- All Solutions for that schedule that share the same input reference the **same** `problemId`.  
  Effect: input JSON is stored **once per schedule** (or once per snapshot), not once per revision → large storage win.

**Implementation note:** Today `startOptimization` and the bridge `timefold.service` create a new Problem per run. This should be refactored to:

- Resolve “current” Problem for the schedule (e.g. `Schedule.problemId`), or create one if none.
- Update `Problem.problemData` from current schedule state when starting optimization (or when “snapshot” is taken), instead of always creating a new Problem.

### 3.3 One Solution Row per Revision (Normalized, No Full Output JSON)

- Each **revision** = one **Solution** row plus its normalized children (SolutionAssignment, SolutionEvent, SolutionMetric).
- **Do not** add a column that stores full `modelOutput` (route-plan JSON). Keep deriving UI/API from assignments + events + metrics.
- Add a **revision number** (or sequence) per schedule, e.g.:
  - `Solution.revisionNumber` (integer, per schedule), or
  - Order by `Solution.createdAt` and derive revision from position.
- Schedule has a pointer to “current” or “published” solution, e.g.:
  - `Schedule.publishedSolutionId` (optional), and/or
  - `Schedule.currentSolutionId` (draft) so UI knows which revision is active.

This keeps a clear audit trail (one row per revision) without storing full output JSON.

### 3.4 Delta Option (Further Compression)

If we need to keep many revisions but want to limit size:

- **Base + deltas**: Store one “full” solution (assignments + metrics) per schedule (e.g. published or first revision). For later revisions, store only **deltas** (e.g. which assignments changed: visitId, previous employee, new employee, time window).
- **Patch format**: Reuse or extend `Solution.patchOperations` (or a dedicated `SolutionDelta` table) to record only changes vs the previous revision. Rebuild “full” state when needed by applying deltas in order.
- **Trade-off**: More complex read path (reconstruct from base + deltas); simpler to implement “last N full revisions + older as deltas” or “full for published + original, deltas for rest.”

Recommendation: start with **full normalized state per revision** (one Solution + children per revision). Introduce delta storage only if retention policy still leaves too many full revisions (e.g. after measuring row counts and growth).

### 3.5 Retention and Cleanup

When a schedule moves to **archived** / **history**:

- **Keep**: The **published** solution (if any) and optionally the **original** (first) solution.
- **Prune**: All other revisions for that schedule (or move to cold storage if we need them for compliance).
- **RL**: Do not rely on keeping all assignment rows long term. Instead, **aggregate** or **sample** (see below).

Policy can be:

- **Active schedule**: Keep last K full revisions (e.g. 10) plus “published” and “original”; delete or delta-compress older ones.
- **Archived schedule**: Keep only published + original; delete the rest (or export to cold storage once).

### 3.6 Data for RL (Demand/Supply Forecasting)

Future RL loops need **demand/supply and outcome signals**, not necessarily every assignment row:

- **Prefer**:
  - **Aggregated metrics per solution**: e.g. SolutionMetric (and existing SolutionComparison) plus schedule/solution identifiers and timestamps. Store in the same DB or in an analytics table.
  - **Time-series summaries**: e.g. per-org, per-service-area, or per-schedule: visit counts, unassigned counts, travel minutes, utilization, continuity score, over time.
  - **Sampled revisions**: If we need some assignment-level data, keep a **sample** of revisions (e.g. 1 in 10 or only “published” solutions) with assignments, not every draft.
- **Avoid**:
  - Keeping every revision’s full assignment/event rows forever for all schedules.

Concrete options:

- **SolutionMetric** (and related metric tables) already exist; ensure we retain these (or an aggregated copy) for published/original and optionally for a sampled set of revisions, even after pruning assignments.
- Add an **analytics / RL export** job: periodically dump compact records (scheduleId, solutionId, revisionNumber, metrics, timestamp) and optionally sampled assignment counts or distributions, to a separate store (e.g. data lake or analytics DB) used only for forecasting. Then the main app DB can prune aggressively.

---

## 4. Summary Table

| Aspect                       | Recommendation                                                                                                                                               |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **When revision is created** | Only on **Save** or **Run optimization** (result saved). Not on Cancel.                                                                                      |
| **Input (problem)**          | One Problem per schedule (or per snapshot); reuse, do not duplicate per run.                                                                                 |
| **Output (solution)**        | One Solution row per revision; normalized assignments/events/metrics only; **no** full modelOutput JSON.                                                     |
| **Versioning**               | Add revision number/sequence per schedule; Schedule points to published and optionally current solution.                                                     |
| **Deltas**                   | Optional later: store base + deltas for older revisions to compress.                                                                                         |
| **Retention**                | On archive: keep published + original; prune or cold-store the rest. For active schedules, consider “last K full + rest as deltas or pruned.”                |
| **RL**                       | Keep aggregated metrics (and optionally sampled revisions); export to analytics/RL store; do not keep every assignment row indefinitely.                     |
| **Metrics**                  | Save at every level (Solution → Employee → Client → ServiceArea); every second accounted for via `SolutionEvent` (conservation law). See C0-24, C0-32–C0-50. |

---

## 5. Implementation Hooks (for C0-281)

- **Refactor Problem creation**: Reuse/update `Schedule.problemId` and `Problem.problemData` instead of creating a new Problem on every optimization run.
- **Solution revision**: Add `Solution.revisionNumber` (or equivalent) and `Schedule.publishedSolutionId` / `Schedule.currentSolutionId`; ensure “save” and “run optimization + accept” create a new Solution row; “cancel” does not.
- **Retention job**: When a schedule is archived (or on a periodic job), prune solutions except published + original (and optionally keep last N); optionally move pruned data to cold storage.
- **RL/analytics**: Define which metrics and dimensions to keep long term; add export or summary tables if needed; document in PRD or Confluence.
- **Metrics (C0-24, C0-32–C0-50)**: Metrics are saved at every level (Solution, Employee, Client, ServiceArea) and every second is accounted for: event-level data in `SolutionEvent` (TRAVEL, VISIT, BREAK, WAIT with seconds, distance, sequence); aggregations on-demand; conservation law (shift = visit + travel + break + wait) enforced.

This document can be referenced from the Confluence PRD and from Jira task C0-281 (Revision & Solution Storage).
