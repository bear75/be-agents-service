# Testing Patterns

## Overview

This document outlines testing patterns and best practices used throughout Caire.

## Test Structure

### Basic Test Setup

```typescript
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Component } from './Component';

describe('Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders correctly', () => {
    render(<Component />);
    expect(screen.getByRole('heading')).toBeInTheDocument();
  });
});
```

## Common Test Patterns

### 1. Component Rendering

```typescript
describe('Component Rendering', () => {
  it('renders with default props', () => {
    render(<Component />);
    expect(screen.getByRole('heading')).toHaveTextContent('Default Title');
  });

  it('renders with custom props', () => {
    render(<Component title="Custom Title" />);
    expect(screen.getByRole('heading')).toHaveTextContent('Custom Title');
  });

  it('renders children correctly', () => {
    render(
      <Component>
        <div data-testid="child">Child Content</div>
      </Component>
    );
    expect(screen.getByTestId('child')).toBeInTheDocument();
  });
});
```

### 2. User Interactions

```typescript
describe('User Interactions', () => {
  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click Me</Button>);

    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('handles form submission', async () => {
    const handleSubmit = vi.fn();
    render(<Form onSubmit={handleSubmit} />);

    await userEvent.type(screen.getByLabelText('Name'), 'John Doe');
    await userEvent.click(screen.getByRole('button', { name: /submit/i }));

    expect(handleSubmit).toHaveBeenCalledWith(expect.objectContaining({
      name: 'John Doe'
    }));
  });
});
```

### 3. Async Operations

```typescript
describe('Async Operations', () => {
  it('loads data correctly', async () => {
    const mockData = { id: 1, name: 'Test' };
    vi.spyOn(api, 'fetchData').mockResolvedValue(mockData);

    render(<DataComponent />);

    expect(screen.getByRole('status')).toHaveTextContent('Loading...');
    await screen.findByText(mockData.name);
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('handles errors', async () => {
    vi.spyOn(api, 'fetchData').mockRejectedValue(new Error('Failed to load'));

    render(<DataComponent />);

    await screen.findByText(/error/i);
    expect(screen.getByText(/failed to load/i)).toBeInTheDocument();
  });
});
```

### 4. Route Testing

```typescript
describe('Route Testing', () => {
  it('navigates correctly', () => {
    render(
      <MemoryRouter initialEntries={['/']}>
        <App />
      </MemoryRouter>
    );

    userEvent.click(screen.getByText('Go to About'));
    expect(screen.getByRole('heading')).toHaveTextContent('About Page');
  });

  it('handles protected routes', () => {
    const { rerender } = render(
      <AuthContext.Provider value={{ isAuthenticated: false }}>
        <ProtectedRoute>
          <SecretPage />
        </ProtectedRoute>
      </AuthContext.Provider>
    );

    expect(screen.getByText(/login required/i)).toBeInTheDocument();

    rerender(
      <AuthContext.Provider value={{ isAuthenticated: true }}>
        <ProtectedRoute>
          <SecretPage />
        </ProtectedRoute>
      </AuthContext.Provider>
    );

    expect(screen.getByText(/secret content/i)).toBeInTheDocument();
  });
});
```

### 5. Hook Testing

```typescript
describe("Hook Testing", () => {
  it("manages state correctly", () => {
    const { result } = renderHook(() => useCounter());

    expect(result.current.count).toBe(0);

    act(() => {
      result.current.increment();
    });

    expect(result.current.count).toBe(1);
  });

  it("handles async operations", async () => {
    const { result } = renderHook(() => useData());

    expect(result.current.loading).toBe(true);

    await waitFor(() => {
      expect(result.current.data).toBeDefined();
    });

    expect(result.current.loading).toBe(false);
  });
});
```

## Mocking Patterns

### 1. API Mocks

```typescript
vi.mock('@/api', () => ({
  fetchData: vi.fn(),
  updateData: vi.fn()
}));

describe('API Integration', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches and displays data', async () => {
    const mockData = { id: 1, name: 'Test' };
    (api.fetchData as Mock).mockResolvedValue(mockData);

    render(<DataComponent />);
    await screen.findByText(mockData.name);

    expect(api.fetchData).toHaveBeenCalledTimes(1);
  });
});
```

### 2. Component Mocks

```typescript
vi.mock('./ComplexComponent', () => ({
  ComplexComponent: () => <div data-testid="mocked">Mocked Component</div>
}));

describe('Component with Dependencies', () => {
  it('renders with mocked dependency', () => {
    render(<ParentComponent />);
    expect(screen.getByTestId('mocked')).toBeInTheDocument();
  });
});
```

### 3. Context Mocks

```typescript
const mockAuthContext = {
  user: null,
  login: vi.fn(),
  logout: vi.fn()
};

describe('Component with Context', () => {
  it('uses context values', () => {
    render(
      <AuthContext.Provider value={mockAuthContext}>
        <Component />
      </AuthContext.Provider>
    );

    expect(screen.getByText(/please login/i)).toBeInTheDocument();
  });
});
```

## Test Utilities

### 1. Custom Renders

```typescript
const renderWithProviders = (
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = configureStore({ reducer: rootReducer, preloadedState }),
    ...renderOptions
  } = {}
) => {
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <Provider store={store}>
      <ThemeProvider>
        <Router>{children}</Router>
      </ThemeProvider>
    </Provider>
  );

  return render(ui, { wrapper: Wrapper, ...renderOptions });
};
```

### 2. Custom Matchers

```typescript
expect.extend({
  toHaveBeenCalledWithMatch(received: Mock, expected: object) {
    const pass = received.mock.calls.some((call) =>
      expect.objectContaining(expected).asymmetricMatch(call[0]),
    );

    return {
      pass,
      message: () =>
        `expected ${received.getMockName()} to have been called with match ${JSON.stringify(expected)}`,
    };
  },
});
```

## Best Practices

1. **Test Organization**
   - Group related tests
   - Use clear descriptions
   - Follow AAA pattern (Arrange, Act, Assert)
   - Keep tests focused

2. **Test Coverage**
   - Test component rendering
   - Test user interactions
   - Test error states
   - Test loading states
   - Test edge cases

3. **Mocking**
   - Mock external dependencies
   - Use meaningful mock data
   - Clear mocks between tests
   - Document mock behavior

4. **Async Testing**
   - Use proper async utilities
   - Handle loading states
   - Test error scenarios
   - Verify cleanup

5. **Accessibility Testing**
   - Test keyboard navigation
   - Verify ARIA attributes
   - Check screen reader compatibility
   - Test focus management

## Common Issues and Solutions

1. **Async Test Issues**
   - Use proper async utilities
   - Handle timeouts
   - Clear pending timers
   - Wait for animations

2. **State Management Issues**
   - Clear state between tests
   - Use proper act() wrapper
   - Handle side effects
   - Test state transitions

3. **Mock Issues**
   - Clear mocks between tests
   - Verify mock calls
   - Handle mock rejections
   - Document mock behavior

4. **Integration Issues**
   - Mock external services
   - Handle network requests
   - Test error boundaries
   - Verify cleanup
