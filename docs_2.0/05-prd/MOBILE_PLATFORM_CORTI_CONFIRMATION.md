# Corti / Speech‑to‑Text Confirmation (Sprint 0)

**Date:** 2026-02-07  
**Scope:** Caregiver MVP + Phase‑1

## Current Status

- **STT integration in mobile:** Uses a generic STT endpoint configured via `EXPO_PUBLIC_STT_ENDPOINT`.
- **Vendor:** Not finalized; Corti remains the leading candidate but requires confirmation.
- **Feature scope:** MVP includes voice recording + transcript save (no SOAP/risk pipeline yet).

## Phase‑1 Decision

- **Proceed with generic STT endpoint** for MVP voice notes.
- **Defer Corti‑specific integration** (streaming, SOAP, risk indicators) to Phase‑2.

## Dependencies (Phase‑2)

- Vendor contract and data residency confirmation.
- API streaming support (real‑time transcription).
- Structured SOAP output and risk signal schema.
- Compliance review with municipalities and legal.

## References

- `docs/docs_2.0/05-prd/Feature-PRD-speech-to-text.md`
