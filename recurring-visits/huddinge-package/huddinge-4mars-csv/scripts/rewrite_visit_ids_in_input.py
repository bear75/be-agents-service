#!/usr/bin/env python3
"""
Rewrite visit id and name in an existing FSR input JSON to the new scheme:
  id:   {kundnr}_r{row_index}_{counter}  (e.g. H015_r0_1)
  name: from old name (strip trailing date) or "{kundnr} Besök {counter}" fallback.

For full name "H015 Morgon Dag Tillsyn" (Kundnr + När + Skift + Insatser) you must
generate input from CSV: attendo_4mars_to_fsr.py (with geocoding) produces that.
This script only rewrites existing input; reference often has "H015 Morgon 2026-03-02".
"""

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Tuple


def _kundnr_and_num(old_id: str) -> Tuple[str, int]:
    """Parse H015_1 -> (H015, 1), H053_r102_2 -> (H053, 2)."""
    if not old_id:
        return ("", 0)
    # Prefer pattern Kundnr_num (e.g. H015_1)
    m = re.match(r"^([A-Za-z0-9]+)_(\d+)$", old_id)
    if m:
        return (m.group(1), int(m.group(2)))
    # Already new style H053_r102_2 -> use as-is for kundnr, last number as counter
    m2 = re.match(r"^([A-Za-z0-9]+)_r\d+_(\d+)$", old_id)
    if m2:
        return (m2.group(1), int(m2.group(2)))
    return (old_id, 0)


def _name_from_old(old_name: str, kundnr: str, occ_index: int) -> str:
    """Prefer old name with trailing date stripped (e.g. 'H015 Morgon 2026-03-02' -> 'H015 Morgon')."""
    if not old_name or not isinstance(old_name, str):
        return f"{kundnr} Besök {occ_index}"
    # Strip trailing date YYYY-MM-DD so "H015 Morgon 2026-03-02" -> "H015 Morgon"
    without_date = re.sub(r"\s+\d{4}-\d{2}-\d{2}\s*$", "", old_name.strip()).strip()
    return without_date if without_date else f"{kundnr} Besök {occ_index}"


def _build_old_to_new_mapping(visits: List[Dict[str, Any]]) -> Dict[str, Tuple[str, str]]:
    """
    Build mapping old_id -> (new_id, new_name).
    Deterministic: sort by (kundnr, old_id), assign row_index by unique kundnr, counter per kundnr.
    Name: from visit's old name (strip trailing date); fallback "{kundnr} Besök {occ}".
    """
    # Collect (old_id, kundnr, num, old_name) and sort by (kundnr, old_id)
    items: List[Tuple[str, str, int, str]] = []
    for v in visits:
        old_id = (v.get("id") or "").strip()
        old_name = (v.get("name") or "").strip()
        kundnr, num = _kundnr_and_num(old_id)
        items.append((old_id, kundnr, num, old_name))
    items.sort(key=lambda x: (x[1], x[2], x[0]))

    kundnr_to_row: Dict[str, int] = {}
    mapping: Dict[str, Tuple[str, str]] = {}
    for old_id, kundnr, num, old_name in items:
        if kundnr not in kundnr_to_row:
            kundnr_to_row[kundnr] = len(kundnr_to_row)
        row = kundnr_to_row[kundnr]
        same_kundnr = [it for it in items if it[1] == kundnr]
        occ_index = next(i for i, it in enumerate(same_kundnr, 1) if it[0] == old_id)
        new_id = f"{kundnr}_r{row}_{occ_index}"
        new_name = _name_from_old(old_name, kundnr, occ_index)
        mapping[old_id] = (new_id, new_name)
    return mapping


def _rewrite_visits(
    visits: List[Dict[str, Any]],
    mapping: Dict[str, Tuple[str, str]],
) -> None:
    """Mutate visits: replace id and name using mapping."""
    for v in visits:
        old_id = (v.get("id") or "").strip()
        if old_id in mapping:
            new_id, new_name = mapping[old_id]
            v["id"] = new_id
            v["name"] = new_name


def _rewrite_dependencies(
    visits: List[Dict[str, Any]],
    mapping: Dict[str, Tuple[str, str]],
) -> None:
    """Replace visitId / precedingVisit in dependencies with new id."""
    for v in visits:
        for key in ("dependencies", "visitDependencies"):
            deps = v.get(key) or []
            for d in deps:
                if isinstance(d, dict):
                    if "visitId" in d and d["visitId"] in mapping:
                        d["visitId"] = mapping[d["visitId"]][0]
                    if "precedingVisit" in d and d["precedingVisit"] in mapping:
                        d["precedingVisit"] = mapping[d["precedingVisit"]][0]


def rewrite_input(input_path: Path, output_path: Path) -> Dict[str, Any]:
    """
    Load FSR input JSON, rewrite visit id/name to new scheme, write output.
    Returns the rewritten payload.
    """
    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    model = data.get("modelInput") or data
    standalone: List[Dict[str, Any]] = model.get("visits") or []
    groups: List[Dict[str, Any]] = model.get("visitGroups") or []

    all_visits: List[Dict[str, Any]] = list(standalone)
    for g in groups:
        all_visits.extend(g.get("visits") or [])

    if not all_visits:
        raise ValueError("No visits found in input")

    mapping = _build_old_to_new_mapping(all_visits)
    # mapping is old_id -> (new_id, new_name). We need to apply to visits and to dependency refs
    _rewrite_visits(all_visits, mapping)
    _rewrite_dependencies(all_visits, mapping)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return data


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Rewrite visit id/name in FSR input to new scheme (kundnr_r{row}_{occ})"
    )
    parser.add_argument("input", type=Path, help="Input JSON (reference or current export)")
    parser.add_argument("-o", "--output", type=Path, help="Output JSON path")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: not found: {args.input}", file=__import__("sys").stderr)
        return 1

    out = args.output or args.input.parent / (args.input.stem + "_newids.json")
    rewrite_input(args.input, out)
    print(f"Wrote: {out}", file=__import__("sys").stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
