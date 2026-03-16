# Field resolvers using Prisma – audit (dashboard-server)

**Scope:** `apps/dashboard-server/src/graphql/resolvers` only.  
**Purpose:** List every field resolver that runs `prisma.*` / `context.prisma`, map to parent loaders, and recommend includes so resolvers can become `return parent.relation`.

---

## 1. Field resolvers that use Prisma

| File                                                     | GraphQL type & field                    | Prisma query                                                                                                 |
| -------------------------------------------------------- | --------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `visit/resolvers/client.ts`                              | `Visit.client`                          | `prisma.visit.findUnique` with `include: { client: true }`                                                   |
| `visit/resolvers/schedule.ts`                            | `Visit.schedule`                        | `prisma.schedule.findUnique` by `parent.scheduleId`                                                          |
| `visit/resolvers/tags.ts`                                | `Visit.tags`                            | `prisma.visitTag.findMany` by `visitId`, `include: { tag: true }`                                            |
| `visit/resolvers/skills.ts`                              | `Visit.skills`                          | `prisma.visitSkill.findMany` by `visitId`, `include: { skill: true }`                                        |
| `visit/resolvers/inset.ts`                               | `Visit.inset`                           | `prisma.inset.findUnique` by `parent.insetId`                                                                |
| `visit/resolvers/groupMemberships.ts`                    | `Visit.groupMemberships`                | `prisma.visitGroupMember.findMany` by `visitId`, `include: { visitGroup: true }`                             |
| `visit/resolvers/visitGroup.ts`                          | `Visit.visitGroup`                      | `prisma.visitGroupMember.findFirst` by `visitId`, `include: { visitGroup: true }`                            |
| `visit/resolvers/requiredStaff.ts`                       | `Visit.requiredStaff`                   | `prisma.visitGroupMember.count` by `visitId` (computed)                                                      |
| `visit/resolvers/visitNotes.ts`                          | `Visit.visitNotes`                      | `prisma.visitNote.findMany` by `visitId`                                                                     |
| `visit/resolvers/visitNoteEmployee.ts`                   | `VisitNote.employee`                    | `prisma.employee.findUnique` by `parent.employeeId`                                                          |
| `visit/resolvers/visitNoteVisit.ts`                      | `VisitNote.visit`                       | `prisma.visit.findUnique` by `parent.visitId`                                                                |
| `visitGroup/resolvers/visitGroupFields.ts`               | `VisitGroup.schedule`                   | `prisma.schedule.findUnique` by `parent.scheduleId`                                                          |
| `visitGroup/resolvers/visitGroupFields.ts`               | `VisitGroup.members`                    | `prisma.visitGroupMember.findMany` by `visitGroupId`, `include: { visit: true }`                             |
| `visitGroup/resolvers/visitGroupMemberFields.ts`         | `VisitGroupMember.visitGroup`           | `prisma.visitGroup.findUnique` by `parent.visitGroupId`                                                      |
| `visitGroup/resolvers/visitGroupMemberFields.ts`         | `VisitGroupMember.visit`                | `prisma.visit.findUnique` by `parent.visitId`                                                                |
| `visitDependency/resolvers/visitDependency.ts`           | `VisitDependency.precedingVisit`        | `prisma.visit.findUniqueOrThrow` by `parent.precedingVisitId`                                                |
| `visitDependency/resolvers/visitDependency.ts`           | `VisitDependency.succeedingVisit`       | `prisma.visit.findUniqueOrThrow` by `parent.succeedingVisitId`                                               |
| `visitDependency/resolvers/serviceAreaDependencyRule.ts` | `ServiceAreaDependencyRule.serviceArea` | `prisma.serviceArea.findUniqueOrThrow` by `parent.serviceAreaId`                                             |
| `visitDependency/resolvers/serviceAreaDependencyRule.ts` | `ServiceAreaDependencyRule.inset`       | `prisma.inset.findUnique` by `parent.insetId`                                                                |
| `visitDependency/resolvers/clientDependencyRule.ts`      | `ClientDependencyRule.client`           | `prisma.client.findUniqueOrThrow` by `parent.clientId`                                                       |
| `visitDependency/resolvers/clientDependencyRule.ts`      | `ClientDependencyRule.inset`            | `prisma.inset.findUnique` by `parent.insetId`                                                                |
| `solution/resolvers/scheduleEmployee.ts`                 | `SolutionAssignment.scheduleEmployee`   | `prisma.solutionAssignment.findUnique` with `include: { scheduleEmployee: { include: { employee: true } } }` |
| `solution/resolvers/employeeMetricsEmployee.ts`          | `EmployeeSolutionMetrics.employee`      | `prisma.employee.findUnique` by `parent.employeeId`                                                          |
| `solution/resolvers/employeeForEvent.ts`                 | `SolutionEvent.employee`                | `prisma.employee.findUnique` by `parent.employeeId`                                                          |
| `schedule/resolvers/visitGroups.ts`                      | `Schedule.visitGroups`                  | `prisma.visitGroup.findMany` by `scheduleId`, `include: { members: { include: { visit: true } } }`           |
| `monthlyAllocation/resolvers/usedMinutes.ts`             | `MonthlyAllocation.usedMinutes`         | `prisma.visit.findMany` (aggregate by clientId/dates) – **computed**, not a relation                         |
| `monthlyAllocation/resolvers/remainingMinutes.ts`        | `MonthlyAllocation.remainingMinutes`    | same – **computed**, not a relation                                                                          |
| `insetGroup/resolvers/insetGroupFields.ts`               | `InsetGroup.members`                    | `prisma.insetGroupMember.findMany` by `insetGroupId`, `include: { inset: true }`                             |
| `insetGroup/resolvers/insetGroupFields.ts`               | `InsetGroupMember.inset`                | `prisma.inset.findUnique` by `parent.insetId`                                                                |
| `inset/resolvers/insetFields.ts`                         | `Inset.defaultDaySlot`                  | `prisma.daySlot.findUnique` by `parent.defaultDaySlotId`                                                     |
| `employee/resolvers/tags.ts`                             | `Employee.tags`                         | `prisma.employeeTag.findMany` by `employeeId` (or uses `parent.tags` if present)                             |
| `employee/resolvers/skills.ts`                           | `Employee.skills`                       | `prisma.employeeSkill.findMany` by `employeeId`, `include: { skill: true }`                                  |

