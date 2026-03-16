# Frontend Development Guidelines

## Code Structure

### Components

- Use functional components with TypeScript
- Implement proper prop typing and validation
- Keep components focused and reusable
- Follow the container/presentation pattern
- Use Helmet for SEO meta tags on all pages
- Implement proper ARIA attributes for accessibility

### State Management

- Use React hooks for local state
- Implement context for shared state when needed
- Keep state as close to usage as possible

## Styling

- Use Tailwind CSS for all styling
- Leverage shadcn/ui components for common UI elements
- Follow mobile-first responsive design principles:
  - Start with mobile layout first
  - Use Tailwind's responsive prefixes (sm:, md:, lg:)
  - Test on all breakpoints before deployment
  - Ensure touch targets are at least 44x44px for mobile
  - Optimize images for different screen sizes
  - Use appropriate font sizes for readability (min 16px for body text)
  - Implement responsive navigation with hamburger menu
  - Use proper spacing for touch interactions
  - Test on real mobile devices

## SEO Best Practices

- Use Swedish language for all content and SEO
- Use Helmet component for meta tags on all pages
- Implement proper JSON-LD structured data
- Ensure semantic HTML structure with proper roles
- Use appropriate heading hierarchy (h1-h6)
- Optimize images with alt text and lazy loading
- Implement canonical URLs
- Create and maintain sitemap.xml
- Configure robots.txt appropriately
- Monitor Core Web Vitals
- Implement schema markup for rich snippets
- Use descriptive URLs
- Optimize for mobile-first indexing

## SEO Optimization

### Meta Tags and Social Media Preview

- All pages must include proper meta tags for SEO optimization
- Social media preview images should follow these specifications:
  - Open Graph (og:image): 1200x630px
  - Twitter Card: 1200x600px
  - Format: PNG with optimized compression
  - Include branding elements and value proposition
  - Text should be readable when scaled down

### Image Requirements

- Preview images are stored in `/public/images/`
- Required formats:
  - og-preview.png (1200x630px) for Facebook/LinkedIn
  - twitter-preview.png (1200x600px) for Twitter
  - Favicon and app icons in various sizes (192x192, 512x512)

### Meta Tag Guidelines

- Use descriptive, keyword-rich titles (50-60 characters)
- Meta descriptions should be compelling and under 155 characters
- Include structured data for better search engine understanding
- Maintain proper social media meta tags (Open Graph, Twitter Cards)
- Use canonical URLs to prevent duplicate content

### Best Practices

- Keep titles unique for each page
- Update meta descriptions to match page content
- Test social media previews using platform validation tools
- Monitor and update structured data as needed
- Ensure all images have proper alt text
- Use semantic HTML elements
- Implement proper heading hierarchy (h1-h6)

## Performance

- Implement code splitting for routes
- Use React.lazy for dynamic imports
- Optimize images and assets
- Monitor and improve Core Web Vitals:
  - Largest Contentful Paint (LCP) < 2.5s
  - First Input Delay (FID) < 100ms
  - Cumulative Layout Shift (CLS) < 0.1
- Use responsive images with srcset
- Implement proper caching strategies
- Minimize bundle size
- Use production builds

## Accessibility

- Follow WCAG 2.1 guidelines
- Implement proper ARIA attributes
- Ensure keyboard navigation
- Test with screen readers
- Maintain sufficient color contrast
- Provide text alternatives for non-text content
- Support reduced motion preferences
- Ensure proper focus management
- Use semantic HTML elements

## Testing

- Write unit tests for critical components
- Implement E2E tests for main user flows
- Test responsive layouts
- Validate form submissions
- Test across different devices and browsers
- Test with different network conditions
- Test accessibility features

## Error Handling

- Implement proper error boundaries
- Show user-friendly error messages
- Log errors for debugging
- Handle network failures gracefully
- Provide fallback UI states

## Security

- Sanitize user inputs
- Implement proper CSRF protection
- Follow security best practices
- Keep dependencies updated
- Use HTTPS
- Implement Content Security Policy (CSP)
- Handle sensitive data appropriately
- Use secure authentication methods

## Mobile-First Development

- Design for mobile first, then scale up
- Use responsive breakpoints consistently
- Implement touch-friendly interactions
- Optimize performance for mobile devices
- Test on various mobile devices and browsers
- Consider offline capabilities
- Implement responsive images
- Use appropriate font sizes and spacing
- Ensure proper viewport configuration

## GDPR Compliance

### Cookie Consent

- Implement cookie banner for first-time visitors
- Allow users to manage cookie preferences
- Store consent status securely
- Provide clear information about cookie usage
- Enable users to withdraw consent

### Form Requirements

- Add consent checkboxes for data collection
- Provide links to privacy policy
- Clearly state data usage purpose
- Implement data retention policies
- Enable data export/deletion requests

### Email Communications

- Include unsubscribe links in all marketing emails
- State data retention period
- Provide privacy policy links
- Include company contact information
- Document consent collection

### Data Collection Points

- Contact forms
- Newsletter subscriptions
- Whitepaper downloads
- Demo requests
- Account registration

### Implementation Guidelines

- Use secure data transmission (HTTPS)
- Implement proper data encryption
- Follow data minimization principle
- Enable user data access/export
- Document all data processing activities

## Animations and Interactivity

### Animation Components

We use Framer Motion for smooth, performant animations. Common animation components include:

- `FadeInSection`: Fades in content when it enters the viewport
- `FloatingElement`: Creates a gentle floating animation for decorative elements

### Animation Guidelines

1. Use animations sparingly and purposefully
2. Ensure animations don't interfere with usability
3. Consider reduced motion preferences
4. Keep animations subtle and professional
5. Use consistent timing and easing curves

### Interactive Elements

1. Provide clear visual feedback on hover/click
2. Use motion to guide attention
3. Ensure keyboard accessibility
4. Maintain performance with debouncing/throttling
5. Test on various devices and screen sizes

### Performance Considerations

1. Lazy load heavy components
2. Use CSS transforms for animations when possible
3. Implement proper loading states
4. Monitor frame rates and animation performance
5. Use `will-change` property judiciously

## Icon Usage Guidelines

- Use icons sparingly and purposefully
- Keep icons only for main section headers and key statistics
- Ensure icons enhance rather than distract from content
- Maintain consistent icon sizing:
  - Section headers: 32x32px (h-8 w-8)
  - Inline statistics: 24x24px (h-6 w-6)
  - Navigation: 16x16px (h-4 w-4)
- Use primary brand color for icons
- Ensure proper icon imports to prevent runtime errors
- Consider performance impact of animated icons

## Article Styling

- Use clear visual hierarchy with consistent heading sizes
- Keep lists clean and readable without unnecessary decorations
- Use proper spacing between sections
- Implement responsive typography
- Ensure proper contrast for readability
- Use icons only for:
  - Main section headers
  - Key statistics or metrics
  - Navigation elements
- Maintain consistent styling across all articles
- Follow accessibility guidelines for content structure
