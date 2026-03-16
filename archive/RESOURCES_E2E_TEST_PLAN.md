# Resources CRUD - E2E Test Plan

> **Branch:** `feat/priority-cascade` (includes all code from `feat/resources-crud-complete`)
> **Created:** 2026-03-08
> **Purpose:** Systematically verify every Resources page works end-to-end

---

## Pre-requisites

- [ ] Dashboard-server running on port 4000
- [ ] Dashboard running on port 3000
- [ ] Database seeded with `seed-attendo` data
- [ ] Logged in as authenticated user with organization access

---

## 1. Organization Resource

### 1.1 Organization Info Tab (`/resources?resource=organization`)

| #   | Test Case                            | Expected                          | Status |
| --- | ------------------------------------ | --------------------------------- | ------ |
| 1   | Page loads without blank screen      | Organization overview renders     |        |
| 2   | Organization name, description shown | Pre-filled from DB                |        |
| 3   | Edit organization info               | Form submits, toast confirms save |        |

### 1.2 Skills Tab (`/resources?resource=organization&tab=skills`)

| #   | Test Case                                      | Expected                | Status |
| --- | ---------------------------------------------- | ----------------------- | ------ |
| 1   | Page loads, shows skills list (or empty state) | No errors               |        |
| 2   | Create a new skill (name, category, level)     | Skill appears in list   |        |
| 3   | Edit an existing skill                         | Changes persist         |        |
| 4   | Delete a skill                                 | Skill removed from list |        |

### 1.3 Tags Tab (`/resources?resource=organization&tab=tags`)

| #   | Test Case                                    | Expected              | Status |
| --- | -------------------------------------------- | --------------------- | ------ |
| 1   | Page loads, shows tags list (or empty state) | No errors             |        |
| 2   | Create a new tag (name, color)               | Tag appears in list   |        |
| 3   | Edit a tag                                   | Changes persist       |        |
| 4   | Delete a tag                                 | Tag removed from list |        |

### 1.4 Insets Tab (`/resources?resource=organization&tab=insets`)

| #   | Test Case                                                            | Expected                | Status |
| --- | -------------------------------------------------------------------- | ----------------------- | ------ |
| 1   | Page loads, shows insets list (or empty state)                       | No errors               |        |
| 2   | Create a new inset (name, displayName, category, duration, priority) | Inset appears in list   |        |
| 3   | Edit an inset                                                        | Changes persist         |        |
| 4   | Delete an inset                                                      | Inset removed from list |        |

### 1.5 Inset Groups Tab (`/resources?resource=organization&tab=inset-groups`)

| #   | Test Case                                            | Expected              | Status |
| --- | ---------------------------------------------------- | --------------------- | ------ |
| 1   | Page loads, shows inset groups list (or empty state) | No errors             |        |
| 2   | Create a new inset group                             | Group appears in list |        |
| 3   | Add members to inset group                           | Members shown         |        |
| 4   | Delete inset group                                   | Group removed         |        |

### 1.6 Day Slots Tab (`/resources?resource=organization&tab=day-slots`)

| #   | Test Case                                         | Expected               | Status |
| --- | ------------------------------------------------- | ---------------------- | ------ |
| 1   | Page loads, shows day slots list (or empty state) | No errors              |        |
| 2   | Create a new day slot (name, startTime, endTime)  | Slot appears in list   |        |
| 3   | Edit a day slot                                   | Changes persist        |        |
| 4   | Delete a day slot                                 | Slot removed from list |        |

### 1.7 Operational Settings Tab (`/resources?resource=organization&tab=operational`)

| #   | Test Case                                   | Expected                           | Status |
| --- | ------------------------------------------- | ---------------------------------- | ------ |
| 1   | Page loads, shows operational settings form | Form renders                       |        |
| 2   | Modify default hourly salary                | Value saves and persists on reload |        |
| 3   | Modify overhead percentage                  | Value saves and persists           |        |
| 4   | Modify travel time multiplier               | Value saves and persists           |        |
| 5   | Modify fairness/continuity/cost weights     | Values save and persist            |        |
| 6   | Modify revenue per hour                     | Value saves and persists           |        |
| 7   | Submit form, check toast                    | Success feedback shown             |        |

---

## 2. Service Area Resource

### 2.1 Service Area List (`/resources?resource=service-areas`)

| #   | Test Case                               | Expected               | Status |
| --- | --------------------------------------- | ---------------------- | ------ |
| 1   | Page loads, shows list of service areas | No errors              |        |
| 2   | Click on a service area                 | Navigates to edit page |        |
| 3   | Delete a service area                   | Removed from list      |        |

### 2.2 Create Service Area (`/resources/service-areas/new`)

