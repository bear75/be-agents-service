# Source CSV Upload (C0-398) — Next Steps and E2E Alignment

**Epic:** [C0-398](https://caire.atlassian.net/browse/C0-398) — Source CSV Upload (single entry point for schedule and resource data)

---

## 1. Current Gap: Dashboard vs Scripts Flow

| Flow                    | Path                                                                                                                               | Output                    |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------- | ------------------------- |
| **Dashboard (current)** | CSV upload → `uploadScheduleForOrganization` → `importAttendoSchedule` → DB → `buildTimefoldModelInput(scheduleId)` → Timefold API | FSR request built from DB |
| **Scripts (Python)**    | Source CSV → `attendo_4mars_to_fsr.py` → FSR JSON (no DB)                                                                          | Direct FSR model input    |

**Problem:** The dashboard path (CSV → DB → input) does **not** produce the same FSR input as the scripts path (CSV → JSON). So:

- Recurrence expansion or time-window logic may differ between `importAttendoSchedule` (TS) and the Python script.
- Only **Attendo** CSV is supported in the dashboard today; **Nova** is not.
- No single “source CSV → one pipeline” story: we have two parallel pipelines (dashboard vs script).

**Goal (C0-398):** One entry point — **source CSV** (Nova or Attendo) → parse + expand in TypeScript → DB (Clients, VisitTemplates, Employees, Schedule, Visits, with stable `externalId`s) → `buildTimefoldModelInput(scheduleId)` produces FSR input **equivalent** to what the Python script would produce from the same CSV.

---

## 2. Jira Stories → Plan Tasks

| Jira       | Summary                                                                    | Plan / implementation                                                                                                                                                  |
| ---------- | -------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **C0-399** | Server: Source CSV parser with format auto-detection (Nova + Attendo)      | **Task 1** — `parseSourceCsv.ts` + `detectFormat()`, canonical `SourceVisitRow`, map Nova/Attendo rows                                                                 |
| **C0-400** | Server: Recurrence expansion engine (TypeScript port from Python)          | **Task 2** — `expandRecurrence.ts`: `parseRecurrence()`, `expandToDates()`, Swedish weekday parsing, pinning rules                                                     |
| **C0-401** | Server: GraphQL mutation `uploadSourceCsvForOrganization`                  | **Task 3** — Resolver: decode base64 → parse → expand → upsert Clients, VisitTemplates, Employees, Visits, Schedule in one transaction                                 |
| **C0-402** | GraphQL schema + operation file + codegen                                  | **Task 4** — `mutations.graphql` + operation file, then `yarn workspace @appcaire/graphql codegen`                                                                     |
| **C0-403** | Frontend: UploadSourceCsvModal with planning window picker                 | **Task 5** — Rewrite upload modal: file picker, format badge, schedule name, planning window (start + 2/4 weeks), preview, call new mutation                           |
| **C0-404** | Tests: parseSourceCsv + expandRecurrence unit tests                        | **Task 6** — Unit tests for parser (format detection, mapping) and expander (pattern parse, date expansion)                                                            |
| **C0-405** | Deprecate old expanded CSV upload + Timefold input JSON upload             | After C0-399–C0-404: deprecate `uploadScheduleForOrganization` CSV path and `createScheduleFromTimefoldJson` as primary entry; keep as fallback.                       |
| **C0-414** | E2E parity: Verify dashboard FSR output matches Python for same source CSV | Compare FSR dump from dashboard path vs Python script; fix projection/expansion until aligned (or document differences).                                               |
| **C0-415** | Fix current Attendo CSV upload E2E (new format not working)                | Investigate and fix existing path: `uploadScheduleForOrganization` → `importAttendoSchedule` → DB → `buildTimefoldModelInput` so current Attendo CSV works end-to-end. |

---

## 3. E2E Flow After C0-398

**Target E2E (single entry point):**

```
Source CSV (Nova or Attendo)
    → UploadSourceCsvModal → uploadSourceCsvForOrganization
    → parseSourceCsv() + expandRecurrence() → DB (Schedule, Visits, Clients, Employees, …)
    → buildTimefoldModelInput(scheduleId)  [same as today]
    → startOptimization / e2e-submit-to-timefold → Timefold API
```

**E2E script** ([`e2e-submit-to-timefold.ts`](../../../apps/dashboard-server/src/scripts/e2e-submit-to-timefold.ts)) already does:

1. Take latest schedule from DB.
2. Build FSR request: `buildTimefoldModelInput(scheduleId, ...)`.
3. Optionally dump JSON: `E2E_DUMP_JSON=out.json yarn e2e:timefold`.
4. Submit to Timefold and poll status.

So the **next steps** for E2E are:

1. **Implement C0-399–C0-404** so schedule creation comes from **source** CSV via `uploadSourceCsvForOrganization` (and optionally keep seed/Attendo for dev).
2. **Verify parity:** For the **same** source CSV file:
   - **Path A:** Dashboard upload → then `E2E_DUMP_JSON=dashboard_input.json yarn e2e:timefold` (no submit, or submit disabled) to dump the FSR request built from DB.
   - **Path B:** Python script produces `script_input.json`.
   - Compare visit counts, group counts, dependency counts, and (if possible) normalized visit IDs/time windows between `dashboard_input.json` and `script_input.json`.
3. **Fix projection/expansion** until Path A matches Path B (or document accepted differences).

---

## 4. Suggested Implementation Order

**Fix current flow first (unblock dashboard):** 0. **C0-415** — Fix current Attendo CSV upload E2E so existing upload path works with the new format (diagnose and fix `importAttendoSchedule` / projection).

**Then new pipeline:**

1. **C0-399** — Parser + format detection (enables testing with real files).
2. **C0-400** — Recurrence expander (port from Python; reuse or align with `importAttendoSchedule.expandRecurrence` logic).
3. **C0-402** — Schema + operation + codegen (so resolver and frontend can call the mutation).
4. **C0-401** — Resolver: wire parse + expand + DB upsert.
5. **C0-404** — Unit tests for parser and expander.
6. **C0-403** — Frontend modal.
7. **C0-414** — E2E parity: same CSV → dashboard dump vs Python dump → compare and fix.
8. **C0-405** — Deprecate old CSV/JSON upload as primary entry (keep as fallback).

---

## 5. References

- **Plan:** [.cursor/plans/source_csv_upload_bbc4bb76.plan.md](../../../.cursor/plans/source_csv_upload_bbc4bb76.plan.md)
- **E2E script:** [apps/dashboard-server/src/scripts/e2e-submit-to-timefold.ts](../../../apps/dashboard-server/src/scripts/e2e-submit-to-timefold.ts)
- **Scheduling E2E:** [SCHEDULING_E2E_FLOW.md](SCHEDULING_E2E_FLOW.md)
- **Current Attendo import:** `apps/dashboard-server/src/services/schedule/importAttendoSchedule.ts` (source CSV + expansion; Attendo-only)
- **Python reference:** `be-agent-service/recurring-visits/huddinge-package/.../attendo_4mars_to_fsr.py`

---

_Last updated: 2026-03-13_
