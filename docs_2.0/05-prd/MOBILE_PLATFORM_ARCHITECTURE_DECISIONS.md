# Mobile Platform Architecture Decisions

**Date:** 2026-02-07  
**Scope:** Caregiver MVP + Phase‑1 gaps  
**Owner:** Engineering

## Summary

This document captures the architecture decisions for the CAIRE mobile platform in Sprint 0.

## Decisions

### 1) Framework & App Location

- **Decision:** Expo managed workflow with React Native + Expo Router.
- **Reason:** Faster iteration, OTA updates, and shared tooling across iOS/Android.
- **Location:** `apps/mobile` in the monorepo (aligned with existing apps/ packages structure).

### 2) Authentication

- **Decision:** Clerk React Native SDK (`@clerk/clerk-expo`) with token cache via SecureStore.
- **Reason:** Matches the rest of the platform and provides org-aware authentication.

### 3) Data Access

- **Decision:** Apollo Client inside Clerk context; no wrapper hooks.
- **Reason:** Ensures auth tokens are available and keeps data layer consistent with web apps.

### 4) EVV Strategy

- **Decision:** Multi‑source EVV with explicit source hierarchy:
  1. Phoniro (official municipal billing)
  2. NFC
  3. GPS
  4. Manual (fallback)
- **Reason:** Supports municipalities with official systems while enabling CAIRE as unified actuals layer.

### 5) Offline‑First Strategy

- **Decision:** WatermelonDB for local caching + queued mutations for offline actions.
- **Reason:** Reliable in low‑connectivity environments and supports eventual sync.

### 6) Push Notifications

- **Decision:** Expo Notifications for device token registration; server‑side push sender added in Phase‑1.
- **Reason:** Expo push API handles APNs/FCM complexity with minimal operational overhead.

## Implications

- Requires Expo Go/EAS builds for device testing.
- Requires explicit EVV configuration per client (ClientCheckInConfig).
- Requires backend validation for GPS radius and manual reasons.

## Follow‑ups

- Implement push sender + subscriptions (Phase‑1).
- Validate Phoniro deep‑link scheme with municipality partners.
