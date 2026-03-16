# Dashboard environments – checklist (prod, pilot, stage)

All three environments use **the same Clerk** (Clerk production). Each has its **own database** (own RDS). Fix “no org”, “no resources”, or “upload disabled” by ensuring each host has the right env and routing.

**Ingen kodändring.** Problemen här är **DevOps / DB / Clerk-konfiguration**. Endast synk av Clerk mot DB efter reset har gjorts i kod; resten är konfiguration.

---

## Clerk Paths (Configure → Paths) – viktigt

**Nuvarande läge:** Clerk prod är uppsatt för `app.pilot.caire.se`. Därför får prod-användare pilot-URL:er och sessioner kopplade till pilot i stället för prod.

Clerk production-instansens **Application paths** (Home URL, Sign-in, Sign-up, Signing out) måste peka på **rätt** miljö:

| Miljö     | Paths ska peka på                                                       |
| --------- | ----------------------------------------------------------------------- |
| **Prod**  | `https://app.caire.se` (och `/sign-in`, `/sign-up` etc. på samma domän) |
| **Pilot** | `https://app.pilot.caire.se`                                            |

**Om Clerk prod har paths satt till pilot** (t.ex. Home URL = `https://app.pilot.caire.se`): då får "prod"-användare pilot-URL:er, redirects och sessioner kopplade till pilot. Resultat: prod visar Clerk men inte resurser / rätt data, eller kaos mellan miljöer.

**Åtgärd (endast i Clerk Dashboard, ingen kod):** Configure → Paths → sätt Application paths för **prod** till `https://app.caire.se`. Behåll eller skapa separat konfiguration för pilot (`https://app.pilot.caire.se`) om samma Clerk-instans används för båda.

---

## /api/graphql – 404 på pilot och stage (DevOps)

| URL                                      | Status            |
| ---------------------------------------- | ----------------- |
| `https://app.caire.se/api/graphql`       | ✅ 200 (fungerar) |
| `https://app.pilot.caire.se/api/graphql` | ❌ 404            |
| `https://app.stage.caire.se/api/graphql` | ❌ 404            |

**Orsak:** På prod-värden finns reverse proxy (nginx/Caddy/traefik) som skickar `/api/` till dashboard-server (t.ex. port 4000). På pilot- och stage-värdena saknas motsvarande route.

**Åtgärd (endast på pilot- och stage-servrarna, ingen kod):** Lägg till samma `location /api/` (eller `/api/graphql`) och `proxy_pass` till dashboard-server som på prod. Se exempel under "Så fixar du piloten" nedan. Efter ändring: `sudo systemctl reload nginx` (eller motsvarande).

---

## One-page matrix

|                                           | **Prod**                          | **Pilot**                                                   | **Stage**                               |
| ----------------------------------------- | --------------------------------- | ----------------------------------------------------------- | --------------------------------------- |
| **Frontend URL**                          | e.g. app.caire.se                 | app.pilot.caire.se                                          | app.stage.caire.se (or your stage host) |
| **Backend (dashboard-server)**            | Same host or api.caire.se         | Must run and be reachable                                   | Same host or stage API host             |
| **Backend `DATABASE_URL`**                | Prod RDS                          | **Pilot RDS** (caire-prod-pilot…)                           | **Stage RDS** (stage DB)                |
| **Backend `CLERK_SECRET_KEY`**            | Clerk production                  | **Same** Clerk production                                   | **Same** Clerk production               |
| **Frontend `VITE_GRAPHQL_URL`**           | `https://<prod-api>/graphql`      | `https://app.pilot.caire.se/api/graphql` (or pilot API URL) | `https://<stage-api>/graphql`           |
| **Frontend `VITE_CLERK_PUBLISHABLE_KEY`** | Clerk production                  | **Same** Clerk production                                   | **Same** Clerk production               |
| **Routing**                               | `/api/graphql` → dashboard-server | `/api/graphql` must exist and proxy to dashboard-server     | Same                                    |

Rule: **One DB per environment.** Same Clerk everywhere. Each backend must use its own `DATABASE_URL`.

---

## Per-environment checklist

### Prod

- [ ] Backend: `DATABASE_URL` = prod RDS.
- [ ] Backend: `CLERK_SECRET_KEY` = Clerk production.
- [ ] Frontend (build/entrypoint): `VITE_GRAPHQL_URL` and `VITE_CLERK_PUBLISHABLE_KEY` set for prod.
- [ ] Nginx (or similar): `POST /api/graphql` → dashboard-server (e.g. port 4000).
- [ ] **Resources:** If “Resurser” is empty, `myOrganizations` or resources query may return nothing. Check that prod DB has `Organization` rows with `clerkId` matching Clerk prod orgs, and that **sync-clerk** has been run against prod DB so `OrganizationMember` exists for your user.

### Pilot

- [ ] Backend: `DATABASE_URL` = **pilot RDS** (not prod).
- [ ] Backend: `CLERK_SECRET_KEY` = Clerk production (same as prod).
- [ ] Frontend: `VITE_GRAPHQL_URL` = `https://app.pilot.caire.se/api/graphql` (or URL where pilot API is served). If frontend calls `https://app.pilot.caire.se/api/graphql`, that route must exist.
- [ ] Nginx on pilot host: `location /api/graphql { proxy_pass http://127.0.0.1:4000; ... }` (or port where dashboard-server runs). **404 here = no org, disabled upload.**
- [ ] Pilot DB: Migrations applied, Clerk sync run (so `Organization` + `OrganizationMember` for Clerk prod users). Attendo catalog seed for org slug `attendo-pilot` if needed.

