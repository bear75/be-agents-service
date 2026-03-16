# SEO Site Structure Implementation - Quick Start Prompt

Use this prompt when starting a new session to continue implementation of the SEO site structure:

```
I'm working on implementing a new SEO-optimized site structure for the CAIRE website. We're adding new pages based on content in the docs/SEO-content-pages/ directory and updating site navigation. The goal is to improve Google indexing and address previous verification failures.

We've already created some pages (`For-verksamheten.tsx`, `Features/RouteOptimization.tsx`) and are following the plan in `docs/SEO-site-structure-implementation-plan.md`.

I need help with [continuing to implement the SEO site structure according to the plan / specific task].

Key requirements for all new pages:
- Use PageSeo component with proper metadata
- Include translated content with i18n
- Follow styling guidelines from frontend-guidelines.md
- Ensure mobile responsiveness
- Update sitemap after page creation
```

# Current Progress (Updated: May 2023)

## Implemented Pages

- **Home Page**: `/src/pages/Index.tsx` - Added SEO content from `home.md`
- **For-verksamheten**: `/src/pages/For-verksamheten.tsx` - Business benefits page
- **RouteOptimizationHomeCare**: `/src/pages/Features/RouteOptimizationHomeCare.tsx` - Route optimization feature page for home care with SEO optimization
- **Products Overview**: `/src/pages/Produkter.tsx` - Products overview page

## Fixed Issues

- **Duplicate Footer**: Fixed the duplicate footer issue by ensuring the Layout component is only applied once in the component hierarchy
- **URL Structure**: Fixed incorrect URLs in the footer navigation for resources section
- **Missing Translations**: Added missing translations for footer elements in both English and Swedish locales
- **Missing Icons**: Created placeholder icons for business areas and route optimization
- **Footer Navigation**: Updated footer with proper section organization and translations for all links

## Recent Improvements

- **Complete Footer Translations**: Added all missing translation strings in both English and Swedish locale files for the footer section
- **Internal Linking**: Improved footer navigation with properly localized paths using the getLocalizedPath helper function
- **Localization Support**: Enhanced i18n implementation for consistent multilingual support across the site

## Lessons Learned

### Styling Guidelines

When implementing new SEO content pages, it's crucial to follow these styling guidelines:

1. **Use the Dark Theme**:
   - Dark background (`bg-black`)
   - Green accent colors (`text-[#00FF7F]`)
   - White/gray text (`text-white`, `text-gray-300`)
2. **Component Styling**:
   - Cards should use `bg-black/40 backdrop-blur-sm` for semi-transparent background
   - Borders should be subtle with `border-white/10` and hover effect `hover:border-[#00FF7F]/20`
   - Add subtle glows with `hover:shadow-[0_0_30px_rgba(0,255,127,0.1)]`
   - Use `rounded-lg` for consistent border radius
3. **Section Structure**:
   - Wrap sections in `<FadeInSection>` for animation effects
   - Use gradient backgrounds with `bg-[radial-gradient(circle_at_center,rgba(0,255,127,0.15),transparent_70%)]`
   - Maintain consistent spacing with `py-16 lg:py-24` for vertical padding

4. **Typography**:
   - Headings: `text-3xl lg:text-4xl font-bold text-white mb-6`
   - Body text: `text-lg text-gray-300`
   - Accent text: `text-[#00FF7F]`

5. **Layout Structure**:
   - Don't include `<Layout>` in individual pages - it's already provided by the `LayoutWrapper` in App.tsx
   - Always implement proper SEO components (PageSeo, JsonLd)

### Page Implementation Workflow

1. Create the new page component following the pattern of existing SEO-optimized pages
2. Add routes to the page in App.tsx for both Swedish and English paths
3. Add any necessary images or assets to the public directory
4. Update translation strings in `sv.json` and `en.json`
5. Test the page to ensure proper styling, content, and navigation

### Running the SEO Checker Script

To verify your SEO implementations, run the SEO checker script:

```bash
node scripts/seo-page-checker.js
```

This script checks for:

- Proper SEO metadata
- Canonical URLs
- Required JSON-LD structured data
- Proper heading hierarchy
- Alt text for images

Fix any issues reported by the script before considering the page complete.

# Overview

The goal of this plan is to implement a comprehensive SEO site structure for CAIRE based on the content files in docs/SEO-content-pages/. This will improve Google indexing and provide valuable content for potential customers.

# Implementation Progress Update (May 2025)

## Completed Pages

- ✅ For-verksamheten (Business Benefits)
- ✅ Features/RouteOptimizationHomeCare - Implemented route optimization feature page
- ✅ Produkter (Products Overview)
- ✅ Updated Footer Navigation with complete translations
- ✅ Features/AiStaffPlanning - Implemented AI staff planning feature page
- ✅ Features/AiSchedulingCarefox - Implemented AI scheduling with Carefox integration page
- ✅ Features/OnboardingCaireCarefox - Implemented onboarding CAIRE with Carefox page
- ✅ vanliga-fragor - Implemented FAQ page with proper structure and translations
- ✅ Updated Navigation with featured dropdown menus for Resources section
- ✅ Updated internal linking between feature pages and FAQ

