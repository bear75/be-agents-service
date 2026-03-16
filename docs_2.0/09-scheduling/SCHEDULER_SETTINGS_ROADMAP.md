# Scheduler Settings CRUD - Implementation Roadmap

## Troubleshooting: Empty shifts / Visits not assigned

- **Visits not showing as assigned**  
  The scheduler shows assignments from `solutionAssignments(solutionId, startDate, endDate)`. If the solution has no `SolutionAssignment` rows (e.g. schedule created from CSV and optimization not run yet), every visit appears in the unplanned pool. **Fix:** Run optimization for the schedule so the solution gets assignments, or create/update assignments manually.

- **All shifts empty**  
  Shifts are read per schedule from `ScheduleEmployeeShift` (schedule-scoped). If the schedule's employees have no shifts in the DB, the UI shows empty rows. Shifts are created when:
  - The upload flow creates employees with shift data (e.g. `createScheduleEmployeesAndShifts`), or
  - `ensureScheduleReadyForOptimization(scheduleId)` runs (e.g. when starting optimization) and adds default 8–17 shifts for employees that have none.  
    **Fix:** Run "Start optimization" so the backend calls `ensureScheduleReadyForOptimization` and creates shifts, or ensure the import creates `ScheduleEmployeeShift` records.

## Current State (Phase 1: Environment Variables)

Scheduler settings are currently configured via environment variables in `.env`:

```env
# Scheduler Settings
VITE_SCHEDULER_SHOW_PREFERENCES=true
VITE_SCHEDULER_SHOW_CONTACTS=true
VITE_SCHEDULER_SHOW_ALLOCATIONS=true
VITE_SCHEDULER_COLOR_BY=category
VITE_SCHEDULER_SHOW_CURRENT_TIME_LINE=true
```

These are read by the `getSchedulerSettings()` function in:

- `apps/dashboard/src/config/scheduler/settings.ts`

## Future State (Phase 2: Database-Driven Settings UI)

### Overview

Create a Settings CRUD UI in the Resources section (`/resources/settings`) that allows per-organization or per-user customization of scheduler behavior.

### Database Schema

Add a new table to store settings:

```prisma
model SchedulerSettings {
  id                     String   @id @default(cuid())
  organizationId         String?
  userId                 String?
  showPreferences        Boolean  @default(true)
  showContacts           Boolean  @default(true)
  showAllocations        Boolean  @default(true)
  colorBy                String   @default("category") // 'category' | 'frequency' | 'priority'
  showCurrentTimeLine    Boolean  @default(true)
  createdAt              DateTime @default(now())
  updatedAt              DateTime @updatedAt

  @@unique([organizationId])
  @@unique([userId])
  @@index([organizationId])
  @@index([userId])
}
```

**Priority Resolution:**

1. User-specific settings (`userId`)
2. Organization-wide settings (`organizationId`)
3. Environment variables (`.env`)
4. Hard-coded defaults

### GraphQL Schema

Add to `packages/graphql/schema/dashboard/types.graphql`:

```graphql
type SchedulerSettings {
  id: ID!
  organizationId: ID
  userId: ID
  showPreferences: Boolean!
  showContacts: Boolean!
  showAllocations: Boolean!
  colorBy: String!
  showCurrentTimeLine: Boolean!
  createdAt: DateTime!
  updatedAt: DateTime!
}

input UpdateSchedulerSettingsInput {
  showPreferences: Boolean
  showContacts: Boolean
  showAllocations: Boolean
  colorBy: String
  showCurrentTimeLine: Boolean
}

extend type Query {
  schedulerSettings: SchedulerSettings
}

extend type Mutation {
  updateSchedulerSettings(
    input: UpdateSchedulerSettingsInput!
  ): SchedulerSettings!
  resetSchedulerSettings: Boolean!
}
```

### Frontend Implementation

#### 1. Create Settings UI Component

**Location:** `apps/dashboard/src/components/Resources/Settings/SchedulerSettings.tsx`

**Features:**

- Toggle switches for show/hide options
- Radio buttons for `colorBy` dimension
- Real-time preview of changes
- Reset to defaults button
- Save/Cancel actions

#### 2. Update Settings Loader

Modify `apps/dashboard/src/config/scheduler/settings.ts` to use `useSchedulerSettingsQuery` and fall back to env while loading.

#### 3. Add Settings Route

Update `apps/dashboard/src/App.tsx`: add `/resources/settings` with children `scheduler` and `general`.

#### 4. Add Navigation Link

Update sidebar in `apps/dashboard/src/components/Layout/Sidebar.tsx`.

### Backend Implementation

Implement resolvers for `schedulerSettings` query and `updateSchedulerSettings` / `resetSchedulerSettings` mutations (user then org fallback).

### Migration Path

1. **Phase 1 (Current):** Environment variables only
2. **Phase 2a:** Add database schema and GraphQL API
3. **Phase 2b:** Build Settings UI components
4. **Phase 2c:** Integrate with existing scheduler
5. **Phase 2d:** Add user/org-level overrides
6. **Phase 3:** Advanced settings (custom color schemes, keyboard shortcuts, etc.)

### Testing Checklist

- [ ] Settings save correctly to database
- [ ] User settings override org settings
- [ ] Org settings override env variables
- [ ] Env variables work as fallback
- [ ] Reset to defaults works
- [ ] Real-time preview updates
- [ ] Changes apply immediately to scheduler
- [ ] Permissions: only admins can change org-wide settings

### Security Considerations

- **Authorization:** Only organization admins for org-wide defaults
- **Validation:** Validate all input (especially `colorBy` enum)
- **Audit Log:** Track who changed settings and when
- **Rate Limiting:** Prevent abuse of update mutation

---

## Related Files

- Current implementation: `apps/dashboard/src/config/scheduler/settings.ts`
- Tooltip renderer: `apps/dashboard/src/components/Scheduler/helpers/tooltipRenderers.tsx`
- Environment config: `apps/dashboard/.env.example`
- GraphQL schema: `packages/graphql/schema/dashboard/types.graphql`
