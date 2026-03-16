# Operational Settings Cascade: Costs and Revenues

This document describes how operational settings (costs and revenues) cascade from organization → service area → employee and how they are connected to scheduling. Resources settings are the source of defaults when entity-level data (employee cost, visit revenue) is missing.

## Intended hierarchy

| Level            | Source                                                                                                                               | Fields                                  |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------- |
| **Organization** | `OperationalSettings` with `level: "organization"`, `serviceAreaId: null`, `employeeId: null`                                        | `defaultHourlySalary`, `revenuePerHour` |
| **Service area** | `OperationalSettings` with `level: "service_area"`, `serviceAreaId` set; or `ServiceArea.costPerHour` / `ServiceArea.revenuePerHour` | Overrides for that area                 |
| **Employee**     | `OperationalSettings` with `level: "employee"`, `employeeId` set; or `EmployeeCost` (hourlySalary)                                   | Per-employee cost                       |

Cascade rule: **employee (or visit/client) → service area default → org operational setting default → env/hardcoded**. When a value is missing, fall back to the next level. Hardcoded fallbacks (230 SEK cost, 534 SEK revenue) should rarely apply since all new orgs are seeded with operational settings.

---

## Shared resolver: `services/operational-defaults.ts`

**File:** `apps/dashboard-server/src/services/operational-defaults.ts`

- **`getEffectiveDefaultHourlySalary(prisma, { organizationId, serviceAreaId?, employeeId? })`**  
  Returns effective default cost for scheduling. Cascade: org OperationalSettings → service area OperationalSettings / ServiceArea.costPerHour → employee-level OperationalSettings → `DEFAULT_HOURLY_SALARY` (230).

- **`getEffectiveRevenuePerHour(prisma, { organizationId, serviceAreaId? })`**  
  Returns effective revenue per hour. Cascade: org OperationalSettings → service area OperationalSettings / ServiceArea.revenuePerHour → `DEFAULT_REVENUE_PER_HOUR` (534).

Both accept Prisma client or transaction client so they work inside upload transactions.

---

## Where the cascade is implemented

### 1. GraphQL query `operationalSettings`

**File:** `apps/dashboard-server/src/graphql/resolvers/operational-settings/queries/operationalSettings.ts`

- **Organization:** Fetches org-level settings (or returns defaults with null salary/revenue).
- **Service area:** If `serviceAreaId` is provided, merges service-area settings over org (non-null overrides).
- **Employee:** If `employeeId` is provided, merges employee-level settings over the result.

The **UI** (Resources → Organization → Operational, or service area edit) shows these merged defaults.

### 2. Building Timefold input (`buildTimefoldModelInput`)

**File:** `apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts`

- For each schedule employee, if `employee.costs.length === 0`, **effective default cost** is resolved via `getEffectiveDefaultHourlySalary(prisma, { organizationId, serviceAreaId: employee.serviceAreaId, employeeId: employee.id })` and passed as synthetic cost into `resolveEmployeeShift`. Every vehicle sent to Timefold therefore has a cost (entity → service area → org → hardcoded).

### 3. Solution metrics (revenue)

**File:** `apps/dashboard-server/src/services/bridge/metrics/solution-metrics.service.ts`

- When stored totalRevenue is null, **effective revenue per hour** is resolved via `getEffectiveRevenuePerHour(prisma, { organizationId, serviceAreaId: schedule.serviceAreas[0]?.serviceAreaId })`. Revenue is then `(totalVisitMinutes / 60) * effectiveRevenuePerHour`. Schedule include was extended with `serviceAreas: { take: 1 }` so the first linked service area is used when present.

### 4. Schedule upload (`uploadScheduleForOrganization`)

**File:** `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/uploadScheduleForOrganization.ts`

- After upserting employees and creating schedule employees/shifts, **`ensureEmployeeCostsFromDefaults(tx, organizationId, employeeIds)`** runs. For each employee without a current `EmployeeCost` (effectiveTo: null), it creates one with `hourlySalary` from `getEffectiveDefaultHourlySalary(tx, { organizationId, serviceAreaId: employee.serviceAreaId, employeeId })` and `effectiveFrom: new Date()`. Uploaded employees therefore get a default cost from the cascade.

### 5. Creating/updating operational settings (service area / employee)

**File:** `apps/dashboard-server/src/graphql/resolvers/operational-settings/mutations/updateOperationalSettings.ts`

When creating or updating **service_area** or **employee** level settings, the mutation can inherit from parent (e.g. `revenuePerHour ?? parentSettings?.revenuePerHour`). That only affects the OperationalSettings rows themselves; scheduling uses the same cascade via the resolver above.

---

## Seeding

- **Bootstrap/seed** scripts (e.g. bootstrap-org, seed-attendo) create org-level operational settings and optionally service areas with `costPerHour`/`revenuePerHour`. They can create `EmployeeCost` for employees using `getEffectiveDefaultHourlySalary` from `services/operational-defaults.ts` if desired; build and upload already apply the same defaults at runtime when cost is missing.

---

## Data model summary

| What                      | Stored where                                                                                                   | Used where                                                                |
| ------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| Org default cost          | `OperationalSettings.defaultHourlySalary` (org-level row)                                                      | operational-defaults resolver → buildTimefoldModelInput, upload, UI query |
| Org default revenue       | `OperationalSettings.revenuePerHour` (org-level row)                                                           | operational-defaults resolver → getSolutionMetrics, UI query              |
| Service area cost/revenue | `ServiceArea.costPerHour`, `ServiceArea.revenuePerHour`; or `OperationalSettings` with `level: "service_area"` | Same resolver; build, metrics, and upload use service area when available |
| Employee cost             | `EmployeeCost.hourlySalary` (effective record)                                                                 | buildTimefoldModelInput (or default from cascade when missing)            |
| Visit revenue             | Not stored on Visit                                                                                            | Metrics use effective revenuePerHour from org/schedule service area       |
