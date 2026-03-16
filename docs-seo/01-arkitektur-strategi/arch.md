### Development architecture structure

- Apps folder structure requires individual packages with no external dependencies
  - Each package must work as standalone NPM package (like React/Brintum)
  - No environment variables or database connections within package directory
- Prisma database should not be separate package
  - Database maps to one microservice only
  - Need different database → create separate microservice
- Server naming clarification needed
  - Shridhar’s server → rename to “dashboard server”
  - Björn’s new server → name as “SEO server” or similar

### Database and server restructuring required

- Move Prisma from packages to new web server (stats-server) under apps
- Create separate application for each backend/database interaction
- One database per application rule
  - Dashboard database access → use GraphQL queries in same application
  - Different database needs → separate server application
- Clean up temporary scripts
  - Move convert Excel to CSV and scraping scripts to dedicated scripts folder
  - Remove root-level clutter from migration

### Component organization changes

- Combine design systems into single UI package
  - No separate design system packages needed
  - Create subfolders within UI source folder (e.g. “SEO” subfolder)
  - Organize all components in same package with variants
- GraphQL definitions structure
  - Keep definitions in packages (contracts only)
  - Move actual resolvers to respective server applications
  - Definitions work across multiple apps with different implementations

### Resolver file structure requirements

- Break down large resolver files into granular structure
  1. Create topic folders (e.g. “municipalities”)
  2. Add mutations and queries subfolders within each topic
  3. One function per file (e.g. municipalities.ts exports single function)
- Follow established structure pattern from Shridhar’s base implementation
- Use AI assistance to separate existing code into this structure
- Maintain strict organization for scalability

### Next steps

- Björn: Create fresh branch from main and restructure code
- Shridhar: Set up team meeting for 1 hour from call time
- Björn: Stash current changes, start clean implementation
- Code review session after initial restructuring complete

---

Chat with meeting transcript: [https://notes.granola.ai/t/75955671-cf73-456e-8186-48411e0f10ad](https://notes.granola.ai/t/75955671-cf73-456e-8186-48411e0f10ad)
