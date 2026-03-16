# SEO Technical Implementation

> **Last updated:** January 2026

This folder contains technical documentation for SEO implementation in Caire marketing sites (https://caire.se), including 2026 AI/agentic search optimization.

---

## Documents

### Core Guides

| Document                                               | Description                                                     |
| ------------------------------------------------------ | --------------------------------------------------------------- |
| [SEO_2026_GUIDE.md](./SEO_2026_GUIDE.md)               | **Main guide** - 2026 SEO best practices & AI optimization      |
| [SEO_SUMMARY_2026.md](./SEO_SUMMARY_2026.md)           | **Status summary** - Current implementation status              |
| [SEO_AUDIT_2026.md](./SEO_AUDIT_2026.md)               | Comprehensive audit report with findings                        |
| [KEYWORD_STRATEGY.md](./KEYWORD_STRATEGY.md)           | **Keyword strategy** - Complete keyword plan by target audience |
| [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md)               | Vite SSR implementation guide                                   |
| [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md)     | Meta tags, react-helmet-async, AI agent directives              |
| [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md) | JSON-LD schema markup                                           |
| [SITEMAP_ROBOTS.md](./SITEMAP_ROBOTS.md)               | Sitemap generation and robots.txt                               |
| [SSR_SEO_TESTING_GUIDE.md](./SSR_SEO_TESTING_GUIDE.md) | Testing procedures for SSR and SEO                              |
| [SEO_CHECKLIST.md](./SEO_CHECKLIST.md)                 | Pre-deployment checklist                                        |

### Migration Guides

| Document                                                                           | Description                                        |
| ---------------------------------------------------------------------------------- | -------------------------------------------------- |
| [NACKAHEMTJANST_MIGRATION_GUIDE.md](./NACKAHEMTJANST_MIGRATION_GUIDE.md)           | WordPress to React migration for nackahemtjanst.se |
| [SEO_CONTENT_AUDIT_NACKAHEMTJANST.md](./SEO_CONTENT_AUDIT_NACKAHEMTJANST.md)       | SEO content audit for Nacka migration              |
| [nackahemtjnst.WordPress.2025-12-22.xml](./nackahemtjnst.WordPress.2025-12-22.xml) | WordPress export file (reference)                  |

---

## Quick Start

### 1. Implement SSR

See [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md) for:

- `entry-server.tsx`
- `entry-client.tsx`
- `server.ts`

### 2. Add SEO Component

See [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md) for:

- Meta tags
- Open Graph
- AI agent directives (2026)

### 3. Structured Data

See [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md) for:

- Organization
- WebSite
- Article
- FAQPage

### 4. Verify

See [SEO_CHECKLIST.md](./SEO_CHECKLIST.md) for complete checklist.

---

## Quick Reference

### Ranking Examples

- **Data-complete provider (ex: OmsorgPlus AB)**: has full structured data (Organization, Service, FAQPage), optimized meta (title/description/Open Graph), llms.txt, fast LCP/CLS; ranking improves and appears in top list cards with rich snippets.
- **Data-sparse provider (ex: TryggVård Demo)**: missing structured data and meta descriptions, thin content, no llms.txt; ranking drops, surfaces lower in lists without rich result enhancements.

### CaireIndex – beräkning (källa vs visning)

- **Databas (källa, v5, [seed-scripts/v2/22-calculate-rankings-comprehensive.ts](../../apps/stats-server/src/seed-scripts/v2/22-calculate-rankings-comprehensive.ts))**: 100 p total med täckningsfaktor `sqrt(completeness)`. Primary 60 p (brukarnöjdhet 25, kontinuitet 20, utbildning 15), Secondary 20 p (planer/rutiner m.m.), Financial 10 p, Operational 10 p. `metadata.details` lagrar för närvarande satisfaction/continuity/education; övriga komponenter finns i `components`.
- **Förenklad visning (UI)**: 4 faktorer som summerar till 100: Brukarnöjdhet 45%, Personalkontinuitet 25%, Utbildningsnivå 10%, Datakvalitet 20%. Datakvalitet = 100 om `isCaireCertified`; annars 70 om org är claimed + verifierad kontaktinfo; annars 0. UI kan även visa backend-komponenterna om de finns i metadata.

### Verify SSR is Working

```bash
curl -s https://sverigeshemtjanst.se/ | grep -A 10 '<div id="root">'
# ✅ Should see HTML content inside root div
```

### Check Meta Tags

```bash
curl -s https://sverigeshemtjanst.se/ | grep -E "(title>|description|GPTBot|anthropic)"
```

### Check Structured Data

```bash
curl -s https://sverigeshemtjanst.se/ | \
  grep -oP '(?<=application/ld\+json">).*(?=</script>)' | \
  jq .
```

### Test AI Citations

Test with ChatGPT/Claude/Perplexity:

- "What is the maximum monthly cost for home care in Sweden?"
- "How do I start a home care business in Sweden?"

---

## Current Status

See [SEO_SUMMARY_2026.md](./SEO_SUMMARY_2026.md) for detailed status.

**Phase 1 Complete:** ✅ Sitemaps, robots.txt, llms.txt updated  
**Phase 2 Ready:** Enhanced components and schema helpers available  
**Phase 3-4:** Content optimization and testing

---

## SSR Status per App

| App               | SSR        | Priority |
| ----------------- | ---------- | -------- |
| eirtech           | ✅ Done    | -        |
| hemtjanstguide    | ✅ Working | -        |
| nackahemtjanst    | ⚠️ Partial | Medium   |
| sverigeshemtjanst | ✅ Working | -        |
| website           | ❌ Missing | High     |

---

## Related Documents

- [Architecture & Strategy](../01-arkitektur-strategi/) - Domain mapping
- [Brand & Design](../03-brand-design/) - Design system
- [Data Integration](../04-data-integration/) - GraphQL setup
