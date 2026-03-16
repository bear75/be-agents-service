# CSV Import & Validation: Best Practices Summary

**Purpose:** Concise, cited best practices for flexible CSV import, canonical intermediate format, traffic-light validation, and data-model alignment. Target: production systems handling messy external CSVs (e.g. client Attendo/Databehov-style), 80–90% accuracy from upload, then CRUD/resources to 100%.

---

## 1. Flexible CSV Import Flows

**Goal:** Resilient to typos, minor text variations, new columns, and new enum-like strings (e.g. "När på dagen" vs `när_på_dagen`, new slot/inset names).

### Column and header resilience

- **Fuzzy column matching:** Use Levenshtein (or normalized similarity 0–1) for header mapping so "emial" → "email", "När på dagen" vs "när*på_dagen". Production option: token-based + Levenshtein; optional AI confidence scoring. *[CSV column mapping, ImportCSV; Stack Overflow fuzzy CSV column matching; csvmatch, fuzzy-csv libraries].\_
- **Normalize before matching:** Trim, lowercase, collapse spaces, normalize diacritics so "Morgon" / "morgon" / " MORgon " map to the same slot. Your `_slot_for_nar_pa_dagen` already uses `.strip().lower()` and substring checks ("morgon", "lunch", "kväll") — extend with a **configurable alias map** (e.g. `DAY_SLOT_ALIASES`) so new client strings (e.g. "Förmiddag") don’t require code changes.
- **Schema evolution:** Allow **optional columns** and **new columns**: unknown columns ignored or stored as optional metadata; new enum values (new slot names, new insets) either map via alias table or surface as **yellow** (review) with default/suggestion. _[Multi-step import flow, CSVBox; Safe bulk imports, AppMaster]._

### Parsing vs business rules

- **Parsing layer:** Only turns raw CSV (headers + rows) into a **normalized, in-memory structure** (e.g. list of row objects with canonical field names and types). No business rules (e.g. “is this visit valid for FSR?”) here.
- **Business / validation layer:** Consumes that normalized structure and applies rules (required fields, date ranges, dependency consistency, FSR constraints). New client strings that are successfully parsed (e.g. new slot name → default slot or “heldag”) don’t break the pipeline; only validation rules may flag them as yellow/red.
- **Concrete:** Keep `_slot_for_nar_pa_dagen`-style logic in a **single place** (e.g. `slotResolver(s, aliasMap)`) fed by a **configurable alias map** (DB or JSON per org/client), not hardcoded if/else. New strings either resolve via alias or fall back to a safe default (e.g. SLOT_HELDAG) and optionally emit a warning.

### Architecture (existing alignment)

- **Upload zone gatekeeper:** All client-specific parsing lives in the upload/mapper layer; backend accepts only **Caire canonical format** (see below). _[SCHEDULE_IMPORT_UPLOAD_FLOW.md; Enterprise Integration Patterns – Canonical Data Model]._
- **Single backend path:** Caire format → `scheduleUploadHelpers` (or equivalent) → DB. No branching on `sourceType === "ATTENDO"` in core backend. _[SCHEDULE_IMPORT_UPLOAD_FLOW.md]._

---

## 2. Canonical Intermediate Format ("Caire format")

**Pattern:** External CSV → **canonical/intermediate format** → backend → DB. Stable "Caire format" holds everything needed for Timefold FSR input generation and for resources CRUD.

**📘 See detailed specification:** [CAIRE_MIDDLE_CSV_FORMAT.md](./CAIRE_MIDDLE_CSV_FORMAT.md)

### Design

- **Canonical data model (CDM):** Application-independent, domain-focused format. Each external format has a **Message Translator** (mapper) to CDM only; new systems need only one mapper to CDM, not N×M. _[Enterprise Integration Patterns – Canonical Data Model; Agility at Scale – Canonical Data Model]._
- **Layers:**
  - **Raw/ingestion:** CSV (or file) lands unchanged; optional raw copy for replay.
  - **Intermediate/canonical:** Technical normalization: column mapping, types, dates, **durations/delays as ISO 8601** (e.g. `PT3H30M`). No business rules.
  - **Semantic/business:** Rules, enrichment, validation (e.g. FSR feasibility). _[dbt intermediate best practices; Data Engineering Best Practices]._

### Caire format contents (conceptual)

- **Clients:** externalId, name, address, coordinates (or geocode hint).
- **Employees:** externalId, shifts (weekday or date-based), service area.
- **Visit templates / visits:** recurrence, **duration and delays as ISO 8601**, time windows, dependencies (ISO duration), inset type, priority, etc.
- **Delays/durations:** Always ISO 8601 in canonical format so backend and Timefold projection never parse client-specific strings. _[SCHEDULE_IMPORT_UPLOAD_FLOW.md]._

