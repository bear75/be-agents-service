#!/usr/bin/env python3
"""
Anonymize sensitive data in Attendo Huddinge CSV: locations (Gata, Postnr, Ort)
and Beskrivning. Leaves all other columns intact. Output: Huddinge-v3 - Data-anonymized.csv
"""
import csv
import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_path = os.path.join(script_dir, "Huddinge-v3 - Data.csv")
    output_path = os.path.join(script_dir, "Huddinge-v3 - Data-anonymized.csv")

    if not os.path.isfile(input_path):
        print(f"Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    # Map each unique (Gata, Postnr, Ort) to anonymized values (preserve grouping)
    location_map = {}
    location_counter = [0]

    def anonymize_location(gata, postnr, ort):
        key = (gata.strip(), postnr.strip(), ort.strip())
        if key not in location_map:
            location_counter[0] += 1
            n = location_counter[0]
            location_map[key] = (f"Adress {n}", "14xxx", "Anonym ort")
        return location_map[key]

    with open(input_path, "r", encoding="utf-8-sig", newline="") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None:
            sys.exit(1)
        fieldnames = list(reader.fieldnames)

        rows = []
        for row in reader:
            gata = row.get("Gata", "")
            postnr = row.get("Postnr", "")
            ort = row.get("Ort", "")
            a_gata, a_postnr, a_ort = anonymize_location(gata, postnr, ort)
            row["Gata"] = a_gata
            row["Postnr"] = a_postnr
            row["Ort"] = a_ort
            row["Beskrivning"] = "[Anonymiserad beskrivning]"
            rows.append(row)

    with open(output_path, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_path}")
    print(f"Anonymized {len(location_map)} unique locations.")

if __name__ == "__main__":
    main()
