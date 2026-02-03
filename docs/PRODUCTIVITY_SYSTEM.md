# AppCaire Productivity System - User Guide

Complete guide to using Boris's 10 Claude Code Techniques implementation.

---

## Quick Start

### For New Claude Code Sessions

```bash
# 5-minute onboarding
./scripts/onboard-claude.sh
```

This will guide you through essential documentation and get you productive immediately.

---

## 📚 Documentation Index

### Essential Reading (Start Here)

| File                                    | Purpose            | Read Time | When to Read                   |
| --------------------------------------- | ------------------ | --------- | ------------------------------ |
| **docs/learning/01-monorepo-basics.md** | 5-min overview     | 5 min     | First thing, every new session |
| **/CLAUDE.md**                          | Complete learnings | 15 min    | Before any work                |
| **docs/ARCHITECT_PROMPT.md**            | Full architecture  | 30 min    | First session only             |
| **This file**                           | How to use system  | 10 min    | You are here!                  |

### Reference Documentation

| Category     | File                                            | What's Inside               |
| ------------ | ----------------------------------------------- | --------------------------- |
| **Skills**   | `.claude/skills/README.md`                      | Available skills index      |
|              | `.claude/skills/monorepo/graphql-full-stack.md` | Complete GraphQL workflow   |
|              | `.claude/skills/monorepo/database-migration.md` | Safe Prisma migrations      |
|              | `.claude/skills/compound/extract-learnings.md`  | Update CLAUDE.md files      |
| **Prompts**  | `.claude/prompts/subagents.md`                  | Parallel execution patterns |
|              | `.claude/prompts/architecture.md`               | Architecture-aware prompts  |
|              | `.claude/prompts/optimization.md`               | Performance optimization    |
|              | `.claude/prompts/testing.md`                    | Testing strategies          |
| **Planning** | `.claude/plans/templates/feature-plan.md`       | Feature planning template   |
|              | `.claude/plans/templates/README.md`             | Planning guide              |
| **Learning** | `docs/learning/README.md`                       | Complete learning path      |
| **Hooks**    | `.claude/hooks/README.md`                       | Pre-commit validation       |

### App-Specific Documentation

| App/Package        | File                               | What's Inside                         |
| ------------------ | ---------------------------------- | ------------------------------------- |
| Dashboard Frontend | `/apps/dashboard/CLAUDE.md`        | React, Vite, Bryntum, Apollo patterns |
| Dashboard Backend  | `/apps/dashboard-server/CLAUDE.md` | GraphQL resolvers, Prisma, auth       |
| GraphQL Package    | `/packages/graphql/CLAUDE.md`      | Codegen workflow, operations          |
| UI Package         | `/packages/ui/CLAUDE.md`           | UI component patterns                 |
| Shared Package     | `/packages/shared/CLAUDE.md`       | Shared utilities patterns             |
| Scripts            | `/scripts/CLAUDE.md`               | Automation and compound workflow      |

---

## 🔧 Manual Usage

### 1. Using Skills

Skills encode best practices for common workflows.

**Available Skills:**

```bash
# GraphQL full-stack feature (database → API → frontend)
claude -p "Use the monorepo/graphql-full-stack skill to add employee certifications feature"

# Safe database migration
claude -p "Use the monorepo/database-migration skill to add phone field to Employee"

# Extract learnings after work
claude -p "Use the compound/extract-learnings skill to document what I learned about Bryntum integration"
```

**How it works:**

- Just mention the skill in your prompt
- Claude reads the skill file
- Follows step-by-step workflow
- Ensures best practices

**Skill files location:** `.claude/skills/`

### 2. Using Prompts

Prompts provide professional templates for specific scenarios.

**Architecture-aware prompts:**

```bash
# Feature design following architecture
claude -p "Read .claude/prompts/architecture.md and design the visit notes feature"

# Multi-app feature
claude -p "Use .claude/prompts/architecture.md Multi-App Feature pattern for updating all SEO sites"
```

**Optimization prompts:**

```bash
# Database optimization
claude -p "Use .claude/prompts/optimization.md to fix N+1 queries in employee resolver"

# Frontend performance
claude -p "Use .claude/prompts/optimization.md to optimize bundle size"
```

**Testing prompts:**

```bash
# Create comprehensive tests
claude -p "Use .claude/prompts/testing.md to create unit tests for getEmployee resolver"
```

**Prompt files location:** `.claude/prompts/`

### 3. Using Subagents for Parallel Work

