# Caire Website Styling Guidelines

## Overview

Your styling architecture uses a **multi-layered approach** combining:

1. **Tailwind CSS** as the primary utility framework
2. **CSS Custom Properties** for design tokens
3. **Component-specific styles** using `class-variance-authority` (CVA)
4. **Custom CSS classes** for specialized components
5. **Framer Motion** for animations

## 🎨 Design System

### Primary Colors

```typescript
// Tailwind Config (tailwind.config.ts)
colors: {
  primary: "#00FF7F",        // Bright green - main brand color
  "primary-dark": "#00CC66", // Darker green variant
}

// CSS Variables (index.css)
--primary: 222.2 47.4% 11.2%;
--primary-foreground: 210 40% 98%;
```

### Brand Color Usage

- **Primary Green (`#00FF7F`)**: CTAs, highlights, active states, brand elements
- **Variations**:
  - `#00FF7F/10` - 10% opacity for subtle backgrounds
  - `#00FF7F/20` - 20% opacity for hover states
  - `#00FF7F/90` - 90% opacity for hover effects on solid buttons

### Background System

```css
/* Base backgrounds */
body: linear-gradient(180deg, #050505 0%, #0a0a0a 100%)
cards: #0a0a0a (with opacity variations)
glass-panels: bg-white/[0.02] with backdrop-blur-sm

/* Gradient backgrounds */
hero-gradient: radial-gradient(circle at center, rgba(0, 255, 157, 0.15) 0%, transparent 70%)
```

## 🏗️ Architecture Layers

### 1. Base Layer (`@layer base`)

**Location**: `src/index.css`

```css
body {
  @apply bg-[#050505] text-white font-sans min-h-screen;
  background: linear-gradient(180deg, #050505 0%, #0a0a0a 100%);
}
```

### 2. Components Layer (`@layer components`)

**Location**: `src/index.css`

```css
.hero-gradient {
  /* Custom gradients */
}
.code-block {
  /* Code styling */
}
.neon-border {
  /* Glowing borders */
}
.glass-panel {
  /* Glass morphism */
}
.feature-card {
  /* Card components */
}
.nav-link {
  /* Navigation */
}
.btn-primary {
  /* Primary buttons */
}
```

### 3. Utilities Layer (`@layer utilities`)

**Location**: `src/index.css`

```css
.text-gradient {
  /* Text gradients */
}
.glow-hover {
  /* Hover effects */
}
.preview-grid {
  /* Grid patterns */
}
```

### 4. Component-Specific Styles

**Pattern**: Using `class-variance-authority` (CVA)

```typescript
// Example: src/components/ui/button.tsx
const buttonVariants = cva("base-classes", {
  variants: {
    variant: {
      default: "variant-specific-classes",
      destructive: "destructive-classes",
    },
    size: {
      sm: "small-size-classes",
      lg: "large-size-classes",
    },
  },
});
```

## 🎯 Component Patterns

### Button System

```typescript
// Primary CTA Button
className =
  "bg-[#00FF7F] hover:bg-[#00FF7F]/90 text-black font-medium px-8 py-3 rounded-md transition-all duration-300";

// Secondary Button
className = "bg-white/10 text-white hover:bg-white/20 border border-white/20";

// Outline Button
className =
  "bg-transparent border border-[#00FF7F] text-[#00FF7F] hover:bg-[#00FF7F]/10";
```

### Card System

```typescript
// Feature Card
className =
  "bg-[#0a0a0a]/80 backdrop-blur-sm rounded-xl p-6 border border-white/[0.05] hover:border-[#00FF7F]/20 transition-all duration-300";

// Glass Panel
className =
  "bg-white/[0.02] backdrop-blur-sm rounded-lg border border-white/[0.05]";

// Content Card
className =
  "bg-gradient-to-br from-gray-900 to-gray-800 p-6 rounded-lg border border-gray-700";
```

### Text System

```typescript
// Headings
h1: "text-4xl md:text-5xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/80";
h2: "text-3xl font-bold text-white";
h3: "text-2xl font-semibold text-gray-100";

// Body Text
primary: "text-gray-300";
secondary: "text-gray-400";
muted: "text-gray-500";

// Special Text
gradient: "bg-gradient-to-r from-[#00FF7F] to-[#00FFCC] bg-clip-text text-transparent";
code: "font-mono text-[#00ff9d]";
```

## 🎬 Animation System

### Tailwind Animations (tailwind.config.ts)

```typescript
animations: {
  float: "float 6s ease-in-out infinite",
  pulse: "pulse 3s ease-in-out infinite",
  "spin-slow": "spin-slow 20s linear infinite",
  glow: "glow 2s ease-in-out infinite",
  ripple: "ripple 3s ease-out infinite",
  "core-pulse": "core-pulse 2s ease-in-out infinite",
  wave: "wave 8s linear infinite",
  flow: "flow 2s ease-out infinite",
}
```

### Framer Motion Patterns

```typescript
// Fade in sections
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.5 }}
>

// Hover effects
whileHover={{ scale: 1.05 }}
transition={{ duration: 0.3 }}
```

