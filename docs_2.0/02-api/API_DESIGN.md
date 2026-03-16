# API Design – GraphQL + Express + Prisma

**Project:** CAIRE Platform Refactoring  
**Current:** 319 Next.js API routes (Drizzle)  
**Target:** GraphQL API (Express + Apollo + Prisma)  
**Architecture:** [See architecture.md](../01-architecture/architecture.md)

**Related Documents:**

- **GraphQL Schema Specification:** `GRAPHQL_SCHEMA_SPECIFICATION.md` - Single source of truth for GraphQL schema files
- **Mapper Specifications:** `MAPPER_SPECIFICATIONS.md` - Detailed mapper function specifications
- **Data Model:** `../03-data/data-model.md` - Database schema documentation

---

## Quick Answer

**Yes, the new API uses the target tech stack:**

✅ **Express** (standalone server, not Next.js API routes)  
✅ **GraphQL** (Apollo Server - primary API)  
✅ **Prisma** (type-safe ORM, not Drizzle)  
✅ **WebSocket** (GraphQL subscriptions for real-time)  
✅ **REST** (secondary - webhooks, files only)

**Operations: ~60-85 total**

- GraphQL: ~50-60 operations (queries + mutations + subscriptions)
- REST: ~10-15 endpoints (webhooks, files, health)

> **📍 Route Optimization Note:** Employee home addresses are **not stored** or used for route optimization. The optimization API uses **office/depot locations** (from organization or service area addresses) as the start and end point for all employees. This data minimization approach reduces privacy risk while maintaining full optimization functionality.

---

## Tech Stack Details

### 1. Express Server

```typescript
// packages/server/src/index.ts

import express from "express";
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@apollo/server/express4";
import { createServer } from "http";
import { WebSocketServer } from "ws";
import { useServer } from "graphql-ws/lib/use/ws";
import { PrismaClient } from "@prisma/client";

const app = express();
const httpServer = createServer(app);
const prisma = new PrismaClient();

// GraphQL server
const apolloServer = new ApolloServer({
  typeDefs,
  resolvers,
});

await apolloServer.start();

// GraphQL endpoint
app.use(
  "/graphql",
  cors(),
  express.json(),
  expressMiddleware(apolloServer, {
    context: async ({ req }) => ({
      prisma,
      user: req.user,
      organizationId: req.organizationId,
    }),
  }),
);

// WebSocket for subscriptions
const wsServer = new WebSocketServer({
  server: httpServer,
  path: "/graphql",
});

useServer({ schema, context: { prisma } }, wsServer);

// REST endpoints (secondary)
app.post("/webhooks/clerk", clerkWebhookHandler);
app.post("/files/upload", fileUploadHandler);
app.get("/health", healthCheckHandler);

httpServer.listen(4000, () => {
  console.log("🚀 Server ready at http://localhost:4000/graphql");
});
```

### 2. Prisma Client

```typescript
// packages/prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// Generated from data-model-v2.md
model Organization {
  id        String   @id
  name      String
  slug      String   @unique

  employees Employee[]
  clients   Client[]
  schedules Schedule[]

  @@map("organizations")
}

model Schedule {
  id             String         @id @default(uuid())
  organizationId String
  date           DateTime
  name           String
  type           ScheduleType
  status         ScheduleStatus

  organization   Organization   @relation(fields: [organizationId], references: [id])
  visits         Visit[]
  solution       Solution?

  @@map("schedules")
}

// ... rest from data-model-v2.md
```

### 3. Apollo Client (Frontend)

```typescript
// packages/client/src/lib/apollo.ts

import { ApolloClient, InMemoryCache, split, HttpLink } from "@apollo/client";
import { GraphQLWsLink } from "@apollo/client/link/subscriptions";
import { getMainDefinition } from "@apollo/client/utilities";
import { createClient } from "graphql-ws";

// HTTP link for queries and mutations
const httpLink = new HttpLink({
  uri: "http://localhost:4000/graphql",
  headers: {
    authorization: `Bearer ${getClerkToken()}`,
  },
});

// WebSocket link for subscriptions
const wsLink = new GraphQLWsLink(
  createClient({
    url: "ws://localhost:4000/graphql",
  }),
);

// Split traffic: subscriptions via WS, queries/mutations via HTTP
const splitLink = split(
  ({ query }) => {
    const definition = getMainDefinition(query);
    return (
      definition.kind === "OperationDefinition" &&
      definition.operation === "subscription"
    );
  },
  wsLink,
  httpLink,
);

export const apolloClient = new ApolloClient({
  link: splitLink,
  cache: new InMemoryCache(),
});
```

