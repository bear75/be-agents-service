# Insets and Client View — Technical Reference

**Purpose:** Technical reference for insets (visit types), InsetGroups, and the client-centric scheduler view.  
**Last Updated:** 2026-03-18

---

## Insets (Visit Types)

### Data Model

| Model | Purpose |
|-------|---------|
| **Inset** | Visit type: `name`, `displayName`, `category`, `defaultDurationMinutes`, `defaultSpreadDelay`, `defaultDaySlotId`, `defaultPriority`, `overlapAllowed` |
| **InsetGroup** | Group of insets (e.g. meals): `name`, `displayName`, `spreadDelay` |
| **InsetGroupMember** | Membership: `insetGroupId`, `insetId`, `sequence` |
| **DaySlot** | Time slots (Morgon, Lunch, Kväll): `name`, `startTime`, `endTime`, `sequence` |

All catalog data is **org-scoped**; see [SEED_DATA_SYSTEM_SETTINGS.md](./SEED_DATA_SYSTEM_SETTINGS.md).

### GraphQL

| Operation | Type | Notes |
|-----------|------|-------|
| `insets` | Query | Includes `insetGroupMembers` when requested (parent data contract) |
| `insetGroups` | Query | |
| `updateInset`, `createInset`, `deleteInset` | Mutation | |
| `createInsetGroup`, `updateInsetGroup`, `deleteInsetGroup` | Mutation | |
| `createInsetGroupMember`, `deleteInsetGroupMember` | Mutation | |

### Resolver Contract

The `insets` resolver conditionally includes `insetGroupMembers` when the selection set requests it. This ensures the `Inset.insetGroupMembers` field resolver receives data. See `apps/dashboard-server/src/graphql/resolvers/inset/queries/insets.ts`.

### Timefold FSR

- `buildTimefoldVisit` uses `resolveVisitDependencies` with `insetGroupMembers` to derive InsetGroup dependencies.
- `resolveInsetGroupDependencies` builds `InsetGroupDependencyEdge` from `InsetGroupMember` sequences.

### UI

- **InsetManagement** (`apps/dashboard/src/components/Resources/Organization/InsetManagement.tsx`) — CRUD insets
- **InsetFormDialog** — Create/edit inset
- **visitTypeConfig** — Inset category mapping for scheduler styling

---

## Client View

### Overview

The **client view** shows clients as resources and assignments as events. It complements the employee view (employees as resources).

### Key Files

| File | Purpose |
|------|---------|
| `ClientScheduler.tsx` | Main client view: Bryntum SchedulerPro, resources = clients |
| `ClientFilterPanel.tsx` | Filters: inset names, inset groups, frequencies, employees, only-with-dependencies |
| `clientViewMapper.ts` | `mapClientViewAll`: assignments → clients, events, time ranges, dependencies |
| `schedulerAppearanceConfig.ts` | Category/frequency colors, `applyClientViewCssVariables()` |

### Data Flow

1. `useClientViewAssignmentsQuery` (or `useSolutionAssignmentsQuery`) → `solutionAssignments(solutionId, startDate, endDate)`
2. `mapClientViewAll(assignments)` → `ClientViewData` (clients, events, timeRanges, dependencies)
3. `ClientFilterPanel` filters events by `insetNames`, `insetGroups`, `templateFrequencies`, `employeeNames`, `onlyWithDependencies`
4. `ClientScheduler` renders Bryntum with `resourceStore`, `eventStore`, `assignmentStore`, `resourceTimeRangeStore`, `dependencyStore`

### GraphQL

- `ClientViewAssignments` query includes `visit.inset.insetGroupMembers`, `visit.precedingDependencies`, `visit.succeedingDependencies`, `visit.groupMemberships`

### Filter Sync

`ClientScheduler` syncs filter params (`clientNameSearch`, `filters`) to the scheduler on visibility/resize via `filterParamsRef` and `applyClientFilters`. Ensures filters apply after scheduler re-renders.

---

## Scheduler Appearance

### Org-Level Overrides

- **Storage:** `Organization.settings.schedulerAppearance` (category colors, frequency border colors)
- **UI:** `SchedulerAppearanceSection` in Operational Settings (`OperationalSettingsForm`)
- **Application:** `SchedulerContainer` loads org settings via `useOrganizationQuery`, calls `setAppearanceOverrides()` and `applyFrequencyCssVariables()` on data load

### Env Fallbacks

| Variable | Purpose |
|----------|---------|
| `VITE_SCHEDULER_CATEGORY_COLORS` | JSON override for category colors |
| `VITE_SCHEDULER_FREQUENCY_COLORS` | JSON override for frequency border colors |
| `VITE_SCHEDULER_CLIENT_VIEW_APPEARANCE` | JSON override for client view appearance |
| `VITE_SCHEDULER_COLOR_BY` | `category` \| `frequency` \| `priority` |

See `apps/dashboard/.env.example` for full override examples.

---

## Related Docs

- [SEED_DATA_SYSTEM_SETTINGS.md](./SEED_DATA_SYSTEM_SETTINGS.md) — Org-scoped catalog
- [SOLUTION_UI_SPECIFICATION.md](./SOLUTION_UI_SPECIFICATION.md) — Visit display rules
- [SCHEDULER_SETTINGS_ROADMAP.md](./SCHEDULER_SETTINGS_ROADMAP.md) — Future DB-driven settings
