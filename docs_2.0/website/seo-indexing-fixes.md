# SEO Indexing Fixes for Caire Website

## Summary of Implemented Fixes

We've addressed the SEO indexing issues identified in Google Search Console by implementing the following changes:

1. **Fixed Redirect Issues**
   - Updated all SEO components to use `https://www.caire.se` instead of `https://caire.se` to prevent redirects
   - Modified canonical URLs in `DefaultSeo.tsx`, `PageSeo.tsx`, and `ArticleSeo.tsx`
   - Updated hreflang alternate links to use the canonical domain
   - Modified organization data to use the www subdomain consistently

2. **Added Multilingual SEO Support**
   - Added proper hreflang tags for Swedish and English content
   - Implemented x-default tags pointing to Swedish (default language)
   - Added language metadata to improve language detection

3. **Fixed Resource Pages**
   - Added logic to prevent resource pages from being accidentally noindexed
   - Added specific checks for blog and resource paths

4. **Maintenance Tools**
   - Created `scripts/fix-indexing.js` to detect and fix indexing issues
   - Created `scripts/generate-sitemap.js` to generate a fresh sitemap
   - Created `scripts/seo-maintenance.sh` script to automate regular SEO checks

## Remaining Tasks

1. **Update Internal Links**
   - 39 internal links still using `https://caire.se` instead of the canonical `https://www.caire.se`
   - Run: `grep -r "https://caire.se" --include="*.tsx" --include="*.jsx" --include="*.ts" --include="*.js" src/` to find them
   - Update them in all components, particularly in:
     - `src/components/AboutSection.tsx`
     - `src/components/seo/MetaTags.tsx`
     - `src/components/seo/PageSeo.tsx`
     - `src/components/seo/ArticleSeo.tsx`

2. **Create robots.txt**
   - Add a robots.txt file to explicitly allow search engines to crawl your site
   - Example:

     ```
     User-agent: *
     Allow: /

     Sitemap: https://www.caire.se/sitemap.xml
     ```

3. **Verify in Google Search Console**
   - Submit the new sitemap to Google Search Console
   - Request indexing for key pages directly via Search Console
   - Set up regular monitoring of indexing issues

## Maintenance Routine

To keep your site well-indexed:

1. Run the SEO maintenance script regularly: `./scripts/seo-maintenance.sh`
2. Check Google Search Console weekly for new indexing issues
3. Generate a fresh sitemap at least monthly: `node scripts/generate-sitemap.js`
4. Submit important new pages to search engines manually

## Technical Implementation

The implemented fixes focus on:

1. **Canonical URL Consistency**: Using www.caire.se consistently throughout the site
2. **Multilingual Support**: Proper language tags and alternate links
3. **Resource Indexing**: Ensuring important pages are properly indexed
4. **Automatic Monitoring**: Tools to detect and fix issues

These changes should resolve the indexing issues reported in Google Search Console.
