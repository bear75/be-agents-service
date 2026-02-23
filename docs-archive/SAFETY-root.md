# Compound Workflow Safety Guide

## ⚠️ Critical Safety Information

The compound workflow scripts (`daily-compound-review.sh` and `auto-compound.sh`) are **SCHEDULED TO RUN AUTOMATICALLY** every night. They have been designed with safety checks to prevent data loss.

## Schedule

- **10:30 PM**: `daily-compound-review.sh` - Reviews threads and updates CLAUDE.md
- **11:00 PM**: `auto-compound.sh` - Picks priority, creates PRD, implements, and creates PR

## Safety Checks (Added 2026-01-31)

Both scripts now include **mandatory safety checks** that will abort execution if:

1. **Uncommitted changes detected**
   - The script will exit immediately
   - No changes will be made
   - You must commit or stash your work first

2. **Not on main branch**
   - The script will exit immediately
   - Prevents accidentally destroying work on feature branches
   - You must switch to main and push all feature work first

## What to Do Before 10:30 PM Each Day

To ensure the nightly workflow runs successfully:

1. **Commit all your work**

   ```bash
   git add -A
   git commit -m "your message"
   git push
   ```

2. **Switch to main branch**

   ```bash
   git checkout main
   ```

3. **Ensure main is clean**
   ```bash
   git status  # Should show "nothing to commit, working tree clean"
   ```

## Why These Checks Matter

**Before these safety checks were added:**

- Scripts used `git reset --hard origin/main` unconditionally
- Any uncommitted work was **permanently deleted**
- Working on a feature branch? Your work was **destroyed**
- This caused the loss of benchmarks work on 2026-01-31

**After these safety checks:**

- Scripts will refuse to run if any work might be lost
- You get a clear error message explaining what's wrong
- No data loss can occur

## What If I Want to Keep Working Past 10:30 PM?

You have two options:

### Option 1: Disable the nightly jobs temporarily

```bash
# Disable daily review
launchctl unload ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist

# Disable auto-compound
launchctl unload ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

Remember to re-enable them later:

```bash
launchctl load ~/Library/LaunchAgents/com.appcaire.daily-compound-review.plist
launchctl load ~/Library/LaunchAgents/com.appcaire.auto-compound.plist
```

### Option 2: Ensure you're on main with clean tree

Just make sure:

1. All work is committed and pushed
2. You're on the main branch
3. Working tree is clean

The scripts will then run safely.

## Manual Execution

You can run these scripts manually anytime:

```bash
# Run daily review
./scripts/compound/daily-compound-review.sh

# Run auto-compound
./scripts/compound/auto-compound.sh
```

The same safety checks apply - they will abort if it's not safe.

## Troubleshooting

### "SAFETY CHECK FAILED: Uncommitted changes detected"

**Cause:** You have uncommitted work in your repo.

**Fix:**

```bash
# See what's uncommitted
git status

# Commit your changes
git add -A
git commit -m "your message"

# Or stash them temporarily
git stash
```

### "SAFETY CHECK FAILED: Not on main branch"

**Cause:** You're on a feature branch.

**Fix:**

```bash
# Push your feature work first
git push

# Switch to main
git checkout main

# If you have uncommitted changes on the feature branch:
git checkout feature/your-branch
git add -A
git commit -m "your message"
git push
git checkout main
```

### "No reports found in reports/ directory"

**Cause:** The auto-compound script expects priority reports in `reports/` directory after resetting to main.

**Fix:**

1. Ensure priority reports are committed to main branch (e.g. `reports/priorities-2026-01-31.md`)
2. Keep the reports directory up-to-date with current priorities

## Historical Context

**2026-01-31:** Added safety checks after benchmarks work was lost due to unconditional `git reset --hard origin/main` running while on feature branch with uncommitted changes.

**Why the original design was dangerous:**

- The scripts were designed to "always succeed" by forcing a clean state
- This achieved reliability at the cost of safety
- Any work in progress was destroyed without warning
- The assumption was that you'd always be on main with clean tree at 10:30 PM

**New design philosophy:**

- **Fail safely** rather than succeed dangerously
- **Explicit is better than implicit** - require manual cleanup
- **Protect user work** above all else
- **Clear error messages** so you know exactly what to do
