# Analytics Implementation

## Overview

This document outlines analytics implementation patterns and best practices used throughout Caire.

## Event Tracking

### Page Views

```typescript
// In page components
useEffect(() => {
  trackPageView({
    path: "/your-path",
    title: "Page Title | Caire",
    section: "Features",
  });
}, []);
```

### User Interactions

```typescript
// Button clicks
const handleClick = () => {
  trackEvent("button_click", {
    button_name: "cta_button",
    page: "/your-path",
    section: "hero",
  });
};

// Form submissions
const handleSubmit = (data: FormData) => {
  trackEvent("form_submit", {
    form_name: "contact_form",
    form_type: "lead",
    page: "/your-path",
  });
};
```

### Section Views

```typescript
const SectionTracking = ({ children, sectionName }: SectionTrackingProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref);

  useEffect(() => {
    if (isInView) {
      trackEvent('section_view', {
        section_name: sectionName,
        page: window.location.pathname
      });
    }
  }, [isInView, sectionName]);

  return <div ref={ref}>{children}</div>;
};
```

## Common Events

### 1. Navigation Events

```typescript
// Menu interactions
const handleMenuClick = (item: string) => {
  trackEvent("menu_click", {
    menu_item: item,
    menu_type: "main_nav",
    current_page: window.location.pathname,
  });
};

// Footer links
const handleFooterClick = (link: string) => {
  trackEvent("footer_click", {
    link_name: link,
    link_type: "footer",
    current_page: window.location.pathname,
  });
};
```

### 2. Feature Usage

```typescript
// Feature interactions
const handleFeatureUse = (feature: string) => {
  trackEvent("feature_use", {
    feature_name: feature,
    feature_type: "tool",
    page: window.location.pathname,
  });
};

// Feature completion
const handleFeatureComplete = (feature: string) => {
  trackEvent("feature_complete", {
    feature_name: feature,
    duration: performance.now() - startTime,
    success: true,
  });
};
```

### 3. Error Tracking

```typescript
// Error handling
const handleError = (error: Error) => {
  trackEvent("error_occurred", {
    error_type: error.name,
    error_message: error.message,
    page: window.location.pathname,
    component: "FeatureComponent",
  });
};

// Form validation errors
const handleValidationError = (errors: ValidationErrors) => {
  trackEvent("form_error", {
    form_name: "contact_form",
    error_fields: Object.keys(errors),
    page: window.location.pathname,
  });
};
```

## Custom Hooks

### usePageTracking

```typescript
export const usePageTracking = (title: string) => {
  useEffect(() => {
    const path = window.location.pathname;
    trackPageView({
      path,
      title: `${title} | Caire`,
      referrer: document.referrer,
    });
  }, [title]);
};
```

### useSectionTracking

```typescript
export const useSectionTracking = (sectionName: string) => {
  const ref = useRef(null);
  const isInView = useInView(ref);

  useEffect(() => {
    if (isInView) {
      trackEvent("section_view", {
        section_name: sectionName,
        page: window.location.pathname,
        viewport_width: window.innerWidth,
      });
    }
  }, [isInView, sectionName]);

  return ref;
};
```

### useFeatureTracking

```typescript
export const useFeatureTracking = (featureName: string) => {
  const startTime = useRef(performance.now());

  const trackStart = () => {
    startTime.current = performance.now();
    trackEvent("feature_start", {
      feature_name: featureName,
      page: window.location.pathname,
    });
  };

  const trackComplete = (success: boolean) => {
    const duration = performance.now() - startTime.current;
    trackEvent("feature_complete", {
      feature_name: featureName,
      duration,
      success,
    });
  };

  return { trackStart, trackComplete };
};
```

## Event Categories

### 1. Page Events

- page_view
- page_exit
- page_scroll
- page_error

### 2. User Events

- user_signup
- user_login
- user_logout
- user_settings_change

### 3. Feature Events

- feature_start
- feature_complete
- feature_error
- feature_abandon

### 4. Form Events

- form_start
- form_submit
- form_error
- form_abandon

### 5. Navigation Events

- menu_click
- link_click
- button_click
- tab_change

## Best Practices

1. **Event Naming**
   - Use snake_case for event names
   - Keep names consistent
   - Use descriptive names
   - Follow naming conventions

2. **Event Properties**
   - Include page context
   - Add user context when relevant
   - Include timestamps
   - Add relevant metadata

3. **Implementation**
   - Use hooks for reusability
   - Track errors consistently
   - Handle async operations
   - Validate data before sending

4. **Performance**
   - Batch events when possible
   - Debounce frequent events
   - Handle offline scenarios
   - Monitor payload size

## Common Issues and Solutions

1. **Duplicate Events**
   - Use debouncing
   - Track unique identifiers
   - Implement cooldown periods
   - Validate before sending

2. **Missing Context**
   - Add page information
   - Include user context
   - Track environment data
   - Add timestamps

3. **Performance Issues**
   - Batch similar events
   - Optimize payload size
   - Use async tracking
   - Handle rate limiting

4. **Data Quality**
   - Validate event data
   - Sanitize user input
   - Handle edge cases
   - Monitor event quality

## Testing Analytics

```typescript
describe('Analytics Tracking', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('tracks page view on mount', () => {
    render(<Page title="Test Page" />);
    expect(trackPageView).toHaveBeenCalledWith({
      path: '/test',
      title: 'Test Page | Caire'
    });
  });

  it('tracks user interactions', async () => {
    render(<Feature name="test-feature" />);

    await userEvent.click(screen.getByRole('button'));
    expect(trackEvent).toHaveBeenCalledWith('feature_use', {
      feature_name: 'test-feature'
    });
  });
});
```
