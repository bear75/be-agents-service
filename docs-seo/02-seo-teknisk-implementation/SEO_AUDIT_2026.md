# Comprehensive SEO Audit 2026 - AppCaire SEO Sites

> **Audit Date:** 2026-01-09  
> **Auditor:** AI SEO Specialist  
> **Scope:** All 4 SEO sites + eirtech.ai  
> **Focus:** SSR, Meta Tags, Structured Data, AI/Agentic Search Optimization

---

## Executive Summary

### Overall Status: ⚠️ **GOOD with Required Improvements**

| Site                     | SSR Status | Meta Tags  | Structured Data | Sitemap     | Robots.txt      | Priority    |
| ------------------------ | ---------- | ---------- | --------------- | ----------- | --------------- | ----------- |
| **sverigeshemtjanst.se** | ✅ Working | ⚠️ Partial | ❌ Missing      | ⚠️ Outdated | ✅ Good         | 🔴 CRITICAL |
| **hemtjanstguide.se**    | ✅ Working | ⚠️ Partial | ❌ Missing      | ✅ Good     | ⚠️ Needs update | 🔴 HIGH     |
| **nackahemtjanst.se**    | ⚠️ Partial | ⚠️ Partial | ❌ Missing      | ⚠️ Minimal  | ⚠️ Needs update | 🟡 MEDIUM   |
| **eirtech.ai**           | ✅ Working | ✅ Good    | ⚠️ Partial      | ❌ Minimal  | ⚠️ Needs update | 🟢 LOW      |

### Key Findings

**✅ Strengths:**

- SSR implementation is functional for sverigeshemtjanst.se and hemtjanstguide.se
- Basic meta tags are present on most pages
- Robots.txt includes AI agent directives
- Sitemap structure exists for major sites

**❌ Critical Issues:**

1. **Missing Structured Data (JSON-LD)** - No schema markup on most pages
2. **Incomplete Meta Tags** - Missing AI agent meta directives, keywords optimization
3. **Outdated Sitemaps** - Missing new routes (/kunskap pages, /anordnare, /topplistor)
4. **No AI/Agentic Search Optimization** - Missing llms.txt, entity extraction, answer-focused content
5. **Inconsistent SEO Component Usage** - Some pages use SEO component, others don't

---

## 1. Site-by-Site Detailed Audit

### 1.1 SverigesHemtjänst.se (B2B Portal)

#### Current Routes (from App.tsx)

**Public Routes:**

- ✅ `/` - LandingPage
- ✅ `/kommuner` - MunicipalityIndex
- ✅ `/kommuner/:slug` - MunicipalityDashboard
- ✅ `/kommuner/:slug/anordnare` - ProviderListing
- ✅ `/anordnare` - ProviderListing (NEW ROUTE ❌ Not in sitemap)
- ✅ `/anordnare/:slug` - ProviderDetail (NEW ROUTE ❌ Not in sitemap)
- ✅ `/topplistor` - TopListsLanding (NEW ROUTE ❌ Not in sitemap)
- ✅ `/topplistor/anordnare` - TopLists (NEW ROUTE ❌ Not in sitemap)
- ✅ `/topplistor/kommuner` - TopListsMunicipalities (NEW ROUTE ❌ Not in sitemap)
- ✅ `/topplistor/metodik` - CaireIndexMethodology (✅ In sitemap)
- ✅ `/kunskap` - KnowledgeHome (NEW ROUTE ❌ Not in sitemap)
- ✅ `/kunskap/ai-schemalaggning` - AISchemalaggning
- ✅ `/kunskap/roi-kalkylator` - ROIKalkylator
- ✅ `/kunskap/beslutsfattare` - Beslutsfattare
- ✅ `/kunskap/systemguiden` - Systemguiden
- ✅ `/kunskap/api-integrationer` - APIIntegrationer
- ✅ `/kunskap/starta-hemtjanstforetag` - StartaHemtjanstforetag (NEW PAGE ✅ Has SEO)
- ✅ `/kunskap/hemtjanst-lonsamhet` - HemtjanstLonsamhet (NEW PAGE ✅ Has SEO)
- ✅ `/kunskap/digitaliseringen-av-hemtjansten` - DigitaliseringenHemtjanst (NEW PAGE ✅ Has SEO)
- ✅ `/kunskap/framtidens-hemtjanst-nya-sol` - FramtidensHemtjanstNyaSol (NEW PAGE ✅ Has SEO)
- ✅ `/sverige` - NationalPrognosis
- ✅ `/om-oss` - AboutUs
- ✅ `/datakallor` - DataSources
- ✅ `/data` - DataDashboard

