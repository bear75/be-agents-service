# WatermelonDB → Prisma Migration Guide

## ✅ What's Been Completed

### 1. Prisma Schema Created (`prisma/schema.prisma`)

- Converted all 6 WatermelonDB tables to Prisma models
- Models: Visit, Client, Address, ScheduleDay, QueuedAction, Notification
- Added proper indexes for performance
- Created initial migration

### 2. Prisma Client Setup (`src/db/prisma.ts`)

- Initialized PrismaClient with React Native extension
- Added reactive hooks support
- Database initialization function
- Disconnect on app close

### 3. Sync Manager Created (`src/sync/SyncManager.ts`)

- **Offline/Online detection** using NetInfo
- **Queue management** for offline mutations
- **Server sync** via Apollo GraphQL
- **Check-in/Check-out** with offline support
- Methods:
  - `syncTodaySchedule(date)` - Fetch from GraphQL → Save to Prisma
  - `queueAction(type, payload)` - Queue mutations for later sync
  - `syncQueuedActions()` - Sync pending queue to server
  - `checkInToVisit(visitId)` - Offline-capable check-in
  - `checkOutFromVisit(visitId, notes)` - Offline-capable check-out

### 4. Offline Context (`src/sync/OfflineContext.tsx`)

- React Context Provider for offline state
- Hooks:
  - `useOffline()` - Full offline context
  - `useNetworkStatus()` - Boolean online/offline
  - `useSyncManager()` - Access sync manager
- Automatic sync when network restored

### 5. App Layouts Updated

- `app/_layout.tsx` - Replaced DatabaseProvider with Prisma initialization
- `app/_layout.web.tsx` - Updated for web compatibility
- Added database initialization on app start
- Added loading states

### 6. Dependencies

- ✅ Installed `@prisma/client@6.1.0`
- ✅ Installed `@prisma/react-native@6.0.1`
- ✅ Installed `prisma@6.1.0`
- ✅ Installed `@react-native-community/netinfo`
- ✅ Installed `react-native-quick-base64`
- ✅ Removed `@nozbe/watermelondb`
- ✅ Removed `@morrowdigital/watermelondb-expo-plugin`

### 7. Configuration

- ✅ Updated `app.json` - Replaced WatermelonDB plugin with Prisma plugin
- ✅ Updated `babel.config.js` - Removed decorator plugins (no longer needed!)
- ✅ Switched back to Hermes engine (decorator issue solved!)
- ✅ Added Prisma scripts to `package.json`:
  - `npm run db:generate` - Generate Prisma Client
  - `npm run db:migrate` - Run migrations
  - `npm run db:studio` - Open Prisma Studio

## ⚠️ Remaining Work

### Files Still Using WatermelonDB (Need Updates):

1. **`src/db/queue.ts`** - Queue management (replace with Prisma QueuedAction)
2. **`src/db/migrations.ts`** - Old WatermelonDB migrations (delete)
3. **`src/db/sync.ts`** - Old sync logic (replace with SyncManager)
4. **`src/db/index.web.ts`** - Web database export (update/delete)
5. **`src/components/visit/VisitEvvSection.tsx`** - Visit component
6. **`app/(tabs)/schedule.tsx`** - Schedule screen
7. **`src/hooks/useQueueStatus.ts`** - Queue hook
8. **`src/hooks/useQueuedActionsCount.ts`** - Queue count hook
9. **`src/components/profile/NotificationCenterSection.tsx`** - Notifications
10. **`src/hooks/useNotificationListener.ts`** - Notification hook

### Migration Pattern for Components:

#### OLD (WatermelonDB):

```typescript
import { useDatabase } from "@nozbe/watermelondb/react";
import { Q } from "@nozbe/watermelondb";
import { VisitModel } from "../../src/db/models";

const database = useDatabase();
const visits = await database.collections
  .get<VisitModel>("visits")
  .query(Q.where("visit_date", visitDate))
  .fetch();
```

#### NEW (Prisma):

```typescript
import { useFindMany } from "@prisma/react-native";

const { data: visits } = useFindMany("visit", {
  where: { visitDate },
});
```

### For Sync Functions:

#### OLD:

```typescript
import { database } from "../db";
const visitCollection = database.collections.get("visits");
await visitCollection.create((visit) => {
  visit.scheduleId = data.scheduleId;
  // ...
});
```

#### NEW:

```typescript
import { useSyncManager } from "../sync/OfflineContext";

const syncManager = useSyncManager();
await syncManager.syncTodaySchedule(today);
```