## Current Focus

- 🔄 Preparing for Resources pages implementation (starting tomorrow)
- 🔄 Planned sections: Articles, Guides, Comparisons, Personas

## Next Steps (Starting May 20, 2025)

1. Implement Resources landing page with proper sections
2. Create Articles section and first key article pages
3. Implement Guides section with implementation guides
4. Create Comparisons section for product feature comparison
5. Develop Personas pages targeting specific user roles
6. Continue enhancing internal linking structure

## Navigation Structure Updates

- ✅ Implemented Resources dropdown in main navigation
- ✅ Added FAQ link to both footer and Resources dropdown
- ✅ Enhanced Features dropdown with additional feature pages
- ✅ Improved footer organization with logical category sections
- ✅ Ensured proper translations for all navigation elements

## SEO Optimizations Completed

- ✅ Fixed JSON-LD structured data implementation across pages
- ✅ Added proper meta descriptions, titles, and keywords
- ✅ Ensured consistent heading hierarchy (h1, h2, h3)
- ✅ Added semantic HTML structure
- ✅ Verified canonical URLs
- ✅ Implemented proper OpenGraph tags

## Critical Lessons Learned

### Styling Issues

Every new page we've created initially had incorrect white styling instead of the required dark theme. This has been a consistent challenge requiring fixes after initial implementation. To avoid this going forward:

1. **ALWAYS use the dark theme for all new pages**
   - Base background: `bg-black`
   - Text colors: `text-white` for primary text, `text-gray-300` for secondary text
   - Accent color: `text-[#00FF7F]` for highlights and interactive elements
   - Cards/sections: `bg-black/40 backdrop-blur-sm` for semi-transparent overlay effects

2. **Always implement 3D card effects and hover animations**
   - Cards should have the hover effect: `hover:border-[#00FF7F]/20 hover:shadow-[0_0_30px_rgba(0,255,127,0.1)]`
   - Elements should scale subtly on hover: `hover:scale-[1.02]`
   - Text should transition color on hover: `group-hover:text-[#00FF7F]`

3. **Maintain consistent gradient backgrounds**
   - Use radial gradients for section backgrounds: `bg-[radial-gradient(circle_at_center,rgba(0,255,127,0.1),transparent_70%)]`
   - Apply subtle glow effects behind important elements

### Dashboard and Data Visualization

We've learned important lessons about visualizing data effectively:

1. **Modern Dashboard Best Practices**
   - Avoid pie charts in favor of more readable bar charts, stat cards, and visual comparisons
   - Use clear, high-contrast color schemes (light elements on dark backgrounds)
   - Include clear labels and percentages on all data points
   - Add comparison markers (% improvement, increase/decrease indicators)
   - Organize information in logical, scannable card layouts
   - Use the recharts library for consistent chart implementations

2. **Data Presentation Guidelines**
   - Always show before/after comparisons when demonstrating improvements
   - Include explicit % improvement calculations for key metrics
   - Use consistent color coding (green for positive, neutral for before/baseline)
   - Add interactive elements like tooltips for additional information
   - Include a clear legend and explanatory text for context

3. **Stat Card Design Pattern**
   - Implement a consistent StatCard component for all feature pages
   - Include icon, title, value, description, and change percentage
   - Use visual indicators (up/down arrows) for change direction
   - Apply consistent border styling and accent colors

### Content Strategy Issues

1. **Client Case Studies**
   - Remove specific client references (e.g., Motala, Södertälje) when not ready for public visibility
   - Replace with anonymized or generalized examples
   - Add placeholder sections for future case studies when they're ready for publication

2. **Translation Consistency**
   - Ensure all text strings use proper i18n translation functions
   - Verify that all CTA buttons and links use consistent translation keys (e.g., t('common:cta.learn_more'))
   - Double-check translation files after page creation to ensure all strings are properly defined
   - Run translation tests to verify proper functioning

3. **Calculator Integration**
   - Consider adding lead magnets like ROI/savings calculators to feature pages
   - Maintain consistent calculator design and styling across sections
   - Integrate calculators that demonstrate value proposition directly to users

### SEO Implementation Issues

Several common SEO issues have been identified across new pages:

1. **Missing or incomplete SEO components**
   - Every page MUST include the PageSeo component with all required props
   - Always include both page-level SEO (meta tags) and structured data (JSON-LD)
   - Missing canonical URLs and alternate language tags

2. **Improper heading hierarchy**
   - Pages frequently missing the required h1 tag
   - Skipping heading levels (e.g., h1 to h3 without h2)
   - Using incorrect heading styles for visual appearance

3. **Incorrect image implementation**
   - Missing alt text on images
   - Images without proper width/height attributes causing layout shifts
   - Non-optimized image sizes

