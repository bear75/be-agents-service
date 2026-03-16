# Schedule Import / Upload Flow — Current vs Target

**Purpose:** Describe how CSV import and upload work today (Nova, Attendo, Carefox) and the target architecture: **upload zone gatekeeper** (client-specific parsers) → **Caire canonical format** → backend. Client names and format-specific parsing must not live in core backend; we will have hundreds of clients and CSV formats change.

---

## 1. Current Flow (As-Is)

### Entry points

| Entry point                       | Use case                                                  | Format detection                                     |
| --------------------------------- | --------------------------------------------------------- | ---------------------------------------------------- |
| **uploadScheduleForOrganization** | Single-step upload (CSV → schedule in one mutation)       | `isAttendoFormat(csvString)` then else expanded      |
| **finalizeScheduleUpload**        | Step 2 of wizard: re-parse CSV + config → create schedule | `scheduleAdapterFactory.detect(csvString)` → adapter |
| **parseAndValidateSchedule**      | Step 1 of wizard: preview/validate only                   | Same factory                                         |

### Format detection and routing

- **uploadScheduleForOrganization**
  - If CSV has "Återkommande" (Attendo-style) → `importAttendoSchedule(...)` (raw CSV → DB in one shot).
  - Else → `parseExpandedCsv(csvBuffer)` (Nova expanded format) → `scheduleUploadHelpers` (upsertClients, upsertEmployees, createScheduleEmployeesAndShifts, upsertVisitGroups, upsertVisitTemplatesAndVisits) → DB.

- **finalizeScheduleUpload**
  - Uses **scheduleAdapterFactory** with registered adapters (in detection order):
    1. **AttendoAdapter** — detects by "Återkommande"; `parse()` returns `sourceType: "ATTENDO"`, summary, validationErrors, rawData.
    2. **CarefoxAdapter** — stub (not supported).
    3. **NovaExpandedAdapter** — detects by "recurringVisit_id"; `parse()` returns `sourceType: "NOVA_EXPANDED"`, summary, etc.
  - If `parsedPreview.sourceType === "ATTENDO"` → calls **importAttendoSchedule** (same as above).
  - Else (Nova) → **parseExpandedCsv** → same helpers → DB.

So today there are **two pipelines**:

1. **Nova / “expanded” path**
   - CSV is already in an expanded, Caire-like shape (each row = concrete visit, columns like `recurringVisit_id`, `visitGroup_id`, etc.).
   - **parseExpandedCsv** (in `services/schedule/csv.ts`) parses it into `ParsedExpandedCsv` (clients, employees, visitTemplates with visits, dateRange).
   - **scheduleUploadHelpers** turn that into DB entities.
   - No client name in the parser; the format is “expanded recurring-visits CSV”.

2. **Attendo path**
   - CSV is client-specific (DATABEHOV-style: columns like Återkommande, När på dagen, Antal tim mellan besöken, etc.).
   - **AttendoAdapter** only does detect + parse (preview/summary); it does **not** convert to a canonical format.
   - **importAttendoSchedule** does the full job: parse raw CSV, map columns, expand recurrence, write Clients, VisitTemplates, Visits, Schedule, etc.
   - Delay strings (e.g. `"3,5 timmar"`) are parsed by a shared util and stored in visit/template metadata; **buildTimefoldModelInput** also reads that metadata and may parse the same delay strings again when building the Timefold request.

### Where “client” names appear today

- **Adapters:** `AttendoAdapter`, `CarefoxAdapter`, `NovaExpandedAdapter` — and `ScheduleSourceType`: `"ATTENDO" | "NOVA_EXPANDED" | "CAREFOX"`.
- **Services:** `importAttendoSchedule.ts` (Attendo-specific column mapping and flow).
- **Utils:** Previously `attendoDelay.ts` (delay string → ISO); name referred to a client.
- **Seed:** `seed-attendo.ts` (dev/seed only).
- **Timefold projection:** `buildTimefoldModelInput` reads visit/template metadata (including delay strings that may be in Swedish form); it uses a delay-parsing util so it can handle legacy or non-normalized data.

### Parsing summary

| Format                        | Detection                   | Parser / importer                                                  | Output into DB                                                               |
| ----------------------------- | --------------------------- | ------------------------------------------------------------------ | ---------------------------------------------------------------------------- |
| **Nova expanded**             | `recurringVisit_id`         | `parseExpandedCsv`                                                 | scheduleUploadHelpers → Schedule, Clients, Employees, VisitTemplates, Visits |
| **Attendo (DATABEHOV-style)** | `Återkommande`              | AttendoAdapter (preview) + **importAttendoSchedule** (full import) | Same entities; delay/duration in metadata                                    |
| **Carefox**                   | `carefox_client_id` / `cf_` | CarefoxAdapter (stub)                                              | Not supported                                                                |

---

## 2. Target Architecture: Upload Gatekeeper → Caire Format → Backend

**Principle:** Client names and client-specific CSV parsing must **not** live in the core backend. CSV formats change and we will have hundreds of clients. All parsing of external CSVs must happen in an **upload zone gatekeeper** that converts **external format → Caire canonical format**. The backend then only accepts **Caire format** and writes to the DB.

### Caire canonical format (conceptual)

- **Clients:** externalId, name, address, coordinates (or geocode hint).
- **Employees:** externalId, shifts (weekday or date-based), service area.
- **Visit templates / visits:** recurrence, duration (e.g. **ISO 8601**), time windows, dependencies (e.g. **ISO duration** between visits), inset type, priority, etc.
- **Delays and durations:** Always **ISO 8601** (e.g. `PT3H30M`) in the canonical format so the backend and Timefold projection never need to parse client-specific strings.

