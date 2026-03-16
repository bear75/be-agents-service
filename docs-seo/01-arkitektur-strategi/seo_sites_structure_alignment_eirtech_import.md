---
name: SEO Sites Structure Alignment & Eirtech Import
overview: Align the 3 SEO sites to follow the simple, minimal structure pattern (like apps/dashboard), ensuring consistency without unnecessary complexity. Also import eirtech.ai from GitHub.
todos: []
---

# SEO Sites Structure Alignment & Eirtech Import Plan

## Overview

Align the 3 SEO sites to follow the **simple, minimal structure pattern** (like `apps/dashboard`), ensuring consistency across the monorepo while keeping them uncomplicated. Also import eirtech.ai from GitHub.

## Reference Pattern: Dashboard (Simple & Clean)

The `apps/dashboard` app provides the ideal reference - it's simple, well-structured, and follows monorepo best practices without unnecessary complexity:

- ✅ TypeScript: `tsconfig.json` + `tsconfig.node.json` (no separate app config needed)
- ✅ Vite: Simple config with path aliases and `envDir`
- ✅ ESLint: Basic config (optional but recommended)
- ✅ Package.json: Standard scripts (dev, build, preview, lint, type-check, clean)
- ❌ No error boundaries (not needed for simple sites)
- ❌ No testing setup (add later if needed)
- ❌ No complex folder structure (keep it simple)

## Current State Analysis

### SEO Sites Current State

- ✅ TypeScript: `tsconfig.json` exists, `tsconfig.node.json` exists
- ⚠️ TypeScript: Missing path aliases `@/*` → `./src/*`
- ❌ ESLint: No eslint config files
- ⚠️ Vite: Basic config, missing `envDir` and path aliases
- ✅ Package.json: Has basic scripts, missing `lint` in some
- ✅ Structure: Simple and clean (keep it that way!)

## Implementation Plan

### Phase 0: Rename Directories (Remove seo- prefix)

**Directories to rename:**

- `apps/seo-sverigeshemtjanst/` → `apps/sverigeshemtjanst/`
- `apps/seo-hemtjanstguide/` → `apps/hemtjanstguide/`
- `apps/seo-nackahemtjanst/` → `apps/nackahemtjanst/`

**Files to update:**

- Root `package.json` - Update scripts:
- `dev:seo-sverigeshemtjanst` → `dev:sverigeshemtjanst`
- `dev:seo-hemtjanstguide` → `dev:hemtjanstguide`
- `dev:seo-nackahemtjanst` → `dev:nackahemtjanst`
- Each app's `package.json` - Update `name` field:
- `"name": "seo-sverigeshemtjanst"` → `"name": "sverigeshemtjanst"`
- `"name": "seo-hemtjanstguide"` → `"name": "hemtjanstguide"`
- `"name": "seo-nackahemtjanst"` → `"name": "nackahemtjanst"`

### Phase 1: TypeScript Configuration (Minimal)

**Files to update:**

- `apps/sverigeshemtjanst/tsconfig.json` - Add path aliases and ensure extends root
- `apps/hemtjanstguide/tsconfig.json` - Add path aliases and ensure extends root
- `apps/nackahemtjanst/tsconfig.json` - Add path aliases and ensure extends root
- `apps/{site}/tsconfig.node.json` - Verify it exists (already exists)

**Changes:**

- Add path aliases `@/*` → `./src/*` in `tsconfig.json`
- Ensure `extends: "../../tsconfig.json"`
- Add `references` to `tsconfig.node.json`
- Keep it simple - no `tsconfig.app.json` needed

### Phase 2: Vite Configuration (Essential Only)

**Files to update:**

- `apps/sverigeshemtjanst/vite.config.ts` - Add path aliases and envDir
- `apps/hemtjanstguide/vite.config.ts` - Add path aliases and envDir
- `apps/nackahemtjanst/vite.config.ts` - Add path aliases and envDir

**Changes:**

- Add path alias: `"@": path.resolve(__dirname, "./src")`
- Add `envDir: path.resolve(__dirname, "../..")` to load root `.env` files
- Keep unique ports (3001, 3002, 3003)
- Keep build config simple (no complex optimizations needed)

### Phase 3: ESLint Configuration (Optional but Recommended)

**Files to create:**

- `apps/sverigeshemtjanst/eslint.config.js` - Basic ESLint 9 flat config
- `apps/hemtjanstguide/eslint.config.js` - Basic ESLint 9 flat config
- `apps/nackahemtjanst/eslint.config.js` - Basic ESLint 9 flat config

**Changes:**

