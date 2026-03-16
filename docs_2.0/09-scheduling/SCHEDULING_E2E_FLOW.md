# Scheduling E2E Flow

> **Purpose:** Define the full end-to-end pipeline for scheduling: data in → optimization → solution stored → UX. Manual E2E verification should cover this entire flow; individual scripts/tests may cover segments.
> **Related:** [SCHEDULE_SOLUTION_ARCHITECTURE.md](SCHEDULE_SOLUTION_ARCHITECTURE.md), [RESOURCES_E2E_TEST_PLAN.md](../../archive/RESOURCES_E2E_TEST_PLAN.md) (archived)

---

## Full E2E pipeline (in order)

### 1. Data import (one of)

Schedule + visits + employees must exist in the DB before optimization. Choose one entry point:

| Method                | API / entry                                                               | Notes                                                                                                                      |
| --------------------- | ------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| **Upload CSV**        | `uploadScheduleForOrganization` (GraphQL)                                 | Attendo-style CSV → `importAttendoSchedule` → Schedule, Visits, Employees                                                  |
| **Upload input JSON** | `createScheduleFromTimefoldJson` (GraphQL)                                | Timefold export format (`modelInput` with vehicles, visits) → `createScheduleFromModelInput` → Schedule, Visits, Employees |
| **Seed data**         | `yarn workspace dashboard-server db:seed:attendo` (or other seed scripts) | Populates DB with schedules, visits, employees for dev/demo                                                                |

### 2. User generates a solution (one of)

| Method                         | API / entry                                | Notes                                                                                                                                            |
| ------------------------------ | ------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Via button**                 | `startOptimization` (GraphQL)              | Builds FSR request from DB → submits to Timefold API → creates Solution record; webhook later fills assignments when job completes               |
| **Upload output JSON**         | `createSolutionFromTimefoldJson` (GraphQL) | Schedule ID + Timefold payload (solution + modelOutput) → `applyTimefoldPayloadToSolution` → Solution + assignments + metrics. No live API call. |
| **Upload output (patch path)** | `createSolutionFromPatch` (GraphQL)        | Can create schedule from input JSON + solution from output JSON in one flow (e.g. run solver externally, then ingest).                           |

### 3. DB → Timefold API (when using “via button”)

When the user triggers **startOptimization**:

- Server builds FSR model from DB: `buildTimefoldModelInput(scheduleId, …)` (see `services/timefold/projection`). Every visit’s time windows are ensured to span at least the visit duration (`ensureTimeWindowMinDuration`), so the FSR matches the script and Timefold does not emit “time window too small” warnings.
- Server submits to Timefold: `TimefoldClient.fullSolve(request)`.
- Solution row is created with status `solving_scheduled` / `solving_active`; `datasetId` stores the Timefold job ID.

**Manual script covering this segment only:**  
`yarn workspace dashboard-server e2e:timefold` runs `src/scripts/e2e-submit-to-timefold.ts`. It assumes a schedule already exists (e.g. from step 1), builds the request, submits to the real Timefold API, and polls status. It does **not** run import, webhook, or UI.

### 4. Webhook → store solution and metrics

When Timefold completes the job it calls our webhook:

- **Route:** `POST /webhooks/timefold` (`routes/webhooks/timefold.ts`).
- **Payload:** Job id, status, `outputLink` (or similar) to fetch solution + modelOutput.
- **Actions:** Fetch output, map to our model (`solution-mapper.service`, `modelOutputToSolution`, etc.), update Solution (assignments, status), compute and store metrics.

So the full “button” path is: **Step 1 (import) → Step 2 (startOptimization) → Step 3 (DB→TF API) → Step 4 (webhook stores solution and metrics).**

### 5. Display solution in UX

- Dashboard reads Solution + SolutionAssignments + metrics via GraphQL (e.g. `solution`, `solutionAssignments`, `metrics`).
- Bryntum (or other UI) displays the plan (who does which visit when).

---

## Summary: what to verify in a “real” E2E

A **full** round-trip E2E should include:

1. **Data import** via CSV, or input JSON, or seed.
2. **Solution generation** via button (`startOptimization`) **or** upload of output JSON (`createSolutionFromTimefoldJson` / `createSolutionFromPatch`).
3. If using the button: **DB → Timefold API** (submit + job created); optional: **webhook** receives completion, **store solution and metrics**.
4. **Display**: solution and metrics visible in dashboard UX.

The script `e2e-submit-to-timefold.ts` only covers **segment 3** (DB → TF API submit + status poll). Use it when you already have data in the DB and want to smoke-test the projection and Timefold submission; for full E2E, run the steps above manually or automate them end-to-end.
