# CSV upload and dashboard flow

Flow: user uploads CSV in the dashboard (beta-appcaire) → schedule and visits are stored in DB → projection runs (count-only) so dashboard numbers match what would be sent to Timefold → user can start optimization to get a solution.

**Last updated**: 2026-03-14

---

## Overview

1. **Upload CSV** (e.g. Attendo format) in the dashboard.
2. **Parse and validate** (e.g. `parseAndValidateSchedule` mutation).
3. **Finalize upload** (`finalizeScheduleUpload`): adapter imports CSV into DB (Schedule, Visit, VisitGroup, Client, Employee, shifts, etc.).
4. **Projection (count-only)**: After import, `buildTimefoldModelInput(scheduleId, undefined, { countOnly: true })` is called. It runs the same projection logic as optimization but only persists counts (visits, visit groups, dependencies) to `schedule.sourceMetadata.modelCounts`. Dashboard metrics (e.g. `Schedule.visitsCount`, `inputSummary`) use these counts so they match the input that would be sent to Timefold.
5. **Optional: start optimization** from the schedule detail page. That calls `buildTimefoldModelInput(scheduleId, jobName)` (full build), sends the payload to Timefold, and creates a new Solution linked to the same Schedule.

---

## Where it lives

- **Repo**: beta-appcaire (dashboard + dashboard-server).
- **Import**: e.g. `importAttendoSchedule` in `apps/dashboard-server/src/services/schedule/importAttendoSchedule.ts`.
- **Finalize mutation**: `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/finalizeScheduleUpload.ts` (calls import, then projection count-only).
- **Projection**: `apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts`.
- **Start optimization**: `apps/dashboard-server/src/graphql/resolvers/solution/mutations/startOptimization.ts`.

---

## Counts and single source of truth

Dashboard numbers (visits, visit groups, dependencies) come from the **same projection** that builds the Timefold input. When `sourceMetadata.modelCounts` exists (after import or after at least one optimization build), `Schedule.visitsCount` and `inputSummary.visitGroupsCount` / `inputSummary.dependenciesCount` use those values so the UI and the payload never disagree.

See [01-source-of-truth.md](./01-source-of-truth.md) and beta-appcaire `docs/docs_2.0/09-scheduling/SCHEDULE_INPUT_FLOWS_AND_COUNTS.md`.
