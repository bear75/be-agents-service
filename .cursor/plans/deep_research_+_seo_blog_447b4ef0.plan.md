---
name: Deep research + SEO blog
overview: Run deep research on homecare route optimization with continuity and special requirements (with academic references), then implement an SEO-optimized blog/article page on www.caire.se that uses that research and existing product knowledge, and is structured so marketing can own a content plan.
todos: []
isProject: false
---

# Deep research + SEO blog for optimization and continuity

## Scope

1. **Deep research** (parallel-cli): Produce a referenced article on route optimization for home care with continuity and special requirements.
2. **Implementation**: Add one new SEO article page on the Caire website (beta-appcaire, `apps/website`) that explains algorithms and maths for efficiency and continuity, and wire it so the marketing team can extend with a content plan (same pattern as existing articles).

---

## Part 1: Deep research (run first)

**When to use:** You attached the parallel-deep-research skill. Run it **before** implementation so the report can seed the blog content and references.

**Topic for `parallel-cli research run`:**

```text
Route optimization for home care and community care: mathematical optimization and algorithms for visit routing, staff continuity (continuity of care), and special requirements. Include: vehicle routing (VRP), constraint programming, time windows, skills matching, double-staff visits, fair distribution of workload. Focus on research papers, academic references, and industry best practices for homecare scheduling efficiency and continuity.
```

**Commands (from skill):**

1. **Start research** (non-blocking):

```bash
   parallel-cli research run "<topic above>" --processor pro-fast --no-wait --json
   

```

   Parse JSON for `run_id` and monitoring URL. Tell the user the URL and expected latency (e.g. 30s–5 min for pro-fast).

1. **Poll for results** (descriptive filename, no `--json`):

```bash
   parallel-cli research poll "<RUN_ID>" -o homecare-route-optimization-continuity --timeout 540
   

```

   Outputs: `homecare-route-optimization-continuity.md` (report) and `homecare-route-optimization-continuity.json` (metadata). Share the executive summary from stdout and the two file paths.

**If `parallel-cli` is not found:** Stop and tell the user to run `/parallel-setup` and retry. Do not substitute with other search tools.

**Use of the report:** The `.md` and `.json` will be used in Part 2 to (1) draft the article body and (2) populate a references/citations section. Plan assumes the report is saved in the repo or a known path (e.g. `docs/` or `apps/website/content/articles/`) so implementation can reference it.

---

## Part 2: Blog / article implementation

The website already has a **Resources > Articles** section (`[apps/website/src/pages/Resurser/Articles.tsx](beta-appcaire/apps/website/src/pages/Resurser/Articles.tsx)`) and per-article pages (e.g. `[future-homecare-trends.tsx](beta-appcaire/apps/website/src/pages/Resources/articles/future-homecare-trends.tsx)`, `[comprehensive-ai-in-home-care.tsx](beta-appcaire/apps/website/src/pages/Resources/articles/comprehensive-ai-in-home-care.tsx)`). Add **one new SEO article** for “algorithms and maths for optimal efficiency and continuity”. Marketing can then add more articles using the same pattern and content plan.

### 2.1 Route and config

- **Routes** (`[apps/website/src/utils/routes.ts](beta-appcaire/apps/website/src/utils/routes.ts)`): Add under `articles`:
  - Swedish: `/resurser/artiklar/optimering-kontinuitet-algoritmer`
  - English: `/en/resources/articles/optimization-continuity-algorithms`
  - Key suggestion: `articles.optimizationContinuityAlgorithms`.
- **App.tsx**: Lazy-load the new page component and register the same route key for both `sv` and `en` (same pattern as `articles.futureHomeCare` and `articles.comprehensiveAiInHomeCare`).

### 2.2 New page component

- **File:** `apps/website/src/pages/Resources/articles/optimization-continuity-algorithms.tsx`.
- **Pattern:** Mirror `[future-homecare-trends.tsx](beta-appcaire/apps/website/src/pages/Resources/articles/future-homecare-trends.tsx)`:
  - `PageSeo` with title, description, canonical, OG image, keywords (optimisation, continuity, scheduling algorithms, efficiency).
  - Schema.org `Article` (headline, description, datePublished, author/publisher).
  - Breadcrumbs (Resurser → Artiklar → [this article]).
  - i18n namespace: `articles/optimization-continuity-algorithms`.
  - Sections: hero/header (title, read time, publish date); body sections with headings and prose; references/citations (from deep research); CTA to product (e.g. route optimization feature).
- **Content sources when writing the copy:**
  - Deep research report (`.md` / `.json`) for structure, claims, and references.
  - Existing product/optimization docs: `[CONTINUITY_STRATEGIES.md](be-agents-service/recurring-visits/docs/CONTINUITY_STRATEGIES.md)`, `[EFFICIENCY_METRICS_EXPLAINED.md](be-agents-service/docs/EFFICIENCY_METRICS_EXPLAINED.md)`, `[PRIORITIES.md](be-agents-service/recurring-visits/huddinge-package/docs/PRIORITIES.md)`, `[DATASET_203cf1d6_ANALYSIS.md](be-agents-service/recurring-visits/huddinge-package/huddinge-datasets/28-feb/DATASET_203cf1d6_ANALYSIS.md)`.
  - Product messaging: if DARWIN workspace is available (e.g. `AgentWorkspace/DARWIN` or path in be-agents-service), read `input/` and `memory/` to align tone and positioning.
