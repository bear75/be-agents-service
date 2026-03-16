# Phoniro Integration Research (Sprint 0)

**Date:** 2026-02-07  
**Scope:** Caregiver MVP + Phase‑1

## Current Findings

- **Official record:** Phoniro is the official EVV/billing record for municipalities such as Nacka.
- **Available integration (current):** Deep‑link to Phoniro app for door access and check‑in/out.
- **API integration:** Not confirmed yet; requires municipality partnership and Phoniro API access.

## Decision (Phase‑1)

- **Implement deep‑link only** in the caregiver app:
  - Show CTA if `phoniroEnabled = true` in ClientCheckInConfig.
  - Open `phoniro://` (or lock‑specific scheme if provided).
  - If app not installed, show guidance.

## Future Work

- Confirm Phoniro API availability, authentication, and data format.
- Evaluate importing actuals from Phoniro to CAIRE unified actuals layer.
- Validate legal/compliance requirements with municipalities.