For complex tasks that can be parallelized:

**Parallel feature development:**

```bash
claude -p "Use .claude/prompts/subagents.md Parallel Development pattern to implement employee certifications:

Subagent 1 (Backend): Database + GraphQL API
Subagent 2 (Frontend): UI components
Subagent 3 (Testing): Unit + integration tests"
```

**Multi-app updates:**

```bash
claude -p "Use .claude/prompts/subagents.md Multi-App pattern to add new field across all 4 SEO sites"
```

**Code review:**

```bash
claude -p "Use .claude/prompts/subagents.md Review Swarm pattern to review PR #123"
```

**Time savings:** 40-80% faster depending on task complexity

### 4. Using Worktrees for Parallel Sessions

Work on multiple features simultaneously without conflicts.

**Create worktree:**

```bash
./scripts/worktree-setup.sh feature add-certifications
# Creates ~/HomeCare/beta-appcaire-feature
# Installs dependencies
# Ready to use

cd ~/HomeCare/beta-appcaire-feature
claude
# Work independently from main worktree
```

**Open parallel sessions:**

```bash
# Full-stack parallel development (3 sessions)
./scripts/sessions/dashboard-stack.sh

# Opens 3 worktrees:
# - frontend (dashboard UI work)
# - backend (API work)
# - testing (test work)
```

**Cleanup when done:**

```bash
./scripts/worktree-cleanup.sh feature add-certifications
# Safely removes worktree
# Optionally deletes branch
```

### 5. Planning Features

Use templates for detailed planning before implementation.

**Create plan:**

```bash
claude -p "Use .claude/plans/templates/feature-plan.md to plan employee certifications feature"

# Creates comprehensive plan:
# - Architecture analysis
# - Affected components
# - Implementation phases
# - File checklist
# - Risk mitigation
```

**Review and approve plan, then implement:**

```bash
claude -p "Implement the plan in .claude/plans/employee-certifications-plan.md"
```

**Benefits:**

- Thorough planning → 1-shot implementations
- Catch issues early
- Clear file checklist
- Risk mitigation upfront

### 6. Monitoring CI

Automatically fix CI failures when possible.

**Manual check:**

```bash
./scripts/ci-monitor.sh

# Checks latest GitHub Actions run
# If failure detected:
#   - Classifies type (TypeScript, lint, test, codegen)
#   - Attempts auto-fix for simple issues
#   - Creates GitHub issue for complex issues
```

**What gets auto-fixed:**

- TypeScript errors (missing codegen, type issues)
- Lint errors (formatting)
- Missing codegen (forgot to run)
- Simple test failures

**What creates issues:**

- Integration failures
- Complex logic errors
- Build configuration issues

---

## 🤖 Automatic Usage (Compound Workflow)

The system runs automatically every night to compound learnings and implement priorities.

### Nightly Schedule

**10:30 PM - Daily Compound Review**

```bash
# Automatically runs: scripts/compound/daily-compound-review.sh

What it does:
1. Reviews all Claude Code threads from last 24 hours
2. Extracts key learnings from each thread
3. Updates relevant CLAUDE.md files
4. Updates timestamps automatically
5. Commits learnings to main branch
```

**11:00 PM - Auto Implementation**

```bash
# Automatically runs: scripts/compound/auto-compound.sh

What it does:
1. Reads reports/priorities-YYYY-MM-DD.md
2. Picks priority #1
3. Creates feature branch
4. Uses appropriate skill (graphql-full-stack, etc.)
5. Implements the feature
6. Creates PR (NOT direct to main)
7. You review in the morning
```

### How CLAUDE.md Auto-Updates

**During daily review (10:30 PM):**

1. **Extract learnings:**
   - Script runs: `claude -p "Use compound/extract-learnings skill..."`
   - Claude reviews threads from last 24h
   - Extracts mistakes, patterns, gotchas
   - Updates relevant CLAUDE.md files

2. **Update timestamps:**
   - Script runs: `./scripts/update-claude-md.sh` on changed files
   - Updates "Last updated: YYYY-MM-DD"
   - Increments "Times updated: N"

3. **Commit:**
   - All CLAUDE.md changes committed
   - Pushed to main
   - Knowledge preserved

**Example commit:**

```
docs: daily compound review - learnings update

Updated CLAUDE.md files:
- /CLAUDE.md - Added GraphQL codegen gotcha
- /apps/dashboard/CLAUDE.md - Added Bryntum integration pattern
- /packages/graphql/CLAUDE.md - Clarified operation naming

Learnings:
- Always run codegen after .graphql changes
- Bryntum requires specific data format
- Operation names should be descriptive
```

