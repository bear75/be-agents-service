# DARWIN memory – structured schema (machine-readable)

Memory files in `memory/` have both human-editable `.md` and machine-readable `.json`. The `.json` files are generated from `.md` by `scripts/darwin/memory-to-structured.js`. Agents and compound should read `.json` when they need structured context.

---

## context.json

Single object describing project context.

```json
{
  "version": 1,
  "updated": "2026-03-02T12:00:00Z",
  "project": "One-line or short description of the project.",
  "focus": "What we are building right now.",
  "constraints": ["Technical or business constraint 1", "Constraint 2"],
  "team": "Who's involved and roles (free text).",
  "links": [
    { "label": "Repo", "url": "https://github.com/..." },
    { "label": "Dashboard", "url": "http://localhost:3010" }
  ]
}
```

**Source:** Parsed from `context.md` sections: `## What is this project?`, `## Current focus`, `## Key constraints`, `## Team & roles`, `## Important links`.

---

## decisions.json

Array of decisions. Each has an optional `id` (e.g. `dec-1`) for stable reference.

```json
{
  "version": 1,
  "updated": "2026-03-02T12:00:00Z",
  "decisions": [
    {
      "id": "dec-1",
      "date": "2026-02-15",
      "title": "Use single priorities.md",
      "context": "Compound was reading both priorities.md and priorities-YYYY-MM-DD.md.",
      "decision": "Use only priorities.md at root; archive dated files.",
      "consequences": "Scripts and compound always read priorities.md."
    }
  ]
}
```

**Source:** Parsed from `decisions.md` blocks: `## YYYY-MM-DD: Title`, then **Context:**, **Decision:**, **Consequences:**.

---

## learnings.json

Array of learnings. Optional `tags` for filtering.

```json
{
  "version": 1,
  "updated": "2026-03-02T12:00:00Z",
  "learnings": [
    {
      "id": "learn-1",
      "date": "2026-02-20",
      "summary": "Timefold travel adjustment formula.",
      "detail": "adjustedTravelTime = multiplier * mapTravelTime + extraTime.",
      "tags": ["timefold", "config"]
    }
  ]
}
```

**Source:** Parsed from `learnings.md`. Each list item or `## date` block becomes one entry; first line = summary, rest = detail. Optional `(tags: a, b)` at end of line.

---

## Validation

- All dates in `YYYY-MM-DD` or ISO8601.
- `id` in decisions and learnings: optional; if present, alphanumeric and hyphen only.
- `links`: array of `{ "label": string, "url": string }`.
- Script `memory-to-structured` should not remove data when converting: if a section is missing in .md, leave the corresponding .json field empty or default.
