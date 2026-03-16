# Model change governance (audit-redo)

Governance for changes to scheduling/optimisation models: RACI, change classes, sign-off rules, and CI-enforced metadata. Use for PRs that touch model artifacts, inference, or planning logic that affects care delivery.

---

## Filöversikt (vad som finns och var)

| Fil                                         | Plats                                   | Roll                                                                                                                                                                                                                                                                                                           |
| ------------------------------------------- | --------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **`.changespec.yml`**                       | **Repo-root**                           | Filen **skapas automatiskt** när du öppnar en PR som rör model paths och den saknas: workflow kopierar från mallen, committar och pushar. Du behöver bara redigera `change.classification` (minor/substantial/major) och ev. identifiers/risk. Vill du skapa den lokalt före push: kör `yarn changespec:init`. |
| `.github/changespec.example.yml`            | I repot                                 | Mall som workflow (eller `yarn changespec:init`) använder för att skapa `.changespec.yml`.                                                                                                                                                                                                                     |
| `.github/changespec.schema.json`            | I repot                                 | JSON-schema som validerar `.changespec.yml`. Används av workflow.                                                                                                                                                                                                                                              |
| `.github/workflows/changespec-validate.yml` | I repot                                 | Workflow "ChangeSpec governance": kräver `.changespec.yml` vid model-path-ändringar, validerar filen, kräver approval-labels.                                                                                                                                                                                  |
| `.github/scripts/validate-changespec.mjs`   | I repot                                 | Skript som validerar `.changespec.yml` mot schemat.                                                                                                                                                                                                                                                            |
| **Labels**                                  | GitHub → repo → **Issues** → **Labels** | Skapas manuellt i GitHub (inte filer). Krävs: `approved/dev`, `approved/architect` (2 sign-offs).                                                                                                                                                                                                              |

Ingen fil saknas i repot. **`.changespec.yml`** i root skapas antingen **automatiskt av workflow** (när du pushar modell-ändringar utan fil) eller med **`yarn changespec:init`** om du vill ha den lokalt före push.

---

## Roles (dev + architect)

| Role          | Responsibility                                           |
| ------------- | -------------------------------------------------------- |
| **Dev**       | Implementation, tests, technical description, risk log.  |
| **Architect** | Design review, impact assessment, sign-off before merge. |

All model-change PRs require **both** sign-offs (approved/dev + approved/architect labels).

---

## Change classes (audit only)

Classification in `.changespec.yml` (minor / substantial / major) is for **audit and traceability** only. The same two labels are required for every model change:

- **Minor:** Small tweaks (e.g. hyperparameter, UI exposure of existing inference).
- **Substantial:** New feature, data snapshot, or weight change affecting routes/planning.
- **Major:** New model class, risk profile, or data source with personal data.

---

## CI/CD – machine-executable metadata

Each PR that qualifies as a model change must include a `.changespec.yml` in the repo root (or path configured in CI). The pipeline:

- Validates the file against the JSON schema (`.github/changespec.schema.json`).
- Requires **both** approval labels: `approved/dev` and `approved/architect`. Merge is blocked until both are on the PR.

**Auto-add:** When the PR touches model paths and `.changespec.yml` is missing, the workflow creates it from the example, commits and pushes. This requires the organisation to allow **Read and write** workflow permissions (Settings → Actions → General). If push fails, run locally: `yarn changespec:init`, set `change.classification`, then commit and push.

See [.changespec.yml example](../../.github/changespec.example.yml) and [JSON schema](../../.github/changespec.schema.json).

---

## Pull request template (model changes)

For PRs that are classified as model changes, use the checklist below in addition to the standard PR template:

### Change summary

- What & why:

### Risk & impact

- Intended use / out-of-scope:
- Harms & mitigations:
- Rollback plan:

### Evidence

- Dataset snapshot: `...`
- Model artifact: `...`
- Test results link: `...`
- Baseline vs new: `metric Δ`, `p-value` (if relevant)

