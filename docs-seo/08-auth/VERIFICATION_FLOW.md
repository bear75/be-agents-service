# Authentication & Verification Flow

## Overview

This document describes the complete authentication and verification system across all Caire sites. The system uses three connected components:

| System                    | Purpose              | Data Stored                                      |
| ------------------------- | -------------------- | ------------------------------------------------ |
| **Clerk**                 | Authentication & SSO | Users, Organizations, Sessions                   |
| **SEO DB** (stats-server) | Provider Directory   | Provider info, Verification status, Gamification |
| **Caire DB** (server)     | Platform Data        | Sensitive scheduling, patients, employees        |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AUTHENTICATION ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────────┐                                                       │
│   │  FRONTEND SITES │                                                       │
│   ├─────────────────┤                                                       │
│   │ app.caire.se    │──┐                                                    │
│   │ www.caire.se    │  │                                                    │
│   │ sverigeshemtjanst│  │     ┌─────────────┐                               │
│   │ hemtjanstguide  │  ├────►│   CLERK     │                               │
│   │ nackahemtjanst  │  │     │   (Auth)    │                               │
│   │ eirtech.ai      │──┘     └──────┬──────┘                               │
│   └─────────────────┘                │                                      │
│                                      │                                      │
│                        ┌─────────────┴─────────────┐                        │
│                        │                           │                        │
│                        ▼                           ▼                        │
│              ┌─────────────────┐         ┌─────────────────┐               │
│              │    SEO DB       │         │    CAIRE DB     │               │
│              │  (stats-server) │         │    (server)     │               │
│              ├─────────────────┤         ├─────────────────┤               │
│              │ • Provider Dir  │         │ • Scheduling    │               │
│              │ • Verification  │         │ • Patients      │               │
│              │ • Gamification  │         │ • Employees     │               │
│              │ • Public Stats  │         │ • RLS Protected │               │
│              └─────────────────┘         └─────────────────┘               │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Sign-Up & Onboarding Flow

### Complete User Journey

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           SIGN-UP FLOW                                        │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  STEP 1: CLERK SIGN-UP                                                       │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ User visits /partner/sign-up                                           │  │
│  │ → Fills email, password, etc.                                          │  │
│  │ → Clerk creates user account                                           │  │
│  │ → Redirects to /partner/onboarding                                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                              ▼                                               │
│  STEP 2: ORGANIZATION ONBOARDING                                             │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ User searches for their provider (hemtjänstanordnare)                  │  │
│  │ → Autocomplete from SEO DB providers                                   │  │
│  │ → Can search by name or org number                                     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                    ┌─────────┴─────────┐                                     │
│                    ▼                   ▼                                     │
│  ┌─────────────────────────┐  ┌─────────────────────────┐                   │
│  │ PROVIDER FOUND          │  │ PROVIDER NOT FOUND      │                   │
│  │ → Show preview card     │  │ → Show request form     │                   │
│  │ → User confirms         │  │ → User enters details   │                   │
│  │ → Create Clerk org      │  │ → Submit request        │                   │
│  │ → Claim provider        │  │ → Wait for approval     │                   │
│  └───────────┬─────────────┘  └───────────┬─────────────┘                   │
│              │                            │                                  │
│              ▼                            ▼                                  │
│  STEP 3: VERIFICATION                                                        │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Auto-verify if:                                                        │  │
│  │ • Org number matches Clerk org metadata                                │  │
│  │ • Caire Provider ID matches                                            │  │
│  │ • Email domain matches (non-generic)                                   │  │
│  │                                                                        │  │
│  │ Otherwise: Pending → Caire admin reviews                               │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                              │                                               │
│                              ▼                                               │
│  STEP 4: ACCESS GRANTED                                                      │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │ Verified users get:                                                    │  │
│  │ • SEO private data access                                              │  │
│  │ • Gamification features                                                │  │
│  │ • Profile editing                                                      │  │
│  │                                                                        │  │
│  │ For Caire platform access: Separate approval required                  │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Routes (Updated January 2026)

