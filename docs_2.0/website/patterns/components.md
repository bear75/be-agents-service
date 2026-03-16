# Component Patterns

## Overview

This document outlines common component patterns and best practices used throughout Caire.

## Component Organization

### Base Component Structure

```typescript
import { memo } from 'react';
import type { ComponentProps } from '@/types';

interface Props extends ComponentProps {
  title: string;
  description?: string;
}

export const Component = memo(({ title, description }: Props) => {
  return (
    <div className="component-wrapper">
      <h2>{title}</h2>
      {description && <p>{description}</p>}
    </div>
  );
});

Component.displayName = 'Component';
```

### Common Patterns

1. **Section Components**

```typescript
export const Section = memo(({ children, className }: SectionProps) => (
  <section className={cn(
    "py-20 relative overflow-hidden",
    className
  )}>
    <div className="container mx-auto px-4">
      {children}
    </div>
  </section>
));
```

2. **Card Components**

```typescript
export const Card = memo(({
  title,
  description,
  icon: Icon,
  className
}: CardProps) => (
  <div className={cn(
    "p-6 bg-white/5 rounded-lg backdrop-blur-sm",
    className
  )}>
    {Icon && (
      <div className="mb-4">
        <Icon className="w-6 h-6 text-[#00FF7F]" />
      </div>
    )}
    <h3 className="text-xl font-semibold mb-2">{title}</h3>
    <p className="text-white/60">{description}</p>
  </div>
));
```

3. **Form Components**

```typescript
export const FormField = memo(({
  label,
  error,
  children
}: FormFieldProps) => (
  <div className="space-y-2">
    <Label>{label}</Label>
    {children}
    {error && (
      <p className="text-red-500 text-sm">{error}</p>
    )}
  </div>
));
```

## Animation Patterns

### Fade In Section

```typescript
export const FadeInSection = memo(({ children }: { children: React.ReactNode }) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true });

  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={isInView ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
      transition={{ duration: 0.5 }}
    >
      {children}
    </motion.div>
  );
});
```

### Floating Element

```typescript
export const FloatingElement = memo(({ children }: { children: React.ReactNode }) => (
  <motion.div
    animate={{
      y: [0, -10, 0],
    }}
    transition={{
      duration: 4,
      repeat: Infinity,
      ease: "easeInOut"
    }}
  >
    {children}
  </motion.div>
));
```

## Loading States

### Skeleton Loading

```typescript
export const SkeletonCard = memo(() => (
  <div className="p-6 bg-white/5 rounded-lg animate-pulse">
    <div className="w-12 h-12 bg-white/10 rounded-full mb-4" />
    <div className="h-6 bg-white/10 rounded w-3/4 mb-2" />
    <div className="h-4 bg-white/10 rounded w-full" />
  </div>
));
```

### Loading Spinner

```typescript
export const LoadingSpinner = memo(() => (
  <div className="flex items-center justify-center">
    <motion.div
      className="w-6 h-6 border-2 border-[#00FF7F] rounded-full border-t-transparent"
      animate={{ rotate: 360 }}
      transition={{
        duration: 1,
        repeat: Infinity,
        ease: "linear"
      }}
    />
  </div>
));
```

## Error States

### Error Boundary

```typescript
export class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  { hasError: boolean }
> {
  state = { hasError: false };

  static getDerivedStateFromError() {
    return { hasError: true };
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="p-6 bg-red-500/10 rounded-lg text-center">
          <h2 className="text-xl font-semibold mb-2">Something went wrong</h2>
          <p className="text-white/60">Please try again later</p>
        </div>
      );
    }

    return this.props.children;
  }
}
```

### Error Message

```typescript
export const ErrorMessage = memo(({
  title = "Error",
  message
}: ErrorMessageProps) => (
  <div className="p-4 bg-red-500/10 rounded-lg">
    <h3 className="text-lg font-semibold mb-2">{title}</h3>
    <p className="text-white/60">{message}</p>
  </div>
));
```

## Form Patterns

### Input Field

```typescript
export const Input = memo(forwardRef<HTMLInputElement, InputProps>(({
  error,
  ...props
}, ref) => (
  <input
    ref={ref}
    className={cn(
      "w-full px-4 py-2 bg-white/5 rounded-lg focus:ring-2 focus:ring-[#00FF7F]",
      error && "ring-2 ring-red-500"
    )}
    {...props}
  />
)));
```

### Form Validation

```typescript
export const useFormValidation = (schema: ZodSchema) => {
  const form = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data: any) => {
    try {
      await schema.parseAsync(data);
      // Handle success
    } catch (error) {
      // Handle error
    }
  };

  return { form, onSubmit };
};
```

## Best Practices

1. **Component Organization**
   - Keep components focused and single-purpose
   - Use proper TypeScript types
   - Implement error boundaries
   - Handle loading states

2. **Performance**
   - Memoize components when beneficial
   - Use proper code splitting
   - Implement lazy loading
   - Optimize re-renders

3. **Accessibility**
   - Use semantic HTML
   - Add ARIA labels
   - Ensure keyboard navigation
   - Maintain proper heading hierarchy

4. **State Management**
   - Use hooks for local state
   - Implement proper data fetching
   - Handle loading states
   - Manage error boundaries

5. **Testing**
   - Write unit tests
   - Test edge cases
   - Verify accessibility
   - Check performance

## Common Issues and Solutions

1. **Re-render Issues**
   - Use memo for expensive components
   - Implement proper dependency arrays
   - Use callback functions
   - Split state logically

2. **Type Issues**
   - Define proper interfaces
   - Use utility types
   - Handle null/undefined
   - Document complex types

3. **Performance Issues**
   - Implement virtualization for long lists
   - Use proper image optimization
   - Implement code splitting
   - Optimize bundle size

4. **Accessibility Issues**
   - Add proper ARIA labels
   - Ensure keyboard navigation
   - Maintain focus management
   - Test with screen readers