| #   | Test Case                          | Expected                          | Status |
| --- | ---------------------------------- | --------------------------------- | ------ |
| 1   | Form loads without errors          | All fields render                 |        |
| 2   | Submit empty form                  | Validation errors shown inline    |        |
| 3   | Fill required fields and submit    | Service area created, toast shown |        |
| 4   | Set costPerHour and revenuePerHour | Values persist in DB              |        |
| 5   | Set latitude/longitude             | Values persist in DB              |        |

### 2.3 Edit Service Area (`/resources/service-areas/:id/edit`)

| #   | Test Case                                      | Expected                 | Status |
| --- | ---------------------------------------------- | ------------------------ | ------ |
| 1   | Page loads with pre-filled data                | All fields populated     |        |
| 2   | Modify name and save                           | Change persists          |        |
| 3   | Modify costPerHour (e.g. 550)                  | DB shows 550 on reload   |        |
| 4   | Modify revenuePerHour                          | DB shows value on reload |        |
| 5   | Modify externalId                              | Value persists           |        |
| 6   | Dependency Rules tab: create/edit/delete rules | Rules CRUD works         |        |

---

## 3. Employee Resource

### 3.1 Employee List (`/resources?resource=employees`)

| #   | Test Case                           | Expected               | Status |
| --- | ----------------------------------- | ---------------------- | ------ |
| 1   | Page loads, shows list of employees | No errors              |        |
| 2   | Click on an employee                | Navigates to edit page |        |
| 3   | Delete an employee                  | Removed from list      |        |

### 3.2 Create Employee (`/resources/employees/new`)

| #   | Test Case                                                    | Expected                       | Status |
| --- | ------------------------------------------------------------ | ------------------------------ | ------ |
| 1   | Form loads without errors                                    | All fields render              |        |
| 2   | Submit empty form                                            | Validation errors shown inline |        |
| 3   | Fill required fields (firstName, lastName, email) and submit | Employee created               |        |
| 4   | Set service area                                             | Service area assigned          |        |
| 5   | Set transport mode, driver license type                      | Values persist in DB           |        |
| 6   | Set contracted hours per week                                | Value persists in DB           |        |
| 7   | Set home latitude/longitude                                  | Values persist in DB           |        |
| 8   | Set default hourly salary                                    | Creates EmployeeCost record    |        |

### 3.3 Edit Employee (`/resources/employees/:id/edit`)

| #   | Test Case                                                    | Expected               | Status |
| --- | ------------------------------------------------------------ | ---------------------- | ------ |
| 1   | Page loads with pre-filled data                              | All fields populated   |        |
| 2   | Modify name and save                                         | Change persists        |        |
| 3   | Skills tab: add/remove skills                                | Skills persist         |        |
| 4   | Tags tab: add/remove tags                                    | Tags persist           |        |
| 5   | Cost Periods: add new cost period with hourly salary 300 SEK | EmployeeCost row in DB |        |
| 6   | Cost Periods: edit existing cost period                      | Changes persist        |        |
| 7   | Cost Periods: delete cost period                             | Row removed from DB    |        |
| 8   | Preferences: add/edit/delete preferences                     | Preferences CRUD works |        |

---

## 4. Client Resource

### 4.1 Client List (`/resources?resource=clients`)

| #   | Test Case                         | Expected               | Status |
| --- | --------------------------------- | ---------------------- | ------ |
| 1   | Page loads, shows list of clients | No errors              |        |
| 2   | Click on a client                 | Navigates to edit page |        |
| 3   | Delete a client                   | Removed from list      |        |

### 4.2 Create Client (`/resources/clients/new`)

| #   | Test Case                       | Expected                       | Status |
| --- | ------------------------------- | ------------------------------ | ------ |
| 1   | Form loads without errors       | All fields render              |        |
| 2   | Submit empty form               | Validation errors shown inline |        |
| 3   | Fill required fields and submit | Client created                 |        |
| 4   | Set latitude/longitude          | Values persist in DB           |        |
| 5   | Set service area                | Value persists                 |        |

### 4.3 Edit Client (`/resources/clients/:id/edit`)

| #   | Test Case                                      | Expected                                         | Status |
| --- | ---------------------------------------------- | ------------------------------------------------ | ------ |
| 1   | Page loads with pre-filled data                | All fields populated                             |        |
| 2   | Modify name and save                           | Change persists                                  |        |
| 3   | Addresses tab: add/edit/delete addresses       | Addresses CRUD works, latitude/longitude persist |        |
| 4   | Contacts tab: add/edit/delete contacts         | Contacts CRUD works                              |        |
| 5   | Skills tab: add/remove skills                  | Skills persist                                   |        |
| 6   | Preferences tab: add/edit/delete preferences   | Preferences CRUD works                           |        |
| 7   | Dependency Rules tab: create/edit/delete rules | Rules CRUD works                                 |        |
| 8   | Monthly Allocations tab: create/edit/delete    | Allocations CRUD works                           |        |

