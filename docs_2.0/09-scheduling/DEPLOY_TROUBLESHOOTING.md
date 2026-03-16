# Dashboard deploy troubleshooting (stage / pilot / prod)

After deploying from `feature/multi-step-upload-wizard` (or any branch), use this checklist when "nothing works" — wrong schema, 404 on API, Clerk issues, no schedules, disabled upload.

**→ One-page matrix for prod / pilot / stage:** [ENVIRONMENT_CHECKLIST.md](./ENVIRONMENT_CHECKLIST.md)

---

## Why deploy doesn’t run migrations (reliably)

Deploy **does** run migrations: the dashboard-server container’s **entrypoint** runs `yarn db:migrate:deploy` before starting the app. So “deploy doesn’t run migrations” usually means one of:

1. **`DATABASE_URL` is not set in the container**  
   The image has no `.env`. The only source for `DATABASE_URL` is the **process environment** set by Docker on the EC2 host (e.g. `docker-compose` with `env_file: .env` or `environment: DATABASE_URL`). If the compose file or `.env` on that host doesn’t pass `DATABASE_URL`, Prisma has no URL and migrations don’t run (or fail). The entrypoint now **exits with a clear error** if `DATABASE_URL` is missing.

2. **`DATABASE_URL` is wrong for that environment**  
   GitHub Actions never set `DATABASE_URL`; they only update image tags and `VITE_*`. So `DATABASE_URL` is whatever is in each EC2’s `/home/ubuntu/app/.env` (or compose). If stage/pilot/prod share a bad or copied `.env`, migrations run against the wrong RDS and some DBs stay on an old schema.

3. **Migration fails and the container exits**  
   Entrypoint uses `set -e`. If `prisma migrate deploy` fails (wrong URL, network, credentials), the script exits and the app never starts. The container may sit in a restart loop; the “right” DB never gets migrations until someone fixes env and restarts.

**Fix:** On **each** EC2 (stage, pilot, prod), ensure the compose file passes `DATABASE_URL` into the dashboard-server service (e.g. `env_file: .env`) and that `/home/ubuntu/app/.env` contains the **correct** RDS URL for that environment. Optionally store per-env DB URLs in GitHub secrets and have the workflow write `DATABASE_URL` into the host’s `.env` before `docker compose up`.

### How we detect migration/startup failure in CI

The **stage deploy job** (push to `main` → `test-build-deploy.yml`) now checks container status after `docker compose up -d`:

- Waits 15 seconds for containers to start (migrations run in the dashboard-server entrypoint).
- Runs `docker compose ps -a` and fails the job if any container has status **Exited**.
- On failure, it prints the last 80 lines of `docker compose logs` so you see migration errors or "DATABASE_URL is not set".

So: **if migrations fail or `DATABASE_URL` is missing, the deploy job will fail** and you’ll see the reason in the "Deploy to Server via SSH" step logs. Fix `DATABASE_URL` (and/or schema) on the stage host, then re-run the workflow or push again.

---

## Migration failed: P3018 / P3009 (VisitGroup already exists) – DevOps

**Symptom (pilot):**

```
Error: P3018
Migration name: 20260308145520_add_priority_cascade
Database error code: 42P07
ERROR: relation "VisitGroup" already exists
```

**Symptom (stage):**

```
Error: P3009
migrate found failed migrations in the target database
The `20260308145520_add_priority_cascade` migration started at ... failed
```

**Cause:** The migration `20260308145520_add_priority_cascade` creates tables `VisitGroup` and `VisitGroupMember`. On pilot, those tables already exist (e.g. from a previous partial run or different source), so `CREATE TABLE` fails. On stage, the migration was attempted and failed, so it is recorded as failed and Prisma will not apply new migrations until it is resolved.

**Recovery (per environment, run from dashboard-server with correct `DATABASE_URL` for that DB):**

1. **If the database already has the tables** (e.g. `VisitGroup` and `VisitGroupMember` exist with the expected columns): mark the migration as applied so Prisma skips running it and can continue with later migrations:

   ```bash
   cd apps/dashboard-server
   # Set DATABASE_URL for pilot or stage (e.g. .env or export)
   npx prisma migrate resolve --applied 20260308145520_add_priority_cascade
   ```

   Then run `npx prisma migrate deploy` again.

2. **If the migration failed partway and the DB is inconsistent:** use `prisma migrate resolve --rolled-back 20260308145520_add_priority_cascade`, then fix the DB (e.g. drop the tables if they were partially created) and run `prisma migrate deploy` again. Only do this if you are sure no data in those tables is needed.

