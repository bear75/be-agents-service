# Productivity System - Quick Reference Card

**30-second guide to Boris's 10 Techniques implementation**

---

## 🚀 New Session? Start Here

```bash
./scripts/onboard-claude.sh  # 5-minute onboarding
```

---

## 📚 Essential Reading

| File                                  | When              | Time   |
| ------------------------------------- | ----------------- | ------ |
| `docs/learning/01-monorepo-basics.md` | First thing       | 5 min  |
| `/CLAUDE.md`                          | Before work       | 15 min |
| `docs/PRODUCTIVITY_SYSTEM.md`         | How to use system | 10 min |

---

## 🎯 Common Tasks

### Implement GraphQL Feature

```bash
claude -p "Use monorepo/graphql-full-stack skill to add employee certifications"
```

### Database Migration

```bash
claude -p "Use monorepo/database-migration skill to add phone field"
```

### Parallel Development

```bash
./scripts/sessions/dashboard-stack.sh  # 3 parallel sessions
```

### Extract Learnings

```bash
claude -p "Use compound/extract-learnings skill"
```

### Plan Complex Feature

```bash
claude -p "Use .claude/plans/templates/feature-plan.md to plan visit notes feature"
```

### Optimize Performance

```bash
claude -p "Use .claude/prompts/optimization.md to fix N+1 queries"
```

### Use Subagents

```bash
claude -p "Use .claude/prompts/subagents.md Parallel Development pattern for [task]"
```

---

## 📂 Documentation Locations

| What                   | Where                          |
| ---------------------- | ------------------------------ |
| **Monorepo learnings** | `/CLAUDE.md`                   |
| **App learnings**      | `/apps/{app}/CLAUDE.md`        |
| **Skills**             | `.claude/skills/*.md`          |
| **Prompts**            | `.claude/prompts/*.md`         |
| **Planning**           | `.claude/plans/templates/*.md` |
| **Learning path**      | `docs/learning/*.md`           |
| **Full guide**         | `docs/PRODUCTIVITY_SYSTEM.md`  |

---

## 🤖 Automatic Workflow

**10:30 PM** - Extracts learnings, updates CLAUDE.md
**11:00 PM** - Implements priority #1

**Your job:**

1. Update priorities: `reports/priorities-$(date +%Y-%m-%d).md`
2. Review PR in morning: `gh pr list`

---

## ⚡ Common Mistakes (Must Read!)

1. **Forgot codegen** → `yarn workspace @appcaire/graphql codegen`
2. **BigInt error** → Convert to Number in resolvers
3. **Missing org filter** → Add organizationId filter
4. **Wrong env prefix** → Use `VITE_` for Vite apps

See `/CLAUDE.md` for complete list!

---

## 🔧 Scripts

```bash
# Worktrees
./scripts/worktree-setup.sh feature my-branch
./scripts/worktree-cleanup.sh feature my-branch

# CI Monitor
./scripts/ci-monitor.sh

# Onboarding
./scripts/onboard-claude.sh
```

---

## 📊 Check Status

```bash
# Recent CLAUDE.md updates
git log --grep="CLAUDE.md"

# Auto-implemented PRs
gh pr list

# Compound workflow logs
tail -f logs/auto-compound.log
```

---

## 💡 Pro Tips

- ✅ Always check `/CLAUDE.md` first - saves hours
- ✅ Use skills for common patterns - faster & consistent
- ✅ Use worktrees for parallel work - 3-5 features at once
- ✅ Update priorities daily - auto-implemented overnight
- ✅ Review auto-PRs every morning - leverage automation

---

**Full documentation:** `docs/PRODUCTIVITY_SYSTEM.md`
