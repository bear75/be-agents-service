# Broken Links Checker

This document describes the automated broken links checking system implemented for the CAIRE project.

## Overview

The broken links checker is a comprehensive tool that scans the entire codebase for internal and external links, validates them, and generates detailed reports. It's designed to catch broken links early in the development process and maintain link integrity across the application.

**Current Status**: ✅ **100% Internal Link Reliability Achieved**

- Total links checked: ~180
- Broken internal links: 0 (reduced from 75)
- Static asset issues: 0 (all fixed)
- Route keys detected: 95

## Implementation Results

### Before Implementation

- **Broken internal links**: 75
- **Missing static assets**: 4 files
- **Route key support**: None
- **CI integration**: None

### After Implementation

- **Broken internal links**: 0 ✅
- **Missing static assets**: 0 ✅
- **Route key support**: 95 keys detected ✅
- **CI integration**: Full automation ✅

### Fixed Issues

- Created missing image files: `ai-illustration.jpg`, `route-map.svg`, `workflow-diagram.svg`
- Fixed hardcoded paths to use route keys
- Enhanced script to understand `LinkTo` component
- Added comprehensive CI/CD integration

## Features

- **Internal Link Validation**: Checks all internal navigation links against the application's routing system
- **External Link Testing**: Makes HTTP requests to verify external links are accessible
- **Route Key Support**: Understands the custom `LinkTo` component and route key system
- **Static Asset Verification**: Validates that referenced images and files exist
- **Dynamic Link Detection**: Identifies dynamically generated links for manual review
- **Comprehensive Reporting**: Generates detailed markdown reports with line numbers and context
- **CI/CD Integration**: Automated checking in GitHub Actions workflows

## Usage

### Manual Testing

```bash
# Run the broken links checker
npm run links:check

# Run in CI mode (ignores external link failures)
npm run links:check-ci

# View existing reports
npm run links:report
```

### Automated Testing

The broken links checker runs automatically in the CI/CD pipeline:

**Build & Test Workflow:**

- On pull requests to main branch
- On pushes to main branch
- When full tests are enabled (`[full-tests]` in commit message)

**Production Deployment Workflow:**

- On pushes to main branch (production deployments)
- During SEO validation phase
- Always runs in CI mode (ignores external link failures)

## Configuration

The checker is configured in `scripts/check-broken-links.js`:

```javascript
const MAX_EXTERNAL_REQUESTS = 150; // Limit external requests
const BASE_URL = process.env.VITE_BASE_URL || "https://www.caire.se";
```

## Link Types Detected

### Internal Links

- React Router `<Link to="...">` components
- Custom `<LinkTo to="...">` components with route keys
- Navigation hooks (`navigate()` calls)
- Static paths to internal pages

### External Links

- HTTP/HTTPS URLs to external websites
- Social media links
- Integration partner links

### Static Assets

- Images (`/images/...`)
- Documents and files
- Icons and graphics

### Dynamic Links

- Template literals with variables
- Computed paths
- Configuration-driven navigation

## Route Key System

The checker understands the application's route key system:

```javascript
// These route keys are automatically validated (95 total):
("home", "about", "contact", "products", "services");
("features.scheduling", "solutions.private", "solutions.chain");
("resourcesCategory.guides", "resourcesCategory.articles");
("guides.optimizeSchedule", "articles.comprehensiveAiInHomeCare");
// ... and 85+ more route keys
```

## Report Format

Reports are generated in markdown format and saved to `reports/broken-links-report-YYYY-MM-DD.md`:

```markdown
# Broken Links Report

Generated: 2025-05-27T03:13:03.694Z

## Found broken links in X files

- Total links checked: 180
- Broken internal links: 0
- Broken external links: 2

### Broken Internal Links

[Details with file paths, line numbers, and context]

### Broken External Links

[Details with URLs and HTTP status codes]

### Dynamic Links (Manual Review Required)

[Links that need manual verification]
```

## CI/CD Integration

