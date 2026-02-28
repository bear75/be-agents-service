# Deprecated: use .compound-state for state and DB

**Session state and the SQLite database now live in `.compound-state/`.**

- **DB file:** `.compound-state/agent-service.db`
- **Session state:** `.compound-state/session-*/`

Do not use this `data/` directory for new state. It is kept only for backward compatibility; existing `data/agent-service.db` (if any) is no longer read by the server. To migrate, copy `data/agent-service.db` to `.compound-state/agent-service.db` once if needed, then rely on `.compound-state/` only.

See [docs/AGENT_WORKSPACE_STRUCTURE.md](../docs/AGENT_WORKSPACE_STRUCTURE.md) for the canonical layout and read/write contract.