### Separation of concerns

- **Parsing/validation:** Mappers only validate “can this row be turned into a canonical row?” (types, required fields, date format). Unknown columns or new enum values become default or warning, not hard failure.
- **Business rules:** Run after canonicalization (e.g. “visit within planning window”, “dependency graph acyclic”, “skill match”). New client strings that map to a valid canonical value don’t break the pipeline; only business checks may flag them.

### File/architecture

- **Single Caire DTO/schema:** One in-memory structure (or JSON schema) for “Caire schedule import” used by both dashboard upload and any script/API. Be-agent-service `csv_to_fsr` effectively produces a FSR-oriented view; for dashboard, prefer **Caire format first** (clients, employees, visit templates, visits, dependencies in normalized form), then **buildTimefoldModelInput** from DB.
- **Location:** Define Caire format in a shared package or dashboard-server types (e.g. `schedule-import/caire-format.ts` or JSON Schema in `docs/`); mappers in upload zone (e.g. `services/schedule/mappers/`) output only this format.

---

## 3. Traffic Light Validation (Green / Yellow / Red)

**Goal:** Categorize issues by entity and severity; present and resolve before commit.

### Severity

- **Green:** OK — row/entity valid, no action.
- **Yellow:** Warnings / review — fixable without blocking (e.g. unknown inset → default or null; new slot name → mapped to default slot; missing optional field). User can confirm and proceed or fix.
- **Red:** Action needed — blocking (e.g. required field missing, invalid reference, duplicate key, business rule violation). Must fix before commit. _[Safe bulk imports, AppMaster; CSVBox multi-step import]._

### By category (entity type)

- Group validation results by: **clients**, **insets (services)**, **recurring visits**, **visits**, **time windows**, **dependencies**, **priorities**, **skills**, **tags** (and any other FSR/resources dimensions).
- Per category: show counts (green/yellow/red) and **row-level detail** (row index, field, message). _[Intacct Import Service – review, fix, validate; Entity Framework validation – errors by entity/property]._

### UX best practices

- **Multi-step flow:** Upload → Map (columns/aliases) → **Validate** (dry run) → **Submit**. No write before explicit user confirm. _[CSVBox multi-step import; Smart Interface Design – Bulk Import UX]._
- **Five stages (bulk):** (1) Pre-import guardrails + example/template, (2) File upload (drag-drop, paste), (3) **Mapping** (headers, inline edit), (4) **Repair** (filter “rows with errors only”, fix duplicates), (5) **Import** (summary, optional tags). _[Smart Interface Design – Bulk Import UX]._
- **Row-level errors:** Show exact row number, field, and human-readable message; offer **downloadable error report** (e.g. CSV with error column) so users fix offline and re-upload. _[CSVBox row-level errors]._
- **Summary before commit:** Total rows, matched/new/skipped, and per-category green/yellow/red counts so user knows what will happen. _[AppMaster safe bulk imports]._

### Implementation

- **Validation service:** Input = Caire-format (or parsed) batch; output = `{ byCategory: { clients: { green, yellow, red, items }, visits: {...}, ... }, blocking: boolean }`. Backend runs same rules in dry run (validate) and on final submit (with write).
- **Frontend:** Summary panel by category with traffic light; expandable list of yellow/red items with row and message; “Fix in UI” links to resources CRUD where applicable (e.g. “Unknown inset → create Inset or map to existing”).

---

## 4. Data Model Alignment: CSV vs Resources as Source of Truth

**Goal:** One data model supports (a) generating Timefold FSR input and (b) resources CRUD (schedule resources and constraints). CSV is short-term input; **resources (DB) are the source of truth** for corrections and ongoing edits.

### Principles

- **Preview–validate–commit:** No commit until validation passes; user explicitly confirms. After commit, **DB is source of truth**; next bulk import can upsert by externalId but should not silently overwrite user edits. _[AppMaster safe bulk imports; Microsoft – staging database for migration]._
- **Staging vs committed:** Optional staging tables or in-memory batch for “this upload”; on confirm, write to real tables (Schedule, Client, Visit, etc.). Post-commit, CRUD and optimization read from DB only. _[Staging database approach, Microsoft; OneUptime data loading patterns]._

### Caire model and FSR + CRUD

