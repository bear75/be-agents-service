# SEO Implementation Guide - 2026 Edition

> **Last Updated:** 2026-01-09  
> **Focus:** AI/Agentic Search Optimization + Traditional SEO

---

## Table of Contents

1. [What's New in 2026 SEO](#whats-new-in-2026-seo)
2. [AI/Agentic Search Optimization](#ai-agentic-search-optimization)
3. [Implementation Checklist](#implementation-checklist)
4. [SEO Component Usage](#seo-component-usage)
5. [Structured Data (JSON-LD)](#structured-data-json-ld)
6. [Meta Tags Best Practices](#meta-tags-best-practices)
7. [Content Optimization for AI](#content-optimization-for-ai)
8. [Testing & Validation](#testing--validation)

---

## What's New in 2026 SEO

### Major Changes from 2024/2025

1. **AI/Agentic Search Dominance**
   - ChatGPT, Claude, Perplexity now drive 30%+ of search traffic
   - Zero-click answers are the norm
   - Entity-based search replaces keyword-based
   - Voice search optimization critical

2. **Core Web Vitals Update**
   - **INP** (Interaction to Next Paint) replaces FID
   - Target: INP < 200ms (stricter than FID < 100ms)
   - Mobile-first indexing is 100% default

3. **New Meta Directives**
   - AI-specific meta tags (GPTBot, Claude-Web, etc.)
   - Entity markup for answer extraction
   - Speakable content annotations

4. **llms.txt Standard**
   - New file at `/llms.txt` for AI agent context
   - Structured format for AI understanding
   - Critical for citation in AI responses

---

## AI/Agentic Search Optimization

### 1. llms.txt File (CRITICAL)

**Location:** `/public/llms.txt`

**Purpose:** Provides structured context for AI agents to understand your site and cite it correctly.

**Format:**

```txt
# [Site Name] - LLM Context File

## Overview
Brief description of site, purpose, target audience

## Coverage & Data Scope
What topics, geographies, time periods you cover

## Key Topics & Expertise
Detailed breakdown of what you're authoritative on

## Key Pages & Resources
List of high-value pages with descriptions

## Key Statistics (current year)
Important numbers AI agents can cite

## Frequently Asked Questions (for AI Agents)
Q&A format that AI can extract

## Contact & Support
How to reach you

## Citation Guidelines
How AI should cite your site

## Limitations & Disclaimers
What you DON'T cover
```

**Examples:**

- `apps/sverigeshemtjanst/public/llms.txt` ✅ Complete
- `apps/hemtjanstguide/public/llms.txt` ✅ Complete

### 2. AI Agent Meta Tags (REQUIRED)

Add to every page in your SEO component:

```typescript
<meta name="robots" content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1" />
<meta name="googlebot" content="index, follow" />
<meta name="bingbot" content="index, follow" />

<!-- AI Agents (2026) -->
<meta name="GPTBot" content="index, follow" />
<meta name="ChatGPT-User" content="index, follow" />
<meta name="anthropic-ai" content="index, follow" />
<meta name="Claude-Web" content="index, follow" />
<meta name="PerplexityBot" content="index, follow" />
<meta name="CCBot" content="index, follow" />
<meta name="Google-Extended" content="index, follow" />
<meta name="Applebot-Extended" content="index, follow" />
```

### 3. Entity Markup (HIGH PRIORITY)

Help AI extract specific entities (prices, dates, people, places):

```typescript
// Add to structured data
{
  "@context": "https://schema.org",
  "@type": "WebPage",
  "mentions": [
    {
      "@type": "MonetaryAmount",
      "currency": "SEK",
      "value": "2169",
      "description": "Maximum monthly fee for home care"
    },
    {
      "@type": "Place",
      "name": "Stockholm",
      "containedIn": {
        "@type": "Country",
        "name": "Sweden"
      }
    }
  ]
}
```

### 4. Answer-Focused Content Structure

**OLD (keyword-focused):**

```markdown
## Home Care Costs in Sweden

Home care costs vary by municipality. The cost is based on income.
Keywords: hemtjänst kostnad, vad kostar hemtjänst, avgift hemtjänst
```

**NEW (answer-focused):**

```markdown
# How Much Does Home Care Cost in Sweden?

## Quick Answer

The maximum monthly fee for home care in Sweden is **2,169 SEK** (2026), regardless of how much care you receive. Your actual cost depends on your income and may be free.

## Detailed Breakdown

- **Income < 14,000 SEK/month:** Free
- **Income 14,000-25,000 SEK/month:** Sliding scale (0-1,500 SEK)
- **Income > 25,000 SEK/month:** Maximum fee (2,169 SEK)

## Who Pays the Rest?

The municipality covers the difference. Average cost to municipality: 8,000-18,000 SEK per recipient per month.

## Examples

| Your Income | Your Cost | Municipality Pays |
| ----------- | --------- | ----------------- |
| 12,000 SEK  | 0 SEK     | 100%              |
| 20,000 SEK  | 1,200 SEK | 85%               |
| 35,000 SEK  | 2,169 SEK | 80%               |
```

### 5. FAQPage Schema (CRITICAL for AI)

For any page with Q&A content:

```typescript
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "How much does home care cost in Sweden?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "The maximum monthly fee is 2,169 SEK (2026) regardless of care amount. Lower income means lower fees, potentially free. The municipality covers the rest.",
      },
    },
    {
      "@type": "Question",
      name: "How do I apply for home care?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Contact your municipality's biståndshandläggare (welfare officer). The process includes: 1) Initial meeting, 2) Home assessment, 3) Decision (2-4 weeks), 4) Choose provider (if LOV municipality), 5) Care starts.",
      },
    },
  ],
};
```

---

## Implementation Checklist

### Phase 1: Critical (Week 1) 🔴

- [x] Update sitemap.xml with all current routes
- [x] Update robots.txt with 2026 AI agent directives
- [x] Create llms.txt file for each site
- [ ] Add AI agent meta tags to SeoHead component
- [ ] Test SSR rendering (curl test)

### Phase 2: Structured Data (Week 2) 🟠

- [ ] Add FAQPage schema to guide pages
- [ ] Add LocalBusiness schema to provider pages
- [ ] Add BreadcrumbList schema to deep pages
- [ ] Add Article schema to knowledge pages
- [ ] Validate with Google Rich Results Test

### Phase 3: Content Optimization (Week 3) 🟡

- [ ] Restructure guides to Q&A format
- [ ] Add "Quick Answer" sections to articles
- [ ] Convert data to tables (for AI extraction)
- [ ] Add entity markup for key facts
- [ ] Update titles for question format ("How to...", "What is...")

### Phase 4: Testing (Week 4) 🟢

- [ ] Test with ChatGPT/Claude/Perplexity
- [ ] Run Lighthouse audits (target: 90+ SEO)
- [ ] Validate structured data
- [ ] Check Core Web Vitals
- [ ] Submit updated sitemaps to GSC

---

## SEO Component Usage

### Current Components

**Package:** `@appcaire/shared/seo`

1. **SeoHead** (react-helmet-async) - Used by sverigeshemtjanst.se
2. **SEO** (basic) - Used by hemtjanstguide.se, nackahemtjanst.se

### Recommended: Upgrade to EnhancedSeoHead

**Location:** Create at `packages/shared/seo/components/shared/EnhancedSeoHead.tsx`

**Features:**

- AI agent meta directives (2026)
- Entity markup support
- Speakable content annotations
- Content classification for AI
- Full backward compatibility

**Usage:**

```typescript
import { EnhancedSeoHead } from "@appcaire/shared/seo";

<EnhancedSeoHead
  title="Starta Hemtjänstföretag | Komplett Guide 2026"
  description="Komplett guide för att starta hemtjänstföretag i Sverige. Krav, licenser, finansiering och marknadsanalys."
  canonicalUrl="https://sverigeshemtjanst.se/kunskap/starta-hemtjanstforetag"
  keywords={["starta hemtjänstföretag", "hemtjänst krav", "IVO registrering"]}

  // 2026 AI Optimization
  contentClassification="Business Guide"
  targetAudience="entrepreneurs, decision-makers"
  publishDate="2026-01-09T00:00:00+01:00"

  // Structured data
  schemaMarkup={articleSchema}

  // Entity hints
  entities={[
    { type: "Organization", name: "IVO" },
    { type: "Organization", name: "Sveriges Kommuner och Regioner" }
  ]}
/>
```

---

## Structured Data (JSON-LD)

### Required Schemas by Page Type

| Page Type             | Schema Types             | Priority    |
| --------------------- | ------------------------ | ----------- |
| **Homepage**          | Organization + WebSite   | 🔴 Critical |
| **Guide/Article**     | Article + FAQPage        | 🔴 Critical |
| **Provider Page**     | LocalBusiness            | 🟠 High     |
| **Municipality Page** | Place + ItemList         | 🟡 Medium   |
| **Ranking Page**      | ItemList                 | 🟡 Medium   |
| **Deep Pages**        | WebPage + BreadcrumbList | 🟢 Low      |

### Examples

**1. FAQPage (Guide Pages)**

```typescript
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "Hur mycket kostar hemtjänst?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Max 2,169 SEK/månad oavsett omfattning. Lägre inkomst = lägre avgift.",
      },
    },
  ],
};
```

**2. LocalBusiness (Provider Pages)**

```typescript
const businessSchema = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": `https://sverigeshemtjanst.se/anordnare/${providerSlug}#business`,
  name: provider.name,
  description: provider.description,
  address: {
    "@type": "PostalAddress",
    addressLocality: provider.city,
    addressCountry: "SE",
  },
  areaServed: provider.municipalities.map((m) => ({
    "@type": "City",
    name: m.name,
  })),
  aggregateRating: provider.caireIndex
    ? {
        "@type": "AggregateRating",
        ratingValue: provider.caireIndex,
        bestRating: "100",
        worstRating: "0",
      }
    : undefined,
};
```

**3. Article (Knowledge Pages)**

```typescript
const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  headline: "Starta Hemtjänstföretag | Komplett Guide 2026",
  description: "Guide to starting a home care business",
  datePublished: "2026-01-09T00:00:00+01:00",
  dateModified: "2026-01-09T00:00:00+01:00",
  author: {
    "@type": "Organization",
    name: "Sveriges Hemtjänst",
  },
  publisher: {
    "@type": "Organization",
    name: "EirTech AB",
    logo: {
      "@type": "ImageObject",
      url: "https://sverigeshemtjanst.se/logo.png",
    },
  },
  // Add speakable sections for voice search
  speakable: {
    "@type": "SpeakableSpecification",
    cssSelector: [".summary", ".quick-answer", ".key-points"],
  },
};
```

---

## Meta Tags Best Practices

### Title Tag Format (2026)

**Pattern:** `[Question/Topic] | [Context] - [Brand]`

**Examples:**

```html
<!-- OLD (keyword stuffing) -->
<title>Hemtjänst Stockholm Bästa Utförare 2026</title>

<!-- NEW (answer-focused, natural) -->
<title>Vem är bästa hemtjänstutförare i Stockholm? | Sveriges Hemtjänst</title>
<title>
  Hur mycket kostar hemtjänst? | Avgifter & Maxtaxa - Hemtjänstguiden
</title>
<title>
  Starta Hemtjänstföretag 2026 | Komplett Guide - Sveriges Hemtjänst
</title>
```

**Length:** 50-60 characters (Google displays ~60 chars)

### Description Tag (2026)

**Pattern:** `[Direct answer]. [Supporting detail]. [Call to action]`

**Examples:**

```html
<!-- OLD (vague, keyword stuffing) -->
<meta
  name="description"
  content="Hemtjänst Stockholm bästa utförare guide jämför hemtjänstföretag kvalitet pris 2026"
/>

<!-- NEW (clear, helpful, conversational) -->
<meta
  name="description"
  content="Max 2,169 SEK/månad oavsett hur mycket vård du får. Lägre inkomst = lägre avgift, ofta gratis. Läs komplett guide om avgifter och maxtaxa."
/>
```

**Length:** 150-160 characters

### Keywords Meta Tag (2026)

**Status:** Not used by major search engines, but helpful for:

- Internal search
- Content planning
- AI context

**Usage:**

```typescript
keywords={[
  "starta hemtjänstföretag",
  "hemtjänst auktorisation",
  "IVO registrering",
  "hemtjänst lönsamhet"
]}
```

---

## Content Optimization for AI

### 1. Use Clear Heading Hierarchy

```markdown
# Main Question (H1) - Only ONE per page

"How Much Does Home Care Cost in Sweden?"

## Sub-Questions (H2)

"What is Maxtaxa?"
"How is the Fee Calculated?"

### Details (H3)

"Income Brackets"
"Regional Differences"
```

### 2. Add Summary Sections

Every article should have:

```markdown
## Quick Answer (at top)

One paragraph with the core answer

## Key Points (bullet list)

- 3-5 main takeaways
- Numbered if sequential
- Bulleted if parallel

## Detailed Information

Full explanation with tables, examples
```

### 3. Use Data Tables

AI extracts tables better than prose:

```markdown
| Municipality | Reimbursement Rate | LOV Status |
| ------------ | ------------------ | ---------- |
| Stockholm    | 380 SEK/hour       | Yes        |
| Göteborg     | 365 SEK/hour       | Yes        |
| Malmö        | 350 SEK/hour       | Yes        |
```

### 4. Add Contextual Information

Always include:

- **Date/Year:** "As of 2026..."
- **Source:** "According to IVO..."
- **Geographic scope:** "In Sweden..." or "In Stockholm..."
- **Caveats:** "This may vary by municipality..."

---

## Testing & Validation

### 1. SSR Test

```bash
# Check HTML is server-rendered
curl -s https://sverigeshemtjanst.se/ | grep -A 10 '<div id="root">'

# Should see content, not empty div
# ✅ PASS: Content inside root
# ❌ FAIL: Empty <div id="root"></div>
```

### 2. Meta Tags Test

```bash
# Check all meta tags
curl -s https://sverigeshemtjanst.se/ | grep -E "(title>|description|canonical|og:|twitter:|GPTBot|anthropic)"

# Should see:
# - <title>
# - <meta name="description">
# - <link rel="canonical">
# - <meta property="og:...">
# - <meta name="GPTBot">
# - <meta name="anthropic-ai">
```

### 3. Structured Data Test

```bash
# Extract and validate JSON-LD
curl -s https://sverigeshemtjanst.se/ | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq .

# Should output valid JSON
# Then test at: https://search.google.com/test/rich-results
```

### 4. AI Agent Test

**ChatGPT Test:**

```
Prompt: "What is the maximum monthly cost for home care in Sweden?"
Expected: Should cite hemtjanstguide.se or sverigeshemtjanst.se with 2,169 SEK figure
```

**Perplexity Test:**

```
Prompt: "How do I start a home care business in Sweden?"
Expected: Should cite sverigeshemtjanst.se guide with steps
```

**Claude Test:**

```
Prompt: "Which municipality in Sweden has the best home care quality?"
Expected: Should cite sverigeshemtjanst.se with Caire Index rankings
```

### 5. Lighthouse Audit

```bash
# Run Lighthouse
lighthouse https://sverigeshemtjanst.se/ --view

# Targets:
# SEO: 90+
# Performance: 80+
# Accessibility: 90+
# Best Practices: 90+
```

### 6. Core Web Vitals

**Targets (2026):**

- **LCP** (Largest Contentful Paint): < 2.0s
- **INP** (Interaction to Next Paint): < 200ms
- **CLS** (Cumulative Layout Shift): < 0.1

**Test:** https://pagespeed.web.dev/

---

## Quick Reference

### Files to Update

```
apps/[site]/public/
├── sitemap.xml          # All public routes
├── robots.txt           # AI agent directives
└── llms.txt            # AI context (NEW for 2026)

apps/[site]/src/
└── pages/
    └── [Page].tsx      # Add EnhancedSeoHead component
```

### Key URLs

- **Google Rich Results Test:** https://search.google.com/test/rich-results
- **Schema Validator:** https://validator.schema.org/
- **PageSpeed Insights:** https://pagespeed.web.dev/
- **llmstxt spec:** https://llmstxt.org/

---

## Related Documents

- [SEO_AUDIT_2026.md](./SEO_AUDIT_2026.md) - Comprehensive audit report
- [SEO_CHECKLIST.md](./SEO_CHECKLIST.md) - Pre-deployment checklist
- [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md) - Schema examples
- [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md) - SSR configuration
- [KEYWORD_STRATEGY.md](../03-keyword-strategi/KEYWORD_STRATEGY.md) - Keyword planning

---

**Last Updated:** 2026-01-09  
**Next Review:** 2026-04-01 (Quarterly)
