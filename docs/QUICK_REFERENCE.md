# Quick Reference

Commands, schedules, and one-pager for the agent service.

## Start Commands

```bash
# Dashboard (port 3010)
yarn start          # Build + start
yarn dev            # Dev with hot reload

# Dual-stack runtime (Darwin + Hannes)
yarn stack:boot:install   # Ensure launchd boot services are installed
yarn stack:all            # Restart all gateways + dashboards
yarn stack:darwin         # Restart Darwin gateway + dashboard
yarn stack:hannes         # Restart Hannes gateway + dashboard
yarn stack:status         # Check status of all stacks
yarn stack:status:telegram  # Send status summary to Telegram
```

## Schedules

| Time | Script | Purpose |
|------|--------|---------|
| 10:30 PM | daily-compound-review.sh | Extract learnings, update CLAUDE.md |
| 11:00 PM | auto-compound.sh | Implement priority #1, create PR |

## Manual Triggers

```bash
# Compound workflow
./scripts/compound/auto-compound.sh <repo-name>

# Daily review
./scripts/compound/daily-compound-review.sh <repo-name>

# Check status
./scripts/compound/check-status.sh <repo-name>
```

## Dashboard Structure (port 3010)

Single entry point: http://localhost:3010. Nav (no overlap, one purpose per page):

- **Overview** — Entry point & workspace (quick start when no repo)
- **Run** — Launch automation (Compound; Commit & push all)
- **Work** — Sessions + tasks in one view (click session to expand)
- **Roster** — Configure who (Agents | Teams)
- **Plans** — What to build (PRDs, roadmaps, repo status)
- **Insights** — Observability & gamification (Analytics | Leaderboard)
- **Marketing** — Marketing domain (campaigns, leads)
- **Settings** — Setup & reference (Config | Docs)

## Key Paths

- **Dashboard:** http://localhost:3010
- **Priorities:** Target repo `reports/priorities-YYYY-MM-DD.md`
- **Logs:** Target repo `logs/auto-compound.log`, `logs/compound-review.log`
