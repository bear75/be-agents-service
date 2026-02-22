# Input — Drop Zone for Docs

Drop markdown (.md) files here: ideas, features, tasks, marketing jobs, PRDs, etc.

**Workflow:**
1. Drop .md files in this folder
2. Run `./scripts/workspace/process-input-docs.sh beta-appcaire` (or use Telegram: "process input docs")
3. Agent extracts ideas → inbox, priorities → priorities.md, tasks → tasks.md
4. Processed docs are moved to `input/read/` (marked handled)

Only .md files are processed. Convert .docx/.xlsx to .md for agent access.
