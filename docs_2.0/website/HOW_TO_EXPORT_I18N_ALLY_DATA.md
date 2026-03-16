# How to Export i18n Ally Data and Fix Translation Issues

## Current Status

✅ **Progress Made**: We've reduced missing translations from **232 to 146** (86 keys fixed)!

## Method 1: Using Our Automated Export Tool

### 1. Export Current State

```bash
pnpm translations:export-i18n-ally
```

This creates detailed reports in the `reports/` directory:

- `i18n-ally-export-[timestamp].json` - Complete data export
- `i18n-ally-summary-[timestamp].md` - Human-readable summary

### 2. Apply Targeted Fixes

```bash
pnpm translations:fix-exact
```

### 3. Sync Changes

```bash
pnpm translations:sync
```

### 4. Verify Results

```bash
pnpm translations:export-i18n-ally
```

## Method 2: Manual Export from i18n Ally (VSCode)

### Option A: Using Command Palette

1. Open VSCode Command Palette (`Cmd+Shift+P`)
2. Type "i18n Ally: Export"
3. Choose export format (JSON recommended)
4. Save the exported file
5. Share the file with me for analysis

### Option B: Using i18n Ally Panel

1. Open i18n Ally panel in VSCode sidebar
2. Click the "..." menu in the i18n Ally panel
3. Select "Export" or "Generate Report"
4. Choose the format and location
5. Share the exported data

### Option C: Copy Missing Keys List

1. In i18n Ally panel, expand "Missing" section
2. Right-click on the missing keys list
3. Select "Copy" or "Export to file"
4. Paste the data in a message to me

## Method 3: Browser Console Debugging

With debugging enabled (already done), you can:

1. Open your browser to `http://localhost:5173`
2. Open Developer Tools (F12)
3. Check the Console tab for i18n debug messages
4. Look for messages like:
   - `i18next: missingKey`
   - `i18next: key not found`
   - Translation loading errors

## Current Issues Identified

Based on our latest export, the main remaining issues are:

### Top Missing Keys (146 total):

- Various namespace-specific keys
- Some nested structure issues
- Cross-namespace reference problems

## Available Fix Commands

```bash
# Complete workflow
pnpm translations:workflow

# Export current state
pnpm translations:export-i18n-ally

# Apply exact fixes for known issues
pnpm translations:fix-exact

# Comprehensive sync
pnpm translations:comprehensive-sync

# Sync to public directory
pnpm translations:sync

# Validate current state
pnpm translations:validate
```

## Next Steps

1. **Check i18n Ally in VSCode** - It should now show fewer missing translations
2. **Export the current state** using any of the methods above
3. **Share the export data** so I can create targeted fixes for the remaining 146 missing keys
4. **Test the application** to see if the translation issues are resolved in the UI

## Debugging Tips

- **Browser Console**: Look for `i18next` debug messages
- **i18n Ally Panel**: Check the progress indicators (should show improvement)
- **Network Tab**: Verify translation files are loading correctly
- **Application**: Test switching between English and Swedish

The debugging is now enabled, so you should see detailed translation logs in the browser console when you visit your application.