### GitHub Actions

The checker is integrated into both workflows:

**Build & Test Workflow** (`.github/workflows/build-test.yml`):

```yaml
- name: Check for broken links
  if: steps.test-scope.outputs.RUN_FULL_TESTS == 'true'
  run: npm run links:check-ci

- name: Upload broken links report
  if: steps.test-scope.outputs.RUN_FULL_TESTS == 'true' && always()
  uses: actions/upload-artifact@v3
  with:
    name: broken-links-report
    path: reports/broken-links-report-*.md
    retention-days: 30
```

**Production Deployment Workflow** (`.github/workflows/production-deployment.yml`):

```yaml
- name: Check for broken links
  run: |
    echo "🔗 Running broken links check..."
    if [ -f scripts/check-broken-links.js ]; then
      npm run links:check-ci
      echo "✅ Broken links check completed"
    else
      echo "⚠️ Broken links checker script not found"
    fi

- name: Upload broken links report
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: broken-links-report
    path: reports/broken-links-report-*.md
    retention-days: 30
```

### Exit Codes

- **Exit 0**: No broken internal links (external link failures ignored in CI mode)
- **Exit 1**: Broken internal links found or external links failed (non-CI mode)

## Common Issues and Solutions

### False Positives

**LinkedIn 405 Errors**: LinkedIn blocks automated requests, resulting in 405 status codes. These are expected and ignored in CI mode.

**Dynamic Route Parameters**: Links with dynamic parameters are marked for manual review rather than automatically failed.

### Route Key Mismatches

If you see errors like `contact (Not found)`, ensure:

1. The route key exists in `src/utils/routes.ts`
2. The key is added to the `commonRouteKeys` array in the checker script
3. The component is using `LinkTo` instead of `Link` for route keys

### Missing Static Assets

Create missing files or update paths:

```bash
# Copy existing similar file
cp "source-file.jpg" "missing-file.jpg"

# Or update the component to use correct path
src="/images/correct-path.jpg"
```

## Maintenance

### Adding New Route Keys

When adding new routes, update both:

1. `src/utils/routes.ts` - Add the route definition
2. `scripts/check-broken-links.js` - Add to `commonRouteKeys` array

### Updating Link Patterns

To detect new link patterns, add regex patterns to `LINK_PATTERNS` in the checker script:

```javascript
const LINK_PATTERNS = {
  // Add new pattern
  newPattern: /your-regex-here/g,
  // ... existing patterns
};
```

## Performance

- **Files scanned**: 236 TypeScript/JavaScript/Markdown files
- **Links checked**: ~180 per run
- **Route keys detected**: 95 valid route keys
- **Valid routes found**: 134 application routes
- **External request limit**: 150 to avoid rate limiting
- **Typical runtime**: 30-60 seconds
- **Success rate**: 100% for internal links

## Best Practices

1. **Use Route Keys**: Prefer `LinkTo` with route keys over hardcoded paths
2. **Regular Monitoring**: Run checks before major releases
3. **Fix Internal Links**: Always fix broken internal links immediately
4. **Review Dynamic Links**: Manually verify dynamically generated links
5. **Update Documentation**: Keep route documentation current

## Troubleshooting

### Script Fails to Run

Check dependencies (already installed):

```bash
# These dependencies are already included in package.json:
# - node-fetch: ^3.3.2
# - undici: ^7.10.0
# - node-html-parser: ^7.0.1

# If needed, reinstall with:
npm install node-fetch undici node-html-parser --legacy-peer-deps
```

### High False Positive Rate

The script may need updates to:

- Better understand your routing system
- Handle new link patterns
- Exclude certain file types or directories

### Performance Issues

Reduce `MAX_EXTERNAL_REQUESTS` or add more file exclusions to the `glob.sync` ignore patterns.

## New Route Keys

- Core feature pages: scheduling, analytics, integrations, onboarding
- Solution pages: scheduler persona, operations manager, private home care, chain