---

## Authentication & Authorization

### Architecture Overview

**Current:** Clerk for authentication  
**Independence:** ✅ Yes, can swap to any auth provider  
**Sync:** Clerk webhooks → `organization_members` table  
**Decoupling:** Auth stored separately from domain data

### Auth-Independent Database Design

**Key Principle:** Domain data is auth-provider independent. Only `organization_members` table contains auth provider IDs.

```typescript
// Domain entity (auth-independent)
model Organization {
  id        String   @id @default(uuid())
  name      String
  slug      String   @unique
  settings  Json?
  members   OrganizationMember[]
  employees Employee[]
  clients   Client[]
  schedules Schedule[]
}

// Auth bridge table (ONLY place with auth provider IDs)
model OrganizationMember {
  id             String   @id @default(uuid())
  organizationId String
  userId         String   @unique  // ← Clerk user ID (swappable)
  role           String   @default("member")  // admin, member, viewer
  joinedAt       DateTime @default(now())
  organization   Organization @relation(fields: [organizationId], references: [id])
  @@unique([organizationId, userId])
}

// Domain entities (no auth data)
model Employee {
  id             String   @id @default(uuid())
  organizationId String
  userId         String?  // ← Optional, for employee portal access
  name           String
  email          String
  // ... domain data only
}
```

**✅ Auth-Independent:**

- `organizations` = Pure domain entity (no auth data)
- `employees` = Pure domain entity (optional userId link)
- `schedules` = Domain entity (userId is just a string for audit)

**⚠️ Auth Bridge:**

- `organization_members` = **ONLY** table with auth provider IDs
- This is the "adapter" layer between Clerk and domain

### Authentication Middleware

```typescript
// packages/server/src/middleware/auth.ts

import { clerkClient } from "@clerk/clerk-sdk-node";

export async function authMiddleware(req, res, next) {
  try {
    // 1. Extract token
    const token = req.headers.authorization?.replace("Bearer ", "");
    if (!token) {
      throw new Error("No token provided");
    }

    // 2. Verify with Clerk
    const session = await clerkClient.verifyToken(token);
    if (!session) {
      throw new Error("Invalid token");
    }

    // 3. Extract user/org from token claims
    const userId = session.sub;
    const organizationId = session.org_id;

    // 4. Load user context from DB
    const member = await prisma.organizationMember.findUnique({
      where: {
        organizationId_userId: {
          organizationId,
          userId,
        },
      },
      include: {
        organization: true,
      },
    });

    if (!member) {
      throw new Error("User not member of organization");
    }

    // 5. Attach to request
    req.user = {
      id: userId,
      role: member.role,
      organizationId: organizationId,
      organization: member.organization,
    };

    next();
  } catch (error) {
    res.status(401).json({ error: "Unauthorized" });
  }
}
```

### GraphQL Context

```typescript
// packages/server/src/graphql/context.ts

export interface Context {
  prisma: PrismaClient;
  user: {
    id: string; // Clerk userId
    role: string; // admin, member, viewer
    organizationId: string;
    organization: Organization;
  };
}

export async function createContext({ req }): Promise<Context> {
  // User already attached by authMiddleware
  return {
    prisma,
    user: req.user,
  };
}
```

### Clerk Webhook Sync

Clerk webhooks sync organization and membership data to our database:

```typescript
// packages/server/src/rest/webhooks/clerk.ts

export async function clerkWebhookHandler(req, res) {
  const wh = new Webhook(process.env.CLERK_WEBHOOK_SECRET);
  const payload = wh.verify(req.body, req.headers);
  const { type, data } = payload;

  switch (type) {
    case "organization.created":
      await handleOrganizationCreated(data);
      break;
    case "organizationMembership.created":
      await handleMembershipCreated(data);
      break;
    case "organizationMembership.updated":
      await handleMembershipUpdated(data);
      break;
    case "organizationMembership.deleted":
      await handleMembershipDeleted(data);
      break;
  }

  res.status(200).json({ received: true });
}
```

**Webhook Flow:**

- `organization.created` → Create `organizations` + `organization_members` (creator as admin)
- `organizationMembership.created` → Insert `organization_members`
- `organizationMembership.updated` → Update `organization_members.role`
- `organizationMembership.deleted` → Delete from `organization_members`

### Authorization Patterns

**Role-Based Access Control (RBAC):**