**Legacy Routes (Redirects):**

- `/innovation/*` → `/kunskap` ✅
- `/regioner/*` → `/kommuner` ✅
- `/nationell-prognos` → `/sverige` ✅

#### Sitemap Issues

**Current Sitemap (sverigeshemtjanst/public/sitemap.xml):**

- ❌ Uses OLD `/regioner/stockholm` paths (should be `/kommuner/stockholm`)
- ❌ Uses OLD `/innovation/*` paths (should be `/kunskap/*`)
- ❌ Missing NEW `/kunskap` overview page
- ❌ Missing NEW `/anordnare` routes
- ❌ Missing NEW `/topplistor` routes
- ✅ Has `/topplistor/metodik` but missing other topplists pages
- ✅ Has most knowledge articles but with OLD `/innovation` prefix

#### Meta Tags Audit

**Example: LandingPage.tsx**

```typescript
<SeoHead
  title="Sveriges Hemtjänst | Hemtjänstmarknadens data- och kunskapsportal"
  description="Sveriges ledande data- och kunskapsportal för hemtjänstbranschen. Marknadsinformation, kvalitetsdata och AI-driven innovation för beslutsfattare."
  canonicalUrl="https://sverigeshemtjanst.se/"
  schemaMarkup={combinedSchema}
  keywords={[...]} // ✅ Keywords present
/>
```

**✅ Strengths:**

- Uses `SeoHead` component (react-helmet-async)
- Has structured data (Organization + WebSite schema)
- Has canonical URLs
- Has keywords array

**❌ Issues:**

- No AI agent meta directives (GPTBot, anthropic-ai, PerplexityBot)
- No Twitter Card tags
- Missing Open Graph image URLs on some pages
- No entity markup for answer extraction

#### Structured Data Audit

**✅ Good:**

- Homepage has Organization + WebSite schema
- Uses `generateArticleSchema` helper

**❌ Missing:**

- LocalBusiness schema for provider pages (`/anordnare/:slug`)
- FAQPage schema (no FAQ sections)
- BreadcrumbList schema for deep pages
- HowTo schema for guides
- ItemList schema for /topplistor pages

#### Keywords & Content Optimization

**Target Keywords from KEYWORD_STRATEGY.md:**
| Keyword | Priority | Current Status | Recommendation |
|---------|----------|----------------|----------------|
| starta hemtjänstföretag | 🔴 HIGH | ✅ Has page `/kunskap/starta-hemtjanstforetag` | Optimize title for "Starta Hemtjänstföretag 2026" |
| hemtjänst lönsamhet | 🔴 HIGH | ✅ Has page `/kunskap/hemtjanst-lonsamhet` | Add calculator/interactive tool |
| bästa hemtjänstsystem | 🔴 HIGH | ⚠️ Has `/kunskap/systemguiden` | Optimize for "bästa" keyword |
| hemtjänst ersättning [kommun] | 🟠 MED | ⚠️ Has kommun pages | Add dedicated `/kommuner/:slug/ersattning` subpages |
| LOV hemtjänst | 🟠 MED | ⚠️ Mentioned | Create dedicated LOV guide |
| IVO hemtjänst | 🟠 MED | ❌ Missing | Create IVO guide page |

---

### 1.2 HemtjänstGuide.se (Consumer Guide)

#### Current Routes (from App.tsx)

**Public Routes:**

