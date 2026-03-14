# Darwin workspace scripts

Scripts that enforce and maintain the **DARWIN** shared workspace structure per [docs/DARWIN_STRUCTURE.md](../../docs/DARWIN_STRUCTURE.md). Layout uses **my/** (your files) and **machine/** (agent output).

| Script | Purpose |
|--------|---------|
| **validate-structure.sh** | Check workspace matches canonical layout (my/ + machine/); exit 1 if violations. |
| **archive-completed.sh** | Move completed inbox items to `machine/archive/inbox-archive-YYYY-MM.md`; move duplicate check-in filenames to `machine/archive/check-ins-duplicates/`. |
| **ensure-structure.sh** | Create missing dirs (my/, machine/, subdirs) and template files in my/ (idempotent; does not overwrite). |
| **memory-to-structured.js** | Parse `my/memory/*.md` → write `my/memory/*.json` (machine-readable). |
| **house-clean.sh** | Run validate → archive → ensure → memory-to-json. Use `--migrate` once to move a flat workspace into my/ and machine/. |
| **summarize-archive-to-memory.js** | One-time: read all `.md` in `archive/notes/` and `research/`, write a summary into `memory/context.md`, and append restructure notes to `memory/decisions.md` and `memory/learnings.md`. Run on your machine where DARWIN is on disk. |

**Darwin manager agent** (runs validate, archive-completed, ensure-structure, memory-to-structured):

```bash
./agents/darwin-manager.sh [workspace-path]
```

**House-clean** (full pipeline + optional one-time migration):

```bash
./scripts/darwin/house-clean.sh [workspace-path]           # validate, archive, ensure, memory-to-json
./scripts/darwin/house-clean.sh [workspace-path] --migrate # same + move root files into my/ and machine/
```

Default workspace path is resolved from `config/repos.yaml` (key `darwin`). Set `DARWIN_WORKSPACE_PATH` to override.

**Summarize archive into memory** (after restructure moved 48+ files out of memory/):

```bash
node scripts/darwin/summarize-archive-to-memory.js [workspace-path]
```

This adds to `memory/context.md` a section "Summary of archived content" with a short excerpt per file from `archive/notes/` and `research/`, and appends one decision and one learning about the restructure. Idempotent: safe to run again.

**Memory schema:** [docs/DARWIN_MEMORY_SCHEMA.md](../../docs/DARWIN_MEMORY_SCHEMA.md).
