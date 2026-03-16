# SEO Tools Documentation

This document outlines the SEO tools available in the Caire project for monitoring and improving search engine optimization.

## Available Tools

The following tools are available to help maintain and improve the site's SEO:

### 1. Alt Text Checker

Scans the codebase for images without appropriate alt text, which is critical for both accessibility and SEO.

```bash
npm run seo:alt-check
```

### 2. Structured Data Validator

Validates structured data (JSON-LD) implementations across the codebase to ensure they follow schema.org standards.

```bash
npm run seo:structured-data
```

### 3. Comprehensive SEO Audit

Performs a full SEO audit, checking:

- Alt text completeness
- Structured data validity
- Meta description uniqueness and length
- Heading hierarchy
- hreflang implementation

```bash
npm run seo:audit
```

The audit generates a detailed report in the `reports/` directory with issues found and recommendations.

### 4. Full SEO Analysis

Runs the comprehensive SEO audit and also performs a Lighthouse analysis for additional performance and SEO metrics.

```bash
npm run seo:full
```

### 5. Sitemap Generation

Updates the sitemap.xml file with the latest content and proper hreflang support.

```bash
npm run sitemap        # Basic sitemap
npm run sitemap:unified # Full sitemap with all content types
```

## Integration into CI/CD

These tools can be integrated into your CI/CD pipeline:

1. Add the SEO audit to your pre-commit or pre-push hooks:

```bash
npx husky add .husky/pre-push "npm run seo:audit"
```

2. Add the alt text check to your pre-commit hook:

```bash
npx husky add .husky/pre-commit "npm run seo:alt-check"
```

## Best Practices

For optimal SEO:

1. **Alt Text**: All images should have descriptive alt text that explains the image content.
   - Decorative images should use `alt=""` with `role="presentation"`.
   - Keep alt text concise (under 125 characters).

2. **Structured Data**: All pages should include appropriate structured data.
   - Use the `PageSeo` component for regular pages.
   - Use the `ArticleSeo` component for blog/article content.
   - Use the `FaqSeo` component for FAQ sections.

3. **Meta Descriptions**:
   - Each page should have a unique meta description.
   - Keep descriptions between 120-155 characters.
   - Make descriptions compelling and include relevant keywords.

4. **Heading Hierarchy**:
   - Each page should have exactly one `<h1>` tag.
   - Headings should follow a logical hierarchy (h1 → h2 → h3, etc.).

5. **Language Support**:
   - All pages should include proper hreflang annotations for Swedish, English, and x-default.
   - Use the `language` prop in page components to set the correct language.

## Report Interpretation

The SEO audit generates a Markdown report in the `reports/` directory with:

1. Summary of issues found
2. Detailed list of issues by category
3. Recommendations for fixing issues

Issues are marked with:

- ✅ No issues found
- ⚠️ Minor issues found (warnings)
- ❌ Critical issues found (errors)

## Troubleshooting

If you encounter issues with the SEO tools:

1. Make sure all dependencies are installed (`npm install`).
2. Check that the scripts directory is executable (`chmod +x scripts/*.js`).
3. For false positives in alt text checking, consider using `role="presentation"` for decorative images.

## Future Improvements

Planned improvements to the SEO tools include:

1. Integration with Google's Rich Results Test API
2. Automated keyword density analysis
3. Content readability scoring
4. Mobile-friendliness checks
5. Schema.org validation during build process