---

## 5. Visit Resource

### 5.1 Create Visit (`/resources/visits/new`)

| #   | Test Case                                                 | Expected                       | Status |
| --- | --------------------------------------------------------- | ------------------------------ | ------ |
| 1   | Form loads without errors                                 | All fields render              |        |
| 2   | Submit empty form                                         | Validation errors shown inline |        |
| 3   | Fill required fields (scheduleId, clientId, dates, times) | Visit created                  |        |
| 4   | Set priority, category                                    | Values persist                 |        |
| 5   | Set insetId                                               | Value persists                 |        |
| 6   | Skills: add/remove skills                                 | Skills persist                 |        |
| 7   | Tags: add/remove tags                                     | Tags persist                   |        |
| 8   | Visit Groups: assign to visit group                       | Membership persists            |        |
| 9   | Dependencies: add visit dependency                        | Dependency persists            |        |

### 5.2 Edit Visit (`/resources/visits/:id/edit`)

| #   | Test Case                       | Expected                      | Status |
| --- | ------------------------------- | ----------------------------- | ------ |
| 1   | Page loads with pre-filled data | All fields populated          |        |
| 2   | Modify duration and save        | Change persists               |        |
| 3   | Delete visit                    | Visit removed, navigates back |        |

---

## 6. Cross-Cutting Concerns

### 6.1 Translations

| #   | Test Case                                             | Expected                       | Status |
| --- | ----------------------------------------------------- | ------------------------------ | ------ |
| 1   | All form labels display translated text (no raw keys) | No `resources.xxx` shown as-is |        |
| 2   | All toast messages show translated text               | No raw keys                    |        |
| 3   | All error messages show translated text               | No raw keys                    |        |
| 4   | Inset pages use i18n (not hardcoded Swedish)          | All strings via `t()`          |        |

### 6.2 UI Feedback

| #   | Test Case                          | Expected                             | Status |
| --- | ---------------------------------- | ------------------------------------ | ------ |
| 1   | Required field left empty + submit | Inline validation error shown        |        |
| 2   | Successful save                    | Toast notification "Saved"           |        |
| 3   | API error on save                  | Error alert/toast shown with message |        |
| 4   | Loading states                     | Spinner/disabled buttons during save |        |

### 6.3 Common Components

| #   | Test Case                                               | Expected         | Status |
| --- | ------------------------------------------------------- | ---------------- | ------ |
| 1   | SkillSelector: shows skills if defined, warning if none | Correct UX       |        |
| 2   | TagSelector: shows tags if defined                      | Correct UX       |        |
| 3   | InsetSelector: shows insets                             | Correct UX       |        |
| 4   | AddressWithLocation: geocode button works               | Address geocoded |        |

---

## Known Bugs Found During Audit

### CRITICAL

1. **Client type resolvers not registered** - Root `resolvers/index.ts` missing `Client: clientResolvers.Client`. Client addresses, contacts, skills, preferences, and monthly allocations will NOT resolve.

### HIGH

2. **createEmployee/updateEmployee missing Decimal conversion** - `homeLatitude`, `homeLongitude`, `contractedHoursPerWeek`, `employmentPercentage`, `maxHoursPerDay`, `maxHoursPerWeek` passed as raw numbers instead of `Prisma.Decimal`.
3. **createAddress/updateAddress missing Decimal conversion** - `latitude`, `longitude` not converted on input or output.
4. **updateOperationalSettings Decimal conversion** - `defaultHourlySalary`, `overtimeMultiplier`, `revenuePerHour`, `overheadPercentage`, `travelTimeMultiplier` passed as raw numbers.
5. **updateVisit not using mapVisit()** - Check-in/check-out coordinate Decimals not converted to Number on output.

### MEDIUM

6. **~20+ missing translation keys** - Various `resources.skills.*`, `common.saved`, `common.actions`, `resources.visits.form.*` keys.
7. **InsetManagement/InsetFormDialog hardcoded Swedish** - Not using `t()` for strings like "Insats skapad", "Insats uppdaterad".

---

## Verification Process

For each page:

1. Open in browser at `http://localhost:3000/resources?resource=...`
2. Check page loads without errors (no blank page)
3. Check all data fields display correctly
4. Test Create flow (submit form, verify DB)
5. Test Edit flow (modify field, save, reload, verify)
6. Test Delete flow (delete, verify removed)
7. Check console for errors
8. Verify translations render (no raw i18n keys visible)