| Route                 | Purpose           | After          | Component       |
| --------------------- | ----------------- | -------------- | --------------- |
| `/auth`               | Clerk auth page   | → `/mittcaire` | `AuthPage.tsx`  |
| `/mittcaire`          | Partner dashboard | -              | `Dashboard.tsx` |
| `/mittcaire/framgang` | Gamification      | -              | `Dashboard.tsx` |

**Note:** Routes have been updated from `/partner` to `/mittcaire` for better Swedish branding.

---

## Key Identifiers

### SEO DB Provider

| Field                 | Description                 | Example       |
| --------------------- | --------------------------- | ------------- |
| `id`                  | Primary key (cuid)          | `clxyz123...` |
| `orgNumber`           | Swedish org number (unique) | `5568949308`  |
| `appcaireProviderId`  | Link to Caire Platform      | `caire-123`   |
| `clerkOrganizationId` | Link to Clerk org           | `org_2abc...` |
| `isClaimedByOrg`      | Whether claimed             | `true/false`  |
| `isVerified`          | Verification status         | `true/false`  |

### Clerk Organization Metadata

```typescript
interface ClerkOrgMetadata {
  // Public metadata (readable by frontend)
  public: {
    orgNumber: string; // Swedish org number
    seoProviderId?: string; // Link to SEO DB Provider.id
    displayName: string;
    logoUrl?: string;
  };
  // Private metadata (server-only)
  private: {
    caireOrganizationId?: string; // Link to Caire DB
    verificationStatus: "pending" | "verified" | "rejected";
    approvalStatus: "pending" | "approved" | "rejected";
  };
}
```

### Caire DB Organization

| Field                 | Description                    |
| --------------------- | ------------------------------ |
| `clerkOrganizationId` | Link to Clerk org              |
| `seoProviderId`       | Link to SEO DB Provider        |
| `isApproved`          | Caire platform access approved |

---

## Verification Methods (Priority Order)

### Method 1: Organization Number (Most Reliable)

```
SEO DB Provider              Clerk Organization
┌──────────────────┐        ┌──────────────────┐
│ orgNumber:       │        │ metadata:        │
│ "5568949308"     │ ═══?═══│ orgNumber:       │
│                  │        │ "5568949308"     │
└──────────────────┘        └──────────────────┘

✅ If match → AUTO-VERIFIED
```

**Why this works:**

- Swedish org numbers are unique per legal entity
- Verified by Bolagsverket
- Cannot be faked or transferred

### Method 2: Caire Platform ID

```
SEO DB Provider              Clerk Organization
┌──────────────────┐        ┌──────────────────┐
│ appcaireProvider │        │ metadata:        │
│ Id: "caire-123"  │ ═══?═══│ appcaireProvider │
│                  │        │ Id: "caire-123"  │
└──────────────────┘        └──────────────────┘

✅ If match → AUTO-VERIFIED
```

**Use case:** Providers already using Caire Platform.

### Method 3: Email Domain

```
SEO DB Provider              Clerk User
┌──────────────────┐        ┌──────────────────┐
│ email:           │        │ email:           │
│ info@curanova.se │ ═══?═══│ anna@curanova.se │
│ (domain match)   │        │ (domain match)   │
└──────────────────┘        └──────────────────┘

✅ If domain matches (not gmail/hotmail/etc) → AUTO-VERIFIED
```

**Ignored domains:** gmail.com, hotmail.com, outlook.com, yahoo.com, icloud.com, live.com

### Method 4: Manual Verification (Fallback)

If no auto-verification succeeds:

1. Claim is marked as "Pending"
2. Caire admin reviews in `/data/admin` → "Förfrågningar" tab
3. Admin approves or rejects
4. User notified (future: email notification)

---

## Two-Tier Access Control

| Tier                 | Verified By         | Grants Access To                     |
| -------------------- | ------------------- | ------------------------------------ |
| **SEO Verification** | Auto or Caire admin | Private provider data, gamification  |
| **Caire Approval**   | Caire admin only    | Scheduling, patients, sensitive data |

