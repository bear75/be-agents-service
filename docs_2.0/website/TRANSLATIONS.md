# Translations Setup

This document explains how translations work in the Caire application.

## Structure

The application uses a simple, maintainable approach for translations:

- All translation files are maintained in **`src/locales/`**
- The build process copies these files to **`public/locales/`** for runtime access
- We use **i18next** with **react-i18next** for internationalization

## Supported Languages

Currently, the application supports:

- English (en)
- Swedish (sv)

## Scripts

We use three main scripts to manage translations:

### `translations:sync`

Copies translation files from `src/locales/` to `public/locales/`.

```bash
pnpm translations:sync
```

This script is automatically run before `dev` and `build` commands, so you typically don't need to run it manually.

### `translations:check`

Checks for missing or inconsistent translations between languages.

```bash
pnpm translations:check
```

Use this to find keys that need to be translated.

### `translations:fix`

Automatically adds missing translation keys from English to Swedish with a prefix to indicate they need translation.

```bash
pnpm translations:fix
```

This script:

1. Identifies keys that exist in English but are missing in Swedish
2. Adds them to the Swedish files with the prefix `[NEEDS TRANSLATION]`
3. **Will not overwrite existing translations** unless they have the prefix
4. Provides a count of added and skipped keys

To force update all placeholder translations (ones with the prefix), use:

```bash
node scripts/fix-missing-translations.js --force
```

## Translation Organization

Translations are split into different namespaces (files) for better organization:

- **common.json**: Shared translations used across the site
- **navigation.json**: Menu items and navigation elements
- **features.json**: Feature-related content
- etc.

Each key should only exist in one namespace to avoid duplication.

### Best Practices for Namespaces

- **Use a single namespace for each major feature or page.**
  - For example, all calculator-related translations should be in `calculator.json` only.
  - Do not mix feature-specific keys into `common.json`.
- **Do not duplicate keys across namespaces.**
  - If a key is used in multiple places, put it in `common.json`.
- **Always specify the namespace in your code.**
  - Use `useTranslation('calculator')` for calculator pages/components.
  - Avoid using multiple namespaces in a single component unless absolutely necessary.
- **Keep key structure hierarchical and consistent.**
  - Use nested objects for related keys (e.g., `card1.title`, `card1.description`).
- **When refactoring or creating new features, start with a clean namespace.**
  - Copy only the keys you need for that feature/page.
  - This avoids legacy key bloat and confusion.

## Development Workflow

1. Add or edit translation files in `src/locales/<language>/<namespace>.json`
2. Run `pnpm translations:check` to ensure all translations are consistent
3. Run `pnpm dev` to start the development server (translations will be automatically synchronized)

## Adding a New Translation Key

1. Add the key to the appropriate English translation file in `src/locales/en/`
2. Either add the Swedish translation manually or run `pnpm translations:fix` to add a placeholder
3. Run `pnpm translations:sync` to copy the files to the public directory
4. Use the key in your code: `t('namespace:key')`

Example:

```tsx
import { useTranslation } from "react-i18next";

function MyComponent() {
  const { t } = useTranslation("features");
  return <h1>{t("title")}</h1>;
}
```

## Adding a New Language

1. Create a new directory in `src/locales/` for the language code (e.g., `de` for German)
2. Copy all files from `src/locales/en/` to the new directory
3. Translate the content in the new files
4. Add the language to the supported languages list in `src/i18n.ts`
5. Run `pnpm translations:sync` to copy the files to the public directory

## Best Practices

1. **Namespaces**: Use separate namespaces (files) for logical sections of the application. For feature pages, use a single dedicated namespace (e.g., `calculator.json`).
2. **No Duplication**: Never duplicate keys across namespaces. If a key is needed in multiple places, put it in `common.json`.
3. **Nesting**: Use nested objects for organizing related translations (e.g., `card1.title`, `card1.description`).
4. **Variables**: Use `{{variable}}` syntax for dynamic content.
5. **Consistency**: Keep key naming and structure consistent across languages and namespaces.
6. **Completeness**: Ensure all keys exist in all language files. Use `translations:check` to verify.
7. **Explicit Namespace Usage**: Always specify the namespace in `useTranslation`. Avoid using multiple namespaces in a single component unless necessary.
8. **Refactor with Care**: When refactoring, start with a clean namespace for the feature/page and only add the keys you need.
9. **No Mixing**: Do not mix feature-specific keys into `common.json` or vice versa.
10. **Review and Test**: After changes, always run the app and check for missing translation warnings in the console.

## Troubleshooting

### Common Issues

#### Translations Not Working on Initial Load

If translations don't work until you reload the page:

1. Make sure React Suspense is properly set up in `main.tsx`
2. Check that `initImmediate: false` is set in `i18n.ts` configuration
3. Ensure all namespaces are properly declared in the `namespaces` array
4. Verify that `preload: ['en', 'sv']` is set in the i18n configuration

#### Missing Translations

If you see missing translation keys in the console:

1. Run `pnpm translations:check` to identify missing keys
2. Add the missing keys to the appropriate language files
3. Make sure the namespaces are properly loaded and included in the `namespaces` array

#### Force Loading Translations

For components that need to ensure specific namespaces are loaded, use the `ForceTranslationReload` component:

```jsx
import { ForceTranslationReload } from "@/components/ForceTranslationReload";

function MyComponent() {
  return (
    <ForceTranslationReload namespaces={["namespace1", "namespace2"]}>
      {/* Your component content */}
    </ForceTranslationReload>
  );
}
```

#### Browser Cache Issues

If you've updated translations but don't see changes:

1. Clear browser cache and localStorage
2. Run `pnpm translations:sync` to ensure files are copied correctly
3. Restart the development server
4. Try a hard refresh (Ctrl+F5 or Cmd+Shift+R)

#### Nested Keys Not Working

If nested keys like `parent.child` aren't working:

1. Make sure you're using the correct syntax: `t('namespace:parent.child')`
2. Check that the object structure is identical in all language files
3. Verify the namespace is loaded using `await i18n.loadNamespaces(['namespace'])`

### Advanced Debugging

For advanced debugging:

1. Set `debug: true` in the i18n configuration
2. Use the browser console to inspect the i18next instance: `window.i18next`
3. Check resource loading with `window.i18next.getResourceBundle('en', 'common')`
4. Use the `i18n_debug` utility in development: `window.__i18n_debug.checkKey('myKey', 'myNamespace')`

## Implementation Details

The application uses:

1. **React Suspense**: For proper loading states
2. **i18next-http-backend**: For dynamic loading of translation files
3. **i18next-browser-languagedetector**: For automatic language detection
4. **Automatic preloading**: Critical namespaces are preloaded on initialization

Translation files are automatically copied from `src/locales/` to `public/locales/` during the build process, ensuring they are available for the HTTP backend to load at runtime.
