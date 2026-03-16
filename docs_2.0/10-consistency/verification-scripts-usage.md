# Verification Scripts - Usage Guide

> **Date:** 2026-01-08  
> **Status:** ✅ Updated - New master script in use

## 📊 Summary: Which Script to Use?

| Script                                | Purpose                                     | Auto in seed.ts?        | When to Use                        |
| ------------------------------------- | ------------------------------------------- | ----------------------- | ---------------------------------- |
| **`00-verify-database-integrity.ts`** | **Master verification** (all checks + JSON) | ✅ **YES** (Step 26)    | **After every seed**               |
| `verify-seed-data.ts`                 | Basic count checks (OLD)                    | ❌ NO (replaced)        | **Don't use** - use master instead |
| `verify-merge-consistency.ts`         | After duplicate merge                       | ❌ NO (special purpose) | **After merge operations only**    |

## ✅ RECOMMENDED: Use Master Verification Script

### `00-verify-database-integrity.ts`

**This is the ONLY script you need for regular verification!**

**Features:**

- ✅ All checks (duplicates, orphans, missing data, rankings, counts, stats)
- ✅ JSON report (`apps/stats-server/verification-report.json`)
- ✅ Actionable recommendations
- ✅ CI/CD ready (exit code 1 on critical issues)
- ✅ Color-coded console output

**Automatic Usage (NEW!):**

```typescript
// In seed.ts (Step 26/26):
const verifyModule = await import("./00-verify-database-integrity.js");
await verifyModule.verifyDatabaseIntegrity();
```

**Manual Usage:**

```bash
# Run verification manually (recommended after changes)
yarn workspace stats-server db:verify

# Output: Console + JSON report
```

**Output Example:**

```bash
🔍 DATABASE INTEGRITY VERIFICATION

🔍 Check 1: Duplicate Providers by orgNumber...
   ✅ No duplicate orgNumbers

📊 VERIFICATION SUMMARY
✅ ALL CHECKS PASSED - Database integrity is excellent!

💾 JSON Report saved: apps/stats-server/verification-report.json
   Timestamp: 2026-01-08T12:00:00.000Z
   Status: PASS
   Critical: 0
   Warnings: 0
```

---

## ⚠️ OLD: Basic Verification (Replaced)

### `verify-seed-data.ts`

**Status:** ❌ **REPLACED by `00-verify-database-integrity.ts`**

**Why replaced:**

- ❌ Basic checks only (counts, simple duplicates)
- ❌ NO JSON report
- ❌ NO actionable recommendations
- ❌ NO orphaned records check
- ❌ NO rankings consistency check

**Migration:**

```bash
# OLD (don't use):
yarn workspace stats-server db:seed:verify

# NEW (use this):
yarn workspace stats-server db:verify
```

**This script is still in the codebase but NOT used in seed.ts anymore.**

---

## 🔧 SPECIAL: Merge Verification

### `verify-merge-consistency.ts`

**Purpose:** Verify data consistency AFTER merging duplicate providers

**When to use:** After running duplicate merge operations

**Workflow:**

```bash
# 1. Find duplicates
yarn workspace stats-server tsx src/scripts/find-and-merge-duplicates.ts

# 2. Merge duplicates
yarn workspace stats-server tsx src/seed-scripts/batch-merge-duplicates.ts

# 3. Verify merge consistency (special check)
yarn workspace stats-server tsx src/seed-scripts/verify-merge-consistency.ts

# 4. Run full verification (master script)
yarn workspace stats-server db:verify
```

**What it checks:**

- ✅ Foreign key integrity after merge
- ✅ No orphaned records
- ✅ Row counts consistent
- ✅ Corporate groups valid
- ✅ National statistics match

**This is a SUPPLEMENT to the master verification, not a replacement.**

---

## 🚀 Complete Workflow

### After Seeding (Automatic)

```bash
# Run seed (includes verification automatically at Step 26)
yarn workspace stats-server db:seed

# Output includes:
# - Step 1-25: All seed scripts
# - Step 26: Master verification (00-verify-database-integrity.ts)
# - verification-report.json created
```

### Manual Verification (After Changes)

```bash
# Quick verification
yarn workspace stats-server db:verify

# Check JSON report
cat apps/stats-server/verification-report.json | jq '.summary'

# Parse status programmatically
STATUS=$(jq -r '.summary.status' apps/stats-server/verification-report.json)
if [ "$STATUS" == "FAIL" ]; then
  echo "❌ Critical issues found!"
  exit 1
fi
```

### After Duplicate Merge

```bash
# 1. Merge duplicates
yarn workspace stats-server tsx src/seed-scripts/batch-merge-duplicates.ts

# 2. Special merge verification
yarn workspace stats-server tsx src/seed-scripts/verify-merge-consistency.ts

# 3. Full verification (master)
yarn workspace stats-server db:verify

# 4. Check report
cat apps/stats-server/verification-report.json | jq '.summary.status'
# Should show: "PASS"
```

---

## 📂 Files Overview

```
apps/stats-server/src/seed-scripts/
├── 00-verify-database-integrity.ts    ✅ MASTER (use this)
│   ├── Auto: YES (seed.ts step 26)
│   ├── Manual: yarn db:verify
│   └── Output: Console + JSON report
│
├── verify-seed-data.ts                ❌ OLD (replaced)
│   ├── Auto: NO (removed from seed.ts)
│   └── Status: Deprecated
│
└── verify-merge-consistency.ts        🔧 SPECIAL (after merge)
    ├── Auto: NO
    ├── Manual: tsx verify-merge-consistency.ts
    └── Use: After duplicate merge only
```

---

## 🎯 Quick Reference

**Most Common Use Cases:**

```bash
# 1. After seeding (automatic in seed.ts)
yarn workspace stats-server db:seed
# ✅ Verification runs automatically at Step 26

# 2. Manual verification (after changes)
yarn workspace stats-server db:verify
# ✅ Uses master script

# 3. Check verification report
cat apps/stats-server/verification-report.json | jq '.'

# 4. After merge operations
yarn workspace stats-server tsx src/seed-scripts/verify-merge-consistency.ts
yarn workspace stats-server db:verify
```

---

## 📋 Summary

| Action            | Command                           | Script Used                                          |
| ----------------- | --------------------------------- | ---------------------------------------------------- |
| **Seed database** | `yarn db:seed`                    | Includes `00-verify-database-integrity.ts` (Step 26) |
| **Manual verify** | `yarn db:verify`                  | `00-verify-database-integrity.ts`                    |
| **After merge**   | `tsx verify-merge-consistency.ts` | `verify-merge-consistency.ts` then `00-verify...`    |
| **Check report**  | `cat verification-report.json`    | Read JSON output                                     |

**Bottom Line:**

- ✅ **Use:** `00-verify-database-integrity.ts` (master script)
- ❌ **Don't use:** `verify-seed-data.ts` (old, replaced)
- 🔧 **Special:** `verify-merge-consistency.ts` (after merge only)

**Automatic in seed.ts:** YES - Master script runs at Step 26/26
