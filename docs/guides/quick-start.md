# Quick Start Guide

## TL;DR - How It Works

### Engineering Team (Automatic Nightly)

**10:30 PM** - Extracts learnings from Claude threads → Updates CLAUDE.md
**11:00 PM** - Reads priority #1 → Implements → Creates PR

No action required! Just create priority files and review PRs in the morning.

### Marketing Team (Manual On-Demand)

Run Jarvis orchestrator with marketing priority → Specialists execute → PR created

**Agents**: Jarvis (Squad Lead), Vision (SEO), Shuri (Product), Fury (Customer Research), Loki (Content), Quill (Social), Wanda (Design), Pepper (Email), Friday (Dev), Wong (Notion)

### Manual (Testing/Development)

```bash
cd ~/HomeCare/be-agent-service

# Test orchestrator
./scripts/orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/priorities-2026-02-07.md \
  ~/HomeCare/beta-appcaire/tasks/prd.json \
  feature/test-branch

# Or run full auto-compound
cd ~/HomeCare/beta-appcaire
../be-agent-service/scripts/auto-compound.sh
```

## Daily Workflow

### 1. Create Priority (Morning)

```bash
cd ~/HomeCare/beta-appcaire

cat > reports/priorities-$(date +%Y-%m-%d).md <<EOF
# Priority 1

**Description:** [What to build]

**Expected outcome:**
- [Specific deliverable 1]
- [Specific deliverable 2]

**Files:**
- [File paths that need changes]
EOF
```

### 2. System Runs Automatically (Night)

- 10:30 PM: Reviews Claude sessions
- 11:00 PM: Implements priority #1
- Creates PR automatically

### 3. Review PR (Next Morning)

```bash
# View PRs
gh pr list

# Review specific PR
gh pr view 123

# Merge if good
gh pr merge 123 --squash
```

## Common Commands

### Check Nightly Automation

```bash
# See if LaunchAgents are running
launchctl list | grep appcaire

# View recent logs
tail -20 ~/Library/Logs/appcaire-compound.log
tail -20 ~/Library/Logs/appcaire-daily-review.log

# Manually trigger tonight's run
launchctl start com.appcaire.auto-compound
```

### Test Verification

```bash
cd ~/HomeCare/beta-appcaire

# Run verification on current branch
~/HomeCare/be-agent-service/agents/verification-specialist.sh "test-$(date +%s)"

# Check result
echo $?  # 0=pass, 1=blocked, 2=error
```

### Check Session State

```bash
cd ~/HomeCare/be-agent-service

# List sessions
ls -la .compound-state/

# View latest orchestrator state
cat .compound-state/session-*/orchestrator.json | jq '.'

# View latest verification results
cat .compound-state/session-*/verification.json | jq '.blockers'
```

### View Logs

```bash
cd ~/HomeCare/be-agent-service

# Latest orchestrator session
ls -t logs/orchestrator-sessions/ | head -1
tail logs/orchestrator-sessions/session-*/orchestrator.log

# Latest verification session
tail logs/verification-sessions/session-*/verification.log
```

## Workflow Examples

### Example 1: Simple Backend Change

**Priority:**
```markdown
# Priority 1
**Description:** Add index to employees table for faster lookups
**Files:** apps/dashboard-server/src/schema.prisma
```

**What happens:**
1. 11:00 PM: Orchestrator reads priority
2. Detects: Backend work (schema keyword)
3. Runs: Backend specialist → Verification → PR

**Morning:** Review PR with database migration

---

### Example 2: Full-Stack Feature

**Priority:**
```markdown
# Priority 1
**Description:** Add employee certifications tracking with UI
**Expected outcome:**
- Database schema for certifications (backend)
- GraphQL API (backend)
- Certifications page (frontend)
```

**What happens:**
1. 11:00 PM: Orchestrator reads priority
2. Detects: Backend + Frontend work
3. Runs: Backend specialist (parallel with infrastructure)
4. Waits: For backend to commit schema
5. Runs: Frontend specialist (uses backend schema)
6. Runs: Verification → PR

**Morning:** Review PR with full-stack changes

---

### Example 3: Package Update

**Priority:**
```markdown
# Priority 1
**Description:** Update React to v19
**Files:** package.json
```

**What happens:**
1. 11:00 PM: Orchestrator reads priority
2. Detects: Infrastructure work (package keyword)
3. Runs: Infrastructure specialist → Verification → PR

**Morning:** Review PR with dependency updates

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

### Fix and Re-run

```bash
cd ~/HomeCare/beta-appcaire

# Fix the issue (e.g., run codegen)
yarn workspace @appcaire/graphql codegen

# Commit fix
git add -A
git commit -m "fix: run codegen"

# Re-run verification
~/HomeCare/be-agent-service/agents/verification-specialist.sh "manual-$(date +%s)"
```

## Marketing Agents (Manual)

### Run Marketing Campaign

