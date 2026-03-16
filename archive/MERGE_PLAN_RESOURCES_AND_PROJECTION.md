# Plan: One branch with Resources CRUD + E2E scheduling + UX

## Goal

One branch that has:

1. **Resources CRUD** — full data model (skills, tags, insets, visit groups, etc.) and UI
2. **Seed or upload CSV** — store resources
3. **E2E scheduling** — build input → solve → store solution → show metrics and schedule
4. **Then** — Scheduler filter & styling v2 (from `.cursor/plans/scheduler_filter_styling_v2_33eb5613.plan.md`) with the new data model

## Easiest and lowest-risk approach: merge cursor into feat

**Merge `cursor/resource-to-solver-projection-beb1` INTO `feat/resources-crud-complete`** (not the other way).

- **feat** = your target: new data model, resources CRUD, rebased on main. Keep it as the base.
- **cursor** = add its projection, CSV upload, seed, solve flow, and metrics on top of feat.

So you end up with one branch that has both.

---

## Step-by-step (low risk)

### Step 1: Fix `feat/resources-crud-complete` schema first (on feat)

On `feat/resources-crud-complete`:

1. Remove the **first** (org-scoped) `VisitGroup` and `Organization.visitGroups` from `schema.prisma`.
2. Remove `Visit.visitGroupId` and `Visit.visitGroup` so the only link is `Visit.groupMemberships` → `VisitGroupMember` → `VisitGroup`.
3. Update any code that still uses the old org-scoped group or `visitGroupId` (e.g. `uploadScheduleForOrganization.ts`, `createScheduleFromModelInput.ts`, `prepareScheduleData.ts`) to use the schedule-scoped VisitGroup and `groupMemberships` / `VisitGroupMember` where needed.
4. Run `yarn workspace dashboard-server db:generate` and fix type errors until `yarn type-check` passes.
5. Commit: e.g. `fix(schema): single VisitGroup (schedule-scoped), remove duplicate and visitGroupId`.

This gives you a clean, valid schema on feat so the merge doesn’t fight two different VisitGroup models.

### Step 2: Merge cursor into feat

```bash
git checkout feat/resources-crud-complete
git pull origin feat/resources-crud-complete   # if needed
git merge cursor/resource-to-solver-projection-beb1 -m "merge: resource-to-solver projection into resources-crud-complete"
```

You will get merge conflicts. Resolve them by:

- **Schema:** Keep feat’s single VisitGroup (schedule-scoped, `requiredStaff`, `VisitGroupMember`). Do not re-add the org-scoped VisitGroup or `Visit.visitGroupId`.
- **Resources CRUD (resolvers, UI):** Keep feat’s version (new data model, authz, etc.).
- **Projection / solver / CSV / seed:** Prefer cursor’s version for:
  - `apps/dashboard-server/src/services/timefold/projection/`
  - `buildTimefoldModelInput`, CSV upload, seed that feeds the solver
  - Solve flow, store solution, metrics
- **Generated (GraphQL):** After resolving source files, run `yarn generate` and commit the regenerated files.

Conflict areas will likely include:

- `schema.prisma` — keep feat’s cleaned schema
- Resolvers that exist in both (e.g. visit, visitGroup) — keep feat’s authz/CRUD, add any projection-specific behavior from cursor if needed
- `prepareScheduleData.ts`, `createScheduleFromModelInput.ts` — use cursor’s projection logic, but make it use the single VisitGroup and `groupMemberships` (no `visitGroupId`)

### Step 3: Verify E2E on the merged branch

1. Seed (or upload CSV) → resources stored.
2. Generate solution / build input (projection) → solve → store solution.
3. Show metrics and schedule solution in the UI.

Fix any remaining type or runtime errors so this flow works on the merged branch.

### Step 4: Scheduler filter & styling v2

Once E2E works, implement the plan in `.cursor/plans/scheduler_filter_styling_v2_33eb5613.plan.md` (event styling, frequency dropdown, filter panel, filter chips, skills, shift utilization) on this same branch. The plan already assumes the PR #100 / projection semantics (e.g. derived `isMovable`, `isMandatory`, resolved skills, priority cascade).

---

## Why not merge feat into cursor?

- **cursor** is based on an older main and doesn’t have the full resources CRUD and rebase-on-main fixes.
- Merging feat into cursor would mean resolving conflicts inside an older codebase and then having to fix schema/CRUD again on cursor. More work and more risk.
- Merging cursor into feat keeps feat as the single source of truth for the new data model and CRUD; you only “add” projection and solve flow.

---

## Summary

| Step | Action                                                                                                          |
| ---- | --------------------------------------------------------------------------------------------------------------- |
| 1    | On **feat**: fix duplicate VisitGroup (keep schedule-scoped only, drop visitGroupId), fix code + types, commit. |
| 2    | **Merge** cursor into feat; resolve conflicts (feat schema + CRUD, cursor projection/solve/CSV/seed).           |
| 3    | Verify **E2E**: seed/upload → resources → build input → solve → store solution → metrics + schedule.            |
| 4    | Implement **scheduler filter & styling v2** plan on the same branch.                                            |

Result: one branch with resources CRUD, seed/upload, full scheduling E2E, and then the matching UX styling and filtering with the new data model.