## SEO Checker Instructions

Before submitting a new page for review, ALWAYS run the SEO checker script:

```bash
# Check a specific page by its route path
node scripts/seo-page-checker.js --path=/path-to-page

# Examples:
node scripts/seo-page-checker.js --path=/For-verksamheten
node scripts/seo-page-checker.js --path=/Features/RouteOptimization
```

The script will:

1. Check for proper SEO components (PageSeo, JSON-LD)
2. Verify heading hierarchy (h1, h2, h3)
3. Check image optimization
4. Validate responsive design implementation
5. Generate a report in the `reports/` directory

### Example Output Interpretation

```
=== SEO Checker for /Features/RouteOptimization ===

Running SEO checks...

✓ PageSeo Component: Pass
✓ Meta Title: Pass
✓ Meta Description: Pass
✓ Keywords: Pass
✓ Canonical URL: Pass
✓ JSON-LD Structured Data: Pass
✓ Layout Component: Pass
✓ Image Alt Text: Pass
✓ Translation Support: Pass
⚠ Analytics Tracking: Warning - Analytics tracking should be implemented
✓ Internal Links: Pass

Analyzing content structure...

⚠ Warning: No h1 heading found - Each page should have exactly one h1 heading
✓ Responsive Design: Pass - Page uses responsive Tailwind classes
✓ Semantic HTML: Pass - Found 5 semantic tags

SEO Check Summary:

✓ Passed: 10 checks
⚠ Warnings: 2 issues
✗ Failed: 0 critical issues

⚠ This page has some SEO warnings that should be addressed when possible.
```

### Required Fixes for Common Issues

1. **Missing h1 Tag**
   - Add exactly ONE h1 tag per page
   - If the design doesn't visually show an h1, add a screen-reader-only version: `<h1 className="sr-only">Page Title</h1>`

2. **Missing JSON-LD**
   - Always implement structured data with the JsonLd component:

   ```jsx
   <JsonLd
     type="Service"
     data={% raw %}{
       name: t("page.title"),
       description: t("page.description"),
       provider: {
         "@type": "Organization",
         "name": "Caire"
       }
     }{% endraw %}
   />
   ```

3. **Missing Image Dimensions**
   - Always include width and height attributes:
   ```jsx
   <img
     src="/path/to/image.jpg"
     alt="Descriptive alt text"
     width={600}
     height={400}
   />
   ```

## Essential Styling Checklist

For every new page, ensure these styling elements are implemented:

### Base Layout

```jsx
<Layout>
  <header className="relative w-full sm:w-auto md:max-w-screen-xl lg:mx-auto xl:px-4">
    <h1 className="sr-only">{t("page.title")}</h1>
    {/* Hero section */}
  </header>

  <main className="bg-black">
    <section className="sm:py-12 md:py-16 lg:py-20 w-full sm:w-auto md:max-w-screen-xl lg:mx-auto xl:px-4">
      {/* Section content */}
    </section>

    {/* Additional sections */}
  </main>
</Layout>
```

### Card Styling

```jsx
<div
  className="bg-black/40 backdrop-blur-sm p-6 rounded-lg border border-white/10 
  hover:border-[#00FF7F]/20 hover:shadow-[0_0_30px_rgba(0,255,127,0.1)] transition-all duration-300"
>
  <div className="mb-4 text-[#00FF7F]">{/* Icon */}</div>
  <h3 className="text-xl font-semibold mb-2 text-white">{title}</h3>
  <p className="text-gray-300">{description}</p>
</div>
```

### Gradient Background Section

```jsx
<section className="relative overflow-hidden py-16">
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,127,0.1),transparent_70%)]" />
  <div className="relative z-10 container mx-auto px-4">
    {/* Section content */}
  </div>
</section>
```

# Overview

This document outlines our plan for implementing a new SEO-optimized site structure for the CAIRE website. The goal is to improve Google indexing by updating the site structure and adding new SEO content pages based on the content in the docs/SEO-content-pages/ directory.

## Current Status

- Google indexing issues identified: verification failure
- Gradual increase in indexed pages (from 2-3 in February to 31 by mid-May 2025)
- New Git branch "seo-site-structure-implementation" created for implementation

## SEO Tools and Components

### Available SEO Tools

Our project includes several tools for SEO monitoring and improvement:

1. **Alt Text Checker**: `npm run seo:alt-check` - Scans codebase for images without alt text
2. **Structured Data Validator**: `npm run seo:structured-data` - Validates JSON-LD implementations
3. **Comprehensive SEO Audit**: `npm run seo:audit` - Performs full SEO audit checking alt text, structured data, meta descriptions, etc.
4. **Full SEO Analysis**: `npm run seo:full` - Runs audit plus Lighthouse analysis
5. **Sitemap Generation**: `npm run sitemap` - Updates sitemap.xml with latest content and hreflang support

### Key SEO Components

We have several components for implementing SEO best practices:

1. **PageSeo**: Main component for page-level SEO - includes title, meta description, OpenGraph, Twitter cards, canonical URLs, and hreflang
2. **ArticleSeo**: For article/blog pages - includes all PageSeo features plus article-specific structured data
3. **FaqSeo**: Adds FAQ schema markup to pages with Q&A content
4. **BreadcrumbSeo**: Adds breadcrumb structured data
5. **DefaultSeo**: Site-wide SEO settings (used in main layout)
6. **JsonLd**: Creates JSON-LD structured data
7. **MetaTags**: Alternative to PageSeo for simple meta tag implementation

### SEO Implementation Guidelines

- Every page must use PageSeo or ArticleSeo component
- Configure canonical URLs and hreflang for all pages
- Implement proper JSON-LD structured data
- Ensure meta descriptions are 50-160 characters
- Use descriptive, unique titles for each page
- After creating a page, update the sitemap using the generation script

## Pages to Add

### Primary Structure Pages

- [x] For Business (För verksamheten) - `/For-verksamheten`
- [x] Products Overview - `/Produkter`
- [ ] About Us - `/Om-oss`
- [ ] Contact - `/Kontakt`
- [ ] FAQ - `/FAQ`

### Features Pages

- [x] Route Optimization - `/Features/RouteOptimization`
- [ ] Scheduling - `/Features/Scheduling`
- [ ] Administration - `/Features/Administration`
- [ ] Analytics - `/Features/Analytics`
- [ ] Integrations - `/Features/Integrations`
- [ ] Onboarding - `/Features/Onboarding`
- [ ] AI Staff Planning - `/Features/AiStaffPlanning` (from ai-personalplanering-hemtjanst.md)
- [ ] AI Scheduling with Carefox - `/Features/AiSchedulingCarefox` (from ai-schemalaggning-carefox.md)
- [ ] Onboarding CAIRE-Carefox - `/Features/OnboardingCaireCarefox` (from onboarding-caire-carefox.md)
- [ ] Route Optimization Home Care - `/Features/RouteOptimizationHomeCare` (from ruttoptimering-hemtjanst.md)

### Resources Pages

- [ ] Articles Overview - `/Resurser/Artiklar`
- [ ] Guides Overview - `/Resurser/Guider`
- [ ] Comparisons Overview - `/Resurser/Jamforelser`
- [ ] Personas Overview - `/Resurser/Personas`

#### Articles

- [ ] AI Revolution - `/Resurser/Artiklar/ai-revolution`
- [ ] Future of Home Care - `/Resurser/Artiklar/future-homecare-trends`
- [ ] AI Scheduling Revolution - `/Resurser/Artiklar/ai-schemaläggning-revolution`
- [ ] Step by Step AI Scheduling - `/Resurser/Artiklar/steg-for-steg-ai-schemaläggning`

#### Comparisons

- [ ] Carefox vs CAIRE - `/Resurser/Jamforelser/carefox-caire`
- [ ] Excel vs AI - `/Resurser/Jamforelser/excel-vs-ai`
- [ ] Scheduling Systems Comparison - `/Resurser/Jamforelser/jamforelse-schemalaggningssystem-hemtjanst`

#### Guides

- [ ] Effective Staff Planning - `/Resurser/Guider/effektiv-personalplanering-i-hemtjansten`
- [ ] Preparing for AI in Home Care - `/Resurser/Guider/forberedelser-infor-ai-i-hemtjanste`
- [ ] Optimize Home Care Schedule - `/Resurser/Guider/optimera-hemtjanst-schema`
- [ ] Implementation Guide - `/Resurser/Guider/implementeringsguide`

#### Personas

- [ ] Streamline Home Care with AI - `/Resurser/Personas/effektivisera-hemtjanst-ai`
- [ ] Tools for Home Care Coordinators - `/Resurser/Personas/verktyg-samordnare-hemtjanst`
- [ ] Whitepapers - `/Resurser/whitepapers`

### Legal Pages

- [ ] Privacy Policy - `/Sekretess`
- [ ] Terms of Service - `/Villkor`
- [ ] Cookies Policy - `/Cookies`

## Pages to Update

- [ ] Home Page - `/` - Update to reflect new site structure
- [ ] Main Navigation - Update to include new pages
- [x] Footer Navigation - Updated to include organized links to all major sections
- [ ] Sitemap XML - Add all new pages

## SEO Value

Implementing this site structure will provide several key SEO benefits:

1. **Improved Information Architecture**
   - Clear hierarchical structure helps search engines understand content relationships
   - Logical grouping of related content improves topical relevance

2. **Enhanced Indexability**
   - More entry points for search engine crawlers
   - Better internal linking structure to distribute link equity

3. **Expanded Keyword Coverage**
   - New pages target specific keywords and search intents
   - More opportunities to rank for long-tail keywords

4. **Improved User Experience**
   - Clearer navigation paths for users
   - Content organized by user intent and search behavior

5. **Content Gaps Addressed**
   - New pages fill existing content gaps identified in SEO analysis
   - More comprehensive coverage of topics related to our business

