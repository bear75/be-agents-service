# Clerk React Native Verification (Sprint 0)

**Date:** 2026-02-07  
**Scope:** Caregiver MVP (Expo Go)

## Purpose

Verify that Clerk authentication works end‑to‑end in the Expo Go mobile app and that Apollo requests include a valid Bearer token.

## Preconditions

- `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY` configured in `apps/mobile/.env`
- `EXPO_PUBLIC_GRAPHQL_URL` reachable from device
- Dashboard server running with `CLERK_SECRET_KEY`

## Test Account (Test Mode)

- **Email:** `info+clerk_test@caire.com`
- **Verification Code:** `424242`
- **Organization:** `org_2wftsOc26bNWM2VwyBNORC7cOBg`

## Verification Steps

1. Start Expo dev server:

   ```bash
   yarn workspace mobile start
   ```

2. Open the app in Expo Go.
3. Sign in with the test email and verification code.
4. Confirm the Profile screen shows:
   - User name + email
   - Organization name
5. Confirm GraphQL queries work:
   - Schedule loads (`mySchedule`)
   - Visit detail loads (`visit`)
6. Check network requests:
   - Apollo requests include `Authorization: Bearer <token>`

## Expected Outcome

- User is authenticated successfully on device.
- Org membership visible in profile.
- GraphQL queries succeed without 401 errors.

## Notes

- If Apollo requests fail, verify Apollo client is created **inside** the Clerk context (see `apps/mobile/app/_layout.tsx`).
- If token missing in requests, confirm `getToken()` is called in Apollo link and not at module scope.