- ✅ `/` - Home
- ✅ `/sverige` - Sverige (national stats)
- ✅ `/hitta-hemtjanst` - HittaHemtjanst (search hub)
- ✅ `/hitta-hemtjanst/:municipalitySlug` - HittaMunicipality (NEW DYNAMIC ✅ In sitemap)
- ✅ `/hitta-hemtjanst/:municipalitySlug/:providerSlug` - ProviderPage
- ✅ `/guider` - Guider (guides hub)
- ✅ `/guider/ansoka-hemtjanst` - AnsokaHemtjanst
- ✅ `/guider/rattigheter` - Rattigheter
- ✅ `/guider/valja-utforare` - ValjaUtforare
- ✅ `/guider/byta-hemtjanst` - BytaHemtjanst (NEW PAGE ❌ Not in sitemap)
- ✅ `/guider/basta-hemtjanst` - BastaHemtjanst (NEW PAGE ❌ Not in sitemap)
- ✅ `/ekonomi` - Ekonomi
- ✅ `/ekonomi/forsakringskassan` - Forsakringskassan
- ✅ `/ekonomi/fonder` - Fonder
- ✅ `/ekonomi/avgifter` - Avgifter
- ✅ `/hjalpmedel` - Hjalpmedel
- ✅ `/hjalpmedel/anpassning-hemmet` - AnpassaHemmet
- ✅ `/hjalpmedel/trygghetslarm` - Trygghetslarm
- ✅ `/hjalpmedel/valfardsteknik` - Valfardsteknik
- ✅ `/jamforelser` - Jamforelser
- ✅ `/jamforelser/hemtjanst-vs-assistans` - HemtjanstVsAssistans
- ✅ `/jamforelser/hemsjukvard` - Hemsjukvard
- ✅ `/jamforelser/sarskilt-boende` - SarskiltBoende
- ✅ `/jamfor-utforare/moderna-system` - ModernaSytem
- ✅ `/jamfor-utforare/caire-certifierad` - CaireCertifierad
- ✅ `/om-oss` - OmOss

#### Sitemap Issues

**Current Sitemap (hemtjanstguide/public/sitemap.xml):**

- ✅ Has top 50 municipalities in `/hitta-hemtjanst/:slug` format
- ❌ Missing `/guider/byta-hemtjanst` (NEW PAGE)
- ❌ Missing `/guider/basta-hemtjanst` (NEW PAGE)
- ❌ Missing `/jamfor-utforare` hub page
- ⚠️ Has `/jamfor-utforare/*` subpages but no main page

#### Meta Tags Audit

**❌ Issues:**

- Uses old `SEO` component (not `SeoHead`)
- No structured data on most pages
- Missing AI agent meta directives
- No keywords array
- Limited Open Graph images

#### Keywords & Content Optimization

**Target Keywords from TARGETED_KEYWORDS.md:**
| Keyword | Priority | Current Status | Recommendation |
|---------|----------|----------------|----------------|
| byta hemtjänst | 🟠 HIGH | ✅ Has `/guider/byta-hemtjanst` | Add to sitemap, optimize meta |
| sveriges bästa hemtjänst | 🟠 HIGH | ✅ Has `/guider/basta-hemtjanst` | Add to sitemap, optimize for "bästa hemtjänst Sverige" |
| hemtjänst [stad] | 🟡 MED | ✅ Has dynamic pages | Ensure all top 100 municipalities in sitemap |
| ansöka hemtjänst | 🟡 MED | ✅ Has guide | Add step-by-step schema markup |
| vad kostar hemtjänst | 🟡 MED | ⚠️ Mentioned | Create dedicated cost calculator page |

---

### 1.3 NackaHemtjanst.se (Local Nacka Guide)

#### Sitemap Issues

**Current Sitemap (nackahemtjanst/public/sitemap.xml):**

- ⚠️ Very minimal (only 6 URLs)
- ❌ Missing local area pages (Saltsjöbaden, Fisksätra, Sickla)
- ❌ Missing provider pages

#### Keywords & Content Optimization

**Target Keywords from TARGETED_KEYWORDS.md:**
| Keyword | Priority | Current Status | Recommendation |
|---------|----------|----------------|----------------|
| hemtjänst Saltsjöbaden | 🟡 LOW | ❌ Missing | Create local area page |
| hemtjänst Fisksätra | 🟡 LOW | ❌ Missing | Create local area page |
| hemtjänst Sickla | 🟡 LOW | ❌ Missing | Create local area page |
| Nackamodellen | 🟢 | ⚠️ Mentioned | Optimize dedicated page |
| bästa hemtjänst Nacka | 🟢 | ⚠️ Partial | Add "bästa" keyword to titles |

