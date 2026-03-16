# App → Domain Mapping

> **Last updated:** January 2025

## Overview

The AppCaire monorepo contains **5 SEO/Marketing apps** deployed to separate domains. All apps use **Vite SSR** for optimal SEO performance.

---

## SEO Marketing Apps

| App                 | Domain                   | Type            | Port | Purpose                             |
| ------------------- | ------------------------ | --------------- | ---- | ----------------------------------- |
| `eirtech`           | **eirtech.ai**           | B2B Tech        | 3004 | AI/Tech company site, EirTech brand |
| `hemtjanstguide`    | **hemtjanstguide.se**    | B2C Marketplace | 3002 | Consumer guide for home care        |
| `nackahemtjanst`    | **nackahemtjanst.se**    | B2C Local       | 3003 | Local SEO for Nacka municipality    |
| `sverigeshemtjanst` | **sverigeshemtjanst.se** | B2B Hub         | 3001 | Industry portal for home care       |
| `website`           | **www.caire.se**         | B2B SaaS        | 3005 | Main product site for Caire         |

---

## Detailed App Descriptions

### 1. eirtech (`apps/eirtech`)

**Domain:** `eirtech.ai`  
**Port:** 3004  
**Type:** B2B Tech Company Site

**Purpose:**

- EirTech AI brand website
- Presentation of AI product portfolio
- Technical focus, English/Swedish

**SSR Status:** ✅ Full SSR implemented

- `entry-server.tsx` - Server-side rendering
- `entry-client.tsx` - Client hydration
- `server.ts` - Express SSR server

**Tech Stack:**

- Vite SSR with Express
- react-helmet-async for meta tags
- i18n (sv/en)
- vite-plugin-sitemap

---

### 2. hemtjanstguide (`apps/hemtjanstguide`)

**Domain:** `hemtjanstguide.se`  
**Port:** 3002  
**Type:** B2C Consumer Marketplace

**Purpose:**

- Guide for consumers looking for home care
- Comparison of providers per municipality
- Information about applications, rights, fees
- SEO focus on "find home care [city]"

**SSR Status:** ⚠️ Needs SSR implementation

**Tech Stack:**

- Vite (CSR)
- Apollo Client for GraphQL
- react-helmet-async
- Connects to stats-server for data

---

### 3. nackahemtjanst (`apps/nackahemtjanst`)

**Domain:** `nackahemtjanst.se`  
**Port:** 3003  
**Type:** B2C Local SEO Satellite

**Purpose:**

- Local SEO for Nacka municipality
- "Cash cow" for local ranking
- Specific information about home care in Nacka
- Feeds traffic into the ecosystem

**SSR Status:** ⚠️ Needs SSR implementation

**Tech Stack:**

- Vite (CSR)
- Apollo Client for GraphQL
- react-helmet-async

---

### 4. sverigeshemtjanst (`apps/sverigeshemtjanst`)

**Domain:** `sverigeshemtjanst.se`  
**Port:** 3001  
**Type:** B2B Industry Hub

**Purpose:**

- Industry portal for home care providers
- National statistics and market data
- Partner portal and dashboard
- Consolidated site (previously separate regional sites)

**SSR Status:** ⚠️ Partial SSR, needs completion

**Tech Stack:**

- Vite (partial SSR config)
- Apollo Client for GraphQL
- Clerk for authentication (partner portal)
- react-helmet-async

---

### 5. website (`apps/website`)

**Domain:** `www.caire.se`  
**Port:** 3005  
**Type:** B2B SaaS Product Site

**Purpose:**

- Main site for Caire scheduling platform
- Lead generation and conversion
- Product information, pricing, demo booking
- Resources, blog, careers

**SSR Status:** ⚠️ Needs SSR implementation  
**Migration:** Replaces current live site from `CairePlatform/caire` repo

**Tech Stack:**

- Vite (CSR)
- Supabase for auth/forms
- Framer Motion for animations
- Comprehensive i18n (sv/en)

---

## Backend Services

| Service        | Port | Purpose                                                   |
| -------------- | ---- | --------------------------------------------------------- |
| `stats-server` | 4005 | SEO GraphQL API for statistics, municipalities, providers |
| `server`       | 4000 | Dashboard API for scheduling                              |

### Data Flow

```
hemtjanstguide     ──┐
nackahemtjanst     ──┼──▶ GraphQL ──▶ stats-server ──▶ PostgreSQL (SEO DB)
sverigeshemtjanst  ──┘

eirtech ──▶ Static content (no backend)
website ──▶ Supabase (forms, auth)
```

---

## SSR Implementation Status

| App               | SSR | entry-server | entry-client | server.ts | Priority  |
| ----------------- | --- | ------------ | ------------ | --------- | --------- |
| eirtech           | ✅  | ✅           | ✅           | ✅        | -         |
| hemtjanstguide    | ❌  | ❌           | ❌           | ❌        | 🔴 High   |
| nackahemtjanst    | ❌  | ❌           | ❌           | ❌        | 🟡 Medium |
| sverigeshemtjanst | ⚠️  | ❌           | ❌           | ❌        | 🔴 High   |
| website           | ❌  | ❌           | ❌           | ❌        | 🔴 High   |

---

## Local Development

### Start all apps

```bash
# From root
yarn dev
```

### Start individual app

```bash
# SEO sites
yarn workspace eirtech dev         # http://localhost:3004
yarn workspace hemtjanstguide dev  # http://localhost:3002
yarn workspace nackahemtjanst dev  # http://localhost:3003
yarn workspace sverigeshemtjanst dev # http://localhost:3001
yarn workspace website dev         # http://localhost:3005

# Backend
yarn workspace stats-server dev    # http://localhost:4005/graphql
```

---

## Deployment Structure

### Production routing

Each domain points to its respective app:

```
eirtech.ai           → apps/eirtech
hemtjanstguide.se    → apps/hemtjanstguide
nackahemtjanst.se    → apps/nackahemtjanst
sverigeshemtjanst.se → apps/sverigeshemtjanst
www.caire.se         → apps/website
```

### Hosting

- **Vercel** - Frontend apps
- **Railway/Fly.io** - SSR servers (Express)
- **Neon/Supabase** - PostgreSQL databases

---

## Deprecated Domains (301 Redirects)

The following domains are deprecated and redirect to `sverigeshemtjanst.se`:

| Old Domain             | Redirect To                             |
| ---------------------- | --------------------------------------- |
| hemtjanstistockholm.se | sverigeshemtjanst.se/regioner/stockholm |
| hemtjanstnacka.se      | sverigeshemtjanst.se/regioner/nacka     |
| stockholmhemtjanst.se  | sverigeshemtjanst.se/innovation         |

**NOTE:** These domains are NOT active apps in the monorepo. They are DNS redirects only.

---

## Related Documents

- [VITE_SSR_SETUP.md](../02-seo-teknisk-implementation/VITE_SSR_SETUP.md) - SSR implementation guide
- [STRATEGY_ECOSYSTEM_2025.md](./STRATEGY_ECOSYSTEM_2025.md) - Domain architecture strategy
- [SEO_CHECKLIST.md](../02-seo-teknisk-implementation/SEO_CHECKLIST.md) - Pre-deployment checklist
