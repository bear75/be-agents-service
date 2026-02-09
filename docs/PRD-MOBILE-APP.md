# PRD: Mobile Caregiver App

**Priority:** 2 (after shared workspace setup)
**Status:** Planning
**Created:** 2026-02-08

---

## 1. Problem Statement

The current AppCaire dashboard (`apps/dashboard/`) is a desktop-only React + Vite web application built with Bryntum SchedulerPro. It serves administrators and coordinators who manage schedules from an office.

**Caregivers in the field have no mobile tool.** They currently rely on printed schedules, phone calls, or checking the desktop dashboard on their phones (poor UX). This causes:

- Missed or late visits due to schedule uncertainty
- No real-time visibility for coordinators on visit status
- No digital check-in/check-out for compliance
- Caregivers can't see route/navigation to next visit
- Schedule changes aren't communicated in real-time

## 2. Decision: Separate Repository

**Why not add to the existing monorepo (`beta-appcaire`)?**

The monorepo is designed for web applications (React + Vite + Tailwind) and backend services (Node.js + Apollo + Prisma). A React Native mobile app has fundamentally different:

- **Build toolchain** — Expo/Metro bundler vs Vite
- **Dependencies** — react-native, expo, native modules vs web-only packages
- **Testing** — Device simulators, TestFlight, Google Play testing vs browser testing
- **Deployment** — App Store + Google Play vs AWS/Vercel
- **CI/CD** — EAS Build / Fastlane vs Docker builds
- **Development workflow** — Physical device testing, hot reload on device

Keeping it in the monorepo would:
- Pollute `yarn.lock` with 500+ native dependencies
- Break `turbo run type-check` (different TS targets)
- Require separate CI/CD pipelines anyway
- Create confusion between web and mobile packages

**Decision:** Create `be-caregiver-app` as a standalone repository.

## 3. Proposed Solution

### 3.1 Repository: `be-caregiver-app`

A standalone Expo (React Native) app that connects to the existing `dashboard-server` GraphQL API.

**Key architecture decision:** The mobile app is a **new client** for the existing backend. No new server needed — it reuses `dashboard-server`'s GraphQL API with Clerk authentication.

```
┌──────────────────────┐     ┌─────────────────────────┐
│  be-caregiver-app    │     │  beta-appcaire           │
│  (new repo)          │────▶│  apps/dashboard-server/  │
│                      │     │  (existing GraphQL API)  │
│  Expo / React Native │     │                          │
│  iOS + Android       │     │  Port 4000               │
└──────────────────────┘     └─────────────────────────┘
         │
         ▼
   Clerk Auth (same org)
```

### 3.2 Core Features (MVP)

| Feature | Description | Priority |
|---------|-------------|----------|
| **My Schedule** | Today's visits with times, client info, address | Must have |
| **Visit Check-in/out** | Tap to record arrival/departure with timestamp | Must have |
| **Client Details** | View client name, address, care notes, contact info | Must have |
| **Navigation** | One-tap directions to next visit (opens Maps) | Must have |
| **Push Notifications** | Schedule changes, new assignments, reminders | Must have |
| **Offline Support** | Cache today's schedule for areas with poor connectivity | Must have |
| **Visit Notes** | Add notes after each visit (text, quick-select options) | Should have |
| **Availability** | Submit preferred hours, time-off requests | Should have |
| **Team Chat** | Simple messaging between caregivers and coordinators | Could have |
| **Document Upload** | Attach photos or documents to visits | Could have |

### 3.3 Tech Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| **Framework** | Expo (React Native) | Cross-platform, OTA updates, managed workflow |
| **Language** | TypeScript | Consistency with backend, type safety |
| **Navigation** | Expo Router (file-based) | Modern, convention-based routing |
| **State** | Apollo Client + React Query | GraphQL + offline cache |
| **Auth** | Clerk Expo SDK | Same auth as dashboard, SSO with org |
| **Push** | Expo Notifications + FCM/APNs | Managed push infrastructure |
| **Maps** | react-native-maps + Linking API | Native map integration + turn-by-turn via system Maps |
| **Offline** | Apollo Cache + AsyncStorage | Persist today's schedule locally |
| **UI** | Tamagui or NativeWind | Tailwind-like styling for React Native |
| **Testing** | Jest + React Native Testing Library | Unit + integration tests |
| **CI/CD** | EAS Build + EAS Submit | Expo's managed build + app store deployment |

## 4. Work Breakdown

### Phase 1: Repository & Infrastructure Setup (Week 1)

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| 1.1 | Create GitHub repo `be-caregiver-app` | S | — |
| 1.2 | Initialize Expo project with TypeScript template | S | 1.1 |
| 1.3 | Set up Clerk Expo SDK + auth flow (login, org select) | M | 1.2 |
| 1.4 | Configure Apollo Client pointing to dashboard-server GraphQL | M | 1.2 |
| 1.5 | Set up EAS Build for iOS + Android | M | 1.2 |
| 1.6 | Create CLAUDE.md with mobile-specific patterns | S | 1.2 |
| 1.7 | Add repo to agent service `config/repos.yaml` | S | 1.1 |
| 1.8 | Set up dev environment docs (simulators, device testing) | S | 1.2 |

