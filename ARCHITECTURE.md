# Multi-Agent Architecture - Agile/Scrum Methodology

## Overview

This multi-agent orchestrator system is designed as an **Agile development team** where you are the **Product Manager** and the orchestrator acts as the **Scrum Master**, coordinating specialist agents (the development team).

---

## Team Structure (Agile/Scrum)

```
┌─────────────────────────────────────────────────────────┐
│                    Product Manager                       │
│                  (You - Human User)                      │
│                                                          │
│  Responsibilities:                                       │
│  • Define priorities (product backlog)                   │
│  • Review sprint output (PRs)                            │
│  • Accept/reject work                                    │
│  • Provide feedback for future sprints                   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                   Scrum Master                           │
│              (Orchestrator Agent)                        │
│                                                          │
│  Responsibilities:                                       │
│  • Read sprint goals (priority files)                    │
│  • Create sprint plan (PRD)                              │
│  • Assign tasks to specialists                           │
│  • Coordinate parallel work                              │
│  • Remove blockers                                       │
│  • Facilitate handoffs (backend → frontend)              │
│  • Ensure Definition of Done (verification)              │
│  • Create sprint deliverable (PR)                        │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│                Development Team                          │
│              (Specialist Agents)                         │
│                                                          │
│  Backend Developer (backend-specialist)                  │
│  • Database schema design                                │
│  • API development (GraphQL)                             │
│  • Business logic                                        │
│                                                          │
│  Frontend Developer (frontend-specialist)                │
│  • UI components                                         │
│  • State management                                      │
│  • User experience                                       │
│                                                          │
│  DevOps Engineer (infrastructure-specialist)             │
│  • Package management                                    │
│  • Configuration                                         │
│  • Documentation                                         │
│                                                          │
│  QA Engineer (verification-specialist)                   │
│  • Quality gates                                         │
│  • Architecture review                                   │
│  • Security audit                                        │
│  • Performance checks                                    │
└─────────────────────────────────────────────────────────┘
```

---

## Sprint Workflow

### 1. Product Backlog (Priority Files)

**Location:** `reports/priorities-YYYY-MM-DD.md`

**You (Product Manager) create:**
```markdown
# Priority 1

**Description:** What to build (user story)

**Expected outcome:**
- Acceptance criteria 1
- Acceptance criteria 2

**Files:**
- Technical context

**Complexity:** Low | Medium | High
```

**This is equivalent to:**
- User stories in Jira/Linear
- Sprint goals
- Product requirements

---

### 2. Sprint Planning (Orchestrator)

**Trigger:** Nightly at 11 PM (or manual)

**Scrum Master (Orchestrator) does:**

1. **Read product backlog item** (priority file)
2. **Create PRD** (detailed technical spec)
3. **Create sprint branch** (`feature/xxx`)
4. **Analyze complexity** (which specialists needed)
5. **Assign tasks** to specialists
6. **Set sprint goal** (PR creation)

**Output:**
- `tasks/prd.json` - Technical breakdown
- Session state files - Sprint tracking

---

### 3. Sprint Execution (Specialists)

**Phase 1: Backend + Infrastructure (Parallel)**

```
Backend Developer:
- Sprint task: "Design schema"
- Sprint task: "Create migration"
- Sprint task: "Build API"
- Updates: Writes to session state

Infrastructure Engineer:
- Sprint task: "Update packages"
- Sprint task: "Configure build"
- Sprint task: "Update docs"
- Updates: Writes to session state

Status: Both work simultaneously (parallel sprint)
```

**Phase 2: Frontend (Sequential)**

```
Frontend Developer:
- Waits for: Backend schema ready
- Sprint task: "Create GraphQL operations"
- Sprint task: "Run codegen"
- Sprint task: "Build UI components"
- Updates: Writes to session state
```

**Phase 3: QA Review (Quality Gate)**

```
QA Engineer:
- Sprint task: "Run type-check"
- Sprint task: "Run build"
- Sprint task: "Architecture review"
- Sprint task: "Security audit"
- Decision: ✅ Pass → PR | ❌ Fail → Block
```

---

