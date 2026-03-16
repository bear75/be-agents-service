# SEO Component Guide

> **Last updated:** January 2025

## Overview

This guide describes how to use SEO components with `react-helmet-async` to manage meta tags, structured data, and AI agent optimization.

---

## React Helmet Async

### Installation

```bash
yarn add react-helmet-async
```

### Provider Setup

Wrap your app with `HelmetProvider`:

```typescript
// entry-server.tsx (SSR)
import { HelmetProvider } from "react-helmet-async";

const helmetContext = {};

<HelmetProvider context={helmetContext}>
  <App />
</HelmetProvider>

// entry-client.tsx (Client)
import { HelmetProvider } from "react-helmet-async";

<HelmetProvider>
  <App />
</HelmetProvider>
```

---

## SEO Component Pattern

### Base Component

```typescript
// src/components/SEO.tsx
import { Helmet } from "react-helmet-async";

interface SEOProps {
  title: string;
  description: string;
  canonical?: string;
  ogImage?: string;
  type?: "website" | "article";
  structuredData?: object;
  keywords?: string[];
  noindex?: boolean;
}

/**
 * SEO component for managing meta tags
 * @param title - Page title (50-60 characters)
 * @param description - Meta description (150-160 characters)
 * @param canonical - Canonical URL
 * @param ogImage - Open Graph image URL
 * @param type - Content type for Open Graph
 * @param structuredData - JSON-LD schema markup
 * @param keywords - Keywords for AI agents
 * @param noindex - Set to true to prevent indexing
 */
const SEO = ({
  title,
  description,
  canonical,
  ogImage,
  type = "website",
  structuredData,
  keywords,
  noindex = false,
}: SEOProps) => {
  const robotsContent = noindex
    ? "noindex, nofollow"
    : "index, follow, max-image-preview:large, max-snippet:-1";

  return (
    <Helmet>
      {/* Basic Meta Tags */}
      <title>{title}</title>
      <meta name="description" content={description} />
      {canonical && <link rel="canonical" href={canonical} />}

      {/* Keywords (for AI agents) */}
      {keywords && <meta name="keywords" content={keywords.join(", ")} />}

      {/* Robots Directives */}
      <meta name="robots" content={robotsContent} />
      <meta name="googlebot" content={robotsContent} />
      <meta name="bingbot" content={robotsContent} />

      {/* AI Agent Directives */}
      <meta name="GPTBot" content="index, follow" />
      <meta name="ChatGPT-User" content="index, follow" />
      <meta name="CCBot" content="index, follow" />
      <meta name="anthropic-ai" content="index, follow" />
      <meta name="Claude-Web" content="index, follow" />
      <meta name="PerplexityBot" content="index, follow" />

      {/* Open Graph */}
      <meta property="og:type" content={type} />
      <meta property="og:title" content={title} />
      <meta property="og:description" content={description} />
      {canonical && <meta property="og:url" content={canonical} />}
      {ogImage && <meta property="og:image" content={ogImage} />}
      <meta property="og:locale" content="sv_SE" />

      {/* Twitter Card */}
      <meta name="twitter:card" content="summary_large_image" />
      <meta name="twitter:title" content={title} />
      <meta name="twitter:description" content={description} />
      {ogImage && <meta name="twitter:image" content={ogImage} />}

      {/* Structured Data (JSON-LD) */}
      {structuredData && (
        <script type="application/ld+json">
          {JSON.stringify(structuredData)}
        </script>
      )}
    </Helmet>
  );
};

export default SEO;
```

---

## Usage Per Page

### Simple Page

```typescript
import SEO from "@/components/SEO";

const HomePage = () => {
  return (
    <>
      <SEO
        title="Home Care Guide - Find Home Care in Sweden"
        description="Compare and find home care providers in your municipality. Free guide to home care, applications, and rights."
        canonical="https://hemtjanstguide.se/"
      />
      <main>
        <h1>Welcome to the Home Care Guide</h1>
        {/* ... */}
      </main>
    </>
  );
};
```

### With Structured Data

```typescript
import SEO from "@/components/SEO";

const GuideArticle = () => {
  const articleSchema = {
    "@context": "https://schema.org",
    "@type": "Article",
    headline: "How to Apply for Home Care",
    description: "Step-by-step guide to applying for home care.",
    datePublished: "2025-01-02",
    dateModified: "2025-01-02",
    author: {
      "@type": "Organization",
      name: "Home Care Guide",
      url: "https://hemtjanstguide.se",
    },
    publisher: {
      "@type": "Organization",
      name: "Home Care Guide",
      logo: {
        "@type": "ImageObject",
        url: "https://hemtjanstguide.se/logo.png",
      },
    },
  };

  return (
    <>
      <SEO
        title="How to Apply for Home Care | Home Care Guide"
        description="Complete guide for applying for home care in your municipality."
        canonical="https://hemtjanstguide.se/guides/apply"
        type="article"
        structuredData={articleSchema}
        keywords={[
          "apply home care",
          "home care application",
          "assistance decision",
          "home care municipality",
        ]}
      />
      <article>
        <h1>How to Apply for Home Care</h1>
        {/* ... */}
      </article>
    </>
  );
};
```

