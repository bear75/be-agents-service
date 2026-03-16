# SEO Pre-Deployment Checklist

> **Last updated:** January 2025

## Overview

Use this checklist before deploying an SEO site to production.

---

## 1. SSR & Rendering

### Server-Side Rendering

- [ ] `entry-server.tsx` exists and exports `render()` function
- [ ] `entry-client.tsx` exists and uses `hydrateRoot()`
- [ ] `server.ts` Express server configured
- [ ] `index.html` has `<!--app-html-->` placeholder
- [ ] Build scripts: `build:client` and `build:server`

### Verify SSR Works

```bash
# Start production server
yarn build && yarn start

# Verify HTML is rendered server-side
curl -s http://localhost:3000 | head -50

# Should see complete HTML, NOT empty <div id="root"></div>
```

---

## 2. Meta Tags

### Every page should have

- [ ] Unique `<title>` (50-60 characters)
- [ ] Unique `<meta name="description">` (150-160 characters)
- [ ] `<link rel="canonical">` with absolute URL
- [ ] `<html lang="sv">` attribute

### Open Graph

- [ ] `og:title`
- [ ] `og:description`
- [ ] `og:image` (1200x630 px)
- [ ] `og:url`
- [ ] `og:type` (website/article)
- [ ] `og:locale` (sv_SE)

### Twitter Card

- [ ] `twitter:card` (summary_large_image)
- [ ] `twitter:title`
- [ ] `twitter:description`
- [ ] `twitter:image`

### AI Agent Directives

- [ ] `<meta name="GPTBot" content="index, follow">`
- [ ] `<meta name="anthropic-ai" content="index, follow">`
- [ ] `<meta name="CCBot" content="index, follow">`
- [ ] `<meta name="PerplexityBot" content="index, follow">`

---

## 3. Structured Data (JSON-LD)

### Homepage

- [ ] `WebSite` schema
- [ ] `Organization` schema

### Article Pages

- [ ] `Article` schema
- [ ] `BreadcrumbList` schema

### FAQ Pages

- [ ] `FAQPage` schema

### Provider Pages (sverigeshemtjanst)

- [ ] `LocalBusiness` schema

### Validation

- [ ] Test with [Rich Results Test](https://search.google.com/test/rich-results)
- [ ] Test with [Schema Validator](https://validator.schema.org/)

---

## 4. HTML Structure

### Heading Hierarchy

- [ ] Exactly ONE `<h1>` per page
- [ ] `<h1>` contains primary keyword
- [ ] Logical hierarchy: h1 → h2 → h3

### Semantic HTML

- [ ] Use `<main>`, `<article>`, `<section>`, `<nav>`
- [ ] Use `<header>` and `<footer>`

### Images

- [ ] All images have `alt` text
- [ ] Images are optimized (WebP/AVIF)
- [ ] Lazy loading for images below fold

---

## 5. Sitemap & Robots

### sitemap.xml

- [ ] Generated at build
- [ ] All public routes included
- [ ] Correct `<lastmod>` dates
- [ ] Correct `<priority>` values

### robots.txt

- [ ] Exists in `public/`
- [ ] `Allow: /` for all crawlers
- [ ] AI agent directives
- [ ] `Sitemap:` reference

### Verification

```bash
# Check robots.txt
curl https://example.com/robots.txt

# Check sitemap
curl https://example.com/sitemap.xml | head -50
```

---

## 6. Performance

### Core Web Vitals

- [ ] LCP < 2.5s
- [ ] FID < 100ms
- [ ] CLS < 0.1

### Optimizations

- [ ] Gzip/Brotli compression
- [ ] Code splitting (vendor chunks)
- [ ] CSS optimized (purge unused)
- [ ] Font preloading

### Tools

- [ ] [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [ ] [PageSpeed Insights](https://pagespeed.web.dev/)

---

## 7. Technical

### HTTPS

- [ ] SSL certificate configured
- [ ] HTTP → HTTPS redirect

### URLs

- [ ] Trailing slash consistent
- [ ] No broken links (404)
- [ ] Redirect loops checked

### Mobile

- [ ] Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] Responsive design
- [ ] Touch-friendly (44px tap targets)

---

## 8. Google Search Console

### Setup

- [ ] Domain verified
- [ ] Sitemap submitted
- [ ] All team members have access

### Check

- [ ] No coverage errors
- [ ] Core Web Vitals passing
- [ ] Mobile usability OK

---

## 9. Analytics

### Google Analytics 4

- [ ] GA4 property created
- [ ] Tracking code implemented
- [ ] Page views tracked
- [ ] Conversion events configured

### Environment Variables

```env
VITE_GA_ID=G-XXXXXXXXXX
```

---

## 10. Final Verification

### Browser Test

- [ ] Test in Chrome
- [ ] Test in Firefox
- [ ] Test in Safari
- [ ] Test on mobile

### SEO Test

```bash
# Verify meta tags
curl -s https://example.com | grep -E "<title>|<meta|<link rel=\"canonical\""

# Verify structured data
curl -s https://example.com | grep "application/ld+json"
```

### Social Preview

- [ ] Test Facebook debugger: [developers.facebook.com/tools/debug](https://developers.facebook.com/tools/debug)
- [ ] Test LinkedIn Post Inspector
- [ ] Test Twitter Card Validator

---

## Quick Verification Commands

```bash
# All-in-one check
curl -s https://example.com | grep -E "(title>|description|canonical|og:|twitter:)" | head -20

# Check structured data
curl -s https://example.com | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq .

# Check sitemap
curl -s https://example.com/sitemap.xml | grep "<loc>"

# Check robots
curl -s https://example.com/robots.txt
```

---

## Related Documents

- [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md)
- [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md)
- [SITEMAP_ROBOTS.md](./SITEMAP_ROBOTS.md)
- [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md)