## 📱 Responsive Design

### Breakpoint Strategy

```typescript
// Tailwind breakpoints
sm: "640px"   // Small devices
md: "768px"   // Medium devices
lg: "1024px"  // Large devices
xl: "1280px"  // Extra large devices
2xl: "1536px" // 2X large devices
```

### Mobile-First Patterns

```typescript
// Typography scaling
"text-4xl md:text-5xl"; // 4xl on mobile, 5xl on medium+
"text-lg md:text-xl"; // lg on mobile, xl on medium+

// Layout adjustments
"grid-cols-1 md:grid-cols-2 lg:grid-cols-3";
"flex-col md:flex-row";
"p-4 md:p-6 lg:p-8";
```

## 🛠️ Implementation Guidelines

### 1. Class Naming Convention

```typescript
// ✅ GOOD - Use Tailwind utilities
className="bg-black text-white p-4 rounded-lg"

// ✅ GOOD - Custom classes for reusable patterns
className="feature-card glass-panel"

// ❌ AVOID - Inline styles
style={{ backgroundColor: 'black' }}
```

### 2. Component Styling Pattern

```typescript
// ✅ RECOMMENDED Pattern
import { cn } from "@/lib/utils"

const Component = ({ className, ...props }) => {
  return (
    <div
      className={cn(
        "base-classes",
        "responsive-classes",
        "state-classes",
        className // Allow override
      )}
      {...props}
    />
  )
}
```

### 3. Color Usage Rules

```typescript
// ✅ Primary brand color usage
"text-[#00FF7F]"; // Text
"bg-[#00FF7F]"; // Solid backgrounds
"border-[#00FF7F]"; // Borders
"bg-[#00FF7F]/10"; // Subtle backgrounds
"hover:bg-[#00FF7F]/20"; // Hover states

// ✅ Neutral colors
"text-white"; // Primary text
"text-gray-300"; // Secondary text
"text-gray-400"; // Tertiary text
"bg-gray-900"; // Dark backgrounds
"border-gray-700"; // Subtle borders
```

### 4. Spacing System

```typescript
// ✅ Consistent spacing scale
"p-4"; // 1rem padding
"p-6"; // 1.5rem padding
"p-8"; // 2rem padding
"mb-4"; // 1rem margin bottom
"gap-6"; // 1.5rem gap
"space-y-4"; // 1rem vertical spacing
```

## 🎨 Specialized Components

### Navigation Styles

**File**: `src/styles/navigation.css`

```css
.nav-link::after {
  content: "";
  position: absolute;
  width: 0;
  height: 2px;
  bottom: -4px;
  left: 0;
  background-color: #00ff7f;
  transition: width 0.3s ease;
}
```

### Mermaid Diagrams

**File**: `src/styles/global.css`

```css
.mermaid-diagram-container {
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(8px);
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
```

### Print Styles

```css
@media print {
  .fixed {
    display: none !important;
  }
  h2 {
    display: none !important;
  }
}
```

## 📋 Best Practices

### 1. Performance

- ✅ Use Tailwind utilities over custom CSS when possible
- ✅ Leverage `cn()` utility for conditional classes
- ✅ Use CSS custom properties for theme values
- ❌ Avoid inline styles
- ❌ Don't create unnecessary custom CSS classes

### 2. Maintainability

- ✅ Follow the established color palette
- ✅ Use consistent spacing scale
- ✅ Implement responsive design mobile-first
- ✅ Use semantic class names for custom components
- ❌ Don't hardcode colors outside the design system

### 3. Accessibility

- ✅ Maintain sufficient color contrast
- ✅ Use focus states with `focus-visible:ring-2 focus-visible:ring-[#00FF7F]`
- ✅ Implement proper hover states
- ✅ Use semantic HTML with appropriate ARIA labels

### 4. Dark Theme Consistency

- ✅ All components assume dark theme by default
- ✅ Use white text with appropriate opacity levels
- ✅ Implement glass morphism with `backdrop-blur-sm`
- ✅ Use subtle borders with `border-white/[0.05]`

## 🔧 Development Workflow

### Adding New Styles

1. **Check existing utilities first** - Use Tailwind classes when available
2. **Add to components layer** - For reusable patterns in `index.css`
3. **Create CVA variants** - For component variations using `class-variance-authority`
4. **Use CSS modules** - Only for complex component-specific styles

### Testing Styles

1. **Test responsive behavior** across all breakpoints
2. **Verify dark theme consistency**
3. **Check accessibility** with screen readers and keyboard navigation
4. **Validate performance** - ensure no layout shifts

### File Organization

```
src/
├── index.css              # Main styles, Tailwind layers
├── styles/
│   ├── global.css         # Global component styles
│   └── navigation.css     # Navigation-specific styles
└── components/ui/
    ├── button.tsx         # Component with CVA variants
    ├── badge.tsx          # Component with CVA variants
    └── *.tsx              # Other UI components
```

This styling system provides a scalable, maintainable foundation that balances utility-first CSS with component-specific customization while maintaining design consistency across the entire application.
