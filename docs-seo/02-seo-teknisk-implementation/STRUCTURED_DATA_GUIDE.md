# Structured Data Implementation Guide

> **Last updated:** January 2025

## Overview

This guide describes how to implement structured data (JSON-LD schema markup) for SEO and AI agent optimization in AppCaire SEO sites.

---

## Apps Using Structured Data

| App               | Schema Types                                  |
| ----------------- | --------------------------------------------- |
| eirtech           | Organization, WebSite                         |
| hemtjanstguide    | WebSite, Article, FAQPage, BreadcrumbList     |
| nackahemtjanst    | LocalBusiness, WebSite                        |
| sverigeshemtjanst | Organization, WebSite, LocalBusiness, Article |
| website           | Organization, WebSite, Product, FAQPage       |

---

## Base Pattern

### Injection via SEO Component

```typescript
import SEO from "@/components/SEO";

const MyPage = () => {
  const schema = {
    "@context": "https://schema.org",
    "@type": "WebPage",
    name: "Page Name",
    description: "Description",
  };

  return (
    <>
      <SEO
        title="Page Title"
        description="Description"
        structuredData={schema}
      />
      {/* Page content */}
    </>
  );
};
```

### Multiple Schemas

```typescript
const schemas = [
  {
    "@context": "https://schema.org",
    "@type": "Organization",
    name: "Home Care Guide",
    // ...
  },
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    name: "Home Care Guide",
    // ...
  },
];

// Wrap in @graph for multiple schemas
const combinedSchema = {
  "@context": "https://schema.org",
  "@graph": schemas,
};

<SEO structuredData={combinedSchema} />
```

---

## Schema Types

### 1. Organization

**Usage:** Homepages, About pages

```typescript
const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://eirtech.ai/#organization",
  name: "EirTech AB",
  alternateName: "EirTech",
  url: "https://eirtech.ai",
  logo: {
    "@type": "ImageObject",
    url: "https://eirtech.ai/logo.png",
    width: 200,
    height: 60,
  },
  description: "AI-driven technology for home care scheduling",
  foundingDate: "2020",
  address: {
    "@type": "PostalAddress",
    streetAddress: "Sveavägen 1",
    addressLocality: "Stockholm",
    postalCode: "111 57",
    addressCountry: "SE",
  },
  contactPoint: {
    "@type": "ContactPoint",
    telephone: "+46-8-123-456-78",
    contactType: "customer service",
    availableLanguage: ["Swedish", "English"],
  },
  sameAs: [
    "https://www.linkedin.com/company/eirtech",
    "https://twitter.com/eirtech",
  ],
};
```

---

### 2. WebSite (with SearchAction)

**Usage:** Homepages

```typescript
const websiteSchema = {
  "@context": "https://schema.org",
  "@type": "WebSite",
  "@id": "https://hemtjanstguide.se/#website",
  name: "Home Care Guide",
  url: "https://hemtjanstguide.se",
  description: "Sweden's guide to finding home care",
  publisher: {
    "@id": "https://hemtjanstguide.se/#organization",
  },
  potentialAction: {
    "@type": "SearchAction",
    target: {
      "@type": "EntryPoint",
      urlTemplate: "https://hemtjanstguide.se/search?q={search_term_string}",
    },
    "query-input": "required name=search_term_string",
  },
  inLanguage: "sv-SE",
};
```

---

### 3. Article

**Usage:** Guides, blog posts, information pages

```typescript
const articleSchema = {
  "@context": "https://schema.org",
  "@type": "Article",
  "@id": "https://hemtjanstguide.se/guides/apply#article",
  headline: "How to Apply for Home Care",
  description: "Step-by-step guide for applying for home care.",
  image: "https://hemtjanstguide.se/images/apply-guide.jpg",
  datePublished: "2025-01-02T00:00:00+01:00",
  dateModified: "2025-01-02T00:00:00+01:00",
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
  mainEntityOfPage: {
    "@type": "WebPage",
    "@id": "https://hemtjanstguide.se/guides/apply",
  },
  wordCount: 1500,
  articleSection: "Guides",
  keywords: ["home care", "application", "assistance decision"],
};
```

---

### 4. FAQPage

**Usage:** FAQ sections