---

## 2. Queries/mutations that return these types and their current include/select

### Visit (parent of client, schedule, tags, skills, inset, groupMemberships, visitGroup, requiredStaff, visitNotes)

| File                                           | Current include/select                                                                                                                                        |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visit/queries/visit.ts`                       | `include: { schedule: { select: { organizationId: true } } }`. No client, tags, skills, inset, groupMemberships, visitNotes.                                  |
| `visit/queries/visits.ts`                      | No include (plain `findMany`).                                                                                                                                |
| `visit/queries/unassignedVisitsForSolution.ts` | No include on visits (separate findMany).                                                                                                                     |
| `schedule/queries/schedule.ts`                 | `include: { visits: { orderBy: ... }, employees: { include: { employee: true } } }`. Visits have no nested includes.                                          |
| `schedule/queries/schedules.ts`                | Visits loaded via separate `visit.findMany`; no nested includes.                                                                                              |
| `solution/queries/solutionAssignments.ts`      | `visit: { include: { client: { include: { primaryAddress: true } }, visitTemplate: true } }`. No tags, skills, inset, groupMemberships, visitNotes, schedule. |

### VisitNote (parent of employee, visit)

| File                                 | Current include/select                                                                            |
| ------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `visit/resolvers/visitNotes.ts`      | Loads notes with `prisma.visitNote.findMany` – no `include: { employee: true }` or `visit: true`. |
| `visit/mutations/createVisitNote.ts` | Returns created note; no `include: { employee: true }`.                                           |

### VisitGroup (parent of schedule, members)

| File                                | Current include/select                                                                                                                                                      |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visitGroup/queries/visitGroup.ts`  | `include: { schedule: { select: { organizationId: true } }, members: { include: { visit: true } } }`. Schedule and members are loaded; members do not include `visitGroup`. |
| `visitGroup/queries/visitGroups.ts` | `include: { members: { include: { visit: true } } }`. No `schedule`; members do not include `visitGroup`.                                                                   |

### VisitGroupMember (parent of visitGroup, visit)

| File                                                                                                                | Current include/select                                                                |
| ------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- |
| Loaded only as nested under VisitGroup (in visitGroup, visitGroups) or under Schedule.visitGroups (field resolver). | visitGroup: `members: { include: { visit: true } }` – no `visitGroup` on each member. |

### VisitDependency (parent of precedingVisit, succeedingVisit)

| File                                                   | Current include/select                                                                            |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| `visitDependency/queries/visitDependency.ts`           | `include: { schedule: { select: { organizationId: true } } }`. No precedingVisit/succeedingVisit. |
| `visitDependency/queries/visitDependenciesForVisit.ts` | No include on dependencies (plain findMany).                                                      |

### ServiceAreaDependencyRule (parent of serviceArea, inset)

