# Vite SSR Setup Guide

> **Last updated:** January 2026

## Overview

This guide describes how to implement **Server-Side Rendering (SSR)** with Vite for SEO-optimized React apps in the AppCaire monorepo.

**Reference implementation:** `apps/eirtech` has full SSR and is used as a template.

---

## Why SSR?

| Without SSR                                  | With SSR           |
| -------------------------------------------- | ------------------ |
| Empty HTML → JS renders                      | Pre-rendered HTML  |
| Google must execute JS                       | Immediate indexing |
| Social sharing doesn't work                  | OG tags work       |
| AI agents (GPTBot, Claude) don't see content | Full visibility    |
| Slower First Contentful Paint                | Fast FCP           |

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    Production Flow                   │
├─────────────────────────────────────────────────────┤
│                                                      │
│   Browser Request                                    │
│        │                                             │
│        ▼                                             │
│   ┌─────────────┐                                   │
│   │  server.ts  │  Express server                   │
│   │  (Node.js)  │                                   │
│   └──────┬──────┘                                   │
│          │                                           │
│          ▼                                           │
│   ┌─────────────────┐                               │
│   │ entry-server.tsx│  renderToString()             │
│   │                 │  HelmetProvider               │
│   └────────┬────────┘                               │
│            │                                         │
│            ▼                                         │
│   ┌─────────────────┐                               │
│   │   index.html    │  Template with <!--app-html-->│
│   │   + injected    │  + helmet tags                │
│   └────────┬────────┘                               │
│            │                                         │
│            ▼                                         │
│   ┌─────────────────┐                               │
│   │ entry-client.tsx│  hydrateRoot()                │
│   │                 │  Interactivity                │
│   └─────────────────┘                               │
│                                                      │
└─────────────────────────────────────────────────────┘
```

---

## Required Files

### 1. `src/entry-server.tsx`

Server-side rendering entry point:

```typescript
import { renderToString } from "react-dom/server";
import { StaticRouter } from "react-router-dom/server";
import { HelmetProvider } from "react-helmet-async";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@appcaire/ui/components/ui";
import App from "./App";
import "./i18n"; // If using i18n

/**
 * Server-side entry point for SSR
 * Renders the React app to HTML string for server-side rendering
 */
export async function render(url: string) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        staleTime: 1000 * 60 * 5,
        gcTime: 1000 * 60 * 10,
      },
    },
  });

  const helmetContext: { helmet?: unknown } = {};

  const html = renderToString(
    <HelmetProvider context={helmetContext}>
      <QueryClientProvider client={queryClient}>
        <TooltipProvider>
          <StaticRouter location={url}>
            <App />
          </StaticRouter>
        </TooltipProvider>
      </QueryClientProvider>
    </HelmetProvider>,
  );

  return {
    html,
    helmet: helmetContext.helmet,
  };
}
```

---

### 2. `src/entry-client.tsx`

Client-side hydration entry:

```typescript
import { hydrateRoot } from "react-dom/client";
import { HelmetProvider } from "react-helmet-async";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { TooltipProvider } from "@appcaire/ui/components/ui";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import "./i18n"; // If using i18n
import "./index.css";

/**
 * Client-side entry point for hydration
 * This is used in SSR mode to hydrate the server-rendered HTML
 */
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5,
      gcTime: 1000 * 60 * 10,
    },
  },
});

const root = document.getElementById("root");

if (!root) {
  throw new Error("Root element not found");
}

hydrateRoot(
  root,
  <HelmetProvider>
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <BrowserRouter>
          <App />
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  </HelmetProvider>,
);
```

---

### 3. `server.ts`

Express SSR server:

```typescript
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import express from "express";
import type { ViteDevServer } from "vite";

interface HelmetData {
  title: { toString: () => string };
  meta: { toString: () => string };
  link: { toString: () => string };
  script: { toString: () => string };
  style: { toString: () => string };
}

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const isProduction = process.env.NODE_ENV === "production";
const port = process.env.PORT || 3000;
const base = process.env.BASE || "/";

