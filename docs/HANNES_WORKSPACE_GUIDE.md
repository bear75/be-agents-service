    # Hannes Workspace Guide

A short guide for using your personal workspace bot on Telegram/WhatsApp.

---

## What You Have

- **Your workspace:** `hannes-space` in shared iCloud (inbox, priorities, tasks, follow-ups, check-ins)
- **Your assistant:** Use **"Message yourself"** in WhatsApp on your phone (+46721588444) — same as pappa does with his number
- **Access:** iPhone (WhatsApp, Files app), PC (iCloud for Windows, icloud.com)

Your workspace syncs via iCloud, so you can see and edit your files from any device. You use **"Message yourself"** in WhatsApp to reach Darwin — just like pappa does with his number.

---

## First-Time Setup: Link Your WhatsApp

**Parent runs once (when Hannes is here):**
```bash
openclaw channels login --channel whatsapp --account hannes
```
Hannes scans the QR code with his phone. After that, Hannes uses "Message yourself" in WhatsApp to talk to Darwin.

---

## What You Can Do

| Say in WhatsApp | What happens |
|-----------------|--------------|
| "Add X to inbox" | Adds X to your inbox |
| "What's in my inbox?" | Shows your inbox items |
| "What are my priorities?" | Shows your priorities |
| "Add X as a follow-up" | Adds a follow-up item |
| "Status" / "Overview" | Summary of inbox, priorities, tasks |
| "Create a doc about X" | Creates a markdown doc in input/ |
| "Process my input docs" | Converts input docs to inbox/priorities/tasks |
| "Add notes to today" | Adds notes to today's check-in |
| "Remember X" | Adds X to memory — Darwin remembers across sessions |
| "Run compound" / "Implement" | Triggers compound: picks Priority #1, creates PR in your repo `hannes-projects` (only your own repo) |
| General questions | Answered from knowledge (loads memory first if relevant) |

---

## Memory: What Darwin Remembers

- **Within a chat:** Yes — remembers the current conversation
- **Across chats:** Yes — via `memory/context.md`, `memory/learnings.md`, `memory/decisions.md`
- **How to add:** Say "remember X", "don't forget X", or "note that X"
- **Where to put info:** Edit `memory/context.md` with interests, projects, preferences

---

## What You Can't Do

- **Trigger compound on other repos:** Darwin can **only** run compound on `hannes-projects` — never on parent's repos (beta-appcaire, etc.).
- **See parent's dashboard:** Your actions don't appear there. Your workspace is separate.

---

## Compound: Build Apps with Darwin

Darwin can run compound **only** on your repo `hannes-projects`. Before it works:

1. **Create the repo** (with parent): `~/HomeCare/hannes-projects`, init git, push to GitHub
2. **Add priorities** in your workspace (`priorities.md`) — compound picks Priority #1
3. Say **"run compound"** or **"implement"** — Darwin creates a PR in your repo

You can still code manually on your PC and push via GitHub Desktop or VS Code.

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
└── memory/           ← Decisions, learnings, context
```

- **iPhone:** Files app → iCloud Drive → AgentWorkspace → hannes-space
- **PC:** iCloud for Windows or icloud.com

---

## Tips

- Add ideas quickly with "add X to inbox"
- Say "remember X" to store things long-term — Darwin loads memory at start of chats
- Use "process my input docs" after dropping .md files in input/
- Check "status" or "overview" for a quick summary
- Edit memory/context.md with interests and preferences for personalized responses
