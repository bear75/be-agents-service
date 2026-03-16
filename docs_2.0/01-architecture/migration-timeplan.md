AppCaire Migration Timeline
20-Week Incremental Migration Plan
Phase 1: Monorepo Foundation (Weeks 1-2)
Week 1: Convert to Monorepo

Initialize Yarn workspaces + Turborepo

Move existing code to apps/client

Update imports and configurations

Verify Next.js app works

Week 2: Base Packages

Create packages/ui (styled-components)

Create packages/graphql (Codegen setup)

Create packages/prisma (introspect DB schema)

Create packages/shared (types & utils)

Phase 2: GraphQL Server with Prisma (Weeks 3-5)
Week 3: Prisma + Express + Apollo

Introspect existing DB → Prisma schema

Create apps/server Express app

Setup Apollo Server

Configure Prisma client

Setup Clerk auth middleware

Week 4: Core GraphQL Schema

Organization types & resolvers (Prisma)

Client types & resolvers (Prisma)

Employee types & resolvers (Prisma)

Service Area types & resolvers (Prisma)

Week 5: Advanced GraphQL

OptimizationJob types & resolvers

SolutionMetrics types & resolvers

Analytics queries

Subscriptions for real-time updates

Phase 3: UI Package Development (Weeks 6-8)
Week 6: Core UI Components

Theme system (styled-components)

Button, Card, Modal, Form components

Input, Select, TextArea

Week 7: Complex UI Components

Badge, Tabs, Dropdown/Menu

DatePicker, Toast, Loading/Skeleton

Setup Storybook

Week 8: Layout Components

Sidebar, Header, PageLayout

DataTable with sorting/filtering

Component exports & documentation

Phase 4: GraphQL Integration in Next.js (Weeks 9-11)
Week 9: Apollo Client Setup

Install @appcaire/graphql in Next.js

Configure Apollo Client (SSR-compatible)

Setup Apollo Provider

Auth token forwarding

Week 10: Migrate First Features

Organization queries → GraphQL

Client list/detail → GraphQL

Employee list/detail → GraphQL

Update components to use generated hooks

Week 11: Migrate Scheduling

Schedule queries → GraphQL

OptimizationJob queries/mutations

Visit queries → GraphQL

Update CalendarView

Phase 5: UI Package Integration (Weeks 12-14)
Week 12: Replace UI Components

Install @appcaire/ui in Next.js

Setup ThemeProvider

Replace Button, Card, Modal, Form components

Week 13: Continue UI Migration

Replace Table, Tabs, Badge, Dropdown

Replace Loading, Toast components

Week 14: Layout & Final UI

Migrate Sidebar, Header, PageLayout

Remove old component files

Visual regression testing

Phase 6: Migrate Next.js to Prisma (Weeks 15-17)
Week 15: Migrate Services

Install @appcaire/prisma in Next.js

Migrate scheduling services (Drizzle → Prisma)

Migrate resource services (clients, employees)

Migrate analytics services

Week 16: Migrate API Routes

Migrate admin API routes → Prisma

Migrate integration API routes → Prisma

Migrate pre-planning API routes → Prisma

Parallel testing (Drizzle vs Prisma)

Week 17: Remove Drizzle

Remove all Drizzle imports/usages

Remove Drizzle dependencies

Delete drizzle/ directory

Update TypeScript types

Phase 7: Cleanup & Optimization (Weeks 18-20)
Week 18: Remove Deprecated Code

Remove unused REST API routes

Remove old component files

Clean up unused dependencies

Update CI/CD

Week 19: Testing

Unit tests for @appcaire/ui

Integration tests for GraphQL

E2E tests for critical flows

Week 20: Performance & Documentation

GraphQL query optimization

Caching strategy (Apollo, Redis)

Bundle size optimization

API & developer documentation

Quick Reference
Phase

Focus

Weeks

Duration

1

Monorepo Foundation

1-2

2 weeks

2

GraphQL Server (Prisma)

3-5

3 weeks

3

UI Package

6-8

3 weeks

4

GraphQL Integration

9-11

3 weeks

5

UI Integration

12-14

3 weeks

6

Drizzle → Prisma

15-17

3 weeks

7

Cleanup & Polish

18-20

3 weeks

Total

1-20

20 weeks (~5 months)

Key Milestones
Week 2: Monorepo working, packages created

Week 5: GraphQL server live with Prisma

Week 8: UI package complete

Week 11: Next.js using GraphQL for new features

Week 14: Next.js using shared UI components

Week 17: Single ORM (Prisma) across codebase

Week 20: Production ready
