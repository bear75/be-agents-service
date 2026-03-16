# Mobile App Quick Start

**Last updated:** 2026-02-11
**Entry point:** `index.js` (Expo Router)

---

## Prerequisites

- Node.js 20+
- Yarn 1.22+
- Expo CLI (`npx expo`)
- iOS Simulator or physical device
- Backend running (`apps/dashboard-server`)

---

## Setup

```bash
# 1. Install dependencies (from monorepo root)
yarn install

# 2. Copy env file
cp apps/mobile/.env.example apps/mobile/.env
# Edit .env with your local IP and Clerk key

# 3. Verify backend
curl -s http://<your-ip>:4000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query":"{ __typename }"}' | jq .
# Should return: {"data":{"__typename":"Query"}}
```

---

## Run

```bash
cd apps/mobile

# Start Metro bundler (clear cache)
npx expo start --clear

# Launch on iOS
npx expo run:ios --device "iPhone 16 Pro"
```

---

## Environment Variables

Create `apps/mobile/.env` from `.env.example`:

```bash
EXPO_PUBLIC_GRAPHQL_URL=http://192.168.x.x:4000/graphql
EXPO_PUBLIC_WS_GRAPHQL_URL=ws://192.168.x.x:4000/graphql
EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_test_...
EXPO_PUBLIC_HANDBOOK_WEB_URL=http://localhost:3006
EXPO_PUBLIC_STT_ENDPOINT=http://localhost:8000
```

Use your machine's local network IP (not `localhost`) so the device/simulator can reach the backend.

---

## Architecture

```
Entry: index.js → expo-router/entry
Routes: app/ (file-based routing)
  ├── _layout.tsx       → ClerkProvider → ApolloProvider → Slot
  ├── sign-in.tsx       → Clerk sign-in
  ├── (tabs)/
  │   ├── schedule.tsx  → Daily/weekly schedule with GraphQL subscriptions
  │   ├── client.tsx    → Client management
  │   ├── handbook.tsx  → Employee handbook (WebView)
  │   └── profile.tsx   → User settings
  └── visit/
      └── [visitId].tsx → Visit detail (check-in/out, notes, photos, voice)
```

---

## Troubleshooting

### Port 8081 already in use

```bash
lsof -ti:8081 | xargs kill -9
```

### Cannot find module @appcaire/graphql

```bash
cd ../.. && yarn install && cd apps/mobile
```

### Metro cache issues

```bash
npx expo start --clear
rm -rf node_modules/.cache
```

### iOS build fails

```bash
cd ios && rm -rf Pods && pod install && cd ..
```

---

## Known Limitation

The mobile app has a monorepo compatibility issue with Metro bundler (custom resolver breaks at scale). The plan is to move `apps/mobile/` to a standalone `caire-mobile` repository. See `MOBILE_STATUS.md` for details.
