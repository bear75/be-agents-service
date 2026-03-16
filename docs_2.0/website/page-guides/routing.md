# Route Configuration Guide

## Overview

This guide covers the process of adding routes for new pages in Caire, ensuring proper navigation and URL structure.

## Route Structure

### Basic Route Setup

Add your route in `src/App.tsx`:

```typescript
import { lazy } from 'react';
import { Routes, Route } from 'react-router-dom';

const YourPage = lazy(() => import('./pages/YourPage'));

// In the Routes component:
<Route path="/your-path" element={<YourPage />} />
```

### Nested Routes

For pages with subroutes:

```typescript
<Route path="/your-path">
  <Route index element={<YourPage />} />
  <Route path="subpage" element={<SubPage />} />
</Route>
```

## URL Structure

Follow these conventions for URLs:

1. Main sections:
   - `/tjanster/*` - Services
   - `/funktioner/*` - Features
   - `/om/*` - About
   - `/kontakt` - Contact

2. Feature pages:
   - `/funktioner/your-feature`
   - `/funktioner/your-feature/details`

3. Service pages:
   - `/tjanster/your-service`
   - `/tjanster/your-service/details`

## Navigation Setup

### Main Navigation

Update `src/components/Navigation.tsx`:

```typescript
// Desktop menu
<NavigationMenuItem>
  <Link
    to="/your-path"
    className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
  >
    <div className="text-sm font-medium leading-none">Your Page</div>
    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
      Brief description
    </p>
  </Link>
</NavigationMenuItem>

// Mobile menu
<SheetNavItem to="/your-path">
  Your Page
</SheetNavItem>
```

### Breadcrumbs

Add breadcrumb navigation:

```typescript
<nav aria-label="Breadcrumb">
  <ol className="flex items-center space-x-2">
    <li>
      <Link to="/" className="text-gray-500 hover:text-gray-700">
        Home
      </Link>
    </li>
    <li className="text-gray-300">/</li>
    <li>
      <span className="text-gray-900">Your Page</span>
    </li>
  </ol>
</nav>
```

### Footer Links

Update `src/components/Footer.tsx` to include your new page:

```typescript
// Footer section links
<div className="grid grid-cols-2 md:grid-cols-4 gap-8">
  <div>
    <h3 className="text-lg font-semibold mb-4">Section Title</h3>
    <ul className="space-y-2">
      <li>
        <Link
          to="/your-path"
          className="text-gray-400 hover:text-white transition-colors"
          onClick={() => window.scrollTo(0, 0)} // Ensure page starts at top
        >
          Your Page
        </Link>
      </li>
    </ul>
  </div>
</div>
```

### Scroll Behavior

1. Add scroll reset on navigation:

```typescript
// In src/App.tsx
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// Add inside the Router component
<Router>
  <ScrollToTop />
  <Routes>
    // ... your routes
  </Routes>
</Router>
```

2. For individual links, add onClick handler:

```typescript
<Link
  to="/your-path"
  onClick={() => window.scrollTo(0, 0)}
>
  Your Page
</Link>
```

3. Update all navigation components to include scroll reset:
   - Main navigation links
   - Footer links
   - Breadcrumb links
   - CTA buttons that link to pages

## Route Guards

### Authentication

For protected routes:

```typescript
const ProtectedRoute = ({ children }: { children: React.ReactNode }) => {
  const { user } = useAuth();

  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
};

// Usage
<Route
  path="/protected"
  element={
    <ProtectedRoute>
      <YourPage />
    </ProtectedRoute>
  }
/>
```

### Role-Based Access

For role-specific routes:

```typescript
const RoleRoute = ({
  children,
  requiredRole
}: {
  children: React.ReactNode;
  requiredRole: string;
}) => {
  const { user, role } = useAuth();

  if (!user || role !== requiredRole) {
    return <Navigate to="/unauthorized" replace />;
  }

  return <>{children}</>;
};
```

## Error Handling

### 404 Page

Create a NotFound component:

```typescript
const NotFound = () => (
  <main className="pt-24 pb-16">
    <div className="container mx-auto px-4 text-center">
      <h1 className="text-4xl font-bold mb-4">Page Not Found</h1>
      <p className="mb-8">The page you're looking for doesn't exist.</p>
      <Link
        to="/"
        className="inline-flex items-center justify-center px-4 py-2 border border-transparent text-base font-medium rounded-md text-white bg-primary hover:bg-primary/90"
      >
        Go Home
      </Link>
    </div>
  </main>
);

// Add catch-all route
<Route path="*" element={<NotFound />} />
```

## Testing

### Route Tests

```typescript
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import App from './App';

describe('Routing', () => {
  it('renders your page at correct route', () => {
    render(
      <MemoryRouter initialEntries={['/your-path']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByRole('heading')).toHaveTextContent('Your Page');
  });

  it('renders 404 for unknown route', () => {
    render(
      <MemoryRouter initialEntries={['/unknown']}>
        <App />
      </MemoryRouter>
    );

    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  });
});
```

## Checklist

Before completing route configuration:

- [ ] Route added to App.tsx
- [ ] Navigation menu items added
- [ ] Breadcrumbs implemented
- [ ] Route guards added if needed
- [ ] 404 handling implemented
- [ ] Tests written
- [ ] URLs follow conventions
- [ ] Navigation working on mobile
- [ ] Active states showing correctly

## Common Issues

1. **Route Not Matching**
   - Check exact path spelling
   - Verify route order
   - Check for trailing slashes

2. **Navigation Not Updating**
   - Verify Link components
   - Check onClick handlers
   - Test active state logic

3. **Protected Route Issues**
   - Verify auth state
   - Check redirect logic
   - Test error handling

## Next Steps

1. Implement page content
2. Add analytics tracking
3. Test navigation flow
4. Document route structure

Proceed to [Navigation Guide](navigation.md)
