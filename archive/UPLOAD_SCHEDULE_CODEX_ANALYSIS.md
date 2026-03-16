# Upload schedule (CSV import) – Codex review analysis

Analysis of the three P1 Codex findings for `uploadScheduleForOrganization`. **Do not merge to production** until these are either fixed or explicitly accepted as known limitations.

---

## 1. Create address records when importing new clients

**Location:** `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/uploadScheduleForOrganization.ts` (resolveClients, ~lines 106–119)

**Current behavior:** New clients are created with only `latitude`/`longitude` on `Client`. No `Address` rows are created and `primaryAddressId` is never set.

**Downstream impact:**

- `generateVisitsFromTemplates` sets `addressId` from `client.primaryAddressId ?? client.addresses[0]?.id` → **null** for these clients.
- Visits are created with `addressId: null`.
- `prepareScheduleData` → `toTimefoldVisit()` uses `visit.address?.latitude` / `visit.address?.longitude`. If `visit.address` is null (no Address), it returns **null** and the visit is dropped.
- Result: **zero visits** are sent to Timefold for a fresh org import → optimization fails with “Schedule has no visits to optimize”.

**Conclusion:** This is a real bug for “CSV-only” imports (new clients with no existing Address). Fix required for optimization to work after import.

**Fix options:**

- **A (recommended):** When creating a new client with valid lat/lon, also create an `Address` (e.g. `addressType: "home"`, placeholder `street`/`city`/`postalCode` like `"Imported"` / `"—"`), set coordinates, then set `Client.primaryAddressId` to that address.
- **B:** Change `toTimefoldVisit` (or visit loading) to fall back to `client.latitude`/`client.longitude` when `visit.address` is null. That avoids creating Address rows but couples the optimizer to Client’s denormalized coordinates and may diverge from other features that rely on Address.

**Schema note:** `Address` requires `street`, `city`, `postalCode` (all non-null). So any new row must supply placeholders if the CSV has no address text.

---

## 2. Normalize preferred day names to scheduler format

**Location:** `uploadScheduleForOrganization.ts` – `extractPreferredDay()` (lines 60–64) and the `preferredDays` passed into `createVisitTemplates` (from `row.recurring_external`).

**Current behavior:** `extractPreferredDay()` returns the raw token after “vecka”/“weekly” (e.g. Swedish `mån`, `tis`, `ons` or full names like `måndag`). These are stored on `VisitTemplate.preferredDays`.

**Downstream impact:**

- `generateVisitsFromTemplates` → `getDatesForTemplate()` compares `preferredDays` to `DAY_NAMES`: `["sunday","monday","tuesday","wednesday","thursday","friday","saturday"]` (English, lowercase).
- Match is: `preferredDays.some((d) => d.toLowerCase().trim() === dayName)`. So `"mån"` never equals `"monday"` → no dates match for weekly/bi-weekly/monthly templates that only have Swedish tokens.
- Result: **no visits generated** for those templates (e.g. “vecka, mån” → preferredDays `["mån"]` → zero dates).

**Conclusion:** Real bug when CSV uses Swedish or other non-English day names. Fix required for recurring templates to expand in non-English imports.

**Fix option:** Normalize the extracted token to English weekday (e.g. map `mån`/`måndag` → `monday`, `tis`/`tisdag` → `tuesday`, …, `sön`/`söndag` → `sunday`) before adding to `preferredDays`. Same mapping already exists in `buildTimefoldInputFromCsv.ts` as `WEEKDAY_MAP` (numeric); we need a small map to English day-name strings for `getDatesForTemplate`.

---

## 3. Preserve recurring/group IDs in template metadata

**Location:** `uploadScheduleForOrganization.ts` – `createVisitTemplates()` (lines 178–181). Template `metadata` is set only to `{ createdFromScheduleId: scheduleId }`.

**Current behavior:** Source rows have `recurringVisit_id` and `visitGroup_id` (NormRow from CSV). These are used only for grouping when building the template (group key = `row.recurringVisit_id || \`${client}_${startTime}\``). They are **not** written to `VisitTemplate.metadata`.

**Downstream impact:**

- `prepareScheduleData` builds Timefold `visitGroups` by reading `visit.visitTemplate?.metadata.recurringVisitId` and `metadata.visitGroupId`. Visits with the same (recurringVisitId | visitGroupId) and same week are grouped; groups with >1 visit become a single `visitGroup` (must be served together).
- Without these keys, every visit has empty group key → all go to `visitsWithoutGroup` → **no visit groups**.
- Double/paired visits (same recurring id or same Dubbelid) are then optimized as independent visits instead of “same vehicle, same time” → **optimization correctness** changes (e.g. paired care no longer enforced).

**Conclusion:** Correctness/UX bug for CSVs that use recurring or group ids. Fix required if we want grouping/paired visits from CSV import.

**Fix option:** When creating a template from a group, store in `metadata` the group’s `recurringVisitId` and `visitGroupId` (e.g. from the first row in the group: `row.recurringVisit_id`, `row.visitGroup_id`). Extend the grouped structure to carry these two fields, then set `metadata: { createdFromScheduleId, recurringVisitId?, visitGroupId? }` in `tx.visitTemplate.create`.

---

## Summary

| Issue                                    | Severity        | Effect if unfixed                                    | Fix complexity                              |
| ---------------------------------------- | --------------- | ---------------------------------------------------- | ------------------------------------------- |
| 1. No Address / primaryAddressId         | **Blocker**     | Optimization fails (0 visits) for fresh import       | Low (create Address + set primaryAddressId) |
| 2. Preferred days not normalized         | **Blocker**     | No visits for weekly/etc. when CSV uses Swedish days | Low (day-name map)                          |
| 3. recurringVisitId/visitGroupId missing | **Correctness** | Paired/recurring grouping lost in optimizer          | Low (pass through from group to metadata)   |

**Recommendation:** Address all three before merging the upload-schedule flow to production. No production merge of this feature until the analysis is accepted and fixes are implemented or explicitly deferred.
