# Agent Competencies & Roles

Complete reference for all agents in the multi-agent development team.

---

## Table of Contents

1. [Orchestrator (Scrum Master)](#orchestrator-scrum-master)
2. [Backend Specialist (Backend Developer)](#backend-specialist-backend-developer)
3. [Frontend Specialist (Frontend Developer)](#frontend-specialist-frontend-developer)
4. [Infrastructure Specialist (DevOps Engineer)](#infrastructure-specialist-devops-engineer)
5. [Verification Specialist (QA Engineer)](#verification-specialist-qa-engineer)
6. [DB Architect Specialist](#db-architect-specialist)
7. [UX Designer Specialist](#ux-designer-specialist)
8. [Documentation Expert](#documentation-expert)
9. [Agent Levelup (Gamification Specialist)](#agent-levelup-gamification-specialist)
10. [Future: Local LLM Specialist (Simple Tasks)](#future-local-llm-specialist-simple-tasks)

---

## Orchestrator (Scrum Master)

**Location:** `scripts/orchestrator.sh`
**Prompt:** N/A (shell script coordination)
**Model:** N/A (coordinates other agents)

### Role

Acts as **Scrum Master** - coordinates the development team, removes blockers, ensures sprint goals are met.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Sprint Planning** | Analyzes priority files, determines which specialists are needed |
| **Task Assignment** | Spawns specialists with clear scope and context |
| **Parallel Coordination** | Runs backend + infrastructure simultaneously |
| **Dependency Management** | Ensures frontend waits for backend schema completion |
| **Blocker Resolution** | Reads specialist blockers, escalates or reassigns |
| **Quality Gate** | Triggers verification before allowing PR creation |
| **Deliverable Creation** | Creates pull request with sprint summary |
| **State Tracking** | Maintains session state for all specialists |

### Competencies

- **Priority Analysis**: Parse markdown priority files to determine scope
- **Complexity Assessment**: Decide if backend, frontend, or infra needed
- **Process Management**: Spawn/wait for background processes
- **State Management**: Read/write JSON state for coordination
- **Decision Making**: Block PR if verification fails
- **Error Handling**: Capture failures, log details, escalate

### Authority Level

- ✅ **CAN**: Spawn specialists, coordinate work, block PRs, create PRs
- ❌ **CANNOT**: Modify code directly, override verification failures

### Communication

**Reads:**
- Priority files (`reports/priorities-*.md`)
- Specialist state files (`.compound-state/session-*/`)

**Writes:**
- Orchestrator state (`orchestrator.json`)
- PRD files (`tasks/prd.json`)
- Session logs (`logs/orchestrator-sessions/`)
- Pull requests (via `gh pr create`)

**Coordinates:**
- Backend ↔ Frontend handoff
- Parallel execution of Backend + Infrastructure
- Sequential execution Frontend → Verification

### Decision Tree

```
1. Read priority file
2. Analyze keywords
   → "schema|database|graphql" → Spawn Backend
   → "ui|component|react" → Spawn Frontend
   → "package|config|docs" → Spawn Infrastructure
3. Execute Phase 1: Backend + Infrastructure (parallel)
4. Wait for Phase 1 completion
5. Execute Phase 2: Frontend (if needed)
6. Wait for Phase 2 completion
7. Execute Phase 3: Verification
8. If verification passes → Create PR
9. If verification fails → Block, log blockers
```

### Metrics Tracked

- Session start/end time
- Phase transitions
- Specialist spawn times
- PR creation success/failure
- Blocker counts

---

## Backend Specialist (Backend Developer)

**Location:** `agents/backend-specialist.sh`
**Prompt:** `.claude/prompts/backend-specialist.md` (in target repo)
**Model:** Claude Sonnet 4.5 (via loop.sh currently, will be direct in Phase 4)

### Role

Acts as **Backend Developer** - designs database schemas, builds APIs, implements business logic.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Database Schema** | Design Prisma models, add fields, create relationships |
| **Migrations** | Generate and review SQL migrations |
| **GraphQL Schema** | Define types, queries, mutations, subscriptions |
| **Resolvers** | Implement GraphQL resolvers with business logic |
| **Data Validation** | Ensure proper types, constraints, validations |
| **Security** | Apply organizationId filtering, prevent SQL injection |
| **Performance** | Use includes, avoid N+1 queries, add indexes |

### Competencies

**Expert Level:**
- Prisma schema design
- PostgreSQL migrations
- GraphQL type system
- TypeScript resolver patterns
- Multi-tenant security (organizationId filtering)

**Advanced:**
- Pagination patterns (`{ records, total }`)
- BigInt → Number conversion
- Complex queries with includes/selects
- Transaction management

**Standard:**
- REST API design (if needed)
- Error handling
- Input validation

### Authority Level

- ✅ **CAN**: Modify `schema.prisma`, create migrations, edit GraphQL schema, write resolvers
- ❌ **CANNOT**: Modify frontend code, change package.json, skip migrations

### Communication

**Reads:**
- Priority file (to understand backend scope)
- Existing schema.prisma
- Existing GraphQL schema
- CLAUDE.md (backend patterns)

**Writes:**
- `apps/dashboard-server/src/schema.prisma`
- `apps/dashboard-server/prisma/migrations/`
- `apps/dashboard-server/src/schema.graphql`
- `apps/dashboard-server/src/graphql/resolvers/`
- Backend state (`backend.json`)

**Signals:**
- Frontend specialist when schema is ready
- Orchestrator when work completed
- Verification specialist if self-detected issues

### Critical Patterns (Must Follow)

1. **BigInt Conversion**
   ```typescript
   // ❌ WRONG
   return await prisma.employee.findUnique({ where: { id } });

   // ✅ CORRECT
   const employee = await prisma.employee.findUnique({ where: { id } });
   return { ...employee, id: Number(employee.id) };
   ```

2. **OrganizationId Filtering**
   ```typescript
   // ❌ WRONG (security vulnerability)
   const employees = await prisma.employee.findMany();

   // ✅ CORRECT
   const { organizationId, role } = context.auth;
   const employees = await prisma.employee.findMany({
     where: role === "SUPER_ADMIN" ? {} : { organizationId }
   });
   ```

3. **Pagination Structure**
   ```typescript
   // ❌ WRONG
   return employees;

   // ✅ CORRECT
   return {
     records: employees.map(e => ({ ...e, id: Number(e.id) })),
     total: await prisma.employee.count({ where })
   };
   ```

### Artifacts Produced

```json
{
  "exports": {
    "schemaUpdated": true,
    "migrationsCreated": ["20260207_add_certifications"],
    "resolversAdded": ["getCertifications", "createCertification"]
  }
}
```

### Quality Checks (Self)

Before marking complete:
- [ ] All BigInt fields converted to Number
- [ ] organizationId filtering present in all queries
- [ ] Pagination structure used for lists
- [ ] Migrations generated (not manual SQL)
- [ ] GraphQL schema updated if new types
- [ ] Max 50 lines per resolver function

### Handoff to Frontend

Writes to state:
```json
{
  "nextSteps": [
    {
      "agent": "frontend",
      "action": "Run codegen to generate hooks from updated schema",
      "priority": "required",
      "dependencies": ["backend-completed"]
    }
  ]
}
```

---

## Frontend Specialist (Frontend Developer)

**Location:** `agents/frontend-specialist.sh`
**Prompt:** `.claude/prompts/frontend-specialist.md` (in target repo)
**Model:** Claude Sonnet 4.5 (via loop.sh currently)

### Role

Acts as **Frontend Developer** - builds UI components, manages state, implements user experience.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **GraphQL Operations** | Create .graphql files for queries and mutations |
| **Code Generation** | Run codegen to generate TypeScript hooks |
| **UI Components** | Build React components with Tailwind styling |
| **State Management** | Use Apollo Client, handle loading/error states |
| **User Experience** | Implement responsive, accessible interfaces |
| **Integration** | Connect UI to GraphQL API |

### Competencies

**Expert Level:**
- React component design
- GraphQL operation writing
- Apollo Client usage
- TypeScript types
- Tailwind CSS patterns

**Advanced:**
- GraphQL codegen
- State management (hooks)
- Form handling and validation
- Error boundaries
- Loading states

**Standard:**
- Responsive design
- Accessibility (a11y)
- Browser compatibility

### Authority Level

- ✅ **CAN**: Create .graphql operations, run codegen, write components, modify UI
- ❌ **CANNOT**: Modify GraphQL schema, change backend resolvers, skip codegen

### Communication

**Reads:**
- Backend state (wait for schema completion)
- GraphQL schema (from backend)
- Priority file (UI requirements)
- Design specs (if provided)

**Writes:**
- `packages/graphql/operations/queries/`
- `packages/graphql/operations/mutations/`
- `packages/graphql/src/generated/` (via codegen)
- `apps/dashboard/src/pages/`
- `apps/dashboard/src/components/`
- Frontend state (`frontend.json`)

**Waits For:**
- Backend specialist schema completion
- Backend specialist resolver implementation

### Critical Patterns (Must Follow)

1. **No Wrapper Hooks**
   ```typescript
   // ❌ WRONG
   export const useCertifications = (id) => {
     return useGetCertificationsQuery({ variables: { id } });
   };

   // ✅ CORRECT (use generated hook directly)
   import { useGetCertificationsQuery } from "@appcaire/graphql";
   const { data, loading } = useGetCertificationsQuery({ variables: { id } });
   ```

2. **Apollo Client in Auth Context** (CRITICAL!)
   ```typescript
   // ❌ WRONG (causes all mutations to fail silently!)
   // lib/apollo.ts
   const apolloClient = new ApolloClient({ ... });
   export default apolloClient;

   // ✅ CORRECT
   function ApolloProviderWithAuth({ children }) {
     const { getToken } = useAuth();
     const apolloClient = useMemo(() => {
       // Create client inside auth context
     }, [getToken]);
     return <ApolloProvider client={apolloClient}>{children}</ApolloProvider>;
   }
   ```

3. **Always Run Codegen**
   ```bash
   # After creating/modifying .graphql files
   yarn workspace @appcaire/graphql codegen
   ```

### Artifacts Produced

```json
{
  "exports": {
    "codegenRun": true,
    "uiComponentsAdded": true
  }
}
```

### Quality Checks (Self)

Before marking complete:
- [ ] GraphQL operations created
- [ ] Codegen run successfully
- [ ] No wrapper hooks created
- [ ] Loading states handled
- [ ] Error states handled
- [ ] Responsive on mobile/desktop
- [ ] Apollo Client in auth context (if new app)

### Dependency on Backend

**Blocking dependency:**
```bash
# Frontend MUST wait for backend to:
1. Update GraphQL schema
2. Commit schema changes
3. Mark backend as "completed"

# Then frontend can:
1. Read new schema
2. Create operations
3. Run codegen
```

**Timeout:** 10 minutes (if backend doesn't complete)

---

## Infrastructure Specialist (DevOps Engineer)

**Location:** `agents/infrastructure-specialist.sh`
**Prompt:** `.claude/prompts/infrastructure-specialist.md` (in target repo)
**Model:** Claude Sonnet 4.5 (or Local LLM in future)

### Role

Acts as **DevOps Engineer** - manages packages, configurations, and documentation.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Package Management** | Install/update dependencies with yarn workspace |
| **Configuration** | Update TypeScript, Vite, build configs |
| **Documentation** | Maintain CLAUDE.md, README files, docs/ |
| **Monorepo Structure** | Enforce package purity, import paths |
| **Environment** | Manage .env.example templates |

### Competencies

**Expert Level:**
- Yarn workspaces
- Monorepo structure
- Turbo build system

**Advanced:**
- TypeScript configuration
- Vite build configuration
- Environment variables

**Standard:**
- Markdown documentation
- Git workflows
- File organization

### Authority Level

- ✅ **CAN**: Modify package.json, update configs, edit documentation
- ❌ **CANNOT**: Add database code to packages, add env vars to packages

### Communication

**Reads:**
- Priority file (infra needs)
- Existing configurations
- CLAUDE.md (patterns to document)

**Writes:**
- `package.json` (all workspaces)
- `yarn.lock`
- `tsconfig.json`
- `vite.config.ts`
- `CLAUDE.md`
- `docs/`
- Infrastructure state (`infrastructure.json`)

**Runs In:** Parallel with backend (no dependencies)

### Critical Patterns (Must Follow)

1. **Packages Stay Pure**
   ```typescript
   // ❌ WRONG (database in package)
   // packages/shared/db/client.ts
   import { PrismaClient } from "@prisma/client";

   // ✅ CORRECT (database only in apps)
   // apps/dashboard-server/src/db/client.ts
   import { PrismaClient } from "@prisma/client";
   ```

2. **Use Package Names**
   ```typescript
   // ❌ WRONG
   import { Button } from "../../../packages/ui/src/button";

   // ✅ CORRECT
   import { Button } from "@appcaire/ui";
   ```

3. **Docs in docs/**
   ```bash
   # ❌ WRONG
   touch README.md CONTRIBUTING.md

   # ✅ CORRECT
   touch docs/README.md docs/CONTRIBUTING.md
   ```

### Artifacts Produced

```json
{
  "exports": {
    "packagesUpdated": true,
    "configUpdated": false,
    "docsUpdated": true
  }
}
```

### Quality Checks (Self)

Before marking complete:
- [ ] No database code in packages
- [ ] No env vars in packages
- [ ] Documentation in `docs/` directory
- [ ] Correct import paths used
- [ ] CLAUDE.md updated with learnings
- [ ] Type-check still passes

### Future: Local LLM

This specialist is a **perfect candidate** for local LLM:
- Tasks are straightforward (package updates, docs)
- Lower stakes (not backend logic)
- Can be done faster locally
- Privacy for documentation

---

## Verification Specialist (QA Engineer)

**Location:** `agents/verification-specialist.sh`
**Prompt:** `.claude/prompts/verification-specialist.md` (in target repo)
**Model:** Shell script (runs checks directly)

### Role

Acts as **QA Engineer** - validates quality, security, and architecture before deployment.

### Responsibilities

| Responsibility | Description |
|----------------|-------------|
| **Type Safety** | Run `turbo run type-check`, ensure 0 errors |
| **Build Validation** | Run `turbo run build`, ensure success |
| **Architecture Review** | Check for CLAUDE.md pattern violations |
| **Security Audit** | Check for vulnerabilities, missing filters |
| **Performance** | Detect N+1 queries, missing pagination |
| **Quality Gate** | **Block PR** if critical issues found |

### Competencies

**Expert Level:**
- Static analysis
- Security pattern recognition
- Architecture compliance checking

**Advanced:**
- Build system knowledge
- TypeScript type system
- GraphQL best practices

**Standard:**
- Shell scripting
- Log parsing
- Error reporting

### Authority Level

- ✅ **CAN**: Run checks, block PRs, escalate to PM
- ✅ **CAN BLOCK**: Entire sprint if critical security issue
- ❌ **CANNOT**: Fix issues (only report), override failures

### Communication

**Reads:**
- All specialist outputs (code changes)
- CLAUDE.md (patterns to enforce)
- Previous session states

**Writes:**
- Verification state (`verification.json`)
- Blocker details with error messages
- Logs (`logs/verification-sessions/`)

**Blocks:** PR creation if critical issues

### Critical Checks

1. **Type Check** (MUST PASS)
   ```bash
   turbo run type-check
   # Exit code 0 required
   ```

2. **Build** (MUST PASS)
   ```bash
   turbo run build
   # Exit code 0 required
   ```

3. **Architecture Patterns** (MUST PASS)
   - No wrapper hooks
   - BigInt converted
   - organizationId filtering
   - Apollo Client timing

4. **Security** (MUST PASS)
   - No hardcoded secrets
   - No .env files committed
   - organizationId in all queries

### Blockers Reported

```json
{
  "blockers": [
    {
      "type": "security",
      "message": "Missing organizationId filter in getEmployees",
      "requiresAgent": "backend",
      "requiresHuman": false
    }
  ]
}
```

### Quality Checks (All Required)

- [ ] Type-check: 0 errors
- [ ] Build: Success
- [ ] No wrapper hooks found
- [ ] No Apollo Client at module level
- [ ] No hardcoded secrets
- [ ] organizationId filtering present

### Escalation Path

```
Issue Found
   ↓
Critical? (Security, Build Failure, Type Errors)
   ↓ Yes
Block PR, write blocker to state
   ↓
Can specialist fix? (requiresAgent)
   ↓ Yes
Assign back to specialist
   ↓ No
Escalate to PM (requiresHuman: true)
```

---

## DB Architect Specialist

**Location:** `agents/db-architect-specialist.sh`
**Prompt:** `.claude/prompts/db-architect-specialist.md` (in target repo, optional)
**Model:** Claude Sonnet 4.5 (via loop.sh)

### Role

Acts as **Database Architect** - database design, Prisma schema, Apollo GraphQL, PostgreSQL optimization, query performance.

### When Spawned

Keywords: schema design, database design, prisma design, migration design

### Runs In

Phase 1 parallel (with backend and infrastructure)

---

## UX Designer Specialist

**Location:** `agents/ux-designer-specialist.sh`
**Prompt:** `.claude/prompts/ux-designer-specialist.md` (in target repo, optional)
**Model:** Claude Sonnet 4.5 (via loop.sh)

### Role

Acts as **UX Designer** - modern UX 2026, responsive design, PWA, React Native, brand guidelines, accessibility, mobile-first.

### When Spawned

Keywords: ux, accessibility, responsive, design system, pwa, mobile-first

### Runs In

Phase 2b sequential (after frontend)

---

## Documentation Expert

**Location:** `agents/documentation-expert.sh`
**Prompt:** `.claude/prompts/documentation-expert.md` (in target repo, optional)
**Model:** Claude Sonnet 4.5 (via loop.sh)

### Role

Acts as **Documentation Expert** - keep docs updated, archive obsolete docs, verify with team, publish to docs page, maintain accuracy.

### When Spawned

Keywords: documentation, docs, readme, archive doc

### Runs In

Phase 1 parallel (with backend and infrastructure)

---

## Agent Levelup (Gamification Specialist)

**Location:** `agents/levelup-specialist.sh`
**Prompt:** `.claude/prompts/levelup-specialist.md` (in target repo, optional)
**Model:** Claude Sonnet 4.5 (via loop.sh)

### Role

Acts as **Gamification Expert** - XP systems, achievements, leaderboards, progression mechanics, engagement optimization.

### When Spawned

Keywords: gamification, xp, achievements, leaderboard

### Runs In

Phase 1 parallel (with backend and infrastructure)

---

## Future: Local LLM Specialist (Simple Tasks)

**Location:** TBD (agents/local-llm-specialist.sh)
**Prompt:** TBD
**Model:** Local LLM via pi-mono or ollama (CodeLlama, DeepSeek Coder)

### Role

Acts as **Assistant for Simple Tasks** - handles straightforward work using local LLM to reduce costs.

### Ideal Tasks For Local LLM

- ✅ Package updates (yarn workspace add)
- ✅ Documentation formatting
- ✅ Log summarization
- ✅ Error message parsing
- ✅ CLAUDE.md updates
- ✅ Simple config changes
- ✅ Test file generation (basic)

### NOT Suitable For Local LLM

- ❌ Database schema design
- ❌ Complex business logic
- ❌ Architecture decisions
- ❌ Security-critical code
- ❌ Complex GraphQL resolvers

### Benefits

- **Cost**: Free (local inference)
- **Speed**: No API latency (~500ms vs ~2s)
- **Privacy**: Documentation stays local
- **Availability**: Works offline

### Implementation Plan

1. Install pi-mono or ollama on Mac mini
2. Create local-llm-specialist.sh
3. Add hybrid decision to orchestrator:
   ```bash
   if [[ "$TASK_COMPLEXITY" == "low" ]]; then
     use local-llm-specialist
   else
     use infrastructure-specialist (Claude API)
   fi
   ```

---

## Agent Selection Matrix

| Task Type | Complexity | Best Agent | Model |
|-----------|------------|------------|-------|
| Database schema | High | Backend | Claude API |
| Schema design | High | DB Architect | Claude API |
| GraphQL API | High | Backend | Claude API |
| React components | High | Frontend | Claude API |
| UX/accessibility | High | UX Designer | Claude API |
| Architecture review | High | Verification | Shell script |
| Package updates | Low | Infrastructure / Local LLM | Local or API |
| Documentation | Low | Documentation Expert / Infrastructure | Claude API |
| Config updates | Medium | Infrastructure | Claude API |
| Gamification | Medium | Agent Levelup | Claude API |
| Log analysis | Low | Local LLM | Local |
| Error summarization | Low | Local LLM | Local |

---

## Summary

- **10 Current Agents**: Orchestrator, Backend, Frontend, Infrastructure, Verification, DB Architect, UX Designer, Documentation Expert, Agent Levelup, Senior Reviewer
- **1 Future Agent**: Local LLM for simple tasks
- **Clear Roles**: Like real software team (Scrum Master, Backend, Frontend, DevOps, QA, DB Architect, UX, Docs, Gamification)
- **Defined Authority**: Each knows what they can/can't do
- **Quality Standards**: Patterns enforced, blockers escalated
- **Communication Protocol**: JSON state files, structured feedback

See **ARCHITECTURE.md** for how these agents work together as an Agile team!