| File                                                   | Current include/select                                                      |
| ------------------------------------------------------ | --------------------------------------------------------------------------- |
| `visitDependency/queries/serviceAreaDependencyRule.ts` | `include: { serviceArea: { select: { organizationId: true } } }`. No inset. |

### ClientDependencyRule (parent of client, inset)

| File                                              | Current include/select                                                 |
| ------------------------------------------------- | ---------------------------------------------------------------------- |
| `visitDependency/queries/clientDependencyRule.ts` | `include: { client: { select: { organizationId: true } } }`. No inset. |

### SolutionAssignment (parent of scheduleEmployee)

| File                                      | Current include/select                                                                                                       |
| ----------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| `solution/queries/solutionAssignments.ts` | `include: { solution: true, scheduleEmployee: true, visit: { ... } }`. scheduleEmployee is included but not nested employee. |

### EmployeeSolutionMetrics / SolutionEvent (parent of employee)

| File                                              | Current include/select                |
| ------------------------------------------------- | ------------------------------------- |
| `solution/queries/solutionEvents.ts`              | No include (plain findMany).          |
| Solution metrics / events from other entry points | Same – employee not loaded on events. |

### Schedule (parent of visitGroups)

| File                            | Current include/select                                                                                  |
| ------------------------------- | ------------------------------------------------------------------------------------------------------- |
| `schedule/queries/schedule.ts`  | `include: { visits: {...}, employees: {...} }`. Returns `visitGroups: []` and relies on field resolver. |
| `schedule/queries/schedules.ts` | Same pattern; visitGroups from field resolver.                                                          |

### MonthlyAllocation (parent of usedMinutes, remainingMinutes)

| File                                                     | Current include/select                                                                      |
| -------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| `monthlyAllocation/mutations/updateMonthlyAllocation.ts` | Loads allocation for update; no relation for used/remaining (they are computed from Visit). |
| `monthlyAllocation/mutations/createMonthlyAllocation.ts` | Returns created allocation.                                                                 |
| `client/resolvers/allocations.ts`                        | Returns allocations via `prisma.monthlyAllocation.findMany` – no Visit relation.            |

**Note:** `usedMinutes` and `remainingMinutes` are derived from Visit (filter by clientId + date range). They cannot be replaced by a single `include` on MonthlyAllocation; they must stay as computed field resolvers.

### InsetGroup / InsetGroupMember (parent of members, inset)

| File                                | Current include/select                                                                               |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `insetGroup/queries/insetGroup.ts`  | `include: { members: { include: { inset: true }, orderBy } }`. Members and inset are already loaded. |
| `insetGroup/queries/insetGroups.ts` | Same.                                                                                                |

### Inset (parent of defaultDaySlot)

| File                      | Current include/select |
| ------------------------- | ---------------------- |
| `inset/queries/inset.ts`  | No include.            |
| `inset/queries/insets.ts` | No include.            |

### Employee (parent of tags, skills)

| File                            | Current include/select                                      |
| ------------------------------- | ----------------------------------------------------------- |
| `employee/queries/employee.ts`  | `include: { tags: { include: { tag: true } } }`. No skills. |
| `employee/queries/employees.ts` | Same.                                                       |

---

## 3. Structured list: field resolver → parent type & field → Prisma in resolver → loader → include to add