### Stage

- [ ] Backend: `DATABASE_URL` = **stage RDS** (not prod, not pilot).
- [ ] Backend: `CLERK_SECRET_KEY` = Clerk production (same as prod).
- [ ] Frontend: `VITE_GRAPHQL_URL` and `VITE_CLERK_PUBLISHABLE_KEY` for stage (same Clerk, stage API URL).
- [ ] Routing: `/api/graphql` (or stage API host) reaches dashboard-server.
- [ ] Stage DB: Migrations applied. Run **sync-clerk** against stage DB (with tunnel if needed) so orgs and members exist; then “org” and resources can show.

---

## Så fixar du piloten (steg för steg)

Pilot visar ingen org oftast av **två** skäl: antingen når frontend inte API:et (404), eller så pekar backend mot fel DB / ingen Clerk-sync har körts.

### 1. På pilot-servern: kör backend och routing

- **Dashboard-server** måste köra på pilot-värden (t.ex. port 4000). Kontrollera att containern/processen är igång.
- **Reverse proxy (nginx/Caddy/traefik)** på samma host måste skicka vidare `/api/graphql` till dashboard-server.

**Nginx-exempel** (på pilot-värden, t.ex. i `/etc/nginx/sites-available/` eller i ett server-block för `app.pilot.caire.se`):

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:4000/;   # eller den port dashboard-server lyssnar på
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

Om frontend anropar `https://app.pilot.caire.se/api/graphql` ska alltså `/api/` matchas och proxy_pass till backend (t.ex. `http://127.0.0.1:4000/` så att request blir `http://127.0.0.1:4000/graphql`). Starta om nginx efter ändring: `sudo systemctl reload nginx`.

**Kontroll:** Öppna `https://app.pilot.caire.se/api/graphql` i webbläsaren eller kör `curl -X POST https://app.pilot.caire.se/api/graphql -H "Content-Type: application/json" -d '{"query":"{ __typename }"}'`. Ska ge 200 (eller GraphQL-svar), inte 404.

### 2. Env på pilot-värden

- **Backend (dashboard-server):**
  - `DATABASE_URL` = pilot-RDS (t.ex. `postgresql://...@caire-prod-pilot....rds.amazonaws.com/...`).
  - `CLERK_SECRET_KEY` = samma Clerk production-nyckel som prod.
- **Frontend (build/entrypoint):**
  - `VITE_GRAPHQL_URL=https://app.pilot.caire.se/api/graphql`
  - `VITE_CLERK_PUBLISHABLE_KEY` = Clerk production (samma som prod).

Så länge frontend anropar `https://app.pilot.caire.se/api/graphql` och routing enligt steg 1 är på plats, ska 404 försvinna.

### 3. Pilot-DB: migreringar + Clerk-sync + (valfritt) Attendo-seed

- Migreringar körs vanligtvis vid deploy (entrypoint `db:migrate:deploy`). Om pilot inte deployas så, kör manuellt mot pilot-DB (t.ex. med tunnel):

  ```bash
  cd apps/dashboard-server
  # Om du behöver tunnel: ./src/scripts/seed-pilot-with-tunnel.sh --tunnel-only
  # I en annan terminal, med .env.pilot som pekar på pilot RDS (eller localhost via tunnel):
  NODE_TLS_REJECT_UNAUTHORIZED=0 dotenvx run -f .env.pilot -- npx prisma migrate deploy
  ```

- **Clerk-sync** (så att org och användare finns i pilot-DB):

  ```bash
  cd apps/dashboard-server
  NODE_TLS_REJECT_UNAUTHORIZED=0 dotenvx run -f .env.pilot -- npx tsx src/scripts/sync-clerk-to-db.ts
  ```

- Om du vill ha Attendo-katalogen på pilot (org med slug `attendo-pilot`):

  ```bash
  dotenvx run -f .env.pilot -- npx tsx src/seed-attendo.ts
  ```

**Full reset + seed** (tunnel + migrate reset + Clerk-sync + Attendo-seed):

```bash
cd apps/dashboard-server
PRISMA_USER_CONSENT_FOR_DANGEROUS_AI_ACTION="ja, kör reset och seed på pilot" ./src/scripts/seed-pilot-with-tunnel.sh
```

### 4. Verifiera i webbläsaren

- Öppna app.pilot.caire.se, logga in med en Clerk-användare som tillhör en org i Clerk production.
- DevTools → Network: anropet till `.../api/graphql` ska ge **200** och svaret på `myOrganizations` ska innehålla minst en org. Då ska org-väljaren och resurser fungera.

---

## Quick verification

1. **Browser → Network:** Call to `.../graphql` returns **200** (not 404). If 404 → fix routing / backend for that host.
2. **Same request → Preview:** `myOrganizations` returns at least one org. If `[]` → backend uses wrong DB or sync-clerk has not been run for that DB.
3. **Backend host:** On the server that runs dashboard-server for that env, `echo $DATABASE_URL` (or inspect `.env`) shows the **correct** RDS for that env (prod / pilot / stage).

---

## See also

- [DEPLOY_TROUBLESHOOTING.md](./DEPLOY_TROUBLESHOOTING.md) – 404, migrations, Clerk, “no resources”.
