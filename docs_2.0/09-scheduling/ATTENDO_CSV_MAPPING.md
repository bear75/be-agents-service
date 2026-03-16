# Attendo CSV import: mapping and unknown values

**Context:** Seed is catalog-only; schedule data comes only from dashboard CSV upload (`finalizeScheduleUpload` → `importAttendoSchedule`). See [SEED_ATTENDO_AND_CSV_UPLOAD.md](./SEED_ATTENDO_AND_CSV_UPLOAD.md) for what the seed does and how upload integrates. Mapping logic lives in `services/schedule/importAttendoSchedule.ts`.

## Behaviour summary

| CSV field                    | Behaviour                                                                                                        | Duplicates?                                                                                                                                                                                        |
| ---------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Insatser**                 | Mapped to catalog inset by `INSET_NAME_MAP` in `importAttendoSchedule`. Unknown label → `insetId` null on visit. | No. Unknown insatser do not create new insets; visits are still created with `insetId: null`. To support new types: add inset in org catalog (e.g. seed-org-defaults) and extend `INSET_NAME_MAP`. |
| **När på dagen**             | Used for time windows (Morgon, Lunch, Kväll → fixed bounds; unknown → 07:00–22:00).                              | No new records; only affects visit time window.                                                                                                                                                    |
| **Skift**                    | Inferred from Slinga prefix (Dag/Kväll/Helg). Employees are **upserted** by normalized `externalId` (Slinga).    | No. Same Slinga → same employee. New Slinga value → new employee (one per unique Slinga).                                                                                                          |
| **Antal tim mellan besöken** | Parsed to `ClientDependencyRule` (e.g. "3,5 tim" → ISO duration).                                                | No. Before create, we check for existing rule with same `clientId` + `defaultMinDelay` and skip if found.                                                                                          |

## Upsert vs create

- **Clients:** Upsert by `externalId` (Kundnr). Exists → update address/coords; else create.
- **Employees:** Upsert by normalized `externalId` (Slinga). Exists → optional coords/serviceArea update; else create.
- **Schedule:** Always create new.
- **Visits / templates / groups / shifts:** Always create new under the new schedule.
- **ClientDependencyRules:** Create new rule per (client, delay); skip if same client + same delay already exists.

So: other **Insatser** or **När på dagen** do not create duplicates; they either map to existing catalog or result in null/default. **Skift** and **timmar mellan besöken** are handled by upsert or duplicate-check so you do not get duplicate employees or dependency rules.
