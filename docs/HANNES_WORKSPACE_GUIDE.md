# Hannes Workspace Guide

A short guide for using your personal workspace bot on Telegram.

---

## What You Have

- **Your workspace:** `hannes-space` in shared iCloud (inbox, priorities, tasks, follow-ups, check-ins)
- **Your assistant:** Telegram (@Appcaire_agent_bot) — same as pappa's setup
- **Access:** iPhone (Telegram, Files app), PC (iCloud for Windows, icloud.com)

Your workspace syncs via iCloud, so you can see and edit your files from any device.

---

## Setup: What You Need to Do

### 1. Telegram (you can do this anytime)

1. Open Telegram (phone or PC)
2. Search for **@userinfobot**
3. Send any message → copy your **numeric user ID** (e.g. `987654321`)
4. Send the ID to pappa
5. Pappa adds it to OpenClaw config and restarts
6. Message **@Appcaire_agent_bot** — Darwin will respond (same bot as pappa, your own workspace)

---

## What You Can Do

| Say in Telegram | What happens |
|-----------------------------|--------------|
| "Add X to inbox" | Adds X to your inbox |
| "What's in my inbox?" | Shows your inbox items |
| "What are my priorities?" | Shows your priorities |
| "Add X as a follow-up" | Adds a follow-up item |
| "Status" / "Overview" | Summary of inbox, priorities, tasks |
| "Create a doc about X" | Creates a markdown doc in input/ |
| "Process my input docs" | Converts input docs to inbox/priorities/tasks |
| "Add notes to today" | Adds notes to today's check-in |
| "Remember X" | Adds X to memory — Darwin remembers across sessions |
| "Run compound" / "Implement" | *(If set up)* Picks Priority #1, creates PR in `hannes-projects` only |
| General questions | Answered from knowledge (loads memory first if relevant) |

---

## Memory: What Darwin Remembers

- **Within a chat:** Yes — remembers the current conversation
- **Across chats:** Yes — via `memory/context.md`, `memory/learnings.md`, `memory/decisions.md`
- **How to add:** Say "remember X", "don't forget X", or "note that X" — or edit the memory files directly
- **Where to put info:** Edit `memory/context.md` with your interests, projects, tech stack, preferences

---

## What You Can't Do

- **Trigger compound on other repos:** Darwin can **only** run compound on `hannes-projects` — never on pappa's repos (beta-appcaire, etc.).
- **See parent's dashboard:** Your actions don't appear there. Your workspace is separate.

---

## Compound: Build Apps with Darwin (optional)

If pappa has set up compound for you, Darwin can create PRs in your repo `hannes-projects` only. Before it works:

1. **Create the repo** (with pappa): `~/HomeCare/hannes-projects`, init git, push to GitHub
2. **Add priorities** in your workspace (`priorities.md`) — compound picks Priority #1
3. Say **"run compound"** or **"implement"** — Darwin creates a PR in your repo

If compound isn't set up yet, the bot is for **planning and ideas** — use it for inbox, priorities, tasks. Code manually on your PC and push via GitHub Desktop or VS Code.

---

## Where Your Files Live

Your workspace is in shared iCloud:

```
AgentWorkspace/hannes-space/
├── inbox.md          ← Ideas, quick captures
├── priorities.md     ← What matters most
├── tasks.md          ← Tracked work
├── follow-ups.md     ← Things to revisit
├── check-ins/        ← Daily/weekly notes
├── input/            ← Drop .md docs here
├── memory/           ← Decisions, learnings, context
└── docs/             ← This guide and setup info
```

- **iPhone:** Files app → iCloud Drive → AgentWorkspace → hannes-space
- **PC:** iCloud for Windows or icloud.com

---

## Tips

- Add ideas quickly with "add X to inbox"
- Say "remember X" to store things long-term — Darwin loads memory at start of chats
- Use "process my input docs" after dropping .md files in input/
- Check "status" or "overview" for a quick summary
- Edit memory/context.md with your interests and preferences for personalized responses
- Ask Darwin "where's my workspace?" or "send me the guide link" — it can share paths and iCloud links
