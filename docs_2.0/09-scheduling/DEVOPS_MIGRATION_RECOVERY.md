# DevOps: Fix migration failure (P3018 / P3009)

When `prisma migrate deploy` fails with **P3018** ("relation X already exists") or **P3009** ("failed migrations in the target database"), use the steps below. No code changes—only these commands. The same fix applies to **any** migration that fails with "already exists": run `resolve --applied <migration_name>` for that migration, then `migrate deploy` again.

---

## Fix (copy-paste)

Run from repo root. Use the **correct `DATABASE_URL`** for the environment (pilot or stage).

**Pilot** (uses `.env.pilot`):

```bash
cd apps/dashboard-server
dotenvx run -f .env.pilot -- npx prisma migrate resolve --applied 20260308145520_add_priority_cascade
dotenvx run -f .env.pilot -- npx prisma migrate deploy
```

**Stage** (set `DATABASE_URL` to stage RDS first, e.g. `export` or `.env.stage`):

```bash
cd apps/dashboard-server
npx prisma migrate resolve --applied 20260308145520_add_priority_cascade
npx prisma migrate deploy
```

**Prod** (same idea—when deploy fails with P3018, run with **prod** `DATABASE_URL`):

```bash
cd apps/dashboard-server
# Set DATABASE_URL to prod RDS (e.g. export or .env.prod)
npx prisma migrate resolve --applied 20260308145520_add_priority_cascade
npx prisma migrate deploy
```

Then run your normal deploy again; entrypoint will run `migrate deploy` and see no pending migrations.

**När ska prod fixas?** Antingen när prod-deploy redan har kraschat med P3018 (då kör ni resolve + deploy mot prod-DB), eller proaktivt före första prod-deploy efter denna migration om ni har tillgång till prod-DB.

**Stage – if a _different_ migration fails next (e.g. "Skill_organizationId_name_key already exists"):**  
Same pattern. Use the **exact migration name** from the error. Example for the Skill unique constraint:

```bash
npx prisma migrate resolve --applied 20260308220000_restore_skill_organization_name_unique
npx prisma migrate deploy
```

If deploy still fails again on another migration, repeat: `resolve --applied <that_migration_name>` then `migrate deploy` until all are applied.

---

## One-time fix: mark _all_ migrations as applied (avoid 27 rounds)

**Recommended flow (no need to verify schema first):**

1. **Deploy once** – Let the normal deploy run. It will run `prisma migrate deploy` and fail with e.g. "X already exists". That’s expected.
2. **Run the resolve-all** – Against the same DB (see below), run the loop so every migration is marked as applied.
3. **Deploy again** – Same deploy; this time `migrate deploy` has nothing to do, entrypoint succeeds, app starts.

From `apps/dashboard-server` with the correct `DATABASE_URL` (stage/prod) set:

```bash
cd apps/dashboard-server
for name in $(ls -1 migrations | grep -E '^[0-9]'); do
  npx prisma migrate resolve --applied "$name" 2>/dev/null || true
done
npx prisma migrate deploy
```

- `resolve --applied` for an already-applied migration is a no-op; for a missing one it marks it applied. Running it for every migration name syncs the migration history to “all applied.”
- Then `migrate deploy` will either apply any remaining ones or report “No pending migrations.”

**With Docker (e.g. stage):**

```bash
docker compose run --rm --entrypoint "" dashboard-server sh -c '
  for name in $(ls -1 migrations | grep -E "^[0-9]"); do
    npx prisma migrate resolve --applied "$name" 2>/dev/null || true
  done
  npx prisma migrate deploy
'
```

(Adjust `migrations` path if your Prisma config uses a different folder.)

If deploy still fails, the migration may have failed partway. Then run:

```bash
npx prisma migrate resolve --rolled-back 20260308145520_add_priority_cascade
```

Fix the DB (e.g. drop partial tables if safe—see the migration SQL in `apps/dashboard-server/migrations/20260308145520_add_priority_cascade/migration.sql`), then run `npx prisma migrate deploy` again.

---

## Test locally

1. **Use a test DB only** (e.g. `apps/dashboard-server` Docker Postgres or a separate database). Never run this against real pilot/stage.
2. Get into a failed state: run `cd apps/dashboard-server && yarn db:migrate:deploy` (or `dotenvx run -f .env.test -- npx prisma migrate deploy`) until you see P3018 or P3009, or restore a DB snapshot where the migration previously failed.
3. Apply the fix:
   ```bash
   cd apps/dashboard-server
   npx prisma migrate resolve --applied 20260308145520_add_priority_cascade
   npx prisma migrate deploy
   ```
4. Confirm the last command exits successfully and later migrations (if any) are applied.

---

## After the fix: new deployment

Once you’ve run the fix on **pilot** or **stage**, the next normal deployment (CI pipeline or `docker compose up` on the server) will run `prisma migrate deploy` in the dashboard-server entrypoint. That migration is already marked as applied, so deploy will only run any newer migrations and the app will start. No extra steps—just deploy as usual.

---

## Why this works

- **P3018:** The migration tries to create a table, index, or constraint that already exists (e.g. `VisitGroup`, `Skill_organizationId_name_key`). `resolve --applied` tells Prisma to treat that migration as done and continue.
- **P3009:** A previous run failed and Prisma recorded it. Same fix: mark it applied, then deploy.
- **Multiple failures:** If deploy fails again on a _different_ migration, run `resolve --applied <that_migration_name>` for the new one and `migrate deploy` again. Repeat until no pending migrations.

---

## App error: "column (not available)" on VisitGroup / VisitDependency

If the app (e.g. schedule list) fails with **"Invalid prisma.visitGroup.findMany() … The column (not available) does not exist"**, the migration was marked as applied but the migration SQL never ran, so the `VisitGroup` (or related) table/columns are missing.

- **Short-term:** The schedules query now returns empty visit groups/dependencies when those tables are missing, so the schedule list can load. Check server logs for `[schedules] VisitGroup.findMany failed` to confirm.
- **Proper fix:** Ensure the migration SQL actually runs on that DB. Options: run the migration file manually (e.g. the `CREATE TABLE "VisitGroup"` part from `20260308145520_add_priority_cascade`), or use `migrate resolve --rolled-back` for that migration then `migrate deploy` so Prisma runs it. Prefer fixing the DB so all features (visit groups, dependencies) work.

[Prisma: Resolving migration issues](https://www.prisma.io/docs/orm/prisma-migrate/workflows/troubleshooting#resolution-failed-migrations) · More context: [DEPLOY_TROUBLESHOOTING.md](./DEPLOY_TROUBLESHOOTING.md)
