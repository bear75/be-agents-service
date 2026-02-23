# Mac Mini Branch Recovery

**Context:** A local branch on the Mac Mini has full configuration (Telegram, WhatsApp, Claude API, GitHub, shared folder) that was not pushed before losing access.

---

## When You Get Access

1. **SSH or physically access the Mac Mini**
2. **Check current branch:**
   ```bash
   cd ~/HomeCare/be-agents-service  # or your actual path
   git status
   git branch
   ```
3. **Create backup branch and push:**
   ```bash
   git checkout -b backup-mac-mini-config-$(date +%Y%m%d)
   git add -A
   git status  # Review what's being committed
   git commit -m "chore: backup Mac Mini config (Telegram, WhatsApp, Claude, GitHub, shared folder)"
   git push origin backup-mac-mini-config-$(date +%Y%m%d)
   ```
4. **Merge to main if desired:**
   ```bash
   git checkout main
   git pull origin main
   git merge backup-mac-mini-config-YYYYMMDD
   # Resolve conflicts if any
   git push origin main
   ```

---

## What to Preserve

- `config/repos.yaml` — repo paths, workspace paths
- `config/openclaw/` — Telegram/WhatsApp bot config
- `.env` or `~/.config/caire/env` — API keys (Claude, GitHub)
- Any plist or launchd config changes
- Shared folder path configuration

---

## Prevention

- **Push frequently** when working on config
- **Use a `config-backup` branch** for experimental setups
- **Document env vars** in `docs/setup/` (without secrets)
