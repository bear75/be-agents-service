# Test Stack Documentation

## Overview

This document outlines the testing setup and conventions used in the Caire project.

## Test Stack

- **Framework**: Vitest
- **Testing Libraries**:
  - `@testing-library/react`
  - `@testing-library/jest-dom`
  - `@testing-library/user-event`
  - `@hookform/resolvers/zod` for form validation testing
  - `@vitest/coverage-v8` for code coverage

## Directory Structure

```
src/
├── test/
│   ├── setup.ts           # Global test setup and mocks
│   └── test-utils.tsx     # Common test utilities and helpers
└── components/
    ├── ComponentName.tsx
    └── __tests__/
        └── ComponentName.test.tsx
```

## Test Setup

### Global Setup (`src/test/setup.ts`)

- Jest DOM matchers
- Global mocks:
  - ResizeObserver
  - IntersectionObserver
  - matchMedia
  - Supabase client
  - Toast notifications
  - Email service
  - User service
  - Analytics tracking
- Automatic cleanup after each test

### Test Utilities (`src/test/test-utils.tsx`)

- Common test data constants
- Render helpers with providers (including Toaster)
- Mock service implementations
- User event setup helper
- Supabase response mocking helper
- Toast notification testing utilities
- Analytics tracking mocks

## Conventions

### File Naming and Location

- Test files should be named `*.test.ts(x)` or `*.spec.ts(x)`
- Place tests in `__tests__` directory next to source files
- Match test file name to component/function being tested

### Writing Tests

1. **Component Tests**:

   ```typescript
   import { screen, waitFor } from '@testing-library/react';
   import { describe, it, expect } from 'vitest';
   import { renderWithProviders, setupUserEvent } from '@/test/test-utils';

   describe('ComponentName', () => {
     it('should render correctly', () => {
       renderWithProviders(<Component />);
       // assertions...
     });
   });
   ```

2. **Form Tests**:

   ```typescript
   it('validates form input', async () => {
     const user = setupUserEvent();
     renderWithProviders(<ContactForm />);

     await user.type(screen.getByLabelText(/name/i), 'Test User');
     await user.type(screen.getByLabelText(/email/i), 'test@example.com');
     await user.type(screen.getByLabelText(/message/i), 'Test message content');
     await user.click(screen.getByLabelText(/gdpr/i));

     await user.click(screen.getByRole('button', { name: /send/i }));

     await waitFor(() => {
       expect(screen.getByText(/message sent/i)).toBeInTheDocument();
     });
   });
   ```

3. **Service Tests**:

   ```typescript
   it('handles service calls', async () => {
     const mockEmailService = vi.spyOn(emailService, 'sendContactForm');
     const mockUserService = vi.spyOn(userService, 'createOrUpdateUser');
     const mockAnalytics = vi.spyOn(analytics, 'trackEvent');

     renderWithProviders(<Component />);

     // Trigger action that calls services

     await waitFor(() => {
       expect(mockEmailService).toHaveBeenCalled();
       expect(mockUserService).toHaveBeenCalled();
       expect(mockAnalytics).toHaveBeenCalledWith('form_submission', expect.any(Object));
     });
   });
   ```

### Common Test Data

```typescript
export const TEST_DATA = {
  email: "test@example.com",
  name: "Test User",
  message: "This is a test message",
  subject: "Test Subject",
  gdprConsent: true,
};
```

## Mocking

### Services

1. **Email Service**:

   ```typescript
   vi.spyOn(emailService, "sendContactForm").mockResolvedValue({
     success: true,
     message: "Email sent successfully",
   });
   ```

2. **User Service**:

   ```typescript
   vi.spyOn(userService, "createOrUpdateUser").mockResolvedValue({
     id: "test-user-id",
     email: TEST_DATA.email,
   });
   ```

3. **Analytics**:

   ```typescript
   vi.spyOn(analytics, "trackEvent").mockImplementation((event, data) => {
     console.log("Tracked event:", event, data);
   });
   ```

4. **Toast Notifications**:
   ```typescript
   // Automatically mocked in setup.ts
   expect(screen.getByText(/message sent/i)).toBeInTheDocument();
   ```

## Coverage Requirements

- Statements: 80%
- Branches: 80%
- Functions: 80%
- Lines: 80%

## Best Practices

1. Use `renderWithProviders` instead of plain render
2. Use `setupUserEvent` for user interactions
3. Use shared test constants from TEST_DATA
4. Mock services in setup.ts
5. Write focused, isolated tests
6. Use meaningful test descriptions
7. Follow the Arrange-Act-Assert pattern
8. Clean up after each test (automatic)
9. Test both success and error cases
10. Verify toast notifications for user feedback
11. Test analytics tracking
12. Mock external services

## Currently Tested Features

### Contact Form

- Form validation
  - Name minimum length
  - Valid email format
  - Message minimum length
  - GDPR consent required
- Submission flow
  - User creation/update
  - Consent recording
  - Email sending
  - Analytics tracking
  - Success notification
- Error handling
  - Validation errors
  - Service errors
  - Error notifications

### User Service

- User creation and updates
- Consent management
- Communication logging
- Analytics tracking

### Email Service

- Contact form emails
- Newsletter emails
- Whitepaper emails
- Error handling
- Analytics tracking

### Analytics Service

- Event tracking
- Page views
- Form submissions
- Error tracking
- User interactions

## Testing Animations and Interactions

### Animation Testing

1. Test animation triggers and completion
2. Verify animation timing and duration
3. Check reduced motion preferences handling
4. Test animation performance
5. Verify cleanup on unmount

Example:

```typescript
import { render, screen } from '@testing-library/react';
import { FadeInSection } from '@/components/animations/FadeInSection';

describe('FadeInSection', () => {
  it('renders children', () => {
    render(
      <FadeInSection>
        <div>Test content</div>
      </FadeInSection>
    );
    expect(screen.getByText('Test content')).toBeInTheDocument();
  });

  it('applies correct animation properties', () => {
    const { container } = render(
      <FadeInSection>
        <div>Test content</div>
      </FadeInSection>
    );
    const element = container.firstChild;
    expect(element).toHaveStyle({
      opacity: '0',
      transform: 'translateY(50px)'
    });
  });
});
```

### Interactive Element Testing

1. Test hover and click states
2. Verify keyboard navigation
3. Check touch interactions
4. Test loading states
5. Verify error handling

Example:

```typescript
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { InteractiveButton } from '@/components/InteractiveButton';

describe('InteractiveButton', () => {
  it('handles click events', async () => {
    const handleClick = vi.fn();
    render(<InteractiveButton onClick={handleClick}>Click me</InteractiveButton>);

    await userEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalled();
  });

  it('handles keyboard navigation', async () => {
    const handleClick = vi.fn();
    render(<InteractiveButton onClick={handleClick}>Click me</InteractiveButton>);

    const button = screen.getByText('Click me');
    button.focus();
    expect(button).toHaveFocus();

    fireEvent.keyDown(button, { key: 'Enter' });
    expect(handleClick).toHaveBeenCalled();
  });
});
```
