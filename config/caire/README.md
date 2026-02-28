# Caire env (API keys)

**The env file is not in this repo.** It lives in your home directory so secrets are never committed.

- **Template in repo:** `config/caire/env.example`
- **Real file (create it):** `~/.config/caire/env`

**Who uses what:** Telegram uses `TELEGRAM_BOT_TOKEN` (often in OpenClaw/plist), not `ANTHROPIC_API_KEY`. Compound jobs (auto-compound, PRD, orchestrator) use the Claude CLI and need `ANTHROPIC_API_KEY` — replace the placeholder with your key from console.anthropic.com or those jobs will fail with "Not logged in".

## Setup

```bash
mkdir -p ~/.config/caire
cp config/caire/env.example ~/.config/caire/env
chmod 600 ~/.config/caire/env
nano ~/.config/caire/env   # replace placeholders with your real keys
```

Used by: compound jobs (Claude CLI), job-executor, auto-compound.sh. See `CLAUDE.md` → Environment Setup.
