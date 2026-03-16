# Page Audit Guide

## Overview

This guide helps verify that existing pages follow Caire's guidelines and standards. Use this guide to audit pages without modifying their content.

## Audit Process

### 1. Component Structure

Check that the page follows the standard structure:

```
src/pages/YourPage/
  ├── index.tsx
  ├── Content.tsx
  ├── sections/
  ├── components/
  ├── hooks/
  └── __tests__/
```

### 2. Code Quality Audit

- [ ] Proper TypeScript types used
- [ ] Components properly memoized
- [ ] Error boundaries implemented
- [ ] Loading states handled
- [ ] Proper code splitting
- [ ] No unused imports
- [ ] No console logs
- [ ] Consistent naming conventions

### 3. SEO Audit

Use the [SEO Audit Template](seo.md#page-audit-template) to verify:

- [ ] Meta tags
- [ ] Content structure
- [ ] Technical SEO
- [ ] Performance
- [ ] Analytics

### 4. Performance Audit

Run performance checks:

```bash
# Run Lighthouse audit
npm run lighthouse

# Check bundle size
npm run analyze
```

Verify metrics:

- [ ] First Contentful Paint < 2s
- [ ] Largest Contentful Paint < 2.5s
- [ ] Time to Interactive < 3.8s
- [ ] Total Blocking Time < 300ms
- [ ] Cumulative Layout Shift < 0.1

### 5. Accessibility Audit

Check WCAG compliance:

- [ ] Proper heading hierarchy
- [ ] ARIA labels present
- [ ] Color contrast sufficient
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Focus indicators visible
- [ ] Alt text on images
- [ ] Form labels and descriptions

### 6. Navigation Audit

Verify all navigation elements:

- [ ] Main menu links work
- [ ] Footer links present
- [ ] Breadcrumbs implemented
- [ ] Scroll to top on navigation
- [ ] Mobile menu works
- [ ] Active states correct

### 7. Content Structure

Check content organization:

- [ ] Clear visual hierarchy
- [ ] Consistent spacing
- [ ] Proper use of components
- [ ] Responsive layout
- [ ] Animations work
- [ ] Error states handled
- [ ] Loading states shown

### 8. Testing Coverage

Verify test implementation:

- [ ] Unit tests present
- [ ] Integration tests added
- [ ] Accessibility tests
- [ ] Performance tests
- [ ] Error handling tested
- [ ] Analytics tracking tested

## Audit Checklist

```markdown
# Page Audit: [Page Name]

## Basic Information

- Page URL:
- Last Updated:
- Responsible Team:

## Component Structure

- [ ] Follows file structure
- [ ] Proper component organization
- [ ] Reusable components identified

## Code Quality

- [ ] TypeScript properly used
- [ ] Error handling implemented
- [ ] Loading states present
- [ ] Code splitting used
- [ ] No console logs
- [ ] Clean imports

## SEO Implementation

- [ ] Meta tags present
- [ ] Structured data added
- [ ] Semantic HTML used
- [ ] URLs properly structured
- [ ] Analytics tracking

## Performance

- [ ] Meets FCP target
- [ ] Meets LCP target
- [ ] Meets TTI target
- [ ] Meets TBT target
- [ ] Meets CLS target

## Accessibility

- [ ] WCAG compliant
- [ ] Keyboard navigation
- [ ] Screen reader friendly
- [ ] Color contrast
- [ ] ARIA attributes

## Navigation

- [ ] Menu links work
- [ ] Footer links present
- [ ] Scroll behavior correct
- [ ] Mobile navigation
- [ ] Breadcrumbs

## Content

- [ ] Clear hierarchy
- [ ] Responsive design
- [ ] Consistent styling
- [ ] Error states
- [ ] Loading states

## Testing

- [ ] Unit tests
- [ ] Integration tests
- [ ] Accessibility tests
- [ ] Performance tests
- [ ] Analytics tests

## Issues Found

1. [List issues]
2. [Prioritize fixes]

## Recommendations

1. [Immediate fixes]
2. [Long-term improvements]
```

## Running the Audit

1. Copy the audit checklist
2. Create a new file: `audits/[page-name]-audit.md`
3. Fill out each section
4. Document issues found
5. Create improvement tasks
6. Share with team

## Common Findings

1. **SEO Issues**
   - Missing meta tags
   - Poor content structure
   - Missing analytics

2. **Performance Issues**
   - Unoptimized images
   - Large bundle size
   - Unnecessary re-renders

3. **Accessibility Issues**
   - Missing ARIA labels
   - Poor color contrast
   - Keyboard navigation issues

4. **Code Quality Issues**
   - Type issues
   - Memory leaks
   - Console logs
   - Unused code

## Action Plan Template

```markdown
# Page Improvement Plan: [Page Name]

## Priority 1 (Immediate)

- [ ] Fix critical accessibility issues
- [ ] Add missing meta tags
- [ ] Optimize performance

## Priority 2 (This Sprint)

- [ ] Improve code quality
- [ ] Add missing tests
- [ ] Update documentation

## Priority 3 (Next Sprint)

- [ ] Enhance features
- [ ] Refactor components
- [ ] Update styling

## Timeline

1. Week 1: Priority 1 items
2. Week 2: Priority 2 items
3. Week 3: Priority 3 items

## Resources Needed

1. [List resources]
2. [List dependencies]

## Success Metrics

1. [Define metrics]
2. [Set targets]
```

## Next Steps

1. Select pages to audit
2. Create audit schedule
3. Assign responsibilities
4. Track improvements
5. Document learnings
