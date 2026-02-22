    # Hannes Workspace Guide

A short guide for using your personal workspace bot on Telegram/WhatsApp.

---

## What You Have

- **Your workspace:** `hannes-space` in shared iCloud (inbox, priorities, tasks, follow-ups, check-ins)
- **Your bot:** A Telegram bot you'll create (see below)
- **Access:** iPhone (Telegram, Files app), PC (iCloud for Windows, icloud.com)

Your workspace syncs via iCloud, so you can see and edit your files from any device.

---

## Setup: What You Need to Do

### 1. Create Your Telegram Bot

1. Open Telegram (phone or PC)
2. Search for **@BotFather**
3. Send: `/newbot`
4. Give it a name (e.g. "Hannes Workspace Bot")
5. Copy the **bot token** (looks like `123456:ABC-DEF-...`)
6. Search for **@userinfobot**
7. Send any message and copy your **numeric user ID** (e.g. `987654321`)

Send your bot token and user ID to your parent so they can finish the setup.

---

## What You Can Do

| Say to your bot | What happens |
|-----------------|--------------|
| "Add X to inbox" | Adds X to your inbox |
| "What's in my inbox?" | Shows your inbox items |
| "What are my priorities?" | Shows your priorities |
| "Add X as a follow-up" | Adds a follow-up item |
| "Status" / "Overview" | Summary of inbox, priorities, tasks |
| "Create a doc about X" | Creates a markdown doc in input/ |
| "Process my input docs" | Converts input docs to inbox/priorities/tasks |
| "Add notes to today" | Adds notes to today's check-in |
| "Remember X" | Adds X to memory — bot remembers across sessions |
| General questions | Answered from knowledge (loads memory first if relevant) |

---

## Memory: What the Bot Remembers

- **Within a chat:** Yes — remembers the current conversation
- **Across chats:** Yes — via `memory/context.md`, `memory/learnings.md`, `memory/decisions.md`
- **How to add:** Say "remember X", "don't forget X", or "note that X"
- **Where to put info:** Edit `memory/context.md` with interests, projects, preferences

---

## What You Can't Do (Yet)

- **Run compound / build apps:** Your bot can't create PRs or run code agents. It's for planning and ideas.
- **See parent's dashboard:** Your actions don't appear there. Your workspace is separate.

---

## Building Apps with GitHub

Right now the bot is for **planning and ideas** (inbox, priorities, tasks, follow-ups). To actually build apps:

1. Use the bot for planning (ideas, priorities, tasks)
2. Code on your PC in your own GitHub repo
3. Push manually via GitHub Desktop, VS Code, or `git push`

If you later get compound/agent access, you could say things like "implement X" and the agent would create PRs in your repo. That would need extra setup.

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
- Say "remember X" to store things long-term — bot loads memory at start of chats
- Use "process my input docs" after dropping .md files in input/
- Check "status" or "overview" for a quick summary
- Edit memory/context.md with interests and preferences for personalized responses
