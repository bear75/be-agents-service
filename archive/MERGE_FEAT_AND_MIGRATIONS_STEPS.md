# Step-by-step: Merge feat with origin and keep migrations correct

**Goal:** Get `feat/resources-crud-complete` in sync with `origin/feat/resources-crud-complete` (ux, bug reports, TDD fixtures) without breaking the migration chain or schema.

**Current state (before starting):**

- Local `feat/resources-crud-complete`: has merge commit (cursor → feat) + uncommitted migration/CI changes.
- Origin `feat/resources-crud-complete`: has 3 commits we don't have (ux, bug reports, TDD fixtures).
- Migrations we care about:
  - `20260309134007`: must only add `Visit.visitGroupId` (no second VisitGroup table).
  - `20260310120000_remove_visit_group_id`: must drop that column (with IF EXISTS).
- Schema: `Visit` has no `visitGroupId`; only schedule-scoped `VisitGroup` + `VisitGroupMember`.

---

## Step 1: Commit all local migration and CI work

We need everything committed so the merge doesn't lose it and conflict resolution is clear.

```bash
cd /path/to/beta-appcaire
git status   # review list
git add apps/dashboard-server/migrations/
git add apps/dashboard-server/schema.prisma
git add apps/dashboard-server/package.json
git add apps/dashboard-server/src/graphql/resolvers/solution/mutations/__tests__/startOptimization.test.ts
git add apps/dashboard-server/src/scripts/e2e-submit-to-timefold.ts
git add .github/workflows/pr-checks.yml
git add .github/workflows/test-build-deploy.yml
git add .github/workflows/test-build-deploy-prod.yml
git add .github/workflows/test-build-deploy-prod-pilot.yml
# Optional: add seed/script/docs if you want them in this branch
# git add apps/dashboard-server/src/seed-attendo.ts apps/dashboard-server/src/seed-insets.ts ...
git status
git commit -m "fix(migrations): single VisitGroup, add remove_visit_group_id; CI migration job and deploy comments"
```

- **If you prefer one commit per concern:** first commit only `apps/dashboard-server/migrations/` + `schema.prisma`, then commit workflows + test fix + e2e script.
- **Important:** Migration folder `20260310120000_remove_visit_group_id` must be added and committed (it's currently untracked).

---

## Step 2: Fetch latest from origin

```bash
git fetch origin
git log --oneline -3 origin/feat/resources-crud-complete
```

Confirm you see the 3 commits (ux, bug reports, TDD fixtures).

---

## Step 3: Merge origin/feat into your current branch

```bash
git checkout feat/resources-crud-complete
git merge origin/feat/resources-crud-complete -m "Merge origin/feat/resources-crud-complete (ux, bug reports, TDD fixtures)"
```

- If merge is clean, go to Step 5.
- If there are conflicts, go to Step 4.

---

## Step 4: Resolve conflicts (keep migrations and schema correct)

**If the merge reports conflicts:**

1. **List conflicted files**

   ```bash
   git diff --name-only --diff-filter=U
   ```

2. **For these paths, keep our version (the one that matches the migration chain and current schema):**
   - `apps/dashboard-server/schema.prisma`  
     → Keep **ours**: no `Visit.visitGroupId`, only schedule-scoped `VisitGroup` and `VisitGroupMember`.
   - `apps/dashboard-server/migrations/20260309134007_add_visit_group_and_visit_group_id_on_visit/migration.sql`  
     → Keep **ours**: only adds `Visit.visitGroupId` + index + FK (no second VisitGroup table).
   - `apps/dashboard-server/migrations/20260310120000_remove_visit_group_id/migration.sql`  
     → Keep **ours**: drops FK, index, and column with IF EXISTS.

   Commands (run from repo root):

   ```bash
   git checkout --ours apps/dashboard-server/schema.prisma
   git add apps/dashboard-server/schema.prisma

   git checkout --ours apps/dashboard-server/migrations/20260309134007_add_visit_group_and_visit_group_id_on_visit/migration.sql
   git add apps/dashboard-server/migrations/20260309134007_add_visit_group_and_visit_group_id_on_visit/migration.sql

   git checkout --ours apps/dashboard-server/migrations/20260310120000_remove_visit_group_id/migration.sql
   git add apps/dashboard-server/migrations/20260310120000_remove_visit_group_id/migration.sql
   ```

3. **For any other conflicted file** (e.g. seed, workflows, app code):
   - Resolve manually: keep both sides' useful changes where possible, or choose theirs if it's only the ux/bug/TDD changes and we have no local edits there.

4. **Finish the merge**
   ```bash
   git add .
   git status
   git commit -m "Merge origin/feat/resources-crud-complete (ux, bug reports, TDD fixtures); keep migration and schema fixes"
   ```

---

## Step 5: Verify migrations

From repo root:

```bash
cd apps/dashboard-server
# Use a throwaway DB or your normal dev DB
export DATABASE_URL="postgresql://..."   # or use .env
npx prisma migrate deploy
```

- If `migrate deploy` succeeds, the migration chain is good.
- If it fails (e.g. "relation already exists", "column does not exist"), stop and fix the migration or schema before pushing.

Optional: run the dashboard-server test suite (including DB) to confirm nothing is broken.

---

## Step 6: Push to origin

```bash
git push origin feat/resources-crud-complete
```

- If push is rejected (e.g. "non-fast-forward"), **do not** force-push without re-reading the plan. Usually it means someone else pushed to `feat/resources-crud-complete`; fetch again and merge (or rebase, if you prefer) and then push.

---

## Step 7: GitHub PRs

- **PR 97** (feat → main): will now show the full history including cursor merge + ux/bug/TDD + migration fixes.
- **PR 100** (cursor → feat): close it with a comment that the work was merged manually into `feat/resources-crud-complete` (merge commit) and is included in this branch.

---

## Checklist before you push

- [ ] All migration-related changes committed (including `20260310120000_remove_visit_group_id`).
- [ ] Merge of `origin/feat/resources-crud-complete` done; conflicts resolved with schema and migrations kept correct.
- [ ] `prisma migrate deploy` runs successfully.
- [ ] No unintended changes to `schema.prisma` or migration SQL (Visit has no `visitGroupId`; only add-then-drop migrations for it).
