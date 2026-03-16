# 🚀 Asset Optimization Guide

## Overview

This guide covers best practices for optimizing assets in the CAIRE project to improve web performance, reduce bundle size, and enhance user experience.

## Current State Analysis

Based on the asset audit, we have:

- **115 total images** consuming **38.97 MB**
- **73 unused images** wasting **20.1 MB** (51% of total size)
- **42 images actually used**
- Potential total savings: **33.23 MB** (85% reduction)

## 🎯 Optimization Strategy

### 1. Asset Cleanup (Immediate Impact)

**Remove 73 unused images to save 20.1 MB**

```bash
# Run the audit first
pnpm run assets:audit

# Clean up unused assets (creates backup)
pnpm run assets:cleanup
```

**Benefits:**

- 20.1 MB immediate savings
- Faster CI/CD deployments
- Cleaner repository structure
- Reduced Vercel deployment time

### 2. Image Format Optimization

**Convert to modern WebP format with fallbacks**

```bash
# Optimize existing images
pnpm run assets:optimize
```

**Results:**

- 60-80% size reduction with WebP
- Maintains quality
- Progressive enhancement with fallbacks
- Responsive image variants

### 3. Implementation Guidelines

#### ✅ Best Practices

1. **Use Optimized Components**

   ```tsx
   // Use OptimizedLogo for logos
   import { OptimizedLogo } from "@/components/ui/OptimizedLogo";

   // Use ResponsiveImage for content images
   import { ResponsiveImage } from "@/components/ui/ResponsiveImage";

   <ResponsiveImage
     src="/images/product-screenshots/dashboard.jpg"
     alt="CAIRE Dashboard"
     quality="high"
     loading="lazy"
   />;
   ```

2. **Lazy Loading Implementation**

   ```tsx
   // Images below the fold
   loading = "lazy";

   // Critical images (hero, logo)
   loading = "eager";
   ```

3. **Responsive Images with srcset**
   ```tsx
   // Automatically handled by ResponsiveImage component
   sizes = "(max-width: 768px) 100vw, 50vw";
   ```

#### ❌ What to Avoid

- Don't use unoptimized images > 500KB
- Avoid PNG for photos (use JPG or WebP)
- Don't load full-size images for thumbnails
- Avoid multiple image format variants manually

### 4. File Organization Structure

```
public/
├── images/
│   ├── optimized/          # WebP + fallbacks
│   │   ├── image-name.webp
│   │   ├── image-name-small.webp
│   │   └── image-name.jpg
│   ├── logos/             # Brand logos
│   ├── product-screenshots/ # App screenshots
│   ├── features/          # Feature illustrations
│   └── og/               # Open Graph images
├── slides/               # Presentation slides
└── favicon/             # Favicon variants
```

### 5. Performance Monitoring

#### Key Metrics to Track

- **Total bundle size**: Target < 15 MB
- **Largest Contentful Paint (LCP)**: < 2.5s
- **Image load time**: < 1s for critical images
- **WebP adoption rate**: > 80% of users

#### Monitoring Tools

```bash
# Lighthouse audit
pnpm run lighthouse

# Asset audit
pnpm run assets:audit

# Build size analysis
pnpm run build
```

## 🛠️ Available Scripts

| Script                     | Purpose                    | Savings         |
| -------------------------- | -------------------------- | --------------- |
| `pnpm run assets:audit`    | Analyze asset usage        | Identify issues |
| `pnpm run assets:cleanup`  | Remove unused images       | 20.1 MB         |
| `pnpm run assets:optimize` | Convert to WebP + optimize | 13+ MB          |

## 📊 Expected Performance Improvements

### Before Optimization

- Total images: 115 files, 38.97 MB
- Unused assets: 73 files, 20.1 MB
- Large unoptimized images: 24 files
- WebP usage: <10%

### After Optimization

- Total images: 42 files, ~5-6 MB
- Unused assets: 0 files
- All images optimized and responsive
- WebP usage: >90%

### Performance Impact

- **Page load time**: -40-60%
- **First Contentful Paint**: -30-50%
- **Cumulative Layout Shift**: Improved
- **Bundle size**: -85%

## 🔄 Maintenance Workflow

### For New Images

1. **Add images to appropriate folder**

   ```bash
   public/images/product-screenshots/new-feature.jpg
   ```

2. **Run optimization**

   ```bash
   pnpm run assets:optimize
   ```

3. **Use optimized components**
   ```tsx
   <ResponsiveImage
     src="/images/product-screenshots/new-feature.jpg"
     alt="New Feature"
   />
   ```

### Monthly Audit

```bash
# Check for unused assets
pnpm run assets:audit

# Review large files
ls -lah public/images/ | grep -E "[0-9]+M"

# Clean up if needed
pnpm run assets:cleanup
```

## 🚨 Critical Considerations

### SEO Impact

- Maintain alt tags for all images
- Use descriptive filenames
- Ensure Open Graph images remain functional

### Accessibility

- Always provide alt attributes
- Use meaningful descriptions
- Test with screen readers

### Browser Support

- WebP: 95% global support
- Fallbacks ensure 100% compatibility
- Progressive enhancement approach

## 🎯 Implementation Priority

### Phase 1: Immediate (Today)

1. ✅ Run asset audit
2. 🟡 Clean up unused assets (20.1 MB savings)
3. 🟡 Update OptimizedLogo usage

### Phase 2: Optimization (This Week)

1. Convert large images to WebP
2. Implement ResponsiveImage component
3. Add lazy loading to non-critical images

### Phase 3: Monitoring (Ongoing)

1. Set up performance monitoring
2. Regular asset audits
3. Optimize new assets automatically

## 📈 Success Metrics

- **Bundle size reduction**: Target 85% (20+ MB saved)
- **Page Speed Score**: Target 90+ (from current ~70)
- **Core Web Vitals**: All green
- **Deployment time**: -50%

## 🔗 Related Resources

- [Web.dev Image Optimization](https://web.dev/fast/#optimize-your-images)
- [WebP Browser Support](https://caniuse.com/webp)
- [Lighthouse Performance Auditing](https://developers.google.com/web/tools/lighthouse)
- [Vercel Image Optimization](https://vercel.com/docs/concepts/image-optimization)

---

**Next Step**: Run `pnpm run assets:cleanup` to immediately save 20.1 MB! 🚀
