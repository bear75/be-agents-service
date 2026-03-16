# Handbook DB – fix migration issue after restore

**Context:** The dump `handbook_db_2026-02-12T10-31-39.sql` is already on the EC2 server. After restoring it into the handbook DB, the app expects a **single** migration (`20260206180000_init`) but the dump contains the **old** migration history (13 rows). That causes a migration diff and can prevent the handbook-server from starting.

**Fix:** Run the following SQL against the handbook DB **after** restoring the dump. It replaces the migration table with one row so the app and DB agree.

---

## SQL to run (fix migration diff)

Use your usual way to run SQL against the handbook DB (e.g. `psql "$DATABASE_URL"` or your app’s DB URL). Paste into a file and run `psql "$DB_URL" -f that_file.sql`, or run inline.

```sql
TRUNCATE _prisma_migrations;

INSERT INTO _prisma_migrations (
  id,
  checksum,
  finished_at,
  migration_name,
  logs,
  rolled_back_at,
  started_at,
  applied_steps_count
) VALUES (
  '2a08355f-c9f6-47c7-989b-976c29ca24a1',
  'b90d020b96d349fb344b3a1f1124f8fac56ef9f541279f96e8ec1f3729bead56',
  now(),
  '20260206180000_init',
  NULL,
  NULL,
  now(),
  1
);
```

Then restart the handbook-server container so it runs `prisma migrate deploy` (it will see no pending migrations and start).

---

## Verify

- `SELECT migration_name FROM _prisma_migrations;` → one row: `20260206180000_init`
- After restart: https://handbook-api.caire.se/health returns 200
