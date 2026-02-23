# Product Owner Workflow Guide

Complete guide for Product Owners working with the multi-agent development team.

---

## Table of Contents

1. [Overview](#overview)
2. [Daily Workflow](#daily-workflow)
3. [Creating Priority Files](#creating-priority-files)
4. [Starting Jobs](#starting-jobs)
5. [Monitoring Progress](#monitoring-progress)
6. [Reviewing PRs](#reviewing-prs)
7. [Best Practices](#best-practices)

---

## Overview

As a Product Owner, you work with **two specialized agent teams**:

### Engineering Team (Automatic Nightly)
- **10:30 PM**: Reviews Claude Code threads, updates CLAUDE.md
- **11:00 PM**: Auto-implements priority #1, creates PR
- **Agents**: Orchestrator, Backend, Frontend, Infrastructure, Verification, Senior Reviewer

### Marketing Team (Manual/On-Demand)
- **Run**: Manual trigger via dashboard or CLI
- **Agents**: Jarvis (Squad Lead), 9 specialist agents
- **Use cases**: Campaigns, content, SEO, social media

---

## Daily Workflow

### Morning Routine (5 minutes)

**1. Check Dashboard**
```bash
open http://localhost:3030
```

**2. Review Overnight Work**
- Check Engineering page for completed sessions
- Review any PRs created by agents
- Check for blockers or failures

**3. Review PRs**
```bash
# List all PRs
gh pr list

# Review specific PR
gh pr view 123

# Merge if approved
gh pr merge 123 --squash
```

### Afternoon Tasks (10-15 minutes)

**1. Create Tomorrow's Priority**
```bash
cd ~/HomeCare/beta-appcaire

# Create priority file for tomorrow
vim reports/priorities-$(date -v+1d +%Y-%m-%d).md
```

**2. Optional: Start Marketing Campaign**
- Go to Sales & Marketing page
- Enter campaign file and branch
- Click "Start Marketing Campaign"

---

## Creating Priority Files

### Location
```
~/HomeCare/beta-appcaire/reports/priorities-YYYY-MM-DD.md
```

### Format

```markdown
# Priority 1

**Description:** [Clear description of what to build]

**Expected outcome:**
- [Specific deliverable 1]
- [Specific deliverable 2]
- [Specific deliverable 3]

**Files:**
- [Relevant file paths for context]

**Dependencies:** [Other priorities this depends on]

**Complexity:** Low | Medium | High
```

### Examples

#### Example 1: Backend Only
```markdown
# Priority 1

**Description:** Add index to employees table for faster lookups

**Expected outcome:**
- Database migration created
- Index added to employeeId field
- Query performance improved

**Files:**
- apps/dashboard-server/src/schema.prisma

**Complexity:** Low
```

#### Example 2: Full-Stack Feature
```markdown
# Priority 1

**Description:** Add employee certifications tracking system

**Expected outcome:**
- Database schema for certifications with expiry dates
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

#### Example 3: Infrastructure
```markdown
# Priority 1

**Description:** Update React to v19

**Expected outcome:**
- All packages updated to React 19
- Type definitions updated
- Build successful
- No breaking changes

**Files:**
- package.json (all workspaces)

**Complexity:** Low
```

### Tips for Good Priorities

**Do:**
- ✅ Be specific about what you want
- ✅ Include clear acceptance criteria
- ✅ Mention relevant files for context
- ✅ Set realistic complexity estimate
- ✅ One feature per priority file

**Don't:**
- ❌ Be vague ("Improve dashboard")
- ❌ Combine multiple unrelated features
- ❌ Forget acceptance criteria
- ❌ Skip complexity estimate

---

## Starting Jobs

### Automatic (Engineering Team)

Engineering jobs run automatically at **11:00 PM** nightly:
1. Reads `priorities-YYYY-MM-DD.md` for today's date
2. Implements Priority #1
3. Creates PR

**No action required!** Just create priority files.

### Manual (Engineering Team)

To run engineering job immediately:

1. **Go to Engineering page**: http://localhost:3030/engineering.html
2. **Select model**: Sonnet (balanced) / Opus (best) / Haiku (fast)
3. **Enter priority file**: `reports/priorities-2026-02-08.md`
4. **Enter branch**: `feature/new-feature`
5. **Click**: "Start Engineering Job"

### Manual (Marketing Team)

To run marketing campaign:

1. **Go to Sales & Marketing page**: http://localhost:3030/sales-marketing.html
2. **Select model**: Usually Sonnet (cost-effective)
3. **Enter campaign file**: `reports/marketing-campaign-Q1.md`
4. **Enter branch**: `feature/q1-campaign`
5. **Describe objectives** (optional)
6. **Click**: "Start Marketing Campaign"

---

## Monitoring Progress

### Dashboard

**Main dashboard**: http://localhost:3030

**Features:**
- Real-time session status (3s refresh)
- Agent progress indicators
- Active jobs list
- Recent PRs
- System statistics

### Engineering Page

http://localhost:3030/engineering.html

**Shows:**
- 6 engineering agents with status
- Active jobs with logs
- Start/stop controls
- Recent sessions

### Sales & Marketing Page

http://localhost:3030/sales-marketing.html

**Shows:**
- 10 marketing agents with status
- Active campaigns
- Recent leads
- Social posts
- Campaign performance

### RL Dashboard

http://localhost:3030/rl-dashboard.html

**Shows:**
- Agent performance metrics
- Success/failure patterns
- Automation opportunities
- Cost tracking

---

## Reviewing PRs

### Check PR Quality

```bash
# View PR details
gh pr view 123

# Check changed files
gh pr diff 123

# View checks status
gh pr checks 123
```

### Review Checklist

Before merging:
- [ ] PR description is clear
- [ ] All tests passed
- [ ] Type-check passed
- [ ] Build successful
- [ ] No security issues
- [ ] Meets acceptance criteria from priority file

### Merge PR

```bash
# Squash merge (recommended)
gh pr merge 123 --squash

# Or merge via dashboard
# Click "Merge pull request" button
```

### Handle Blocked PRs

If verification failed:

```bash
# Check verification logs
cat ~/HomeCare/be-agents-service/.compound-state/session-*/verification.json | jq '.blockers'

# Common issues:
# - Type errors: Run codegen
# - Build failure: Check dependencies
# - Security: Missing organizationId filter
```

---

## Best Practices

### Priority File Management

**Naming convention:**
```
priorities-YYYY-MM-DD.md  # Daily engineering priorities
marketing-campaign-Q1.md  # Marketing campaigns
```

**Organization:**
```
reports/
├── priorities-2026-02-08.md  # Today's engineering work
├── priorities-2026-02-09.md  # Tomorrow's engineering work
├── marketing-blog-post.md    # Marketing: blog post
├── marketing-q1-campaign.md  # Marketing: Q1 campaign
└── archive/
    └── 2025/                 # Archive old priorities
```

### Communication with Agents

**In priority files, be clear:**
```markdown
# Good
**Description:** Add pagination to employees list with 50 items per page

# Bad
**Description:** Make employees list better
```

**Provide context:**
```markdown
**Files:**
- apps/dashboard/src/pages/employees/index.tsx  # Main list component
- apps/dashboard-server/src/graphql/resolvers/employees.ts  # Backend resolver
```

### Scheduling Work

**Engineering (Automatic):**
- Create priority files in advance
- One priority per day
- Agents work at 11:00 PM
- Review PRs next morning

**Marketing (Manual):**
- Create campaign files as needed
- Run via dashboard when ready
- Monitor progress in real-time
- Review deliverables when complete

### Handling Failures

**If job fails:**
1. Check logs in dashboard
2. Review blocker messages
3. Fix issue manually or update priority
4. Re-run if needed

**If PR blocked:**
1. Review verification.json for details
2. Fix blockers (usually codegen, types)
3. Commit fixes
4. Re-run verification

**If confused:**
```bash
# Check session state
cat .compound-state/session-*/orchestrator.json | jq '.'

# View logs
tail -50 ~/Library/Logs/appcaire-compound.log
```

---

## Quick Reference

### Essential Commands

| Task | Command |
|------|---------|
| **Dashboard** | `open http://localhost:3030` |
| **Create priority** | `vim ~/HomeCare/beta-appcaire/reports/priorities-$(date +%Y-%m-%d).md` |
| **Check PRs** | `gh pr list` |
| **Review PR** | `gh pr view 123` |
| **Merge PR** | `gh pr merge 123 --squash` |
| **Check sessions** | `ls -la ~/HomeCare/be-agents-service/.compound-state/` |
| **View logs** | `tail -50 ~/Library/Logs/appcaire-compound.log` |
| **Trigger nightly** | `launchctl start com.appcaire.auto-compound` |

### Dashboard Pages

| Page | URL | Purpose |
|------|-----|---------|
| **Management** | `/management-team.html` | CEO dashboard, upload tasks, hire/fire agents |
| **Engineering** | `/engineering.html` | 6 engineering agents, start jobs |
| **Sales & Marketing** | `/sales-marketing.html` | 10 marketing agents, campaigns |
| **RL Dashboard** | `/rl-dashboard.html` | Performance metrics, automation |
| **Task Board** | `/kanban.html` | Kanban view of tasks |
| **Docs & Commands** | `/commands.html` | All commands and documentation |

---

## Workflow Summary

```
Morning (5 min)
  ↓
Check Dashboard → Review PRs → Merge if good
  ↓
Afternoon (10 min)
  ↓
Create Tomorrow's Priority → Optional: Start Marketing
  ↓
Evening (Automatic)
  ↓
Agents Work → PR Created
  ↓
Next Morning
  ↓
Review → Merge → Repeat
```

**Your time investment: ~15 minutes/day**
**Agent output: Full-stack features, working code, PRs ready to merge**

---

For technical details, see:
- [Quick Start Guide](quick-start.md)
- [Engineering Guide](engineering-guide.md)
- [Marketing Guide](marketing-guide.md)
- [Agents Reference](../reference/agents.md)
