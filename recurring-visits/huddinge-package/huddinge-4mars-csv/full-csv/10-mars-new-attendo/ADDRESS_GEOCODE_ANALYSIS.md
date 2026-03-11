# Address cleanup and geocoding analysis

## Failing addresses (before fix)

Two addresses failed lookup when running `add_coordinates_to_csv.py` because the **lookup key** produced by the pipeline did not match any key in `address_coordinates.json`.

| CSV Gata (example) | Postnr | Ort | Normalized lookup key | Reason |
|--------------------|--------|-----|------------------------|--------|
| GRAN BACKEN 19 | 14131 | HUDDINGE | `granbacken 19, 14131 huddinge, sweden` | `_normalize_gata` merges space before "backen" → "GRANbacken 19". JSON had `gran backen 19,...` (with space). |
| PATRON PEHRS VÄG 36 LGH 1101 | 14135 | HUDDINGE | `patron pehrsväg 36, 14135 huddinge, sweden` | Same: " VÄG" is merged to "väg" → "pehrsväg". JSON had `patron pehrs väg 36,...`. |

The script `attendo_4mars_to_fsr.py` (and thus `add_coordinates_to_csv.py`) builds the address with `_address_string_4mars` and looks up with `_normalize_address_for_fallback_lookup(addr)`. Street suffixes like " backen" and " vägen" are merged into the previous word, so the key has no space (e.g. `granbacken`, `pehrsväg`). The JSON had been built with keys that kept the space.

## Fixes applied

1. **address_coordinates.json**  
   Added the two missing lookup keys with the same coordinates as the existing variants:
   - `granbacken 19, 14131 huddinge, sweden` → same coords as `gran backen 19, ...`
   - `patron pehrsväg 36, 14135 huddinge, sweden` → same coords as `patron pehrs väg 36, ...`

2. **Data CSV cleanup** (`cleanup_addresses_in_csv.py`)  
   - **Gata:** strip, collapse multiple spaces to one, remove trailing comma (e.g. `"URBERGS VÄGEN 31,"` → `URBERGS VÄGEN 31`).
   - **Postnr:** remove spaces (e.g. `141 44` → `14144`).  
   Run: `python cleanup_addresses_in_csv.py "huddinge-81-clients - Data.csv"`

3. **Regenerate with-coords CSV**  
   After cleanup and JSON update:
   ```bash
   python add_coordinates_to_csv.py "10-mars-new-attendo/huddinge-81-clients - Data.csv" \
     --coordinates "10-mars-new-attendo/address_coordinates.json" \
     -o "10-mars-new-attendo/huddinge-81-clients-with-coords.csv"
   ```
   Result: all 614 rows have Lat/Lon; no missing addresses.

## Pipeline order

1. Clean the Data CSV (Gata, Postnr) with `cleanup_addresses_in_csv.py`.
2. Ensure `address_coordinates.json` contains keys that match the **normalized** address string (lowercase, suffix-merged). Add aliases if the script produces a different key (e.g. `granbacken` vs `gran backen`).
3. Run `add_coordinates_to_csv.py` to produce `huddinge-81-clients-with-coords.csv`.
4. Use the with-coords CSV for dashboard seed or `attendo_4mars_to_fsr.py` (with `--no-geocode` when all rows have Lat/Lon).