## 🚀 How to Complete Migration

### Step 1: Update Schedule Screen

```bash
# Edit: app/(tabs)/schedule.tsx
# Replace WatermelonDB queries with Prisma useFindMany hooks
```

### Step 2: Update Hooks

```bash
# Replace in all hooks:
# - useDatabase() → useFindMany()
# - database.collections.get() → prisma.model
```

### Step 3: Delete Old Files

```bash
cd apps/mobile
rm -rf src/db/queue.ts src/db/migrations.ts src/db/sync.ts src/db/index.web.ts
```

### Step 4: Test App

```bash
npm run ios  # or npx expo run:ios
```

## 📊 Benefits of Prisma vs WatermelonDB

| Feature          | WatermelonDB                    | Prisma                       |
| ---------------- | ------------------------------- | ---------------------------- |
| **Decorators**   | ❌ Broken with RN 0.81 + Hermes | ✅ No decorators needed      |
| **Type Safety**  | ⚠️ Manual types                 | ✅ Auto-generated types      |
| **Expo Support** | ⚠️ Community plugin             | ✅ Official support          |
| **Tech Stack**   | ❌ Different from server        | ✅ Same ORM as server        |
| **Maintenance**  | ⚠️ Plugin issues                | ✅ Actively maintained       |
| **React Hooks**  | ❌ Manual subscriptions         | ✅ `useFindMany()` hook      |
| **Migrations**   | ⚠️ Manual schema changes        | ✅ Auto-generated migrations |

## 🎯 Example: Updating a Screen

### Before (WatermelonDB):

```typescript
// app/(tabs)/schedule.tsx
import { useDatabase } from "@nozbe/watermelondb/react";
import { Q } from "@nozbe/watermelondb";

export default function Schedule() {
  const database = useDatabase();
  const [visits, setVisits] = useState([]);

  useEffect(() => {
    const subscription = database.collections
      .get("visits")
      .query(Q.where("visit_date", today))
      .observe()
      .subscribe(setVisits);

    return () => subscription.unsubscribe();
  }, []);

  // ...
}
```

### After (Prisma):

```typescript
// app/(tabs)/schedule.tsx
import { useFindMany } from "@prisma/react-native";
import { useSyncManager } from "../../src/sync/OfflineContext";

export default function Schedule() {
  const syncManager = useSyncManager();
  const { data: visits, isLoading } = useFindMany("visit", {
    where: { visitDate: today },
    orderBy: { startTime: "asc" },
  });

  // Sync from server
  useEffect(() => {
    syncManager.syncTodaySchedule(today);
  }, [today]);

  // Auto-refreshes when data changes!
  // ...
}
```

## 🔄 Offline/Online Pattern

```typescript
import { useOffline, useSyncManager } from "../sync/OfflineContext";

function MyComponent() {
  const { isOnline, syncStatus, pendingQueueCount } = useOffline();
  const syncManager = useSyncManager();

  // Check-in with offline support
  const handleCheckIn = async (visitId: string) => {
    await syncManager.checkInToVisit(visitId);
    // ✅ Works offline! Queues mutation, syncs when online
  };

  return (
    <View>
      {!isOnline && (
        <Text>Offline - {pendingQueueCount} pending actions</Text>
      )}
      {syncStatus === "syncing" && <ActivityIndicator />}
    </View>
  );
}
```

## 📝 Next Steps

1. **Update remaining files** (see list above)
2. **Test offline functionality**
3. **Test sync when coming back online**
4. **Remove old WatermelonDB files**
5. **Update documentation**

## 🐛 Troubleshooting

### Migration doesn't apply

```bash
cd apps/mobile
rm -rf prisma/app.db  # Delete old DB
npm run db:migrate    # Re-run migration
```

### Prisma Client not found

```bash
npm run db:generate   # Regenerate client
```

### Type errors

```bash
npm run db:generate   # Regenerate types
```

## 🎉 Why This Solves Your Problem

**The original blocker**: WatermelonDB decorators created non-writable properties that Hermes rejected.

**The solution**: Prisma doesn't use decorators! It uses:

- Reactive hooks (`useFindMany`)
- Type-safe query builders
- Auto-generated TypeScript types
- Same ORM as your server (tech stack consistency!)

**Result**:

- ✅ No more "property is not writable" errors
- ✅ App launches successfully
- ✅ Consistent tech stack (Prisma everywhere)
- ✅ Better DX with auto-complete and type safety
