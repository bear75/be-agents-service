# Engineering Commands & Guide

Complete reference for engineering team operations and commands.

---

## Table of Contents

1. [Engineering Agents](#engineering-agents)
2. [Running Jobs](#running-jobs)
3. [Common Commands](#common-commands)
4. [Verification](#verification)
5. [Debugging](#debugging)
6. [Best Practices](#best-practices)

---

## Engineering Agents

### Agent Roster

| Agent | Role | Responsibility |
|-------|------|----------------|
| **Orchestrator** | Scrum Master | Coordinates team, assigns work, creates PRs |
| **Backend** | Backend Developer | Database, GraphQL API, resolvers |
| **Frontend** | Frontend Developer | UI components, codegen, operations |
| **Infrastructure** | DevOps Engineer | Packages, configs, documentation |
| **Verification** | QA Engineer | Testing, type-check, build validation |
| **Senior Reviewer** | Senior Engineer | Code review, architecture guidance |

### Agent Workflow

```
Priority File
     ↓
Orchestrator (analyzes, creates PRD)
     ↓
  ┌──────┴──────┐
  ↓             ↓
Backend    Infrastructure  (parallel)
  ↓             ↓
  └──────┬──────┘
         ↓
     Frontend  (waits for backend schema)
         ↓
   Verification  (quality gate)
         ↓
    PR Created  OR  Blocked
```

---

## Running Jobs

### Automatic (Nightly)

Engineering jobs run automatically at **11:00 PM**:

```bash
# Configured via LaunchAgent
~/Library/LaunchAgents/com.appcaire.auto-compound.plist

# Check if running
launchctl list | grep appcaire

# View logs
tail -f ~/Library/Logs/appcaire-compound.log
```

### Manual (Dashboard)

**Go to**: http://localhost:3030/engineering.html

**Steps:**
1. Select model (Sonnet/Opus/Haiku)
2. Enter priority file: `reports/priorities-2026-02-08.md`
3. Enter branch: `feature/new-feature`
4. Click "Start Engineering Job"

**Monitor:**
- Active Jobs section shows progress
- Click "View Logs" to see agent output
- Click "Stop Job" to cancel if needed

### Manual (CLI)

```bash
cd ~/HomeCare/be-agent-service

# Run orchestrator
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-08.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/new-feature

# Or run auto-compound
cd ~/HomeCare/beta-appcaire
../be-agent-service/scripts/auto-compound.sh
```

---

## Common Commands

### Check System Status

```bash
# Check LaunchAgents
launchctl list | grep appcaire

# View orchestrator logs
tail -20 ~/Library/Logs/appcaire-compound.log

# View daily review logs
tail -20 ~/Library/Logs/appcaire-daily-review.log
```

### Session Management

```bash
cd ~/HomeCare/be-agent-service

# List all sessions
ls -la .compound-state/

# View latest orchestrator state
cat .compound-state/session-*/orchestrator.json | jq '.'

# View verification results
cat .compound-state/session-*/verification.json | jq '.blockers'

# View specific agent state
cat .compound-state/session-*/backend.json | jq '.'
cat .compound-state/session-*/frontend.json | jq '.'
```

### Log Viewing

```bash
cd ~/HomeCare/be-agent-service

# Latest orchestrator session
ls -t logs/orchestrator-sessions/ | head -1

# View orchestrator logs
tail logs/orchestrator-sessions/session-*/orchestrator.log

# View backend logs
tail logs/orchestrator-sessions/session-*/backend.log

# View frontend logs
tail logs/orchestrator-sessions/session-*/frontend.log

# View verification logs
tail logs/verification-sessions/session-*/verification.log
```

### Verification Commands

```bash
cd ~/HomeCare/beta-appcaire

# Run verification on current branch
~/HomeCare/be-agent-service/agents/verification-specialist.sh "test-$(date +%s)"

# Check result
echo $?  # 0=pass, 1=blocked, 2=error

# Run type-check manually
turbo run type-check

# Run build manually
turbo run build
```

### Git & PR Commands

```bash
# View all PRs
gh pr list

# View specific PR
gh pr view 123

# Check PR diff
gh pr diff 123

# Check PR checks
gh pr checks 123

# Merge PR
gh pr merge 123 --squash

# View recent commits
git log --oneline -10
```

---

## Verification

### What It Checks

**1. Type Check (MUST PASS)**
```bash
turbo run type-check
# Exit code 0 required
```

**2. Build (MUST PASS)**
```bash
turbo run build
# Exit code 0 required
```

**3. Architecture Patterns (MUST PASS)**
- No wrapper hooks
- BigInt converted to Number
- organizationId filtering present
- Apollo Client in auth context

**4. Security (MUST PASS)**
- No hardcoded secrets
- No .env files committed
- organizationId in all queries

### Common Verification Failures

#### Type Errors

**Symptom:**
```
Cannot find module '@appcaire/graphql' or corresponding type declarations
```

**Fix:**
```bash
cd ~/HomeCare/beta-appcaire
yarn workspace @appcaire/graphql codegen
git add -A
git commit -m "fix: run codegen"
```

#### Build Failures

**Symptom:**
```
Build failed: Cannot resolve module
```

**Fix:**
```bash
# Install missing dependencies
yarn install

# Or add specific package
yarn workspace @appcaire/dashboard add date-fns
```

#### Security Issues

**Symptom:**
```
Missing organizationId filter in getEmployees
```

**Fix:**
```typescript
// Add organizationId filter
const employees = await prisma.employee.findMany({
  where: { organizationId }
});
```

### Re-running Verification

```bash
cd ~/HomeCare/beta-appcaire

# Fix the issue
yarn workspace @appcaire/graphql codegen

# Commit fix
git add -A
git commit -m "fix: run codegen"

# Re-run verification
~/HomeCare/be-agent-service/agents/verification-specialist.sh "manual-$(date +%s)"
```

---

## Debugging

### PR Not Created?

```bash
# Check orchestrator state
cat ~/HomeCare/be-agent-service/.compound-state/session-*/orchestrator.json | jq '.status'

# If "blocked", check verification
cat ~/HomeCare/be-agent-service/.compound-state/session-*/verification.json | jq '.blockers'

# Common issues:
# - Type-check failed: Missing codegen
# - Build failed: Configuration error
# - Security issue: Hardcoded secrets
```

### Agent Stuck?

```bash
# Check agent state
cat .compound-state/session-*/backend.json | jq '.status'

# View agent logs
tail -50 logs/orchestrator-sessions/session-*/backend.log

# Check for blockers
cat .compound-state/session-*/backend.json | jq '.blockers'
```

### Wrong Branch?

```bash
# Ensure on main branch
cd ~/HomeCare/beta-appcaire
git checkout main
git pull origin main

# Check current branch
git branch --show-current
```

### Permission Errors?

```bash
# Make scripts executable
chmod +x ~/HomeCare/be-agent-service/scripts/*.sh
chmod +x ~/HomeCare/be-agent-service/agents/*.sh
```

---

## Best Practices

### Backend Agent

**Always:**
- ✅ Convert BigInt to Number in resolvers
- ✅ Add organizationId filtering to all queries
- ✅ Use pagination structure `{ records, total }`
- ✅ Generate migrations (never manual SQL)
- ✅ Run codegen after GraphQL schema changes

**Never:**
- ❌ Return raw BigInt from resolvers
- ❌ Skip organizationId filter (security issue!)
- ❌ Create wrapper hooks
- ❌ Commit without running codegen

**Example:**
```typescript
// ✅ CORRECT
const employees = await prisma.employee.findMany({
  where: role === "SUPER_ADMIN" ? {} : { organizationId }
});
return {
  records: employees.map(e => ({ ...e, id: Number(e.id) })),
  total: await prisma.employee.count({ where })
};

// ❌ WRONG
const employees = await prisma.employee.findMany();
return employees;
```

### Frontend Agent

**Always:**
- ✅ Create .graphql operations first
- ✅ Run codegen after creating operations
- ✅ Use generated hooks directly (no wrappers!)
- ✅ Handle loading and error states
- ✅ Ensure Apollo Client in auth context

**Never:**
- ❌ Create wrapper hooks around generated hooks
- ❌ Create Apollo Client at module level
- ❌ Skip codegen after .graphql changes
- ❌ Hardcode API endpoints

**Example:**
```typescript
// ✅ CORRECT
import { useGetEmployeesQuery } from "@appcaire/graphql";

const { data, loading, error } = useGetEmployeesQuery({
  variables: { organizationId }
});

// ❌ WRONG
const useEmployees = (id) => {
  return useGetEmployeesQuery({ variables: { id } });
};
```

### Infrastructure Agent

**Always:**
- ✅ Keep packages pure (no DB code)
- ✅ Use package names for imports
- ✅ Update CLAUDE.md with learnings
- ✅ Test type-check after config changes

**Never:**
- ❌ Add database code to packages
- ❌ Add env vars to packages
- ❌ Use relative paths for package imports
- ❌ Skip documentation updates

---

## Command Reference

### Daily Commands

```bash
# Check nightly automation
launchctl list | grep appcaire
tail -20 ~/Library/Logs/appcaire-compound.log

# Check session state
cat .compound-state/session-*/orchestrator.json | jq '.'

# View PRs
gh pr list

# Trigger nightly run manually
launchctl start com.appcaire.auto-compound
```

### Testing Commands

```bash
# Test orchestrator
./scripts/orchestrator.sh ~/HomeCare/beta-appcaire reports/priorities.md tasks/prd.json feature/test

# Test verification
./agents/verification-specialist.sh "test-$(date +%s)"

# Test safety mechanisms
./scripts/test-safety.sh

# Check status
./scripts/check-status.sh
```

### Cleanup Commands

```bash
# Clean old sessions
rm -rf .compound-state/session-* logs/*/session-*

# Clean old branches
git branch | grep feature/ | xargs git branch -D

# Reset to main
git checkout main
git pull origin main
git stash
```

---

## Architecture Overview

```
Orchestrator (Scrum Master)
    ↓
Analyzes priority file
    ↓
Creates PRD with tasks
    ↓
┌────────────┴────────────┐
↓                         ↓
Backend Specialist   Infrastructure Specialist
(Database, API)      (Packages, Configs)
    ↓                         ↓
Commits schema changes   Commits package updates
    ↓                         ↓
└────────────┬────────────┘
             ↓
    Frontend Specialist
    (UI, Components)
             ↓
    Runs codegen
             ↓
    Creates components
             ↓
    Verification Specialist
    (QA, Testing)
             ↓
    Type-check, Build, Security
             ↓
    ✅ Pass → PR Created
    ❌ Fail → Blocked (logs blocker)
```

---

For more details:
- [PO Workflow Guide](po-workflow.md)
- [Quick Start Guide](quick-start.md)
- [Agents Reference](../reference/agents.md)
- [Architecture](../reference/architecture.md)
