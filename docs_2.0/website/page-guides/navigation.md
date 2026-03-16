# Navigation Guide

## Overview

This guide covers the implementation of navigation elements for new pages in Caire, ensuring consistent user experience and proper routing.

## Navigation Components

### Main Navigation

1. Update `src/components/Navigation.tsx`:

```typescript
// Desktop menu item
<NavigationMenuItem>
  <Link
    to="/your-path"
    className="block select-none space-y-1 rounded-md p-3 leading-none no-underline outline-none transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground"
  >
    <div className="text-sm font-medium leading-none">Your Page Title</div>
    <p className="line-clamp-2 text-sm leading-snug text-muted-foreground">
      Brief description of your page
    </p>
  </Link>
</NavigationMenuItem>

// Mobile menu item
<SheetNavItem
  to="/your-path"
  onClick={() => setIsMenuOpen(false)}
>
  Your Page Title
</SheetNavItem>
```

### Footer Navigation

1. Update `src/components/Footer.tsx`:

```typescript
<div className="grid grid-cols-2 md:grid-cols-4 gap-8">
  <div>
    <h3 className="text-lg font-semibold mb-4">Section Title</h3>
    <ul className="space-y-2">
      <li>
        <Link
          to="/your-path"
          className="text-gray-400 hover:text-white transition-colors"
          onClick={() => window.scrollTo(0, 0)}
        >
          Your Page
        </Link>
      </li>
    </ul>
  </div>
</div>
```

### Breadcrumbs

1. Implement breadcrumb navigation:

```typescript
<nav aria-label="Breadcrumb" className="mb-4">
  <ol className="flex items-center space-x-2">
    <li>
      <Link
        to="/"
        className="text-gray-500 hover:text-gray-700"
        onClick={() => window.scrollTo(0, 0)}
      >
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

## Navigation Patterns

### 1. Section Organization

Organize pages under appropriate sections:

```
/tjanster/* - Services
  ├── /tjanster/service-1
  └── /tjanster/service-2
/funktioner/* - Features
  ├── /funktioner/feature-1
  └── /funktioner/feature-2
/om/* - About
  ├── /om/company
  └── /om/team
/kontakt - Contact
```

### 2. URL Structure

Follow URL naming conventions:

- Use kebab-case for URLs
- Keep URLs descriptive and concise
- Include relevant keywords for SEO
- Maintain consistent depth

### 3. Navigation State

Handle active states:

```typescript
const isActive = useMatch(path);

<Link
  to={path}
  className={cn(
    "nav-link",
    isActive && "text-[#00FF7F]"
  )}
>
  {title}
</Link>
```

## Scroll Behavior

### 1. Scroll to Top

Add scroll reset on navigation:

```typescript
// In src/App.tsx
function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

// Add inside Router
<Router>
  <ScrollToTop />
  <Routes>
    {/* routes */}
  </Routes>
</Router>
```

### 2. Smooth Scrolling

For in-page navigation:

```typescript
const scrollToSection = (id: string) => {
  const element = document.getElementById(id);
  element?.scrollIntoView({ behavior: "smooth" });
};
```

## Analytics Integration

Track navigation events:

```typescript
const handleNavClick = (item: string) => {
  trackEvent("navigation_click", {
    item_name: item,
    current_page: window.location.pathname,
  });
};
```

## Accessibility

### 1. Keyboard Navigation

Ensure keyboard accessibility:

```typescript
<Link
  to={path}
  className="focus:ring-2 focus:ring-[#00FF7F] focus:outline-none"
  role="menuitem"
  tabIndex={0}
>
  {title}
</Link>
```

### 2. ARIA Labels

Add proper ARIA attributes:

```typescript
<nav aria-label="Main navigation">
  <ul role="menubar">
    <li role="none">
      <Link role="menuitem" aria-current={isActive ? 'page' : undefined}>
        {title}
      </Link>
    </li>
  </ul>
</nav>
```

## Mobile Considerations

### 1. Responsive Menu

Handle mobile menu state:

```typescript
const [isMenuOpen, setIsMenuOpen] = useState(false);

<Sheet open={isMenuOpen} onOpenChange={setIsMenuOpen}>
  <SheetTrigger asChild>
    <Button variant="ghost" className="md:hidden">
      <Menu className="h-6 w-6" />
    </Button>
  </SheetTrigger>
  <SheetContent>
    {/* Mobile menu items */}
  </SheetContent>
</Sheet>
```

### 2. Touch Targets

Ensure proper sizing:

```typescript
<Link
  to={path}
  className="block py-3 px-4 min-h-[44px] min-w-[44px]"
>
  {title}
</Link>
```

## Testing

### 1. Navigation Tests

```typescript
describe('Navigation', () => {
  it('renders navigation items', () => {
    render(<Navigation />);
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('handles navigation clicks', async () => {
    render(<Navigation />);
    await userEvent.click(screen.getByText('Your Page'));
    expect(window.location.pathname).toBe('/your-path');
  });
});
```

### 2. Mobile Tests

```typescript
describe('Mobile Navigation', () => {
  it('opens mobile menu', async () => {
    render(<Navigation />);
    await userEvent.click(screen.getByLabelText('Open menu'));
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });
});
```

## Checklist

Before completing navigation implementation:

- [ ] Main navigation items added
- [ ] Mobile menu items added
- [ ] Footer links added
- [ ] Breadcrumbs implemented
- [ ] Scroll behavior configured
- [ ] Analytics tracking added
- [ ] Keyboard navigation tested
- [ ] Mobile responsiveness verified
- [ ] ARIA labels added
- [ ] Tests written

## Common Issues

1. **Scroll Issues**
   - Implement ScrollToTop component
   - Add onClick handlers
   - Test on different devices

2. **Mobile Menu Issues**
   - Verify touch targets
   - Test menu closing
   - Check scroll locking

3. **Active State Issues**
   - Use proper route matching
   - Handle nested routes
   - Test edge cases

## Next Steps

1. Implement page content
2. Add analytics tracking
3. Test navigation flow
4. Update documentation

Proceed to [Content Implementation Guide](content.md)
