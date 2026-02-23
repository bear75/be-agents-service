# Agent Prompts (Souls)

Prompts in this directory are the **system prompts** ("souls") for each agent. The dashboard's Agent Details view reads them via the API.

## Lookup Order

1. **be-agents-service** `agents/prompts/{prompt}.md`
2. **Target repo** (e.g. beta-appcaire) `.claude/prompts/{prompt}.md`

To add or update prompts: create them here first, or copy from the target repo.

---

## All 25 Agents vs Prompts

`AGENT_TO_FILES` in `apps/server/src/routes/file.ts` maps each agent to a script and a prompt file. Script paths are `agents/{script}.sh`. Scripts and prompts now exist for **all 25 agents**.

### Engineering (10) — all prompts exist

| Agent ID | Script | Prompt file | Status |
|----------|--------|-------------|--------|
| agent-backend | backend-specialist | backend-specialist.md | ✅ |
| agent-frontend | frontend-specialist | frontend-specialist.md | ✅ |
| agent-infrastructure | infrastructure-specialist | infrastructure-specialist.md | ✅ |
| agent-verification | verification-specialist | verification-specialist.md | ✅ |
| agent-senior-reviewer | senior-code-reviewer | senior-code-reviewer.md | ✅ |
| agent-db-architect | db-architect-specialist | db-architect-specialist.md | ✅ |
| agent-ux-designer | ux-designer-specialist | ux-designer-specialist.md | ✅ |
| agent-docs-expert | documentation-expert | documentation-expert.md | ✅ |
| agent-levelup | levelup-specialist | levelup-specialist.md | ✅ |
| agent-orchestrator | orchestrator | orchestrator.md | ✅ |

### Marketing (10) — all prompts exist

| Agent ID | Script | Prompt file | Status |
|----------|--------|-------------|--------|
| agent-jarvis | marketing/jarvis-orchestrator | jarvis-orchestrator.md | ✅ |
| agent-vision | marketing/vision-seo-analyst | vision-seo-analyst.md | ✅ |
| agent-loki | marketing/loki-content-writer | loki-content-writer.md | ✅ |
| agent-shuri | marketing/shuri-product-analyst | shuri-product-analyst.md | ✅ |
| agent-fury | marketing/fury-customer-researcher | fury-customer-researcher.md | ✅ |
| agent-wanda | marketing/wanda-designer | wanda-designer.md | ✅ |
| agent-quill | marketing/quill-social-media | quill-social-media.md | ✅ |
| agent-pepper | marketing/pepper-email-marketing | pepper-email-marketing.md | ✅ |
| agent-friday | marketing/friday-developer | friday-developer.md | ✅ |
| agent-wong | marketing/wong-notion-agent | wong-notion-agent.md | ✅ |

### Management (5) — all prompts exist

| Agent ID | Script | Prompt file | Status |
|----------|--------|-------------|--------|
| agent-ceo | management/ceo | ceo.md | ✅ |
| agent-cmo-cso | management/cmo-cso | cmo-cso.md | ✅ |
| agent-cpo-cto | management/cpo-cto | cpo-cto.md | ✅ |
| agent-hr-lead | management/hr-agent-lead | hr-agent-lead.md | ✅ |
| agent-interface | management/interface-agent | interface-agent.md | ✅ |

---

## Management scripts

Management scripts are thin stubs that delegate:

- **CEO** → Orchestrator (engineering)
- **CPO/CTO** → Orchestrator (engineering)
- **CMO/CSO** → Jarvis (marketing)
- **HR Agent Lead** → daily-compound-review.sh (learnings extraction)
- **Interface Agent** → status check; main logic runs via OpenClaw gateway

---

## How to add prompts

1. Copy an existing prompt (e.g. `backend-specialist.md`) as a template.
2. Create `agents/prompts/{prompt-name}.md` — filename must match the `prompt` key in `AGENT_TO_FILES`.
3. Adjust role, scope, constraints, and JSON schema for that agent.
4. Optionally copy to target repo: `beta-appcaire/.claude/prompts/{prompt-name}.md`.