```typescript
// GraphQL resolvers check authorization
export const scheduleResolvers = {
  Query: {
    schedule: async (_, { id }, { prisma, user }) => {
      const schedule = await prisma.schedule.findUnique({
        where: { id },
      });

      // Org-level authorization
      if (schedule.organizationId !== user.organizationId) {
        throw new Error("Not authorized");
      }

      return schedule;
    },
  },
  Mutation: {
    deleteSchedule: async (_, { id }, { prisma, user }) => {
      // Role-based authorization
      if (user.role !== "admin") {
        throw new Error("Admin role required");
      }

      const schedule = await prisma.schedule.findUnique({
        where: { id },
      });

      if (schedule.organizationId !== user.organizationId) {
        throw new Error("Not authorized");
      }

      await prisma.schedule.delete({ where: { id } });
      return true;
    },
  },
};
```

**GraphQL Directive-Based Authorization:**

```graphql
directive @auth(requires: Role = MEMBER) on FIELD_DEFINITION

enum Role {
  ADMIN
  MEMBER
  VIEWER
}

type Mutation {
  createSchedule(input: CreateScheduleInput!): Schedule! @auth(requires: MEMBER)
  deleteSchedule(id: ID!): Boolean! @auth(requires: ADMIN)
}
```

### Multi-Tenancy Pattern

All queries automatically scoped to user's organization:

```typescript
export const scheduleResolvers = {
  Query: {
    schedules: async (_, { filter }, { prisma, user }) => {
      // Automatically inject organizationId filter
      return prisma.schedule.findMany({
        where: {
          organizationId: user.organizationId, // ← Always filtered
          ...filter,
        },
      });
    },
  },
};
```

### Auth Provider Independence

**To switch from Clerk to Auth0/Supabase/Custom:**

1. **Update `organization_members` table** (optional column rename)
2. **Update webhook handler** (1 file) - different payload structure
3. **Update auth middleware** (1 file) - different token verification
4. **Unchanged:** All domain logic, GraphQL resolvers, business logic

**Estimated effort:** 1-2 days

**Current Implementation:**

- ✅ JWT verification via Clerk
- ✅ Organization webhooks
- ✅ SSO, MFA support
- ✅ Role management
- ✅ Auth data isolated in `organization_members`
- ✅ Domain entities auth-independent

---

## GraphQL Operations Summary

### Total: ~71 Operations

**Queries (30):**

- Organizations: 2
- Employees: 3
- Clients: 3
- Schedules: 4
- Visits: 2
- Visit Templates: 2
- Templates (Slinga): 2
- Schedule Groups: 2
- Optimization: 2
- Solutions: 3
- Scenarios: 2
- Metrics: 4

**Mutations (38):**

- Organizations: 3 (create, update, delete)
- Employees: 4 (CRUD + addSkill)
- Clients: 4 (CRUD + updatePreferences)
- Schedules: 5 (CRUD + publish + duplicate)
- Visits: 4 (CRUD + pin + assign)
- Visit Templates: 5 (CRUD + lifecycle + convert)
- Templates: 3 (CRUD + instantiate)
- Schedule Groups: 3 (CRUD)
- Optimization: 3 (run, fineTune, terminate)
- Solutions: 1 (accept)
- Scenarios: 3 (CRUD)

**Subscriptions (3):**

- optimizationProgress(jobId)
- solutionUpdated(scheduleId)
- scheduleUpdated(scheduleId)

---

## REST Endpoints (15 Secondary)

Used only for:

- **Webhooks:** 5 (Clerk, Timefold, Carefox, etc.)
- **Files:** 3 (upload, download, export)
- **Integrations:** 3 (token endpoints)
- **Auth:** 2 (token refresh, me)
- **Health:** 2 (health, db health)

---

## Why GraphQL + Express + Prisma?

### vs Current (Next.js + REST + Drizzle)

| Feature             | Current            | New                              | Benefit                |
| ------------------- | ------------------ | -------------------------------- | ---------------------- |
| **Type Safety**     | ❌ Manual          | ✅ Auto-generated                | No type mismatches     |
| **API Efficiency**  | ❌ Over-fetching   | ✅ Request exactly what you need | Faster, less bandwidth |
| **Real-time**       | ❌ Polling         | ✅ WebSocket subscriptions       | Live updates           |
| **Code Generation** | ❌ Manual          | ✅ Prisma + GraphQL codegen      | Less boilerplate       |
| **Documentation**   | ❌ Manual          | ✅ Introspection (auto)          | Always up-to-date      |
| **Monorepo**        | ❌ Monolith        | ✅ Modular packages              | Better separation      |
| **Testing**         | ❌ Hard            | ✅ Easy (mocking)                | Better quality         |
| **Scaling**         | ❌ Tied to Next.js | ✅ Independent server            | Deploy separately      |

