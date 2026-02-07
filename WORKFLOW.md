# Workflow: Tasks, Sessions, Learnings & Compound Knowledge

Complete guide to how work flows through the multi-agent system, from priority creation to merged PRs and accumulated knowledge.

---

## Table of Contents

1. [Priority Files (Product Backlog)](#priority-files-product-backlog)
2. [Sessions (Sprints)](#sessions-sprints)
3. [Tasks (Sprint Backlog)](#tasks-sprint-backlog)
4. [Learnings (Retrospectives)](#learnings-retrospectives)
5. [Compound Knowledge](#compound-knowledge)
6. [Complete Workflow Example](#complete-workflow-example)

---

## Priority Files (Product Backlog)

### What They Are

Priority files are your **product backlog** - user stories and features you want built.

**Location:** `~/HomeCare/beta-appcaire/reports/priorities-YYYY-MM-DD.md`

### Format

```markdown
# Priority 1

**Description:** [User story or feature description]

**Expected outcome:**
- [Acceptance criterion 1]
- [Acceptance criterion 2]
- [Acceptance criterion 3]

**Files:**
- [Relevant file paths for context]

**Dependencies:** [Other priorities this depends on]

**Complexity:** Low | Medium | High
```

### Example

```markdown
# Priority 1

**Description:** Add employee certifications tracking system

**Expected outcome:**
- Database table for certifications with expiry dates
- GraphQL API for CRUD operations
- UI page to view and manage certifications
- Automated expiry notifications

**Files:**
- apps/dashboard-server/src/schema.prisma
- apps/dashboard-server/src/schema.graphql
- apps/dashboard/src/pages/employees/

**Dependencies:** None

**Complexity:** Medium
```

### How Orchestrator Reads It

The orchestrator analyzes the priority file to determine:

1. **Which specialists needed?**
   - "database" → Backend specialist
   - "UI page" → Frontend specialist
   - "schema.prisma" → Backend specialist

2. **Complexity estimate?**
   - Low: ~5-10 tasks
   - Medium: ~10-15 tasks
   - High: ~15-25 tasks

3. **Dependencies?**
   - If depends on Priority 2, check if Priority 2 is completed

### Creation Tips

**Good priorities:**
- ✅ Clear user value ("Add certifications tracking")
- ✅ Specific outcomes (not vague)
- ✅ Include acceptance criteria
- ✅ Mention relevant files for context

**Bad priorities:**
- ❌ Too vague ("Improve dashboard")
- ❌ No acceptance criteria
- ❌ Multiple unrelated features in one priority
- ❌ Missing complexity estimate

---

## Sessions (Sprints)

### What They Are

A **session** is one execution of the orchestrator - equivalent to a sprint in Agile.

**Location:** `.compound-state/session-{timestamp}/`

### Session Lifecycle

```
1. Planning      → Orchestrator analyzes priority
2. Phase 1       → Backend + Infrastructure (parallel)
3. Phase 2       → Frontend (sequential, waits for backend)
4. Verification  → QA checks quality
5. PR Creation   → Deliverable ready for review
6. Completed     → Session ends, PR awaits merge
```

### Session Directory

```
.compound-state/session-1770451234/
├── session.json           # Session metadata
├── orchestrator.json      # Orchestrator state
├── backend.json           # Backend specialist state
├── frontend.json          # Frontend specialist state
├── infrastructure.json    # Infrastructure specialist state
└── verification.json      # Verification specialist state
```

### Session Metadata (session.json)

```json
{
  "sessionId": "session-1770451234",
  "createdAt": "2026-02-07T23:00:00Z",
  "status": "active",
  "agents": ["orchestrator", "backend", "frontend", "verification"]
}
```

### Orchestrator State (orchestrator.json)

```json
{
  "status": "in_progress",
  "startTime": "2026-02-07T23:00:00Z",
  "targetRepo": "/Users/bjornevers_MacPro/HomeCare/beta-appcaire",
  "priorityFile": "reports/priorities-2026-02-07.md",
  "branchName": "feature/add-certifications",
  "phase": "phase2_frontend",
  "specialists": {
    "backend": "completed",
    "frontend": "in_progress",
    "infrastructure": "completed",
    "verification": "pending"
  }
}
```

### Session Logs

```
logs/orchestrator-sessions/session-1770451234/
├── orchestrator.log       # Orchestrator coordination logs
├── backend.log            # Backend specialist logs
├── frontend.log           # Frontend specialist logs
├── infrastructure.log     # Infrastructure specialist logs
└── verification.log       # Verification specialist logs
```

### Session States

| State | Meaning | Duration |
|-------|---------|----------|
| `planning` | Analyzing priority, creating PRD | 1-2 min |
| `phase1_parallel` | Backend + Infra working | 5-15 min |
| `phase2_frontend` | Frontend working | 5-10 min |
| `verification` | QA checking quality | 2-5 min |
| `pr_creation` | Creating pull request | 1 min |
| `completed` | Session done, PR created | N/A |
| `blocked` | Waiting for resolution | Until fixed |
| `failed` | Critical error, needs PM | Until fixed |

### Viewing Sessions

**Dashboard:** http://localhost:3030

**CLI:**
```bash
# List all sessions
ls -la ~/.compound-state/

# View latest session state
cat ~/.compound-state/session-*/orchestrator.json | jq '.'

# View session logs
tail logs/orchestrator-sessions/session-*/orchestrator.log
```

---

## Tasks (Sprint Backlog)

### What They Are

Tasks are the breakdown of a priority into concrete, implementable steps.

**Location:** `tasks/prd.json` (generated by orchestrator)

### Format

```json
{
  "priority": "Add employee certifications tracking",
  "tasks": [
    {
      "id": 1,
      "description": "Update Prisma schema with Certification model",
      "status": "pending",
      "specialist": "backend",
      "estimatedMinutes": 5
    },
    {
      "id": 2,
      "description": "Generate database migration for certifications",
      "status": "pending",
      "specialist": "backend",
      "estimatedMinutes": 2
    },
    {
      "id": 3,
      "description": "Add GraphQL types for Certification",
      "status": "pending",
      "specialist": "backend",
      "estimatedMinutes": 5
    }
  ]
}
```

### Task States

- `pending` - Not started
- `in_progress` - Currently being worked on
- `completed` - Done and committed
- `blocked` - Waiting for dependency or blocker resolution
- `skipped` - Not needed (scope changed)

### Task Assignment

Orchestrator assigns tasks to specialists based on keywords:

```
Task: "Update Prisma schema"
Keywords: "schema" → Backend specialist

Task: "Add UI page for certifications"
Keywords: "UI page" → Frontend specialist

Task: "Update package.json with date-fns"
Keywords: "package.json" → Infrastructure specialist
```

### Task Tracking

Specialists write task progress to their state files:

```json
{
  "agentName": "backend",
  "completedTasks": [
    {
      "id": "backend-1",
      "description": "Updated Prisma schema",
      "duration": 180,
      "artifacts": ["apps/dashboard-server/src/schema.prisma"]
    }
  ]
}
```

---

## Learnings (Retrospectives)

### What They Are

**Learnings** are patterns, mistakes, and best practices extracted from completed sessions.

**Trigger:** Daily at 10:30 PM (daily-compound-review.sh)

### Process

1. **Scan Sessions**: Review all Claude Code threads from last 24 hours
2. **Extract Patterns**:
   - What worked well (keep doing)
   - What caused blockers (avoid in future)
   - New patterns discovered (add to knowledge base)
3. **Update CLAUDE.md**: Add to "Common Mistakes" or other sections
4. **Commit**: Commit CLAUDE.md updates to main branch

### Example Learning

```markdown
## Common Mistakes & How to Avoid

### 11. Forgetting to Run Codegen After GraphQL Changes

**Symptom:**
```
Cannot find module '@appcaire/graphql' or corresponding type declarations
```

**Cause:** Created .graphql operations but didn't run codegen

**Fix:**
```bash
yarn workspace @appcaire/graphql codegen
```

**Rule:** ALWAYS run codegen immediately after creating/modifying .graphql files

**Occurrences:** 5 → 2 (improving!)
**Added:** 2026-02-07
```

### Learning Categories

1. **Common Mistakes** - Things that went wrong
2. **Best Practices** - Things that went right
3. **Performance Improvements** - Optimizations discovered
4. **Security Patterns** - Security lessons
5. **Architecture Decisions** - Why we chose approach X over Y

### Viewing Learnings

```bash
# Read CLAUDE.md
cat ~/HomeCare/beta-appcaire/CLAUDE.md

# See recent updates
git log --since="1 week ago" --grep="docs.*CLAUDE.md"

# See specific section
grep -A 20 "Common Mistakes" CLAUDE.md
```

---

## Compound Knowledge

### What It Is

**Compound knowledge** is the accumulated learnings from all sessions over time.

Like compound interest, knowledge grows exponentially:
- Week 1: 5 learnings
- Week 2: 5 + 3 new = 8 learnings
- Week 3: 8 + 2 new = 10 learnings
- Week 4: 10 + 1 new = 11 learnings

Mistakes decrease as knowledge increases:
- Week 1: Apollo Client timing error (3 times)
- Week 2: Apollo Client timing error (1 time)
- Week 3: Apollo Client timing error (0 times) ✅

### Storage Locations

**Primary:**
- `CLAUDE.md` (root) - General learnings
- `apps/*/CLAUDE.md` - App-specific learnings
- `packages/*/CLAUDE.md` - Package-specific learnings

**Secondary:**
- Git history (why changes were made)
- PR descriptions (context)
- Session logs (detailed traces)

### Compound Knowledge Loop

```
1. Session runs (sprint)
   ↓
2. Mistakes made or patterns discovered
   ↓
3. Daily review extracts learnings
   ↓
4. CLAUDE.md updated
   ↓
5. Specialist prompts reference CLAUDE.md
   ↓
6. Future sessions avoid same mistakes
   ↓
7. Fewer blockers, higher velocity
   ↓
8. Team gets "smarter" over time
```

### Knowledge Categories

| Category | Description | Example |
|----------|-------------|---------|
| **Patterns** | Reusable solutions | "Use Prisma includes for N+1 prevention" |
| **Anti-patterns** | Things to avoid | "Never create Apollo Client at module level" |
| **Architecture** | Structural decisions | "Packages must stay pure (no DB)" |
| **Security** | Security rules | "Always filter by organizationId" |
| **Performance** | Optimization techniques | "Add indexes for frequently queried fields" |
| **Workflow** | Process improvements | "Run codegen immediately after .graphql changes" |

### Measuring Knowledge Growth

```bash
# Count CLAUDE.md entries over time
git log --oneline --grep="docs.*CLAUDE.md" | wc -l
# Output: 24 (24 knowledge updates)

# Count "Common Mistakes" entries
grep "###" CLAUDE.md | grep -c "Common Mistake"
# Output: 11 (11 documented mistakes)

# Track mistake occurrences
grep "Occurrences:" CLAUDE.md
# Shows reduction over time (5 → 2 → 0)
```

---

## Complete Workflow Example

### Day 1: Morning (Product Manager)

```bash
# You create priority for today
cat > reports/priorities-2026-02-07.md <<EOF
# Priority 1

**Description:** Add employee certifications tracking

**Expected outcome:**
- Database schema for certifications
- CRUD API (GraphQL)
- UI page to manage certifications

**Files:**
- apps/dashboard-server/src/schema.prisma
- apps/dashboard/src/pages/certifications/

**Complexity:** Medium
EOF
```

### Day 1: Night (Automated)

**10:30 PM - Daily Review**
```
daily-compound-review.sh runs:
1. Scans yesterday's Claude Code sessions
2. Extracts: "BigInt conversion missed in getEmployees"
3. Updates CLAUDE.md with learning
4. Commits to main
```

**11:00 PM - Auto-Compound**
```
auto-compound.sh runs:
1. Reads priority-2026-02-07.md
2. Creates PRD with 12 tasks
3. Creates branch: feature/add-certifications
4. Calls orchestrator.sh
```

**11:01 PM - Orchestrator Planning**
```
orchestrator.sh:
1. Analyzes priority
2. Determines: Backend, Frontend, Verification needed
3. Creates session-1770451234
```

**11:02 PM - Phase 1 (Parallel)**
```
Backend specialist spawned:
- Task 1: Update schema.prisma ✅ (3 min)
- Task 2: Generate migration ✅ (2 min)
- Task 3: Add GraphQL types ✅ (4 min)
- Task 4: Implement resolvers ✅ (6 min)
- Status: Completed (15 min total)

Infrastructure specialist spawned (parallel):
- Task 1: Update docs ✅ (2 min)
- Status: Completed (2 min total)
```

**11:17 PM - Phase 2 (Frontend)**
```
Frontend specialist spawned:
- Waits for backend schema (ready at 11:17)
- Task 1: Create .graphql operations ✅ (3 min)
- Task 2: Run codegen ✅ (1 min)
- Task 3: Build UI page ✅ (8 min)
- Status: Completed (12 min total)
```

**11:29 PM - Verification**
```
Verification specialist runs:
- Type-check: ✅ Pass
- Build: ✅ Pass
- Architecture: ✅ Pass
- Security: ✅ Pass
- Status: Completed (3 min total)
```

**11:32 PM - PR Creation**
```
Orchestrator creates PR:
- Title: "feat: add employee certifications tracking"
- Body: Session summary, acceptance criteria
- Branch: feature/add-certifications → main
- PR #123 created
```

### Day 2: Morning (Product Manager Review)

```bash
# You wake up and check dashboard
open http://localhost:3030

# See completed session
# Click session-1770451234
# Review: All specialists completed, verification passed

# Check PR
gh pr list
# Output: #123 feat: add employee certifications tracking

gh pr view 123
# Review code changes

# Accept work
gh pr merge 123 --squash

# Done! Feature shipped in <1 min of your time
```

### Week Later: Compound Effect

**Same task now runs faster:**
```
Previous session (Week 1):
- Backend: 15 min
- Frontend: 12 min
- Blockers: 2 (codegen forgotten)
- Total: 35 min

Current session (Week 5):
- Backend: 12 min (learned patterns)
- Frontend: 8 min (no codegen forgotten!)
- Blockers: 0
- Total: 20 min

Improvement: 43% faster, 0 blockers
```

**Knowledge accumulated:**
- 11 documented patterns
- 3 security rules
- 5 performance optimizations
- 24 CLAUDE.md updates

**Team is "smarter":**
- Fewer mistakes
- Faster execution
- Higher quality
- Better architecture

---

## Workflow Summary

```
Priority (You write)
   ↓
Session (Auto-runs nightly)
   ↓
Tasks (Auto-breakdown)
   ↓
Implementation (Specialists)
   ↓
Verification (QA gate)
   ↓
PR (Auto-created)
   ↓
Review (You approve/reject)
   ↓
Merge (Feature shipped)
   ↓
Learnings (Extracted)
   ↓
Knowledge Base (CLAUDE.md updated)
   ↓
Future Sessions (Smarter, faster)
```

**You focus on WHAT, team figures out HOW, knowledge compounds over time!**

---

## Viewing Workflow in Dashboard

**Dashboard:** http://localhost:3030

Shows:
- All sessions (sprints)
- Current phase (planning, phase1, phase2, verification)
- Specialist statuses
- Completed tasks
- Blockers
- PR links

**Like a Kanban board:**
- Backlog: Priority files
- In Progress: Active sessions
- Review: PRs created
- Done: Merged PRs

See **ARCHITECTURE.md** for Agile/Scrum mapping!