### 4. Sprint Review (Pull Request)

**Scrum Master (Orchestrator) creates:**
- Pull request with sprint deliverables
- Summary of completed work
- Links to technical details

**Product Manager (You) reviews:**
- Code changes
- Acceptance criteria met?
- Quality satisfactory?
- Decision: Merge or request changes

---

### 5. Sprint Retrospective (Learnings)

**Trigger:** Daily at 10:30 PM

**Process:**
1. **Review completed sprints** (Claude Code sessions)
2. **Extract learnings** (what worked, what didn't)
3. **Update team knowledge** (CLAUDE.md files)
4. **Improve process** (update patterns, avoid mistakes)

**This is equivalent to:**
- Daily standup notes
- Sprint retrospective
- Team knowledge base
- Continuous improvement

---

## Agile Concepts Mapped to Our System

| Agile/Scrum Concept | Our System Implementation |
|---------------------|---------------------------|
| **Product Owner** | You (human user) |
| **Scrum Master** | Orchestrator agent |
| **Development Team** | Specialist agents (backend, frontend, infra, QA) |
| **Product Backlog** | `reports/priorities-*.md` files |
| **Sprint** | One orchestrator session |
| **Sprint Planning** | Orchestrator analyzes priority, creates PRD |
| **Sprint Backlog** | Tasks in `tasks/prd.json` |
| **Daily Standup** | Specialist state updates (JSON files) |
| **Sprint Review** | Pull request created |
| **Sprint Retrospective** | Daily review at 10:30 PM (learnings extraction) |
| **Definition of Done** | Verification specialist checks pass |
| **Sprint Board** | Dashboard at http://localhost:3030 |
| **Burndown Chart** | Dashboard session progress |
| **Velocity** | Sessions completed per day/week |
| **Story Points** | Priority complexity (Low/Medium/High) |

---

## Kanban Board (Dashboard)

The dashboard at **http://localhost:3030** acts as a **Kanban board**:

### Columns (Status)

```
┌─────────┬────────────┬───────────┬──────────┬──────────┐
│ Backlog │ In Progress│ Review    │ Blocked  │ Done     │
├─────────┼────────────┼───────────┼──────────┼──────────┤
│ Priority│ Session    │ Waiting   │ Failed   │ Merged   │
│ files   │ running    │ for review│ sessions │ PRs      │
│         │            │ (PR open) │          │          │
└─────────┴────────────┴───────────┴──────────┴──────────┘
```

### Card Details (Click Session)

```
Session: session-1770451234
Status: In Progress
Phase: Frontend Development

Sprint Team:
✅ Backend Developer    - Completed
🟣 Frontend Developer   - In Progress
✅ Infrastructure Eng.  - Completed
⏳ QA Engineer         - Pending

Sprint Goal: Add employee certifications
Acceptance Criteria:
  ✅ Database schema created
  ✅ GraphQL API built
  🟣 UI components (in progress)
  ⏳ Tests passing (pending)
```

---

## Session = Sprint

### Session Structure

```
.compound-state/session-{timestamp}/
├── session.json           # Sprint metadata
├── orchestrator.json      # Scrum Master tracking
├── backend.json           # Backend dev status
├── frontend.json          # Frontend dev status
├── infrastructure.json    # DevOps status
└── verification.json      # QA status
```

### Session States

| State | Agile Equivalent | Meaning |
|-------|------------------|---------|
| `planning` | Sprint Planning | Orchestrator analyzing priority |
| `phase1_parallel` | Sprint Day 1-2 | Backend + Infra working |
| `phase2_frontend` | Sprint Day 3 | Frontend working |
| `verification` | Sprint Review Prep | QA checking quality |
| `pr_creation` | Sprint Deliverable | Creating PR |
| `completed` | Sprint Done | PR created, ready for review |
| `blocked` | Sprint Blocked | Waiting for resolution |
| `failed` | Sprint Failed | Needs PM intervention |

---

## Agent Competencies & Roles

### Orchestrator (Scrum Master)

**Competencies:**
- Sprint planning and task breakdown
- Dependency management
- Parallel work coordination
- Blocker identification and escalation
- Deliverable creation (PR)

**Authority:**
- Spawn and kill specialists
- Decide execution order
- Skip unnecessary specialists
- Block PR if quality fails

**Communication:**
- Reads: Priority files
- Writes: Session state, PRD, PR
- Coordinates: Specialist handoffs

---

### Backend Specialist (Backend Developer)

**Competencies:**
- Database schema design (Prisma)
- Migration generation
- GraphQL schema design
- Resolver implementation
- Business logic

**Authority:**
- Modify database schema
- Create migrations
- Define API contracts
- Block work if schema conflicts

**Communication:**
- Reads: Priority, existing schema
- Writes: Schema, migrations, resolvers, state
- Signals: Frontend when schema ready

**Quality Standards:**
- BigInt → Number conversion
- organizationId filtering (security)
- Pagination structure
- Max 50 lines per resolver

---

### Frontend Specialist (Frontend Developer)

**Competencies:**
- GraphQL operation design
- Type generation (codegen)
- React component development
- State management
- UI/UX implementation

**Authority:**
- Modify UI components
- Define component API
- Choose libraries (within guidelines)
- Block work if backend not ready

**Communication:**
- Reads: GraphQL schema, design specs
- Writes: Operations, components, state
- Waits for: Backend schema completion

**Quality Standards:**
- No wrapper hooks (use generated directly)
- Apollo Client in auth context
- Handle loading/error states
- Follow Tailwind patterns

---

### Infrastructure Specialist (DevOps Engineer)

**Competencies:**
- Package management (yarn workspaces)
- Configuration updates
- Documentation maintenance
- Monorepo structure enforcement

**Authority:**
- Update package.json
- Modify configs
- Update CLAUDE.md
- Enforce monorepo rules

**Communication:**
- Reads: Priority, existing configs
- Writes: Packages, configs, docs, state
- Runs in: Parallel with backend

**Quality Standards:**
- Packages stay pure (no DB, no env vars)
- Documentation in `docs/`
- Use package names (not relative paths)
- Update CLAUDE.md with learnings

---

### Verification Specialist (QA Engineer)

**Competencies:**
- Type safety validation
- Build verification
- Architecture compliance
- Security auditing
- Performance analysis

**Authority:**
- **Block PR creation** if critical issues
- Escalate to PM if unfixable
- Fail entire sprint if security breach

**Communication:**
- Reads: All specialist outputs
- Writes: Verification results, blockers
- Decides: ✅ Deploy or ❌ Block

**Quality Standards:**
- Zero type errors
- Successful build
- No security vulnerabilities
- Architecture patterns followed
- CLAUDE.md rules enforced

---

## Sprint Metrics (Dashboard)

### Velocity Tracking

```
Sessions per Week:
Mon: 1 completed
Tue: 1 completed
Wed: 1 blocked
Thu: 2 completed
Fri: 1 completed

Velocity: 5 sessions/week (1 blocked = need improvement)
```

### Success Rate

```
Total Sessions: 25
Completed: 20 (80%)
Blocked: 3 (12%)
Failed: 2 (8%)

Quality Score: 80% (target: >90%)
```

### Blocker Analysis

```
Common Blockers:
1. Type errors (5 occurrences) → Need better codegen
2. Missing organizationId (3 occurrences) → Need template
3. Build failures (2 occurrences) → Need pre-check
```

---

## Continuous Improvement (Compound Learning)

### Daily Review (10:30 PM)

**Process:**
1. Scan completed sessions (Claude Code threads)
2. Extract patterns:
   - What worked well
   - What caused blockers
   - What mistakes were made
3. Update team knowledge (CLAUDE.md)
4. Improve specialist prompts
5. Update verification rules

**Example Learning:**
```markdown
## Common Mistake #10: Apollo Client Timing

**Symptom:** All mutations fail silently
**Cause:** Apollo Client created before auth provider
**Fix:** Create client inside auth context
**Rule:** Never create clients at module level

Added: 2026-02-07
Occurrences: 3 (reduced from 5 last week)
```

---

## Communication Protocols

### State Updates (Standup)

Each specialist writes JSON state updates:

```json
{
  "agentName": "backend",
  "status": "in_progress",
  "completedTasks": [
    {"id": "backend-1", "description": "Created schema"}
  ],
  "blockers": [],
  "nextSteps": [
    {"agent": "frontend", "action": "Run codegen"}
  ]
}
```

**This is equivalent to daily standup:**
- "Yesterday I completed: schema design"
- "Today I'm working on: migrations"
- "Blockers: None"
- "Handoff needed: Frontend can now run codegen"

---

### Blocker Escalation

```json
{
  "agentName": "verification",
  "status": "blocked",
  "blockers": [
    {
      "type": "security",
      "message": "Missing organizationId filter",
      "requiresAgent": "backend",
      "requiresHuman": false
    }
  ]
}
```

**Escalation path:**
1. Specialist identifies blocker
2. Writes to state with `requiresAgent`
3. Orchestrator reads blocker
4. If `requiresHuman: true` → Escalate to PM (you)
5. If `requiresHuman: false` → Assign to specialist

---

## Product Management Workflow

### Your Daily Routine

**Morning (5 minutes):**
```bash
# 1. Check sprint board
open http://localhost:3030

# 2. Review overnight sprint deliverable
gh pr list
gh pr view [NUMBER]

# 3. Accept or reject
gh pr merge [NUMBER] --squash  # Accept
# OR provide feedback in PR comments
```

**Evening (5 minutes):**
```bash
# 4. Define tomorrow's sprint goal
cat > reports/priorities-$(date -v+1d +%Y-%m-%d).md <<EOF
# Priority 1
**Description:** Add certifications tracking
**Expected outcome:**
- Database schema for certs
- CRUD API
- UI to manage
EOF

# That's it! Team will execute overnight
```

---

## Feedback Loops

### Sprint Retrospective Insights

**Weekly review of learnings:**

```bash
# Read CLAUDE.md updates from this week
git log --since="1 week ago" --grep="docs.*CLAUDE.md"

# Review patterns:
# - What mistakes were avoided?
# - What new patterns were added?
# - How is the team improving?
```

### Velocity Improvements

**Track over time:**
```
Week 1: 3 sessions, 2 completed (66%)
Week 2: 5 sessions, 4 completed (80%)
Week 3: 5 sessions, 5 completed (100%)

Improvement: Team is learning, fewer blockers
```

---

## Advanced: Multiple Teams (Multi-Repo)

When you expand to multiple repos:

```
Team Beta-Appcaire:
- Orchestrator: beta-appcaire-scrum-master
- Specialists: 4 agents
- Sprint schedule: Nightly 11 PM

Team Cowork:
- Orchestrator: cowork-scrum-master
- Specialists: 4 agents
- Sprint schedule: Nightly 12 AM

Team Marketing:
- Orchestrator: marketing-scrum-master
- Specialists: 3 agents (no backend)
- Sprint schedule: Weekly Sundays

Dashboard shows: All teams, all sprints
```

---

## Summary: You as Product Manager

**Your role:**
1. ✅ Define sprint goals (priority files)
2. ✅ Review deliverables (PRs)
3. ✅ Accept/reject work (merge or comment)
4. ✅ Monitor team health (dashboard)
5. ✅ Improve process (update priorities based on learnings)

**Team does:**
1. ✅ Sprint planning (orchestrator)
2. ✅ Implementation (specialists)
3. ✅ Quality assurance (verification)
4. ✅ Deliverable creation (PR)
5. ✅ Continuous learning (retrospectives)

**You focus on WHAT to build, team figures out HOW.**

---

## Next: Enhanced Dashboard Features

Coming soon:
- 📊 Kanban columns (Backlog → In Progress → Review → Done)
- 📈 Velocity charts (sessions/week over time)
- 🎯 Sprint burndown (tasks completed vs remaining)
- 🐛 Blocker trends (what blocks sprints most often)
- 📚 Learning feed (CLAUDE.md updates in real-time)

---

This architecture lets you manage an autonomous development team using familiar Agile/Scrum methodology!
