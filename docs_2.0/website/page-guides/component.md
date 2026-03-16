# Component Creation Guide

## Overview

This guide covers the process of creating a new page component in Caire, focusing on best practices and common patterns.

## File Structure

Create your page component in the appropriate directory:

```
src/
  pages/
    YourPage/
      index.tsx        # Main page component
      Content.tsx      # Main content sections
      sections/        # Page-specific sections
      components/      # Page-specific components
      hooks/          # Page-specific hooks
      __tests__/      # Test files
```

## Component Template

Use this template as a starting point:

```typescript
import { Helmet } from 'react-helmet-async';
import { useEffect } from 'react';
import { trackPageView } from '@/utils/analytics';
import { FadeInSection } from '@/components/animations/FadeInSection';

export const YourPage = () => {
  useEffect(() => {
    trackPageView('/your-path', 'Your Page | Caire');
  }, []);

  return (
    <>
      <Helmet>
        <title>Your Page | Caire</title>
        <meta name="description" content="Page description" />
      </Helmet>

      <main className="pt-24 pb-16">
        <FadeInSection>
          {/* Your content here */}
        </FadeInSection>
      </main>
    </>
  );
};

export default YourPage;
```

## Key Features

### 1. SEO and Analytics

- Always include Helmet for SEO
- Track page views on mount
- Add descriptive meta tags
- Include relevant keywords

### 2. Performance

- Use lazy loading for heavy components
- Implement proper code splitting
- Optimize images and media
- Minimize bundle size

### 3. Accessibility

- Use semantic HTML
- Add ARIA labels
- Ensure keyboard navigation
- Maintain proper heading hierarchy

### 4. State Management

- Use hooks for local state
- Implement proper data fetching
- Handle loading states
- Manage error boundaries

### 5. Styling

- Use Tailwind utility classes
- Follow the color scheme
- Maintain consistent spacing
- Implement responsive design

## Best Practices

1. Component Organization:
   - Keep components focused
   - Use proper TypeScript types
   - Implement error boundaries
   - Handle loading states

2. Code Quality:
   - Write clean, readable code
   - Add proper comments
   - Follow naming conventions
   - Use TypeScript effectively

3. Testing:
   - Write comprehensive tests
   - Test edge cases
   - Verify accessibility
   - Check performance

4. Documentation:
   - Document props
   - Explain complex logic
   - Note dependencies
   - Include usage examples

## Common Patterns

### Loading States

```typescript
const LoadingSkeleton = () => (
  <div className="w-full space-y-4">
    <div className="h-8 w-1/3 bg-gray-200 animate-pulse rounded" />
    <div className="h-24 w-full bg-gray-200 animate-pulse rounded" />
  </div>
);
```

### Error Handling

```typescript
const ErrorDisplay = ({ error }: { error: Error }) => (
  <div className="p-4 bg-red-50 text-red-900 rounded">
    <h2>Something went wrong</h2>
    <p>{error.message}</p>
  </div>
);
```

### Animation Wrapper

```typescript
const AnimatedSection = ({ children }: { children: React.ReactNode }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5 }}
  >
    {children}
  </motion.div>
);
```

## Checklist

Before completing component creation:

- [ ] SEO elements implemented
- [ ] Analytics tracking added
- [ ] Proper TypeScript types used
- [ ] Loading states handled
- [ ] Error states managed
- [ ] Animations implemented
- [ ] Tests written
- [ ] Documentation added
- [ ] Accessibility verified
- [ ] Performance optimized

## Next Steps

1. Add route configuration
2. Implement navigation
3. Add content
4. Write tests

Proceed to [Route Configuration Guide](routing.md)

## UI Components

### Available Components

The following UI components are available in `@/components/ui`:

1. **Navigation Components**
   - `Link` - For internal and external links with safety checks
   - `Button` - Styled button component
   - `NavigationMenu` - Navigation menu component

2. **Layout Components**
   - `Container` - Container with responsive padding
   - `Prose` - Typography styles for article content
   - `Section` - Section wrapper with consistent spacing

3. **Form Components**
   - `Input` - Form input component
   - `Textarea` - Multiline text input
   - `Select` - Dropdown select component
   - `Checkbox` - Checkbox input
   - `RadioGroup` - Radio button group

4. **Feedback Components**
   - `Toast` - Notification component
   - `Dialog` - Modal dialog
   - `Alert` - Alert messages
   - `Progress` - Progress indicators

### Common Import Patterns

```typescript
// Basic components
import { Button } from "@/components/ui/button";
import { Link } from "@/components/ui/link";
import { Container } from "@/components/ui/container";

// Form components
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Select } from "@/components/ui/select";

// Feedback components
import { Toast } from "@/components/ui/toast";
import { Dialog } from "@/components/ui/dialog";
import { Alert } from "@/components/ui/alert";
```

### Component Usage Examples

```typescript
// Link usage
<Link href="/demo">Book Demo</Link>
<Link href="https://example.com" external>External Link</Link>

// Button with Link
<Button asChild>
  <Link href="/demo">Book Demo</Link>
</Button>

// Container with Prose
<Container>
  <Prose>
    <h1>Article Title</h1>
    <p>Article content...</p>
  </Prose>
</Container>
```
