#!/usr/bin/env python3
"""
Produce a CSV with the same content as the original but Lat/Lon set to substitute
coordinates (not real Attendo locations). No anonymization: Gata, Postnr, Ort and
Beskrivning are left unchanged.

Reads:
  - Huddinge-v3 - Data.csv (original)
  - address_coordinates_anonymized.json (pool of substitute [lat, lon] points)

Writes:
  - Huddinge-v3 - Data-substitute-locations.csv (original text + Lat,Lon from pool)
"""
import csv
import json
import os
import sys


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_csv = os.path.join(script_dir, "Huddinge-v3 - Data.csv")
    coords_json = os.path.join(script_dir, "address_coordinates_anonymized.json")
    output_csv = os.path.join(script_dir, "Huddinge-v3 - Data-substitute-locations.csv")

    if not os.path.isfile(input_csv):
        print(f"Input CSV not found: {input_csv}", file=sys.stderr)
        sys.exit(1)
    if not os.path.isfile(coords_json):
        print(f"Coordinates JSON not found: {coords_json}", file=sys.stderr)
        sys.exit(1)

    with open(coords_json, "r", encoding="utf-8") as f:
        coords_data = json.load(f)
    # Ordered list of substitute [lat, lon]
    substitute_coords = [v for v in coords_data.values() if isinstance(v, list) and len(v) >= 2]
    if not substitute_coords:
        print("No coordinates in JSON.", file=sys.stderr)
        sys.exit(1)

    # Map each unique (Gata, Postnr, Ort) to a substitute coord (deterministic)
    location_to_coord = {}
    coord_index = [0]

    def get_substitute_coord(gata: str, postnr: str, ort: str):
        key = (gata.strip(), postnr.strip(), ort.strip())
        if key not in location_to_coord:
            lat, lon = substitute_coords[coord_index[0] % len(substitute_coords)]
            coord_index[0] += 1
            location_to_coord[key] = (float(lat), float(lon))
        return location_to_coord[key]

    with open(input_csv, "r", encoding="utf-8-sig", newline="") as f_in:
        reader = csv.DictReader(f_in)
        if reader.fieldnames is None:
            sys.exit(1)
        fieldnames = list(reader.fieldnames)
        if "Lat" not in fieldnames:
            fieldnames.append("Lat")
        if "Lon" not in fieldnames:
            fieldnames.append("Lon")

        rows = []
        for row in reader:
            gata = row.get("Gata", "")
            postnr = row.get("Postnr", "")
            ort = row.get("Ort", "")
            lat, lon = get_substitute_coord(gata, postnr, ort)
            row["Lat"] = f"{lat:.6f}"
            row["Lon"] = f"{lon:.6f}"
            rows.append(row)

    with open(output_csv, "w", encoding="utf-8", newline="") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Wrote {len(rows)} rows to {output_csv}")
    print(f"Assigned substitute coordinates for {len(location_to_coord)} unique locations (no anonymization).")


if __name__ == "__main__":
    main()
