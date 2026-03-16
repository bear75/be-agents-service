# Adding a New Page to Caire

This document outlines the step-by-step process for adding a new page to the Caire project, based on our learnings and best practices.

## Introduction

Before diving into implementation, it's important to understand why proper page creation and documentation are crucial. A well-structured page not only provides better user experience but also ensures maintainability and accessibility for all users. This guide will help you create pages that align with Caire's standards and best practices.

## Prerequisites

Before adding a new page, ensure you have:

- Access to the codebase
- Development environment set up
- Understanding of the page requirements from PRD/task breakdown
- Reviewed all relevant documentation in the `docs/` folder
- Familiarity with React, TypeScript, and our UI component library
- Access to design assets and content requirements

## Steps Overview

1. Planning and Research
2. Create the Page Component
3. Add Route Configuration
4. Add Navigation and Footer Links
5. Content Implementation
6. SEO Implementation
7. Implement Testing
8. Performance Optimization
9. Accessibility Implementation
10. Documentation
11. Quality Checklist
12. Implementation Review

For detailed instructions on each step, refer to the following guides:

### Planning and Structure

- [Page Planning Guide](page-guides/planning.md)
- [Component Creation Guide](page-guides/component.md)
- [Route Configuration Guide](page-guides/routing.md)

### Content and SEO

- [Content Implementation Guide](page-guides/content.md)
- [SEO Guide](page-guides/seo.md)

### Testing and Performance

- [Testing Guide](page-guides/testing.md)
- [Performance Guide](page-guides/performance.md)

### Accessibility and Documentation

- [Accessibility Guide](page-guides/accessibility.md)
- [Documentation Guide](page-guides/documentation.md)

### Quality and Review

- [Quality Checklist](page-guides/quality-checklist.md)
- [Implementation Review Guide](page-guides/implementation-review.md)

## Component Patterns

For reusable component patterns and implementations, refer to:

### Layout Components

```typescript
// Basic page layout
const PageLayout: React.FC<PageLayoutProps> = ({ children }) => {
  return (
    <>
      <Header />
      <main className="min-h-screen">
        {children}
      </main>
      <Footer />
    </>
  );
};

// Section layout
const Section: React.FC<SectionProps> = ({
  title,
  description,
  children,
  className
}) => {
  return (
    <section className={cn("py-12", className)}>
      <div className="container">
        {title && <h2 className="text-3xl font-bold mb-4">{title}</h2>}
        {description && <p className="text-gray-600 mb-8">{description}</p>}
        {children}
      </div>
    </section>
  );
};
```

### Common Components

```typescript
// Hero section
const Hero: React.FC<HeroProps> = ({
  title,
  description,
  ctaText,
  ctaHref
}) => {
  return (
    <div className="bg-primary text-white py-16">
      <div className="container">
        <h1 className="text-4xl font-bold mb-4">{title}</h1>
        <p className="text-xl mb-8">{description}</p>
        <Button asChild>
          <Link href={ctaHref}>{ctaText}</Link>
        </Button>
      </div>
    </div>
  );
};

// Feature grid
const FeatureGrid: React.FC<FeatureGridProps> = ({ features }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {features.map(feature => (
        <FeatureCard key={feature.id} {...feature} />
      ))}
    </div>
  );
};
```

For more component patterns and examples, see:

- [Component Patterns Guide](patterns/components.md)
- [Common UI Patterns](patterns/ui.md)

## Implementation Checklist

Before starting implementation:

- [ ] Read all referenced guides
- [ ] Review similar pages in the codebase
- [ ] Create implementation plan
- [ ] Set up development environment

During implementation:

- [ ] Follow each guide in sequence
- [ ] Complete all checklist items
- [ ] Document any deviations or new patterns
- [ ] Request reviews at key milestones
- [ ] Update navigation and footer links
- [ ] Ensure scroll behavior is correct
- [ ] Verify SEO implementation
- [ ] Test all user interactions

After implementation:

- [ ] Verify all checklist items
- [ ] Run all tests
- [ ] Check performance metrics
- [ ] Update documentation
- [ ] Prepare for code review
- [ ] Verify accessibility
- [ ] Test responsive design
- [ ] Check analytics implementation

## SEO Checklist

Before considering your page complete, verify that you've implemented these SEO requirements:

- **Title & Meta Tags**: Use the PageSeo component to set title, description, keywords and canonical URLs
- **Structured Data**: Add [JSON-LD](https://schema.org/) markup using the JsonLd component with correct `type` property
- **Mobile Responsiveness**: Verify responsive design using Tailwind breakpoint classes (sm:, md:, lg:, xl:)
- **Performance**: Minimize image sizes and ensure Core Web Vitals compliance (LCP, FID, CLS)
- **Accessibility**: Include proper alt tags, ARIA attributes, and color contrast
- **Analytics**: Ensure Google Analytics tracking is in place

After implementation, run `node scripts/seo-page-checker.js --path=/your-path` to verify compliance.

## Heading Hierarchy & Semantic HTML

### Proper Heading Structure

Every page MUST have a proper heading hierarchy that starts with exactly ONE `<h1>` tag for the page's main topic:

1. **H1**: Only one per page - the main page title
2. **H2**: Major section headings
3. **H3**: Sub-sections within H2 sections
4. **H4-H6**: Further nested sub-sections as needed

If your design doesn't visually feature an H1 (common with hero sections that use large text), you should still add an H1 with the `sr-only` class:

```jsx
<HeroSection title="Page Title">
  <h1 className="sr-only">Complete Page Title With Keywords</h1>
  {/* Hero content */}
</HeroSection>
```

### Semantic HTML Elements

Always structure your page with proper semantic HTML elements:

```jsx
<Layout>
  <header>{/* Page header/hero */}</header>

  <main>
    <section>
      {/* A distinct section of content */}
      <article>
        {/* Self-contained composition (e.g., blog post, testimonial) */}
      </article>
    </section>

    <section>
      {/* Another distinct section */}
      <aside>{/* Content tangentially related to main content */}</aside>
    </section>
  </main>

  <footer>{/* Page footer */}</footer>
</Layout>
```

### Common Mistakes to Avoid

1. **Multiple H1 Tags**: Never include more than one H1 per page
2. **Skipping Heading Levels**: Don't jump from H1 to H3 without using H2
3. **Empty Semantic Elements**: Each semantic element should contain meaningful content
4. **Missing Semantic Structure**: Don't rely only on divs; use semantic elements
5. **Images Without Dimensions**: Always include width and height attributes on images
6. **Inaccessible Interactive Elements**: Ensure all interactive elements are keyboard accessible
7. **Pure Style-Based Headings**: Don't create "headings" that are just styled paragraphs

### Tooling and Validation

- Use the SEO page checker to verify your page structure: `node scripts/seo-page-checker.js --path=/path-to-page`
- Check accessibility with browser developer tools (Lighthouse)
- Validate HTML structure with the W3C validator

## Content Requirements

Before your page is ready for review, ensure:

- All copy is free of spelling and grammatical errors
- Text is concise, scannable, and addresses user needs
- All claims are factually accurate and consistent with our marketing
- Content is correctly translated in all required languages
- All buttons and links work as expected
- No placeholder content or "TODO" comments remain

## Automated SEO Checks

After creating a new page, run the automated SEO checker:

```bash
npm run seo:check -- --path=/path-to-your-page
```

This will analyze your page for SEO best practices and report any issues found.

## Recent Learnings and Best Practices

For the latest best practices and solutions, refer to:

- [Component Patterns](patterns/components.md)
- [Common Issues and Solutions](troubleshooting/common-issues.md)

## Need Help?

If you encounter issues or need clarification:

1. Check the [Common Issues Guide](troubleshooting/common-issues.md)
2. Review similar implementations
3. Ask in the development channel
4. Update documentation with new learnings