| Field resolver file                                           | Parent type & field                             | Prisma query in resolver                                    | Query/mutation that loads parent                                                                       | Include to add (so resolver can be `return parent.relation`)                                                                                                                                                         |
| ------------------------------------------------------------- | ----------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `visit/resolvers/client.ts`                                   | Visit.client                                    | visit.findUnique + client                                   | visit.ts, visits.ts, schedule.ts, schedules.ts, unassignedVisitsForSolution.ts, solutionAssignments.ts | In each Visit loader: `client: true` (and handle deleted client in mapper or resolver).                                                                                                                              |
| `visit/resolvers/schedule.ts`                                 | Visit.schedule                                  | schedule.findUnique                                         | Same as above                                                                                          | In each Visit loader: `schedule: true` (or keep schedule for org check and pass through).                                                                                                                            |
| `visit/resolvers/tags.ts`                                     | Visit.tags                                      | visitTag.findMany + tag                                     | Same                                                                                                   | `tags: { include: { tag: true }, orderBy: { createdAt: 'asc' } }`.                                                                                                                                                   |
| `visit/resolvers/skills.ts`                                   | Visit.skills                                    | visitSkill.findMany + skill                                 | Same                                                                                                   | `skills: { include: { skill: true }, orderBy: { createdAt: 'asc' } }`.                                                                                                                                               |
| `visit/resolvers/inset.ts`                                    | Visit.inset                                     | inset.findUnique                                            | Same                                                                                                   | `inset: true` (or omit when insetId null).                                                                                                                                                                           |
| `visit/resolvers/groupMemberships.ts`                         | Visit.groupMemberships                          | visitGroupMember.findMany + visitGroup                      | Same                                                                                                   | `groupMemberships` or custom load: not a direct Prisma relation name – either add a virtual/custom include or keep resolver and batch.                                                                               |
| `visit/resolvers/visitGroup.ts`                               | Visit.visitGroup                                | visitGroupMember.findFirst + visitGroup                     | Same                                                                                                   | Can be derived from groupMemberships if loaded; else keep resolver or add batched load.                                                                                                                              |
| `visit/resolvers/requiredStaff.ts`                            | Visit.requiredStaff                             | visitGroupMember.count                                      | Same                                                                                                   | Cannot be “include” (count). Keep as field resolver or add computed field in loader.                                                                                                                                 |
| `visit/resolvers/visitNotes.ts`                               | Visit.visitNotes                                | visitNote.findMany                                          | Same                                                                                                   | `visitNotes: { include: { employee: true }, orderBy: { createdAt: 'desc' } }` so VisitNote.employee can become pass-through.                                                                                         |
| `visit/resolvers/visitNoteEmployee.ts`                        | VisitNote.employee                              | employee.findUnique                                         | visitNotes (field), createVisitNote                                                                    | In visitNotes loader: `visitNotes: { include: { employee: true } }`; in createVisitNote: return with `include: { employee: true }`.                                                                                  |
| `visit/resolvers/visitNoteVisit.ts`                           | VisitNote.visit                                 | visit.findUnique                                            | Same                                                                                                   | In visitNotes: include visit (e.g. minimal select) or resolve from parent.visitId; createVisitNote: optional include visit for consistency.                                                                          |
| `visitGroup/resolvers/visitGroupFields.ts` (schedule)         | VisitGroup.schedule                             | schedule.findUnique                                         | visitGroup.ts, visitGroups.ts, schedule.visitGroups                                                    | visitGroup.ts: already has schedule (select). visitGroups.ts: add `schedule: { select: { organizationId: true } }` (or full schedule). schedule.ts: when adding visitGroups include, include schedule on each group. |
| `visitGroup/resolvers/visitGroupFields.ts` (members)          | VisitGroup.members                              | visitGroupMember.findMany + visit                           | visitGroup.ts, visitGroups.ts                                                                          | Both already have `members: { include: { visit: true } }`. Add `visitGroup: true` on each member so VisitGroupMember.visitGroup can be pass-through.                                                                 |
| `visitGroup/resolvers/visitGroupMemberFields.ts` (visitGroup) | VisitGroupMember.visitGroup                     | visitGroup.findUnique                                       | Loaded under VisitGroup.members                                                                        | Add `visitGroup: true` to members include in visitGroup.ts and visitGroups.ts.                                                                                                                                       |
| `visitGroup/resolvers/visitGroupMemberFields.ts` (visit)      | VisitGroupMember.visit                          | visit.findUnique                                            | Same                                                                                                   | Already have `visit: true` on members; resolver can become `return parent.visit`.                                                                                                                                    |
| `visitDependency/resolvers/visitDependency.ts`                | VisitDependency.precedingVisit, succeedingVisit | visit.findUniqueOrThrow x2                                  | visitDependency.ts, visitDependenciesForVisit.ts                                                       | Add `include: { precedingVisit: true, succeedingVisit: true }` (or minimal select) in both.                                                                                                                          |
| `visitDependency/resolvers/serviceAreaDependencyRule.ts`      | ServiceAreaDependencyRule.serviceArea, inset    | serviceArea.findUniqueOrThrow, inset.findUnique             | serviceAreaDependencyRule.ts                                                                           | Already has serviceArea. Add `inset: true`.                                                                                                                                                                          |
| `visitDependency/resolvers/clientDependencyRule.ts`           | ClientDependencyRule.client, inset              | client.findUniqueOrThrow, inset.findUnique                  | clientDependencyRule.ts                                                                                | Already has client. Add `inset: true`.                                                                                                                                                                               |
| `solution/resolvers/scheduleEmployee.ts`                      | SolutionAssignment.scheduleEmployee             | solutionAssignment.findUnique + scheduleEmployee + employee | solutionAssignments.ts                                                                                 | Already has `scheduleEmployee: true`. Add `scheduleEmployee: { include: { employee: true } }` if GraphQL exposes nested employee; then resolver can return parent.scheduleEmployee.                                  |
| `solution/resolvers/employeeMetricsEmployee.ts`               | EmployeeSolutionMetrics.employee                | employee.findUnique                                         | Queries that return EmployeeSolutionMetrics (e.g. solution metrics)                                    | Load employee in the query that returns metrics (e.g. include/join by employeeId).                                                                                                                                   |
| `solution/resolvers/employeeForEvent.ts`                      | SolutionEvent.employee                          | employee.findUnique                                         | solutionEvents.ts                                                                                      | Add `include: { employee: true }` to solutionEvent.findMany in solutionEvents.ts.                                                                                                                                    |
| `schedule/resolvers/visitGroups.ts`                           | Schedule.visitGroups                            | visitGroup.findMany + members + visit                       | schedule.ts, schedules.ts                                                                              | In schedule.ts: add `visitGroups: { include: { members: { include: { visit: true, visitGroup: true } } }, orderBy: { createdAt: 'asc' } }`. In schedules.ts: same for the batch load of visit groups per schedule.   |
| `monthlyAllocation/resolvers/usedMinutes.ts`                  | MonthlyAllocation.usedMinutes                   | visit.findMany (aggregate)                                  | updateMonthlyAllocation, createMonthlyAllocation, client allocations                                   | N/A – computed; keep as resolver.                                                                                                                                                                                    |
| `monthlyAllocation/resolvers/remainingMinutes.ts`             | MonthlyAllocation.remainingMinutes              | same                                                        | Same                                                                                                   | N/A – computed; keep as resolver.                                                                                                                                                                                    |
| `insetGroup/resolvers/insetGroupFields.ts` (members)          | InsetGroup.members                              | insetGroupMember.findMany + inset                           | insetGroup.ts, insetGroups.ts                                                                          | Already have `members: { include: { inset: true } }`; resolver can become `return parent.members`.                                                                                                                   |
| `insetGroup/resolvers/insetGroupFields.ts` (inset)            | InsetGroupMember.inset                          | inset.findUnique                                            | Same                                                                                                   | Already included; resolver can become `return parent.inset`.                                                                                                                                                         |
| `inset/resolvers/insetFields.ts`                              | Inset.defaultDaySlot                            | daySlot.findUnique                                          | inset.ts, insets.ts                                                                                    | Add `defaultDaySlot: true` (or `include: { defaultDaySlot: true }`) in inset.ts and insets.ts.                                                                                                                       |
| `employee/resolvers/tags.ts`                                  | Employee.tags                                   | employeeTag.findMany or parent.tags                         | employee.ts, employees.ts                                                                              | Already have `tags: { include: { tag: true } }`; resolver can return parent.tags (with mapping if needed).                                                                                                           |
| `employee/resolvers/skills.ts`                                | Employee.skills                                 | employeeSkill.findMany + skill                              | employee.ts, employees.ts                                                                              | Add `skills: { include: { skill: true }, orderBy: { createdAt: 'desc' } }` in both.                                                                                                                                  |