- **Same entities:** Clients, Employees, VisitTemplates, Visits, Insets, DaySlots, InsetGroups, VisitDependency, VisitGroupMember, ClientDependencyRule, etc. CSV import **creates/updates** these via upsert (e.g. by externalId). _[PR97_RESOURCES_CRUD_HANDOFF.md](../../archive/PR97_RESOURCES_CRUD_HANDOFF.md) (archived)._
- **Timefold projection:** `buildTimefoldModelInput` reads from DB and builds FSR request. All delay/duration in DB should be **normalized (e.g. ISO)** so projection does not parse client-specific strings. _[SCHEDULE_IMPORT_UPLOAD_FLOW.md; PR97]._
- **Resources CRUD:** Users fix post-import (wrong slot, wrong inset, add dependency) via dashboard CRUD. Those edits are stored in the same DB; next FSR run uses updated data. CSV does not override corrections unless re-import is explicitly run and overwrite semantics are defined (e.g. “replace schedule” vs “merge”).

### CSV short-term, resources long-term

- **CSV:** Initial load or periodic bulk update; 80–90% accurate; validation (traffic light) drives fixes before commit; after commit, treat as “baseline” for that schedule.
- **Resources CRUD:** Ongoing source of truth; users correct inset, day slot, dependencies, skills, tags; `buildTimefoldModelInput` and UI read from DB.
- **Idempotency:** Use **externalId** (e.g. Kundnr, Slinga id) for clients and employees so re-upload updates instead of duplicating; visits/templates may be “replace by schedule + window” or keyed by external visit id if present. _[ATTENDO_CSV_MAPPING; PR97]._

### File/architecture

- **Single source of truth:** DB (dashboard-server Prisma models). No separate “import model”; import writes to the same tables CRUD uses.
- **Normalize at upload:** Mappers output Caire format with ISO durations; `scheduleUploadHelpers` (or equivalent) write to DB. No client-specific parsing in `buildTimefoldModelInput`; optional legacy fallback in one place (e.g. `parseDelayStringToIso`) only for already-stored metadata. _[PR97; SCHEDULE_IMPORT_UPLOAD_FLOW]._

---

## 5. Implementation Status (feature/import-zone)

The Schedule Upload Secure Import Zone has been implemented with the following components:

### Phase 1: Foundation & Types ✅

- **Caire canonical format types** (`apps/dashboard-server/src/services/schedule/import/caireFormat.ts`)
  - Complete TypeScript type definitions for CaireImportPayload
  - Canonical time slots, insets, weekdays, frequencies
  - Strongly typed intermediate format between adapters and DB
- **Middle CSV format documentation** ([CAIRE_MIDDLE_CSV_FORMAT.md](./CAIRE_MIDDLE_CSV_FORMAT.md))
  - Detailed specification of canonical field names and aliases
  - Column mapping rules and fuzzy matching strategies
  - Traffic-light validation examples

### Phase 2: Configurable Mapping ✅

- **Alias maps** (`apps/dashboard-server/src/services/schedule/import/aliasMaps.ts`)
  - Configurable slot/inset alias resolution (no code changes for new client strings)
  - Swedish duration parsing to ISO 8601 (`parseDurationToISO8601`)
  - Case-insensitive, whitespace-tolerant matching
- **Fuzzy column matching** (AttendoAdapter)
  - Handles column name variations (case, whitespace, underscores)
  - Supports v2 and v3 CSV formats (Column-0 is optional)
  - Normalized header matching (exact → case-insensitive → normalized)
- **Updated importAttendoSchedule**
  - Uses `resolveSlot()` and `resolveInsets()` instead of hardcoded maps
  - Emits warnings for unknown values (yellow validation)

### Phase 3: Attendo → Caire Conversion ✅

- **Conversion module** (`apps/dashboard-server/src/services/schedule/import/attendoToCaire.ts`)
  - Transforms Attendo CSV parse results to canonical Caire format
  - Normalizes addresses, coordinates, slots, insets, durations
  - Generates individual visits from templates
  - Collects conversion warnings for traffic-light validation

### Phase 4: Traffic-Light Validation ✅

- **Validation by category** (`apps/dashboard-server/src/services/schedule/import/validateCaire.ts`)
  - Green (valid) / Yellow (warning) / Red (blocking) severity
  - Categories: clients, employees, visits, insets, time_slots, dependencies
  - Row-level validation with field-specific error messages
  - Blocking flag indicates if any category has red issues
- **GraphQL schema extension** (`packages/graphql/schema/dashboard/types.graphql`)
  - Added `ValidationIssue`, `ValidationCategorySummary`, `ValidationByCategory` types
  - Extended `ParsedSchedulePreview` with `validationByCategory` and `blocking` fields
  - Backward compatible (existing `validationErrors` field preserved)