## Internal Linking Strategy

### Current Challenges

- Many of the planned pages do not exist yet
- Internal linking is crucial for SEO and user experience
- We need a phased approach to implement internal links

### Linking Implementation Phases

#### Phase 1: Link to Existing Pages (In Progress)

- ✅ Implement links to all existing pages (For-verksamheten, Features/RouteOptimization, Produkter)
- ✅ Update navigation menus to include links to these pages
- ✅ Add contextual links within content where relevant

#### Phase 2: Progressive Enhancement

- As each new page is created, immediately:
  1. Update navigation and relevant sidebar menus
  2. Add links to the new page from related existing pages
  3. Add links from the new page to existing pages
  4. Update the sitemap.xml

#### Phase 3: Placeholder Management

- For links to pages that don't exist yet, we have two options:
  1. **Delayed Implementation**: Only add links when the target page exists (recommended for initial phases)
  2. **Coming Soon Pages**: Create placeholder pages that announce upcoming content (useful for important sections)

### Internal Linking Best Practices

- Use descriptive anchor text that includes target keywords
- Maintain a natural link density (avoid over-linking)
- Prioritize contextual links within relevant content
- Ensure all key pages are within 3 clicks from the homepage
- Use a hierarchical link structure that matches the site architecture
- Implement bidirectional linking (pages should link to each other when contextually relevant)
- Use call-to-action buttons for primary links to important pages

## SEO Checklist For New Pages

To ensure consistent SEO implementation across new pages and prevent common issues, follow this checklist for every new page:

### 1. Complete Meta Tag Implementation

- [ ] Use the PageSeo component with all required props
- [ ] Include unique, descriptive title (50-60 characters)
- [ ] Write compelling meta description (under 155 characters)
- [ ] Add proper keywords relevant to the page content
- [ ] Set canonical URL and hreflang attributes for all supported languages
- [ ] Verify title and description appear correctly in search previews

### 2. Structured Data Implementation

- [ ] Add appropriate JSON-LD structured data using the JsonLd component with the required `type` property
- [ ] Choose the right schema type (Article, Service, FAQ, Organization, etc.)
- [ ] Include all required properties for the chosen schema
- [ ] Test structured data with Google's Rich Results Test before deployment
- [ ] Ensure structured data is language-specific if needed

### 3. Proper Heading Hierarchy

