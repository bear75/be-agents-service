# Handbook Server – Migration recovery (P3009)

When the handbook-server container exits with **P3009** (“migrate found failed migrations in the target database”), `prisma migrate deploy` will not run until the failed migration is resolved.

## What happened

- Migration `20260206180000_init` was recorded as **failed** in `_prisma_migrations` (e.g. timeout, connection drop, or error mid-run).
- Prisma blocks further `migrate deploy` until that failure is resolved.

## Fix: run `prisma migrate resolve` once against production

You must run **one** of the following against the **production** handbook DB (`handbook_db` on RDS), then redeploy the container.

### Option A – Mark as applied (use when schema is already there)

If the init migration actually succeeded (all handbook tables exist) but Prisma marked it failed (e.g. connection dropped after applying):

```bash
# From a machine that can reach the prod DB (e.g. Webapps EC2 or your laptop with DB access)
cd /path/to/beta-appcaire  # repo root

export DATABASE_URL="postgresql://USER:PASSWORD@caire-prod-new.cdwuayemyua7.eu-north-1.rds.amazonaws.com:5432/handbook_db?sslmode=no-verify&schema=public"

yarn workspace handbook-server exec prisma migrate resolve --applied 20260206180000_init
```

Then restart/redeploy the handbook-server container so it runs `prisma migrate deploy` again (it will see no pending migrations and start the app).

### Option B – Mark as rolled back (use when migration did not complete)

If the migration did **not** complete (tables missing or partial):

```bash
export DATABASE_URL="..."  # same as above

yarn workspace handbook-server exec prisma migrate resolve --rolled-back 20260206180000_init
```

Then restart/redeploy the handbook-server container. The next startup will run `prisma migrate deploy` again and **re-apply** `20260206180000_init`.

## How to choose

- **Check the DB first.** Connect to `handbook_db` and see if tables like `organization_branding`, `system_languages`, `handbook_pages` exist.
  - If **all** init tables exist → use **Option A** (`--applied`).
  - If **any** are missing or schema is incomplete → use **Option B** (`--rolled-back`), then fix any partial state if needed before redeploying.

## After resolve

1. Restart or redeploy the handbook-server container (so entrypoint runs `prisma migrate deploy` again).
2. Confirm https://handbook-api.caire.se/graphql returns 200 (not 404).

## Seeding prod from local dump (via SSH)

**Warning:** This **replaces** the production handbook DB with the dump contents (the dump includes `--clean --if-exists`). Use only when intentionally seeding or restoring prod.

To seed the production handbook DB from a local SQL dump using SSH and the prod DB URL:

1. **Create a dump** (from a DB you want to copy, e.g. dev):

   ```bash
   yarn workspace handbook-server db:backup
   ```

   Output: `apps/handbook-server/backups/handbook_db_<timestamp>.sql`

2. **Set env and run seed** (from monorepo root):

   ```bash
   export PROD_DATABASE_URL="postgresql://USER:PASSWORD@caire-prod-new.cdwuayemyua7.eu-north-1.rds.amazonaws.com:5432/handbook_db?sslmode=no-verify&schema=public"
   export SSH_HOST="ubuntu@<WEBAPPS_EC2_IP>"
   yarn workspace handbook-server db:seed-prod
   ```

   - Get **WEBAPPS_EC2_IP** from GitHub → Repository → Settings → Environments → **prod** → Environment variables.
   - For RDS, include `?sslmode=no-verify&schema=public` in the URL if your client requires it.
   - The script uses `caire-prod.pem` in the repo root for SSH; override with `SEED_PROD_PEM=/path/to/key.pem` if needed.
   - Optional: `DUMP_FILE=apps/handbook-server/backups/handbook_db_2026-02-26T08-59-22.sql` to use a specific dump (default: latest).

The script copies the dump to the EC2 host and runs `psql` there so the connection to RDS stays from a host that has network access.

### After restore: align migration history (dumps with old 13-migration state)

The repo has **one** migration: `20260206180000_init`. Restored dumps may have the **old** 13 migration rows in `_prisma_migrations`. Align so Prisma sees a single applied migration:

**Option 1 – Prisma (when you have Node/Prisma on the host):**

```bash
# From monorepo root with DATABASE_URL set to the restored DB
yarn workspace handbook-server db:align-migrations
```

This truncates `_prisma_migrations` and runs `prisma migrate resolve --applied 20260206180000_init`.

**Option 2 – SQL only (e.g. on EC2 with just psql):**

```bash
psql "$DATABASE_URL" -f /path/to/apps/handbook-server/scripts/align-migration-history.sql
```

Then restart the handbook-server container so it runs `prisma migrate deploy` (it will see no pending migrations).

### Seed prod from your terminal (no SSH)

Only works if your machine can reach prod RDS (VPN, same network, or RDS endpoint reachable). Restores the dump then aligns `_prisma_migrations` in one go.

```bash
export PROD_DATABASE_URL="postgresql://USER:PASSWORD@caire-prod-new....rds.amazonaws.com:5432/handbook_db?sslmode=no-verify&schema=public"
yarn workspace handbook-server db:seed-prod-from-terminal
```

Optional: use a specific dump (default: latest in `backups/`):

```bash
DUMP_FILE=apps/handbook-server/backups/handbook_db_2026-02-26T08-59-22.sql yarn workspace handbook-server db:seed-prod-from-terminal
```

If the script fails with a connection error, prod RDS is not reachable from your laptop; use the SSH-based flow (dump on server + psql there, then align via SQL on server or from a host that can reach RDS).

### If the dump is already on the server

If the SQL dump is already on the EC2 (e.g. in ubuntu’s home or in `~/app`), SSH in and run:

```bash
# Load DATABASE_URL from app env (adjust path if your .env is elsewhere)
set -a; source ~/app/.env; set +a   # or: source ~/prod/.env
psql "$DATABASE_URL" -f ~/handbook_db_2026-02-12T10-31-39.sql
```

Or with the URL set explicitly:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@caire-prod-new.cdwuayemyua7.eu-north-1.rds.amazonaws.com:5432/handbook_db?sslmode=no-verify&schema=public"
psql "$DATABASE_URL" -f ~/handbook_db_2026-02-12T10-31-39.sql
```

## Production endpoints (reference)

| Service        | URL                                            | Notes |
| -------------- | ---------------------------------------------- | ----- |
| Handbook API   | https://handbook-api.caire.se/graphql, /health |       |
| Handbook app   | https://handbook.caire.se                      |       |
| Handbook admin | https://handbook-admin.caire.se                |       |

All three subdomains resolve to the same host (Webapps EC2). If the API is up, `/health` and `/graphql` return 200.

## Reference

- Prisma: [Production troubleshooting](https://www.prisma.io/docs/guides/database/production-troubleshooting)
- Resolve command: `prisma migrate resolve --applied <name>` / `--rolled-back <name>`
