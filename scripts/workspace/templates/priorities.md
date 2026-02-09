# Current Priorities

The agent picks Priority #1 each night for implementation.
Edit this file to change what gets built next.

## High Priority

1. **Shared Markdown Workspace Setup** — Set up the Mac mini: initialize workspace on iCloud, install OpenClaw, configure Telegram/WhatsApp bot, load LaunchD plists, test end-to-end messaging flow. See `config/openclaw/README.md`.
2. **Mobile Caregiver App — New Repository** — Create a separate repository for the React Native (or Expo) mobile app for caregivers. The current monorepo dashboard is desktop-only; caregivers need a dedicated mobile app with offline support, real-time schedule sync, visit check-in/check-out, and route navigation. See `docs/PRD-MOBILE-APP.md`.

## Medium Priority

1. **TimeFold Integration — Employee Scheduling + Field Service Routing** — Integrate TimeFold's optimization engine for automated employee shift scheduling and field service route optimization. Combines our current scheduling data with TimeFold's constraint solver for optimal visit assignments and travel routes. Documentation only for now. See `docs/PRD-TIMEFOLD-INTEGRATION.md`.

## Low Priority

1. Dashboard Mission Control UI redesign (see ROADMAP.md)
2. Multi-evaluator review system (Option 3 in ROADMAP.md)
3. Local LLM for simple tasks (pi-mono/ollama)

## Parking Lot

- Multi-language support (beyond Swedish)
- Integration with external calendar services
- Email notification system for schedule changes
- Dark mode for dashboard