### GraphQL Benefits for CAIRE

**1. Efficient Data Fetching**

```graphql
# Client requests exactly what it needs:
query GetScheduleForCalendar($id: ID!) {
  schedule(id: $id) {
    id
    name
    visits {
      id
      name
      plannedStartTime
      duration
      client {
        name
      } # Only client name
      assignment {
        employee {
          name
        } # Only employee name
      }
    }
  }
}

# vs REST: Would need 3-4 endpoints
# GET /schedules/:id (includes ALL fields)
# GET /schedules/:id/visits
# GET /visits/:id/client
# GET /assignments/:id/employee
```

**2. Real-time Updates**

```typescript
// Subscribe to optimization progress
useSubscription(OPTIMIZATION_PROGRESS, {
  variables: { jobId: "job_123" },
  onData: ({ data }) => {
    setProgress(data.optimizationProgress.progress);
    // Updates automatically, no polling!
  },
});
```

**3. Type Safety**

```typescript
// Prisma generates types
const schedule = await prisma.schedule.findUnique({
  where: { id },
  include: { visits: true }, // TypeScript knows 'visits' exists
});

// GraphQL Codegen generates hooks
const { data, loading } = useGetScheduleQuery({
  variables: { id: scheduleId },
});
// TypeScript knows exact shape of 'data'
```

---

## Monorepo Structure

```
appcaire-v2/                          # New monorepo
├── packages/
│   ├── client/                       # React + Vite frontend
│   │   ├── src/
│   │   │   ├── features/             # Feature modules
│   │   │   ├── graphql/              # GraphQL queries/mutations
│   │   │   ├── lib/apollo.ts         # Apollo Client setup
│   │   │   └── main.tsx
│   │   └── package.json
│   │
│   ├── server/                       # Express + Apollo backend
│   │   ├── src/
│   │   │   ├── graphql/
│   │   │   │   ├── schema.graphql    # GraphQL schema
│   │   │   │   └── resolvers/        # Resolver functions
│   │   │   ├── services/             # Business logic
│   │   │   ├── integrations/         # External APIs
│   │   │   ├── middleware/           # Auth, logging, etc.
│   │   │   ├── rest/                 # REST endpoints
│   │   │   └── index.ts              # Server entry
│   │   └── package.json
│   │
│   └── prisma/                       # Shared Prisma schema
│       ├── schema.prisma             # From data-model-v2.md
│       ├── migrations/               # Migration files
│       ├── seed.ts                   # Seed data
│       └── package.json
│
├── turbo.json                        # Turborepo config
└── package.json                      # Root dependencies
```

---

## Implementation Timeline

### Week 1-2: Infrastructure + Core API

- [ ] Setup monorepo structure
- [ ] Setup Express + Apollo Server
- [ ] Generate Prisma schema from data-model-v2.md
- [ ] Create initial migrations
- [ ] Setup authentication middleware
- [ ] Implement core GraphQL schema (Organizations, Employees, Clients)
- [ ] Implement core resolvers
- [ ] Setup Apollo Client in frontend
- [ ] Test end-to-end

**Deliverable:** CRUD operations working for core resources

### Week 3: Scheduling Features

- [ ] Implement Schedule operations
- [ ] Implement Visit operations
- [ ] Implement Visit Template operations
- [ ] Implement Template (Slinga) operations
- [ ] Implement Schedule Group operations
- [ ] Setup WebSocket subscriptions
- [ ] Test real-time updates

**Deliverable:** Scheduling operations complete

### Week 4: Optimization + Analytics

- [ ] Implement Optimization operations
- [ ] Implement Solution operations
- [ ] Implement Scenario operations
- [ ] Implement Metrics operations
- [ ] Implement REST endpoints (webhooks, files)
- [ ] Complete testing
- [ ] API documentation

**Deliverable:** Complete API ready for production

---

## Migration from Current API

### Don't Port Old Endpoints

**Why not port existing 319 routes?**

- ❌ Many are broken/unused
- ❌ Inconsistent patterns
- ❌ Tied to old schema (Drizzle)
- ❌ No type safety
- ❌ Technical debt

### Build Fresh with GraphQL

**Why start fresh?**

