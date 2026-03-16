# Content Implementation Guide

## Overview

This guide outlines the process of implementing content for new pages in Caire, ensuring consistency in content structure, language, and presentation.

## Content Structure

### 1. Page Layout Components

```typescript
// Basic page structure
const YourPage = () => {
  return (
    <PageLayout>
      <PageSeo title="Your Title" description="Your description" />
      <Hero />
      <MainContent />
      <Benefits />
      <CtaSection />
    </PageLayout>
  );
};

// Hero section structure
const Hero = () => {
  return (
    <section className="hero-section">
      <h1>Swedish Title</h1>
      <p className="hero-description">Swedish description text</p>
      <CtaButton>Swedish CTA text</CtaButton>
    </section>
  );
};
```

### 2. Content Organization

- Use semantic HTML structure
- Follow heading hierarchy (h1-h6)
- Group related content in sections
- Use appropriate spacing and layout

## Content Types

### 1. Text Content

- Headlines (H1-H6)
- Body text
- Lists (ordered/unordered)
- Call-to-action text
- Links and buttons
- Form labels and hints

### 2. Rich Content

- Images with alt text
- Videos with captions
- Icons with labels
- Charts and graphs
- Interactive elements

## Language Guidelines

### 1. Swedish Content

- All user-facing content must be in Swedish
- Use professional, clear language
- Follow Swedish grammar and punctuation rules
- Maintain consistent terminology

### 2. Content Structure

```typescript
// Example content structure
const pageContent = {
  hero: {
    title: "AI-driven hemtjänstplattform",
    description: "Vi revolutionerar hemtjänsten med...",
    ctaText: "Boka Demo",
  },
  benefits: [
    {
      title: "Intelligent Matchning",
      description: "AI matchar rätt personal...",
    },
    // ... more benefits
  ],
};
```

## Content Components

### 1. Text Components

```typescript
// Reusable text components
const SectionTitle = ({ children }: { children: React.ReactNode }) => (
  <h2 className="text-2xl font-bold mb-4">{children}</h2>
);

const SectionDescription = ({ children }: { children: React.ReactNode }) => (
  <p className="text-gray-600 mb-6">{children}</p>
);
```

### 2. Content Blocks

```typescript
// Feature block component
const FeatureBlock = ({ title, description, icon }: FeatureBlockProps) => (
  <div className="feature-block">
    <div className="icon-wrapper">{icon}</div>
    <h3 className="feature-title">{title}</h3>
    <p className="feature-description">{description}</p>
  </div>
);
```

## Dynamic Content

### 1. Content Loading

```typescript
// Content loading with skeleton
const ContentSection = () => {
  const { data, loading } = useContent();

  if (loading) {
    return <ContentSkeleton />;
  }

  return (
    <section>
      {data.map(item => (
        <ContentBlock key={item.id} {...item} />
      ))}
    </section>
  );
};
```

### 2. Error States

```typescript
// Error handling in content
const ContentDisplay = () => {
  const { data, error } = useContent();

  if (error) {
    return (
      <ErrorMessage
        title="Kunde inte ladda innehåll"
        message="Försök igen senare"
      />
    );
  }

  return <Content data={data} />;
};
```

## Content Management

### 1. Content Updates

- Store content in `page-content.md`
- Use content constants for reusable text
- Implement i18n structure for future localization
- Document content dependencies

### 2. Content Validation

```typescript
// Content validation schema
const contentSchema = z.object({
  title: z.string().min(1),
  description: z.string().min(10),
  sections: z.array(
    z.object({
      title: z.string(),
      content: z.string(),
    }),
  ),
});
```

## Accessibility

### 1. Text Accessibility

- Use sufficient color contrast
- Implement proper heading structure
- Add descriptive alt text
- Support screen readers

### 2. Interactive Content

- Keyboard navigation support
- Focus management
- ARIA labels and roles
- Screen reader announcements

## Performance

### 1. Content Loading

- Implement lazy loading
- Use image optimization
- Cache content when appropriate
- Handle loading states

### 2. Content Updates

- Minimize content updates
- Use efficient re-rendering
- Implement proper memoization
- Handle content transitions

## Testing

### 1. Content Tests

```typescript
describe('PageContent', () => {
  it('renders content correctly', () => {
    render(<PageContent />);
    expect(screen.getByRole('heading')).toHaveTextContent('Expected Title');
    expect(screen.getByText('Expected description')).toBeInTheDocument();
  });

  it('handles missing content gracefully', () => {
    render(<PageContent content={null} />);
    expect(screen.getByText('Innehåll saknas')).toBeInTheDocument();
  });
});
```

### 2. Content Validation

```typescript
describe("Content Validation", () => {
  it("validates required content", () => {
    const result = contentSchema.safeParse(invalidContent);
    expect(result.success).toBe(false);
  });
});
```

## Checklist

Before completing content implementation:

- [ ] All text content in Swedish
- [ ] Proper heading hierarchy
- [ ] Alt text for images
- [ ] Error states handled
- [ ] Loading states implemented
- [ ] Content tests written
- [ ] Accessibility verified
- [ ] Performance optimized
- [ ] Content documented
- [ ] Translations prepared

## Common Issues

1. **Missing Content**
   - Implement fallback content
   - Add error boundaries
   - Log missing content
   - Notify content team

2. **Performance Issues**
   - Optimize content loading
   - Implement caching
   - Use code splitting
   - Monitor performance

3. **Accessibility Issues**
   - Check heading structure
   - Verify color contrast
   - Test screen readers
   - Validate ARIA usage

## Next Steps

1. Implement page content
2. Add content tests
3. Verify accessibility
4. Document content structure
5. Update content management

Proceed to [Testing Guide](testing.md)