---

## Summary

- **Visit**: Most impact. Add `client`, `schedule`, `tags`, `skills`, `inset`, and `visitNotes` (with `employee` and optionally `visit`) in every place that loads Visit (visit, visits, schedule, schedules, unassignedVisitsForSolution, solutionAssignments). `groupMemberships` / `visitGroup` / `requiredStaff` need either a relation or batched/computed handling.
- **VisitNote**: Load `employee` (and optionally `visit`) where VisitNotes are loaded (visitNotes field resolver, createVisitNote).
- **VisitGroup**: visitGroups query should include `schedule`. VisitGroup.members should include `visitGroup` so VisitGroupMember resolvers can be pass-through.
- **VisitDependency**: Include `precedingVisit` and `succeedingVisit` where dependencies are loaded. ServiceAreaDependencyRule and ClientDependencyRule: add `inset`.
- **Solution**: solutionEvents should include `employee`. solutionAssignments already includes scheduleEmployee; add nested employee if needed.
- **Schedule**: Add `visitGroups` (with members and visitGroup on members) in schedule and schedules.
- **MonthlyAllocation**: usedMinutes/remainingMinutes stay as computed resolvers.
- **InsetGroup/InsetGroupMember**: Already loaded; resolvers can become `return parent.members` / `return parent.inset`.
- **Inset**: Add `defaultDaySlot` in inset and insets.
- **Employee**: Already have tags; add `skills` (with skill) in employee and employees; tags resolver can use parent when present.
