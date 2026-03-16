# SEO Optimization Guide

## Overview

This guide covers SEO best practices for Caire pages, ensuring optimal visibility and ranking. It includes both technical implementation details and content strategy guidelines. For detailed content generation instructions and master prompts, refer to [SEO Context Guide](../seo-context.md).

## Content Generation

For generating new content:

1. Use the master prompt from [SEO Context Guide](../seo-context.md)
2. Follow the content type specifications
3. Adapt the structure template for your content type
4. Use the provided example as reference

## Content Strategy

### Target Audience

- Small to medium-sized private home care companies in Sweden (fewer than 500 employees)
- Companies without dedicated IT departments
- Decision-makers looking for efficiency improvements

### Market Context

Include these key statistics in content when relevant:

1. Market Size:
   - Total home care market: 80 billion SEK annually
   - Administrative costs: 30 billion SEK (40% of total)
   - Transport costs: 4.2 billion SEK annually

2. Industry Challenges:
   - Aging Population: 25% over 65 by 2030, rising to 40% by 2050
   - Staff Shortage: 150,000 new care workers needed by 2030
   - Current Status: 70% of companies report weekly staff shortages
   - Administrative Burden: 40% of work time spent on administration

### Product Features to Highlight

1. Administrative Automation:
   - Automated deviation reports
   - Journal documentation
   - Billing linked to correct client/staff
   - Elimination of double data entry

2. Real-time AI Scheduling:
   - Instant schedule updates
   - Automatic staff notifications
   - Integration with existing systems
   - Smart staff allocation

3. Route Optimization:
   - Geographic considerations
   - Traffic pattern analysis
   - Resource optimization
   - Environmental impact reduction

4. Data-driven Insights:
   - Staff efficiency metrics
   - Revenue and billable hours
   - Staffing needs forecasts
   - Transport cost analysis
   - Capacity warnings

### Key Topics and Keywords

1. Primary Keywords:
   - AI-baserad schemaläggning
   - Ruttoptimering hemtjänst
   - Kritisk personalbrist
   - Hållbar välfärd
   - Minimera administration hemtjänst
   - Digital transformation i vården

2. Secondary Keywords:
   - Hemtjänstbolag
   - Automatisering administration
   - Schemaläggning realtid
   - Personaleffektivitet
   - Ruttplanering
   - Vårdkvalitet

### Content Guidelines

1. Tone and Style:
   - Professional but accessible
   - Friendly and trustworthy
   - Solution-focused
   - Clear and concise
   - Swedish language 1st priority, english 2nd

2. Content Structure:
   - Clear introduction addressing industry challenges
   - Solution-focused main content
   - Specific examples and use cases
   - Clear call-to-action
   - Supporting statistics and data

3. Key Messages:
   - Automation reduces administrative costs
   - Real-time scheduling improves efficiency
   - Route optimization reduces travel time and costs
   - Better work environment leads to lower staff turnover
   - Data-driven insights improve decision-making

## Technical Implementation

### Meta Tags Implementation

#### Basic Meta Tags

```typescript
<Helmet>
  <title>Page Title | Caire</title>
  <meta name="description" content="Clear, concise description of the page content" />
  <meta name="keywords" content="relevant, comma-separated, keywords" />
  <meta name="author" content="Caire" />
  <meta name="robots" content="index, follow" />
  <link rel="canonical" href="https://caire.se/your-path" />
</Helmet>
```

#### Open Graph Tags

```typescript
<Helmet>
  <meta property="og:title" content="Page Title | Caire" />
  <meta property="og:description" content="Clear, concise description" />
  <meta property="og:image" content="https://caire.se/images/og-image.jpg" />
  <meta property="og:url" content="https://caire.se/your-path" />
  <meta property="og:type" content="website" />
  <meta property="og:site_name" content="Caire" />
</Helmet>
```

#### Twitter Card Tags

```typescript
<Helmet>
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Page Title | Caire" />
  <meta name="twitter:description" content="Clear, concise description" />
  <meta name="twitter:image" content="https://caire.se/images/twitter-card.jpg" />
</Helmet>
```

## Content Structure

### Semantic HTML

1. Use proper heading hierarchy:

```typescript
<h1>Page Title</h1>
<section>
  <h2>Section Title</h2>
  <h3>Subsection Title</h3>
</section>
```

2. Use semantic elements:

```typescript
<header>
<main>
<article>
<section>
<aside>
<footer>
<nav>
```

### Content Guidelines

1. Text Content:
   - Clear, descriptive headings in Swedish
   - Concise paragraphs
   - Bullet points for lists
   - Natural keyword usage
   - Industry-specific terminology
   - Supporting statistics and data

2. Images:

```typescript
<img
  src="/path/to/image.jpg"
  alt="Descriptive alt text in Swedish"
  width="800"
  height="600"
  loading="lazy"
/>
```

## Performance Optimization

### Image Optimization

1. Use next-gen formats:
   - WebP with fallback
   - Responsive images
   - Proper sizing