### Phase 2: Dashboard-Server API Extensions (Week 1-2)

The mobile app needs some queries/mutations that may not exist yet on the backend:

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| 2.1 | Add `myScheduleToday` query (visits for logged-in caregiver, today) | M | — |
| 2.2 | Add `checkInVisit` mutation (record arrival timestamp + location) | M | — |
| 2.3 | Add `checkOutVisit` mutation (record departure + visit notes) | M | — |
| 2.4 | Add `myUpcomingVisits` query (next 7 days schedule) | S | — |
| 2.5 | Add `updateAvailability` mutation (submit preferred hours) | M | — |
| 2.6 | Add push notification subscription endpoint | L | — |
| 2.7 | Ensure all queries filter by `employeeId` from Clerk token | S | 2.1-2.5 |

*These tasks run in the `beta-appcaire` monorepo, not the mobile app repo.*

### Phase 3: Core Mobile App (Week 2-3)

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| 3.1 | Build login screen (Clerk sign-in, org selection) | M | Phase 1 |
| 3.2 | Build "My Schedule" — today's visit list with times | M | 2.1 |
| 3.3 | Build visit detail screen (client info, address, care notes) | M | 2.1 |
| 3.4 | Build check-in flow (tap to check in, confirm, timestamp) | M | 2.2 |
| 3.5 | Build check-out flow (check out, add notes, rate visit) | M | 2.3 |
| 3.6 | Add navigation button (open Maps with address) | S | 3.3 |
| 3.7 | Build "Upcoming" tab — next 7 days schedule | M | 2.4 |
| 3.8 | Implement offline cache for today's schedule | L | 3.2 |

### Phase 4: Notifications & Polish (Week 3-4)

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| 4.1 | Set up Expo push notifications (FCM + APNs) | L | Phase 1 |
| 4.2 | Push notification for schedule changes | M | 4.1 |
| 4.3 | Push notification for new visit assignment | M | 4.1 |
| 4.4 | Build availability/time-off request screen | M | 2.5 |
| 4.5 | Swedish localization (all UI text) | M | Phase 3 |
| 4.6 | App icon, splash screen, onboarding | S | — |
| 4.7 | TestFlight / Google Play internal testing | M | Phase 3 |
| 4.8 | Performance optimization (list virtualization, image caching) | M | Phase 3 |

### Phase 5: Release (Week 4-5)

| # | Task | Effort | Dependencies |
|---|------|--------|-------------|
| 5.1 | Beta testing with 3-5 caregivers | L | Phase 4 |
| 5.2 | Bug fixes from beta feedback | M-L | 5.1 |
| 5.3 | App Store submission | M | 5.2 |
| 5.4 | Google Play submission | M | 5.2 |
| 5.5 | Coordinator training (how to see check-ins on dashboard) | S | 5.3 |

## 5. Agent Service Integration

Add the new repo to the agent service for nightly automation:

```yaml
# config/repos.yaml
repos:
  be-caregiver-app:
    path: ~/HomeCare/be-caregiver-app
    workspace:
      path: ~/Library/Mobile Documents/com~apple~CloudDocs/AgentWorkspace/be-caregiver-app
      enabled: true
    schedule:
      review: "22:30"
      compound: "23:00"
    priorities_dir: reports/
    logs_dir: logs/
    tasks_dir: tasks/
    enabled: true
    github:
      owner: bear75
      repo: be-caregiver-app
      default_branch: main
```

## 6. Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Caregiver adoption | 80% within 1 month | Active users / total caregivers |
| Visit check-in rate | 95%+ | Check-ins recorded / visits scheduled |
| Schedule visibility | Real-time | Coordinator can see caregiver status live |
| App crash rate | <1% | Expo crash reporting |
| Offline reliability | 100% | Schedule accessible without network |
| Time to next visit | <3 taps | From app open to navigation started |

## 7. Non-Goals (V1)

- ❌ Video calling between caregiver and client
- ❌ Medication tracking or medical records
- ❌ Payroll integration
- ❌ Multi-language beyond Swedish (V2)
- ❌ Wearable (Apple Watch) app
- ❌ Custom route optimization (handled by TimeFold integration, Priority 3)

## 8. Open Questions

1. **Expo vs bare React Native?** — Recommendation: Start with Expo managed workflow. Eject later if native modules needed.
2. **Same Clerk org for mobile?** — Yes, caregivers are employees in the same Clerk organization. Their role determines they see mobile-specific views.
3. **Offline data scope?** — Cache today's visits + client details. Don't cache historical data.
4. **Visit note templates?** — Pre-defined quick-select options (e.g., "client feeling well", "client needed extra support") + free text.

---

*See also: `docs/PRD-TIMEFOLD-INTEGRATION.md` for how route optimization will complement this app in Priority 3.*
