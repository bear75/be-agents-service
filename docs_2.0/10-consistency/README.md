# Frontend-Backend Consistency Documentation

## Essential Documents (Keep These)

### 1. **QUERY_USAGE_GUIDE.md** ⭐ **MOST IMPORTANT**

**Purpose:** Practical guide for developers on how to use queries and hooks
**When to read:** When implementing new features or fixing queries
**Content:** Hook usage patterns, query recommendations, best practices

### 2. **FRAGMENT_REFERENCE.md** ⭐ **QUICK REFERENCE**

**Purpose:** Quick lookup for all available fragments
**When to read:** When writing new queries or updating existing ones
**Content:** All fragments with field counts and usage examples

### 3. **COMPLETE_CONSISTENCY_SUMMARY.md** ⭐ **OVERVIEW**

**Purpose:** High-level summary of the entire consistency solution
**When to read:** To understand the overall architecture and what was fixed
**Content:** Problems solved, fragments created, validation approach

## Detailed Documentation (Reference)

### 4. **FRONTEND_BACKEND_CONSISTENCY.md**

**Purpose:** Detailed analysis of the problem and solution
**When to read:** To understand the root cause and architectural decisions
**Content:** Problem statement, current state analysis, solution design

### 5. **PROVIDER_QUERY_CONSISTENCY.md**

**Purpose:** Specific guide for provider query consistency
**When to read:** When working with provider queries specifically
**Content:** Provider fragments, municipality data consistency in providers

## Recommended Structure

```
docs/docs_2.0/10-consistency/
├── README.md (this file)
├── QUERY_USAGE_GUIDE.md ⭐ Start here for developers
├── FRAGMENT_REFERENCE.md ⭐ Quick lookup
├── COMPLETE_CONSISTENCY_SUMMARY.md ⭐ Overview
├── FRONTEND_BACKEND_CONSISTENCY.md (detailed reference)
└── PROVIDER_QUERY_CONSISTENCY.md (provider-specific)
```

## Quick Start for Developers

1. **New to the system?** → Read `COMPLETE_CONSISTENCY_SUMMARY.md`
2. **Writing a new query?** → Check `FRAGMENT_REFERENCE.md`
3. **Using hooks in code?** → Follow `QUERY_USAGE_GUIDE.md`
4. **Working with providers?** → See `PROVIDER_QUERY_CONSISTENCY.md`