### How Auto-Implementation Works

**When you update priorities:**

```bash
# Edit priorities file
vim reports/priorities-$(date +%Y-%m-%d).md

# Put most important task at #1:
1. Add employee certifications feature

# Commit
git add reports/
git commit -m "docs: update priorities"
git push origin main
```

**That night at 11:00 PM:**

1. **Read priority #1:**
   - Script reads `reports/priorities-YYYY-MM-DD.md`
   - Extracts priority #1: "Add employee certifications feature"

2. **Create plan** (if complex):
   - Uses `.claude/plans/templates/feature-plan.md`
   - Creates comprehensive plan
   - Analyzes architecture impact

3. **Create branch:**
   - Creates: `feature/priority-{date}-certifications`

4. **Implement using skills:**
   - For GraphQL features: Uses `monorepo/graphql-full-stack` skill
   - For migrations: Uses `monorepo/database-migration` skill
   - For updates: Uses appropriate skill

5. **Create PR:**
   - Commits all changes
   - Creates PR with detailed description
   - Links to priority report
   - Ready for morning review

**Morning routine:**

```bash
# Check what was implemented
gh pr list

# Review the PR
gh pr view [number]

# If good, merge
gh pr merge [number]

# If needs changes, add comments
gh pr comment [number] --body "Please fix..."
```

### Integration with Skills

**Auto-implementation uses skills automatically:**

```bash
# In scripts/compound/loop.sh

# Detects GraphQL feature
if [task needs database + API + UI]; then
  claude -p "Use monorepo/graphql-full-stack skill to implement..."
fi

# Detects migration
if [task needs database changes]; then
  claude -p "Use monorepo/database-migration skill to implement..."
fi

# Detects multi-app update
if [task affects multiple SEO sites]; then
  claude -p "Use subagents Multi-App pattern to implement..."
fi
```

**Result:**

- Consistent implementations
- Best practices followed
- Architecture compliance
- Complete features

---

## 📊 Monitoring the System

### Check CLAUDE.md Update History

```bash
# See when CLAUDE.md files were last updated
find . -name "CLAUDE.md" -exec grep "Last updated:" {} \; -print

# See how many times updated
find . -name "CLAUDE.md" -exec grep "Times updated:" {} \; -print

# See recent CLAUDE.md changes
git log --all --oneline --grep="CLAUDE.md"
```

### Check Compound Workflow Logs

```bash
# Daily review logs
tail -f logs/daily-review.log

# Auto-implementation logs
tail -f logs/auto-compound.log

# CI monitor logs
tail -f logs/ci-monitor.log
```

### Check Auto-Implemented PRs

```bash
# List recent PRs from compound workflow
gh pr list --author "app/github-actions"

# Or PRs with "compound" label
gh pr list --label "compound-workflow"
```

### LaunchAgent Status

```bash
# Check if scheduled jobs are running
launchctl list | grep appcaire

# View specific job status
launchctl list com.appcaire.daily-compound-review
launchctl list com.appcaire.auto-compound
```

---

## 🎯 Recommended Workflow

### Daily Routine

**Morning (9:00 AM):**

```bash
# 1. Check auto-implemented PR
gh pr list

# 2. Review and merge (or request changes)
gh pr view [number]
gh pr merge [number]

# 3. Pull latest
git checkout main
git pull origin main
```

**During Work:**

```bash
# For new session - quick onboarding
./scripts/onboard-claude.sh

# For complex features - use skills
claude -p "Use graphql-full-stack skill to add [feature]"

# For parallel work - use worktrees
./scripts/sessions/dashboard-stack.sh

# For optimization - use prompts
claude -p "Use .claude/prompts/optimization.md to optimize [query]"
```

**End of Day:**

```bash
# Update priorities for tomorrow night
vim reports/priorities-$(date +%Y-%m-%d).md
git add reports/
git commit -m "docs: update priorities"
git push origin main

# Compound workflow will handle the rest automatically!
```

### Weekly Routine

**Monday:**

- Review last week's auto-implementations
- Update priorities for the week
- Check CLAUDE.md files for new learnings

**Friday:**

- Review what was learned this week (check CLAUDE.md)
- Update priorities for next week
- Archive completed priorities

---

## 🔍 Troubleshooting

### "Skill not working"

