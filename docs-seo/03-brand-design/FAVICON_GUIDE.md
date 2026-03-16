# Favicon Guide - Design & Setup

## Overview

All favicon files are configured in:

- `index.html` - Base favicon links in each app
- `packages/shared/seo/components/Favicons.tsx` - Dynamic favicon component (shared)
- `packages/shared/seo/components/DefaultSeo.tsx` - Includes Favicons component

## Design: Caire Brand Icon with Site Colors

We use the **Caire brand icon** (handshake + heart in rounded square) with site-specific colors. This matches the Caire logo style and provides excellent brand recognition.

### Why Icon-Based Favicons?

1. **Better at Small Sizes**: Logos are too complex to be recognizable at 16x16 or 32x32 pixels
2. **Brand Consistency**: Same icon across all sites maintains brand unity
3. **Site Differentiation**: Different colors help users distinguish between sites
4. **Social Media**: Works better for social sharing previews
5. **Professional**: Clean, modern look that scales well

## Design Specifications

### Icon Design

- **Base Icon**: Caire brand icon - Handshake + Heart in rounded square
- **Style**: Matches Caire logo style - rounded square with gradient background, white handshake+heart icon inside
- **Background**: Rounded square with site-specific color gradient
- **Icon**: White handshake inside white heart outline

### Site-Specific Colors (from `Favicons.tsx`)

| Site              | Color   | Hex Code  | Usage               | Notes                        |
| ----------------- | ------- | --------- | ------------------- | ---------------------------- |
| sverigeshemtjanst | Indigo  | `#4f46e5` | National B2B brand  | Uses stockholm favicon files |
| stockholm         | Blue    | `#0ea5e9` | Primary brand color |                              |
| nacka             | Emerald | `#10b981` | Primary brand color |                              |
| innovation        | Purple  | `#8b5cf6` | Primary brand color |                              |
| hemtjanstguide    | Amber   | `#f59e0b` | Primary brand color |                              |
| nackahemtjanst    | Rose    | `#f43f5e` | Primary brand color |                              |

## File Naming Convention

All favicon files should follow this pattern:

```
favicon-[site]-[size].[ext]
```

Examples:

- `favicon-stockholm-16x16.png`
- `favicon-stockholm-32x32.png`
- `favicon-stockholm-180x180.png`
- `favicon-stockholm.ico`
- `favicon-nacka-16x16.png`
- etc.

## Required Files Per Site

Place these files in the `public/` directory:

### Standard Favicons

- `favicon-[site]-16x16.png` - 16x16 PNG
- `favicon-[site]-32x32.png` - 32x32 PNG
- `favicon-[site].ico` - Multi-resolution ICO file (16x16, 32x32, 48x48)

### Apple Touch Icons

- `favicon-[site]-180x180.png` (required)
- `favicon-[site]-152x152.png`
- `favicon-[site]-144x144.png`
- `favicon-[site]-120x120.png`
- `favicon-[site]-114x114.png`
- `favicon-[site]-76x76.png`
- `favicon-[site]-72x72.png`
- `favicon-[site]-60x60.png`
- `favicon-[site]-57x57.png`

### Android Chrome Icons

- `favicon-[site]-192x192.png` - 192x192
- `favicon-[site]-512x512.png` - 512x512

### Microsoft Tiles

- `favicon-[site]-144x144.png` (reuse from Apple)
- `favicon-[site]-150x150.png`
- `favicon-[site]-310x310.png`
- `favicon-[site]-310x150.png` (wide tile)
- `favicon-[site]-70x70.png`

## Generating Favicons

### Option 1: Using the Script (Recommended)

1. Install sharp:

   ```bash
   npm install --save-dev sharp
   ```

2. Generate favicons from a logo:

   ```bash
   npm run favicons:generate [logo-file]
   ```

   Example:

   ```bash
   npm run favicons:generate hemtjanstistockholm-logo.png
   ```

### Option 2: Online Tools

Use online favicon generators:

- [RealFaviconGenerator](https://realfavicongenerator.net/)
- [Favicon.io](https://favicon.io/)
- [Favicon Generator](https://www.favicon-generator.org/)

Upload your logo and download all sizes.

### Option 3: Design Tools (Figma/Sketch)

1. Create the base icon (handshake + heart)
2. Export at all required sizes
3. Apply site-specific colors
4. Export as PNG/ICO

### Option 4: ImageMagick

```bash
# Install ImageMagick (macOS)
brew install imagemagick

# Generate favicons
convert public/hemtjanstistockholm-logo.png -resize 16x16 public/favicon-16x16.png
convert public/hemtjanstistockholm-logo.png -resize 32x32 public/favicon-32x32.png
convert public/hemtjanstistockholm-logo.png -resize 180x180 public/apple-touch-icon.png
# ... repeat for all sizes

# Create ICO file
convert public/favicon-16x16.png public/favicon-32x32.png public/favicon.ico
```

## Site-Specific Favicons

The `Favicons` component (in `packages/shared/seo/components/Favicons.tsx`) automatically selects site-specific favicons based on the `siteKey` prop:

```typescript
// Usage in app
import { Favicons } from "@appcaire/shared/seo";

// In component
<Favicons siteKey="sverigeshemtjanst" />
```

### Favicon Mapping

| Site Key            | Favicon Prefix           | Theme Color         |
| ------------------- | ------------------------ | ------------------- |
| `sverigeshemtjanst` | `favicon-stockholm`      | `#4f46e5` (Indigo)  |
| `stockholm`         | `favicon-stockholm`      | `#0ea5e9` (Blue)    |
| `nacka`             | `favicon-nacka`          | `#10b981` (Emerald) |
| `innovation`        | `favicon-innovation`     | `#8b5cf6` (Purple)  |
| `hemtjanstguide`    | `favicon-hemtjanstguide` | `#f59e0b` (Amber)   |
| `nackahemtjanst`    | `favicon-nackahemtjanst` | `#f43f5e` (Rose)    |

Note: `sverigeshemtjanst` uses the same favicon files as `stockholm` (both use the blue favicon) but has a different theme color (Indigo for meta tags).

## Design Checklist

- [ ] Icon is recognizable at 16x16 pixels
- [ ] Icon works on both light and dark backgrounds
- [ ] Colors match site brand colors exactly
- [ ] All sizes generated (16x16 through 512x512)
- [ ] ICO file includes multiple resolutions
- [ ] Files follow naming convention
- [ ] Tested in browser tabs
- [ ] Tested on iOS (Apple touch icons)
- [ ] Tested on Android (Chrome icons)
- [ ] Tested social media sharing

## Alternative: Using Logos

If you prefer to use the existing logos:

1. **Simplify the logo** - Remove text, keep only the icon/symbol
2. **Ensure it works at 16x16** - If not readable, use the icon approach instead
3. **Follow the same file naming** - Just replace "favicon" with "logo" if needed
4. **Update Favicons.tsx** - Change the `faviconMap` to point to logo files

## Testing

1. Open the site in a browser
2. Check browser tab for favicon
3. Test on mobile devices (iOS/Android)
4. Use [RealFaviconGenerator's checker](https://realfavicongenerator.net/favicon_checker) to verify all sizes

## Notes

- Favicons are cached aggressively by browsers - use versioning or cache busting if updating
- The `browserconfig.xml` file is already configured for Windows tiles
- All favicon links are included in `index.html` for immediate availability
- The `Favicons` component adds dynamic favicon support via React Helmet