---

### 1.4 EirTech.ai (Corporate Site)

#### Sitemap Issues

**Current Sitemap (eirtech/public/sitemap.xml):**

- ⚠️ Minimal (3 URLs: /, /privacy-policy, /terms)
- ❌ Missing /produkter, /om-oss, /kontakt

#### Meta Tags Audit

**✅ Good:**

- Has custom SEO component
- Uses react-helmet-async

**❌ Issues:**

- Minimal sitemap
- No structured data beyond basic WebSite schema

---

## 2. AI/Agentic Search Optimization (2026 Best Practices)

### 2.1 Current Status: ❌ **NOT IMPLEMENTED**

**What is Agentic Search?**
Agentic search refers to AI assistants (ChatGPT, Claude, Perplexity, Gemini) that crawl websites to answer user questions. In 2026, this is a major traffic source.

### 2.2 Required Implementations

#### A. llms.txt File (CRITICAL)

**Status:** ❌ Missing on all sites

**What:** A text file at `/llms.txt` that provides structured information for AI agents.

**Example for sverigeshemtjanst.se:**

```txt
# Sveriges Hemtjänst - LLM Context

## Overview
Sveriges Hemtjänst is Sweden's leading B2B knowledge portal for home care decision-makers.

## Key Data
- 290 municipalities covered
- 1000+ home care providers tracked
- Updated daily with IVO, Kolada, and financial data

## Primary Topics
1. Home care market analysis by municipality
2. Provider quality rankings (Caire Index)
3. AI scheduling and optimization tools
4. LOV (Freedom of Choice) regulations
5. Home care reimbursement models

## Key Pages
- /kommuner - All municipalities with market data
- /topplistor - Provider and municipality rankings
- /kunskap/starta-hemtjanstforetag - Guide to starting home care business
- /kunskap/systemguiden - Comparison of home care software systems
- /anordnare - Provider directory

## Expertise Areas
- Home care market dynamics
- Quality measurement (Caire Index methodology)
- Financial analysis of providers
- Regulatory compliance (IVO, LOV)
- Digital transformation in elderly care

## Contact
- Website: https://sverigeshemtjanst.se
- Email: info@eirtech.ai
- Parent company: EirTech AB

## Data Sources
- IVO (Inspektionen för vård och omsorg)
- Kolada (municipal statistics)
- Bolagsverket (company registry)
- Sveriges Kommuner och Regioner (SKR)

## Updates
This data is updated daily. Last major update: 2026-01-09
```

**Recommendation:** Create llms.txt for all 4 sites following above pattern.

#### B. Entity Markup (CRITICAL)

**Status:** ❌ Not implemented

**What:** Structured data that helps AI extract specific entities (prices, dates, statistics).

**Example additions needed:**

```typescript
// Provider page - add PriceSpecification
{
  "@type": "LocalBusiness",
  "priceRange": "$$",
  "makesOffer": {
    "@type": "Offer",
    "itemOffered": {
      "@type": "Service",
      "name": "Hemtjänst",
      "serviceType": "Home Care Services"
    },
    "areaServed": {
      "@type": "City",
      "name": "Stockholm"
    }
  }
}

// Article page - add speakable sections for voice search
{
  "@type": "Article",
  "speakable": {
    "@type": "SpeakableSpecification",
    "cssSelector": [".summary", ".key-points"]
  }
}
```

#### C. Answer-Focused Content (HIGH PRIORITY)

**Status:** ⚠️ Partial - Some pages have good Q&A format

**What:** Content structured to directly answer questions AI agents ask.

**Examples of good patterns:**

```markdown
# How Much Does Home Care Cost in Stockholm?

## Quick Answer

Home care in Stockholm typically costs between 250-400 SEK per hour in 2026, depending on the type of service and time of day.

## Detailed Breakdown

- Daytime personal care: 280 SEK/hour
- Evening/weekend: 350 SEK/hour
- Night care: 400 SEK/hour
- Municipal subsidies: Up to 75% covered for low-income seniors

## Who Pays?

...
```

