# Org-scoped data – no system-level catalog

**Status:** All catalog and resource data in dashboard-server is **org-scoped**. There is no system-level or shared data between organizations.

## Scope

- **Skill**, **Inset**, **DaySlot**, **InsetGroup**: All are created with `organizationId` set and `isSystemLevel: false`. Resolvers and services filter only on `organizationId`; no queries include `organizationId = null` or system-level rows.
- **Other models** (Organization, Client, Employee, Visit, Schedule, ServiceArea, Tag, etc.) are already org- or resource-linked.

## Implementation details

| Area                      | Behavior                                                                                                                                                                                                                 |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Seed**                  | `seed-org-defaults.ts` exposes `seedDefaultsForOrganization(organizationId, tx)`. No global catalog; each org is seeded per organization.                                                                                |
| **seed-attendo**          | Creates org first, then calls `seedDefaultsForOrganization(organization.id, tx)` in the same transaction.                                                                                                                |
| **List/single resolvers** | insets, daySlots, insetGroups, skills (and single: inset, daySlot, insetGroup, skill) use only `organizationId` in `where`. Rows with `organizationId == null` are not returned; single resolvers return null/NOT_FOUND. |
| **Mutations**             | create/update/delete require org membership via `validateOrganizationId`; no SUPER_ADMIN branch for system-level.                                                                                                        |
| **Upload/Timefold**       | `uploadScheduleForOrganization` and `buildTimefoldModelInput` fetch insets/skills with `where: { organizationId }`.                                                                                                      |

## Schema

In Prisma, Skill, Inset, DaySlot, and InsetGroup still have `organizationId String?` and `isSystemLevel Boolean` for backward compatibility. Comments state that the app uses only org-scoped data; system-level is not used.

## Verification

- No `OR` conditions that include `organizationId: null` in dashboard-server for these models.
- All org catalog is created via `seedDefaultsForOrganization(orgId, tx)` (bootstrap-org, seed-attendo, or db:seed:org-defaults).
- Documentation: `docs/docs_2.0/09-scheduling/SEED_DATA_SYSTEM_SETTINGS.md` describes org-scoped seeding.

_Last updated: 2026-03-11_
