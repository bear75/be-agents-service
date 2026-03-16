# Mobile Platform Release Checklist

## Pre-release

- [ ] Confirm `EXPO_PUBLIC_GRAPHQL_URL`, `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY`, and `EXPO_PUBLIC_HANDBOOK_WEB_URL` are set for production.
- [ ] Update `apps/mobile/app.json` version, iOS buildNumber, and Android versionCode.
- [ ] Verify `eas.json` profiles (development/preview/production).
- [ ] Ensure privacy policy URL is correct.

## Build & Submit

- [ ] Run `eas build --profile production --platform ios`.
- [ ] Run `eas build --profile production --platform android`.
- [ ] Submit to TestFlight and Google Play Internal Testing.

## Post-build Validation

- [ ] Install builds on physical devices.
- [ ] Validate login, schedule, EVV flows, offline sync, and voice notes.
- [ ] Verify push notifications and deep links.

## Launch

- [ ] Publish release notes.
- [ ] Monitor crash reports and analytics.
