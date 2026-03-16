# Migration 20260308145520 – Legacy column data loss (post-hoc note)

## Risk identified (Codex P1)

Migration `20260308145520_add_priority_cascade` drops legacy columns **without** a preceding step that copies their data into the new normalized skill tables:

- **Client:** `allergies`, `languagePreference`, `languages` → intended to be represented via `ClientSkill` (and skill category)
- **Employee:** `certifications`, `languages` → intended to be represented via `EmployeeSkill` (and skill category)

Any deployment that had existing values in these columns **before** this migration was applied will have lost that data permanently.

## Why no code fix here

- The migration has already been applied (schema no longer contains these columns).
- Prisma rules: **do not edit applied migrations**.
- A new migration cannot “run before” an already-applied one; adding a migration that copies from these columns would run only on DBs that haven’t run `20260308145520` yet (e.g. fresh installs), and would fail on DBs where the columns are already dropped.

## For future migrations

When removing columns that hold user data:

1. Add a **separate migration** (earlier timestamp) that:
   - Copies data from the old columns into the new normalized tables (e.g. create/link `Skill` and `ClientSkill` / `EmployeeSkill`).
   - Uses conditional SQL (e.g. `information_schema`) so the copy is a no-op if the columns are already gone.
2. Then run the migration that drops the columns.

This avoids production data loss when the drop migration is applied.
