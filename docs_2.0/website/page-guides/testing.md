# Testing Guide

## Overview

This guide outlines the testing requirements and best practices for new pages in Caire. It covers unit testing, integration testing, and end-to-end testing approaches.

## Test Setup

### 1. Test Environment

```typescript
// src/test/setup.ts
import "@testing-library/jest-dom";
import { vi } from "vitest";

// Mock ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

// Mock matchMedia
global.matchMedia = vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));
```

### 2. Test Utilities

```typescript
// src/test/test-utils.tsx
import { render } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { Toaster } from '@/components/ui/toaster';

export const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <>
      {ui}
      <Toaster />
    </>,
    { wrapper: BrowserRouter }
  );
};

export const setupUserEvent = () => userEvent.setup();
```

## Component Testing

### 1. Basic Component Tests

```typescript
import { screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { renderWithProviders } from '@/test/test-utils';
import YourPage from './YourPage';

describe('YourPage', () => {
  it('renders page title', () => {
    renderWithProviders(<YourPage />);
    expect(screen.getByRole('heading', { level: 1 }))
      .toHaveTextContent('Expected Title');
  });

  it('displays content sections', () => {
    renderWithProviders(<YourPage />);
    expect(screen.getByTestId('hero-section')).toBeInTheDocument();
    expect(screen.getByTestId('features-section')).toBeInTheDocument();
    expect(screen.getByTestId('cta-section')).toBeInTheDocument();
  });
});
```

### 2. Interactive Tests

```typescript
import { screen, waitFor } from '@testing-library/react';
import { setupUserEvent } from '@/test/test-utils';

describe('Interactive Elements', () => {
  it('handles button clicks', async () => {
    const user = setupUserEvent();
    renderWithProviders(<YourPage />);

    await user.click(screen.getByRole('button', { name: /boka demo/i }));

    await waitFor(() => {
      expect(screen.getByText(/tack för din bokning/i)).toBeInTheDocument();
    });
  });

  it('validates form input', async () => {
    const user = setupUserEvent();
    renderWithProviders(<YourPage />);

    await user.type(screen.getByLabelText(/namn/i), 'Test User');
    await user.type(screen.getByLabelText(/email/i), 'invalid-email');
    await user.click(screen.getByRole('button', { name: /skicka/i }));

    expect(screen.getByText(/ogiltig e-postadress/i)).toBeInTheDocument();
  });
});
```

## Integration Testing

### 1. Route Testing

```typescript
import { screen, waitFor } from '@testing-library/react';
import { createMemoryRouter, RouterProvider } from 'react-router-dom';

describe('Page Navigation', () => {
  it('navigates to correct route', async () => {
    const router = createMemoryRouter(routes, {
      initialEntries: ['/your-page'],
    });

    renderWithProviders(<RouterProvider router={router} />);

    await waitFor(() => {
      expect(screen.getByRole('heading')).toHaveTextContent('Expected Title');
    });
  });
});
```

### 2. Data Integration

```typescript
describe('Data Integration', () => {
  it('loads and displays data', async () => {
    vi.spyOn(dataService, 'fetchData').mockResolvedValue(mockData);

    renderWithProviders(<YourPage />);

    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(mockData.title)).toBeInTheDocument();
    });
  });

  it('handles error states', async () => {
    vi.spyOn(dataService, 'fetchData').mockRejectedValue(new Error('Failed'));

    renderWithProviders(<YourPage />);

    await waitFor(() => {
      expect(screen.getByText(/kunde inte ladda data/i)).toBeInTheDocument();
    });
  });
});
```

## Service Testing

### 1. API Integration

```typescript
describe('API Integration', () => {
  it('makes correct API calls', async () => {
    const mockApi = vi.spyOn(api, 'post');

    renderWithProviders(<YourPage />);
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(mockApi).toHaveBeenCalledWith('/endpoint', expect.any(Object));
  });
});
```

### 2. Analytics Testing

```typescript
describe('Analytics', () => {
  it('tracks page view', () => {
    const mockTrack = vi.spyOn(analytics, 'trackPageView');

    renderWithProviders(<YourPage />);

    expect(mockTrack).toHaveBeenCalledWith({
      page_title: 'Your Page',
      page_path: '/your-page'
    });
  });

  it('tracks user interactions', async () => {
    const mockTrack = vi.spyOn(analytics, 'trackEvent');
    const user = setupUserEvent();

    renderWithProviders(<YourPage />);
    await user.click(screen.getByRole('button', { name: /cta/i }));

    expect(mockTrack).toHaveBeenCalledWith('cta_click', expect.any(Object));
  });
});
```

## Performance Testing

### 1. Load Time Tests

```typescript
describe('Performance', () => {
  it('renders within performance budget', async () => {
    const startTime = performance.now();

    renderWithProviders(<YourPage />);
    await screen.findByRole('heading');

    const endTime = performance.now();
    expect(endTime - startTime).toBeLessThan(200);
  });
});
```

### 2. Memory Usage

```typescript
describe('Memory Usage', () => {
  it('cleans up resources', () => {
    const { unmount } = renderWithProviders(<YourPage />);

    unmount();

    // Verify cleanup
    expect(mockObserver.disconnect).toHaveBeenCalled();
  });
});
```

## Accessibility Testing

### 1. A11y Tests

```typescript
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

describe('Accessibility', () => {
  it('has no accessibility violations', async () => {
    const { container } = renderWithProviders(<YourPage />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### 2. Keyboard Navigation

```typescript
describe('Keyboard Navigation', () => {
  it('supports keyboard interaction', async () => {
    const user = setupUserEvent();
    renderWithProviders(<YourPage />);

    await user.tab();
    expect(screen.getByRole('link', { name: /start/i })).toHaveFocus();

    await user.tab();
    expect(screen.getByRole('button', { name: /menu/i })).toHaveFocus();
  });
});
```

## Test Coverage

### 1. Coverage Requirements

- Statements: 80%
- Branches: 80%
- Functions: 80%
- Lines: 80%

### 2. Coverage Report

```bash
# Run tests with coverage
npm run test:coverage
```

## Checklist

Before completing testing:

- [ ] Unit tests written
- [ ] Integration tests written
- [ ] Service tests written
- [ ] Performance tests written
- [ ] Accessibility tests written
- [ ] Coverage requirements met
- [ ] All tests passing
- [ ] Edge cases covered
- [ ] Error states tested
- [ ] Analytics verified

## Common Issues

1. **Async Testing**
   - Use waitFor for async operations
   - Handle loading states
   - Test error scenarios
   - Verify cleanup

2. **Mock Issues**
   - Properly mock external services
   - Reset mocks between tests
   - Verify mock calls
   - Clean up after tests

3. **Coverage Gaps**
   - Identify uncovered code
   - Add missing tests
   - Test edge cases
   - Document exclusions

## Next Steps

1. Write component tests
2. Add integration tests
3. Verify accessibility
4. Check test coverage
5. Document test cases

Proceed to [Performance Guide](performance.md)
