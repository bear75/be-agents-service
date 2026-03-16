# Platform Documentation – Multi-Language Support

## Overview

The CAIRE Platform documentation (`/platform/`) supports multiple languages: English (en), Swedish (sv), and Norwegian (no). Additional languages can be added by extending the configuration and running the translation script.

## Supported Languages

| Code | Language | Path            | hreflang |
| ---- | -------- | --------------- | -------- |
| en   | English  | `/platform/en/` | en       |
| sv   | Svenska  | `/platform/sv/` | sv       |
| no   | Norsk    | `/platform/no/` | nb       |

## Architecture

- **Per-language folders**: `apps/dashboard/public/platform/{en,sv,no}/` contain HTML files with the same structure.
- **Common navbar**: `common-navbar.js` detects language from the URL path and renders navigation labels in the current language.
- **Language switcher**: Dropdown in the navbar to switch between available languages (same page, different language).

## Adding a New Language

1. **Update `common-navbar.js`**:
   - Add the language to `LANGUAGES` (code, label, flag, hreflang).
   - Add `navConfig[code]` with all navigation labels translated.

2. **Create the language folder**:

   ```bash
   cp -r apps/dashboard/public/platform/en apps/dashboard/public/platform/XX
   ```

3. **Update internal links and meta**:
   - Replace `/platform/en/` with `/platform/XX/` in all HTML files.
   - Set `lang="xx"` on the `<html>` element.
   - Update canonical and hreflang links.

4. **Run the translation script** (recommended for full translation):

   ```bash
   DEEPL_API_KEY=your_key yarn platform:translate --source en --target XX
   ```

5. **Update sitemap**:
   - Add the new URLs to `sitemap.jsonld` under `hasPart`.
   - Add the language to `inLanguage`.

6. **Add hreflang to existing pages**:
   - Add `<link rel="alternate" href="https://app.caire.se/platform/XX/..." hreflang="xx">` to en/sv/no pages.

## Translation Script

**Location:** `scripts/translate-platform-pages.ts`

**Usage:**

```bash
DEEPL_API_KEY=xxx yarn platform:translate [--source en] [--target no,sv] [--dry-run]
```

- **--source**: Source language (default: en).
- **--target**: Comma-separated target languages (default: no).
- **--dry-run**: Validate paths without translating.

**Requirements:**

- `DEEPL_API_KEY` environment variable (get a key at https://www.deepl.com/pro-api).
- `deepl-node` (installed as root devDependency).

The script:

1. Reads HTML files from the source language folder.
2. Extracts body content.
3. Translates via DeepL API (preserves HTML structure).
4. Updates meta tags, canonical, hreflang, and internal links.
5. Writes to the target language folder.

## File Structure

```
apps/dashboard/public/platform/
├── common-navbar.js      # Language-aware navigation
├── common-footer.js
├── common-analytics.js
├── sitemap.jsonld        # Includes all language URLs
├── en/                   # English
├── sv/                   # Swedish
└── no/                   # Norwegian
```

## Related

- `NAVBAR_README.md` – Navbar implementation details.
- `NAVIGATION.md` – Platform navigation structure.
