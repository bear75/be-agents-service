# NativeWind Compatibility Matrix

**Date:** 2026-02-07  
**Scope:** Caregiver MVP + Phase‑1 gaps

This matrix summarizes how shared UI patterns map to NativeWind in `apps/mobile`.

| UI Pattern / Component      | Status     | Notes                                                            |
| --------------------------- | ---------- | ---------------------------------------------------------------- |
| Typography (Text, Heading)  | ✅ Ready   | Tailwind text classes used in mobile screens.                    |
| Buttons (Primary/Secondary) | ✅ Ready   | Implemented via Pressable + Tailwind classes.                    |
| Cards / Containers          | ✅ Ready   | Rounded containers with `bg-slate-*` used across screens.        |
| Tabs / Segmented Controls   | ✅ Ready   | Implemented in Schedule screen (`Day/Week`).                     |
| Lists / Timeline            | ✅ Ready   | Timeline list uses Tailwind layout utilities.                    |
| Form Inputs                 | ✅ Ready   | TextInput uses Tailwind classes; needs consistent validation UI. |
| Modals / Dialogs            | ⚠️ Partial | No shared modal wrapper yet (use native modal if needed).        |
| Toast / Snackbar            | ❌ Missing | Not implemented; should use a lightweight RN toast library.      |
| Skeleton Loaders            | ❌ Missing | Planned for Phase‑1 schedule UX.                                 |
| Iconography                 | ⚠️ Partial | Native icons not standardized in mobile yet.                     |

## Notes

- The mobile app uses NativeWind 4.x + Tailwind configuration in `apps/mobile/tailwind.config.js`.
- Shared web components in `@appcaire/ui` are not directly reusable; mobile uses RN primitives with Tailwind classes.
