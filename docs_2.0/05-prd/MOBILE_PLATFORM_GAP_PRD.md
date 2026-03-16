# CAIRE Mobile Platform – Gap PRD (Delta Scope)

**Version:** 1.0  
**Date:** 2026-02-06  
**Owner:** Product + Engineering  
**Purpose:** Close the gaps between the current implementation and the CAIRE Mobile Platform PRD v1.1, with clear priorities and acceptance criteria.

---

## 1) Executive Summary

The CAIRE Mobile Platform codebase contains core caregiver functionality but does **not** fully meet the requirements in the PRD v1.1. This Gap PRD defines **what is missing**, how it will be delivered, and the order of work.

**Primary focus:** Stabilize a **Caregiver MVP** that works in Expo Go with Clerk + Apollo, then deliver remaining Phase 1 items before moving to advanced features.

---

## 2) Goals

### Caregiver MVP (P0)

Deliver a **stable, testable** caregiver experience:

- Clerk login works in Expo Go (device).
- GraphQL calls succeed with Apollo auth.
- Daily schedule loads and is navigable.
- Visit detail works with EVV GPS/manual check‑in/out.
- Notes (text + voice transcript) are saved.
- Offline read cache is functional.
- Push token registration succeeds.

### Phase 1 Completion (P1)

Deliver remaining Phase 1 PRD features:

- Weekly schedule view + timeline.
- EVV multi‑source UI (Phoniro/NFC detection + UX).
- Offline queue + sync status + conflict handling.
- Visit execution enhancements (care plan, tasks, photos).
- Push notifications + subscription updates.

### Phase 2+ (P2)

Advanced features (Corti SOAP/risk, client app, live tracking, etc.) remain **out of scope** until Phase 1 is complete and validated.

---

## 3) Non‑Goals

- Client app live tracking, family sharing, accessibility audit.
- Corti SOAP/risk detection (until STT provider confirmed).
- Phoniro API integration (only deep link and config UI in Phase 1).
- App store release, compliance audits.

---

## 4) Gap Summary (What’s Missing)

| Area                           | Status     | Gap                                                                               |
| ------------------------------ | ---------- | --------------------------------------------------------------------------------- |
| **Clerk + Apollo reliability** | ❌ Missing | Expo Go fails due to Babel/lru-cache mismatch; auth flow not validated on device. |
| **Today view / Quick stats**   | ❌ Missing | No home screen with current/next visit + stats.                                   |
| **Weekly schedule view**       | ❌ Missing | No weekly calendar grid or timeline view.                                         |
| **EVV multi-source**           | ⚠️ Partial | GPS/manual only; no Phoniro deep link or NFC reader.                              |
| **Offline sync queue**         | ❌ Missing | No mutation queue, no sync status, no conflict resolution.                        |
| **Visit execution**            | ⚠️ Partial | No care plan viewer, tasks, photos, deviation alert.                              |
| **Push notifications**         | ⚠️ Partial | Token registration only; no sending + preferences + history.                      |
| **Subscriptions**              | ❌ Missing | No scheduleUpdated/visitAssigned subscription system.                             |
| **Handbook**                   | ⚠️ Partial | Web link only; no in‑app content.                                                 |

---

## 5) Requirements by Workstream

### WS1 — Auth & Connectivity Stability (P0)

**Goal:** User can sign in and use API in Expo Go.

**Requirements**

1. Clerk login works on device using publishable key.
2. Apollo client uses Clerk token (auth header verified).
3. GraphQL URL reachable from device.
4. Clear error UI if API is offline.

**Acceptance Criteria**

- User signs in with Clerk test email.
- `mySchedule` query succeeds.
- No Metro/Babel runtime errors.

---

### WS2 — Schedule & Today View (P1)

**Goal:** Provide daily + weekly views, timeline visualization.

**Requirements**

1. Today view with current/next visit + stats.
2. Weekly view with visit counts per day.
3. Vertical timeline for daily visits.
4. Empty + loading + error states.

**Acceptance Criteria**

- Weekly navigation works.
- Timeline order matches visit times.
- Stats calculated from actual visits.

---

### WS3 — EVV Multi‑Source UX (P1)

**Goal:** Support Phoniro/NFC/GPS/Manual with correct guidance.

**Requirements**

1. Detect EVV method from `ClientCheckInConfig`.
2. Phoniro deep link CTA if enabled.
3. NFC tag read (Android) with matching tag ID.
4. GPS validation with radius from config.
5. Manual reason required if GPS fails.

**Acceptance Criteria**

- UI shows correct method per client.
- Manual check‑in stores reason.
- NFC check‑in passes with valid tag ID.

---

### WS4 — Offline Mode (P1)

**Goal:** Reliable offline workflow.

**Requirements**

1. Offline indicator + sync status.
2. Queue check‑in/out and notes when offline.
3. Sync queue on reconnect with retry.
4. Conflict handling UI.

**Acceptance Criteria**

- Offline check‑in recorded locally and synced later.
- User sees sync status and failure reasons.

---

### WS5 — Visit Execution Enhancements (P1)

**Goal:** Complete visit flow.

**Requirements**

1. Care plan viewer.
2. Task checklist (optional).
3. Photo capture + compression + upload.
4. Deviation alert if late.
5. Emergency contact call.

**Acceptance Criteria**

- Photo upload stored and linked to visit notes.
- Deviation alert appears if >15m late.

---

### WS6 — Push + Subscriptions (P1)

**Goal:** Real‑time updates + notification delivery.

**Requirements**

1. Subscription infrastructure (graphql‑ws + pub/sub).
2. scheduleUpdated + visitAssigned subscriptions.
3. Expo push sender service.
4. Notification preferences + history UI.

**Acceptance Criteria**

- Schedule updates appear within 5s.
- Push notification received for new visit.

---

## 6) Milestones

| Milestone                 | Scope | Exit Criteria                      |
| ------------------------- | ----- | ---------------------------------- |
| **M0 – Stabilize MVP**    | WS1   | Clerk + Apollo verified on device  |
| **M1 – Schedule UX**      | WS2   | Today + Weekly + Timeline done     |
| **M2 – EVV Multi‑Source** | WS3   | Phoniro/NFC/GPS/Manual UX done     |
| **M3 – Offline**          | WS4   | Offline queue + sync status        |
| **M4 – Visit Execution**  | WS5   | Care plan, tasks, photo, deviation |
| **M5 – Real‑Time**        | WS6   | Subscriptions + push delivery      |

---

## 7) Dependencies

- **Clerk** publishable key + allowed origins.
- **Local GraphQL** accessible from device (LAN or dev deployment).
- NFC hardware (Android device required).
- Phoniro deep link schema or official app URL.
- Storage bucket for photo upload (S3/R2).

---

## 8) Risks & Mitigation

| Risk                       | Severity | Mitigation                           |
| -------------------------- | -------- | ------------------------------------ |
| Expo/Babel incompatibility | High     | Pin dependencies + lock node version |
| Offline sync complexity    | High     | Start with read-only + queue small   |
| NFC iOS limitations        | Medium   | Android-only scope + fallback        |
| Phoniro API unknown        | Medium   | Deep-link only in Phase 1            |

---

## 9) Success Metrics

**Caregiver MVP**

- Login success rate >95%
- `mySchedule` load time <3s
- EVV check‑in/out success >95%
- Offline queue sync success >99%

---

## 10) Appendix – Reference Links

- PRD v1.1: `docs/docs_2.0/05-prd/MOBILE_PLATFORM_PRD.md`
- Release checklist: `docs/docs_2.0/05-prd/MOBILE_PLATFORM_RELEASE_CHECKLIST.md`
