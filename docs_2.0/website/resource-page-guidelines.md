# Resource Page Guidelines

## Overview

This document outlines the patterns and best practices for creating resource pages in the Caire platform, incorporating learnings from implementation and error resolution.

## File Structure

A resource page requires three main files:

1. A markdown file in `src/content/articles/` containing the content and metadata
2. A React component in `src/pages/Resurser/` for rendering
3. Metadata entry in `src/utils/article-utils.ts`

### Markdown Content Structure

```markdown
---
title: "Article Title"
description: "Article description"
date: "DD månad YYYY"
category: "Guide | Artikel | AI | Trender | Implementation"
readingTime: "X min"
---

# Title of the Article

Introduction paragraph...

## Section Heading

Content...

[Internal Link Example](/funktioner/feature-name)
[External Link Example](https://external-site.com){:target="\_blank" rel="noopener noreferrer"}
```

Key points for markdown files:

- Use Swedish language throughout
- Include frontmatter with metadata
- External links should include `{:target="_blank" rel="noopener noreferrer"}`
- Internal links should use relative paths starting with `/`
- Demo/contact links should point to `/kontakt`
- Dates should be in format "DD månad YYYY" (e.g., "9 januari 2025")
- Categories must match those defined in `article-utils.ts`

### Article Metadata

The `article-utils.ts` file serves as a central registry for article metadata:

```typescript
const articleMetadata: Record<string, Omit<Article, "href" | "icon">> = {
  "article-slug": {
    title: "Article Title",
    description: "Article description",
    date: "DD månad YYYY",
    readingTime: "X min",
    category: "Category",
  },
};
```

Important:

- Dates in metadata must match markdown frontmatter
- Categories must have corresponding icons in `iconMap`
- Slugs must match file names without extension

### React Component Structure

```typescript
import { Helmet } from 'react-helmet-async';
import { ErrorBoundary } from 'react-error-boundary';
import { useEffect, useState } from 'react';
import { Container } from '@/components/ui/container';
import { Button } from '@/components/ui/button';
import { Link as RouterLink } from 'react-router-dom';
import { formatDate } from '@/lib/utils';
import { motion } from 'framer-motion';
import { FadeInSection } from '@/components/animations/FadeInSection';
import { FloatingElement } from '@/components/animations/FloatingElement';
import { usePageTracking } from '@/hooks/usePageTracking';
import { useSeo } from '@/hooks/use-seo';
import ReactMarkdown from 'react-markdown';
import { loadMarkdownContent } from '@/utils/markdown-loader';

// Required icons based on category
import {
  Brain, // AI
  ClipboardList, // Guide
  FileText, // Artikel
  Settings, // Implementation
  TrendingUp, // Trender
  // ... other utility icons
} from 'lucide-react';

// Component structure:
1. Error boundary
2. SEO metadata
3. Page layout
   - Header with floating elements
   - Back button
   - Main content with markdown
   - Sidebar with:
     - Quick links
     - Key statistics
     - CTA section
```

## Error Handling

Common errors and solutions:

1. **FileText is not defined**
   - Ensure all required icons are imported from lucide-react
   - Add icon to iconMap in article-utils.ts

2. **Date inconsistencies**
   - Use markdown file as single source of truth
   - Ensure dates match between:
     - Markdown frontmatter
     - article-utils.ts metadata
     - Component publishDate

3. **Missing ErrorFallback**
   - Always include ErrorBoundary component
   - Implement user-friendly error message
   - Provide navigation back to resources

## SEO Configuration

```typescript
const structuredData = {
  "@context": "https://schema.org",
  "@type": "Article", // or "TechArticle", "HowTo" based on content
  name: "Article Title",
  description: "Article description",
  datePublished: publishDate.toISOString(),
  author: {
    "@type": "Organization",
    name: "Caire",
    url: "https://caire.se",
  },
  publisher: {
    "@type": "Organization",
    name: "Caire",
    logo: {
      "@type": "ImageObject",
      url: "https://caire.se/images/logo.png",
    },
  },
  mainEntityOfPage: {
    "@type": "WebPage",
    "@id": "https://caire.se/resurser/article-slug",
  },
  keywords: ["keyword1", "keyword2"],
  inLanguage: "sv-SE",
};
```

## Analytics Integration

```typescript
// Track page view
usePageTracking("Article Title");

// Track content visibility
const contentRef = useRef(null);
const isVisible = useInView(contentRef);

useEffect(() => {
  if (isVisible) {
    trackEvent("article_content_view", {
      article: "Article Title",
      category: "Category",
    });
  }
}, [isVisible]);
```

## Styling Guidelines

1. Use Tailwind classes consistently:
   - Dark theme with black background
   - White/gray text hierarchy
   - Primary color for accents
   - Consistent spacing

2. Animations:
   - FadeInSection for page sections
   - FloatingElement for decorative icons
   - Motion transitions for text and lists
   - Consider reduced motion preferences

3. Typography:
   - Use proper heading hierarchy
   - Consistent text sizes and weights
   - Adequate line height for readability
   - Proper link styling

4. Layout:
   - Responsive grid system
   - Proper spacing between sections
   - Consistent sidebar positioning
   - Mobile-first approach

## Best Practices

1. Content Organization:
   - Keep markdown clean and structured
   - Use consistent heading levels
   - Organize content logically
   - Include clear call-to-actions

2. Performance:
   - Lazy load images
   - Optimize animations
   - Implement proper error boundaries
   - Monitor loading performance

3. Accessibility:
   - Proper ARIA attributes
   - Semantic HTML structure
   - Keyboard navigation
   - Screen reader support

4. Maintenance:
   - Keep metadata in sync
   - Regular content updates
   - Monitor analytics
   - Test all interactive elements

## Testing

1. Unit Tests:
   - Test component rendering
   - Verify error boundaries
   - Check markdown parsing
   - Validate date formatting

2. Integration Tests:
   - Test navigation flow
   - Verify analytics tracking
   - Check SEO metadata
   - Validate structured data

3. E2E Tests:
   - Test user journey
   - Verify responsive layout
   - Check accessibility
   - Validate links and CTAs

```

```
