# Clerk Authentication Components

## Overview

This document clarifies which authentication UI components are **standard Clerk components** (same across all apps) vs **custom components** (may differ between apps or need merging from old repo).

---

## ✅ Standard Clerk Components (Same Everywhere)

These components come from `@clerk/clerk-react` and work identically across all apps:

### 1. Sign In / Sign Up Forms

```typescript
import { SignIn, SignUp } from "@clerk/clerk-react";

// Sign In - includes forgot password flow
<SignIn
  routing="path"
  path="/sign-in"
  signUpUrl="/sign-up"
  afterSignInUrl="/dashboard"
/>

// Sign Up - includes email verification
<SignUp
  routing="path"
  path="/sign-up"
  signInUrl="/sign-in"
  afterSignUpUrl="/onboarding"
/>
```

**Features included:**

- ✅ Email/password authentication
- ✅ Social OAuth (Google, GitHub, etc.) - if configured
- ✅ Forgot password flow (built into SignIn)
- ✅ Email verification (built into SignUp)
- ✅ Magic links (if enabled)
- ✅ Multi-factor authentication (if enabled)

**These are the SAME components** - no merging needed.

---

### 2. User Profile & Account Management

```typescript
import { UserButton } from "@clerk/clerk-react";

// Dropdown menu with profile, settings, logout
<UserButton afterSignOutUrl="/" />
```

**Features included:**

- ✅ View profile
- ✅ Edit profile (name, email, password)
- ✅ Account settings
- ✅ Security settings (MFA, sessions)
- ✅ Sign out
- ✅ Organization switching (if user has multiple orgs)

**This is the SAME component** - no merging needed.

---

### 3. Organization Switcher

```typescript
import { OrganizationSwitcher } from "@clerk/clerk-react";

// Dropdown to switch between organizations
<OrganizationSwitcher afterSelectOrganizationUrl="/dashboard" />
```

**Features included:**

- ✅ List all user's organizations
- ✅ Switch active organization
- ✅ Create new organization
- ✅ Invite members (if admin)

**This is the SAME component** - no merging needed.

---

### 4. Full Profile Pages (Modal/Page)

```typescript
import { UserProfile, OrganizationProfile } from "@clerk/clerk-react";

// Full user profile page/modal
<UserProfile routing="path" path="/user-profile" />

// Full organization profile page/modal
<OrganizationProfile routing="path" path="/organization-profile" />
```

**Features included:**

- ✅ Complete profile management
- ✅ All settings in one place
- ✅ Member management (for orgs)
- ✅ Billing (if applicable)

**These are the SAME components** - no merging needed.

---

## 🔧 Custom Components (May Need Merging)

These are custom-built components that wrap Clerk or add custom flows:

### 1. Organization Onboarding Flow

**Location:** `apps/sverigeshemtjanst/src/pages/partner/OrganizationOnboarding.tsx`

**Purpose:** Custom step after sign-up to select/create provider organization

**Status:**

- ✅ Implemented in `sverigeshemtjanst`
- ⏳ **Needs merging** to `dashboard` app from old repo

**What it does:**

- Provider search/autocomplete
- Provider selection
- Create new provider request
- Link Clerk org to SEO DB provider

**Will this be the same?**

- **Logic:** Yes, should be shared
- **UI:** May have app-specific styling
- **Recommendation:** Extract to `@appcaire/shared` or merge from old repo

---

### 2. Auth Layout Wrappers

**Locations:**

- `apps/dashboard/src/components/AuthLayout.tsx`
- `apps/sverigeshemtjanst/src/pages/partner/AuthPage.tsx` (custom layout)

**Purpose:** Custom branding/layout around Clerk components

**Status:**

- ✅ Each app has its own layout
- ⚠️ **May differ** between apps (branding)

**Will this be the same?**

- **No** - each app can have different branding
- Dashboard might use different colors/layout than partner portal

---

### 3. Protected Route Wrappers

**Locations:**

- `apps/dashboard/src/components/ProtectedRoute.tsx`
- `apps/sverigeshemtjanst/src/components/partner/PartnerRoute.tsx`

**Purpose:** Check authentication before rendering routes

**Status:**

- ✅ Each app has its own
- ✅ **Logic is similar** - can be shared

**Will this be the same?**

- **Logic:** Yes, should be shared
- **Recommendation:** Extract to `@appcaire/shared` or use Clerk's built-in `<SignedIn>` component

---

## 📋 Component Checklist

| Component                   | Type                    | Same Everywhere? | Needs Merge? |
| --------------------------- | ----------------------- | ---------------- | ------------ |
| `<SignIn />`                | Clerk                   | ✅ Yes           | ❌ No        |
| `<SignUp />`                | Clerk                   | ✅ Yes           | ❌ No        |
| Forgot Password             | Clerk (in SignIn)       | ✅ Yes           | ❌ No        |
| `<UserButton />`            | Clerk                   | ✅ Yes           | ❌ No        |
| View Profile                | Clerk (in UserButton)   | ✅ Yes           | ❌ No        |
| `<OrganizationSwitcher />`  | Clerk                   | ✅ Yes           | ❌ No        |
| `<UserProfile />`           | Clerk                   | ✅ Yes           | ❌ No        |
| `<OrganizationProfile />`   | Clerk                   | ✅ Yes           | ❌ No        |
| Logout                      | Clerk (via `signOut()`) | ✅ Yes           | ❌ No        |
| **Organization Onboarding** | **Custom**              | ❌ **No**        | ✅ **Yes**   |
| Auth Layout                 | Custom                  | ❌ No            | ⚠️ Maybe     |
| Protected Routes            | Custom                  | ⚠️ Similar       | ⚠️ Maybe     |

