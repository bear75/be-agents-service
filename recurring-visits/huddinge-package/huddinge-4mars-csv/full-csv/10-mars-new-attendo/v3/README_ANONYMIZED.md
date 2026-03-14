# Anonymized Huddinge v3 data (testing only)

Sensitive data (locations and Beskrivning) in the Attendo CSV has been anonymized for safe use in scripts and CI.

## Files

| File | Purpose |
|------|---------|
| `Huddinge-v3 - Data-anonymized.csv` | Same structure as original; Gata/Postnr/Ort → "Adress N", "14xxx", "Anonym ort"; Beskrivning → "[Anonymiserad beskrivning]". |
| `address_coordinates_anonymized.json` | Dummy lat/lon for Adress 1–110 (required by FSR script; no real geocoding). |
| `fsr_input_anonymized.json` | Timefold FSR modelInput produced by the scripts flow from the anonymized CSV. |

## Regenerate anonymized CSV

From this directory:

```bash
python3 anonymize_csv.py
```

Requires original `Huddinge-v3 - Data.csv` in the same folder (do not commit the original).

## Test scripts flow (CSV → FSR JSON)

From `huddinge-package/huddinge-4mars-csv/scripts/`:

```bash
python3 attendo_4mars_to_fsr.py \
  "../full-csv/10-mars-new-attendo/v3/Huddinge-v3 - Data-anonymized.csv" \
  -o "../full-csv/10-mars-new-attendo/v3/fsr_input_anonymized.json" \
  --start-date 2026-03-02 --end-date 2026-03-15 \
  --address-coordinates "../full-csv/10-mars-new-attendo/v3/address_coordinates_anonymized.json"
```

Without `--address-coordinates` the script would try to geocode "Adress N, 14xxx Anonym ort" and fail. The JSON coordinates file supplies dummy positions so the pipeline runs end-to-end.

## Regenerate dummy coordinates (if you add more anonymized addresses)

If you change the anonymization and get more than 110 unique locations, recreate the coordinates file, e.g.:

```bash
cd "v3"
python3 -c "
import json
N = 110  # set to your number of unique addresses
coords = {f'Adress {n}, 14xxx Anonym ort, Sweden': [59.2 + (n % 20) * 0.01, 18.0 + (n % 15) * 0.01] for n in range(1, N + 1)}
with open('address_coordinates_anonymized.json', 'w', encoding='utf-8') as f:
    json.dump(coords, f, indent=0)
"
```
