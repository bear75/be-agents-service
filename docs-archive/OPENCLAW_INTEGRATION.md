# OpenClaw Integration — How It Connects to the Agent Flow

This document explains how OpenClaw/Telegram connects to the agent service and how to keep everything in sync.

## Architecture

```
Telegram
       ↓
   OpenClaw (chat + LLM)
       ↓
   MCP Bridge (apps/openclaw-bridge)
       ↓
   ├── Workspace files (inbox, priorities, tasks, etc.)
   ├── Agent Service API (http://localhost:3030)
   └── trigger_compound → auto-compound.sh
```

## What Is Connected

### 1. Workspace priorities → Compound workflow

**auto-compound.sh reads workspace first** (lines 128–131):

- If `workspace/priorities.md` exists → uses it
- Else falls back to `reports/` in the repo

So priorities you set via Telegram (via add_to_inbox, or edits you make in workspace) flow into compound **if** they end up in workspace `priorities.md`.

### 2. Trigger compound from chat

When you say **"run compound"**, **"start agents"**, or **"implement priority"**, the MCP tool `trigger_compound` runs `auto-compound.sh` in the background. It will:

1. Read Priority #1 from workspace
2. Create PRD
3. Implement
4. Open PR

### 3. Dashboard / API

The MCP bridge calls **http://localhost:3030** for:

- `get_teams`, `get_agents`
- `get_sessions`
- `get_stats`
- `start_session`
- `track_command`

## Configuration

### OpenClaw config (`~/.openclaw/openclaw.json`)

Ensure the MCP server env includes:

```json
"env": {
  "WORKSPACE_CONFIG": "/path/to/config/repos.yaml",
  "WORKSPACE_REPO": "beta-appcaire",
  "AGENT_API_URL": "http://localhost:3030"
}
```

### Server must be running

The Agent Service must be running on port 3030 for DB-backed tools (teams, sessions, stats, trigger_compound) to work.

## What Is NOT Connected

### LLM usage tracking

- OpenClaw uses its own Anthropic API key.
- Its LLM calls never go through the Agent Service.
- The LLM usage dashboard only shows usage from compound, llm-invoke, etc. — **not** from OpenClaw chat.

There is no way to track OpenClaw chat usage in our system unless OpenClaw adds a webhook/callback.

### Edit priorities from chat

There is no MCP tool to **write** to `priorities.md`. You can:

- Add to inbox → `add_to_inbox`
- Add follow-ups → `add_follow_up`
- Add check-in notes → `add_checkin_notes`
- Process input docs → `process_input_docs` (creates inbox/priorities/tasks from input/)

To change priorities, edit `workspace/priorities.md` directly or drop a doc in `input/` and run `process_input_docs`.

## Sandbox Setup

For an isolated setup (e.g. family member with own workspace, no repo access), see [SANDBOX_SETUP.md](SANDBOX_SETUP.md).

## Quick reference

| Action | How |
|--------|-----|
| Add idea | `add_to_inbox` |
| See priorities | `get_priorities` |
| Run compound | Say "run compound" → `trigger_compound` |
| Process input docs | Say "process input docs" → `process_input_docs` |
| Check status | Say "status" → `get_overview` |
| See sessions | `get_sessions` |