### Approvals (tick before merge)

- [ ] Dev sign-off → add label `approved/dev`
- [ ] Architect sign-off → add label `approved/architect`

---

## Test and evidence (minimum)

- **Technical regression:** Stability metrics, latency, cost, error rate.
- **Domain quality:** Metrics tied to home care (e.g. travel time, continuity, contractual/legal).
- **Clinical safety:** Checks for risk scenarios (e.g. missed visit, double-booking at night).
- **Data protection:** KPIs for data minimisation, retention, access logs.

---

## Audit trail (what reviewers expect)

- Sign-off chain from PR to deploy (person, time, comment).
- Immutable link **artifact ↔ dataset ↔ testsuite** (hashes).
- Classification rationale (why minor / substantial / major).
- Release protocol including canary outcome and any rollback.

---

## Automated governance (CI)

The **ChangeSpec governance** workflow (`.github/workflows/changespec-validate.yml`) runs on every PR and:

1. **Requires `.changespec.yml`** when the PR touches model/solver paths; if missing, the check fails with an instruction to run **`yarn changespec:init`**, set `change.classification`, then commit and push. (Auto-creation would require org to allow "Read and write" for Actions; if that option is greyed out, it is set by the organization.)
2. **Validates** `.changespec.yml` against the JSON schema and fails if invalid.
3. **Enforces approval labels:** merge is blocked until the PR has **both** `approved/dev` and `approved/architect`.

When the check fails, run **`yarn changespec:init`**, set `change.classification` (minor/substantial/major), commit and push.

### Required GitHub labels (create once in the repo)

Create these two labels in the repository (Settings → Labels) so reviewers can apply sign-off:

| Label                | Used for           |
| -------------------- | ------------------ |
| `approved/dev`       | Developer sign-off |
| `approved/architect` | Architect sign-off |

After each role has approved, add the corresponding label to the PR. The workflow checks that both labels are present.

### Branch protection (recommended)

To make governance mandatory before merge:

1. Go to Settings → Branches → Branch protection rules (e.g. for `main` and `development`).
2. Enable **Require status checks to pass before merging**.
3. In the box **"Search for status checks in the last week"**: GitHub visar bara checks som **redan har körts** i repot. Om rutan visar "No checks have been added":
   - Spara regeln (Create) **utan** att välja någon check, **eller**
   - Öppna först en PR (t.ex. mot `main`) så att workflow körs – då dyker **ChangeSpec governance** (och ev. **quality** från PR checks) upp i listan. Gå tillbaka till Settings → Branches → redigera regeln och lägg till check(s).
4. Välj **ChangeSpec governance** (och om du vill **quality** från `pr-checks.yml`).
5. Rekommenderat: kryssa i **Do not allow bypassing the above settings** så att även admins måste ha gröna checks.
6. Save. PRs will then be blocked until the selected checks pass.

### Extending model paths

If you add solver/optimisation logic under other directories, add their path prefixes to the workflow env `MODEL_PATH_PREFIXES` in `.github/workflows/changespec-validate.yml`. PRs that change files under those paths will then require `.changespec.yml` and the approval labels.

---

## Quick implementation checklist

1. Create the two approval labels in the repo: `approved/dev`, `approved/architect` (see above).
2. Enable branch protection and require the **ChangeSpec governance** workflow.
3. When you change model/solver code, add `.changespec.yml` (copy from `.github/changespec.example.yml`), set `classification`, and get dev + architect sign-offs; reviewers add the two labels.

---

## Relation to existing PR workflow

- General PR rules (size, branch naming, type-check, lint, test) remain in [.cursor/rules/pr-workflow.mdc](../../.cursor/rules/pr-workflow.mdc).
- Model-change PRs additionally require `.changespec.yml`, the model-change checklist above, and the approval labels enforced by the `changespec` workflow.
