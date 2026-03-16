# CAIRE Mobile Platform PRD

> **Purpose**: Transform the handbook app into a full-featured mobile platform for caregivers and clients, integrated with the CAIRE scheduling system.
> **Audience**: Mobile developers, Backend developers, Product
> **Last Updated**: 2026-02-05

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [User Personas](#2-user-personas)
3. [Feature Requirements by Phase](#3-feature-requirements-by-phase)
4. [Technical Architecture](#4-technical-architecture)
5. [Data Models](#5-data-models)
6. [Multi-Source EVV Integration](#6-multi-source-evv-integration)
7. [Security and Compliance](#7-security-and-compliance)
8. [Success Metrics](#8-success-metrics)
9. [Sprint Breakdown](#9-sprint-breakdown)
10. [Appendix](#10-appendix)

---

## 1. Executive Summary

### Vision

CAIRE's mobile platform extends the scheduling system to the field: caregivers use a modern, Uber-like app for daily work, while clients gain visibility and control over their care schedule. The platform integrates with existing municipal EVV systems (Phoniro, NFC) while providing CAIRE's own GPS/manual check-in as fallback.

### Problem Statement

- Caregivers lack a unified mobile tool for schedules, navigation, check-in, and documentation
- External systems (eCare, Carefox) provide schedules but not integrated field execution
- Municipalities require EVV (Electronic Visit Verification) for reimbursement—Phoniro, NFC, or similar
- Clients have no visibility into who is coming or when
- Documentation burden: 20-30% of visit time spent on manual notes

### Solution Overview

1. **Caregiver App (Priority)**: Schedule viewing, GPS navigation, multi-source check-in (Phoniro/NFC/GPS/Manual), visit instructions, offline support, voice documentation
2. **Client App (Phase 3)**: View schedule, see planned employees, visit descriptions, cancel visits, chat with care team
3. **Integration**: Dashboard-server GraphQL API, handbook content, real-time subscriptions

### Key Technical Decisions

| Decision         | Choice                                      | Rationale                                        |
| ---------------- | ------------------------------------------- | ------------------------------------------------ |
| Mobile framework | React Native + Expo                         | Cross-platform, OTA updates, shared codebase     |
| Offline storage  | WatermelonDB                                | Offline-first, sync, not AsyncStorage            |
| Auth             | Clerk                                       | Consistent with web apps, satellite domains      |
| EVV strategy     | Multi-source (Phoniro > NFC > GPS > Manual) | Municipality-specific, Phoniro official in Nacka |
| Actuals storage  | Extended Visit model                        | No separate VisitExecution table                 |

---

## 2. User Personas

### Caregiver / Field Staff

- Views daily schedule with addresses and times
- Navigates to client locations via GPS
- Checks in/out via Phoniro lock, NFC tag, or CAIRE app (GPS/manual)
- Documents visits via text or voice (speech-to-text)
- Updates availability, reports sick leave, requests shift swaps
- Accesses handbook content offline

### Client (Brukare)

- Views upcoming visits and planned employees
- Sees visit descriptions and care instructions
- Cancels or reschedules visits (with approval flow)
- Chats with assigned caregivers or admins
- Adds notes for care team

### Administrator / Scheduler

- Configures EVV methods per client (Phoniro lock ID, NFC tag)
- Monitors actuals from CAIRE app and imported external systems
- Manages employee availability and shift assignments

---

## 3. Feature Requirements by Phase

### Phase 1: Caregiver MVP (Sprints 0–6)

| Feature           | Description                                               |
| ----------------- | --------------------------------------------------------- |
| My Schedule       | Daily list of visits with client, address, time, duration |
| Visit Details     | Client info, address, instructions, navigation link       |
| GPS Check-in/out  | Geofence verification, manual fallback                    |
| Offline Support   | WatermelonDB sync, cached schedule for 7 days             |
| Visit Execution   | Start/end visit, add notes, deviation reporting           |
| Real-time Updates | Push notifications, GraphQL subscriptions                 |

### Phase 2: Enhanced Employee (Sprints 7–10)

| Feature              | Description                                           |
| -------------------- | ----------------------------------------------------- |
| Self-Service         | Availability updates, shift swap requests, sick leave |
| Voice Documentation  | Speech-to-text (Corti), SOAP notes                    |
| Handbook Integration | Handbook content in app, offline access               |

### Phase 3: Client Portal (Sprints 11–12)

| Feature         | Description                                          |
| --------------- | ---------------------------------------------------- |
| Client MVP      | View schedule, planned employees, visit descriptions |
| Client Advanced | Cancel visits, chat, add notes                       |

### Phase 4: Advanced (Sprint 13+)

| Feature           | Description                                  |
| ----------------- | -------------------------------------------- |
| Team Chat         | See nearby employees, swap visits            |
| AI Insights       | Risk alerts, care plan suggestions           |
| App Store Release | Production deployment, TestFlight/Play Store |

---

## 4. Technical Architecture

### Stack

```
┌─────────────────────────────────────────────────────────────┐
│                    Mobile Apps (React Native + Expo)         │
│  ┌─────────────────┐  ┌─────────────────┐                  │
│  │ Caregiver App   │  │ Client App      │                  │
│  └────────┬────────┘  └────────┬────────┘                  │
│           │                    │                             │
│  ┌────────▼────────────────────▼────────┐                  │
│  │ Apollo Client │ WatermelonDB │ Clerk  │                  │
│  └────────┬──────────────────────────────┘                  │
└───────────┼─────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────┐
│              dashboard-server (GraphQL, port 4000)           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Schedules    │  │ Visits/EVV   │  │ Handbook     │     │
│  │ Employees    │  │ Check-in API │  │ Content      │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
            │
┌───────────▼─────────────────────────────────────────────────┐
│  PostgreSQL │ Phoniro API │ NFC Export │ eCare/Carefox     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **Expo**: EAS Build, OTA updates, config plugins
- **NativeWind**: Tailwind CSS for React Native
- **Apollo Client**: GraphQL, offline cache, subscriptions
- **WatermelonDB**: Local SQLite, sync with server
- **Clerk**: Auth, satellite domains for mobile
- **Expo Notifications**: Push notifications

---

## 5. Data Models

### Extended Visit Model

Extend existing `Visit` in `apps/dashboard-server/schema.prisma`:

```prisma
// ACTUAL EXECUTION DATA (Multi-Source)
actualStartTime       DateTime?
actualEndTime         DateTime?
actualDurationMinutes Int?

checkInTime           DateTime?
checkInSource         CheckInSource?
checkInLatitude       Decimal?   @db.Decimal(10, 7)
checkInLongitude      Decimal?   @db.Decimal(10, 7)
checkInDeviceId       String?
checkInVerified       Boolean    @default(false)

checkOutTime          DateTime?
checkOutSource        CheckInSource?
checkOutLatitude      Decimal?   @db.Decimal(10, 7)
checkOutLongitude     Decimal?   @db.Decimal(10, 7)

actualsImportedAt     DateTime?
actualsImportSource   String?
actualsImportBatchId   String?

deviationMinutes      Int?
deviationReason       String?

visitNotes            VisitNote[]
```

### New Models

**ClientCheckInConfig** – Per-client EVV configuration:

```prisma
model ClientCheckInConfig {
  id              String   @id @default(cuid())
  clientId        String   @unique
  client          Client   @relation(...)

  phoniroEnabled  Boolean  @default(false)
  phoniroLockId   String?
  nfcEnabled      Boolean  @default(false)
  nfcTagId        String?
  gpsEnabled      Boolean  @default(true)
  gpsRadiusMeters Int      @default(100)
}
```

**VisitNote** – Visit documentation:

```prisma
model VisitNote {
  id          String   @id @default(cuid())
  visitId     String
  visit       Visit    @relation(...)
  employeeId  String
  employee    Employee @relation(...)

  content     String   @db.Text
  noteType    NoteType @default(TEXT)
  audioUrl    String?

  createdAt   DateTime @default(now())
  updatedAt   DateTime @updatedAt
}

enum NoteType {
  TEXT
  VOICE_TRANSCRIPT
  SOAP
  DEVIATION
}
```

**DevicePushToken** – Push notification tokens:

```prisma
model DevicePushToken {
  id        String   @id @default(cuid())
  userId    String
  user      User     @relation(...)
  token     String   @unique
  platform  Platform
  isActive  Boolean  @default(true)
}

enum Platform {
  IOS
  ANDROID
}

enum CheckInSource {
  PHONIRO
  NFC
  GPS
  MANUAL
  CAREFOX
  ECARE
  OTHER
}
```

---

## 6. Multi-Source EVV Integration

### Priority Order (per client)

1. **Phoniro** – Smart lock at client door; official record in Nacka
2. **NFC** – Physical tag at client location
3. **GPS** – CAIRE app geofence verification
4. **Manual** – Fallback when no system available

### ClientCheckInConfig

Each client has a config indicating which methods are available. The app checks `ClientCheckInConfig` to determine the expected check-in flow.

### Import Flow

- **CAIRE-captured**: App writes directly to `Visit` (checkInTime, checkInSource, etc.)
- **External import**: Batch job populates `actualsImportedAt`, `actualsImportSource`, `actualsImportBatchId`
- **Dual source**: Support both; external may override for billing

---

## 7. Security and Compliance

- **Auth**: Clerk JWT, organization-scoped
- **Data**: Employee sees only own schedule; client sees only own visits
- **EVV**: Audit trail for check-in source and timestamps
- **GDPR**: Minimal data on device, sync only required fields
- **SoL/HSL**: Deviation reporting for Swedish compliance

---

## 8. Success Metrics

| Metric              | Target                                    |
| ------------------- | ----------------------------------------- |
| Caregiver adoption  | 80% of field staff use app daily          |
| Check-in completion | 95% of visits have verified check-in      |
| Offline reliability | Schedule available 7 days without network |
| Voice documentation | 50% of notes via speech-to-text           |
| Client satisfaction | NPS > 40 for client app                   |

---

## 9. Sprint Breakdown

### Sprint 0: Foundation (2 weeks)

**Goal**: Monorepo ready for React Native, Expo configured.

| Task | Description                                         | Validation                         |
| ---- | --------------------------------------------------- | ---------------------------------- |
| 0.1  | Add `apps/mobile` Expo app to monorepo              | `yarn workspace mobile start` runs |
| 0.2  | Configure NativeWind, Tailwind                      | Styles apply in app                |
| 0.3  | Add shared packages (graphql, ui) as workspace deps | Imports resolve                    |
| 0.4  | EAS Build config for iOS/Android                    | `eas build` succeeds               |
| 0.5  | Document mobile setup in README                     | README exists                      |

### Sprint 1: React Native Core (2 weeks)

**Goal**: App shell, navigation, auth.

| Task | Description                               | Validation                     |
| ---- | ----------------------------------------- | ------------------------------ |
| 1.1  | Bottom tab navigation (Schedule, Profile) | Tabs render                    |
| 1.2  | Clerk React Native SDK integration        | Sign-in/sign-out works         |
| 1.3  | Apollo Client with auth link              | GraphQL requests include token |
| 1.4  | Organization context from Clerk           | User org available             |
| 1.5  | Splash screen, loading states             | UX flows work                  |

### Sprint 2: Schedule Views (2 weeks)

**Goal**: My Schedule screen, visit details.

| Task | Description                                  | Validation         |
| ---- | -------------------------------------------- | ------------------ |
| 2.1  | GraphQL query `mySchedule(employeeId, date)` | Returns visits     |
| 2.2  | My Schedule screen with visit list           | List renders       |
| 2.3  | Visit detail screen (client, address, time)  | Detail renders     |
| 2.4  | Open in Maps / navigation link               | Opens external app |
| 2.5  | Date picker for schedule                     | Can change date    |

### Sprint 3: Backend EVV (2 weeks)

**Goal**: Schema changes, GraphQL API for check-in.

| Task | Description                                                                         | Validation                |
| ---- | ----------------------------------------------------------------------------------- | ------------------------- |
| 3.1  | Prisma migration: extend Visit, add ClientCheckInConfig, VisitNote, DevicePushToken | Migration applies         |
| 3.2  | GraphQL types for EVV fields                                                        | Schema includes new types |
| 3.3  | Mutation `visitCheckIn`, `visitCheckOut`                                            | Mutations work            |
| 3.4  | Query `clientCheckInConfig(clientId)`                                               | Returns config            |
| 3.5  | Resolver tests for check-in                                                         | Tests pass                |

### Sprint 4: GPS Check-in (2 weeks)

**Goal**: GPS check-in/out, geofencing.

| Task | Description                               | Validation               |
| ---- | ----------------------------------------- | ------------------------ |
| 4.1  | Expo Location permission and accuracy     | Location obtained        |
| 4.2  | Geofence check (client coords vs current) | Within radius = verified |
| 4.3  | Check-in button with GPS capture          | Check-in writes coords   |
| 4.4  | Check-out button with GPS capture         | Check-out writes coords  |
| 4.5  | Manual fallback when GPS fails            | Manual check-in works    |

### Sprint 5: Offline (2 weeks)

**Goal**: WatermelonDB, offline sync.

| Task | Description                                   | Validation     |
| ---- | --------------------------------------------- | -------------- |
| 5.1  | WatermelonDB schema (Visit, Client, Employee) | DB initializes |
| 5.2  | Sync adapter: fetch schedule → local DB       | Data persists  |
| 5.3  | Schedule screen reads from WatermelonDB       | Works offline  |
| 5.4  | Sync on app foreground / pull-to-refresh      | Sync triggers  |
| 5.5  | Conflict resolution (server wins)             | No data loss   |

### Sprint 6: Visit Execution (2 weeks)

**Goal**: Visit flow, notes, deviations.

| Task | Description                           | Validation           |
| ---- | ------------------------------------- | -------------------- |
| 6.1  | Start visit / End visit buttons       | Updates visit status |
| 6.2  | Add text note mutation                | Note saved           |
| 6.3  | Deviation report (late, missed, etc.) | Deviation recorded   |
| 6.4  | Visit notes list in detail            | Notes display        |
| 6.5  | Actual duration calculation           | Duration correct     |

### Sprint 7: Real-time (2 weeks)

**Goal**: Push notifications, subscriptions.

| Task | Description                            | Validation         |
| ---- | -------------------------------------- | ------------------ |
| 7.1  | Expo Notifications setup               | Push received      |
| 7.2  | DevicePushToken mutation               | Token stored       |
| 7.3  | GraphQL subscription `scheduleUpdated` | Subscription works |
| 7.4  | Schedule change notification           | User notified      |
| 7.5  | Deep link to affected visit            | Navigation works   |

### Sprint 8: Self-Service (2 weeks)

**Goal**: Availability, shift swaps, sick leave.

| Task | Description                        | Validation          |
| ---- | ---------------------------------- | ------------------- |
| 8.1  | Update availability mutation       | Availability saved  |
| 8.2  | Availability UI (calendar/pattern) | UI works            |
| 8.3  | Shift swap request mutation        | Request created     |
| 8.4  | Sick leave report mutation         | Sick leave recorded |
| 8.5  | Pending requests list              | List displays       |

### Sprint 9: Voice (2 weeks)

**Goal**: Speech-to-text integration.

| Task | Description                                   | Validation      |
| ---- | --------------------------------------------- | --------------- |
| 9.1  | Corti/STT SDK integration                     | Audio → text    |
| 9.2  | Record voice note in visit                    | Recording works |
| 9.3  | Transcribe and save as VisitNote              | Note saved      |
| 9.4  | SOAP structure extraction (if Corti supports) | Structured note |
| 9.5  | Playback of saved voice note                  | Playback works  |

### Sprint 10: Handbook (2 weeks)

**Goal**: Handbook content in app.

| Task | Description                        | Validation               |
| ---- | ---------------------------------- | ------------------------ |
| 10.1 | Handbook GraphQL query from mobile | Content fetched          |
| 10.2 | Handbook tab/screen in app         | Content displays         |
| 10.3 | Offline handbook content           | Works offline            |
| 10.4 | Role-based content filtering       | Correct content per role |
| 10.5 | Search within handbook             | Search works             |

### Sprint 11: Client MVP (2 weeks)

**Goal**: Client app basics.

| Task | Description                      | Validation            |
| ---- | -------------------------------- | --------------------- |
| 11.1 | Client app Expo project          | App runs              |
| 11.2 | Client auth (Clerk, client role) | Client signs in       |
| 11.3 | My Visits query (client-scoped)  | Returns client visits |
| 11.4 | Client schedule view             | Schedule displays     |
| 11.5 | Planned employees per visit      | Employees shown       |

### Sprint 12: Client Advanced (2 weeks)

**Goal**: Client communication features.

| Task | Description                       | Validation        |
| ---- | --------------------------------- | ----------------- |
| 12.1 | Cancel visit request mutation     | Request created   |
| 12.2 | Client–caregiver chat (or note)   | Message saved     |
| 12.3 | Client add note for care team     | Note saved        |
| 12.4 | Visit description display         | Description shown |
| 12.5 | Notification for schedule changes | Client notified   |

### Sprint 13: Release (2 weeks)

**Goal**: App store prep, production.

| Task | Description                           | Validation       |
| ---- | ------------------------------------- | ---------------- |
| 13.1 | App icons, splash, store assets       | Assets ready     |
| 13.2 | TestFlight (iOS) / Internal (Android) | Builds install   |
| 13.3 | Production API URLs, env config       | Config correct   |
| 13.4 | Privacy policy, terms                 | Documents linked |
| 13.5 | Release checklist, runbook            | Docs complete    |

---

## 10. Appendix

### Related Documents

- [SCHEDULING_MASTER_PRD.md](./SCHEDULING_MASTER_PRD.md) – Core scheduling platform
- [Feature-PRD-speech-to-text.md](./Feature-PRD-speech-to-text.md) – Clinical AI layer
- [prd-umbrella.md](./prd-umbrella.md) – Overall product vision

### Sprint Queue for be-agent-service

Sprint priority files are in `reports/mobile-platform/`. Copy a sprint file to `reports/priorities-YYYY-MM-DD.md` to queue it for the nightly agent run.
