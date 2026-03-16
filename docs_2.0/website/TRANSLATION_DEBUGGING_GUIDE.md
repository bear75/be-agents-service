# Translation Debugging & Validation Guide

This guide provides a systematic approach to analyze, debug, and fix translation issues in the Caire React application.

## 🚀 Quick Start

### 1. Install Required VSCode Extensions

**Primary Recommendation: i18n Ally**

```bash
code --install-extension Lokalise.i18n-ally
```

**Alternative: Sherlock (inlang)**

```bash
code --install-extension inlang.vs-code-extension
```

### 2. Run Translation Validation

```bash
# Validate all translations
pnpm translations:validate

# Check for missing translations
pnpm translations:check

# Fix missing translations
pnpm translations:fix
```

## 🔍 Systematic Analysis Approach

### Step 1: Automated Validation

Run the comprehensive validation script:

```bash
pnpm translations:validate
```

This script will:

- ✅ Scan all React components for translation usage
- ✅ Check for missing translation keys
- ✅ Identify unused translation keys
- ✅ Validate namespace usage consistency
- ✅ Detect hardcoded strings that should be translated

### Step 2: Visual Inspection with i18n Ally

With i18n Ally installed, you'll see:

1. **Inline Annotations**: Translation values displayed directly in your code
2. **Hover Support**: Edit translations by hovering over keys
3. **Missing Key Indicators**: Red underlines for missing translations
4. **Extract Suggestions**: One-click extraction of hardcoded strings

### Step 3: Manual Code Review

Look for these common issues:

#### ❌ Incorrect Namespace Syntax

```tsx
// WRONG: Using colon syntax when namespace is already specified
const { t } = useTranslation(["calculator"]);
return <h1>{t("calculator:title")}</h1>; // ❌

// CORRECT: Use dot notation when namespace is specified
const { t } = useTranslation(["calculator"]);
return <h1>{t("calculator.title")}</h1>; // ✅
```

#### ❌ Missing Namespace Specification

```tsx
// WRONG: Not specifying namespace for page-specific translations
const { t } = useTranslation(); // Defaults to 'common'
return <h1>{t("calculator.title")}</h1>; // ❌ Won't find calculator namespace

// CORRECT: Specify the namespace
const { t } = useTranslation(["calculator", "common"]);
return <h1>{t("calculator.title")}</h1>; // ✅
```

#### ❌ Hardcoded Strings

```tsx
// WRONG: Hardcoded text
return <button>Start Calculating</button>; // ❌

// CORRECT: Use translations
const { t } = useTranslation(["calculator"]);
return <button>{t("calculator.cta.start", "Start Calculating")}</button>; // ✅
```

## 🛠️ Best Practices

### 1. Namespace Usage

**Always specify namespaces explicitly:**

```tsx
// ✅ GOOD: Explicit namespace specification
const { t } = useTranslation(["calculator", "common"]);

// ✅ GOOD: Multiple namespaces for complex components
const { t: tCalc } = useTranslation("calculator");
const { t: tCommon } = useTranslation("common");
```

### 2. Translation Key Structure

**Use consistent dot notation:**

```tsx
// ✅ GOOD: Consistent structure
t("calculator.benefits.efficiency.title");
t("calculator.benefits.efficiency.description");
t("calculator.cta.start");
t("calculator.cta.contact");
```

### 3. Fallback Values

**Always provide fallback values:**

```tsx
// ✅ GOOD: With fallback
t("calculator.title", "Calculate your savings potential");

// ❌ AVOID: No fallback
t("calculator.title");
```

### 4. Cross-namespace References

**Use explicit namespace syntax for cross-namespace references:**

```tsx
const { t } = useTranslation(["calculator", "common"]);

// ✅ GOOD: Explicit namespace for shared content
const homeLink = t("common:nav.home", "Home");
const calculatorTitle = t("calculator.title", "Calculator");
```

## 🔧 Fixing Common Issues

### Issue 1: Mixed Languages on Same Page

**Problem**: English text appearing on Swedish pages or vice versa.

**Solution**:

1. Check namespace specification in `useTranslation()`
2. Verify translation keys exist in both language files
3. Ensure correct key syntax (dot vs colon notation)

