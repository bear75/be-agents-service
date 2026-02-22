# LLM Routing — Ollama vs Claude

When the agent orchestrator runs compound workflows, it routes tasks to either:

- **Ollama** (local, free) — for simple, high-volume, or token-heavy tasks
- **Claude** (paid API) — for complex reasoning, code implementation, and creative work

## Routing Rules

| Task Type | Use | Why |
|-----------|-----|-----|
| **analyze** | Ollama | Short text analysis, JSON extraction, priority picking. Low creativity needed. |
| **convert** | Ollama | PRD→JSON, format conversion. Structured extraction. |
| **triage** | Ollama | Inbox categorization, checkbox updates. Simple classification. |
| **prd** | Claude | Long-form creative documents. Needs architecture understanding. |
| **implement** | Claude | Code changes, debugging, testing. Requires code context. |
| **review** | Claude | Learning extraction, CLAUDE.md updates. Needs thread comprehension. |

## When Uncertain

**If you're not sure which model to use, ask the user.**

Options:

1. **Interactive**: Run with `llm-invoke.sh uncertain "…"` — prompts on stdin
2. **Telegram**: If OpenClaw/Telegram configured, notify and wait for reply
3. **Default**: When running headless (launchd), default to **Claude** — safer for correctness

## Scripts That Use LLM Routing

- `scripts/compound/analyze-report.sh` → analyze (Ollama)
- `scripts/compound/auto-compound.sh` → prd, implement (Claude)
- `scripts/workspace/process-inbox.sh` → triage (Ollama)
- `scripts/compound/daily-compound-review.sh` → review (Claude)

## Configuration

- `OLLAMA_MODEL` — Local model name (default: `phi`)
- Ollama must be running: `brew services start ollama`
- Model must be pulled: `ollama pull phi`

## Fallback

If Ollama is unavailable (not installed, model missing), scripts automatically fall back to Claude.