**Check:**

```bash
# Skill file exists?
ls .claude/skills/monorepo/graphql-full-stack.md

# Mention it correctly in prompt?
claude -p "Use monorepo/graphql-full-stack skill..."
# NOT: "Use the skill at .claude/skills/..."
```

### "Compound workflow didn't run"

**Check:**

```bash
# LaunchAgent loaded?
launchctl list | grep appcaire

# Check logs
tail -100 ~/Library/Logs/appcaire-compound.log

# Safety check passed?
# Must be on main branch, no uncommitted changes
git status
```

### "CLAUDE.md not updating"

**Check:**

```bash
# Script exists?
ls scripts/update-claude-md.sh

# Permissions?
ls -la scripts/update-claude-md.sh  # Should be executable

# Run manually
./scripts/update-claude-md.sh /CLAUDE.md
```

---

## 📖 Learning Path for New Users

### Week 1 - Basics

1. Run `./scripts/onboard-claude.sh`
2. Read `docs/learning/01-monorepo-basics.md`
3. Read `/CLAUDE.md` sections as needed
4. Use `graphql-full-stack` skill for one feature

### Week 2 - Skills & Prompts

1. Try all 3 skills
2. Use architecture prompts
3. Try worktrees for parallel work
4. Create first plan with template

### Week 3 - Advanced

1. Use subagents for complex task
2. Monitor compound workflow
3. Update CLAUDE.md with learnings
4. Optimize a query using prompts

### Week 4 - Mastery

1. Comfortable with all skills
2. Using worktrees regularly
3. Contributing to CLAUDE.md
4. Leveraging compound workflow

---

## 🎓 Additional Resources

### In Repository

- `/CLAUDE.md` - Comprehensive monorepo learnings
- `docs/ARCHITECT_PROMPT.md` - Full architecture
- `.claude/skills/` - All available skills
- `.claude/prompts/` - All prompt templates
- `docs/learning/` - Learning materials

### External

- [Claude Code Documentation](https://claude.ai/claude-code)
- [Prisma Documentation](https://www.prisma.io/docs)
- [Apollo GraphQL](https://www.apollographql.com/docs)
- [Boris's Original Thread](https://twitter.com/boris_vc/claude-code-techniques)

---

## 🚀 Quick Command Reference

```bash
# Onboarding
./scripts/onboard-claude.sh

# Skills
claude -p "Use monorepo/graphql-full-stack skill to add [feature]"
claude -p "Use monorepo/database-migration skill to add [field]"
claude -p "Use compound/extract-learnings skill"

# Worktrees
./scripts/worktree-setup.sh [name] [branch]
./scripts/worktree-cleanup.sh [name] [branch]
./scripts/sessions/dashboard-stack.sh

# Prompts
claude -p "Use .claude/prompts/architecture.md to design [feature]"
claude -p "Use .claude/prompts/optimization.md to optimize [query]"
claude -p "Use .claude/prompts/subagents.md [Pattern] for [task]"

# Planning
claude -p "Use .claude/plans/templates/feature-plan.md to plan [feature]"

# CI Monitor
./scripts/ci-monitor.sh

# Check status
gh pr list
git log --grep="CLAUDE.md"
launchctl list | grep appcaire
```

---

## 💡 Tips for Maximum Productivity

1. **Start every session with onboarding** - 5 minutes now saves hours later
2. **Check relevant CLAUDE.md first** - Common mistakes documented
3. **Use skills for common patterns** - Faster and more consistent
4. **Use worktrees for parallel work** - 3-5 features simultaneously
5. **Use subagents for complex tasks** - 40-80% time savings
6. **Update priorities daily** - Compound workflow implements overnight
7. **Review auto-PRs every morning** - Leverage overnight work
8. **Contribute to CLAUDE.md** - Make system smarter for next session

---

## 📞 Getting Help

**For documentation questions:**

1. Check this guide
2. Read relevant CLAUDE.md file
3. Check `.claude/skills/README.md`
4. Check `docs/learning/README.md`

**For technical issues:**

1. Check `/CLAUDE.md` Common Mistakes section
2. Check app-specific CLAUDE.md
3. Check troubleshooting in this guide

**For architecture questions:**

1. Read `docs/ARCHITECT_PROMPT.md`
2. Check `/CLAUDE.md` Architecture section
3. Use architecture prompts for guidance

---

**This productivity system is designed to make you faster, more consistent, and more effective. Use it to its full potential!** 🚀
