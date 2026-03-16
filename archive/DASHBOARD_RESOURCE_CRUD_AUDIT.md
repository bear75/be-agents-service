# Dashboard Resource CRUD Audit

**Date:** 2026-03-08  
**Scope:** All dashboard resource CRUD pages — Form → GraphQL → Resolver → Prisma chain.

---

## 1. Resource types identified

| Resource        | Create/Edit pages                          | Form component  | List/other pages                 |
| --------------- | ------------------------------------------ | --------------- | -------------------------------- |
| **Client**      | ClientCreatePage, ClientEditPage           | ClientForm      | ClientList, ClientCard           |
| **Employee**    | EmployeeCreatePage, EmployeeEditPage       | EmployeeForm    | EmployeeList, EmployeeCard       |
| **ServiceArea** | ServiceAreaCreatePage, ServiceAreaEditPage | ServiceAreaForm | ServiceAreaList, ServiceAreaCard |
| **Visit**       | VisitCreatePage, VisitEditPage             | VisitForm       | VisitDetailPage, etc.            |

There are no separate CRUD pages for Vehicle, Template, or other entities under `components/Resources`; Organization is settings/overview, not a simple CRUD form flow.

---

## 2. Per-resource verification

### 2.1 Client

| Check                 | Status | Notes                                                                                                                                                                                                                                                                                                                                                                                   |
| --------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Form fields (key)** | OK     | firstName, lastName, personalNumber, birthYear, gender, email, phone, contactPerson, address, latitude, longitude, municipality, externalId, serviceAreaId, careLevel, diagnoses (string → split to array on submit), notes. Skills via separate createClientSkill/deleteClientSkill.                                                                                                   |
| **Schema / input**    | OK     | CreateClientInput & UpdateClientInput in `types.graphql` include all of the above (diagnoses as `[String!]`).                                                                                                                                                                                                                                                                           |
| **Mutation maps all** | OK     | createClient and updateClient map every input field to `prisma.client.create/update` with correct null/undefined handling.                                                                                                                                                                                                                                                              |
| **Query returns all** | OK     | client query returns full record; Client query document requests all form-relevant fields + addresses, contacts, skills, preferences, allocations.                                                                                                                                                                                                                                      |
| **Prisma columns**    | OK     | Client model has columns for all form fields (diagnoses as String[]).                                                                                                                                                                                                                                                                                                                   |
| **Gaps**              | None   | **Fixed:** Client query converts latitude/longitude (Prisma Decimal) to Number. **Fixed:** CreateClient and UpdateClient mutation responses now include gender, birthYear, contactPerson, address, latitude, longitude, municipality, careLevel, diagnoses. **Fixed:** createClient and updateClient resolvers now pass latitude/longitude as `Prisma.Decimal` so values persist in DB. |

---

### 2.2 Employee

| Check                 | Status | Notes                                                                                                                                                                                                                                                                                                                                                                                                                 |
| --------------------- | ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Form fields (key)** | OK     | firstName, lastName, email, phone, gender, serviceAreaId, status, role, startDate, endDate, homeAddress, homeLatitude, homeLongitude, externalId, isPlaceholder, driverLicenseType, transportMode, contractType, contractedHoursPerWeek, employmentPercentage, maxHoursPerDay, maxHoursPerWeek, maxVisitsPerDay, maxTravelTimePerDay, preferredWorkDays, unavailableDates, notes. Skills/tags via separate mutations. |
| **Schema / input**    | OK     | CreateEmployeeInput & UpdateEmployeeInput include all of the above.                                                                                                                                                                                                                                                                                                                                                   |
| **Mutation maps all** | OK     | createEmployee and updateEmployee map every input field to Prisma (with Decimal/array casting and BigInt→Number in response where needed).                                                                                                                                                                                                                                                                            |
| **Query returns all** | OK     | employee query uses mapEmployee; query document requests all form-relevant fields.                                                                                                                                                                                                                                                                                                                                    |
| **Prisma columns**    | OK     | Employee model has columns for all form fields.                                                                                                                                                                                                                                                                                                                                                                       |
| **Gaps**              | None   | **Fixed:** CreateEmployee mutation response now includes `driverLicenseType` and `isPlaceholder`.                                                                                                                                                                                                                                                                                                                     |

