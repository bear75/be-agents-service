# Accessibility Guide

## Overview

This guide outlines accessibility requirements and best practices for new pages in Caire, ensuring WCAG 2.1 compliance and a better experience for all users.

## WCAG 2.1 Requirements

### 1. Perceivable

- Provide text alternatives for non-text content
- Provide captions and alternatives for multimedia
- Create content that can be presented in different ways
- Make it easier for users to see and hear content

### 2. Operable

- Make all functionality available from keyboard
- Give users enough time to read and use content
- Do not use content that causes seizures
- Help users navigate and find content

### 3. Understandable

- Make text readable and understandable
- Make content appear and operate in predictable ways
- Help users avoid and correct mistakes

### 4. Robust

- Maximize compatibility with current and future tools

## Semantic HTML

### 1. Document Structure

```typescript
// Use semantic HTML elements
const PageLayout = () => (
  <div role="document">
    <header role="banner">
      <nav role="navigation" aria-label="Main navigation">
        {/* Navigation content */}
      </nav>
    </header>

    <main role="main">
      <h1>Page Title</h1>
      {/* Main content */}
    </main>

    <footer role="contentinfo">
      {/* Footer content */}
    </footer>
  </div>
);
```

### 2. Content Structure

```typescript
// Proper heading hierarchy
const ContentSection = () => (
  <section aria-labelledby="section-title">
    <h2 id="section-title">Section Title</h2>
    <article>
      <h3>Article Title</h3>
      <p>Content...</p>
    </article>
  </section>
);
```

## ARIA Implementation

### 1. ARIA Landmarks

```typescript
// Proper ARIA landmarks
const PageContent = () => (
  <>
    <nav aria-label="Main">
      {/* Navigation items */}
    </nav>

    <main aria-label="Main content">
      {/* Main content */}
    </main>

    <aside aria-label="Complementary content">
      {/* Sidebar content */}
    </aside>
  </>
);
```

### 2. ARIA States and Properties

```typescript
// ARIA states for interactive elements
const InteractiveButton = ({ isExpanded, onClick }) => (
  <button
    aria-expanded={isExpanded}
    aria-controls="content-id"
    onClick={onClick}
  >
    {isExpanded ? 'Collapse' : 'Expand'}
  </button>
);
```

## Focus Management

### 1. Focus Indicators

```typescript
// Visible focus indicators
const FocusableButton = styled.button`
  &:focus-visible {
    outline: 2px solid #00FF7F;
    outline-offset: 2px;
  }
`;

// Focus trap for modals
const Modal = ({ isOpen, onClose }) => {
  const ref = useRef(null);

  useEffect(() => {
    if (isOpen) {
      const focusTrap = createFocusTrap(ref.current, {
        escapeDeactivates: true,
        allowOutsideClick: true
      });
      focusTrap.activate();
      return () => focusTrap.deactivate();
    }
  }, [isOpen]);

  return (
    <dialog ref={ref} aria-modal="true" role="dialog">
      {/* Modal content */}
    </dialog>
  );
};
```

### 2. Skip Links

```typescript
// Skip to main content link
const SkipLink = () => (
  <a
    href="#main-content"
    className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4"
  >
    Hoppa till huvudinnehåll
  </a>
);
```

## Forms

### 1. Form Labels and Controls

```typescript
// Accessible form controls
const FormField = ({ id, label, error, ...props }) => (
  <div role="group" aria-labelledby={`${id}-label`}>
    <label
      id={`${id}-label`}
      htmlFor={id}
      className="block text-sm font-medium"
    >
      {label}
    </label>
    <input
      id={id}
      aria-describedby={error ? `${id}-error` : undefined}
      aria-invalid={error ? "true" : undefined}
      {...props}
    />
    {error && (
      <div id={`${id}-error`} role="alert" className="text-red-500">
        {error}
      </div>
    )}
  </div>
);
```

### 2. Error Handling

```typescript
// Form error announcements
const FormErrors = ({ errors }) => (
  <div role="alert" aria-live="polite">
    {errors.map(error => (
      <p key={error.id} className="text-red-500">
        {error.message}
      </p>
    ))}
  </div>
);
```

