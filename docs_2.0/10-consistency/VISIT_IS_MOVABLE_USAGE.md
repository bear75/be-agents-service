# Visit: movable, pinned, mandatory, priority (FSR and app)

**Purpose:** Align FSR (Timefold) semantics with our DB and UI so backend and frontend are accurate.

---

## 1. FSR semantics (Timefold Field Service Routing)

In FSR there are **no** separate “movable” or “mandatory” fields on the Visit. Behaviour is determined by **time windows**, **pinning**, and **priority**.

### Movable

- **In FSR:** “Movable” = the solver can choose **when** (and on which day) to place the visit. This is expressed **only by time windows**:
  - **Multi-day visit time windows:** one `timeWindow` with `minStartTime`–`maxEndTime` spanning multiple days, or multiple `timeWindows` (e.g. one per eligible day). The solver places the visit within those windows.
- FSR has **no** `isMovable` or `movable` field. Movable is purely “this visit has (multi-)day flexibility in its time windows”.

### Pinned

- **In FSR:** `pinningRequested: true` means the visit **must keep its current assignment** (vehicle and time). The solver does not move or reassign it. Used for real-time planning and fine-tune.

### Mandatory

- **In FSR:** There is **no** “mandatory” or “optional” field on the Visit. Whether a visit is treated as mandatory is **derived** from the **planning window** and the visit’s **time window**:
  - **Mandatory (in this run):** visit’s time window lies entirely within the planning window → solver should try to assign it; “Require scheduling mandatory visits” penalizes unassigned such visits.
  - **Optional:** visit’s time window extends beyond the planning window → can be left for a later run.
- So nothing is sent to FSR for “mandatory”; it’s implicit from `timeWindows` + `planningWindow`.

### Priority

- **In FSR:** Visit has a **`priority`** field (e.g. string `"1"`–`"10"`). Used for tie-breaking and soft constraints (e.g. assign higher-priority visits first). Convention: **1 = highest**, **10 = lowest**.

---

## 2. Our backend (accurate)

| Concept       | FSR API                          | Our mapping                                                                                                                                                                                                                        | Verdict |
| ------------- | -------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------- |
| **Movable**   | No field; multi-day time windows | We send one `timeWindows: [{ minStartTime, maxEndTime }]` from `allowedTimeWindowStart` / `allowedTimeWindowEnd`. When that range spans multiple calendar days, the visit is movable in FSR terms. We do **not** send `isMovable`. | Correct |
| **Pinned**    | `pinningRequested`               | `pinningRequested: visit.isPinned` (DB). Fine-tune: from assignment + `unpinnedVisitIds`.                                                                                                                                          | Correct |
| **Mandatory** | No field; derived from windows   | We do **not** send any mandatory field. FSR derives it from time window vs planning window. Our DB `isMandatory` is for **UI/business** only (e.g. “Kritisk insats”).                                                              | Correct |
| **Priority**  | `priority` (string)              | `priority: (visit.priority ?? 6).toString()`. Visit schema default is 6.                                                                                                                                                           | Correct |

So: **movable** in FSR = multi-day time windows (we express it correctly by sending that window). **Pinned** = `isPinned` → `pinningRequested`. **Mandatory** = not sent; FSR infers from windows. **Priority** = sent as string.

---

## 3. Our DB and UI

### DB

- **Visit.isMovable:** **Deprecated, optional (nullable).** Only **old CSV upload** uses it (bridge daily-schedule schema, `parseScheduleCsv`). FSR and UI derive “movable” from time window (multi-day). New visits get `null` unless CSV or client sends it. **Not sent to FSR.**
- **Visit.isPinned:** Drives `pinningRequested` in FSR. Correct.
- **Visit.isMandatory:** UI and business only (e.g. critical intervention). Not sent to FSR.
- **Visit.priority:** Default **6** in schema. Sent to FSR as string.

### UI (scheduler)

- **Movable styling:** **Derived from time window.** In `visitMapper.ts`, `deriveMovableFromTimeWindow(gql)` returns true when `allowedTimeWindowStart` and `allowedTimeWindowEnd` are on different calendar days. So UI “movable” = “solver can choose day” = multi-day time windows (FSR-aligned). DB `isMovable` is not used for scheduler styling.
- **Pinned:** We have `pinningRequested` and pinning UI; correct.
- **Mandatory / priority:** Shown in UI from DB; not sent to FSR (mandatory) or sent as priority (priority). Correct.

### Visit list and recurrence

- **Visit category (Kategori) column was removed.** Recurrence is shown only as **Återkommande** = `visit.template?.frequency` (daily, weekly, bi_weekly, monthly). We do not show `visitCategory` (daily | recurring) on the list; all visits are recurring with a frequency from the template.

### VisitCategory (DB) – deprecated

- **Visit.visitCategory** (daily | recurring) is **deprecated** in favor of **Visit.template.frequency** (daily | weekly | bi_weekly | monthly | custom). Recurrence is defined by the template; the DB column is kept only for backward compatibility until removal.
- **Backend:** On create/update, `visitCategory` is **derived from the template** when `visitTemplateId` is set (`frequencyToVisitCategory(template.frequency)`). If no template, default is `daily`. CreateVisitInput.visitCategory is optional and deprecated.
- **Frontend:** Mappers and UI use `template?.frequency` for mandatory/optional styling and labels; `visitCategory` is only a fallback when template is missing. Visit form no longer has a Kategori field; new visits get recurrence from their template (or default daily).
- **Removal path:** Once all visits have a template or we backfill from template, the column can be made nullable and then dropped.

---

## 4. Short glossary

| Term          | FSR meaning                                                                         | Our backend / UI                                                                                                                                                            |
| ------------- | ----------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Movable**   | Multi-day visit time windows; solver picks day/time within them.                    | Expressed by sending a time window that can span multiple days. DB `isMovable` is **deprecated** (optional, CSV upload only). UI **derives** movable from time window span. |
| **Pinned**    | Visit must keep current assignment.                                                 | `pinningRequested: Visit.isPinned`.                                                                                                                                         |
| **Mandatory** | Visit should be assigned in this run (derived from time window vs planning window). | Not sent. DB `isMandatory` = UI/business only.                                                                                                                              |
| **Priority**  | Importance for tie-breaking / soft constraints (1 = highest).                       | `priority: Visit.priority` as string.                                                                                                                                       |

---

## 5. References

- Timefold FSR: [Real-time planning – pinning visits](https://docs.timefold.ai/field-service-routing/latest/real-time-planning/real-time-planning-pinning-visits)
- Timefold FSR: [Priority visits and optional visits](https://docs.timefold.ai/field-service-routing/latest/visit-service-constraints/priority-visits-and-optional-visits)
- Our projection: `apps/dashboard-server/src/services/timefold/projection/classifyVisitWindow.ts` (movableAcrossDays = spansMultipleDays from time window)
