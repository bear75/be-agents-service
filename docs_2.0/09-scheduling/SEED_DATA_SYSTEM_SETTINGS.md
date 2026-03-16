# Seed Data for Resources and System Settings

All catalog data (DaySlots, Insets, InsetGroups, Skills) is **org-scoped**. There is no system-level or shared data between organizations.

**Related files:**

- `apps/dashboard-server/src/seed-attendo.ts` – Full Attendo Huddinge demo
- `apps/dashboard-server/src/seed-org-defaults.ts` – Org default catalog (DaySlots, Insets, InsetGroups, Skills); used by bootstrap and seed-attendo
- `apps/dashboard-server/src/seed-org-bootstrap.ts` – CLI: bootstrap one org (Clerk webhook / manual: db:seed:org)
- `apps/dashboard-server/src/services/bootstrap-org.ts` – Bootstrap logic
- `apps/dashboard-server/src/seed.ts` – **Deprecated.** Legacy seed (Stockholm Hemtjänst AB). Prefer seed-org-bootstrap + seed-org-defaults or seed-attendo.

---

## 1. Org-scoped catalog (no system-level data)

- **seed-org-defaults.ts** exports `seedDefaultsForOrganization(organizationId, tx)` which creates DaySlots, Insets, InsetGroups, and Skills **for a specific organization** (all with `organizationId` set, `isSystemLevel: false`). Called by bootstrap-org.ts (on new org) and by seed-attendo.ts (Attendo demo).
- **seed-attendo.ts** creates the organization first, then calls `seedDefaultsForOrganization(organization.id, tx)` in the same transaction, so the Attendo org gets its own catalog.
- **Resolvers** (insets, daySlots, insetGroups, skills) filter only on `organizationId`; no data with `organizationId = null` is used or returned.
- **Bootstrap** (bootstrap-org.ts) calls `seedDefaultsForOrganization` when a new org is created, so new orgs get the default catalog immediately. To (re)seed an existing org’s catalog: `ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults [--reset]`.

### 1.1 DaySlots (time windows) – per org

These values are defined in `seed-org-defaults.ts` (`SYSTEM_DAY_SLOTS`) and used when seeding an org’s catalog.

| name        | displayName       | startTime | endTime | sequence |
| ----------- | ----------------- | --------- | ------- | -------- |
| morgon      | Morgon            | 07:00     | 10:00   | 1        |
| formiddag   | Förmiddag         | 10:00     | 11:30   | 2        |
| lunch       | Lunch             | 11:30     | 13:30   | 3        |
| eftermiddag | Eftermiddag       | 13:30     | 15:00   | 4        |
| middag      | Middag            | 16:00     | 19:00   | 5        |
| kvall       | Kväll             | 19:00     | 22:00   | 6        |
| natt        | Natt              | 22:00     | 07:00   | 7        |
| custom      | Custom / Flexible | 00:00     | 23:59   | 98       |

### 1.2 Insets (visit types) – per org

About 30 standard Insets with categories: `personal_care`, `meals`, `daily_support`, `supervision`, `household`, `social_activities`. Fields: `name`, `displayName`, `category`, `defaultSpreadDelay`, `defaultDaySlotId`, `defaultPriority`, etc.

### 1.3 InsetGroups – per org

| name               | displayName                         | spreadDelay | members                            |
| ------------------ | ----------------------------------- | ----------- | ---------------------------------- |
| meals              | Måltider (Frukost → Lunch → Middag) | PT3H        | breakfast, lunch_time, dinner_time |
| daily_care_routine | Daglig vårdrutin (Morgon → Kväll)   | PT6H        | morning_care, evening              |

### 1.4 Skills (catalog) – per org

12 standard skills (language, certifications, medical, gender preference, allergy, etc.). All created with `organizationId` set.

**Command to seed an existing org’s catalog:**  
`ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults [--reset]`

That command also ensures one default service area ("Huvudområde") if the org has none (for the Upload Schedule Wizard). See [SEED_VS_CSV_UPLOAD.md](./SEED_VS_CSV_UPLOAD.md).

---

## 2. seed-org-bootstrap.ts / bootstrap-org.ts

Used when creating a new organization (Clerk webhook or manual run with `CLERK_ORG_ID`, `ORG_NAME`, `ORG_SLUG`).

- **Organization:** name, slug, clerkId, status, settings.
- **OrganizationMember (optional):** If `CLERK_USER_ID` is provided: one member with `role: ADMIN`.
- **OperationalSettings, ServiceArea:** Created with default values.
- **Default catalog:** bootstrap-org calls `seedDefaultsForOrganization(organization.id, tx)` so new orgs get DaySlots, Insets, InsetGroups, and Skills immediately.

---

## 3. seed-attendo.ts (full demo)

- Creates the **organization** first.
- Calls **seedDefaultsForOrganization(organization.id, tx)** in the same transaction → org-specific DaySlots, Insets, InsetGroups, Skills.
- Creates remaining resources: OperationalSettings, ServiceArea, clients, employees, schedule, visits, rules.
- Does **not** rely on any system-level catalog.

---

## 4. seed.ts (deprecated)

- **Deprecated.** Legacy seed for organization “Stockholm Hemtjänst AB”.
- Does **not** seed DaySlots, Insets, InsetGroups, Skills. For full behavior use `seedDefaultsForOrganization` for that org (e.g. via script with ORGANIZATION_ID) or use seed-attendo as reference.

---

## 5. Summary – org-scoped data

| Entity          | System-level | Org-level | Note                                 |
| --------------- | ------------ | --------- | ------------------------------------ |
| DaySlots        | No           | Yes       | Only via seedDefaultsForOrganization |
| Insets          | No           | Yes       | Only via seedDefaultsForOrganization |
| InsetGroups     | No           | Yes       | Only via seedDefaultsForOrganization |
| Skills          | No           | Yes       | Only via seedDefaultsForOrganization |
| Organization    | –            | Yes       | Each org has its own data            |
| Other resources | –            | Yes       | Always tied to organizationId        |

**All data is org-scoped; no system-level or shared catalog.**

---

## 6. Command reference

| Command                                                       | Purpose                                                      |
| ------------------------------------------------------------- | ------------------------------------------------------------ |
| `ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults`            | Seed org-specific catalog (DaySlots, Insets, Groups, Skills) |
| `ORGANIZATION_ID=<uuid> yarn db:seed:org-defaults --reset`    | Reset and seed org catalog                                   |
| `CLERK_ORG_ID=... ORG_NAME=... ORG_SLUG=... yarn db:seed:org` | Bootstrap new organization                                   |
| `yarn db:seed:attendo`                                        | Full Attendo Huddinge demo (includes org catalog)            |
| `yarn db:seed:attendo --reset`                                | Truncate and seed Attendo                                    |
| `yarn db:seed`                                                | **Deprecated.** Legacy seed (Stockholm Hemtjänst AB)         |

---

_Last updated: 2026-03-11_
