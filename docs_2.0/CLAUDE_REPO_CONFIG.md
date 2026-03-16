# Using repo-local `.claude` directory

By default, Claude Code (CLI) uses `~/.claude` for config and data. To use this repo’s `.claude` instead (e.g. `beta-appcaire/.claude`), point the CLI at the repo root.

## Claude Code CLI

Set **`CLAUDE_CONFIG_DIR`** to the repo’s `.claude` path before running `claude`:

```bash
export CLAUDE_CONFIG_DIR="/Users/bjornevers_MacPro/HomeCare/beta-appcaire/.claude"
claude
```

Or in one line when launching:

```bash
CLAUDE_CONFIG_DIR="$(pwd)/.claude" claude
```

Run that from the repo root (`beta-appcaire`), or use the absolute path as above.

**Optional:** Source the helper script from repo root so the env is set in your shell:

```bash
source scripts/use-repo-claude.sh
claude
```

## Cursor

Cursor resolves paths relative to the **workspace root**:

- **Single folder:** Open **File → Open Folder →** `beta-appcaire`. Then `.claude` is `beta-appcaire/.claude`.
- **Multi-root workspace:** With `appcaire.code-workspace`, each folder has its own root. When the active file or context is under `beta-appcaire`, Cursor uses that folder as the root for that context, so `.claude` there is `beta-appcaire/.claude`.

To guarantee the repo’s `.claude` is used, open **only** the `beta-appcaire` folder in Cursor, or ensure your work is in the beta-appcaire root when using `.claude` paths.

## Ensure the directory exists

```bash
mkdir -p /Users/bjornevers_MacPro/HomeCare/beta-appcaire/.claude
```

The repo’s `.gitignore` includes `.claude/`, so the directory is local-only by default.
