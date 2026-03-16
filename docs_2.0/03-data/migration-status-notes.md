# Dashboard-server migration status

## Prisma migrations: generated vs migrated

Prisma migrations under `apps/dashboard-server/migrations/` are **generated** when you run:

```bash
yarn workspace dashboard-server db:migrate --name <name>
# or: npx prisma migrate dev --name <name>
```

They are **migrated** (applied) when you run:

```bash
yarn workspace dashboard-server db:migrate:deploy
# or: npx prisma migrate deploy
```

- **Generated** = the migration file exists and was created from `schema.prisma`.
- **Migrated** = the migration has been executed against a specific database and recorded in `_prisma_migrations`.

Whether a migration is migrated depends on the target database and whether `db:migrate:deploy` (or equivalent) was run against it. Local/dev/staging/prod can each have different migration history.

### 20260126111153_add_operational_settings

- **Generated:** Yes (Prisma-style folder + `migration.sql`).
- **Migrated:** Depends on environment. If `db:migrate:deploy` was run for that DB, it is migrated there.

### 20260127063104_add_data_model_2_0_fields

- **Generated:** Yes (Prisma-style folder + `migration.sql`).
- **Migrated:** Test DB failures (“column `diagnoses` does not exist”, “column `status` does not exist”) indicate this migration has **not** been applied to the dashboard-server test database. Other environments may or may not have it applied.

To bring a DB up to date:

```bash
yarn workspace dashboard-server db:migrate:deploy
```

Then regenerate the Prisma client if needed:

```bash
yarn workspace dashboard-server db:generate
```

## Removed: fix_movable_visit_update_data_preservation.sql

A standalone SQL file `fix_movable_visit_update_data_preservation.sql` was previously present in `apps/dashboard-server/migrations/`. It has been removed because:

1. **Wrong layout:** Prisma migrations live in timestamped folders with a single `migration.sql` file (e.g. `20260126111153_name/migration.sql`). A lone `.sql` file in the migrations root is not part of Prisma’s migration flow.
2. **Wrong schema:** It targeted the table `movable_visits` (snake_case) and created `movable_visits_audit_log`. The dashboard-server uses **Prisma** and has no `movable_visits` in its schema; that table belongs to the appcaire/Drizzle schema.
3. **Origin:** It was a leftover from the appcaire repo (Drizzle-based). Running it against the beta-appcaire Prisma database would fail because `movable_visits` does not exist there.

Only Prisma-generated migrations under `YYYYMMDDHHMMSS_name/migration.sql` should remain in `apps/dashboard-server/migrations/`.