**How to add salary, cost per hour:** Open an employee in **edit** mode. Scroll to the section **«Salary & cost per hour»** (Lön och kostnad per timme). Click **«Add Cost»** to create a cost period. Each period has: effective from/to dates, **hourly salary** (timlön), overtime rate, evening/night/weekend/holiday bonuses, travel compensation. Costs are stored in `EmployeeCost`; the `Employee.costs` field resolver returns them. On **create** the section is not shown; after saving the new employee, open it again to add costs.

---

### 2.3 ServiceArea

| Check                 | Status | Notes                                                                                                                                                                                                                                                 |
| --------------------- | ------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Form fields (key)** | OK     | name, shortName, parentId, externalId, address, latitude, longitude, continuityThreshold, continuityThresholdScenarioOverridable, unusedHoursRecapturePriority, costPerHour, revenuePerHour, isAbstracted, abstractedType, representedServiceAreaIds. |
| **Schema / input**    | OK     | CreateServiceAreaInput & UpdateServiceAreaInput include all of the above.                                                                                                                                                                             |
| **Mutation maps all** | OK     | createServiceArea and updateServiceArea map every input field (including continuityThresholdScenarioOverridable); Decimal handling for costPerHour/revenuePerHour.                                                                                    |
| **Query returns all** | OK     | serviceArea query converts Decimal to Number and returns all fields; query document requests them.                                                                                                                                                    |
| **Prisma columns**    | OK     | ServiceArea model has columns for all form fields (Decimal for latitude, longitude, costPerHour, revenuePerHour; representedServiceAreaIds as String[]).                                                                                              |
| **Gaps**              | None   | —                                                                                                                                                                                                                                                     |

---

### 2.4 Visit

| Check                 | Status  | Notes                                                                                                                                                                                                                                                                                                    |
| --------------------- | ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Form fields (key)** | OK      | scheduleId, clientId, durationMinutes, visitCategory, type, insetId, visitStatus, priority, requiredStaff, isPinned, pinnedEmployeeId, isMandatory, isMovable, latestSlaEndTime, allowedTimeWindowStart/End, preferredTimeWindowStart/End, notes, externalId. Skills/tags/groups via separate mutations. |
| **Schema / input**    | OK      | CreateVisitInput & UpdateVisitInput include insetId, isMandatory, isMovable, latestSlaEndTime.                                                                                                                                                                                                           |
| **Mutation maps all** | **GAP** | createVisit does **not** pass insetId, isMandatory, isMovable, latestSlaEndTime to `prisma.visit.create`. updateVisit does **not** include them in updateData.                                                                                                                                           |
| **Query returns all** | OK      | visit query uses mapVisit; Visit query document requests insetId, isMandatory, isMovable, latestSlaEndTime.                                                                                                                                                                                              |
| **Prisma columns**    | OK      | Visit model has insetId, isMandatory, isMovable, latestSlaEndTime.                                                                                                                                                                                                                                       |
| **Gaps**              | 2       | (1) Resolvers don’t persist four fields. (2) Create/Update mutation responses don’t request them.                                                                                                                                                                                                        |

**Concrete fixes (implemented):**

1. **createVisit** — In `apps/dashboard-server/src/graphql/resolvers/visit/mutations/createVisit.ts`, added to the `data` object: `insetId`, `isMandatory`, `isMovable`, `latestSlaEndTime`.

2. **updateVisit** — In `apps/dashboard-server/src/graphql/resolvers/visit/mutations/updateVisit.ts`, added to `updateData`: `insetId`, `isMandatory`, `isMovable`, `latestSlaEndTime`.