```typescript
<picture>
  <source srcSet="/image.webp" type="image/webp" />
  <source srcSet="/image.jpg" type="image/jpeg" />
  <img
    src="/image.jpg"
    alt="Description"
    loading="lazy"
  />
</picture>
```

### Loading Optimization

1. Implement lazy loading:

```typescript
const HeavyComponent = lazy(() => import('./HeavyComponent'));

// Usage
<Suspense fallback={<LoadingSkeleton />}>
  <HeavyComponent />
</Suspense>
```

2. Prioritize critical content:

```typescript
<link rel="preload" href="/critical.css" as="style" />
<link rel="preload" href="/hero-image.jpg" as="image" />
```

## URL Structure

1. Use SEO-friendly URLs in Swedish:
   - Descriptive
   - Kebab-case
   - Include relevant keywords
   - Keep it short

Example:

```
/tjanster/hemtjanst/stockholm
/funktioner/schema-optimering
/losningar/ai-schemaläggning
```

## Structured Data

Add relevant schema markup:

```typescript
<Helmet>
  <script type="application/ld+json">
    {JSON.stringify({
      "@context": "https://schema.org",
      "@type": "WebPage",
      "name": "Page Title",
      "description": "Page description",
      "url": "https://caire.se/your-path",
      "inLanguage": "sv-SE",
      // Add more relevant schema properties
    })}
  </script>
</Helmet>
```

## Analytics and Monitoring

1. Track key metrics:

```typescript
useEffect(() => {
  trackPageView("/your-path", "Page Title");
  trackEvent("page_section_view", {
    section: "hero",
    page: "/your-path",
  });
}, []);
```

2. Monitor performance:
   - Core Web Vitals
   - Page load time
   - Time to interactive
   - User engagement metrics
   - Conversion tracking

## Content Creation Process

1. **Research Phase**
   - Identify target keywords
   - Analyze competitor content
   - Gather industry statistics
   - Define content goals

2. **Content Planning**
   - Create content outline
   - Define key messages
   - Plan supporting media
   - Set success metrics

3. **Content Writing**
   - Write in Swedish
   - Follow tone guidelines
   - Include target keywords
   - Add relevant statistics
   - Include clear CTAs

4. **Content Review**
   - Check keyword usage
   - Verify facts and statistics
   - Review tone and style
   - Ensure mobile readability

## Checklist

Before deployment:

### Technical SEO

- [ ] Meta tags implemented
- [ ] Open Graph tags added
- [ ] Twitter Card tags added
- [ ] Semantic HTML used
- [ ] Images optimized
- [ ] Alt text added
- [ ] Structured data implemented
- [ ] URLs SEO-friendly
- [ ] Analytics tracking set up
- [ ] Performance optimized
- [ ] Schema markup added

### Content SEO

- [ ] Content in Swedish
- [ ] Target keywords included
- [ ] Clear heading hierarchy
- [ ] Industry statistics used
- [ ] CTAs implemented
- [ ] Mobile-friendly layout
- [ ] Internal links added
- [ ] External references linked
- [ ] Content goals defined
- [ ] Success metrics set

## Verification Tools

1. Test implementation with:
   - Google Search Console
   - Google Mobile-Friendly Test
   - PageSpeed Insights
   - Schema Validator
   - Meta Tag Validator
   - Swedish language checker

## Common Issues

1. **Missing Meta Tags**
   - Use meta tag checker
   - Verify all required tags
   - Check content length
   - Ensure Swedish language tag

2. **Poor Performance**
   - Optimize images
   - Implement lazy loading
   - Minimize bundle size
   - Check mobile performance

3. **Content Issues**
   - Check keyword density
   - Verify heading hierarchy
   - Ensure mobile readability
   - Validate Swedish language
   - Check content relevance

## Next Steps

1. Implement all SEO elements
2. Test with verification tools
3. Monitor performance
4. Track rankings and metrics
5. Review content performance
6. Update based on analytics

## Page Audit Template

Use this template to audit existing pages:

```markdown
# SEO Audit: [Page Name]

## Meta Tags

- [ ] Title tag present and optimized
- [ ] Meta description present and compelling
- [ ] Open Graph tags implemented
- [ ] Twitter Card tags implemented
- [ ] Canonical URL set
- [ ] Swedish language tag set

## Content Structure

- [ ] Clear H1 heading in Swedish
- [ ] Proper heading hierarchy
- [ ] Semantic HTML elements
- [ ] Alt text on images in Swedish
- [ ] Target keywords included
- [ ] Industry statistics present
- [ ] Clear CTAs implemented
```

## Resources

1. SEO Context Document
   - [SEO Context Guide](../seo-context.md)
   - Contains detailed information about target audience, messaging, and content strategy

2. Style Guide
   - Swedish language guidelines
   - Tone and voice guidelines
   - Content structure templates

3. Analytics
   - Performance tracking setup
   - Conversion tracking
   - User behavior analysis