```typescript
const faqSchema = {
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://hemtjanstguide.se/#faq",
  mainEntity: [
    {
      "@type": "Question",
      name: "How much does home care cost?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Home care typically costs between 200-400 SEK per hour, depending on municipality and scope of services.",
      },
    },
    {
      "@type": "Question",
      name: "How long does it take to get home care?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "Processing time varies between 2-4 weeks depending on municipality and complexity of application.",
      },
    },
    {
      "@type": "Question",
      name: "Can I choose which home care provider I want?",
      acceptedAnswer: {
        "@type": "Answer",
        text: "In municipalities with LOV (Freedom of Choice Act), you can freely choose among approved providers.",
      },
    },
  ],
};
```

---

### 5. BreadcrumbList

**Usage:** Articles and subpages

```typescript
const breadcrumbSchema = {
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  itemListElement: [
    {
      "@type": "ListItem",
      position: 1,
      name: "Home",
      item: "https://hemtjanstguide.se",
    },
    {
      "@type": "ListItem",
      position: 2,
      name: "Guides",
      item: "https://hemtjanstguide.se/guides",
    },
    {
      "@type": "ListItem",
      position: 3,
      name: "Apply for Home Care",
      item: "https://hemtjanstguide.se/guides/apply",
    },
  ],
};
```

---

### 6. LocalBusiness (Home Care Provider)

**Usage:** sverigeshemtjanst provider pages

```typescript
const localBusinessSchema = {
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "@id": "https://sverigeshemtjanst.se/provider/example-ab#business",
  name: "Example Home Care AB",
  description: "Home care provider in Stockholm with focus on quality.",
  image: "https://sverigeshemtjanst.se/logos/example.png",
  url: "https://sverigeshemtjanst.se/provider/example-ab",
  telephone: "+46-8-123-456-78",
  email: "info@example-homecare.se",
  address: {
    "@type": "PostalAddress",
    streetAddress: "Home Street 10",
    addressLocality: "Stockholm",
    postalCode: "111 22",
    addressCountry: "SE",
  },
  geo: {
    "@type": "GeoCoordinates",
    latitude: 59.3293,
    longitude: 18.0686,
  },
  areaServed: [
    {
      "@type": "City",
      name: "Stockholm",
    },
    {
      "@type": "City",
      name: "Solna",
    },
  ],
  priceRange: "$$",
  openingHours: "Mo-Fr 07:00-17:00",
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: "4.5",
    reviewCount: "120",
  },
};
```

---

### 7. Product (SaaS Product)

**Usage:** caire.se product pages

```typescript
const productSchema = {
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "@id": "https://www.caire.se/#product",
  name: "Caire",
  applicationCategory: "BusinessApplication",
  operatingSystem: "Web",
  description: "AI-driven scheduling for home care",
  url: "https://www.caire.se",
  screenshot: "https://www.caire.se/images/screenshot.png",
  offers: {
    "@type": "Offer",
    price: "0",
    priceCurrency: "SEK",
    description: "Contact us for pricing",
  },
  aggregateRating: {
    "@type": "AggregateRating",
    ratingValue: "4.8",
    reviewCount: "25",
  },
  featureList: [
    "AI scheduling",
    "Route optimization",
    "Mobile app",
    "API integrations",
  ],
};
```

---

## Validation

### Tools

1. **Google Rich Results Test**  
   [https://search.google.com/test/rich-results](https://search.google.com/test/rich-results)

2. **Schema Markup Validator**  
   [https://validator.schema.org/](https://validator.schema.org/)

3. **JSON-LD Playground**  
   [https://json-ld.org/playground/](https://json-ld.org/playground/)

### Command

```bash
# Extract and validate structured data
curl -s https://example.com | grep -oP '(?<=type="application/ld\+json">).*(?=</script>)' | jq .
```

---

## Best Practices

### 1. Use @id for Linking

```typescript
// Define organization once
const org = {
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  name: "Example",
};

// Reference with @id
const article = {
  "@type": "Article",
  author: { "@id": "https://example.com/#organization" },
};
```

### 2. Dates in ISO 8601

```typescript
datePublished: "2025-01-02T00:00:00+01:00",
dateModified: "2025-01-02T12:00:00+01:00",
```

### 3. Images

- Always include `image` property
- At least 1200x630 px
- WebP or JPEG

### 4. Combine schemas with @graph

```typescript
{
  "@context": "https://schema.org",
  "@graph": [
    { "@type": "Organization", ... },
    { "@type": "WebSite", ... },
    { "@type": "WebPage", ... }
  ]
}
```

---

## Related Documents

- [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md)
- [SEO_CHECKLIST.md](./SEO_CHECKLIST.md)
- [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md)
