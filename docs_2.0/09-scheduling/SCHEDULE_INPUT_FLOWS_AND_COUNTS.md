# Schedule input flows and where the schedule numbers come from

## Schedule ↔ Timefold input ↔ Solution (data model)

**Sanningen = det vi skickar till Timefold som input.** Den byggs deterministiskt från schemat i DB.

| Concept            | Meaning                                                                                                                             |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Schedule (DB)**  | Ett schema i databasen: besök, medarbetare, grupper, beroenden, insättningar. Källan till allt.                                     |
| **Timefold input** | JSON-payload som skickas till FSR-API. Byggs av `buildTimefoldModelInput(scheduleId)` från samma data som schemat.                  |
| **Solution**       | En optimeringskörning: en submission till Timefold, ett resultat (tilldelningar, score). Länkas till ett Schedule via `scheduleId`. |

**Deterministisk projektion:** För ett givet schema (samma besök, medarbetare, grupper, beroenden i DB) ger `buildTimefoldModelInput(scheduleId)` alltid samma input. Schemat “ändras” inte mellan olika skickanden – om inget har ändrats i DB är input identisk. Om man redigerar besök, importerar om eller ändrar medarbetare uppdateras schemat, och nästa build ger då en annan payload.

**Ett schema → många lösningar:** Ett och samma schema kan ha många Solutions (flera optimeringskörningar: olika parametrar, seeds, eller bara fler körningar). Det krävs **inte** flera scheman i DB för att ha flera lösningar. Modellen: `Schedule` 1 → N `Solution` (varje Solution = en körning, en Problem-snapshot, en Timefold-job).

- **Kod:** `buildTimefoldModelInput(scheduleId, jobName?, options?)` i `apps/dashboard-server/src/services/timefold/projection/buildTimefoldModelInput.ts`
- **Anrop:** Vid `startOptimization` (en körning), vid `finalizeScheduleUpload` (count-only efter import), och i script (dump-fsr, e2e-submit).

---

## Var kommer schemasiffrorna ifrån? (Where do the schedule numbers come from?)

**Schemasiffrorna** (Besök, Besöksgrupper, Beroenden) kommer från **samma räknelogik som indata till Timefold** – projektionen i `buildTimefoldModelInput`. Siffrorna måste vara identiska i dashboard och i input-payload (samma matematik).

| Källa                 | Används till                                                                                                                                                                                                                          | Visas i UI?                                            |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------ |
| **CSV**               | Import: CSV laddas upp → importeras till DB. Efter import körs projektion (count-only) så att antal sätts.                                                                                                                            | Nej – CSV används bara vid uppladdning.                |
| **Projektion**        | **Enda källan för antal.** `buildTimefoldModelInput` räknar besök, grupper och beroenden och sparar i `sourceMetadata.modelCounts`. `Schedule.visitsCount` och `inputSummary` (besöksgrupper, beroenden) använder dessa när de finns. | **Ja** – Mätvärdena = samma som i input till Timefold. |
| **Input** (Timefold)  | Samma projektion bygger JSON-payload. Antalen är identiska med det som visas i dashboard.                                                                                                                                             | – (samma siffror som Mätvärden)                        |
| **Output** (Timefold) | Lösningen från Timefold (tilldelade besök, rutter).                                                                                                                                                                                   | Nej – det är _lösningar_, inte indata-siffror.         |

**Kort svar:** Schemasiffrorna och input till Timefold byggs från **samma kod** (projektionen). Efter import körs projektionen i count-only-läge så att antalen finns direkt; vid optimering används samma antal i payload. Matematiken är alltid densamma.

---

Three pipelines can produce visit/group/dependency counts. The dashboard and the Timefold input payload now use **the same counts** from the projection (`buildTimefoldModelInput`).

## The three flows

| Flow                    | Description                                                                                                                                                                      | Typical counts (example)           |
| ----------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------- |
| **CSV → script → JSON** | Python (e.g. `csv_to_fsr.py`, `expand_recurring.py`) expands CSV to FSR JSON.                                                                                                    | 3844 visits, 152 groups, 2165 deps |
| **CSV → DB**            | Dashboard import (Attendo/Nova) writes to DB. `Schedule.inputSummary` shows **Indata (DB)**.                                                                                     | 3816 visits, 162 groups, 2005 deps |
| **DB → JSON**           | `buildTimefoldModelInput` loads DB and builds the optimization payload. Model counts are stored in `sourceMetadata.modelCounts` but are **not** shown in the schedule detail UI. | 4017 visits, 167 groups, 2005 deps |

## Why they differ

- **Visits**: DB has one row per visit. The **model** expands flexible (multi-day) visits into one Timefold visit per candidate day, so model visit count ≥ DB visit count. The **script** may use different date expansion or filtering.
- **Visit groups**: DB has one `VisitGroup` per distinct group. The **model** can create more groups when collapsing/splitting flexible groups. The **script** may count unique group keys differently.
- **Dependencies**: **Indata** and **Modell** use the same logic (explicit + same-day ordering with skip rules). The **script** may use different same-day or dependency rules, so its count (e.g. 2165) can differ from DB/Model (e.g. 2005).

## Dashboard (single set of metrics = same as input)

The schedule detail page shows **only** the schedule’s numbers (DB / `inputSummary`). There is no separate “Modell (vid optimering)” block. The same figures should be used for CSV, input, and output in production.

- **Source**: `Schedule.inputSummary` and `Schedule.visitsCount` — counts from the database (visits, visit groups, dependencies with projection-aligned logic).
- **Removed**: The “Modell (vid optimering)” block that showed `modelVisitsCount`, `modelVisitGroupsCount`, `modelDependenciesCount` from `sourceMetadata.modelCounts` has been removed so the UI has one set of metrics only.

## Facit (expected from CSV)

At Attendo import we store in `schedule.metadata.facit`:

- **expectedVisitCount** — sum of (visits per week per row) × period weeks; one formula from recurrence (daily=7, weekly=N days, biweekly=0.5, etc.).
- **expectedVisitGroupsCount** — number of unique (client, date, Dubbel) with ≥2 visits (same definition as created visit groups).
- **expectedSameDayOrderingCount** — sum over (client, date) of max(0, n−1) ordering edges (same-day only; no skip logic in facit).

These are **not** shown in the dashboard (to avoid confusion). They remain in the API and in `schedule.metadata.facit` for verification or scripts if needed.

## Aligning counts (CSV, input, output)

Dashboard and Timefold input now use the **same counts** (projection):

1. **Single source of truth**: The projection (`buildTimefoldModelInput`) is the only place that defines how visits, visit groups, and dependencies are counted. It persists `modelCounts` to `schedule.sourceMetadata`. `Schedule.visitsCount` and `inputSummary` read from `modelCounts` when present.
2. **After import**: `finalizeScheduleUpload` runs the projection with `countOnly: true` so `modelCounts` (and thus dashboard numbers) are set right after upload.
3. **Script pipeline** (e.g. `csv_to_fsr.py`): If you need script output to match dashboard/input, mirror the same counting logic (visit expansion, group uniqueness, dependency rules) as in `buildTimefoldModelInput`.