```tsx
// Before (problematic)
const { t } = useTranslation(); // Defaults to 'common'
return <h1>{t("calculator:title")}</h1>; // Wrong syntax

// After (fixed)
const { t } = useTranslation(["calculator"]);
return <h1>{t("calculator.title", "Default Title")}</h1>;
```

### Issue 2: Missing Translation Keys

**Problem**: Keys showing as raw strings instead of translated text.

**Solution**:

1. Run `pnpm translations:validate` to identify missing keys
2. Add missing keys to both `en` and `sv` translation files
3. Ensure key structure matches exactly

### Issue 3: Namespace Conflicts

**Problem**: Components using wrong namespace or multiple conflicting namespaces.

**Solution**:

1. Consolidate related translations into appropriate namespaces
2. Use explicit namespace specification
3. Follow the namespace hierarchy:
   - `common`: Shared UI elements (buttons, navigation, etc.)
   - `calculator`: Calculator-specific content
   - `features`: Feature descriptions
   - `products`: Product information
   - etc.

## 📊 Validation Commands

### Available Scripts

```bash
# Full validation suite
pnpm translations:validate

# Check for missing translations
pnpm translations:check

# Automatically fix missing translations
pnpm translations:fix

# Sync translation files
pnpm translations:sync

# Run i18n compliance tests
pnpm test:i18n
```

### Validation Output

The validation script provides:

- **Error Count**: Critical issues that break functionality
- **Warning Count**: Best practice violations and potential issues
- **Namespace Usage**: Overview of translation file sizes
- **Missing Keys**: Specific keys that need to be added
- **Unused Keys**: Keys that can potentially be removed
- **Hardcoded Strings**: Text that should be translated

## 🎯 VSCode Integration

### i18n Ally Features

With the extension installed, you get:

1. **Inline Annotations**: See translation values directly in code
2. **Hover Editing**: Edit translations without opening JSON files
3. **Auto-completion**: Intelligent key suggestions
4. **Missing Key Detection**: Visual indicators for missing translations
5. **Extract Tool**: Convert hardcoded strings to translation keys
6. **Review System**: Collaborative translation review

### Extension Settings

The project includes optimized VSCode settings in `.vscode/settings.json`:

- Configured for React + i18next
- Proper file associations
- Optimized search and suggestion settings
- JSON formatting rules

## 🚨 Troubleshooting

### Common Error Messages

**"Missing namespace: calculator"**

- Add the namespace to your `useTranslation()` call
- Ensure the namespace file exists in both `en` and `sv` directories

**"Missing key 'title' in calculator.en.json"**

- Add the missing key to the translation file
- Check for typos in the key name

**"Unused translation key: calculator:old.feature"**

- Remove unused keys or verify they're actually used
- Check for different key syntax (colon vs dot notation)

### Debug Mode

Enable debug mode in your i18n configuration:

```typescript
// src/i18n.ts
i18n.init({
  debug: true, // Enable in development
  // ... other options
});
```

This will log translation loading and key resolution to the browser console.

## 📈 Monitoring & Maintenance

### Regular Checks

1. **Weekly**: Run `pnpm translations:validate` before releases
2. **After new features**: Check for hardcoded strings
3. **Before translations**: Validate key structure consistency
4. **After translations**: Verify all languages have complete coverage

### Automation

Consider adding translation validation to your CI/CD pipeline:

```yaml
# .github/workflows/translations.yml
- name: Validate Translations
  run: pnpm translations:validate
```

## 🎉 Success Metrics

Your translations are properly implemented when:

- ✅ `pnpm translations:validate` passes without errors
- ✅ All pages display correctly in both languages
- ✅ No hardcoded strings in user-facing components
- ✅ Consistent namespace usage across components
- ✅ i18n Ally shows no missing key warnings

---

## 📚 Additional Resources

- [i18next Documentation](https://www.i18next.com/)
- [react-i18next Documentation](https://react.i18next.com/)
- [i18n Ally Extension](https://marketplace.visualstudio.com/items?itemName=Lokalise.i18n-ally)
- [Translation Best Practices](./i18n-best-practices.md)

For questions or issues, refer to the project's translation documentation or create an issue in the repository.
