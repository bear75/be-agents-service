# Best Practices for Multilingual Navigation in Next.js/React

Looking at your current implementation, I see several challenges in how language handling is managed across multiple files. Here's how to implement a more streamlined, SEO-friendly multilingual navigation system:

## Current Issues

1. **Duplicate Route Definitions**: App.tsx defines each route twice (Swedish and English versions)
2. **Inconsistent Path Mapping**: Navigation.tsx uses a separate mapping system from routes.ts
3. **Underutilized routes.ts**: Contains only a subset of routes, mostly English ones

## Recommended Approach

### 1. Centralized Route Configuration

Create a single source of truth for all routes with language mappings:

```tsx
// src/utils/routes.ts
export const routes = {
  // Format: [swedish path, english path]
  home: ["/", "/en"],
  about: ["/om-oss", "/en/about"],
  products: ["/produkter", "/en/products"],
  business: ["/for-verksamheten", "/en/for-business"],
  features: ["/funktioner", "/en/features"],
  contact: ["/kontakt", "/en/contact"],

  // Nested routes
  features: {
    index: ["/funktioner", "/en/features"],
    scheduling: ["/funktioner/schemaläggning", "/en/features/scheduling"],
    routeOptimization: [
      "/funktioner/ruttoptimering",
      "/en/features/route-optimization",
    ],
    // Add other feature sub-routes
  },

  // Resources
  resources: {
    index: ["/resurser", "/en/resources"],
    // Add resource sub-routes
  },
};

// Helper function to get path by language
export function getLocalizedPath(routeKey: string, lang: "sv" | "en"): string {
  const pathPair = getNestedRouteValue(routes, routeKey);
  if (!pathPair) return "/";
  return lang === "en" ? pathPair[1] : pathPair[0];
}

// Helper to get nested route by dot notation (e.g., "features.scheduling")
function getNestedRouteValue(
  obj: any,
  path: string,
): [string, string] | undefined {
  const parts = path.split(".");
  let current = obj;

  for (const part of parts) {
    if (current[part] === undefined) return undefined;
    current = current[part];
  }

  return current;
}
```

### 2. Unified Language Detection

Create a custom hook for consistent language handling:

```tsx
// src/hooks/useLanguage.ts
import { useLocation } from "react-router-dom";
import { useTranslation } from "react-i18next";

export function useLanguage() {
  const location = useLocation();
  const { i18n } = useTranslation();

  // Detect language from URL
  const isEnglish = location.pathname.startsWith("/en");
  const language = isEnglish ? "en" : "sv";

  // Ensure i18n matches URL language
  if (i18n.language !== language) {
    i18n.changeLanguage(language);
  }

  // Get equivalent path in other language
  const getAlternateLink = (currentPath: string): string => {
    if (isEnglish) {
      // Convert /en/page to /page
      return currentPath.replace(/^\/en/, "");
    } else {
      // Convert /page to /en/page
      return `/en${currentPath}`;
    }
  };

  return {
    language,
    isEnglish,
    getAlternateLink,
  };
}
```

### 3. Simplified Navigation Component

Use the centralized routes in the Navigation component:

```tsx
// In Navigation.tsx
import { routes, getLocalizedPath } from "@/utils/routes";
import { useLanguage } from "@/hooks/useLanguage";

export const Navigation = () => {
  const { language } = useLanguage();
  const { t } = useTranslation();

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black/50 backdrop-blur-md border-b border-white/10">
      <nav className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link
          to={getLocalizedPath("home", language)}
          className="text-white font-bold text-xl"
        >
          {/* Logo content */}
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center justify-between flex-1 ml-8">
          <NavigationMenu>
            <NavigationMenuList>
              <NavigationMenuItem>
                <Link
                  to={getLocalizedPath("products", language)}
                  className="text-white hover:text-[#00FF7F] px-4 py-2"
                >
                  {t("nav.products")}
                </Link>
              </NavigationMenuItem>
              {/* Other menu items */}
            </NavigationMenuList>
          </NavigationMenu>
        </div>

        {/* Mobile Navigation */}
        {/* ... */}
      </nav>
    </header>
  );
};
```

### 4. Simplified Routing in App.tsx

Dramatically reduce duplication in App.tsx:

```tsx
// In App.tsx
// ...imports

const App = () => {
  return (
    <React.StrictMode>
      <ErrorBoundary>
        <QueryClientProvider client={queryClient}>
          <TooltipProvider>
            <Toaster />
            <Sonner />
            <BrowserRouter>
              <ScrollToTop />
              <DefaultSeo />
              <Routes>
                {/* Special routes that don't need language handling */}
                <Route path="/preview" element={<Preview />} />
                <Route path="/auth" element={<Auth />} />

                {/* Main routes with LayoutWrapper */}
                <Route element={<LayoutWrapper />}>
                  {/* Swedish Routes */}
                  <Route path="/" element={<Index />} />
                  <Route path="/produkter" element={<ProductsPage />} />
                  <Route path="/kontakt" element={<Contact />} />
                  <Route path="/for-verksamheten" element={<BusinessPage />} />
                  <Route path="/funktioner" element={<Features />} />
                  <Route
                    path="/funktioner/schemaläggning"
                    element={<Scheduling />}
                  />
                  <Route
                    path="/funktioner/ruttoptimering"
                    element={<RouteOptimizationHomeCare />}
                  />
                  <Route path="/om-oss" element={<About />} />
                  {/* Other Swedish routes */}

                  {/* English Routes */}
                  <Route path="/en" element={<Index />} />
                  <Route path="/en/products" element={<ProductsPage />} />
                  <Route path="/en/contact" element={<Contact />} />
                  <Route path="/en/for-business" element={<BusinessPage />} />
                  <Route path="/en/features" element={<Features />} />
                  <Route
                    path="/en/features/scheduling"
                    element={<Scheduling />}
                  />
                  <Route
                    path="/en/features/route-optimization"
                    element={<RouteOptimizationHomeCare />}
                  />
                  <Route path="/en/about" element={<About />} />
                  {/* Other English routes */}

                  {/* 404 catch-all route */}
                  <Route path="*" element={<NotFound />} />
                </Route>
              </Routes>
            </BrowserRouter>
          </TooltipProvider>
        </QueryClientProvider>
      </ErrorBoundary>
    </React.StrictMode>
  );
};
```

### 5. SEO Optimization for Multilingual Content

In each page component, implement proper language alternates and canonical URLs:

```tsx
// Example for About.tsx
import { useLanguage } from "@/hooks/useLanguage";
import { PageSeo } from "@/components/seo/PageSeo";
import { JsonLd } from "@/components/seo/JsonLd";
import { BASE_URL } from "@/config/env";

const About: FC = () => {
  const { language, isEnglish, getAlternateLink } = useLanguage();
  const { t } = useTranslation();
  const currentPath = useLocation().pathname;

  return (
    <>
      <PageSeo
        title={t("about.page.meta.title")}
        description={t("about.page.meta.description")}
        keywords={t("about.page.meta.keywords")}
        canonical={`${BASE_URL}${currentPath}`}
        languageAlternates={[
          { hrefLang: "sv", href: `${BASE_URL}/om-oss` },
          { hrefLang: "en", href: `${BASE_URL}/en/about` },
          { hrefLang: "x-default", href: `${BASE_URL}/om-oss` },
        ]}
      />
      <JsonLd
        type="Organization"
        data={{
          name: "Caire",
          url: BASE_URL,
          logo: `${BASE_URL}/images/logo.png`,
          description: t("about.page.meta.description"),
        }}
      />

      {/* Page content */}
    </>
  );
};

export default About;
```

## Additional Best Practices

1. **Use an i18n middleware** for detecting user language preferences (if migrating to Next.js App Router in the future)
2. **Generate a sitemap.xml** that includes hreflang tags for all pages
3. **Implement structured data (JSON-LD)** for each page in both languages
4. **Use rel="alternate" hreflang tags** for all pages to help search engines understand language relationships
5. **Set the html lang attribute** based on the current language

## Implementation Plan

1. Update routes.ts with the centralized route configuration
2. Create the useLanguage hook for consistent language detection
3. Update Navigation.tsx to use the new route utilities
4. Refactor page components to handle language consistently
5. Implement proper SEO components on all pages

This approach will significantly reduce code duplication, centralize language handling, and improve SEO for multilingual content.
