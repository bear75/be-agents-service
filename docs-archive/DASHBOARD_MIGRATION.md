# Dashboard Migration: HTML → React

**One doc for fresh sessions.** Explains what changed, why, and how.

---

## Old Setup (What)

**Classic HTML pages** served as static files:

| Page | Purpose |
|------|---------|
| `overview.html` | Sessions overview (orchestrator runs, status, PR links) |
| `commands.html` | Commands & docs (links to markdown files) |
| `engineering.html` | Start jobs, view agents, running jobs |
| `kanban.html` | Task board (Pending → Completed) |
| `management-team.html` | CEO dashboard, upload tasks, hire/fire agents |
| `sales-marketing.html` | Campaigns, leads |
| `rl-dashboard.html` | RL experiments, patterns |
| `settings.html` | Integrations config |

**Assets:** `style.css`, `app.js` shared across all pages.

**Location:** `apps/server/public/` (previously `dashboard/public/`).

---

## Old Setup (Why It Was Removed)

- HTML was agreed to be "no good" — separate pages, no shared state, duplicated nav
- Mixed paradigms: React app at `/` plus 8 classic HTML pages
- Two nav systems: React had Quick Links pointing to HTML; HTML had its own nav
- Harder to maintain: inline JS, scattered styles, no component reuse

---

## New Setup (What)

**Single React SPA** at `http://localhost:3030`:

| Route | Purpose |
|------|---------|
| `/` | Workspace (repo selector, workspace, plans, agents) |
| `/sessions` | Sessions overview |
| `/kanban` | Task board |
| `/engineering` | Start jobs, agents, running jobs |
| `/commands` | Doc links |
| `/settings` | Integrations list |

**One entry point.** React Router handles client-side routing. Shared layout with nav.

---

## New Setup (Why)

- Single codebase: React only, no HTML
- One nav, one layout, shared state (e.g. `selectedRepo` in layout)
- Reuses existing API: `/api/sessions`, `/api/tasks`, `/api/jobs`, `/api/agents`, etc.
- Easier to extend: add routes, components, hooks

---

## How (Implementation So Far)

### 1. Removed

- All `.html` pages except React shell (`index.html`)
- `style.css`, `app.js`
- Quick Links nav in `DashboardPage` that pointed to HTML

### 2. API Client (`apps/dashboard/src/lib/api.ts`)

- `fetchRaw<T>()` for endpoints that return raw JSON (sessions, tasks, jobs, agents, data, integrations, rl)
- `fetchApi<T>()` for endpoints that return `{ success, data }` (repos, workspace, plans)
- New functions: `getSessions`, `getTasks`, `getJobs`, `startJob`, `stopJob`, `getHrAgents`, `getIntegrations`, etc.

### 3. Types (`apps/dashboard/src/types/index.ts`)

- `DbSession`, `DbTask`, `JobInfo`, `DbAgent`, `DbIntegration`, etc.

### 4. React Router

- `BrowserRouter` in `App.tsx`
- Routes: `/`, `/sessions`, `/kanban`, `/engineering`, `/commands`, `/settings`
- `Layout` component with shared header, nav, footer, `RepoSelector`

### 5. Pages

- `SessionsPage` — table of sessions from `/api/sessions`
- `KanbanPage` — columns by status, task cards from `/api/tasks`
- `EngineeringPage` — start job form, jobs list, agents grid, log modal
- `CommandsPage` — doc links to `/api/file/docs?path=...`
- `SettingsPage` — integrations from `/api/integrations`

### 6. Server

- `GET /api/file/docs?path=guides/quick-start.md` — serves docs from `docs/` dir
- SPA fallback: non-API GET requests get `index.html`

### 7. DashboardPage

- Uses `useOutletContext` for `selectedRepo` from Layout
- Header/footer moved to Layout; only tab content remains

---

## Not Yet Migrated

- **Management team** — CEO dashboard, upload tasks, hire/fire (API exists)
- **Sales & marketing** — campaigns, leads (API exists)
- **RL dashboard** — experiments, patterns (API exists)

These can be added as new React routes when needed.

---

## Quick Reference

```
yarn build:unified   # Build React → apps/server/public/
yarn start           # Server on 3030
yarn dev             # Build + dev with hot reload
```

**Dashboard:** http://localhost:3030

---

## URL Reference: Old → New

This section maps old HTML URLs to new React routes:

| Old URL | New URL | Notes |
|---------|---------|-------|
| `/` or `/overview.html` | `/sessions` | Sessions overview moved to dedicated route |
| `/kanban.html` | `/kanban` | Same purpose, React implementation with drag & drop |
| `/engineering.html` | `/engineering` | Same purpose, React implementation |
| `/commands.html` | `/commands` | Same purpose, React implementation |
| `/settings.html` | `/settings` | Same purpose, React implementation |
| `/management-team.html` | _Not yet migrated_ | Will be `/management` when implemented |
| `/sales-marketing.html` | _Not yet migrated_ | Will be `/marketing` when implemented |
| `/rl-dashboard.html` | _Not yet migrated_ | Will be `/rl` when implemented |

**Important:** Old `.html` URLs will either 404 or redirect to the React app (SPA fallback). Update all bookmarks and links to use the new URLs without `.html` extension.

---

## Troubleshooting

### Docs Endpoint Not Working

**Symptom:** Clicking doc links in `/commands` shows 404 or fails to load markdown.

**Cause:** Usually a server build or restart issue. The file route may not be loaded correctly.

**Fix:**
```bash
# 1. Rebuild server
cd apps/server
yarn build

# 2. Restart server via launchd
launchctl unload ~/Library/LaunchAgents/com.appcaire.agent-server.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.agent-server.plist

# 3. Or restart manually
yarn workspace server start

# 4. Test endpoint
curl "http://localhost:3030/api/file/docs?path=guides/quick-start.md"
```

**Verify:** The endpoint should return markdown text content. If you get JSON with an error, check that:
- `docs/guides/quick-start.md` exists
- Server is running on port 3030
- No TypeScript compilation errors in `apps/server/dist/`

---

### React Router Not Working (404 on Refresh)

**Symptom:** Direct URL access like `http://localhost:3030/kanban` returns 404 when you refresh.

**Cause:** SPA fallback is not configured correctly in server.

**Fix:**

Check `apps/server/src/index.ts` has this fallback:

```typescript
// SPA fallback: serve index.html for non-API GET requests
app.get('*', (req, res, next) => {
  if (req.path.startsWith('/api/')) return next();
  res.sendFile(path.join(STATIC_DIR, 'index.html'));
});
```

This is already implemented. If still broken:
1. Rebuild server: `cd apps/server && yarn build`
2. Restart server (see above)

---

### Kanban Drag & Drop Not Working

**Symptom:** Cannot drag tasks between columns, or drag works but status doesn't update.

**Cause:**
- Missing API endpoint: `/api/tasks/:id/status`
- Database method `updateTask()` not exported
- Frontend not calling `updateTaskStatus()`

**Fix:**

1. Verify API endpoint exists:
```bash
curl -X PATCH http://localhost:3030/api/tasks/TASK_ID/status \
  -H "Content-Type: application/json" \
  -d '{"status":"in_progress"}'
```

2. Check database exports in `lib/database.js`:
```javascript
module.exports = {
  // ... other exports
  updateTask,
  updateTaskStatus,
};
```

3. Rebuild and restart server (see above)

---

### Teams API Not Found

**Symptom:** `/api/teams` returns 404.

**Cause:** Teams route not registered in server index.

**Fix:**

Check `apps/server/src/index.ts` includes:
```typescript
import teamsRouter from './routes/teams.js';
// ...
app.use('/api/teams', teamsRouter);
```

Rebuild and restart server.

---

### TypeScript Compilation Errors

**Symptom:** Build fails with type errors.

**Cause:** Missing types or imports in dashboard code.

**Fix:**

1. Check `apps/dashboard/src/types/index.ts` has all required types:
   - `DbTeam`, `DbTeamWithDetails` for teams
   - `DbTask`, `DbAgent`, `DbSession` for other entities

2. Check API client imports types correctly:
```typescript
import type { DbTeam, DbTask } from '../types';
```

3. Run type check:
```bash
cd apps/dashboard
yarn tsc --noEmit
```

---

## Testing Checklist

After building and restarting:

- [ ] Dashboard loads at `http://localhost:3030`
- [ ] All navigation links work (Sessions, Kanban, Engineering, Commands, Settings)
- [ ] Direct URL access works (refresh on `/kanban` stays on kanban)
- [ ] Kanban drag & drop works (task moves between columns)
- [ ] Task status updates persist (refresh page, task stays in new column)
- [ ] Doc links in Commands page load markdown
- [ ] Teams API works: `curl http://localhost:3030/api/teams`
- [ ] No console errors in browser dev tools

---

## Related Documentation

- [API_ENDPOINTS.md](./API_ENDPOINTS.md) - Complete REST API reference
- [ARCHITECTURE.md](./ARCHITECTURE.md) - System architecture overview
- [README.md](./README.md) - Documentation index