## Images and Media

### 1. Image Alternatives

```typescript
// Accessible images
const AccessibleImage = ({ src, alt, caption }) => (
  <figure>
    <img src={src} alt={alt} />
    {caption && <figcaption>{caption}</figcaption>}
  </figure>
);

// Decorative images
const DecorativeImage = ({ src }) => (
  <img src={src} alt="" role="presentation" />
);
```

### 2. Video Accessibility

```typescript
// Accessible video player
const AccessibleVideo = ({ src, captions }) => (
  <div role="region" aria-label="Video player">
    <video controls>
      <source src={src} type="video/mp4" />
      <track
        kind="captions"
        src={captions}
        srcLang="sv"
        label="Svenska"
        default
      />
    </video>
  </div>
);
```

## Color and Contrast

### 1. Color Contrast

```typescript
// High contrast text
const HighContrastText = styled.p`
  color: ${props => props.theme.colors.highContrast};
  background-color: ${props => props.theme.colors.background};
`;

// Color independence
const StatusIndicator = ({ status }) => (
  <div
    className="flex items-center"
    aria-label={`Status: ${status}`}
  >
    <span className={`status-dot ${status}`} aria-hidden="true" />
    <span className="ml-2">{status}</span>
  </div>
);
```

### 2. Focus Visibility

```typescript
// Enhanced focus styles
const FocusableLink = styled(Link)`
  &:focus-visible {
    outline: 2px solid #00ff7f;
    outline-offset: 2px;
    box-shadow: 0 0 0 4px rgba(0, 255, 127, 0.2);
  }
`;
```

## Motion and Animation

### 1. Reduced Motion

```typescript
// Respect reduced motion preferences
const AnimatedComponent = () => {
  const prefersReducedMotion = usePrefersReducedMotion();

  return (
    <motion.div
      animate={{ opacity: 1, y: 0 }}
      initial={{ opacity: 0, y: 20 }}
      transition={{
        duration: prefersReducedMotion ? 0 : 0.5
      }}
    >
      Content
    </motion.div>
  );
};
```

### 2. Pause/Stop Controls

```typescript
// Controllable animations
const ControlledAnimation = () => {
  const [isPlaying, setIsPlaying] = useState(true);

  return (
    <div>
      <button
        onClick={() => setIsPlaying(!isPlaying)}
        aria-label={isPlaying ? 'Pausa animation' : 'Spela animation'}
      >
        {isPlaying ? 'Pause' : 'Play'}
      </button>
      <motion.div animate={isPlaying ? "animate" : "initial"}>
        Content
      </motion.div>
    </div>
  );
};
```

## Testing

### 1. Automated Testing

```typescript
// Accessibility testing with jest-axe
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Component Accessibility', () => {
  it('should have no accessibility violations', async () => {
    const { container } = render(<YourComponent />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 2. Manual Testing

- Screen reader testing with VoiceOver/NVDA
- Keyboard navigation testing
- High contrast mode testing
- Browser zoom testing
- Mobile accessibility testing

## Checklist

Before completing implementation:

- [ ] Semantic HTML structure
- [ ] Proper heading hierarchy
- [ ] ARIA landmarks implemented
- [ ] Focus management
- [ ] Form accessibility
- [ ] Image alternatives
- [ ] Color contrast
- [ ] Reduced motion support
- [ ] Keyboard navigation
- [ ] Screen reader testing
- [ ] Automated tests passing

## Common Issues

1. **Missing Focus Management**
   - Implement focus traps
   - Add skip links
   - Ensure visible focus
   - Handle modal focus

2. **Improper ARIA Usage**
   - Validate ARIA roles
   - Test with screen readers
   - Check ARIA states
   - Verify live regions

3. **Color Contrast Issues**
   - Check all text contrast
   - Test in high contrast
   - Provide alternatives
   - Verify focus visibility

## Next Steps

1. Implement accessibility features
2. Run automated tests
3. Perform manual testing
4. Document accessibility features
5. Monitor accessibility

Proceed to [Quality Checklist](quality-checklist.md)
