# Pre-Merge Checklist ✅

**Enforced by:** Documentation Expert Agent
**Purpose:** Ensure code quality, architecture compliance, and documentation accuracy before merging to main

---

## 📋 Architecture Compliance

### Beta-AppCaire Monorepo Rules

Reference: `/Users/bjornevers_MacPro/HomeCare/beta-appcaire/.cursor/rules/appcaire-monorepo.mdc`

- [ ] **Package Structure:** Changes follow workspace organization (apps/, packages/)
- [ ] **GraphQL Schema:** Schema changes include:
  - [ ] Updated schema.graphql
  - [ ] Ran codegen (`yarn workspace @appcaire/graphql codegen`)
  - [ ] Updated operations in frontend
- [ ] **Prisma Schema:** Database changes include:
  - [ ] Updated schema.prisma
  - [ ] Created migration
  - [ ] Tested migration locally
- [ ] **Type Safety:** No TypeScript errors (`yarn workspace <workspace> type-check`)
- [ ] **Dependencies:**
  - [ ] New dependencies added to correct workspace
  - [ ] No duplicate dependencies across workspaces
  - [ ] Packages remain pure (no database imports in shared packages)

### Architecture Document

Reference: `/Users/bjornevers_MacPro/HomeCare/beta-appcaire/.claude/prompts/architecture.md`

- [ ] **Data Flow:** Changes follow established data flow patterns
- [ ] **State Management:** React state management follows conventions
- [ ] **API Patterns:** GraphQL resolvers follow established patterns
- [ ] **Security:** organizationId filtering applied where required
- [ ] **Performance:** N+1 queries prevented with proper includes

---

## 📚 Documentation Updates

### Documentation Expert Responsibilities

- [ ] **README Updates:** Project README reflects new features/changes
- [ ] **CLAUDE.md Updates:**
  - [ ] New learnings added to appropriate CLAUDE.md
  - [ ] Anti-patterns documented
  - [ ] Common errors added to troubleshooting
- [ ] **Architecture Docs:**
  - [ ] architecture.md updated if structural changes
  - [ ] Component documentation current
  - [ ] API documentation current
- [ ] **Migration Notes:** Breaking changes documented in MIGRATION_NOTES.md (if exists)
- [ ] **Obsolete Docs:** Outdated documentation moved to docs-archive/

### Agent Service Documentation

- [ ] **AGENTS.md:** New agents added with complete descriptions
- [ ] **WHERE_IS_THE_DATA.md:** Data architecture current
- [ ] **WORKFLOW.md:** Process changes documented
- [ ] **Testing Guide:** New features have testing instructions

---

## 🧪 Testing & Verification

### Code Quality

- [ ] **Build Success:** All workspaces build without errors
- [ ] **Type Check:** No TypeScript errors in any workspace
- [ ] **Lint:** Code follows linting rules (warnings acceptable)
- [ ] **Tests:** Existing tests still pass (if test suite exists)

### Functional Verification

- [ ] **Feature Works:** New feature tested manually
- [ ] **No Regressions:** Existing features still work
- [ ] **Error Handling:** Error states handled gracefully
- [ ] **Edge Cases:** Common edge cases tested

### Database Changes

- [ ] **Migration Tested:** Migration runs successfully on clean database
- [ ] **Rollback Plan:** Migration can be rolled back if needed
- [ ] **Data Integrity:** Foreign keys and constraints properly configured
- [ ] **Indexes:** Performance indexes added for frequently queried fields

---

## 🔒 Security Review

- [ ] **Input Validation:** User input validated on backend
- [ ] **Authentication:** Protected routes require authentication
- [ ] **Authorization:** organizationId filtering prevents data leakage
- [ ] **SQL Injection:** Prisma parameterized queries used (no raw SQL strings with user input)
- [ ] **XSS Protection:** User content sanitized before rendering
- [ ] **Secrets:** No API keys, passwords, or secrets in code