```bash
# 1. Create marketing priority
cat > ~/HomeCare/beta-appcaire/reports/marketing-blog-$(date +%Y-%m-%d).md <<'EOF'
# Priority: SEO Blog Post

**Description:** Create blog post about employee scheduling

**Expected outcome:**
- Keyword research (target keywords with volume/difficulty)
- Product positioning analysis
- Customer pain points identified
- Blog post written (1500+ words, SEO-optimized)
- Header image created
- Published to website
- Promoted on social media

**Complexity:** Medium
EOF

# 2. Run Jarvis marketing orchestrator
cd ~/HomeCare/be-agent-service
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-blog-$(date +%Y-%m-%d).md \
  ~/HomeCare/beta-appcaire/tasks/marketing-prd.json \
  feature/blog-scheduling-$(date +%Y%m%d)

# 3. Monitor in dashboard
open http://localhost:3030

# 4. Review PR when done
gh pr list
gh pr view [NUMBER]
gh pr merge [NUMBER] --squash
```

### Run Individual Marketing Agent

```bash
# SEO analysis only
cd ~/HomeCare/be-agent-service
./agents/marketing/vision-seo-analyst.sh \
  "session-seo-$(date +%s)" \
  ~/HomeCare/beta-appcaire \
  ~/HomeCare/beta-appcaire/reports/marketing-priority.md

# View results
cat .compound-state/session-seo-*/vision.json | jq '.deliverables'
```

## Multi-Repo Usage (Future)

Work on other repos besides beta-appcaire:

```bash
cd ~/HomeCare/be-agent-service

# Cowork repo
./scripts/orchestrator.sh \
  ~/HomeCare/cowork \
  ~/HomeCare/cowork/reports/priorities.md \
  ~/HomeCare/cowork/tasks/prd.json \
  feature/dashboard-update

# Marketing repo (engineering agents)
./scripts/orchestrator.sh \
  ~/HomeCare/marketing \
  ~/HomeCare/marketing/reports/priorities.md \
  ~/HomeCare/marketing/tasks/prd.json \
  feature/landing-redesign

# Marketing repo (marketing agents)
./agents/marketing/jarvis-orchestrator.sh \
  ~/HomeCare/marketing \
  ~/HomeCare/marketing/reports/content-priorities.md \
  ~/HomeCare/marketing/tasks/marketing-prd.json \
  feature/blog-campaign
```

## Architecture At-a-Glance

```
Priority File (reports/priorities-*.md)
         ↓
   Orchestrator (scripts/orchestrator.sh) - keyword detection
         ↓
   Phase 1 (parallel): Backend, Infra, DB Architect, Docs Expert, Levelup
         ↓
   Phase 2: Frontend (waits for backend)
         ↓
   Phase 2b: UX Designer (when UX keywords detected)
         ↓
   Verification (quality gate)
         ↓
  ✅ PR Created  OR  ❌ Blocked
```

## Status & Phases

**✅ Completed (Phase 1-2):**
- State management
- Verification specialist
- Orchestrator coordinator
- Multi-repo support

**🚧 In Progress (Phase 3):**
- Backend specialist agent
- Frontend specialist agent
- Infrastructure specialist agent

**📋 Planned (Phase 4-5):**
- Integrate orchestrator with auto-compound
- Enable parallel specialist execution
- Dynamic replanning

## Getting Help

**Check logs first:**
```bash
tail -50 ~/Library/Logs/appcaire-compound.log
```

**View session details:**
```bash
cat ~/HomeCare/be-agent-service/.compound-state/session-*/orchestrator.json | jq '.'
```

**Manual debugging:**
```bash
# Run auto-compound with verbose output
cd ~/HomeCare/beta-appcaire
../be-agent-service/scripts/auto-compound.sh 2>&1 | tee debug.log
```

## Dashboard Command Center

**All commands and documentation in one place!**

```bash
# Open dashboard
open http://localhost:3030

# Navigate to Commands & Docs page
open http://localhost:3030/commands.html
```

**Features:**
- **Product Owner Guide** - How to start projects with your Scrum agent team
- **Engineering Commands** - All engineering agent commands with copy buttons
- **Marketing Commands** - All marketing agent commands with copy buttons
- **All Agents** - Complete list of engineering + marketing agents with roles
- **Documentation** - Links to all docs (Architecture, Workflow, Agents, etc.)

## Quick Cheat Sheet

| Task | Command |
|------|---------|
| **Dashboard** | `open http://localhost:3030` |
| **Commands & Docs** | `open http://localhost:3030/commands.html` |
| Create priority | `vim ~/HomeCare/beta-appcaire/reports/priorities-$(date +%Y-%m-%d).md` |
| Test orchestrator | `./scripts/orchestrator.sh ~/HomeCare/beta-appcaire ...` |
| Run marketing | `./agents/marketing/jarvis-orchestrator.sh ...` |
| Run verification | `./agents/verification-specialist.sh "test-$(date +%s)"` |
| Check session state | `cat .compound-state/session-*/orchestrator.json \| jq '.'` |
| View logs | `tail logs/orchestrator-sessions/session-*/orchestrator.log` |
| Trigger nightly run | `launchctl start com.appcaire.auto-compound` |
| View PRs | `gh pr list` |
| Clean old sessions | `rm -rf .compound-state/session-* logs/*/session-*` |
