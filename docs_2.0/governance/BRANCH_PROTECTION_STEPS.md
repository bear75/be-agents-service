# Branch protection – steg för steg (en gång per repo)

Målet: Git ska automatiskt stoppa merge tills alla checks är gröna. Du behöver bara göra detta **en gång** (eller när du lägger till en ny skyddad branch).

---

## Om du rör model paths (dashboard-server, benchmarks-server)

Workflow **kräver** då att `.changespec.yml` finns. Skapa den med: **`yarn changespec:init`**, sätt `change.classification`, committa och pusha. (Automatisk skapande kräver att org tillåter "Read and write" för Actions – om det är nedtonat är det org-policy.)

---

## Steg 1: Se till att workflows har körts

GitHub visar bara status checks som **redan har körts** i repot. Om du inte sett dem än:

1. Öppna en **Pull request** mot `main` (valfri branch med ändringar).
2. Vänta tills **Actions** har körts (gröna eller röda – det räcker att de körts).
3. Då dyker check-namnen upp i inställningarna i steg 2.

---

## Steg 2: Sätt branch protection för `main`

1. Gå till repot på GitHub → **Settings** (fliken högst upp).
2. Vänstermeny: klicka **Branches** (under "Code and automation").
3. Under "Branch protection rules" → klicka **Add rule** (eller redigera befintlig regel för `main`).
4. **Branch name pattern:** skriv `main`.
5. Kryssa i:
   - **Require a pull request before merging** (välj t.ex. 1 approval om du vill).
   - **Require status checks to pass before merging**.
6. Klicka **i den tomma rutan** under "Require status checks to pass before merging" – det är en **sökruta**. Skriv t.ex. `ChangeSpec` eller `quality`. Om workflows har körts ska förslag dyka upp; välj:
   - **ChangeSpec governance**
   - **quality** (från PR checks)
7. (Rekommenderat) Kryssa i **Do not allow bypassing the above settings**.
8. Klicka **Create** eller **Save changes**.

Därefter kan ingen merga till `main` förrän dessa checks är gröna.

---

## Vad du inte behöver förstå

- Du behöver inte förstå YAML, workflows eller "refs". Det räcker att följa stegen ovan.
- När du bygger features: gör ändringar, push till en branch, öppna PR. Om något check blir rött visar GitHub vad som saknas (t.ex. "Add .changespec.yml" eller "Fix lint"). Fixa det och pusha igen.

---

## Kort sammanfattning

| Du gör                                        | Git/CI gör                                                     |
| --------------------------------------------- | -------------------------------------------------------------- |
| Skriver kod, pushar till en branch, öppnar PR | Kör type-check, lint, test, ChangeSpec-validering              |
| Fixar det CI klagar på (om något är rött)     | Blir grön när allt stämmer                                     |
| Någon med behörighet godkänner PR             | Merge till main blockeras tills checks är gröna + ev. approval |

När branch protection är satt kan du lägga till features utan att behöva tänka på "git governance" – workflow sköter det.