**Recommendation:** Restructure all guide pages to follow this Q&A format with clear headings.

#### D. FAQ Schema Markup (HIGH PRIORITY)

**Status:** ❌ Not implemented

**What:** FAQPage schema for pages with Q&A sections.

**Example:**

```typescript
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "Hur mycket kostar hemtjänst i Stockholm?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Hemtjänst i Stockholm kostar mellan 250-400 kr/timme beroende på tid och tjänst. Kommunen täcker ofta 75% av kostnaden för låginkomsttagare.",
      },
    },
  ],
};
```

#### E. Meta Tags for AI Agents (CRITICAL)

**Status:** ⚠️ Partial - robots.txt has AI agent directives, but meta tags missing

**Required meta tags for EVERY page:**

```html
<!-- AI Agent Directives -->
<meta
  name="robots"
  content="index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
/>
<meta name="googlebot" content="index, follow" />
<meta name="bingbot" content="index, follow" />
<meta name="GPTBot" content="index, follow" />
<meta name="ChatGPT-User" content="index, follow" />
<meta name="anthropic-ai" content="index, follow" />
<meta name="Claude-Web" content="index, follow" />
<meta name="PerplexityBot" content="index, follow" />
<meta name="CCBot" content="index, follow" />
<meta name="Google-Extended" content="index, follow" />
<meta name="Applebot-Extended" content="index, follow" />

<!-- Content Classification for AI -->
<meta name="subject" content="Home Care Services, Elderly Care" />
<meta name="classification" content="Business" />
<meta name="coverage" content="Sweden" />
<meta name="target" content="decision-makers, seniors, families" />
```

---

## 3. Updated SEO Component Implementation

### 3.1 Current SEO Component Status

**SverigesHemtjänst.se:** ✅ Uses `SeoHead` component (react-helmet-async)
**HemtjänstGuide.se:** ⚠️ Uses old `SEO` component (needs upgrade)
**NackaHemtjänst.se:** ⚠️ Uses old `SEO` component (needs upgrade)
**EirTech.ai:** ✅ Has custom SEO component

### 3.2 Recommended Enhanced SEO Component

Create new `EnhancedSeoHead` component at `packages/shared/seo/components/shared/EnhancedSeoHead.tsx`:

```typescript
import { Helmet } from "react-helmet-async";

interface EnhancedSeoHeadProps {
  // Required
  title: string;
  description: string;
  canonicalUrl: string;

  // Optional but recommended
  keywords?: string[];
  ogImage?: string;
  ogType?: "website" | "article";
  twitterCard?: "summary" | "summary_large_image";
  schemaMarkup?: object | object[];

  // AI/Agentic Search (NEW for 2026)
  aiAgentIndex?: boolean; // Default true
  contentClassification?: string; // e.g., "Business Guide"
  targetAudience?: string; // e.g., "decision-makers, seniors"
  coverage?: string; // e.g., "Sweden"
  publishDate?: string; // ISO 8601
  modifiedDate?: string; // ISO 8601
  author?: string;

  // Voice Search Optimization (NEW for 2026)
  speakable?: string[]; // CSS selectors for speakable content

  // Entity Extraction Hints (NEW for 2026)
  entities?: {
    type: "Person" | "Organization" | "Place" | "Product" | "Service";
    name: string;
  }[];
}

export const EnhancedSeoHead: React.FC<EnhancedSeoHeadProps> = ({
  title,
  description,
  canonicalUrl,
  keywords = [],
  ogImage = "https://www.caire.se/og-image.jpg",
  ogType = "website",
  twitterCard = "summary_large_image",
  schemaMarkup,
  aiAgentIndex = true,
  contentClassification,
  targetAudience,
  coverage = "Sweden",
  publishDate,
  modifiedDate,
  author,
  speakable,
  entities,
}) => {
  // Construct full schema with entities
  const fullSchema = schemaMarkup ? (
    Array.isArray(schemaMarkup) ? schemaMarkup : [schemaMarkup]
  ) : [];

  // Add entity mentions if provided
  if (entities && entities.length > 0) {
    fullSchema.push({
      "@context": "https://schema.org",
      "@type": "WebPage",
      "mentions": entities.map(entity => ({
        "@type": entity.type,
        "name": entity.name,
      })),
    });
  }

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      <link rel="canonical" href={canonicalUrl} />

      {/* Keywords (still useful for internal search) */}
      {keywords.length > 0 && (
        <meta name="keywords" content={keywords.join(", ")} />
      )}

      {/* Open Graph */}
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      <meta property="og:url" content={canonicalUrl} />
      <meta property="og:image" content={ogImage} />
      <meta property="og:type" content={ogType} />
      <meta property="og:locale" content="sv_SE" />

      {/* Twitter Card */}
      <meta name="twitter:card" content={twitterCard} />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      <meta name="twitter:image" content={ogImage} />

      {/* AI Agent Directives (2026) */}
      <meta name="robots" content={`index, follow, max-snippet:-1, max-image-preview:large${aiAgentIndex ? "" : ", noai"}`} />
      <meta name="googlebot" content="index, follow" />
      <meta name="bingbot" content="index, follow" />
      {aiAgentIndex && (
        <>
          <meta name="GPTBot" content="index, follow" />
          <meta name="ChatGPT-User" content="index, follow" />
          <meta name="anthropic-ai" content="index, follow" />
          <meta name="Claude-Web" content="index, follow" />
          <meta name="PerplexityBot" content="index, follow" />
          <meta name="CCBot" content="index, follow" />
          <meta name="Google-Extended" content="index, follow" />
          <meta name="Applebot-Extended" content="index, follow" />
        </>
      )}

      {/* Content Classification for AI (2026) */}
      {contentClassification && (
        <meta name="classification" content={contentClassification} />
      )}
      {targetAudience && (
        <meta name="target" content={targetAudience} />
      )}
      <meta name="coverage" content={coverage} />

      {/* Article Metadata */}
      {publishDate && <meta property="article:published_time" content={publishDate} />}
      {modifiedDate && <meta property="article:modified_time" content={modifiedDate} />}
      {author && <meta name="author" content={author} />}

      {/* Structured Data */}
      {fullSchema.length > 0 && (
        <script type="application/ld+json">
          {JSON.stringify(
            fullSchema.length === 1 ? fullSchema[0] : {
              "@context": "https://schema.org",
              "@graph": fullSchema,
            }
          )}
        </script>
      )}
    </Helmet>
  );
};
```

---

## 4. Critical Action Items (Prioritized)

### Phase 1: Critical Fixes (Week 1) 🔴

**1.1 Update Sitemaps (ALL SITES)**

- [ ] **sverigeshemtjanst.se** - Add all new /kunskap pages, /anordnare routes, /topplistor routes
- [ ] **hemtjanstguide.se** - Add /guider/byta-hemtjanst, /guider/basta-hemtjanst
- [ ] **nackahemtjanst.se** - Add local area pages
- [ ] **eirtech.ai** - Add missing pages

**1.2 Add AI Agent Meta Directives (ALL PAGES)**

- [ ] Update SeoHead component with AI agent meta tags
- [ ] Add to all page components

**1.3 Create llms.txt Files (ALL SITES)**

- [ ] sverigeshemtjanst.se
- [ ] hemtjanstguide.se
- [ ] nackahemtjanst.se
- [ ] eirtech.ai

### Phase 2: Structured Data (Week 2) 🟠

**2.1 Add Core Schemas**

- [ ] LocalBusiness schema for provider pages (`/anordnare/:slug`)
- [ ] FAQPage schema for guides with Q&A sections
- [ ] BreadcrumbList schema for deep pages
- [ ] Article schema for all knowledge/guide pages

**2.2 Add Entity Markup**

- [ ] PriceSpecification for cost pages
- [ ] Place entities for municipality pages
- [ ] Organization entities for provider pages

### Phase 3: Content Optimization (Week 3) 🟡

**3.1 Restructure Key Pages for AI**