### Upload zone (gatekeeper)

- **Single entry:** Uploaded file (CSV or future formats).
- **Format detection:** By structure/columns, not by client name (e.g. “has column Återkommande” → use Databehov-style mapper; “has recurringVisit_id” → use expanded mapper).
- **Per-format mappers:** Each mapper knows how to go from **one external format** → **Caire canonical format**.
  - Example: “Databehov-style CSV” mapper (columns like Återkommande, När på dagen, Antal tim mellan besöken) → Caire (clients, employees, visits with ISO durations).
  - Delay strings like `"3,5 timmar"` are converted to ISO **in the mapper** and only ISO is passed on.
- **No client names in backend:** The backend only sees “Caire format” (e.g. normalized delay = ISO). Adapter/mapper names can be format-based (e.g. DatabehovCsvMapper) rather than client-based (Attendo).

### Backend (after the gate)

- **Single importer:** Accepts only **Caire canonical format** (e.g. in-memory DTO or a single “Caire CSV” schema).
  - Today’s `scheduleUploadHelpers` (upsertClients, upsertEmployees, upsertVisitGroups, upsertVisitTemplatesAndVisits, etc.) are the right shape: they consume already-normalized structures.
- **Timefold projection:** **buildTimefoldModelInput** reads from DB. If all upload paths write **normalized** data (e.g. delay/duration as ISO in metadata), the projection does not need to parse any client-specific strings; it can use generic ISO helpers only.
- **Shared utils:** Format-agnostic only (e.g. “parse Swedish-style delay string to ISO” for legacy or for use inside the upload zone). No “Attendo” or other client names in backend utils.

### Concretely

1. **Rename / relocate** so **no client name** appears in core backend:
   - Delay parsing: e.g. `parseDelayStringToIso` in `utils/delayStringToIso.ts` (format: “Swedish-style delay, e.g. 3,5 timmar” → ISO). Used by upload mappers and, if needed, by projection for **legacy** metadata.
2. **Upload zone:** Move (or duplicate) client-specific parsing into an explicit “upload” or “mappers” layer that **outputs Caire format only**. Over time, AttendoAdapter + importAttendoSchedule become “Databehov-style CSV” detection + mapper that outputs the same Caire DTO the expanded path uses.
3. **Single backend path:** One code path: **Caire format** → scheduleUploadHelpers (or equivalent) → DB. No branching on `sourceType === "ATTENDO"` in the backend; format-specific branching stays in the gatekeeper.
4. **Normalize at upload:** All mappers write delay/duration as ISO (e.g. in visit/template metadata). Then **buildTimefoldModelInput** only needs `durationToMinutesSafe(isoString)` and no client-specific parsing.

---

## 3. Current File Roles (Quick Reference)

| File / layer                        | Role                                                                                                                                                                                                 |
| ----------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **uploadScheduleForOrganization**   | Mutation: if Attendo-style CSV → importAttendoSchedule; else parseExpandedCsv → helpers.                                                                                                             |
| **finalizeScheduleUpload**          | Mutation: adapter.detect/parse; if ATTENDO → importAttendoSchedule; else parseExpandedCsv → helpers.                                                                                                 |
| **parseAndValidateSchedule**        | Mutation: adapter.detect/parse; returns preview + sourceType (no DB write).                                                                                                                          |
| **scheduleAdapterFactory**          | Registers AttendoAdapter, CarefoxAdapter, NovaExpandedAdapter; `detect(csvString)` returns first matching adapter.                                                                                   |
| **AttendoAdapter**                  | detect (Återkommande), parse (preview/summary), validate; returns sourceType `"ATTENDO"`.                                                                                                            |
| **NovaExpandedAdapter**             | detect (recurringVisit_id), parse (preview); returns sourceType `"NOVA_EXPANDED"`.                                                                                                                   |
| **importAttendoSchedule**           | Full import: raw Attendo-style CSV → DB (clients, employees, visits, templates, schedule).                                                                                                           |
| **parseExpandedCsv**                | Parses Nova expanded CSV → ParsedExpandedCsv (Caire-like).                                                                                                                                           |
| **scheduleUploadHelpers**           | upsertClients, upsertEmployees, createScheduleEmployeesAndShifts, upsertVisitGroups, upsertVisitTemplatesAndVisits.                                                                                  |
| **buildTimefoldModelInput**         | Reads schedule from DB, builds Timefold FSR request; reads delay/duration from visit/template metadata (may still see legacy Swedish-style strings → uses delay parsing for backward compatibility). |
| **utils/delayStringToIso** (target) | Parse “Swedish-style” delay (e.g. 3,5 timmar, 18h) → ISO 8601. Used by upload mappers and, if needed, projection for legacy metadata. No client name.                                                |

---

## 4. Next Steps (Product / Tech)

- **Done (this change):** Remove client name from backend delay util: rename to format-based `parseDelayStringToIso` / `delayStringToIso.ts`; projection and upload/seed call that instead of an “Attendo”-named util.
- **Later:** Define a single **Caire canonical** DTO (or CSV schema) and make all upload paths produce it; move Attendo-style parsing into a “Databehov” (or format-based) mapper in the upload zone; have backend accept only Caire format.
- **Later:** Ensure all mappers write ISO durations in metadata so **buildTimefoldModelInput** does not need to parse client-specific delay strings.