### With FAQ Schema

```typescript
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  mainEntity: [
    {
      "@type": "Question",
      name: "How much does home care cost?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Home care typically costs between 200-400 SEK per hour...",
      },
    },
    {
      "@type": "Question",
      name: "How do I apply for home care?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "You apply for home care by contacting your municipality...",
      },
    },
  ],
};

<SEO
  title="Frequently Asked Questions About Home Care | FAQ"
  description="Answers to the most common questions about home care."
  structuredData={faqSchema}
/>
```

---

## AI Agent Optimization

### Why AI Agent Directives?

Modern AI search engines (ChatGPT, Perplexity, Claude) crawl the web to:

1. Train their models
2. Provide real-time answers to questions
3. Cite sources in answers

### Meta Tags for AI

```html
<!-- Allow all AI crawlers -->
<meta name="GPTBot" content="index, follow" />
<meta name="ChatGPT-User" content="index, follow" />
<meta name="CCBot" content="index, follow" />
<meta name="anthropic-ai" content="index, follow" />
<meta name="Claude-Web" content="index, follow" />
<meta name="PerplexityBot" content="index, follow" />
```

### robots.txt for AI

```txt
# robots.txt
User-agent: *
Allow: /

# Explicit AI agent permissions
User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: anthropic-ai
Allow: /

User-agent: Claude-Web
Allow: /

User-agent: PerplexityBot
Allow: /

User-agent: CCBot
Allow: /

Sitemap: https://example.com/sitemap.xml
```

---

## Title & Description Best Practices

### Title Tags

| Rule                  | Example                                     |
| --------------------- | ------------------------------------------- |
| 50-60 characters      | ✅ "Home Care Stockholm - Find Providers"   |
| Primary keyword first | ✅ "Home Care Nacka \| Compare Providers"   |
| Include brand         | ✅ "Apply for Home Care \| Home Care Guide" |

### Meta Descriptions

| Rule               | Example                                            |
| ------------------ | -------------------------------------------------- |
| 150-160 characters | ✅ Complete sentence summarizing the page          |
| Include CTA        | ✅ "...Compare and find the right provider today." |
| Natural keyword    | ✅ Integrate the search term naturally             |

---

## Structured Data Types

### WebSite (Homepage)

```javascript
{
  "@context": "https://schema.org",
  "@type": "WebSite",
  name: "Home Care Guide",
  url: "https://hemtjanstguide.se",
  potentialAction: {
    "@type": "SearchAction",
    target: "https://hemtjanstguide.se/search?q={search_term_string}",
    "query-input": "required name=search_term_string"
  }
}
```

### Organization

```javascript
{
  "@context": "https://schema.org",
  "@type": "Organization",
  name: "EirTech AB",
  url: "https://eirtech.ai",
  logo: "https://eirtech.ai/logo.png",
  sameAs: [
    "https://linkedin.com/company/eirtech",
    "https://twitter.com/eirtech"
  ]
}
```

### LocalBusiness (Home Care Provider)

```javascript
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://hemtjanstguide.se/provider/example",
  name: "Example Home Care AB",
  address: {
    "@type": "PostalAddress",
    streetAddress: "Example Street 1",
    addressLocality: "Stockholm",
    postalCode: "111 22",
    addressCountry: "SE"
  },
  telephone: "+46-8-123-456-78",
  areaServed: {
    "@type": "City",
    name: "Stockholm"
  }
}
```

### BreadcrumbList

```javascript
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    {
      "@type": "ListItem",
      position: 1,
      name: "Home",
      item: "https://hemtjanstguide.se"
    },
    {
      "@type": "ListItem",
      position: 2,
      name: "Guides",
      item: "https://hemtjanstguide.se/guides"
    },
    {
      "@type": "ListItem",
      position: 3,
      name: "Apply for Home Care",
      item: "https://hemtjanstguide.se/guides/apply"
    }
  ]
}
```

---

## Canonical URLs

### Important

Always include canonical URL to avoid duplicate content:

```typescript
<SEO
  canonical="https://hemtjanstguide.se/guides/apply"
  // ... other props
/>
```

### Rules

- Always use HTTPS
- Include full URL (not relative)
- Self-referencing canonical on all pages
- Choose one "master" URL for multiple versions

---

## Verification

### Test with curl

```bash
# Verify SSR meta tags
curl -s https://example.com | head -100
```

### Google Rich Results Test

[https://search.google.com/test/rich-results](https://search.google.com/test/rich-results)

### Schema Markup Validator

[https://validator.schema.org/](https://validator.schema.org/)

---

## Related Documents

- [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md) - SSR implementation
- [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md) - Deeper guide on schema
- [SITEMAP_ROBOTS.md](./SITEMAP_ROBOTS.md) - Sitemap and robots.txt