---

## 🎯 Answer to Your Question

> "Will all sign up, select org, sign in, forgot pssw, logout, view profile, select org etc, use the same components currently in the old repo?"

### ✅ YES - These use the SAME Clerk components:

- **Sign In** - `<SignIn />` (includes forgot password)
- **Sign Up** - `<SignUp />`
- **View Profile** - Built into `<UserButton />`
- **Select Org** - `<OrganizationSwitcher />` or built into `<UserButton />`
- **Logout** - Built into `<UserButton />` or `signOut()` function

**No merging needed** - these are standard Clerk components.

### ⚠️ MAYBE - These might need merging:

- **Organization Onboarding** (select org after sign-up)
  - Currently in `sverigeshemtjanst`
  - **Needs merging** to `dashboard` from old repo
  - Should be shared component

### ❌ NO - These are app-specific:

- **Auth Layout** (branding/wrapper)
  - Each app can have different styling
  - Dashboard vs Partner portal might look different

---

## 🔄 Recommended Approach

### Option 1: Use Clerk Components Directly (Recommended)

```typescript
// All apps use the same Clerk components
import {
  SignIn,
  SignUp,
  UserButton,
  OrganizationSwitcher
} from "@clerk/clerk-react";

// Only customize appearance, not functionality
<SignIn
  appearance={{
    elements: {
      formButtonPrimary: "bg-blue-600",
    },
  }}
/>
```

### Option 2: Shared Custom Components

If you need custom logic, extract to `@appcaire/shared`:

```typescript
// packages/shared/src/auth/components/OrganizationOnboarding.tsx
export { OrganizationOnboarding } from "./OrganizationOnboarding";

// All apps import from shared
import { OrganizationOnboarding } from "@appcaire/shared/auth";
```

---

## 📚 Clerk Documentation

- [Sign In Component](https://clerk.com/docs/components/authentication/sign-in)
- [Sign Up Component](https://clerk.com/docs/components/authentication/sign-up)
- [User Button](https://clerk.com/docs/components/user/user-button)
- [Organization Switcher](https://clerk.com/docs/components/organizations/organization-switcher)
- [User Profile](https://clerk.com/docs/components/user/user-profile)
- [Organization Profile](https://clerk.com/docs/components/organizations/organization-profile)

---

## Multi-Domain Satellite Configuration

When running Clerk across multiple domains (e.g., sverigeshemtjanst.se, hemtjanstguide.se), satellite mode is used:

### Environment Variables

```env
# Primary domain (dashboard.caire.se)
VITE_CLERK_PUBLISHABLE_KEY=pk_live_...

# Satellite domains (SEO sites)
# VITE_CLERK_DOMAIN = actual satellite domain (e.g. sverigeshemtjanst.se), NOT clerk.sverigeshemtjanst.se
# Sign-in/sign-up MUST point to primary (app.caire.se) – do not render <SignIn />/<SignUp /> on satellites
VITE_CLERK_IS_SATELLITE=true
VITE_CLERK_DOMAIN=sverigeshemtjanst.se
VITE_CLERK_SIGN_IN_URL=https://app.caire.se/sign-in
VITE_CLERK_SIGN_UP_URL=https://app.caire.se/sign-up
```

### ClerkProvider Configuration

```typescript
// apps/sverigeshemtjanst/src/main.tsx
import { ClerkProvider } from "@clerk/clerk-react";
import { getClerkConfig } from "./lib/env";

const clerkConfig = getClerkConfig();

<ClerkProvider
  publishableKey={clerkConfig.publishableKey}
  isSatellite={clerkConfig.isSatellite}
  domain={clerkConfig.domain}
  signInUrl={clerkConfig.signInUrl}
  signUpUrl={clerkConfig.signUpUrl}
>
  <App />
</ClerkProvider>
```

### Localhost Detection

Satellite mode is automatically disabled in development (localhost) for easier testing:

```typescript
// apps/sverigeshemtjanst/src/lib/env.ts
export function getClerkConfig() {
  const isLocalhost =
    typeof window !== "undefined" && window.location.hostname === "localhost";

  return {
    publishableKey: import.meta.env.VITE_CLERK_PUBLISHABLE_KEY,
    isSatellite:
      !isLocalhost && import.meta.env.VITE_CLERK_IS_SATELLITE === "true",
    domain: import.meta.env.VITE_CLERK_DOMAIN,
    signInUrl: import.meta.env.VITE_CLERK_SIGN_IN_URL,
    signUpUrl: import.meta.env.VITE_CLERK_SIGN_UP_URL,
  };
}
```

### SSR-Safe Wrapper

For SSR apps, use the `ClerkProviderSSR` wrapper:

```typescript
// apps/hemtjanstguide/src/lib/components/ClerkProviderSSR.tsx
export function ClerkProviderSSR({ children }) {
  // Safe for SSR - only renders on client
  return (
    <ClerkProvider {...getClerkConfig()}>
      {children}
    </ClerkProvider>
  );
}
```

---

## Key Route Changes

The partner portal routes have been updated:

| Old Route           | New Route             | Component              |
| ------------------- | --------------------- | ---------------------- |
| `/partner`          | `/mittcaire`          | Partner dashboard      |
| `/partner/framgang` | `/mittcaire/framgang` | Gamification dashboard |
| `/partner/auth`     | `/auth`               | Auth page              |

---

## Summary

**Most components are the same** because they're Clerk's standard components. The only component that might need merging is the **custom organization onboarding flow**, which should be shared across apps after merging from the old repo.

**Multi-domain support** is enabled through Clerk's satellite mode, with automatic localhost detection for development.