**Full DevOps guide (including how to test locally):** [DEVOPS_MIGRATION_RECOVERY.md](./DEVOPS_MIGRATION_RECOVERY.md)

**Reference:** [Prisma: Resolving migration issues](https://www.prisma.io/docs/orm/prisma-migrate/workflows/troubleshooting#resolution-failed-migrations)

---

## 1. GraphQL URL (404 → no data, disabled upload)

**Symptom:** Console shows `api/graphql` 404, no schedules, upload button disabled or broken.

**Cause:** Frontend is calling a GraphQL URL that doesn’t exist or isn’t reachable for that environment.

**Fix per environment:**

| Environment | Set in GitHub / server                | Value (example)                                                                                                                      |
| ----------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Stage**   | Stage env vars / `.env` on stage host | `VITE_GRAPHQL_URL=https://<stage-api-host>/graphql` (and `VITE_GRAPHQL_WS_URL=wss://...`)                                            |
| **Pilot**   | Prod env (pilot deploy)               | `VITE_GRAPHQL_URL` / `VITE_GRAPHQL_WS_URL` → pilot API (e.g. `https://app.caire.se/api/graphql` if same host, or pilot-specific URL) |
| **Prod**    | Prod env                              | `VITE_GRAPHQL_URL=https://app.caire.se/api/graphql` (or whatever serves the dashboard-server)                                        |

- The **dashboard** build gets these at **runtime** via `window.env` (see `apps/dashboard/entrypoint.sh` and `public/env.js`). So the **server** (EC2) where the dashboard container runs must have `VITE_GRAPHQL_URL` and `VITE_GRAPHQL_WS_URL` in its `.env` (or equivalent) so the entrypoint can inject them.
- If the API is on the **same origin** (e.g. `https://app.caire.se/api/graphql`), the reverse proxy (e.g. nginx) must route `/api/graphql` to the dashboard-server (e.g. port 4000). If that route is missing or wrong → 404.

**Quick check:** Open the app in the browser, Network tab, find the request to `graphql`. If it’s 404, fix the URL or the proxy.

---

## 2. DB schema (missing tables, e.g. `Inset`)

**Symptom:** Backend or UI errors about missing relation/table (e.g. `Inset`), or "relation Inset does not exist".

**Cause:** Migrations haven’t been applied to **that** database. The deploy **does** run `prisma migrate deploy` in the dashboard-server container entrypoint, but only against the DB pointed to by **`DATABASE_URL`** in the **container’s** environment. The **image has no `.env`**; `DATABASE_URL` must be provided by Docker (e.g. the EC2 host’s `docker-compose` with `env_file: .env` or `environment: DATABASE_URL`). If `DATABASE_URL` is missing or wrong on that host, migrations run against the wrong DB or fail (container may exit before starting the app).

**Fix:**

- On **each** EC2 (stage / pilot / prod), the `.env` (or env passed to the dashboard-server container) must have:
  - **Stage:** `DATABASE_URL` → stage RDS
  - **Pilot:** `DATABASE_URL` → pilot RDS (`caire-prod-pilot...`)
  - **Prod:** `DATABASE_URL` → prod RDS
- If `DATABASE_URL` was wrong or missing, the running container may have applied migrations to the wrong DB (or failed at startup). Set the correct `DATABASE_URL` for that environment, then **redeploy or restart** the dashboard-server so the entrypoint runs again and applies migrations to the right DB.

**Quick check:** Connect to the RDS for that env (e.g. TablePlus) and run:

```sql
SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = 'Inset';
```

If no row → migrations haven’t been applied to that DB. Fix `DATABASE_URL` and redeploy/restart.

---

## 3. Clerk (dev keys, org not found)

**Symptom:** "Clerk development keys" warning, or "No organizations found" / wrong org.

**Cause:** App is using Clerk **development** keys in a deployed environment, or the Clerk org isn’t linked in the DB.

**Fix:**

- For **stage / pilot / prod**, use a **production** Clerk application and set:
  - `VITE_CLERK_PUBLISHABLE_KEY` (and any other Clerk env the app needs) from that **production** app.
- Ensure the **same** Clerk org ID is used in the backend (e.g. `Organization.clerkId`) so the dashboard’s org selector and schedule/upload flows see the right org.

---

## 4. No resources / upload schedules disabled / no org

**Symptom:** Prod: resources page empty. Pilot / stage: no org, upload disabled, "Select an organization" or nothing loads.

**Cause:** Either (A) the frontend never gets org data because the API is unreachable (404, wrong URL), or (B) the API is reachable but **`myOrganizations`** returns `[]` because the backend uses the wrong DB or the DB has no orgs synced from Clerk.

- **404 on `/api/graphql`** → Fix routing and `VITE_GRAPHQL_URL` for that environment (see [ENVIRONMENT_CHECKLIST.md](./ENVIRONMENT_CHECKLIST.md)).
- **200 but `myOrganizations` = []** → Backend’s `DATABASE_URL` must point to that env’s DB, and that DB must have **Organization** rows with `clerkId` matching Clerk prod. Run **sync-clerk** against that DB (pilot: part of seed; prod/stage: run manually or add to deploy).

The frontend only shows data when **`selectedOrganizationId`** is set. That comes from **`myOrganizations`**: the backend returns organizations whose **`clerkId`** matches one of the **Clerk orgs the signed-in user is a member of** (from the JWT). So:

1. There must be an **Organization** row in the DB with `clerkId = <the org the user is in in Clerk>`.
2. The user must be signed in and have that org in their Clerk memberships (and optionally selected as active org).

**How Clerk sync works**

- **`sync-clerk-to-db.ts`** (run manually): Calls Clerk API, fetches all organizations and all users with their memberships. For each Clerk org it creates or updates an **Organization** in the DB (keyed by `clerkId`). For each user it creates or updates **OrganizationMember** (userId → organizationId, role). This script does **not** run on deploy; run it when you add new Clerk orgs or users and need them in the DB.
- **At runtime:** The dashboard backend does **not** use `OrganizationMember` for `myOrganizations`. It uses the JWT: the user's list of Clerk org IDs (`organizationMemberships`) and optionally `activeOrganizationId`. It then looks up **Organization** rows where `clerkId` is in that list. So every org the user is in (in Clerk) must exist in the DB with that `clerkId`.

**Fix for pilot (after seed)**

Pilot **syncs all orgs from Clerk production** (no `CLERK_ORG_ID` in `.env.pilot`). The seed script runs Clerk sync first, then attaches the Attendo catalog to the org with slug `attendo-pilot` (that slug must exist in Clerk for the Attendo pilot org). All production users can log in to their orgs. To run only the tunnel and sync/seed manually: `cd apps/dashboard-server`, start the tunnel with `./src/scripts/seed-pilot-with-tunnel.sh --tunnel-only`, then `NODE_TLS_REJECT_UNAUTHORIZED=0 yarn sync-clerk:pilot` and `dotenvx run -f .env.pilot -- npx tsx src/seed-attendo.ts`.

**Quick check:** In the browser, Network tab, find the `myOrganizations` GraphQL request. If it returns `[]`, the backend found no Organization with `clerkId` matching your Clerk memberships; run sync-clerk for that env or ensure the seeded org's `clerkId` matches your Clerk org.

---

## 5. Branch-specific (e.g. `feature/multi-step-upload-wizard`)

- The **frontend** on this branch uses **current** GraphQL (e.g. `scheduleType`, no `scheduleDate`). So the backend must expose the **current** schema (migrations applied).
- No **new** env vars are required for the multi-step upload wizard beyond the usual: `VITE_GRAPHQL_URL`, `VITE_GRAPHQL_WS_URL`, and backend `DATABASE_URL`.
- If something still breaks only after this branch, compare:
  - Which **GraphQL operations** the wizard uses (e.g. `parseAndValidateSchedule`, `finalizeScheduleUpload`, `organization`, `serviceAreas`) and confirm the **backend** for that environment has those resolvers and that **migrations** have been applied so the DB has the expected tables (including `Inset`, `DaySlot`, etc.).

---

## Order of operations

1. **Fix GraphQL URL** for the environment (stops 404, restores API calls).
2. **Fix `DATABASE_URL`** for that environment and **redeploy/restart** dashboard-server (applies migrations to correct DB).
3. **Fix Clerk** keys and org linkage for non-dev environments.
4. **If no resources/upload:** Ensure the user's Clerk org exists in the DB (`clerkId` match). Pilot runs Clerk sync automatically (all production orgs); for other envs run **sync-clerk** or ensure the org exists.

After that, re-test schedules list and upload; if something still fails, the browser Network/Console and backend logs will point to the next issue (e.g. a specific mutation or missing table).
