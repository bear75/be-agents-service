# Design System Documentation

## Overview

The AppCaire design system provides a comprehensive, reusable design language for all SEO sites and applications. Built with **Tailwind CSS**, **Radix UI**, and modern design principles including **glassmorphism**, **3D effects**, **gradient cards**, and beautiful animations.

## SEO Sites

The design system is used across the following SEO marketing sites:

| App                                               | Domain               | Port | SSR         |
| ------------------------------------------------- | -------------------- | ---- | ----------- |
| **EirTech** (`apps/eirtech`)                      | eirtech.ai           | 3004 | ✅ Full SSR |
| **Hemtjänstguide** (`apps/hemtjanstguide`)        | hemtjanstguide.se    | 3002 | Needs SSR   |
| **Nacka Hemtjänst** (`apps/nackahemtjanst`)       | nackahemtjanst.se    | 3003 | Needs SSR   |
| **Sveriges Hemtjänst** (`apps/sverigeshemtjanst`) | sverigeshemtjanst.se | 3001 | Needs SSR   |
| **Website** (`apps/website`)                      | www.caire.se         | 3005 | Needs SSR   |

All SEO sites share:

- The same UI component library (`@appcaire/ui`)
- SEO-specific business components (`@appcaire/shared/seo/components/shared`)
- **Shared explanation pages** (`@appcaire/shared/seo/pages/`) - CaireIndex methodology, ranking explanation, data sources
- Site-specific themes (eirtech, hemtjanstguide, nacka, sverige)
- Swedish localization standards
- Consistent design patterns (glassmorphism, gradients, 3D effects)
- **SSR-compatible components** (see [SSR Compatibility](#ssr-compatibility) section)

## Table of Contents

- [Component Architecture](#component-architecture)
- [Design Principles](#design-principles)
- [Glassmorphism](#glassmorphism)
- [3D Effects & Gradients](#3d-effects--gradients)
- [Icons](#icons)
- [Charts](#charts)
- [Swedish Formatting](#swedish-formatting)
- [Installation & Setup](#installation--setup)
- [Component Usage](#component-usage)
- [Using Shared vs Local Components](#using-shared-vs-local-components)
- [Best Practices](#best-practices)
- [SSR Compatibility](#ssr-compatibility)

---

## Component Architecture

The design system follows a clear hierarchical structure:

### `@appcaire/ui` - Universal UI Components

**Location:** `packages/ui/`  
**Purpose:** Generic, reusable UI primitives used across ALL apps

**Contains:**

- **UI Primitives** (`components/ui/`): Button, Card, Input, Dialog, Tabs, etc.
- **Compound Components** (`components/`): Hero, FeatureCard, StatCard, GradientCard, Section
- **Design Tokens**: Colors, gradients, shadows, glass effects
- **Themes**: Site-specific themes (admin, eirtech, hemtjanstguide, nacka, sverige)

**✅ Use for:** Buttons, cards, forms, modals, navigation, layout components

### `@appcaire/shared/seo/components/shared/` - SEO Business Components

**Location:** `packages/shared/src/seo/components/shared/`  
**Purpose:** SEO-specific business logic components

**Contains:**

- ProviderCard, MunicipalityCard, Hero, StatCard
- QualityIndicators, ProviderDetailPage, MunicipalityProviders
- FAQ, CTA, CTABox, ContentSection
- ModernNavigation, PageLayout, ArticleLayout

**✅ Use for:** SEO-domain specific components with business logic

### `apps/{app}/src/components/` - App-Specific Components

**Location:** Individual app directories  
**Purpose:** Components truly unique to a specific app

**✅ Use for:** Only when a component cannot be shared and is app-specific

---

## Design Principles

### 1. Glassmorphism First

Use glassmorphism effects for modern, depth-rich interfaces with backdrop blur and transparency.

### 2. 3D Depth & Gradients

Create visual hierarchy using gradient backgrounds, layered shadows, and 3D hover effects.

### 3. Consistent Color System

Use the design system's color tokens and gradients consistently across all components.

### 4. Swedish Localization

All currency, numbers, and text formatting must follow Swedish standards.

### 5. Accessibility

All components must be keyboard navigable, screen-reader friendly, and meet WCAG AA contrast ratios.

---

## Glassmorphism

Glassmorphism creates depth and visual interest through semi-transparent backgrounds with backdrop blur.

### CSS Classes

```css
/* Basic glass effect */
.glass {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
}

/* Glass card with hover */
.glass-card {
  background: rgba(255, 255, 255, 0.72);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 1rem;
  transition: all 0.3s ease-out;
}

.glass-card:hover {
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.12);
  transform: translateY(-4px);
}
```

### Usage Examples

#### Glass Card

```tsx
import { Card } from "@appcaire/ui/components/ui";

<Card glass className="p-6">
  <h3>Glass Card</h3>
  <p>Content with glassmorphism effect</p>
</Card>;
```

#### Glass Button

```tsx
import { Button } from "@appcaire/ui/components/ui";

<Button variant="glass">Glass Button</Button>;
```

#### Custom Glass Container

```tsx
<div className="backdrop-blur-xl bg-white/70 border-2 border-white/60 shadow-xl">
  {/* Content */}
</div>
```

### Design Tokens

```css
--glass-white: rgba(255, 255, 255, 0.72);
--glass-light: rgba(255, 255, 255, 0.48);
--glass-dark: rgba(0, 0, 0, 0.24);
--glass-border: rgba(255, 255, 255, 0.18);
--glass-blur: 20px;
```

---

## 3D Effects & Gradients

### Gradient Cards

Use gradient cards with 3D depth effects for featured content:

```tsx
import { GradientCard } from "@appcaire/ui/components";

<GradientCard
  title="Feature Title"
  description="Feature description"
  variant="emerald" // emerald, blue, purple, orange
  icon={Sparkles}
  featured
/>;
```

**Variants:**

- `emerald` - Green gradient (success, positive metrics)
- `blue` - Blue gradient (information, primary actions)
- `purple` - Purple gradient (premium, featured content)
- `orange` - Orange gradient (warnings, highlights)

### Stat Cards with Gradients

```tsx
import { StatCard } from "@appcaire/shared/seo/components/shared";

<StatCard
  value="290"
  label="Kommuner"
  description="Antal kommuner i databasen"
  icon={MapPin}
  trend="up"
  trendValue="+12%"
  variant="highlight" // default, highlight, glass
/>;
```

**Features:**

- Gradient backgrounds with depth
- Animated icon with shadow
- Trend indicators with color coding
- Hover effects with scale and shadow transitions

### 3D Hover Effects

Cards should lift on hover with enhanced shadows:

```tsx
<div
  className="
  rounded-2xl p-6 
  bg-gradient-to-br from-gray-50 via-slate-50 to-zinc-50 
  border-2 border-white/80 
  shadow-lg shadow-gray-200/50
  transition-all duration-300
  hover:shadow-xl hover:shadow-gray-300/50 
  hover:-translate-y-1
"
>
  {/* Content */}
</div>
```

### Gradient Backgrounds

```css
/* Primary gradient */
.gradient-primary {
  background: linear-gradient(
    135deg,
    hsl(var(--brand-primary)),
    hsl(var(--brand-secondary))
  );
}

/* Text gradient */
.text-gradient {
  background: linear-gradient(
    to right,
    var(--accent-blue),
    var(--accent-purple),
    var(--accent-green)
  );
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### Animated Gradient Orbs

For hero sections and backgrounds:

```tsx
<div className="absolute inset-0 overflow-hidden pointer-events-none">
  {/* Main gradient orb */}
  <div
    className="
    absolute -top-32 -right-32 w-[500px] h-[500px] 
    rounded-full blur-3xl bg-blue-200/40
    animate-pulse
  "
    style={{ animationDuration: "4s" }}
  />

  {/* Secondary orb */}
  <div
    className="
    absolute -bottom-32 -left-32 w-[400px] h-[400px] 
    rounded-full blur-3xl bg-cyan-200/30
    animate-pulse
  "
    style={{ animationDuration: "5s", animationDelay: "1s" }}
  />
</div>
```

---

## Icons

All icons use **Lucide React** for consistency.

### Installation

```bash
# Already included in package.json
"lucide-react": "^0.462.0 || ^0.562.0"
```

### Usage

```tsx
import {
  MapPin,
  Users,
  TrendingUp,
  ArrowRight,
  Phone,
  Mail,
  Globe,
} from "lucide-react";

<Button>
  <RefreshCw className="h-4 w-4 mr-2" />
  Refresh
</Button>;
```

### Icon Sizing

Use consistent sizing:

- **Small:** `h-4 w-4` (16px) - Inline with text, buttons
- **Medium:** `h-5 w-5` (20px) - Card headers, stat cards
- **Large:** `h-6 w-6` (24px) - Feature cards, hero sections

### Icon with Background

```tsx
<div
  className="
  p-3 rounded-xl shadow-lg
  bg-gradient-to-br from-blue-500 to-cyan-500
  text-white
  transition-all duration-300
  hover:scale-110 hover:shadow-xl
"
>
  <Icon className="w-5 h-5" />
</div>
```

---

## Charts

Charts use **Recharts** with consistent styling and Swedish formatting.

### Chart Container Style

All charts should be wrapped in a styled container:

```tsx
<div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
  <h3 className="text-lg font-bold text-slate-900 mb-1">Chart Title</h3>
  {description && <p className="text-sm text-slate-500 mb-6">{description}</p>}

  {/* Chart content */}

  {source && (
    <div className="mt-4 text-[10px] text-slate-400 font-medium uppercase tracking-wider text-right">
      Källa: {source}
    </div>
  )}
</div>
```

### Chart Components

```tsx
import {
  GenericBarChart,
  GenericPieChart,
  GenericLineChart,
} from "@appcaire/shared/seo/components/Charts";

<GenericBarChart
  title="Chart Title"
  description="Chart description"
  data={chartData}
  height={300}
  layout="vertical" // or "horizontal"
  unit=" kr"
  source="Socialstyrelsen / 2025"
/>;
```

### Chart Design Standards

1. **Colors:**
   - Primary: `#6366f1` (indigo)
   - Secondary: `#94a3b8` (slate)
   - Grid: `#f1f5f9` (light slate)

2. **Typography:**
   - Title: `text-lg font-bold text-slate-900`
   - Description: `text-sm text-slate-500`
   - Axis labels: `fontSize: 12, fill: "#64748b"`

3. **Borders & Shadows:**
   - Container: `rounded-2xl shadow-sm border border-slate-200`
   - Tooltip: `borderRadius: "12px", border: "none", boxShadow: "0 10px 15px -3px rgb(0 0 0 / 0.1)"`

4. **Bar Charts:**
   - Bar radius: `[6, 6, 0, 0]` for vertical, `[0, 6, 6, 0]` for horizontal
   - Bar size: `24-32px` depending on data density

5. **Source Attribution:**
   - Always include source in Swedish: `Källa: {source}`
   - Format: `text-[10px] text-slate-400 font-medium uppercase tracking-wider text-right`

### Chart Data Format

```typescript
interface ChartData {
  name: string;
  value: number;
  color?: string; // Optional custom color
}

const chartData: ChartData[] = [
  { name: "Januari", value: 100, color: "#6366f1" },
  { name: "Februari", value: 200, color: "#94a3b8" },
];
```

---

## Swedish Formatting

All currency, numbers, and dates must follow Swedish formatting standards.

### Currency Formatting (SEK)

#### Standard Currency Format

```tsx
import { formatCurrency } from "@appcaire/shared/seo/components/ROICalculator";

// Full format: "12 345 kr"
const formatCurrency = (value: number): string => {
  return new Intl.NumberFormat("sv-SE", {
    style: "currency",
    currency: "SEK",
    maximumFractionDigits: 0,
  }).format(value);
};
```

#### Large Number Abbreviations

For very large numbers, use Swedish abbreviations:

```tsx
const formatSEK = (value: string | number | null | undefined) => {
  if (value === null || value === undefined) return "N/A";
  const num = typeof value === "string" ? parseInt(value, 10) : value;
  if (isNaN(num)) return "N/A";

  // Billion (miljard)
  if (num >= 1000000000) return `${(num / 1000000000).toFixed(1)} mrd kr`;
  // Million (miljon)
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)} mnkr`;
  // Thousand (tusen)
  return `${(num / 1000).toFixed(0)} tkr`;
};

// Examples:
// 1,500,000,000 → "1.5 mrd kr"
// 2,500,000 → "2.5 mnkr"
// 15,000 → "15 tkr"
```

### Number Formatting

```tsx
// Swedish number format (space as thousand separator, comma as decimal)
const formatNumber = (value: number): string => {
  return new Intl.NumberFormat("sv-SE", {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  }).format(value);
};

// Examples:
// 1234567.89 → "1 234 567,89"
// 1000 → "1 000"
```

### Date Formatting

```tsx
// Swedish date format
const formatDate = (date: Date): string => {
  return new Intl.DateTimeFormat("sv-SE", {
    year: "numeric",
    month: "long", // or "short" for abbreviated
    day: "numeric",
  }).format(date);
};

// Examples:
// "2025-01-15" → "15 januari 2025"
// "2025-01-15" → "15 jan. 2025" (with month: "short")
```

### Percentage Formatting

```tsx
// Swedish percentage format
const formatPercent = (value: number, decimals: number = 1): string => {
  return new Intl.NumberFormat("sv-SE", {
    style: "percent",
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value / 100);
};

// Examples:
// 85.5 → "85,5 %"
// 12.3 → "12,3 %"
```

---

## Installation & Setup

### 1. Dependencies

The design system is already included as workspace dependencies:

```json
{
  "@appcaire/ui": "*",
  "@appcaire/shared": "*"
}
```

### 2. Configure Tailwind CSS

Create or update `tailwind.config.ts`:

```typescript
import type { Config } from "tailwindcss";
import { designSystemPreset } from "@appcaire/ui/tailwind";

export default {
  presets: [designSystemPreset as Partial<Config>],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      // Your app-specific overrides
    },
  },
  plugins: [require("tailwindcss-animate")],
} satisfies Config;
```

### 3. Import Styles

In your main CSS file (e.g., `src/styles/index.css`):

```css
/* Design System Base Styles */
@import "@appcaire/ui/styles/index.css";

/* Site-specific theme */
@import "@appcaire/ui/themes/admin"; /* or eirtech, hemtjanstguide, nacka, sverige */
```

### 4. Import in Main Entry

In your `main.tsx` or `index.tsx`:

```typescript
import "./styles/index.css";
```

---

## Component Usage

### UI Primitives (from `@appcaire/ui`)

```tsx
import { Button, Card, Input, Dialog } from '@appcaire/ui/components/ui';
import { cn } from '@appcaire/ui';

// Button with variants
<Button variant="gradient" size="lg">Get Started</Button>
<Button variant="glass">Learn More</Button>

// Card with glass effect
<Card glass hover>
  <CardHeader>
    <CardTitle>Glass Card</CardTitle>
  </CardHeader>
  <CardContent>Content here</CardContent>
</Card>

// Input
<Input type="text" placeholder="Enter text..." />
```

### SEO Business Components (from `@appcaire/shared`)

```tsx
import {
  ProviderCard,
  Hero,
  StatCard,
  QualityIndicators
} from '@appcaire/shared/seo/components/shared';

<Hero
  title="Welcome"
  subtitle="Description text"
  ctaText="Get Started"
  ctaLink="/start"
  align="center"
  size="default"
/>

<StatCard
  value="290"
  label="Kommuner"
  icon={MapPin}
  trend="up"
  trendValue="+12%"
  variant="highlight"
/>
```

---

## Using Shared vs Local Components

### 🎯 Component Selection Hierarchy

**ALWAYS follow this order:**

1. **First:** Check `@appcaire/ui/components/ui` for generic UI primitives
2. **Second:** Check `@appcaire/shared/seo/components/shared` for SEO business components
3. **Last resort:** Create app-specific component in `apps/{app}/src/components/`

### ✅ When to Use Shared Components

**Use `@appcaire/ui` for:**

- Buttons, inputs, forms, modals, dialogs
- Cards, badges, tooltips, dropdowns
- Navigation, tabs, accordions
- Layout components (containers, sections)
- Generic UI patterns

**Use `@appcaire/shared/seo/components/shared` for:**

- ProviderCard, MunicipalityCard
- SEO-specific Hero, StatCard variants
- Business logic components (QualityIndicators, ProviderDetailPage)
- Domain-specific layouts (PageLayout, ArticleLayout)

### ❌ When NOT to Create Local Components

**Don't create local components for:**

- Generic buttons (use `@appcaire/ui/components/ui/button`)
- Generic cards (use `@appcaire/ui/components/ui/card`)
- Generic forms (use `@appcaire/ui/components/ui/form`)
- Generic modals (use `@appcaire/ui/components/ui/dialog`)

**Only create local components when:**

- Component contains app-specific business logic that can't be abstracted
- Component is truly unique to one app and won't be reused
- Component requires app-specific integrations (e.g., specific API calls)

### 📋 Decision Flowchart

```
Need a component?
│
├─ Is it a generic UI primitive?
│  └─ YES → Use @appcaire/ui/components/ui
│
├─ Is it SEO-domain specific?
│  └─ YES → Use @appcaire/shared/seo/components/shared
│
└─ Is it truly app-unique?
   └─ YES → Create in apps/{app}/src/components/
   └─ NO → Consider adding to shared
```

### ✅ Correct Import Patterns

```tsx
// ✅ GOOD: UI primitives from @appcaire/ui
import { Button, Card, Input } from "@appcaire/ui/components/ui";
import { cn } from "@appcaire/ui";

// ✅ GOOD: SEO business components from @appcaire/shared
import { ProviderCard, Hero } from "@appcaire/shared/seo/components/shared";

// ✅ GOOD: Chart components
import { GenericBarChart } from "@appcaire/shared/seo/components/Charts";

// ✅ GOOD: App-specific component (only if truly unique)
import { MyUniqueAppComponent } from "../components/MyUniqueAppComponent";
```

### ❌ Incorrect Patterns

```tsx
// ❌ BAD: Relative paths across packages
import { Button } from "../../../packages/ui/src/components/ui/button";

// ❌ BAD: Creating local component when shared exists
// Don't create apps/myapp/src/components/Button.tsx
// Use @appcaire/ui/components/ui/button instead

// ❌ BAD: Duplicating shared components
// Don't copy ProviderCard to local - use shared version

// ❌ BAD: Using old package names
import { Button } from "@appcaire/ui-tailwind"; // use @appcaire/ui
```

### 🔄 Refactoring Checklist

Before creating a new component:

1. ✅ Check `@appcaire/ui/components/ui` - does a primitive exist?
2. ✅ Check `@appcaire/ui/components` - does a compound component exist?
3. ✅ Check `@appcaire/shared/seo/components/shared` - does a business component exist?
4. ✅ Can existing components be composed to solve the need?
5. ✅ If creating new, can it be shared? → Add to appropriate shared package
6. ✅ If truly app-specific, create in `apps/{app}/src/components/`

---

## Best Practices

### 1. Always Use Design System Components

```tsx
// ✅ Good
import { Button } from '@appcaire/ui/components/ui';
<Button variant="gradient">Click</Button>

// ❌ Bad
<button className="custom-button">Click</button>
```

### 2. Use Glassmorphism for Depth

```tsx
// ✅ Good
<Card glass hover>
  <CardContent>Content with glass effect</CardContent>
</Card>

// ❌ Bad
<div className="bg-white border">Content</div>
```

### 3. Use Gradients for Visual Interest

```tsx
// ✅ Good
<StatCard variant="highlight" /> // Uses gradient background
<div className="bg-gradient-to-br from-blue-50 to-cyan-50" />

// ❌ Bad
<div className="bg-gray-100" />
```

### 4. Consistent Spacing

Use Tailwind spacing utilities:

```tsx
// ✅ Good
<div className="space-y-6">
  <Card className="p-6">...</Card>
</div>

// ❌ Bad
<div style={{ marginBottom: "24px" }}>...</div>
```

### 5. Swedish Formatting Always

```tsx
// ✅ Good
const formatted = formatSEK(1500000); // "1.5 mnkr"

// ❌ Bad
const formatted = `$${(value / 1000000).toFixed(1)}M`; // Wrong currency and format
```

### 6. Responsive Design

Always consider mobile-first:

```tsx
// ✅ Good
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
  {/* Cards */}
</div>

// ❌ Bad
<div className="grid grid-cols-4">
  {/* Not responsive */}
</div>
```

### 7. Accessibility

- Use semantic HTML
- Include ARIA labels where needed
- Ensure keyboard navigation works
- Maintain proper color contrast (WCAG AA)
- Screen reader friendly

### 8. Icons from Lucide

```tsx
// ✅ Good
import { MapPin, Users } from 'lucide-react';
<MapPin className="h-4 w-4" />

// ❌ Bad
<img src="/icon.svg" alt="icon" /> // Use Lucide icons instead
```

---

## Design Tokens Reference

### Colors

```css
/* Primary colors */
--brand-primary: 217 91% 60%;
--brand-secondary: 221 83% 53%;

/* Accent colors */
--accent-blue: 217 91% 60%;
--accent-purple: 262 83% 58%;
--accent-green: 142 76% 36%;

/* Surface colors */
--surface-50: 0 0% 98%;
--surface-100: 0 0% 96%;
--surface-900: 0 0% 9%;
```

### Gradients

```css
--gradient-primary: linear-gradient(
  135deg,
  hsl(var(--brand-primary)),
  hsl(var(--brand-secondary))
);
--gradient-warm: linear-gradient(135deg, hsl(16, 90%, 68%), hsl(32, 95%, 80%));
--gradient-care: linear-gradient(
  135deg,
  hsl(157, 50%, 62%),
  hsl(160, 70%, 88%)
);
```

### Shadows

```css
--shadow-soft: 0 2px 20px rgba(63, 210, 199, 0.08);
--shadow-medium: 0 8px 40px rgba(63, 210, 199, 0.12);
--shadow-large: 0 20px 60px rgba(63, 210, 199, 0.16);
--shadow-glass: 0 8px 32px 0 rgba(0, 0, 0, 0.08);
--shadow-glass-lg: 0 25px 50px -12px rgba(0, 0, 0, 0.12);
```

### Glassmorphism

```css
--glass-white: rgba(255, 255, 255, 0.72);
--glass-light: rgba(255, 255, 255, 0.48);
--glass-border: rgba(255, 255, 255, 0.18);
--glass-blur: 20px;
```

---

## Component API Reference

### Button

```tsx
interface ButtonProps {
  variant?:
    | "default"
    | "destructive"
    | "outline"
    | "secondary"
    | "ghost"
    | "link"
    | "gradient"
    | "glass";
  size?: "default" | "sm" | "lg" | "xl" | "icon";
  asChild?: boolean;
}
```

### Card

```tsx
interface CardProps {
  glass?: boolean; // Enable glassmorphism effect
  hover?: boolean; // Enable hover lift animation
}
```

### StatCard

```tsx
interface StatCardProps {
  value: string;
  label: string;
  description?: string;
  icon?: LucideIcon;
  trend?: "up" | "down" | "neutral";
  trendValue?: string;
  variant?: "default" | "highlight" | "glass";
}
```

### GradientCard

```tsx
interface GradientCardProps {
  title: string;
  description?: string;
  href?: string;
  icon?: LucideIcon;
  variant?: "emerald" | "blue" | "purple" | "orange";
  badge?: string;
  featured?: boolean;
}
```

---

## SSR Compatibility

All design system components are **SSR-safe** and work with Vite SSR.

### Package SSR Status

| Package                                  | SSR Status  | Notes                                          |
| ---------------------------------------- | ----------- | ---------------------------------------------- |
| `@appcaire/ui`                           | ✅ SSR-safe | All UI primitives work with `renderToString()` |
| `@appcaire/shared`                       | ✅ SSR-safe | No browser-only APIs in components             |
| `@appcaire/shared/gamification`          | ✅ SSR-safe | Presentational components only                 |
| `@appcaire/shared/stats-data-components` | ✅ SSR-safe | Data passed via props                          |

### Why SSR-Safe?

1. **No browser-only APIs** - Components don't use `window`, `document`, `localStorage`
2. **No side effects** - No `useEffect` or `useState` in shared components
3. **Props-based** - All data comes from props, not browser APIs
4. **React 18+ compatible** - Works with `renderToString()` and `hydrateRoot()`

### Using Components in SSR Context

```typescript
// entry-server.tsx - This works fine with shared components
import { renderToString } from "react-dom/server";
import { LevelBadge } from "@appcaire/shared/gamification";
import { Button, Card } from "@appcaire/ui/components/ui";

export async function render(url: string) {
  const html = renderToString(
    <div>
      <Card>
        <LevelBadge level={3} />
        <Button>Click me</Button>
      </Card>
    </div>,
  );
  return { html };
}
```

### Browser APIs in App Code

If your **app-specific code** needs browser APIs, guard them:

```typescript
// ❌ UNSAFE - Will crash during SSR
const width = window.innerWidth;

// ✅ SAFE - Guard with typeof check
const getWidth = () => {
  if (typeof window === "undefined") return 0;
  return window.innerWidth;
};

// ✅ SAFE - Use inside useEffect
useEffect(() => {
  setWidth(window.innerWidth);
}, []);
```

### Related Documentation

- [VITE_SSR_SETUP.md](../02-seo-teknisk-implementation/VITE_SSR_SETUP.md) - Full SSR guide
- [SEO_COMPONENT_GUIDE.md](../02-seo-teknisk-implementation/SEO_COMPONENT_GUIDE.md) - Meta tags with SSR

---

## Troubleshooting

### Components not styling correctly

1. Ensure Tailwind config includes design system preset
2. Check that CSS imports are correct in main entry
3. Verify content paths in `tailwind.config.ts` include design system

### Theme not applying

1. Verify theme CSS is imported after base styles
2. Check CSS variable values in browser DevTools
3. Ensure theme file exists in `packages/ui/src/themes/`

### TypeScript errors

1. Ensure `@appcaire/ui` and `@appcaire/shared` are in dependencies
2. Check TypeScript can resolve the packages
3. Verify exports in package index files

---

## Additional Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Radix UI Documentation](https://www.radix-ui.com/)
- [Lucide Icons](https://lucide.dev/)
- [Recharts Documentation](https://recharts.org/)
- [Swedish Number Format](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Intl/NumberFormat)

---

## Support

For issues or questions about the design system:

1. Check this documentation first
2. Review component source code in `packages/ui/src/` and `packages/shared/src/seo/components/`
3. Check existing implementations in apps (eirtech, hemtjanstguide, etc.)
4. Follow the component hierarchy: UI → Shared → Local