- ✅ Type-safe from day 1
- ✅ Based on new schema (Prisma)
- ✅ Consistent patterns
- ✅ Better architecture
- ✅ Easier to maintain

### Prototype Integration

**Bryntum Calendar → GraphQL:**

```typescript
// Old approach (REST):
const response = await fetch(`/api/scheduling/schedules/${id}`);
const data = await response.json();

// New approach (GraphQL):
const { data } = useGetScheduleDetailsQuery({
  variables: { id: scheduleId },
});

// Bryntum config
const schedulerConfig = {
  loadUrl: null, // No JSON file
  resources: data.schedule.employees.map(mapEmployeeToResource),
  events: data.schedule.visits.map(mapVisitToEvent),
  assignments: data.schedule.solution?.assignments || [],
};
```

---

## API Endpoint Count Breakdown

### GraphQL Operations: ~71

| Category           | Operations | Breakdown                                                                     |
| ------------------ | ---------- | ----------------------------------------------------------------------------- |
| **Core Resources** | 37         | Orgs(5), Employees(7), Clients(7), Schedules(10), Visits(6), Service Areas(2) |
| **Scheduling**     | 20         | Visit Templates(7), Templates(5), Schedule Groups(5), Problems(3)             |
| **Optimization**   | 12         | Optimization(7), Solutions(4), Scenarios(5)                                   |
| **Analytics**      | 4          | Metrics queries                                                               |
| **Real-time**      | 3          | Subscriptions                                                                 |

### REST Endpoints: ~15

| Category         | Endpoints |
| ---------------- | --------- |
| **Webhooks**     | 5         |
| **Files**        | 3         |
| **Integrations** | 3         |
| **Auth**         | 2         |
| **Health**       | 2         |

**Total: ~60-85 operations/endpoints** (vs 319 current)

---

## Comparison Table

| Aspect            | Current (Next.js)            | New (Express + GraphQL)             |
| ----------------- | ---------------------------- | ----------------------------------- |
| **Tech Stack**    | Next.js API Routes + Drizzle | Express + Apollo + Prisma           |
| **API Type**      | REST only                    | GraphQL primary + REST secondary    |
| **Operations**    | 319 route files              | ~60-85 operations                   |
| **Type Safety**   | Partial (Drizzle types only) | Complete (Prisma + GraphQL Codegen) |
| **Real-time**     | Polling                      | WebSocket subscriptions             |
| **Structure**     | Monolith                     | Monorepo (client/server/prisma)     |
| **Deployment**    | Vercel (Next.js)             | Separate Express server + Client    |
| **Scalability**   | Tied to Next.js              | Independent scaling                 |
| **Development**   | Harder to test               | Easier (mocking, DI)                |
| **Documentation** | Manual                       | Auto-generated (introspection)      |

---

## Benefits Summary

### 1. Type Safety (End-to-End)

**Prisma → GraphQL → Client:**

```typescript
// 1. Prisma generates types from schema
// packages/prisma/schema.prisma
model Schedule {
  id     String
  name   String
  visits Visit[]
}

// 2. TypeScript types auto-generated
type Schedule = {
  id: string;
  name: string;
  visits: Visit[];
}

// 3. GraphQL schema matches Prisma
type Schedule {
  id: ID!
  name: String!
  visits: [Visit!]!
}

// 4. Frontend codegen generates typed hooks
const { data } = useGetScheduleQuery();
// data.schedule is fully typed!
```

### 2. Efficient Data Fetching

**GraphQL eliminates over-fetching:**

```graphql
# Request only what Bryntum needs:
query GetScheduleForBryntum($id: ID!) {
  schedule(id: $id) {
    visits {
      id
      name
      plannedStartTime
      duration
      client {
        name
      } # Just name, not all client fields
      assignment {
        employeeId
        startTime
      }
    }
    employees {
      id
      employee {
        name
        transportMode # Just these fields
      }
      shifts {
        minStartTime
        maxEndTime
      }
    }
  }
}

# REST equivalent would require:
# GET /schedules/:id
# GET /schedules/:id/visits (returns ALL visit fields)
# GET /schedules/:id/employees (returns ALL employee fields)
# = 3 requests with over-fetched data

# GraphQL: 1 request, exact data needed
```

### 3. Real-time Updates

**WebSocket subscriptions:**

```typescript
// Frontend subscribes to optimization progress
const { data } = useSubscription(OPTIMIZATION_PROGRESS, {
  variables: { jobId: "job_123" },
});

// Backend publishes updates
await pubsub.publish(`OPTIMIZATION_PROGRESS_${jobId}`, {
  jobId,
  status: "SOLVING_ACTIVE",
  progress: 65,
  eta: 120,
});

// Frontend automatically receives updates
// No polling needed!
```