const app = express();

// Development vs Production middleware
let vite: ViteDevServer | undefined;
if (!isProduction) {
  const { createServer } = await import("vite");
  vite = await createServer({
    server: { middlewareMode: true },
    appType: "custom",
    base,
  });
  app.use(vite.middlewares);
} else {
  const compression = (await import("compression")).default;
  const sirv = (await import("sirv")).default;
  app.use(compression());
  app.use(base, sirv("./dist/client", { extensions: [] }));
}

// SSR handler
app.use("*", async (req, res) => {
  try {
    const url = req.originalUrl.replace(base, "");

    let template: string;
    let renderFn: (
      url: string,
    ) => Promise<{ html: string; helmet: HelmetData }>;

    if (!isProduction) {
      template = fs.readFileSync(
        path.resolve(__dirname, "index.html"),
        "utf-8",
      );
      template = await vite!.transformIndexHtml(url, template);
      const module = await vite!.ssrLoadModule("/src/entry-server.tsx");
      renderFn = module.render;
    } else {
      template = fs.readFileSync(
        path.resolve(__dirname, "dist/client/index.html"),
        "utf-8",
      );
      const module = await import("./dist/server/entry-server.js");
      renderFn = module.render;
    }

    const { html: appHtml, helmet } = await renderFn(url);

    // Inject app HTML
    let html = template.replace(`<!--app-html-->`, appHtml);

    // Inject helmet head tags
    if (helmet) {
      const headContent = [
        helmet.title.toString(),
        helmet.meta.toString(),
        helmet.link.toString(),
        helmet.script.toString(),
        helmet.style.toString(),
      ].join("");

      html = html.replace(
        /<head>([\s\S]*?)<\/head>/,
        `<head>$1${headContent}</head>`,
      );
    }

    res.status(200).set({ "Content-Type": "text/html" }).send(html);
  } catch (e: unknown) {
    const error = e as Error;
    vite?.ssrFixStacktrace(error);
    console.log(error.stack);
    res.status(500).end(error.stack);
  }
});

app.listen(port, () => {
  console.log(`Server started at http://localhost:${port}`);
});
```

---

### 4. `index.html`

Template with placeholder:

```html
<!DOCTYPE html>
<html lang="sv">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/png" href="/favicon.png" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <!-- Helmet tags injected here by SSR -->
  </head>
  <body>
    <div id="root"><!--app-html--></div>
    <script type="module" src="/src/entry-client.tsx"></script>
  </body>
</html>
```

---

## Package.json Scripts

```json
{
  "scripts": {
    "dev": "npx vite",
    "dev:ssr": "node --import tsx server.ts",
    "build": "npm run build:client && npm run build:server",
    "build:client": "vite build --outDir dist/client",
    "build:server": "vite build --ssr src/entry-server.tsx --outDir dist/server",
    "start": "NODE_ENV=production node dist/server/entry-server.js",
    "preview": "vite preview"
  }
}
```

---

## Dependencies

```json
{
  "dependencies": {
    "react-helmet-async": "^2.0.5",
    "react-router-dom": "^6.30.1"
  },
  "devDependencies": {
    "compression": "^1.8.1",
    "express": "^5.2.1",
    "sirv": "^3.0.2"
  }
}
```

---

## Vite Config for SSR

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react-swc";

export default defineConfig({
  plugins: [react()],
  // SSR-specific config
  ssr: {
    noExternal: [], // Bundle all dependencies for SSR
  },
  build: {
    // Client build outputs to dist/client
    // Server build outputs to dist/server
  },
});
```

---

## SSR-Compatible Shared Packages

### @appcaire/ui

✅ **SSR-safe** - All components work with SSR.

```typescript
// Safe to import in SSR
import { Button, Card, TooltipProvider } from "@appcaire/ui/components/ui";
import { cn } from "@appcaire/ui";
```

### @appcaire/shared

✅ **SSR-safe** - No browser-only APIs in components.

