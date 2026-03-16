# CAIRE Dashboard MVP - Implementation Plan

> **This plan has been split into focused documents for parallel development.**

## 📁 Plan Documents

| Document                                                                     | Scope                                | Est. Time |
| ---------------------------------------------------------------------------- | ------------------------------------ | --------- |
| [`docs/plan-00-overview.md`](docs/plan-00-overview.md)                       | Overview, architecture, coordination | -         |
| [`docs/plan-01-foundation.md`](docs/plan-01-foundation.md)                   | Dependencies, Apollo Client, types   | 0.5 days  |
| [`docs/plan-02-bryntum-models.md`](docs/plan-02-bryntum-models.md)           | Custom models, scheduler config      | 0.75 days |
| [`docs/plan-03-graphql-layer.md`](docs/plan-03-graphql-layer.md)             | Queries, mutations, mappers, hooks   | 1 day     |
| [`docs/plan-04-scheduler-component.md`](docs/plan-04-scheduler-component.md) | Scheduler, context, config hook      | 1 day     |
| [`docs/plan-05-unplanned-grid.md`](docs/plan-05-unplanned-grid.md)           | UnplannedGrid, DragHelper            | 0.75 days |
| [`docs/plan-06-i18n-styles.md`](docs/plan-06-i18n-styles.md)                 | i18n, translations, Bryntum theme    | 0.5 days  |

## 🚀 Quick Start

### Parallel Work Assignment

```
Wave 1 (Start immediately):
├── Agent A: Part 01 + Part 02
├── Agent B: Part 06
└── (No dependencies)

Wave 2 (After Part 01):
└── Agent C: Part 03

Wave 3 (After Parts 01-03):
└── Agent D: Part 04 + Part 05
```

### Dependency Graph

```
Part 01 (Foundation)
    │
    ├──────────────────┐
    │                  │
    ▼                  ▼
Part 02            Part 03
(Models)           (GraphQL)
    │                  │
    └────────┬─────────┘
             │
             ▼
         Part 04
       (Scheduler)
             │
             ▼
         Part 05
    (Unplanned Grid)

Part 06 (i18n/Styles) ─── Independent, can run in parallel
```

## 📋 Scope Reference

See [`scope-mvp.md`](scope-mvp.md) for original requirements and timeline.