### 4. Modular Architecture

**Monorepo packages:**

```
packages/
├── client/       # Can deploy to Vercel/Netlify
├── server/       # Can deploy to Railway/Render/AWS
└── prisma/       # Shared schema, migrations
```

**Benefits:**

- ✅ Deploy frontend/backend separately
- ✅ Scale independently
- ✅ Clear boundaries
- ✅ Easier testing

---

## Cost Analysis

### Development Time

| Component                | Time          |
| ------------------------ | ------------- |
| **Setup Infrastructure** | 20 hours      |
| Monorepo setup           | 8h            |
| Express + Apollo         | 8h            |
| Prisma schema            | 4h            |
| **Core GraphQL API**     | 60 hours      |
| Schema definition        | 12h           |
| Resolvers                | 36h           |
| Testing                  | 12h           |
| **Scheduling Features**  | 48 hours      |
| Optimization             | 16h           |
| Templates                | 16h           |
| Solutions                | 16h           |
| **Analytics + REST**     | 32 hours      |
| Metrics                  | 16h           |
| REST endpoints           | 12h           |
| WebSockets               | 4h            |
| **Total**                | **160 hours** |

**vs Porting Current API:** Would take 200+ hours with technical debt

---

## Decision Matrix

### Should We Use GraphQL?

**✅ YES - Reasons:**

1. **Complex UI Requirements**
   - Bryntum calendar needs nested data (schedules → visits → clients → employees)
   - Different views need different fields
   - GraphQL perfect for this

2. **Real-time Requirements**
   - Optimization progress
   - Schedule collaboration
   - GraphQL subscriptions built-in

3. **Type Safety**
   - Prisma generates DB types
   - GraphQL generates API types
   - Codegen generates React hooks
   - Complete type safety

4. **Future-Proof**
   - Mobile app can use same API
   - Third-party integrations easier
   - API versioning built-in

5. **Developer Experience**
   - Auto-generated documentation
   - GraphQL Playground for testing
   - Better debugging

**❌ Only Con:**

- Learning curve (but worth it)

---

## Implementation Checklist

### Setup (Week 1)

- [ ] Create monorepo structure
- [ ] Setup Turborepo
- [ ] Install Express
- [ ] Install Apollo Server
- [ ] Install Prisma
- [ ] Generate Prisma schema from data-model-v2.md
- [ ] Create initial migration
- [ ] Setup authentication middleware
- [ ] Setup GraphQL schema
- [ ] Setup Apollo Client in frontend

### Core API (Week 2)

- [ ] Implement Organizations resolvers
- [ ] Implement Employees resolvers
- [ ] Implement Clients resolvers
- [ ] Implement Schedules resolvers
- [ ] Implement Visits resolvers
- [ ] Add pagination
- [ ] Add filtering
- [ ] Add error handling
- [ ] Write tests

### Scheduling (Week 3)

- [ ] Implement Visit Templates resolvers
- [ ] Implement Templates (Slinga) resolvers
- [ ] Implement Schedule Groups resolvers
- [ ] Implement Optimization resolvers
- [ ] Setup WebSocket subscriptions
- [ ] Test real-time updates

### Analytics + Polish (Week 4)

- [ ] Implement Metrics resolvers
- [ ] Implement Analytics resolvers
- [ ] Implement REST endpoints
- [ ] Complete testing
- [ ] API documentation
- [ ] Performance optimization

---

## Summary

✅ **New API uses target tech stack:**

- Express (standalone server)
- GraphQL with Apollo Server
- Prisma ORM
- WebSocket subscriptions
- Monorepo structure (client/server/prisma)

✅ **~60-85 operations** (vs 319 current routes)

- GraphQL: ~71 operations
- REST: ~15 endpoints

✅ **Complete type safety:**

- Prisma → TypeScript
- GraphQL → TypeScript
- Codegen → React hooks

✅ **Better architecture:**

- Modular monorepo
- Clear separation
- Independent scaling
- Easier testing

**Timeline:** 3-4 weeks  
**Developer Time:** ~160 hours  
**Benefit:** Clean, modern, maintainable API

**Related:**

- Architecture: `architecture.md`
- Schema: `data-model-v2.md`
- Migration: `MIGRATION_STRATEGY.md`
- Roadmap: `PROTOTYPE_ROADMAP.md`