- [ ] Convert guide pages to Q&A format with clear headings
- [ ] Add "Quick Answer" sections at top of articles
- [ ] Add data tables for numerical info (costs, statistics)

**3.2 Add Missing Content**

- [ ] IVO guide page (sverigeshemtjanst.se)
- [ ] LOV guide page (sverigeshemtjanst.se)
- [ ] Cost calculator page (hemtjanstguide.se)
- [ ] Local area pages (nackahemtjanst.se)

### Phase 4: Testing & Validation (Week 4) 🟢

**4.1 SEO Testing**

- [ ] Run Lighthouse audits (target: 90+ SEO score)
- [ ] Validate structured data with Google Rich Results Test
- [ ] Test meta tags with Facebook Debugger, Twitter Card Validator
- [ ] Check sitemap.xml in Google Search Console

**4.2 AI Agent Testing**

- [ ] Test with ChatGPT: "What is the best home care in Uppsala?"
- [ ] Test with Perplexity: "How much does home care cost in Stockholm?"
- [ ] Test with Claude: "How do I start a home care business in Sweden?"
- [ ] Verify answers cite our sites correctly

---

## 5. Updated Robots.txt Template (2026)

```txt
# Robots.txt for [SITE] - Updated 2026-01-09
# https://[domain]

# Allow all search engines
User-agent: *
Allow: /
Disallow: /api/
Disallow: /admin/
Disallow: /partner/

# Explicit AI Agent Permissions (2026 Update)
# GPT-based agents
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

# Claude (Anthropic)
User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

# Common Crawl (used by many AI models)
User-agent: CCBot
Allow: /

# Google's AI training
User-agent: Google-Extended
Allow: /

# Perplexity
User-agent: PerplexityBot
Allow: /

# Apple Intelligence
User-agent: Applebot-Extended
Allow: /

# Cohere
User-agent: cohere-ai
Allow: /

# Meta AI
User-agent: Meta-ExternalAgent
Allow: /

# Bing AI
User-agent: Bingbot
Allow: /

# Yandex
User-agent: YandexBot
Allow: /

# Sitemap
Sitemap: https://[domain]/sitemap.xml

# LLM Context (2026 standard)
# See https://llmstxt.org/
Allow: /llms.txt
```

---

## 6. Performance & Technical SEO

### 6.1 SSR Status

**✅ Working:**

- sverigeshemtjanst.se
- hemtjanstguide.se
- eirtech.ai

**⚠️ Needs Verification:**

- nackahemtjanst.se

**Test Command:**

```bash
curl -s https://sverigeshemtjanst.se/ | grep -A 10 '<div id="root">'
# Should see rendered HTML content, not empty div
```

### 6.2 Core Web Vitals Targets (2026)

| Metric                              | Target  | Priority    |
| ----------------------------------- | ------- | ----------- |
| **LCP** (Largest Contentful Paint)  | < 2.0s  | 🔴 CRITICAL |
| **INP** (Interaction to Next Paint) | < 200ms | 🔴 CRITICAL |
| **CLS** (Cumulative Layout Shift)   | < 0.1   | 🟡 HIGH     |
| **FCP** (First Contentful Paint)    | < 1.5s  | 🟡 HIGH     |
| **TTFB** (Time to First Byte)       | < 600ms | 🟡 HIGH     |

**Note:** FID (First Input Delay) has been replaced by INP in 2024/2026.

### 6.3 Bundle Size Optimization

**Current Status:** Unknown (need to measure)

**Targets:**

- Initial JS bundle: < 200 KB (gzipped)
- Total page size: < 1.5 MB
- CSS: < 100 KB (gzipped)

**Recommended Tools:**

```bash
# Analyze bundle size
yarn workspace sverigeshemtjanst build --analyze

# Check gzipped sizes
du -sh apps/sverigeshemtjanst/dist/**/*.{js,css} | gzip -c | wc -c
```

---

## 7. Mobile SEO

### 7.1 Mobile-First Indexing

**Status:** ✅ All sites are responsive

**Required:**

- [ ] Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] Touch targets: Minimum 44px x 44px
- [ ] Readable text: Minimum 16px font size
- [ ] No horizontal scrolling

### 7.2 Mobile Performance

