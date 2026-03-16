# VisitTemplate.preferredTimeSlot and DaySlot

**Purpose:** Clarify that `VisitTemplate.preferredTimeSlot` is **not** a foreign key to `DaySlot`; values should align with `DaySlot.name` for consistency.

---

## Current schema

- **VisitTemplate.preferredTimeSlot:** `String?` — free-text column, no FK.
- **DaySlot:** Table with `id`, `organizationId`, `name`, `displayName`, `startTime`, `endTime`, `sequence`, etc. Used by **Inset** (e.g. `defaultDaySlotId`) and by the **create-visit flow** for dropdown options.

## Intended usage

- **UI:** Load time-slot options from `daySlots(organizationId)`. Show `DaySlot.displayName` in the dropdown; store **`DaySlot.name`** in `VisitTemplate.preferredTimeSlot` (e.g. `morgon`, `formiddag`, `eftermiddag`, `kvall`, `lunch`, `middag`, `natt`, `custom`).
- **Consistency:** Using `DaySlot.name` keeps template values aligned with the org’s day-slot catalog. No FK is required for that; the string is a convention.
- **Optional:** preferredTimeSlot, preferredDays, and similar fields are optional on the form and in the API.

## If you want a formal link later

Adding `VisitTemplate.preferredDaySlotId` (FK to `DaySlot`) would allow referential integrity and a single source of truth. Today we keep the string column and align values with `DaySlot.name` so the UI and seeds stay consistent without a migration.
