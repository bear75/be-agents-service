# Multi-Agent Architecture Setup Guide

## Overview

The be-agent-service orchestrates automated development across multiple repos using a hierarchical multi-agent architecture.

## Prerequisites

- Mac Mini with macOS
- Claude Code CLI installed
- Git repositories cloned:
  - `~/HomeCare/be-agent-service` (this repo)
  - `~/HomeCare/beta-appcaire` (target repo)
  - Future: `~/HomeCare/cowork`, `~/HomeCare/marketing`, etc.
- GitHub CLI (`gh`) installed and authenticated
- Node.js, Yarn installed

## Installation

### 1. Verify Repository Structure

```bash
cd ~/HomeCare
ls -la

# Should see:
# beta-appcaire/
# be-agent-service/
```

### 2. Make Scripts Executable

```bash
cd ~/HomeCare/be-agent-service
chmod +x scripts/*.sh
chmod +x agents/*.sh
chmod +x lib/*.sh
```

### 3. Test State Manager

```bash
# Test state management
source lib/state-manager.sh

# Create test session
session_dir=$(init_session "test-$(date +%s)")
echo "Session created: $session_dir"

# Write test state
write_state "test-123" "orchestrator" '{"status": "testing"}'

# Read test state
read_state "test-123" "orchestrator"

# Clean up test
rm -rf .compound-state/test-*
```

### 4. Test Verification Specialist

```bash
cd ~/HomeCare/beta-appcaire

# Run verification (will detect current type errors)
~/HomeCare/be-agent-service/agents/verification-specialist.sh "test-$(date +%s)"

# Check logs
ls -la ~/HomeCare/be-agent-service/logs/verification-sessions/
```

## Automatic Workflow (Nightly)

### How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  10:30 PM - Daily Review (LaunchAgent)                      │
├─────────────────────────────────────────────────────────────┤
│  1. Scans Claude Code threads                               │
│  2. Extracts learnings from conversations                   │
│  3. Updates CLAUDE.md files                                 │
│  4. Commits to main                                         │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  11:00 PM - Auto-Compound (LaunchAgent)                     │
├─────────────────────────────────────────────────────────────┤
│  1. Reads latest priority from reports/                     │
│  2. Creates PRD from priority                               │
│  3. Switches to feature branch                              │
│  4. Calls orchestrator.sh ← NEW                             │
│     ├─ Orchestrator coordinates workflow                   │
│     ├─ Backend + Infrastructure (parallel)                  │
│     ├─ Frontend (after backend)                             │
│     ├─ Verification specialist                              │
│     └─ Create PR (only if verification passes)              │
│  5. Returns to main branch                                  │
└─────────────────────────────────────────────────────────────┘
                         ↓
                   GitHub PR Created
                         ↓
                  Human Review & Merge
```

### Current Implementation

**Right now (transition phase):**
```bash
auto-compound.sh
  → loop.sh (existing sequential implementation)
  → verification-specialist.sh (NEW)
  → create PR
```

**Future (Phase 3+):**
```bash
auto-compound.sh
  → orchestrator.sh (NEW)
    → backend-specialist.sh }
    → infrastructure-specialist.sh } parallel
    → frontend-specialist.sh (waits for backend)
    → verification-specialist.sh
    → create PR
```

### LaunchAgent Configuration

Check if agents are loaded:
```bash
launchctl list | grep appcaire
```

Should see:
```
- com.appcaire.auto-compound
- com.appcaire.daily-compound-review
- com.appcaire.caffeinate
```

View logs:
```bash
tail -f ~/Library/Logs/appcaire-compound.log
tail -f ~/Library/Logs/appcaire-daily-review.log
```

### Manually Trigger Nightly Run

```bash
# Trigger 10:30 PM review
launchctl start com.appcaire.daily-compound-review

# Trigger 11:00 PM auto-compound
launchctl start com.appcaire.auto-compound
```

## Manual Workflow (Development/Testing)

### Option 1: Test Orchestrator Directly

```bash
cd ~/HomeCare/be-agent-service