- [ ] Include exactly ONE h1 heading per page (either visible or as sr-only for accessibility)
- [ ] Ensure h1 contains the main page title/topic
- [ ] Use h2 for main sections and h3 for subsections
- [ ] Never skip heading levels (e.g., don't jump from h1 to h3 without h2)
- [ ] Use appropriate font sizes and styles with Tailwind classes
- [ ] If using a component like HeroSection that doesn't have an h1, add one with className="sr-only"

### 4. Semantic HTML Structure

- [ ] Wrap page content in `<main>` tags
- [ ] Include `<header>` for the page header or hero section
- [ ] Use `<section>` tags for distinct content sections
- [ ] Use `<article>` for self-contained content (like blog posts, testimonials, or case studies)
- [ ] Include appropriate ARIA attributes for interactive elements
- [ ] Use `<nav>` for navigation elements
- [ ] Include `<footer>` for page footer content

### 5. Image Optimization

- [ ] Add descriptive alt text to all images
- [ ] Include width and height attributes to prevent layout shifts
- [ ] Set appropriate dimensions for all images (even with Tailwind classes)
- [ ] Optimize image file sizes (compress without quality loss)
- [ ] Use responsive image techniques when appropriate
- [ ] Ensure images have appropriate file names with keywords
- [ ] Create proper Open Graph and Twitter Card images

### 6. Internal Linking Strategy

- [ ] Add links to the new page from at least 3 relevant existing pages
- [ ] Include links from the new page to related content
- [ ] Update navigation components to include the new page
- [ ] Ensure descriptive anchor text with target keywords
- [ ] Update sitemap.xml to include the new page
- [ ] Check that all links use proper translation with getLocalizedPath

### 7. Technical Page Setup

- [ ] Ensure proper responsive design with Tailwind breakpoint classes (sm:, md:, lg:, xl:)
- [ ] Use semantic HTML elements consistently
- [ ] Check mobile responsiveness across devices
- [ ] Verify page performance meets Core Web Vitals standards
- [ ] Implement proper ARIA attributes for accessibility
- [ ] Test keyboard navigation and screen reader compatibility

### 8. Post-Launch Tasks

- [ ] Update sitemap by running `npm run sitemap`
- [ ] Run the SEO audit tool to check for issues: `npm run seo:audit`
- [ ] Run page-specific SEO check: `node scripts/seo-page-checker.js --path=/path-to-page`
- [ ] Verify inclusion in navigation and footer links
- [ ] Test in Google's Mobile-Friendly Test
- [ ] Submit URL to Google Search Console
- [ ] Check for any warning or errors in the browser console

### 9. Analytics Integration

- [ ] Ensure Google Analytics tracking is properly implemented
- [ ] Add any required event tracking for user interactions
- [ ] Verify tracking works in all page states (loaded, interactive)
- [ ] Set up goal tracking if applicable

### Common SEO Issues to Avoid

- [ ] Multiple h1 tags on a single page
- [ ] Missing JSON-LD structured data
- [ ] Missing image width/height attributes
- [ ] Lack of semantic HTML elements
- [ ] Non-descriptive link text ("click here", "read more")
- [ ] Missing alt text on images
- [ ] Improper heading hierarchy (skipping levels)
- [ ] Duplicate page titles or meta descriptions
- [ ] Missing or poor internal linking

A script has been created (`scripts/seo-page-checker.js`) to automate many of these checks. Run it for new pages with:

```bash
node scripts/seo-page-checker.js --path=/path/to/new/page
```

### Example of Proper Heading Structure and Semantic HTML

```jsx
// Good example with proper heading hierarchy and semantic HTML
<Layout>
  <header>
    <HeroSection title="Page Title" description="Page description">
      <h1 className="sr-only">Main Page Title</h1>
      {/* Hero content */}
    </HeroSection>
  </header>

  <main>
    <section className="bg-black">
      <div className="container">
        <h2 className="text-3xl font-bold">First Major Section</h2>
        <p>Section content</p>

        <div className="grid md:grid-cols-2">
          <article>
            <h3 className="text-2xl font-semibold">Sub-section Title</h3>
            <p>Article content</p>
          </article>

          <article>
            <h3 className="text-2xl font-semibold">Another Sub-section</h3>
            <p>More content</p>
          </article>
        </div>
      </div>
    </section>

    <section className="bg-gray-100">
      <div className="container">
        <h2 className="text-3xl font-bold">Second Major Section</h2>
        {/* More content */}
      </div>
    </section>
  </main>

  <footer>{/* Footer content */}</footer>
</Layout>
```

## UI Styling and Interactivity Guidelines

Based on lessons learned from implementing pages like `For-verksamheten`, `Features/RouteOptimization`, and `Produkter`, the following UI standards should be applied consistently to all new pages:

### Dark Theme Implementation

1. **Background Colors**
   - Primary background: `bg-black`
   - Secondary background: `bg-black/90 backdrop-blur-sm`
   - Gradient backgrounds: `bg-gradient-to-br from-black to-gray-900`
   - Radial glows: `bg-[radial-gradient(circle_at_center,rgba(0,255,127,0.1),transparent_70%)]`

2. **Text Colors**
   - Primary text: `text-white`
   - Secondary text: `text-gray-300`
   - Tertiary text: `text-gray-400`
   - Accent text: `text-[#00FF7F]`

3. **Borders and Separators**
   - Default borders: `border border-white/10`
   - Hover borders: `border-[#00FF7F]/20` or `border-[#00FF7F]/30`
   - Dividers: `border-t border-white/10`

### 3D Card Mouseover Effects

Implement consistent card hover effects using these patterns:

```jsx
<motion.div
  className="bg-black/40 backdrop-blur-sm p-6 rounded-lg relative h-full 
    group border border-transparent 
    hover:border-[#00FF7F]/20 hover:shadow-[0_0_30px_rgba(0,255,127,0.1)]
    transition-all duration-300"
  whileHover={{
    scale: 1.02,
    transition: { duration: 0.2 },
  }}
>
  <div className="relative z-10">
    {/* Card content */}
    <motion.div
      whileHover={{ scale: 1.1 }}
      transition={{ duration: 0.2 }}
      className="mb-4"
    >
      {icon}
    </motion.div>
    <h3 className="text-xl font-semibold text-white mb-2 group-hover:text-[#00FF7F] transition-colors">
      {title}
    </h3>
    <p className="text-gray-300">{description}</p>
  </div>
</motion.div>
```

Key components of the effect:

- Group hover states (`group` and `group-hover:` classes)
- Subtle scaling (`scale: 1.02` on hover)
- Green glow shadows (`hover:shadow-[0_0_30px_rgba(0,255,127,0.1)]`)
- Border transitions (`border-transparent` to `border-[#00FF7F]/20`)
- Text color transitions (`group-hover:text-[#00FF7F]`)
- Nested icon scaling for additional depth (`scale: 1.1`)

### Image Hover Effects

For interactive image containers:

```jsx
<motion.div className="group" whileHover={{ scale: 1.01 }}>
  <div className="overflow-hidden rounded-lg border border-white/10 group-hover:border-[#00FF7F]/20 group-hover:shadow-[0_0_30px_rgba(0,255,127,0.15)] transition-all duration-300">
    <img
      src="/path/to/image.jpg"
      alt="Description"
      className="w-full h-auto rounded-lg transition-transform duration-500 group-hover:scale-105"
      width={600}
      height={400}
    />
  </div>
</motion.div>
```

Key components:

- Subtle container scaling (`scale: 1.01`)
- More pronounced image scaling (`group-hover:scale-105`)
- Longer transform duration for smooth zoom (`duration-500`)
- Overflow hidden to contain zoomed image

### List Item Interactions

For interactive list items:

```jsx
<li className="flex items-start group/item hover:translate-x-1 transition-transform">
  <div className="mr-2 mt-1 h-5 w-5 text-[#00FF7F] flex-shrink-0 group-hover/item:scale-110 transition-transform">
    •
  </div>
  <span className="text-gray-300 group-hover/item:text-gray-100 transition-colors">
    {listItemText}
  </span>
</li>
```

Key components:

- Subtle horizontal shift (`hover:translate-x-1`)
- Bullet point scaling (`group-hover/item:scale-110`)
- Text brightening (`text-gray-300` to `text-gray-100`)

### Button Styling

Primary and secondary button styling:

```jsx
// Primary button
<Button className="bg-[#00FF7F] text-black hover:bg-[#00FF7F]/90 hover:shadow-[0_0_30px_rgba(0,255,127,0.3)] transition-all duration-300">
  {buttonText}
</Button>

// Secondary button
<Button variant="outline" className="bg-transparent border-[#00FF7F]/50 text-[#00FF7F] hover:bg-[#00FF7F]/10 hover:shadow-[0_0_20px_rgba(0,255,127,0.2)] transition-all duration-300 hover:scale-105">
  {buttonText}
</Button>

// Link button
<Link
  to={getLocalizedPath('/path')}
  className="inline-flex items-center px-6 py-3 bg-transparent border border-white/20 text-white rounded-lg hover:bg-white/5 hover:border-white/30 transition-all duration-300"
>
  {linkText}
  <ArrowRight className="w-4 h-4 ml-2" />
</Link>
```

### Scroll Animation Patterns

Use the `FadeInSection` component to introduce sections as they come into view:

```jsx
<FadeInSection>
  <section className="bg-black">{/* Section content */}</section>
</FadeInSection>
```

### Gradient and Glow Patterns

Use these consistent patterns for background effects:

1. **Centered radial glow**

```jsx
<div className="relative overflow-hidden py-16">
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(0,255,127,0.1),transparent_70%)]" />
  <div className="relative z-10">{/* Content */}</div>
</div>
```

2. **Corner radial glow**

```jsx
<div className="relative overflow-hidden py-16">
  <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_right,rgba(0,255,127,0.1),transparent_70%)]" />
  <div className="relative z-10">{/* Content */}</div>
</div>
```

### Component Hierarchy Patterns

Maintain this structure consistently:

```jsx
<Layout>
  <header>
    <HeroSection>
      <h1 className="sr-only">Page Title for SEO</h1>
      {/* Hero stats/content */}
    </HeroSection>
  </header>

  <main>
    <FadeInSection>
      <section className="bg-black">
        <ContentSection>
          <Container>
            {/* Section content with proper heading hierarchy */}
          </Container>
        </ContentSection>
      </section>
    </FadeInSection>

    {/* Additional sections */}
  </main>
</Layout>
```

### Motion Component Usage

Leverage Framer Motion consistently:

```jsx
// For section items staggered appearance
<motion.div
  initial={{ opacity: 0, y: 20 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.5, delay: 0.1 * index }}
>
  {/* Content */}
</motion.div>

// For hero stats
<motion.div
  className="bg-white/10 backdrop-blur-sm px-6 py-3 rounded-lg"
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ delay: 0.3 }}
>
  {/* Stat content */}
</motion.div>
```

### Implementation Recommendations

1. **Consistency across related pages**:
   - Use the same motion effects, timing, and hover states for similar components across pages
   - Maintain the same color scheme and glow effects throughout the site
   - Keep card and button styling consistent for a unified experience

2. **Performance considerations**:
   - Use `viewport={{ once: true }}` for one-time animations to avoid re-triggering
   - Apply effects judiciously to avoid overwhelming the user
   - Ensure transitions are smooth (typically 0.2-0.5s duration)

3. **Accessibility concerns**:
   - Respect user preferences with `prefers-reduced-motion`
   - Ensure hover states have sufficient contrast
   - Don't rely solely on hover effects for important functions

By following these UI patterns, all new pages will maintain a consistent look and feel with the existing dark theme and interactive 3D effects.

## Internal Linking Progress - Feature Pages

### Completed Tasks

- ✅ Implemented consistent internal linking between all feature pages (RouteOptimizationHomeCare, AiStaffPlanning, AiSchedulingCarefox, OnboardingCaireCarefox)
- ✅ Added "Related Features" sections on all feature pages with proper translations
- ✅ Ensured all internal links use proper translation with getLocalizedPath function
- ✅ Updated footer navigation with complete translations and links to all feature pages
- ✅ Created bidirectional linking between related feature pages

### Next Steps for Resource Pages

- [ ] Implement internal links from feature pages to relevant resource pages once created
- [ ] Ensure resource pages link back to relevant feature pages
- [ ] Create "Related Resources" sections on feature pages
- [ ] Add contextual links within content where relevant
- [ ] Update sitemap with all new resource pages

### Long-term Strategy

- [ ] Create a visual sitemap to identify linking opportunities
- [ ] Implement breadcrumb navigation on all content pages
- [ ] Consider adding "Related Pages" sections at the end of content pages
- [ ] Track click-through rates on internal links to identify optimization opportunities
- [ ] Review and update internal linking strategy quarterly

## Implementation Checklist Status - Feature Pages

The following items have been completed for all feature pages (RouteOptimizationHomeCare, AiStaffPlanning, AiSchedulingCarefox, OnboardingCaireCarefox):

### Page Structure and SEO

- ✅ Each page uses PageSeo component with proper metadata
- ✅ All pages include properly translated content with i18n
- ✅ All pages follow dark theme styling guidelines from frontend-guidelines.md
- ✅ Mobile responsiveness implemented and tested on all pages
- ✅ Sitemap updated with all feature pages

### Visual Components

- ✅ Modern dashboard visualizations implemented (replacing pie charts with more readable alternatives)
- ✅ Client case study sections removed until ready for public visibility
- ✅ Consistent stat card design used across feature pages
- ✅ Before/after comparisons with clear metrics and visual indicators
- ✅ Proper card styling with hover effects (hover:border-[#00FF7F]/20)

### Translation and Navigation

- ✅ All text strings use proper i18n translation functions
- ✅ CTA buttons and links use consistent translation keys
- ✅ Translation files verified for all new pages
- ✅ Internal navigation links correctly implemented between feature pages
- ✅ Links to Home, Products, and other main sections properly implemented

## Footer Update Strategy

The footer should be updated to include the new site structure, categorized by main sections:

### Footer Sections

1. **Features** - Already exists, but should include links to feature subpages as they're created
2. **About** - Include links to Om-oss and related pages
3. **Resources** - Add links to new Resurser section and sub-pages
4. **Products** - Add product-related links
5. **Contact** - Keep existing contact information
6. **Legal** - Add links to Sekretess, Villkor, Cookies

### Footer Implementation Recommendations

- ✅ Redesigned the Footer component with a 6-column layout for better organization
- ✅ Included a company section with logo and description
- ✅ Grouped links by logical categories (Features, Products, Resources, Contact)
- ✅ Implemented language-aware navigation with getLocalizedPath function
- ✅ Moved legal links to a bottom row for cleaner separation
- [ ] Continue updating with new pages as they are created
- [ ] Consider adding a newsletter signup in the footer
- [ ] Add social media links as they become available
- [ ] Ensure all links have proper hover states and accessibility attributes

## Implementation Progress

| Page                               | Status      | Assigned To | Target Date   | Completion Date |
| ---------------------------------- | ----------- | ----------- | ------------- | --------------- |
| For-verksamheten                   | Completed   |             |               | May 18, 2025    |
| Features/RouteOptimizationHomeCare | Completed   |             |               | May 20, 2025    |
| Produkter                          | Completed   |             |               | May 22, 2025    |
| Footer Translations                | Completed   |             |               | May 24, 2025    |
| Features/AiStaffPlanning           | Completed   |             |               | May 26, 2025    |
| Features/AiSchedulingCarefox       | Completed   |             |               | May 26, 2025    |
| Features/OnboardingCaireCarefox    | Completed   |             |               | May 27, 2025    |
| Resurser/Artiklar                  | Not Started |             | June 15, 2025 |                 |
| Resurser/Guider                    | Not Started |             | June 20, 2025 |                 |
| Resurser/Jamforelser               | Not Started |             | June 25, 2025 |                 |
| Resurser/Personas                  | Not Started |             | June 30, 2025 |                 |

## Next Steps

1. **Current Focus**: Implement Resources section pages (Artiklar, Guider, Jamforelser)
2. **Concurrent Task**: Update internal linking structure for existing feature pages
3. **Completed Task**: ✅ Implement feature pages with modern dashboard visualizations
4. Next: Create Personas pages and whitepapers
5. Continue with additional resources pages
6. Update navigation and footer as new pages are created
7. Regularly update sitemap.xml with new pages
8. Verify all pages with Google Search Console

## Performance Tracking

- Monitor Google Search Console for indexing progress
- Track organic traffic to new pages
- Monitor keyword rankings for targeted terms
- Analyze user behavior on new pages (bounce rate, time on page, etc.)

## SEO Audit Process

After implementing pages, run the audit tools to ensure compliance:

1. Run comprehensive audit: `npm run seo:audit`
2. Review reports in the reports/ directory
3. Address any critical issues identified
4. Validate structured data using Google's Rich Results Test
5. Test mobile responsiveness using Chrome DevTools
6. Check page speed using PageSpeed Insights
7. Verify inclusion in sitemap
8. Submit URLs to Google Search Console
