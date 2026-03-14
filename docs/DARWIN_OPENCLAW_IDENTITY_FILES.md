# How the OpenClaw/Telegram identity files are used (and why Telegram “remembers nothing”)

The files **AGENTS.md**, **BOOTSTRAP.md**, **HEARTBEAT.md**, **IDENTITY.md**, **SOUL.md**, **TOOLS.md**, **USER.md** (and **MEMORY.md**) in the DARWIN folder are used by **OpenClaw** — the system that runs your Telegram (and other) agents. They are the agent’s **only** persistent “memory” across sessions.

---

## How they’re used

OpenClaw doesn’t store conversation history or “memory of you” in a database. Each time the agent runs (e.g. when you message the Telegram bot), it **starts from scratch** and is told to read these files from the workspace:

| File | When it’s used | What it’s for |
|------|----------------|---------------|
| **AGENTS.md** | Every session | **Instructions for the agent:** “Read SOUL.md, USER.md, memory daily files, MEMORY.md; behave like this; use heartbeats like this.” The agent follows this first. |
| **SOUL.md** | Every session | **Who the agent is:** personality, boundaries, vibe. The agent reads this to know how to act. |
| **USER.md** | Every session | **Who you are:** your name, what to call you, timezone, notes, context. This is the main “memory of you.” If it’s empty, the agent has no idea who you are. |
| **IDENTITY.md** | Every session (optional) | **Agent’s own identity:** name, creature, vibe, emoji, avatar. Filled during first run (bootstrap). |
| **memory/YYYY-MM-DD.md** | Every session | **Recent context:** today + yesterday. Raw daily notes. |
| **MEMORY.md** | Main session only (e.g. direct Telegram chat) | **Long-term curated memory:** decisions, things to remember, lessons. The agent is told to read and update this. If it’s missing or empty, the agent has no long-term memory. |
| **BOOTSTRAP.md** | First run only | **First-time setup:** “Who am I? Who are you?” — then fill IDENTITY.md and USER.md. After that you delete it. |
| **HEARTBEAT.md** | When heartbeat runs | **Periodic checks:** what to do on a heartbeat (e.g. check inbox, calendar). Can be empty to skip. |
| **TOOLS.md** | When needed | **Your local notes:** cameras, SSH, TTS voice, etc. Optional. |

So: **Telegram “remembers” only what’s written in these files.** If USER.md and MEMORY.md are empty or missing, the bot has no memory of you and no long-term memory after a reset.

---

## Why they seem to have “no value” right now

- They are **templates**. IDENTITY.md, USER.md, SOUL.md, TOOLS.md are placeholders: “Name:”, “Timezone:”, “Notes:” with nothing filled in.
- **Nobody has run the bootstrap.** BOOTSTRAP.md is still there; the “who am I / who are you” conversation never happened (or the results weren’t written into USER.md and IDENTITY.md).
- **MEMORY.md was moved** during the DARWIN restructure (into `research/`). The agent is instructed to read `MEMORY.md` at workspace root. If it’s not there, the agent has no long-term memory file to load. It has been restored to the DARWIN root so OpenClaw can find it again.

So the files *are* used — but only if they contain real content. Empty templates = no value and “Telegram remembers nothing.”

---

## What to do so Telegram has a “memory of you”

1. **Fill USER.md** (in DARWIN root). This is the main place for “who you are”:
   - **Name** — Your name.
   - **What to call them** — How the agent should address you (e.g. first name, “you”).
   - **Timezone** — So it can reason about “today”, “tomorrow”, “in 2 hours”.
   - **Notes / Context** — What you care about, what you’re working on, preferences. The more you put here, the more the bot can act like it “knows” you.

2. **Keep MEMORY.md at DARWIN root.** It has been restored there. The agent reads and updates it for long-term memory. Don’t move it back into `research/` if you want Telegram to use it.

3. **Optionally run the bootstrap once:** Open a main session (e.g. direct Telegram chat), let the agent see BOOTSTRAP.md, and do the “who am I / who are you” flow. It will fill IDENTITY.md and USER.md. Then delete BOOTSTRAP.md.

4. **Optionally tune SOUL.md and IDENTITY.md** so the agent’s personality and name match what you want.

5. **HEARTBEAT.md** — Leave empty (or comments only) if you don’t want heartbeat checks; or add a short checklist so the agent knows what to do when it runs a heartbeat.

---

## Summary

| Problem | Cause | Fix |
|--------|--------|-----|
| “No value” in these files | They’re unfilled templates | Fill USER.md (and optionally IDENTITY.md, SOUL.md) with real content. |
| Telegram remembers nothing | Bot has no persistent state except these files; USER.md and MEMORY.md were empty or missing | Fill USER.md; keep MEMORY.md at DARWIN root (restored). Optionally run bootstrap and maintain MEMORY.md. |
| MEMORY.md missing for agent | It was moved to research/ during restructure | MEMORY.md has been copied back to DARWIN root so the agent can read/update it again. |

The “memory” of you and of past context is entirely file-based in the workspace. Update the files, and the next time the agent runs it will read that and behave as if it remembers.