# Run orchestrator on beta-appcaire
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-07.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/test-multi-agent

# Check session state
ls -la .compound-state/session-*/
cat .compound-state/session-*/orchestrator.json | jq '.'

# Check session logs
ls -la logs/orchestrator-sessions/session-*/
tail logs/orchestrator-sessions/session-*/orchestrator.log
```

### Option 2: Run Auto-Compound Manually

```bash
cd ~/HomeCare/beta-appcaire

# Ensure on main branch
git checkout main
git pull origin main

# Run auto-compound (will use orchestrator in future)
../be-agent-service/scripts/auto-compound.sh
```

This will:
1. Read latest priority from `reports/priorities-*.md`
2. Create PRD
3. Create feature branch
4. Execute tasks
5. Run verification
6. Create PR

### Option 3: Test Verification Only

```bash
cd ~/HomeCare/beta-appcaire

# Ensure you have changes committed on a feature branch
git checkout -b feature/test-verification
# ... make some changes ...
git add -A
git commit -m "test: verification test"

# Run verification
~/HomeCare/be-agent-service/agents/verification-specialist.sh "manual-test-$(date +%s)"

# Check results (exit code)
echo $?  # 0 = pass, 1 = blocked, 2 = error

# View detailed feedback
cat ~/HomeCare/be-agent-service/.compound-state/manual-test-*/verification.json | jq '.'
```

### Option 4: Test State Manager

```bash
cd ~/HomeCare/be-agent-service

# Create a test session
source lib/state-manager.sh
session_id="manual-$(date +%s)"

# Initialize session
init_session "$session_id"

# Simulate backend agent
write_state "$session_id" "backend" '{
  "status": "in_progress",
  "task": "Creating schema"
}'

# Simulate frontend agent
write_state "$session_id" "frontend" '{
  "status": "pending",
  "waitingFor": "backend"
}'

# Read backend state
read_state "$session_id" "backend" | jq '.'

# List all agents in session
get_agents "$session_id"

# Clean up
rm -rf .compound-state/$session_id
```

## Working with Priorities

### Create Priority File

Priorities go in the target repo's `reports/` directory:

```bash
cd ~/HomeCare/beta-appcaire

# Create today's priority
cat > reports/priorities-$(date +%Y-%m-%d).md <<EOF
# Priority 1

**Description:** Add employee certifications tracking

**Expected outcome:**
- Database schema for certifications
- GraphQL API for CRUD operations
- UI to view/manage certifications

**Files:**
- apps/dashboard-server/src/schema.prisma
- apps/dashboard-server/src/schema.graphql
- apps/dashboard/src/pages/certifications/

**Dependencies:** None

**Estimated complexity:** Medium
EOF
```

### Priority Format

The orchestrator analyzes priority content to determine which specialists to spawn:

- **Keywords for backend:** schema, database, migration, resolver, graphql, prisma
- **Keywords for frontend:** ui, component, react, vite, page
- **Keywords for infrastructure:** package, dependency, config, documentation

Example priority that triggers all three:

```markdown
# Priority 1

**Description:** Add employee certifications with UI

Add database schema for certifications (backend),
GraphQL API (backend), and React UI components (frontend).
Also update package.json to add date-fns library (infrastructure).

**Expected outcome:**
- Database table for certifications
- GraphQL queries/mutations
- Certifications list page
- date-fns for date formatting
```

## Workflow Examples

### Example 1: Backend-Only Change

```bash
cd ~/HomeCare/beta-appcaire

# Create priority for backend change
cat > reports/priorities-2026-02-07.md <<EOF
# Priority 1
**Description:** Add database index for faster employee lookups
**Files:** apps/dashboard-server/src/schema.prisma
EOF

# Run orchestrator
cd ~/HomeCare/be-agent-service
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-07.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/add-employee-index

