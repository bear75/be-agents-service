# Dashboard navigation audit

> **Purpose:** Ensure every route has at least one visible way to reach it from the UI. Avoid "hidden" features.

## Why client visits was missing

The **Client visits** page (`/resources/clients/:clientId/visits`) existed and worked, but the **Clients** list only offered **Edit** and **Delete** per row. There was no link or button to open that client’s visits. Fixes applied:

1. **Clients list:** Added a **Besök** (Visits) action button (calendar icon) per row → navigates to `/resources/clients/:id/visits`.
2. **Client edit page:** Added a **Besök** button at the top of the form when editing a client → same destination.

## Route → navigation checklist

| Route                                          | How to reach it                                                 |
| ---------------------------------------------- | --------------------------------------------------------------- |
| `/`                                            | Landing; sign-in redirect                                       |
| `/sign-in`, `/sign-up`                         | Landing, nav when logged out                                    |
| `/schedules`                                   | **Nav:** Scheduling (header)                                    |
| `/schedules/:id`                               | From Schedules list                                             |
| `/schedules/:scheduleId/solutions/:solutionId` | From schedule detail                                            |
| `/compare`                                     | **Nav:** Jämför (header)                                        |
| `/resources`                                   | **Nav:** Resources (header)                                     |
| `/resources?resource=clients`                  | Resources → Clients tab (Organization overview)                 |
| `/resources/clients/create`                    | Clients list → "Add Client"                                     |
| `/resources/clients/:id/edit`                  | Clients list → Edit (pencil)                                    |
| **`/resources/clients/:clientId/visits`**      | **Clients list → Besök (calendar); Client edit → Besök**        |
| `/resources/visits/create`                     | From client visits list → "Nytt besök" (with clientId in query) |
| `/resources/visits/:id`                        | Scheduler (click visit); Client visits list (click row)         |
| `/resources/visits/:id/edit`                   | Visit detail page → Edit                                        |
| `/resources/employees/create`                  | Employees (Resources) → Create                                  |
| `/resources/employees/:id/edit`                | Employees list → row click / edit                               |
| `/resources/service-areas/create`              | Service areas list → Create                                     |
| `/resources/service-areas/:id/edit`            | Service areas list → row click                                  |
| `/account`, `/billing`, `/products`            | **Nav:** Account (header)                                       |
| `/user-profile/*`                              | Account / profile dropdown                                      |
| `/admin`                                       | **Nav:** Admin (header, super admin only)                       |
| `/benchmarks`                                  | Legacy redirect to Admin; no nav link (intentional)             |

## When adding a new page

1. **Add the route** in `App.tsx`.
2. **Add at least one navigation path:** link or button from a relevant list, tab, or header.
3. **Update this doc** with the new route and how to reach it.

---

_Last updated: 2026-03-08_