- **Efficiency definition (must be consistent):** Use “routing efficiency” as in the codebase: `visit_time / (visit_time + travel_time + wait_time)`; exclude idle. See `[EFFICIENCY_METRICS_EXPLAINED.md](be-agents-service/docs/EFFICIENCY_METRICS_EXPLAINED.md)` (efficiency_assignable_used_pct / routing_efficiency_pct).

### 2.3 i18n and locale files

- **Namespaces** (`[apps/website/src/i18n.ts](beta-appcaire/apps/website/src/i18n.ts)`): Add `articles/optimization-continuity-algorithms`.
- **Locale files:** Add JSON for both languages. Backend loadPath is `/locales/{{lng}}/{{ns}}.json`; namespace contains a slash, so the file path is `.../articles/optimization-continuity-algorithms.json` per language. Confirm whether the app uses `public/locales/` or `src/locales/` (or build-time copy) and add:
  - `sv`: meta (header.title, meta.description, meta.keywords), header (readTime, publishDate, author), section keys, references, navigation.
  - `en`: same structure.

### 2.4 Listing and nav

- **Articles listing** (`[apps/website/src/pages/Resurser/Articles.tsx](beta-appcaire/apps/website/src/pages/Resurser/Articles.tsx)`): Add a card for the new article (title, description, href via `getLocalizedPath("articles.optimizationContinuityAlgorithms", lang)`, reading time, category, tags: e.g. optimisation, continuity, algorithms, efficiency).
- **Nav** (`[apps/website/src/components/nav/navConfig.ts](beta-appcaire/apps/website/src/components/nav/navConfig.ts)`): In `resources.sections.articles.items`, add an entry for this article (label + href for sv/en) so it appears in the Resurser dropdown.

### 2.5 SEO and assets

- **Meta:** Swedish and English title/description targeting “optimisation”, “continuity”, “scheduling algorithms”, “efficiency”.
- **OG image:** Add or reuse an image (e.g. `public/images/og/articles/optimization-continuity-algorithms.jpg`) and reference it in PageSeo and Schema.org.
- **Sitemap:** If the site generates sitemap from routes, ensure the new path is included (or document that marketing/content plan should cover sitemap updates).

### 2.6 Content plan for marketing

- The **blog** is the existing **Resurser > Artiklar** section; this task adds the **first** article in the “algorithms & efficiency & continuity” theme.
- Document in a short note (e.g. in `docs/` or in the repo’s marketing area): “New article route and component pattern; add future posts by duplicating the article page + route + i18n + Articles card + nav item.” Optionally add a placeholder “Blog content plan” doc for marketing (only if you want a dedicated doc; otherwise the pattern is sufficient).

---

## Dependencies and order

```mermaid
flowchart LR
  A[Run deep research] --> B[Save report .md + .json]
  B --> C[Implement route + page + i18n]
  C --> D[Seed content from report + product docs]
  D --> E[Add to Articles list + nav]
  E --> F[SEO + OG image]
```



1. Run Part 1 (deep research); obtain and store the report.
2. Implement Part 2 using the report for content and references; use existing optimization docs and (if available) DARWIN input/memory for product alignment.

---

## Files to add


| Path                                                                               | Purpose                                             |
| ---------------------------------------------------------------------------------- | --------------------------------------------------- |
| `apps/website/src/pages/Resources/articles/optimization-continuity-algorithms.tsx` | New article page (SEO, structure, body, references) |
| Locale JSON (sv + en) for `articles/optimization-continuity-algorithms`            | Title, meta, sections, references copy              |
| Optional: OG image under `public/images/og/articles/`                              | Social preview                                      |


## Files to modify


| Path                                           | Change                                                           |
| ---------------------------------------------- | ---------------------------------------------------------------- |
| `apps/website/src/utils/routes.ts`             | Add `articles.optimizationContinuityAlgorithms` [svPath, enPath] |
| `apps/website/src/App.tsx`                     | Lazy import + route entries for the new article                  |
| `apps/website/src/i18n.ts`                     | Add namespace `articles/optimization-continuity-algorithms`      |
| `apps/website/src/pages/Resurser/Articles.tsx` | Add card for new article                                         |
| `apps/website/src/components/nav/navConfig.ts` | Add article item under resources.articles                        |


---

## Out of scope (for later)

- Dashboard or pipeline UI for schedule optimization (that’s in be-agents-service).
- Multiple new articles in one PR (only one article is added; pattern allows more).
- Automated ingestion of the research report into the page (content is authored in i18n/TSX using the report as source material).