# Orchestrator will:
# 1. Detect: backend specialist needed
# 2. Skip: frontend (not needed)
# 3. Run: verification
# 4. Create PR
```

### Example 2: Full-Stack Feature

```bash
# Priority mentions schema, GraphQL, and UI
# Orchestrator will:
# 1. Spawn: backend + infrastructure (parallel)
# 2. Wait for backend
# 3. Spawn: frontend (after backend completes)
# 4. Run: verification
# 5. Create PR
```

### Example 3: Multi-Repo (Future)

```bash
# Work on cowork repo instead of beta-appcaire
./scripts/orchestrator.sh \
  ~/HomeCare/cowork \
  ~/HomeCare/cowork/reports/priorities.md \
  ~/HomeCare/cowork/tasks/prd.json \
  feature/new-dashboard
```

## Debugging

### Check Session State

```bash
cd ~/HomeCare/be-agent-service

# List all sessions
ls -la .compound-state/

# View orchestrator state
cat .compound-state/session-*/orchestrator.json | jq '.'

# View verification results
cat .compound-state/session-*/verification.json | jq '.blockers'
```

### Check Logs

```bash
# Orchestrator logs
tail -f logs/orchestrator-sessions/session-*/orchestrator.log

# Verification logs
tail -f logs/verification-sessions/session-*/verification.log

# Nightly automation logs (LaunchAgent)
tail -f ~/Library/Logs/appcaire-compound.log
```

### Common Issues

**Issue: "Session ID required"**
```bash
# Fix: Provide session ID
./agents/verification-specialist.sh "test-123"
```

**Issue: "Target repo not found"**
```bash
# Fix: Use absolute path
./scripts/orchestrator.sh ~/HomeCare/beta-appcaire ...
```

**Issue: "Verification blocked"**
```bash
# Check what failed
cat .compound-state/session-*/verification.json | jq '.blockers'

# Common blockers:
# - Type-check failed: Run yarn workspace @appcaire/graphql codegen
# - Build failed: Check turbo run build output
# - Security issue: Review code for hardcoded secrets
```

## Environment Variables

### be-agent-service

No environment variables required. State is managed via JSON files.

### Target Repos (beta-appcaire, etc.)

Each target repo needs:

```bash
# apps/dashboard/.env (Vite app)
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
VITE_GRAPHQL_URL=http://localhost:4000/graphql

# apps/dashboard-server/.env (Node server)
DATABASE_URL=postgresql://...
CLERK_SECRET_KEY=sk_test_...
```

## Monitoring

### Real-Time Session Monitoring

```bash
# Watch orchestrator state updates
watch -n 1 'cat ~/HomeCare/be-agent-service/.compound-state/session-*/orchestrator.json | jq ".phase, .specialists"'

# Watch verification progress
watch -n 1 'cat ~/HomeCare/be-agent-service/.compound-state/session-*/verification.json | jq ".checks"'
```

### Session Cleanup

Old sessions are automatically cleaned up after 7 days:

```bash
source lib/state-manager.sh
cleanup_sessions 7  # Remove sessions older than 7 days
```

Manual cleanup:
```bash
rm -rf .compound-state/session-*
rm -rf logs/orchestrator-sessions/session-*
```

## Next Steps

### Phase 3: Implement Specialist Agents

Create actual specialist agents to replace loop.sh:
- `agents/backend-specialist.sh`
- `agents/frontend-specialist.sh`
- `agents/infrastructure-specialist.sh`

### Phase 4: Enable Orchestrator

Update `auto-compound.sh` to use orchestrator:
```bash
# Add feature flag
USE_ORCHESTRATOR=true ./scripts/auto-compound.sh
```

### Phase 5: Multi-Repo Support

Set up orchestration for other repos:
```bash
# Cowork
./scripts/orchestrator.sh ~/HomeCare/cowork ...

# Marketing
./scripts/orchestrator.sh ~/HomeCare/marketing ...
```

## Support

- **Issues:** https://github.com/bear75/be-agent-service/issues
- **Logs:** `~/Library/Logs/appcaire-*.log`
- **State:** `~/HomeCare/be-agent-service/.compound-state/`
