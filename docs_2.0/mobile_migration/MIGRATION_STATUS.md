# Mobile App Migration Status

## ✅ Completed

### 1. Removed All Prisma Dependencies

- Removed `@prisma/client`, `@prisma/react-native`, `prisma` from package.json
- Removed `react-native-quick-sqlite` (Prisma dependency)
- Removed Prisma plugin from app.json
- Deleted/stubbed Prisma files: prisma.ts, schema.prisma

### 2. Migrated to Apollo Client GraphQL

**Updated Files:**

- `app/(tabs)/schedule.tsx` - Now uses `useMyScheduleQuery` and `useMyScheduleWeekQuery`
- `app/(tabs)/client.tsx` - Already uses `useMyClientVisitsQuery`, removed offline queue
- `app/_layout.tsx` - Simplified, removed Prisma initialization
- `app/_layout.web.tsx` - Removed OfflineContext

**Simplified Hooks:**

- `src/hooks/useQueueStatus.ts` - Returns default values (no offline queue yet)
- `src/hooks/useNotificationListener.ts` - Stub implementation

**Simplified Components:**

- `src/components/profile/NotificationCenterSection.tsx` - Shows "Inga notiser än"
- Visit components - Removed OfflineContext imports

### 3. Environment Configuration

- React downgraded to 18.3.1 for better compatibility
- React Native 0.81.5 (Expo SDK 54)
- React Native New Architecture enabled
- Metro bundler configured for monorepo

### 4. Build Status

- ✅ Native iOS build succeeds with 0 errors
- ✅ Metro bundler loads all code without Prisma errors
- ✅ JavaScript bundle generates successfully

## ❌ Current Blocker

### FormData Polyfill Issue

**Error:** `ReferenceError: Property 'FormData' doesn't exist`

**Root Cause:**
React Native doesn't provide FormData in the global scope. Apollo Client or one of its dependencies tries to access it during module initialization, before polyfills can be loaded.

**Attempted Fixes:**

1. ✗ Added FormData polyfill in \_layout.tsx (too late in load order)
2. ✗ Installed react-native-url-polyfill and form-data packages
3. ✗ Created custom index.js entry point (still loads after Metro initialization)
4. ✗ Multiple clean rebuilds and cache clears

## 🎯 Recommended Solutions

### Option 1: Downgrade to Expo SDK 53 (Most Likely to Work)

Expo SDK 53 is more stable with React 18 and has better polyfill support.

```bash
cd apps/mobile
yarn add expo@~53.0.0 react-native@0.80.0
npx expo prebuild --clean
yarn ios
```

### Option 2: Use EAS Development Build

EAS builds have better polyfill handling than Expo CLI builds.

```bash
npx eas build --profile development --platform ios --local
```

### Option 3: Remove Apollo Client File Upload Support

If file uploads aren't needed, we could potentially configure Apollo to not require FormData.

```typescript
// In Apollo Client setup
const httpLink = createHttpLink({
  uri: graphqlUrl,
  fetchOptions: {
    // Disable multipart/form-data
  },
});
```

### Option 4: Use Expo SDK 54 with React 19

Revert React to 19.1.0 (Expo SDK 54's default) but accept that some libraries may have compatibility issues.

## 📊 Architecture Changes

### Before (with Prisma)

```
User Action → Prisma Query → Local SQLite → UI Update
              ↓
         Sync Manager → GraphQL → Backend
```

### After (Apollo Only)

```
User Action → Apollo GraphQL Query → Backend → UI Update
              ↓
         Apollo InMemoryCache (basic offline support)
```

**Benefits:**

- Simpler architecture (no local database)
- No decorator issues
- Direct connection to backend
- Easier to maintain

**Trade-offs:**

- Less sophisticated offline support
- No local data persistence between app restarts
- Requires network for all operations

## 🔧 Implementation Details

### GraphQL Queries Used

- `useMyScheduleQuery(date)` - Fetch visits for specific day
- `useMyScheduleWeekQuery(startDate)` - Fetch visits for week
- `useMyClientVisitsQuery(date)` - Fetch client's visits
- Subscriptions: `useScheduleUpdatedSubscription`, `useVisitAssignedSubscription`

### Files Modified (19 files)

1. package.json - Dependencies
2. app.json - Removed Prisma plugin, enabled New Architecture
3. app/\_layout.tsx - Removed Prisma initialization
4. app/\_layout.web.tsx - Removed OfflineContext
5. app/(tabs)/schedule.tsx - GraphQL queries
6. app/(tabs)/client.tsx - Removed offline queue
7. src/hooks/useQueueStatus.ts - Simplified
8. src/hooks/useNotificationListener.ts - Simplified
9. src/components/profile/NotificationCenterSection.tsx - Simplified
10. src/components/visit/VisitEvvSection.tsx - Removed OfflineContext
11. src/components/visit/VisitNotesSection.tsx - Removed OfflineContext
12. src/components/visit/VisitPhotoSection.tsx - Removed OfflineContext
13. src/components/visit/VisitTaskChecklist.tsx - Removed OfflineContext
14. metro.config.js - Monorepo configuration (from earlier)
15. babel.config.js - Removed decorator plugins (from earlier)
16. index.js - Created custom entry point with polyfills (doesn't work yet)
    17-19. Prisma files deleted/stubbed

### Files That Still Need Work

- Visit detail screens - Check-in/check-out functionality needs GraphQL mutations
- Offline mutation queue - Not implemented (currently fails when offline)
- Notifications - Not implemented

## 🚀 Next Steps

1. **Choose and implement one of the recommended solutions above**
2. **Test the app launches and displays data**
3. **Implement remaining GraphQL mutations:**
   - `useVisitCheckInMutation`
   - `useVisitCheckOutMutation`
   - Photo upload mutations
   - Task completion mutations
4. **Optional: Implement basic offline queue with AsyncStorage**
5. **Optional: Implement push notifications with GraphQL subscriptions**

## 📝 Notes

- **Total debugging time:** ~2-3 hours
- **Build success rate:** 100% (native builds always succeed)
- **Runtime success rate:** 0% (FormData error prevents app load)
- **Confidence in solutions:** High for Option 1, Medium for Option 2

---

**Last Updated:** 2026-02-08
**Status:** Awaiting decision on solution approach
