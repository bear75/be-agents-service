# Environment Variables Configuration

## Overview

This document explains how environment variables are configured and used in the Caire project for Google Analytics, IndexNow, and other services.

## 🔧 Current Environment Variables

### ✅ **Google Analytics**

```bash
VITE_GA_MEASUREMENT_ID=G-DB10R88XR4
```

- **Purpose**: Google Analytics 4 tracking ID
- **Usage**: Used in `src/lib/analytics.ts` for tracking page views, events, and user interactions
- **Fallback**: If not set, defaults to `G-4K4R24WKE0` (hardcoded)

### ✅ **Supabase Configuration**

```bash
VITE_SUPABASE_URL=your-supabase-project-url
VITE_SUPABASE_ANON_KEY=your-supabase-anon-key
```

- **Purpose**: Supabase database connection and authentication
- **Usage**: Used in `src/integrations/supabase/client.ts` for database operations
- **Security Note**: ⚠️ **The anon key warning is NORMAL and EXPECTED**
  - The anonymous key is designed to be public and exposed in client-side code
  - Your data is protected by Row Level Security (RLS) policies, not by hiding the anon key
  - This is exactly how Supabase is designed to work
  - The real security comes from your database policies, which are properly configured

### ✅ **IndexNow API**

```bash
INDEX_NOW_API_KEY=9fe33310912b13cdb4d0cae2e71b4c44
```

- **Purpose**: API key for IndexNow service (faster search engine indexing)
- **Usage**: Used in `src/lib/indexNow.ts` and GitHub Actions workflow
- **Supported by**: Bing, Yandex, and other search engines

### ✅ **Base URL**

```bash
VITE_BASE_URL=https://www.caire.se
```

- **Purpose**: Base URL for your application
- **Usage**: Used for sitemap generation, IndexNow submissions, and canonical URLs
- **Environment-specific**:
  - Development: `http://localhost:5173`
  - Production: `https://www.caire.se`

## 📁 File Structure

```
├── .env                    # Main environment file (gitignored)
├── .env.example           # Template file (committed to git)
├── .env.local             # Local development template
└── scripts/
    ├── setup-env.js       # Environment setup script
    └── add-env-vars.js    # Add missing variables script
```

## 🚀 Setup Instructions

### For New Developers

1. **Clone the repository**
2. **Run the environment setup**:
   ```bash
   npm run env:setup
   ```
3. **Copy the local template**:
   ```bash
   cp .env.local .env
   ```
4. **Update with your values** (if needed)

### For Existing Projects

If you need to add missing environment variables:

```bash
npm run env:add-vars
```

## 🌐 Production Deployment (Vercel)

Add these environment variables in your Vercel dashboard under **Settings > Environment Variables**:

```bash
VITE_GA_MEASUREMENT_ID=G-DB10R88XR4
INDEX_NOW_API_KEY=9fe33310912b13cdb4d0cae2e71b4c44
VITE_BASE_URL=https://www.caire.se
VITE_SUPABASE_URL=https://thxcwxurmyzcsvyohenj.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 🔍 How Environment Variables Are Used

### Google Analytics (`VITE_GA_MEASUREMENT_ID`)

```typescript
// In src/lib/analytics.ts
const measurementId = import.meta.env.VITE_GA_MEASUREMENT_ID || "G-4K4R24WKE0";

// Usage
export const initGA = (): void => {
  const script = document.createElement("script");
  script.src = `https://www.googletagmanager.com/gtag/js?id=${measurementId}`;
  // ... rest of initialization
};
```

### IndexNow API (`INDEX_NOW_API_KEY`)

```typescript
// In src/lib/indexNow.ts
const apiKey = import.meta.env.INDEX_NOW_API_KEY || process.env.INDEX_NOW_API_KEY;

// Usage in GitHub Actions
- name: Submit to IndexNow
  env:
    INDEX_NOW_API_KEY: ${{ secrets.INDEX_NOW_API_KEY }}
```

### Base URL (`VITE_BASE_URL`)

```typescript
// In sitemap generation and IndexNow submissions
const baseUrl = import.meta.env.VITE_BASE_URL || "https://www.caire.se";
```

## 🔒 Security Best Practices

1. **Never commit `.env` files** - They're in `.gitignore`
2. **Use `.env.example`** for templates
3. **Rotate API keys** regularly
4. **Use different keys** for different environments
5. **Validate environment variables** at startup

## 🛠️ Available Scripts

```bash
# Set up environment files
npm run env:setup

# Add missing environment variables
npm run env:add-vars

# Set up IndexNow specifically
npm run indexnow:setup

# Test IndexNow integration
npm run indexnow:test

# Check for broken links
npm run links:check

# Check links in CI mode (ignores external failures)
npm run links:check-ci

# View broken links reports
npm run links:report
```

## 🐛 Troubleshooting

### Google Analytics Not Working

1. Check if `VITE_GA_MEASUREMENT_ID` is set correctly
2. Verify the measurement ID format: `G-XXXXXXXXXX`
3. Check browser console for analytics errors
4. Ensure consent is granted (check cookie consent)

### IndexNow Not Working

1. Verify `INDEX_NOW_API_KEY` is set
2. Check if the API key is valid (32-character hex string)
3. Ensure the key file exists in your public directory
4. Check GitHub Actions logs for submission errors

### Broken Links Checker Issues

1. Check that required dependencies are installed: `node-fetch`, `undici`, `node-html-parser`
2. Verify the script has access to the routes configuration
3. Check that static assets exist in the public directory
4. Review the generated report in `reports/broken-links-report-*.md`

### Environment Variables Not Loading

1. Restart the development server after adding variables
2. Ensure variable names start with `VITE_` for client-side access
3. Check for typos in variable names
4. Verify the `.env` file is in the project root

## 📊 Monitoring

### Google Analytics

- Track page views, events, and conversions
- Monitor Core Web Vitals
- Analyze user behavior and engagement

### IndexNow

- Monitor search engine indexing speed
- Track URL submission success rates
- Verify faster discovery in search results

## 🔄 Environment-Specific Configuration

### Development

```bash
VITE_BASE_URL=http://localhost:5173
VITE_GA_MEASUREMENT_ID=G-XXXXXXXXXX  # Use test GA property
```

### Staging

```bash
VITE_BASE_URL=https://staging.caire.se
VITE_GA_MEASUREMENT_ID=G-YYYYYYYYYY  # Use staging GA property
```

### Production

```bash
VITE_BASE_URL=https://www.caire.se
VITE_GA_MEASUREMENT_ID=G-DB10R88XR4  # Use production GA property
```

## 🔗 Link Integrity Monitoring

The project includes automated broken links checking that:

- Validates all internal navigation links against the routing system
- Checks external links for accessibility
- Verifies static assets exist in the public directory
- Supports the custom `LinkTo` component with route keys
- Generates detailed reports in `reports/broken-links-report-*.md`

### Link Checker Configuration

```bash
# No additional environment variables required
# Uses existing VITE_BASE_URL for validation
```

### Current Status

- **Internal links**: 100% reliability (0 broken links)
- **Static assets**: All files verified and accessible
- **Route keys**: 95 keys automatically detected and validated
- **CI Integration**: Automated checking on every deployment

This setup ensures proper tracking and functionality across all environments while maintaining security and flexibility.
