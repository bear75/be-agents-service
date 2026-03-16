# Sync Summary - fas1-scope.md

## Changes Made

✅ **Documentation synchronized:**

- `fas1-scope.md` - Source of truth (updated)
- `fas1-scope-printable.html` - Updated to match markdown (removed extra "Visuell referens" sections)
- Fixed HTML entities in markdown (`&amp;` → `&`)

✅ **Sync script updated:**

- Added `fas1-scope.md` to Attendo pilot title map in `.github/scripts/sync-to-confluence.py`
- Enhanced `sync_file()` function to automatically upload images referenced in markdown
- Image `process-flow-diagram.png` will be uploaded automatically

## To Sync to Confluence

### Option 1: Run sync script (recommended)

```bash
cd /Users/bjornevers_MacPro/HomeCare/caire-platform/appcaire

# Set credentials (if not already set)
export CONFLUENCE_USERNAME="your-email@example.com"
export CONFLUENCE_API_TOKEN="your-api-token"

# Run sync (will sync all Attendo pilot docs including fas1-scope.md)
python3 .github/scripts/sync-to-confluence.py
```

### Option 2: Sync only fas1-scope.md

The sync script will automatically:

1. Create/update page: "Attendo - Pilot Data, Process & Optimization Flow (Fas 1)"
2. Upload image: `process-flow-diagram.png` as attachment
3. Place under parent: Attendo Pilot Documentation (ID: 21200897) in CAIREHCDD space

### Confluence Details

- **Space:** CAIREHCDD (Customer Due Diligence)
- **Parent Page:** Attendo Pilot Documentation - Overview (ID: 21200897)
- **Page Title:** Attendo - Pilot Data, Process & Optimization Flow (Fas 1)
- **Image:** process-flow-diagram.png (uploaded as attachment)

## Files Status

- ✅ `fas1-scope.md` - Source of truth, ready to sync
- ✅ `fas1-scope-printable.html` - Matches markdown
- ✅ `process-flow-diagram.png` - Exists and ready to upload
- ✅ Sync script - Updated and ready
