# Performance Guide

## Overview

This guide outlines performance optimization strategies and best practices for new pages in Caire. It covers loading optimization, rendering performance, and monitoring.

## Core Web Vitals

### 1. Performance Metrics

- **LCP (Largest Contentful Paint)**: < 2.5s
- **FID (First Input Delay)**: < 100ms
- **CLS (Cumulative Layout Shift)**: < 0.1
- **FCP (First Contentful Paint)**: < 1.8s
- **TTI (Time to Interactive)**: < 3.8s

### 2. Monitoring Setup

```typescript
// Performance monitoring
export const trackWebVitals = () => {
  if (typeof window !== "undefined") {
    // Track LCP
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        analytics.trackPerformance("LCP", entry.startTime);
      });
    }).observe({ entryTypes: ["largest-contentful-paint"] });

    // Track FID
    new PerformanceObserver((entryList) => {
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        analytics.trackPerformance(
          "FID",
          entry.processingStart - entry.startTime,
        );
      });
    }).observe({ entryTypes: ["first-input"] });

    // Track CLS
    new PerformanceObserver((entryList) => {
      let clsValue = 0;
      const entries = entryList.getEntries();
      entries.forEach((entry) => {
        if (!entry.hadRecentInput) {
          clsValue += entry.value;
        }
      });
      analytics.trackPerformance("CLS", clsValue);
    }).observe({ entryTypes: ["layout-shift"] });
  }
};
```

## Code Splitting

### 1. Route-based Splitting

```typescript
// In src/App.tsx
import { lazy, Suspense } from 'react';

const YourPage = lazy(() => import('./pages/YourPage'));

function App() {
  return (
    <Suspense fallback={<PageSkeleton />}>
      <Routes>
        <Route path="/your-path" element={<YourPage />} />
      </Routes>
    </Suspense>
  );
}
```

### 2. Component-level Splitting

```typescript
// Heavy component with dynamic import
const HeavyComponent = lazy(() => import('./components/HeavyComponent'));

function YourPage() {
  return (
    <div>
      <Suspense fallback={<ComponentSkeleton />}>
        <HeavyComponent />
      </Suspense>
    </div>
  );
}
```

## Image Optimization

### 1. Responsive Images

```typescript
// Optimized image component
const OptimizedImage = ({ src, alt, sizes }: ImageProps) => {
  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      decoding="async"
      sizes={sizes}
      className="w-full h-auto"
    />
  );
};

// Usage with srcset
<OptimizedImage
  src="/images/hero.jpg"
  alt="Hero image"
  sizes="(max-width: 768px) 100vw, 50vw"
  srcSet="/images/hero-300.jpg 300w,
          /images/hero-600.jpg 600w,
          /images/hero-900.jpg 900w"
/>
```

### 2. Image Loading Strategy

```typescript
// Progressive image loading
const ProgressiveImage = ({ lowQuality, highQuality, alt }: ProgressiveImageProps) => {
  const [loaded, setLoaded] = useState(false);

  return (
    <div className="relative">
      <img
        src={lowQuality}
        alt={alt}
        className={cn(
          "transition-opacity duration-300",
          loaded ? "opacity-0" : "opacity-100"
        )}
      />
      <img
        src={highQuality}
        alt={alt}
        onLoad={() => setLoaded(true)}
        className={cn(
          "absolute top-0 left-0 transition-opacity duration-300",
          loaded ? "opacity-100" : "opacity-0"
        )}
      />
    </div>
  );
};
```

## State Management

### 1. Memoization

```typescript
// Memoize expensive calculations
const memoizedValue = useMemo(() => {
  return expensiveCalculation(props.data);
}, [props.data]);

// Memoize callbacks
const memoizedCallback = useCallback(() => {
  handleAction(props.id);
}, [props.id]);

// Memoize components
const MemoizedComponent = memo(({ data }) => {
  return <div>{/* Render data */}</div>;
});
```

### 2. State Updates

```typescript
// Batch state updates
const handleAction = () => {
  setBatchedState((prev) => ({
    ...prev,
    value1: newValue1,
    value2: newValue2,
  }));
};

// Use reducers for complex state
const [state, dispatch] = useReducer(reducer, initialState);
```

## Data Fetching

### 1. Data Caching

```typescript
// Cache data with React Query
const { data, isLoading } = useQuery({
  queryKey: ["data", id],
  queryFn: () => fetchData(id),
  staleTime: 5 * 60 * 1000, // 5 minutes
  cacheTime: 30 * 60 * 1000, // 30 minutes
});
```

### 2. Prefetching

```typescript
// Prefetch on hover
const prefetchOnHover = () => {
  queryClient.prefetchQuery({
    queryKey: ["data", nextId],
    queryFn: () => fetchData(nextId),
  });
};
```

## Animation Performance

### 1. CSS Animations

```typescript
// Use CSS transforms and opacity
const AnimatedComponent = () => (
  <div className="transform transition-transform hover:scale-105">
    Content
  </div>
);

// Use will-change for heavy animations
const HeavyAnimation = () => (
  <div className="will-change-transform">
    Animated content
  </div>
);
```

### 2. Framer Motion Optimization

```typescript
// Optimize animations with Framer Motion
const OptimizedAnimation = () => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{
      duration: 0.5,
      type: "spring",
      stiffness: 100,
      damping: 15
    }}
    style={{
      willChange: "transform",
      backfaceVisibility: "hidden"
    }}
  >
    Content
  </motion.div>
);
```

## Bundle Optimization

### 1. Import Optimization

```typescript
// Use named imports
import { Button } from "@/components/ui/button";

// Avoid importing entire libraries
import { map } from "lodash-es/map";
```

### 2. Tree Shaking

```typescript
// Export individual components
export { Button } from "./Button";
export { Card } from "./Card";

// Use barrel exports carefully
export * from "./components";
```

## Performance Testing

### 1. Lighthouse CI

```yaml
# .github/workflows/lighthouse.yml
name: Lighthouse CI
on: [push]
jobs:
  lighthouse:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run Lighthouse CI
        uses: treosh/lighthouse-ci-action@v3
        with:
          urls: |
            https://staging.caire.se/your-page
          budgetPath: ./budget.json
          uploadArtifacts: true
```

### 2. Performance Budget

```json
{
  "performance-budget": {
    "resourceSizes": [
      {
        "resourceType": "script",
        "budget": 300
      },
      {
        "resourceType": "total",
        "budget": 1000
      }
    ],
    "resourceCounts": [
      {
        "resourceType": "third-party",
        "budget": 10
      }
    ]
  }
}
```

## Checklist

Before deployment:

- [ ] Core Web Vitals optimized
- [ ] Images optimized
- [ ] Code splitting implemented
- [ ] State management optimized
- [ ] Data fetching optimized
- [ ] Animations optimized
- [ ] Bundle size optimized
- [ ] Performance tests passing
- [ ] No layout shifts
- [ ] Loading states implemented

## Common Issues

1. **Large Bundle Size**
   - Implement code splitting
   - Optimize imports
   - Remove unused code
   - Use tree shaking

2. **Slow Initial Load**
   - Optimize critical path
   - Implement preloading
   - Use loading strategies
   - Cache effectively

3. **Layout Shifts**
   - Reserve space for content
   - Use proper image dimensions
   - Handle font loading
   - Minimize dynamic content

## Next Steps

1. Implement performance optimizations
2. Run performance tests
3. Monitor metrics
4. Document optimizations
5. Set up monitoring

Proceed to [Accessibility Guide](accessibility.md)
