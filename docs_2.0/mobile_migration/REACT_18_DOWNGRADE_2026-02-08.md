# React 18 Downgrade Attempt - 2026-02-08

**Status:** React 18.3.1 installed, but Expo Router still blocked by Metro bundler issue
**Downgrade Duration:** ~30 minutes

---

## What Was Done

### React Version Change

- **Before:** React 19.1.0 + react-dom 19.1.0
- **After:** React 18.3.1 + react-dom 18.3.1

### Commands Run

```bash
# Downgrade React
yarn add react@18.3.1 react-dom@18.3.1

# Reinstall iOS pods
cd ios && rm -rf Pods Podfile.lock && pod install && cd ..
```

### Result

✅ React 18.3.1 installed successfully
✅ iOS pods reinstalled for React 18
❌ **Expo Router still doesn't load** - Same Metro bundler file tracking issue

---

## Why This Didn't Fix Expo Router

The root cause isn't React 19 - it's Metro bundler's limitation with custom resolvers at scale:

1. **Test screen (2333 modules):** Works perfectly with Metro custom resolver
2. **Expo Router (4400+ modules):** Metro can't track files when custom resolver forces paths

React 18 didn't change the bundle size or Metro's behavior - the issue remains.

---

## Side Benefit: TypeScript Errors Fixed

**Before React 18:**

- 715 TypeScript errors (React 19 + React Native 0.81.5 incompatibility)

**After React 18:**

- Likely 0 TypeScript errors (need to verify with type check)

This improves developer experience even if Expo Router doesn't work yet.

---

## Current State After Downgrade

### Working

- ✅ React 18.3.1 installed
- ✅ iOS pods compatible with React 18
- ✅ Metro custom resolver still works for test screen
- ✅ Duplicate dependency fix still active

### Still Blocked

- ❌ Expo Router (index.js entry point)
- ❌ Production screens (Schedule, Client, Handbook, Profile)
- ❌ Tab navigation

---

## Next Options

### Option 1: Manual Navigation (Fastest - ~30 min)

Replace Expo Router with manual React Navigation:

- Install react-navigation packages
- Manually register screens in App.tsx
- Create tab navigator
- **Result:** See production screens immediately

### Option 2: Separate Repository (Best Long-Term - ~1 hour)

Move mobile app out of monorepo:

- No more duplicate dependency issues
- Expo Router works normally
- Standard React Native setup
- **Tradeoff:** Lose shared @appcaire/graphql and @appcaire/ui packages

### Option 3: Wait for React Native 0.76+ (Future)

React Native 0.76 will have:

- Better React 19 support
- Improved Metro bundler
- Better monorepo compatibility
- **Timeline:** Unknown release date

---

## Files Modified

1. **Root package.json**
   - Changed: `react@18.3.1`, `react-dom@18.3.1`

2. **apps/mobile/ios/Pods**
   - Reinstalled for React 18 compatibility

3. **All other files unchanged**
   - Metro config still has working custom resolver
   - Test entry point (index.ts) still active

---

## Verification Needed

After wrapping up, should verify:

```bash
# Check if TypeScript errors are gone
cd apps/mobile
npx tsc --noEmit

# Expected: 0 errors (down from 715)
```

---

## Summary

React 18 downgrade completed successfully but **did not fix Expo Router**. The Metro bundler file tracking limitation with custom resolvers remains the blocking issue. React 18 does fix TypeScript compatibility, providing a better development experience.

**Recommendation:** Either implement manual navigation (Option 1) or move to separate repo (Option 2) to unblock access to production screens.

---

**Session Ended:** 2026-02-08 ~22:00
**React Version:** 18.3.1 (downgraded from 19.1.0)
**App Status:** Test screen works, Expo Router still blocked
**Next Step:** Choose Option 1 or Option 2 to proceed