```typescript
// Safe to import in SSR
import { LevelBadge, StatCardHero } from "@appcaire/shared/gamification";
import { MunicipalityStatsCard } from "@appcaire/shared/stats-data-components";
```

### Avoid in SSR context

```typescript
// ❌ UNSAFE - Don't use in entry-server.tsx or components rendered on server
window.scrollTo();
document.title;
localStorage.getItem();

// ✅ SAFE - Use inside useEffect (only runs on client)
useEffect(() => {
  window.scrollTo(0, 0);
}, []);

// ✅ SAFE - Guard with typeof check
if (typeof window !== "undefined") {
  window.scrollTo(0, 0);
}
```

---

## Apollo Client with SSR

For apps using GraphQL (hemtjanstguide, nackahemtjanst, sverigeshemtjanst):

```typescript
// entry-server.tsx
import { ApolloClient, InMemoryCache, ApolloProvider } from "@apollo/client";
import { getDataFromTree } from "@apollo/client/react/ssr";

export async function render(url: string) {
  const client = new ApolloClient({
    ssrMode: true,
    uri: process.env.GRAPHQL_URL,
    cache: new InMemoryCache(),
  });

  const helmetContext = {};

  const App = (
    <ApolloProvider client={client}>
      <HelmetProvider context={helmetContext}>
        <StaticRouter location={url}>
          <AppComponent />
        </StaticRouter>
      </HelmetProvider>
    </ApolloProvider>
  );

  // Pre-fetch all queries
  await getDataFromTree(App);

  const html = renderToString(App);
  const state = client.extract();

  return { html, helmet: helmetContext.helmet, apolloState: state };
}
```

---

## SEO Component Pattern

Each page should use the SEO component:

```typescript
import SEO from "@/components/SEO";

const MyPage = () => {
  return (
    <>
      <SEO
        title="Page Title | Site"
        description="Meta description for the page"
        canonical="https://example.com/page"
        structuredData={{
          "@context": "https://schema.org",
          "@type": "WebPage",
          name: "Page Title",
        }}
      />
      {/* Page content */}
    </>
  );
};
```

---

## Development vs Production

| Mode      | Command        | Description                       |
| --------- | -------------- | --------------------------------- |
| Dev (CSR) | `yarn dev`     | Standard Vite dev server, fastest |
| Dev (SSR) | `yarn dev:ssr` | SSR development with hot reload   |
| Build     | `yarn build`   | Builds client + server bundles    |
| Prod      | `yarn start`   | Runs production SSR server        |

---

## Troubleshooting

### "window is not defined"

Use `typeof window !== 'undefined'` or move to `useEffect`:

```typescript
// ❌ Wrong
const width = window.innerWidth;

// ✅ Correct
const [width, setWidth] = useState(0);
useEffect(() => {
  setWidth(window.innerWidth);
}, []);
```

### Hydration mismatch

Ensure server and client render the same thing:

```typescript
// ❌ Wrong - different on server vs client
const date = new Date().toLocaleString();

// ✅ Correct - use state
const [date, setDate] = useState<string | null>(null);
useEffect(() => {
  setDate(new Date().toLocaleString());
}, []);
```

---

## Checklist for new SSR app

- [ ] Create `src/entry-server.tsx`
- [ ] Create `src/entry-client.tsx`
- [ ] Create `server.ts`
- [ ] Update `index.html` with `<!--app-html-->`
- [ ] Add build scripts to `package.json`
- [ ] Install dependencies (`compression`, `express`, `sirv`)
- [ ] Verify all components are SSR-safe
- [ ] Test with `yarn dev:ssr`
- [ ] Verify meta tags with curl

---

## Related Documents

- [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md) - Meta tags and helmet
- [SEO_CHECKLIST.md](./SEO_CHECKLIST.md) - Pre-deployment checklist
- [APP_DOMAIN_MAPPING.md](../01-arkitektur-strategi/APP_DOMAIN_MAPPING.md) - SSR status per app