```
                    ┌──────────────────────────────┐
                    │        PUBLIC ACCESS         │
                    │  • Provider directory        │
                    │  • Public statistics         │
                    │  • Quality metrics           │
                    └──────────────────────────────┘
                                 │
                                 │ Sign up + Select provider
                                 ▼
                    ┌──────────────────────────────┐
                    │    SEO VERIFIED ACCESS       │
                    │  • Private provider notes    │
                    │  • Gamification features     │
                    │  • Profile editing           │
                    │  • Analytics dashboard       │
                    └──────────────────────────────┘
                                 │
                                 │ Caire admin approval
                                 ▼
                    ┌──────────────────────────────┐
                    │    CAIRE PLATFORM ACCESS     │
                    │  • Scheduling system         │
                    │  • Patient data              │
                    │  • Employee management       │
                    │  • AI optimization           │
                    └──────────────────────────────┘
```

---

## Provider Request Flow

When a user can't find their provider in the database:

```
User fills form:
┌────────────────────────────────────┐
│ • Organisationsnummer *            │
│ • Verksamhetsnamn *                │
│ • Juridiskt namn                   │
│ • Ort                              │
│ • E-post                           │
│ • Telefon                          │
│ • Hemsida                          │
└────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│ System checks:                     │
│ • Org number already exists? ──────┼──► Show existing provider
│ • Pending request exists?   ───────┼──► Show "already pending"
└────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│ ProviderRequest created            │
│ Status: PENDING                    │
└────────────────────────────────────┘
                │
                ▼
┌────────────────────────────────────┐
│ Caire Admin reviews in:            │
│ /data/admin → Förfrågningar tab    │
│                                    │
│ Options:                           │
│ • Approve → Create provider        │
│ • Reject → Provide reason          │
└────────────────────────────────────┘
```

---

## Admin Approval Interface

### Location

`/data/admin` → "Förfrågningar" tab (requires admin access)

### Capabilities

- View all pending provider requests
- See requester email and details
- Approve: Creates provider in SEO DB
- Reject: Requires reason, notifies user (future)

---

## Database Schema

### SEO DB - Provider

```prisma
model Provider {
  id                    String   @id @default(cuid())
  slug                  String   @unique
  orgNumber             String?  @unique
  name                  String

  // Caire Platform link
  appcaireProviderId    String?  @unique

  // Clerk Organization link
  clerkOrganizationId   String?  @unique
  isClaimedByOrg        Boolean  @default(false)
  claimedAt             DateTime?
  claimedByUserId       String?

  // Verification
  organizationAccess    OrganizationAccess[]
}
```

### SEO DB - OrganizationAccess

```prisma
model OrganizationAccess {
  id                  String      @id @default(cuid())
  clerkOrganizationId String
  providerId          String?
  accessLevel         AccessLevel @default(VIEWER)
  isVerified          Boolean     @default(false)
  verifiedAt          DateTime?
  verifiedByUserId    String?

  @@unique([clerkOrganizationId, providerId])
}
```

### SEO DB - ProviderRequest

```prisma
model ProviderRequest {
  id                String        @id @default(cuid())
  orgNumber         String
  name              String
  legalName         String?
  city              String?
  email             String?
  phone             String?
  website           String?
  requesterClerkId  String
  requesterEmail    String
  status            RequestStatus @default(PENDING)
  reviewedAt        DateTime?
  reviewedByUserId  String?
  reviewNotes       String?
  createdProviderId String?

  @@index([status])
}

enum RequestStatus {
  PENDING
  APPROVED
  REJECTED
  DUPLICATE
}
```

### Caire DB - Organization

```prisma
model Organization {
  // ... existing fields ...

  // Clerk integration
  clerkOrganizationId  String?  @unique
  seoProviderId        String?  @unique
  isApproved           Boolean  @default(false)
  approvedAt           DateTime?
  approvedByUserId     String?
}
```