3. **Mutation responses** — Done: `createVisit.graphql` and `updateVisit.graphql` now request `insetId isMandatory isMovable latestSlaEndTime`.

---

## 3. Summary table

| Resource    | Form fields complete? | Schema/input complete? | Mutation maps all? | Query returns all? | Prisma has columns? | Gaps                                                                       |
| ----------- | --------------------- | ---------------------- | ------------------ | ------------------ | ------------------- | -------------------------------------------------------------------------- |
| Client      | Yes                   | Yes                    | Yes                | Yes                | Yes                 | None (mutation responses broadened; Client query Decimal→Float fixed).     |
| Employee    | Yes                   | Yes                    | Yes                | Yes                | Yes                 | None (Create mutation response includes driverLicenseType, isPlaceholder). |
| ServiceArea | Yes                   | Yes                    | Yes                | Yes                | Yes                 | None.                                                                      |
| Visit       | Yes                   | Yes                    | Yes (fixed)        | Yes                | Yes                 | None (createVisit/updateVisit and mutation docs updated).                  |

---

## 4. Checklist for future CRUD

Use this when adding or changing a dashboard resource CRUD flow:

1. **Form**
   - List every field the create/edit form collects (including from nested components).
   - For arrays (e.g. diagnoses, skills), decide: single input (e.g. comma-split) vs separate junction mutations.

2. **GraphQL schema** (`packages/graphql/schema/dashboard/`)
   - Ensure the type has all fields the form needs (and correct types, e.g. Float for decimals).
   - Ensure CreateXInput and UpdateXInput include every field the form sends, with correct nullability.

3. **Operations**
   - **Mutations:** In `packages/graphql/operations/mutations/dashboard/`, create/updateX: selection set must include every field the UI needs after save (or rely on refetch; if refetch, ensure the query requests them).
   - **Queries:** In `packages/graphql/operations/queries/dashboard/`, the single-entity query (e.g. client, employee, serviceArea, visit) must request all form fields and any nested relations the form uses.

4. **Resolvers** (`apps/dashboard-server/src/graphql/resolvers/`)
   - createX: map **every** input field into `prisma.x.create({ data: { ... } })` with correct null/undefined handling (and enums/Decimal/arrays as required by Prisma).
   - updateX: for each updatable input field, `if (input.field !== undefined) updateData.field = input.field ?? null` (or equivalent); then `prisma.x.update({ where: { id }, data: updateData })`.
   - Single-entity query: return the entity so that GraphQL types match (e.g. convert Prisma Decimal to Number for Float, BigInt to Number if applicable).

5. **Prisma** (`apps/dashboard-server/schema.prisma`)
   - Model X must have a column (or relation) for every field the form and schema use; types must align (e.g. Decimal for money/coords, String[] for string arrays, DateTime for dates).

6. **Run**
   - `yarn workspace @appcaire/graphql codegen` after any schema or operation change.
   - Manually test create and edit: submit form, then load the same entity and confirm all values round-trip.

---

## 5. File reference

| Layer     | Path                                                                                                      |
| --------- | --------------------------------------------------------------------------------------------------------- |
| Forms     | `apps/dashboard/src/components/Resources/{Client,Employee,ServiceArea,Visit}/*Form.tsx`                   |
| Pages     | `apps/dashboard/src/pages/resources/*CreatePage.tsx`, `*EditPage.tsx`                                     |
| Schema    | `packages/graphql/schema/dashboard/types.graphql`, `mutations.graphql`                                    |
| Queries   | `packages/graphql/operations/queries/dashboard/{client,employee,serviceArea,visit}.graphql`               |
| Mutations | `packages/graphql/operations/mutations/dashboard/create*.graphql`, `update*.graphql`                      |
| Resolvers | `apps/dashboard-server/src/graphql/resolvers/{client,employee,service-area,visit}/mutations/`, `queries/` |
| Prisma    | `apps/dashboard-server/schema.prisma`                                                                     |