- Use simple ESLint config (TypeScript + React rules)
- No i18n rules (not needed)
- Add to package.json: `"lint": "eslint ."`

**Note:** This is optional - can skip if not needed immediately.

### Phase 4: Package.json Scripts Alignment

**Files to update:**

- `apps/sverigeshemtjanst/package.json` - Ensure standard scripts exist
- `apps/hemtjanstguide/package.json` - Ensure standard scripts exist
- `apps/nackahemtjanst/package.json` - Ensure standard scripts exist
- Root `package.json` - Update scripts to use new names: `dev:sverigeshemtjanst`, `dev:hemtjanstguide`, `dev:nackahemtjanst`

**Scripts to verify/add:**

- ✅ `"dev": "vite"` - Already exists
- ✅ `"build": "vite build"` - Already exists
- ✅ `"preview": "vite preview"` - Already exists
- ⚠️ `"lint": "eslint ."` - Add if ESLint config created
- ✅ `"type-check": "tsc --noEmit"` - Already exists
- ✅ `"clean": "rm -rf dist .turbo node_modules"` - Already exists

### Phase 5: Import Eirtech.ai

**Steps:**

1. Clone/copy from `https://github.com/CairePlatform/eirtech`
2. Analyze structure to determine pattern:

- If simple static site → use SEO site pattern (this plan)
- If complex with i18n → use website pattern (more complex)

3. Create `apps/eirtech/` directory
4. Copy files maintaining structure
5. Update package.json to use workspace dependencies:

- `"@appcaire/graphql": "*"` (if needed)
- `"@appcaire/ui": "*"` (if needed)

6. Align configs:

- TypeScript: `tsconfig.json` + `tsconfig.node.json` with path aliases
- Vite: Simple config with path aliases and envDir
- ESLint: Basic config (optional)

7. Add to root `package.json`: `"dev:eirtech": "turbo run dev --filter=eirtech"`
8. Choose port: Suggest 3004 (or 5174 if 3004 conflicts)

**Decisions needed:**

- What port should eirtech use? (suggest 3004)
- Does it need i18n? (check original repo - probably not)
- Does it have a database? (check original repo)

## Files to Modify

### SEO Sites (all 3 sites):

**Essential (must do):**

- `apps/sverigeshemtjanst/tsconfig.json` - Add path aliases
- `apps/hemtjanstguide/tsconfig.json` - Add path aliases
- `apps/nackahemtjanst/tsconfig.json` - Add path aliases
- `apps/sverigeshemtjanst/vite.config.ts` - Add path aliases and envDir
- `apps/hemtjanstguide/vite.config.ts` - Add path aliases and envDir
- `apps/nackahemtjanst/vite.config.ts` - Add path aliases and envDir
- `apps/{site}/package.json` - Add lint script if ESLint added (all 3 sites)
- Root `package.json` - Update dev scripts to remove `seo-` prefix

**Optional (nice to have):**

- `apps/sverigeshemtjanst/eslint.config.js` - Create basic config
- `apps/hemtjanstguide/eslint.config.js` - Create basic config
- `apps/nackahemtjanst/eslint.config.js` - Create basic config

### Eirtech:

- `apps/eirtech/` - Create entire directory structure
- Root `package.json` - Add dev script
- `turbo.json` - Verify pipeline includes eirtech

## Key Principles

1. **Keep It Simple:**

- Follow dashboard pattern, not website pattern
- No error boundaries unless needed
- No testing setup unless needed
- No complex folder structure

2. **Essential Consistency:**

- TypeScript configs with path aliases
- Vite configs with path aliases and envDir
- Standard package.json scripts
- ESLint (optional but recommended)

3. **Maintain Uniqueness:**

- Keep Swedish-only (no i18n)
- Keep SEO database (DATABASE_URL)
- Keep unique ports (3001, 3002, 3003)

## Success Criteria

- ✅ All 3 SEO sites have path aliases (`@/*` → `./src/*`)
- ✅ All 3 SEO sites have `envDir` in Vite config
- ✅ All 3 SEO sites have standard package.json scripts
- ✅ ESLint configs added (optional)
- ✅ Eirtech.ai imported and aligned to monorepo standards
- ✅ All apps can run with `yarn dev:sverigeshemtjanst`, `yarn dev:hemtjanstguide`, `yarn dev:nackahemtjanst`
- ✅ All apps pass type-checking

## What We're NOT Adding

- ❌ Error boundaries (not needed for simple sites)
- ❌ Testing setup (add later if needed)
- ❌ Complex build optimizations (keep it simple)
- ❌ Analytics setup (add later if needed)
- ❌ Complex folder structure (keep current structure)