---

## 🎨 UX/Design Review

- [ ] **Responsive:** UI works on mobile, tablet, desktop
- [ ] **Accessibility:** Basic accessibility guidelines followed
- [ ] **Brand Guidelines:** Design follows brand identity from docs/docs-seo/03-brand-design/
- [ ] **Error Messages:** User-friendly error messages
- [ ] **Loading States:** Loading indicators for async operations
- [ ] **Empty States:** Meaningful empty state messages

---

## 📊 Gamification & RL Learning

### Agent Performance

- [ ] **XP Tracking:** Task completion awards XP correctly
- [ ] **Metrics Recorded:** Performance metrics logged to database
- [ ] **RL Evaluation:** Agent performance tracked for keep/kill/double-down decisions

### Database Integrity

- [ ] **Foreign Keys:** All relationships properly defined
- [ ] **Indexes:** Performance indexes created
- [ ] **Views:** Analytics views return correct data

---

## 🚀 Deployment Readiness

### Pre-Merge Requirements

- [ ] **Branch Updated:** Branch rebased on latest main
- [ ] **Conflicts Resolved:** No merge conflicts
- [ ] **PR Description:** Clear description of changes
- [ ] **Breaking Changes:** Breaking changes documented and communicated

### Post-Merge Plan

- [ ] **Deployment Notes:** Special deployment steps documented (if any)
- [ ] **Rollback Plan:** Rollback procedure identified
- [ ] **Monitoring:** Know how to verify deployment success
- [ ] **Team Communication:** Team aware of changes

---

## 🎯 Final Verification

**Documentation Expert Sign-Off:**
- [ ] All documentation reviewed and updated
- [ ] Architecture compliance verified
- [ ] Obsolete docs archived
- [ ] Team notified of documentation changes

**Senior Reviewer Sign-Off:**
- [ ] Code quality acceptable
- [ ] Architecture patterns followed
- [ ] Security concerns addressed
- [ ] Performance acceptable

**Orchestrator Sign-Off:**
- [ ] All tests pass
- [ ] Build succeeds
- [ ] Integration verified
- [ ] Ready to merge

---

## ⚠️ Common Mistakes to Avoid

1. **Forgetting Codegen:** Always run `yarn workspace @appcaire/graphql codegen` after GraphQL schema changes
2. **Skipping Type Check:** Run type-check before PR to catch errors early
3. **Missing organizationId:** Always filter by organizationId in multi-tenant queries
4. **Duplicate Dependencies:** Check if dependency already exists in another workspace
5. **Outdated Docs:** Update README, CLAUDE.md, and architecture docs with changes
6. **No Migration:** Prisma schema changes require migrations
7. **Raw SQL with User Input:** Use Prisma parameterized queries, never string concatenation
8. **No Error Handling:** Handle errors gracefully with user-friendly messages
9. **Forgetting Mobile:** Test responsive design on mobile viewport
10. **Skipping Security Review:** Always review organizationId filtering and input validation

---

## 🔄 Automation

**Pre-Commit Hooks:**
```bash
# Run type-check
yarn type-check

# Run lint
yarn lint

# Check for secrets
git secrets --scan
```

**GitHub Actions (Future):**
- Automated type checking
- Automated tests
- Build verification
- Documentation link checking

---

## 📝 Notes

**For Documentation Expert:**
- Review this checklist before every merge
- Update checklist based on recurring issues
- Archive outdated checklist items
- Communicate checklist updates to team

**For Orchestrator:**
- Run verification specialist before PR creation
- Block PR creation if critical items fail
- Document blockers clearly for human review

**For CEO/Product Owner:**
- Review PR with this checklist in mind
- Approve only when all items checked
- Provide feedback on documentation quality
- Prioritize documentation debt in next sprint

---

**Last Updated:** 2026-02-08
**Maintained By:** Documentation Expert Agent (agent-docs-expert)
