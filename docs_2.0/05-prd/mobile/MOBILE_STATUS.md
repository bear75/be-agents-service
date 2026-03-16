# Caire Mobile Platform - Current Status

**Last updated:** 2026-02-11
**Location:** `apps/mobile/` (monorepo), planned: separate `caire-mobile` repo
**Status:** Code complete, pending migration to standalone repo

---

## Current State

### Tech Stack

| Component     | Version  | Notes                                 |
| ------------- | -------- | ------------------------------------- |
| React Native  | 0.81.5   | via Expo SDK 54                       |
| Expo          | ~54.0.0  | Managed workflow                      |
| Expo Router   | ^6.0.23  | File-based routing (`app/` directory) |
| React         | 19.1.0   | Workspace resolution                  |
| Clerk         | ^2.19.22 | `@clerk/clerk-expo`                   |
| Apollo Client | ^3.14.0  | GraphQL with subscriptions            |
| NativeWind    | ^4.1.26  | Tailwind CSS for RN                   |
| TypeScript    | ^5.8.3   | Strict mode                           |

### What Exists (apps/mobile/)

```
apps/mobile/
├── app/                     # Expo Router file-based routes
│   ├── _layout.tsx          # Root layout (Clerk → Apollo providers)
│   ├── _layout.web.tsx      # Web layout variant
│   ├── index.tsx            # Entry redirect
│   ├── sign-in.tsx          # Authentication
│   ├── (tabs)/
│   │   ├── _layout.tsx      # Tab navigator
│   │   ├── schedule.tsx     # Schedule with GraphQL subscriptions
│   │   ├── client.tsx       # Client management
│   │   ├── handbook.tsx     # Employee handbook
│   │   └── profile.tsx      # User settings
│   └── visit/
│       └── [visitId].tsx    # Visit detail (check-in/out, notes, photos)
├── src/
│   ├── components/          # Reusable UI components
│   ├── hooks/               # Domain hooks (location, voice, queue)
│   ├── providers/           # Apollo, notification providers
│   ├── db/                  # Local SQLite via Prisma (offline)
│   └── utils/               # Geofence, network, transcribe, etc.
├── metro.config.js          # Custom resolver for monorepo dedup
├── index.js                 # Expo Router entry point
└── .env.example             # Required environment variables
```

### Backend Support (apps/dashboard-server/)

The backend fully supports the mobile app with:

- **GraphQL queries**: `myProfile`, `mySchedule`, `myScheduleWeek`, `myClientVisits`, `clientForMobile`, `visit`, `clientCheckInConfig`, `myShiftSwapRequests`
- **GraphQL mutations**: `visitCheckIn`, `visitCheckOut`, `createVisitNote`, `registerDevicePushToken`, `updateEmployeeAvailability`, `createShiftSwapRequest`, `reportSickLeave`, `requestVisitCancellation`, `createClientNote`, `updateClientCheckInConfig`
- **GraphQL subscriptions**: `scheduleUpdated`, `visitAssigned`
- **REST endpoints**: `/api/visit-audio` (upload), `/api/visit-photos` (upload), `/api/transcribe`
- **Database migrations**: `add_mobile_self_service`, `add_visit_note_photo`

---

## Monorepo Challenge

React Native + Metro bundler has a fundamental compatibility issue with the monorepo:

- **With custom Metro resolver**: Fixes duplicate deps but Metro's SHA-1 file tracking breaks at scale (4400+ modules)
- **Without custom resolver**: Duplicate singleton packages cause runtime crashes

This is a Metro architectural limitation, not a configuration issue. All known workarounds (nohoist, resolutions, custom resolvers, React 18 downgrade, swapping Expo Router for React Navigation) have been tried and documented.

**The monorepo works great for all 13+ web apps. React Native needs its own space.**

---

## Next Steps: Separate Repository

### Plan

1. Create `caire-mobile` repository
2. Copy `apps/mobile/` to new repo root
3. Copy `@appcaire/graphql` generated types to `src/generated/`
4. Update `package.json` to remove workspace references
5. Standard `yarn install && npx expo start`
6. Set up EAS Build for CI/CD

### What Stays in Monorepo

- Backend (dashboard-server) -- GraphQL API, REST endpoints, migrations
- GraphQL package -- schema, operations, codegen (source of truth)
- Shared packages -- types, utilities

### What Moves to Separate Repo

- All of `apps/mobile/` (screens, components, hooks, providers, utils)
- Metro config
- Expo/RN-specific dependencies

### Sync Strategy

- GraphQL types: copy `packages/graphql/generated/` on schema changes
- Consider a CI job or script to auto-sync types on push to main
- Backend API is consumed via HTTP/WebSocket -- no code sharing needed at runtime

---

## Environment Variables

```bash
# Required (see apps/mobile/.env.example)
EXPO_PUBLIC_GRAPHQL_URL=http://<your-ip>:4000/graphql
EXPO_PUBLIC_WS_GRAPHQL_URL=ws://<your-ip>:4000/graphql
EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
EXPO_PUBLIC_HANDBOOK_WEB_URL=http://localhost:3006
EXPO_PUBLIC_STT_ENDPOINT=http://localhost:8000
```

---

## Development Commands

```bash
# Start Metro bundler
cd apps/mobile
npx expo start --clear

# Launch on iOS simulator
npx expo run:ios --device "iPhone 16 Pro"

# Verify backend is running
curl -s http://<your-ip>:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}' | jq .
```

---

## Key Files (Do Not Modify Without Understanding)

1. `metro.config.js` -- Custom resolver for monorepo duplicate dedup
2. `index.js` -- Expo Router entry point
3. `app/_layout.tsx` -- Provider hierarchy (Clerk → Apollo)

---

## Related Documents

- `docs/docs_2.0/05-prd/MOBILE_PLATFORM_ARCHITECTURE_DECISIONS.md` -- Architecture decisions
- `docs/docs_2.0/05-prd/MOBILE_PLATFORM_RELEASE_CHECKLIST.md` -- Release checklist
- `apps/mobile/README.md` -- App-level README
- `apps/dashboard-server/CLAUDE.md` -- Backend patterns