**Targets:**

- Mobile Lighthouse score: 80+
- Mobile LCP: < 2.5s
- Mobile INP: < 200ms

---

## 8. Security & HTTPS

### 8.1 HTTPS Status

**✅ All sites use HTTPS**

**Required Headers:**

```
Strict-Transport-Security: max-age=31536000; includeSubDomains
X-Content-Type-Options: nosniff
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## 9. International SEO (Future)

### 9.1 Current Status

- [ ] All sites are Swedish only (lang="sv")
- [ ] No hreflang tags (not needed currently)

### 9.2 If Expanding to Other Countries

```html
<link rel="alternate" hreflang="sv" href="https://hemtjanstguide.se/" />
<link rel="alternate" hreflang="en" href="https://hemtjanstguide.se/en/" />
<link rel="alternate" hreflang="x-default" href="https://hemtjanstguide.se/" />
```

---

## 10. Monitoring & Analytics

### 10.1 Required Tools

**✅ Google Analytics 4** (Check if installed)
**✅ Google Search Console** (Check if sites are verified)
**❌ Google Tag Manager** (Recommended)
**❌ Plausible/Fathom** (Privacy-friendly alternative)

### 10.2 Key Metrics to Track

**SEO Metrics:**

- Organic traffic by page
- Top performing keywords
- Average position in SERP
- Click-through rate (CTR)
- Core Web Vitals

**AI Agent Metrics (NEW for 2026):**

- Referrals from ChatGPT, Claude, Perplexity
- "Zero-click searches" (AI answered without click)
- Citation frequency in AI responses

---

## 11. Recommended SEO Tools Stack

| Tool                        | Purpose                       | Priority    |
| --------------------------- | ----------------------------- | ----------- |
| **Google Search Console**   | Track search performance      | 🔴 CRITICAL |
| **Google Analytics 4**      | Track user behavior           | 🔴 CRITICAL |
| **Screaming Frog**          | Technical SEO audits          | 🟡 HIGH     |
| **Ahrefs/SEMrush**          | Keyword research, backlinks   | 🟡 HIGH     |
| **Lighthouse CI**           | Automated performance testing | 🟡 HIGH     |
| **Schema Markup Validator** | Validate structured data      | 🟡 HIGH     |

---

## 12. Summary of Key Changes for 2026

### New in 2026 SEO:

1. **AI/Agentic Search Optimization** - llms.txt, entity markup, answer-focused content
2. **Voice Search Optimization** - Speakable schema, conversational Q&A format
3. **Interaction to Next Paint (INP)** - Replaced FID for Core Web Vitals
4. **Entity-based SEO** - Focus on structured entities, not just keywords
5. **Zero-click SERP optimization** - Content that answers questions directly in AI tools
6. **Multi-modal search** - Images, videos, and text combined in search results

### Deprecated/Less Important:

1. ~~Keyword density~~ - Now about entity relevance
2. ~~Meta keywords tag~~ - Not used by major search engines
3. ~~PageRank~~ - Replaced by more complex authority metrics
4. ~~Exact match domains~~ - Less important than brand authority

---

## Conclusion

### Overall Assessment: ⚠️ **GOOD FOUNDATION, NEEDS 2026 UPDATES**

**Strengths:**

- SSR is working on main sites
- Basic meta tags are present
- Sitemap and robots.txt structure exists
- Content quality is high

**Critical Gaps:**

- No AI/agentic search optimization
- Missing structured data on most pages
- Outdated sitemaps missing new routes
- No llms.txt files
- Limited entity markup

**Estimated Time to Fix:**

- Phase 1 (Critical): 1 week
- Phase 2 (Structured Data): 1 week
- Phase 3 (Content): 1 week
- Phase 4 (Testing): 1 week

**Total:** 4 weeks to full 2026 SEO compliance

---

**Next Steps:**

1. Review this audit with team
2. Prioritize Phase 1 critical fixes
3. Create tickets for each action item
4. Set up monitoring in Google Search Console
5. Schedule weekly check-ins to track progress

---

_Audit completed: 2026-01-09_  
_Next audit recommended: 2026-04-01 (quarterly)_