---

## Row-Level Security (Caire DB)

Sensitive data in Caire DB is protected by PostgreSQL RLS:

```sql
-- Set organization context per-request
SELECT set_config('app.current_org_id', 'org-uuid', true);

-- RLS policy example
CREATE POLICY client_org_isolation ON "Client"
  USING ("organizationId" = app_get_current_org_id());
```

### Protected Tables

- Client (patients)
- Employee
- Visit
- Schedule
- Solution
- Problem

---

## Clerk Configuration

### Required Settings

1. **Enable Organizations** in Clerk Dashboard
2. **Multi-domain setup** for all sites (satellite mode):
   - Primary: `app.caire.se`
   - Satellites: `sverigeshemtjanst.se`, `hemtjanstguide.se`, `nackahemtjanst.se`, `eirtech.ai`

### Environment Variables

```env
# All apps
VITE_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...

# Satellite apps (SEO sites)
# VITE_CLERK_DOMAIN = actual satellite domain (e.g. sverigeshemtjanst.se), NOT a subdomain like clerk.sverigeshemtjanst.se
# Sign-in/sign-up MUST point to the primary domain – auth is not allowed on satellite domains
VITE_CLERK_IS_SATELLITE=true
VITE_CLERK_DOMAIN=sverigeshemtjanst.se
VITE_CLERK_SIGN_IN_URL=https://app.caire.se/sign-in
VITE_CLERK_SIGN_UP_URL=https://app.caire.se/sign-up
```

### SSR-Safe ClerkProvider

For SSR apps like hemtjanstguide, use the `ClerkProviderSSR` wrapper:

```typescript
// apps/hemtjanstguide/src/lib/components/ClerkProviderSSR.tsx
export function ClerkProviderSSR({ children }) {
  // Handles SSR hydration safely
  return <ClerkProvider {...getClerkConfig()}>{children}</ClerkProvider>;
}
```

### Localhost Detection

Satellite mode is automatically disabled on localhost for easier development. See `CLERK_COMPONENTS.md` for details.

---

## Troubleshooting

### "Onboarding step not showing after sign-up"

**Possible causes:**

1. Clerk `afterSignUpUrl` not working
2. User already signed up before change was deployed
3. Missing route configuration

**Solutions:**

1. Check `/partner/onboarding` route exists in App.tsx
2. Verify `afterSignUpUrl="/partner/onboarding"` in SignUp component
3. Clear browser cache/cookies
4. Sign up with new email to test fresh flow

### "Auto-verification not working"

**Check:**

1. Is `orgNumber` set in Clerk org metadata?
2. Does it match Provider's `orgNumber` in SEO DB?
3. Formatting differences? (spaces, dashes are stripped)

### "Provider claimed by wrong organization"

**Admin action:**

1. Go to `/data/admin`
2. Find provider in database
3. Clear `clerkOrganizationId` and `isClaimedByOrg`
4. Delete OrganizationAccess entry

---

## Future: Pre-Provisioning Strategy

> ⚠️ **NOT YET IMPLEMENTED** - For future use when sites launch

### Goal

Pre-create Clerk organizations for all providers with valid emails, enabling:

- Marketing campaigns ("Claim your profile")
- Instant onboarding for known providers
- Built-in verification (email ownership = verified)

### Prerequisites

- [ ] Sites launched and stable
- [ ] Email templates A/B tested
- [ ] GDPR compliance reviewed
- [ ] Manual approval to start campaign

### Safety

- No automatic emails until `ENABLE_MARKETING_EMAILS=true`
- All invitations held in queue until manual trigger
- Gradual rollout with analytics

---

## Related Documents

- [Clerk Documentation](https://clerk.com/docs)
- [APP_DOMAIN_MAPPING.md](../01-arkitektur-strategi/APP_DOMAIN_MAPPING.md)
- [Shared Auth Architecture Plan](/.cursor/plans/shared_auth_architecture_a5b611b3.plan.md)
