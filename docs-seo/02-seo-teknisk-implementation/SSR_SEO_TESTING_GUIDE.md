# SSR & SEO Testing Guide

> **Last updated:** January 2025  
> **Purpose:** Comprehensive guide for testing SSR functionality and SEO implementation

---

## Table of Contents

1. [Quick Start Testing](#1-quick-start-testing)
2. [SSR Functionality Tests](#2-ssr-functionality-tests)
3. [SEO Meta Tags Tests](#3-seo-meta-tags-tests)
4. [Structured Data Tests](#4-structured-data-tests)
5. [Performance Tests](#5-performance-tests)
6. [Browser Testing](#6-browser-testing)
7. [Automated Testing](#7-automated-testing)

---

## 1. Quick Start Testing

### Test SSR is Working

```bash
# 1. Start SSR development server
yarn workspace hemtjanstguide dev:ssr
# or
yarn workspace nackahemtjanst dev:ssr
# or
yarn workspace sverigeshemtjanst dev:ssr
# or
yarn workspace website dev:ssr

# 2. In another terminal, check the HTML source
curl -s http://localhost:3002 | head -100

# ✅ GOOD: Should see rendered HTML content
# ❌ BAD: Should NOT see empty <div id="root"></div>
```

### Test SEO Meta Tags

```bash
# Check meta tags are present
curl -s http://localhost:3002 | grep -E "<title>|<meta name=\"description\"|<link rel=\"canonical\""

# Should output:
# <title>Hemtjänstguide - Hitta hemtjänst i Sverige</title>
# <meta name="description" content="..."/>
# <link rel="canonical" href="..."/>
```

---

## 2. SSR Functionality Tests

### 2.1 Verify Server-Side Rendering

**Test:** HTML should be pre-rendered on the server, not empty.

```bash
# Start SSR server
yarn workspace hemtjanstguide dev:ssr

# Check raw HTML (should contain content, not just <div id="root"></div>)
curl -s http://localhost:3002 | grep -A 20 "<div id=\"root\">"

# ✅ Expected: HTML content inside root div
# ❌ Bad: Empty <div id="root"></div>
```

**Manual Browser Test:**

1. Open `http://localhost:3002` in browser
2. Right-click → "View Page Source" (NOT Inspect Element)
3. Search for `<div id="root">`
4. ✅ Should see rendered HTML content
5. ❌ Should NOT see empty `<div id="root"></div>`

### 2.2 Verify Client Hydration

**Test:** React should hydrate without errors.

```bash
# Start SSR server
yarn workspace hemtjanstguide dev:ssr

# Open browser console and check for:
# ✅ No hydration errors
# ✅ No "Warning: Text content did not match" errors
# ✅ Page is interactive (click buttons, navigate)
```

**Browser Console Check:**

1. Open DevTools → Console
2. Look for:
   - ✅ No `Warning: Text content did not match`
   - ✅ No `Hydration failed` errors
   - ✅ No `Uncaught Error` related to React

### 2.3 Test Client-Side Navigation

**Test:** Navigation should work without full page reload.

```bash
# Start SSR server
yarn workspace hemtjanstguide dev:ssr
```

**Manual Test:**

1. Navigate to `http://localhost:3002`
2. Click a navigation link
3. ✅ URL should change
4. ✅ Content should update (no full page reload)
5. ✅ Browser back/forward buttons work
6. ✅ View Page Source shows correct HTML for new route

### 2.4 Test Production Build

**Test:** Production SSR should work correctly.

```bash
# Build for production
yarn workspace hemtjanstguide build

# Start production server
yarn workspace hemtjanstguide start

# Test in another terminal
curl -s http://localhost:3002 | head -50

# ✅ Should see complete HTML with content
```

---

## 3. SEO Meta Tags Tests

### 3.1 Basic Meta Tags

**Test:** Every page should have essential meta tags.

```bash
# Check homepage
curl -s http://localhost:3002 | grep -E "<title>|<meta name=\"description\"|<link rel=\"canonical\""

# Check specific page
curl -s http://localhost:3002/utforare | grep -E "<title>|<meta name=\"description\"|<link rel=\"canonical\""
```

**Expected Output:**

```html
<title>anordnare - Hemtjänstguide</title>
<meta name="description" content="Hitta hemtjänstutförare i din kommun..." />
<link rel="canonical" href="https://hemtjanstguide.se/utforare" />
```

### 3.2 Open Graph Tags

**Test:** Social media sharing should work.

```bash
# Check Open Graph tags
curl -s http://localhost:3002 | grep -E "og:|property=\"og:"

# Should see:
# <meta property="og:title" content="..."/>
# <meta property="og:description" content="..."/>
# <meta property="og:image" content="..."/>
# <meta property="og:url" content="..."/>
# <meta property="og:type" content="website"/>
```

**Online Validators:**

- [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
- [LinkedIn Post Inspector](https://www.linkedin.com/post-inspector/)
- [Twitter Card Validator](https://cards-dev.twitter.com/validator)

### 3.3 Twitter Card Tags

**Test:** Twitter cards should be configured.

```bash
# Check Twitter Card tags
curl -s http://localhost:3002 | grep -E "twitter:|name=\"twitter:"

# Should see:
# <meta name="twitter:card" content="summary_large_image"/>
# <meta name="twitter:title" content="..."/>
# <meta name="twitter:description" content="..."/>
# <meta name="twitter:image" content="..."/>
```

### 3.4 Language and Locale

**Test:** HTML lang attribute should be set.

```bash
# Check HTML lang attribute
curl -s http://localhost:3002 | grep "<html"

# Should see:
# <html lang="sv">
```

### 3.5 Robots Meta Tags

**Test:** Robots directives should be correct.

```bash
# Check robots meta
curl -s http://localhost:3002 | grep -i "robots"

# Should see:
# <meta name="robots" content="index, follow"/>
```

---

## 4. Structured Data Tests

### 4.1 JSON-LD Validation

**Test:** Structured data should be valid JSON-LD.

```bash
# Extract JSON-LD
curl -s http://localhost:3002 | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq .

# Should output valid JSON
```

**Online Validators:**

- [Google Rich Results Test](https://search.google.com/test/rich-results)
- [Schema.org Validator](https://validator.schema.org/)

### 4.2 Test Different Schema Types

**Homepage:**

```bash
curl -s http://localhost:3002 | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq '.@type'

# Should see: "WebSite" or "Organization"
```

**Article Pages:**

```bash
curl -s http://localhost:3002/resurser/artiklar/... | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq '.@type'

# Should see: "Article"
```

**Provider Pages (sverigeshemtjanst):**

```bash
curl -s http://localhost:3001/utforare/... | grep -oP '(?<=application/ld\+json">).*(?=</script>)' | jq '.@type'

# Should see: "LocalBusiness"
```

---

## 5. Performance Tests

### 5.1 Lighthouse Audit

**Test:** Run Lighthouse for SEO, Performance, Accessibility.

```bash
# Install Lighthouse globally (if not installed)
npm install -g lighthouse

# Run audit
lighthouse http://localhost:3002 --view --output-path=./lighthouse-report.html

# Or use Chrome DevTools:
# 1. Open DevTools → Lighthouse tab
# 2. Select "SEO" + "Performance"
# 3. Click "Analyze page load"
```

**Target Scores:**

- SEO: 90+
- Performance: 80+
- Accessibility: 90+

### 5.2 Core Web Vitals

**Test:** Check LCP, FID, CLS.

```bash
# Use PageSpeed Insights
# https://pagespeed.web.dev/

# Or Chrome DevTools:
# 1. Open DevTools → Performance tab
# 2. Record page load
# 3. Check Web Vitals section
```

**Targets:**

- LCP (Largest Contentful Paint): < 2.5s
- FID (First Input Delay): < 100ms
- CLS (Cumulative Layout Shift): < 0.1

### 5.3 Network Analysis

**Test:** Check bundle sizes and load times.

```bash
# Chrome DevTools:
# 1. Open DevTools → Network tab
# 2. Reload page
# 3. Check:
#    - Total page size < 2MB
#    - JavaScript bundles < 500KB each
#    - CSS < 200KB
```

---

## 6. Browser Testing

### 6.1 Cross-Browser Test

**Test:** SSR should work in all major browsers.

```bash
# Test in:
# ✅ Chrome/Edge (Chromium)
# ✅ Firefox
# ✅ Safari
# ✅ Mobile Safari (iOS)
# ✅ Chrome Mobile (Android)
```

**Checklist:**

- [ ] Page renders correctly
- [ ] Navigation works
- [ ] No console errors
- [ ] Meta tags present (View Source)
- [ ] Interactive elements work

### 6.2 Mobile Testing

**Test:** Responsive design and mobile SEO.

```bash
# Chrome DevTools:
# 1. Open DevTools → Toggle device toolbar
# 2. Test different devices:
#    - iPhone 12/13/14
#    - iPad
#    - Samsung Galaxy
```

**Checklist:**

- [ ] Viewport meta tag: `<meta name="viewport" content="width=device-width, initial-scale=1">`
- [ ] Text is readable (no zoom required)
- [ ] Touch targets are 44px minimum
- [ ] No horizontal scrolling

---

## 7. Automated Testing

### 7.1 Create Test Script

Create a test script to automate checks:

```bash
# Create test script
cat > scripts/test-ssr-seo.sh << 'EOF'
#!/bin/bash

APP_URL="http://localhost:3002"
echo "Testing SSR and SEO for $APP_URL"

# Test 1: Check HTML is rendered
echo "1. Checking SSR..."
HTML=$(curl -s $APP_URL)
if echo "$HTML" | grep -q '<div id="root"><!--app-html-->'; then
  echo "❌ FAIL: Empty root div (SSR not working)"
  exit 1
else
  echo "✅ PASS: HTML is server-rendered"
fi

# Test 2: Check title tag
echo "2. Checking title tag..."
if echo "$HTML" | grep -q '<title>'; then
  echo "✅ PASS: Title tag present"
else
  echo "❌ FAIL: Title tag missing"
  exit 1
fi

# Test 3: Check meta description
echo "3. Checking meta description..."
if echo "$HTML" | grep -q '<meta name="description"'; then
  echo "✅ PASS: Meta description present"
else
  echo "❌ FAIL: Meta description missing"
  exit 1
fi

# Test 4: Check canonical URL
echo "4. Checking canonical URL..."
if echo "$HTML" | grep -q '<link rel="canonical"'; then
  echo "✅ PASS: Canonical URL present"
else
  echo "❌ FAIL: Canonical URL missing"
  exit 1
fi

# Test 5: Check Open Graph tags
echo "5. Checking Open Graph tags..."
OG_COUNT=$(echo "$HTML" | grep -c 'property="og:')
if [ "$OG_COUNT" -ge 4 ]; then
  echo "✅ PASS: Open Graph tags present ($OG_COUNT tags)"
else
  echo "❌ FAIL: Missing Open Graph tags (found $OG_COUNT, expected 4+)"
  exit 1
fi

# Test 6: Check structured data
echo "6. Checking structured data..."
if echo "$HTML" | grep -q 'application/ld+json'; then
  echo "✅ PASS: Structured data present"
else
  echo "❌ FAIL: Structured data missing"
  exit 1
fi

echo ""
echo "✅ All tests passed!"
EOF

chmod +x scripts/test-ssr-seo.sh

# Run test
./scripts/test-ssr-seo.sh
```

### 7.2 Add to package.json

```json
{
  "scripts": {
    "test:ssr": "bash scripts/test-ssr-seo.sh",
    "test:seo": "curl -s http://localhost:3002 | grep -E '(title>|description|canonical|og:|twitter:)'"
  }
}
```

---

## Quick Reference Commands

### SSR Testing

```bash
# Start SSR dev server
yarn workspace <app> dev:ssr

# Check HTML is rendered
curl -s http://localhost:3002 | grep -A 20 "<div id=\"root\">"

# Build and test production
yarn workspace <app> build && yarn workspace <app> start
```

### SEO Testing

```bash
# Check all meta tags
curl -s http://localhost:3002 | grep -E "(title>|description|canonical|og:|twitter:)"

# Check structured data
curl -s http://localhost:3002 | grep "application/ld+json" | jq .

# Check sitemap
curl -s http://localhost:3002/sitemap.xml | head -20

# Check robots.txt
curl -s http://localhost:3002/robots.txt
```

### Performance Testing

```bash
# Lighthouse audit
lighthouse http://localhost:3002 --view

# PageSpeed Insights (online)
# https://pagespeed.web.dev/
```

---

## Common Issues & Solutions

### Issue: Empty HTML in View Source

**Symptom:** `<div id="root"></div>` is empty in View Source.

**Solution:**

1. Check SSR server is running: `yarn workspace <app> dev:ssr`
2. Verify `entry-server.tsx` exists and exports `render()` function
3. Check `server.ts` is calling `render()` function
4. Check browser console for errors

### Issue: Hydration Mismatch

**Symptom:** Console shows "Text content did not match" warnings.

**Solution:**

1. Ensure server and client render the same content
2. Check for `typeof window !== 'undefined'` guards
3. Avoid using `Date.now()` or `Math.random()` in render
4. Use `useEffect` for client-only code

### Issue: Meta Tags Not Showing

**Symptom:** Meta tags missing in View Source.

**Solution:**

1. Check `react-helmet-async` is configured in `entry-server.tsx`
2. Verify `HelmetProvider` wraps the app
3. Check helmet data is injected in `server.ts`
4. Ensure `<head>` tag exists in `index.html`

### Issue: Structured Data Invalid

**Symptom:** Google Rich Results Test shows errors.

**Solution:**

1. Validate JSON-LD syntax: `jq .` on extracted JSON
2. Check required fields for schema type
3. Use [Schema.org Validator](https://validator.schema.org/)
4. Ensure JSON is properly escaped in HTML

---

## Related Documents

- [VITE_SSR_SETUP.md](./VITE_SSR_SETUP.md) - SSR implementation guide
- [SEO_COMPONENT_GUIDE.md](./SEO_COMPONENT_GUIDE.md) - Meta tags component usage
- [SEO_CHECKLIST.md](./SEO_CHECKLIST.md) - Pre-deployment checklist
- [STRUCTURED_DATA_GUIDE.md](./STRUCTURED_DATA_GUIDE.md) - Structured data implementation
