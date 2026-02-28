# Metrics-varianter (28-feb)

Alla körningar har räknats om med två varianter för hur skifttimmar och idle hanteras.

## Var finns rapporterna?

För varje dataset (t.ex. `203cf1d6/`):

- **`metrics/`** – ursprunglig rapport (alla skift enl. schema, idle inkl. tomma skift och slutet av skift).
- **`metrics/variant1/`** – Variant 1: endast helt tomma skift borttagna.
- **`metrics/variant2/`** – Variant 2: variant 1 + tomma delar i skift borttagna (visit-span).
- **`continuity.csv`** – kontinuitet (distinct vårdgivare per klient); oförändrad mellan varianterna.

## Hur idle räknas ut

**Utgångsläge (default):**  
Skifttid = schemalagd längd för alla skift.  
Idle = skift − (besök + resa + väntan + rast). Inkluderar helt tomma skift och tom tid efter sista besök till skiftslut.

**Variant 1** (`--exclude-empty-shifts-only`):  
- Helt tomma skift och tomma medarbetare bidrar **0** skifttimmar.  
- Skifttimmar = endast skift som har minst ett besök (enligt schema längd).  
- Idle = skift − (besök + resa + väntan + rast); **inkl. tom tid i slutet av skift** (efter sista besök).

**Variant 2** (`--visit-span-only`):  
- Som variant 1.  
- Dessutom: varje skift med besök räknas endast från **första besök start** till **sista besök slut** (ingen tom tid efter sista besök; rast efter sista besök räknas inte).  
- Idle = **0** (inga helt tomma skift, inga tomma delar i skift).

## Kommandon (från `docs_2.0/recurring-visits/scripts`)

```bash
# Variant 1
python3 metrics.py ../huddinge-package/huddinge-datasets/28-feb/<id>/output.json \
  --input ../huddinge-package/huddinge-datasets/28-feb/<id>/input.json \
  --exclude-empty-shifts-only --save ../huddinge-package/huddinge-datasets/28-feb/<id>/metrics/variant1

# Variant 2
python3 metrics.py ../huddinge-package/huddinge-datasets/28-feb/<id>/output.json \
  --input ../huddinge-package/huddinge-datasets/28-feb/<id>/input.json \
  --visit-span-only --save ../huddinge-package/huddinge-datasets/28-feb/<id>/metrics/variant2
```

## Kontinuitet

Kontinuitet (antal distinkta vårdgivare per klient) beror bara på besök→fordon→klient och är **samma** för alla varianter. Filen `continuity.csv` i varje dataset används oförändrad.