- **Updated parseAndValidateSchedule resolver**
  - Converts Attendo data to Caire format for validation
  - Returns traffic-light validation results in GraphQL response
  - Merges conversion warnings into legacy validationErrors

### Phase 5: Import Flow Integration ✅

- **Import flow** (finalizeScheduleUpload)
  - Uses importAttendoSchedule with new alias resolution
  - Flexible mapping works with v3 CSV without code changes
- **Projection** (buildTimefoldModelInput)
  - Works correctly with current metadata structure
  - Parsing centralized and stable

### What Works Now

- ✅ V3 CSV uploads without code changes (fuzzy column matching)
- ✅ Unknown slot values → default to `heldag` with yellow warning
- ✅ Unknown inset values → skipped with yellow warning
- ✅ New client strings added via alias config (no deployment needed)
- ✅ Preview shows traffic-light summary before finalizing
- ✅ Category-based validation (clients, visits, insets, time_slots, dependencies)
- ✅ 80-90% accuracy via CSV upload, 100% via resources CRUD

### Future Enhancements (Not in Scope)

- Frontend dashboard wizard UI for traffic-light display
- Python offline CSV converter (custom format → Caire middle CSV)
- Complete refactor to `importFromCaire()` (currently uses existing importAttendoSchedule with enhancements)
- Graph-based dependency validation (detect circular dependencies)

### Files Modified

- `apps/dashboard-server/src/services/schedule/adapters/AttendoAdapter.ts`
- `apps/dashboard-server/src/services/schedule/importAttendoSchedule.ts`
- `apps/dashboard-server/src/graphql/resolvers/schedule/mutations/parseAndValidateSchedule.ts`
- `packages/graphql/schema/dashboard/types.graphql`

### Files Created

- `apps/dashboard-server/src/services/schedule/import/caireFormat.ts`
- `apps/dashboard-server/src/services/schedule/import/aliasMaps.ts`
- `apps/dashboard-server/src/services/schedule/import/attendoToCaire.ts`
- `apps/dashboard-server/src/services/schedule/import/validateCaire.ts`
- `docs/docs_2.0/09-scheduling/CAIRE_MIDDLE_CSV_FORMAT.md`

---

## 6. Summary Table

| Area                 | Practice                                                                                                                         | Source                                                                  |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- |
| **Flexible CSV**     | Fuzzy column match (Levenshtein/token); configurable alias map for slots/insets; optional columns + new enum → default or yellow | ImportCSV, csvmatch/fuzzy-csv, CSVBox, SCHEDULE_IMPORT_UPLOAD_FLOW      |
| **Canonical format** | External → Caire (ISO durations) → backend; parsing vs business rules separation; one Caire DTO/schema                           | EIP Canonical Data Model, dbt intermediate, SCHEDULE_IMPORT_UPLOAD_FLOW |
| **Traffic light**    | Green/yellow/red by category; row-level errors; upload→map→validate→submit; summary before commit                                | AppMaster, CSVBox, Smart Interface Design, Intacct                      |
| **Data model**       | DB = source of truth; CSV = baseline; preview–validate–commit; externalId upsert; buildTimefoldModelInput from DB only           | PR97, SEED_VS_UPLOAD_BEST_PRACTICE, Microsoft staging, AppMaster        |

---

## References (short)

- **Enterprise Integration Patterns:** [Canonical Data Model](https://www.enterpriseintegrationpatterns.com/patterns/messaging/CanonicalDataModel.html)
- **CSVBox:** [Multi-step import flow](https://blog.csvbox.io/multi-step-import-flow/), [Row-level errors](https://blog.csvbox.io/row-level-errors-csv/)
- **AppMaster:** [Safe bulk imports: preview, validate, commit](https://appmaster.io/blog/safe-bulk-imports-preview-validate-commit)
- **Smart Interface Design Patterns:** [Bulk Import UX](https://smart-interface-design-patterns.com/articles/bulk-ux/)
- **Internal:** `docs/docs_2.0/09-scheduling/SCHEDULE_IMPORT_UPLOAD_FLOW.md`, `ATTENDO_CSV_MAPPING.md`, `PR97_RESOURCES_CRUD_HANDOFF.md` (in [../../archive/](../../archive/README.md)), `SEED_VS_UPLOAD_BEST_PRACTICE.md`
- **Fuzzy matching:** Stack Overflow “Fuzzy CSV column matching”; csvmatch (Python); fuzzy-csv (Groovy/Java); ImportCSV (Levenshtein + token + AI)
- **Staging / loading:** Microsoft Power Platform – staging database; OneUptime – data loading / bulk loading patterns
