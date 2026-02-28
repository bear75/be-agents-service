#!/usr/bin/env node
/**
 * Anonymizes visitId (=visitName) and vehicleId in a visits CSV.
 * Replaces real names with mock names: Client-001, Client-002, ... and Driver-01, Driver-02, ...
 *
 * Usage:
 *   node anonymize-visits-csv.mjs [--input path] [--output path]
 *   node anonymize-visits-csv.mjs --input huddinge.csv --output demo-data/source/huddinge_anonymized.csv
 *
 * Note: This script uses comma delimiter and column indices (0, 5, 15, 17).
 * For Huddinge format (semicolon), use scripts/anonymize_huddinge_to_demo.py.
 */

import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, ".");
const DEFAULT_INPUT = path.join(ROOT, "docs/docs_2.0/testing/visits-planned-12-14.csv");

const args = process.argv.slice(2);
const getArg = (name) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : null;
};
const INPUT = path.resolve(getArg("--input") || getArg("-i") || DEFAULT_INPUT);
const OUTPUT = path.resolve(getArg("--output") || getArg("-o") || INPUT);

function parseCsvLine(line) {
  const fields = [];
  let i = 0;
  while (i < line.length) {
    if (line[i] === '"') {
      let field = "";
      i++;
      while (i < line.length) {
        const c = line[i];
        const next = line[i + 1];
        if (c === '"') {
          if (next === '"') {
            field += '"';
            i += 2;
          } else if (next === "," || next === undefined || next === "\r" || next === "\n") {
            i++;
            break;
          } else {
            field += c;
            i++;
          }
        } else {
          field += c;
          i++;
        }
      }
      fields.push(field);
      if (line[i] === ",") i++;
    } else {
      let end = line.indexOf(",", i);
      if (end === -1) end = line.length;
      fields.push(line.slice(i, end).trim());
      i = end < line.length ? end + 1 : line.length;
    }
  }
  return fields;
}

function escapeCsvField(value) {
  if (value == null) return "";
  const s = String(value);
  if (s.includes(",") || s.includes('"') || s.includes("\n") || s.includes("\r")) {
    return '"' + s.replace(/"/g, '""') + '"';
  }
  return s;
}

function formatCsvRow(fields) {
  return fields.map(escapeCsvField).join(",");
}

const visitNames = [
  "Client-Alfa",
  "Client-Bravo",
  "Client-Charlie",
  "Client-Delta",
  "Client-Echo",
  "Client-Foxtrot",
  "Client-Golf",
  "Client-Hotel",
  "Client-India",
  "Client-Juliet",
  "Client-Kilo",
  "Client-Lima",
  "Client-Mike",
  "Client-November",
  "Client-Oscar",
  "Client-Papa",
  "Client-Quebec",
  "Client-Romeo",
  "Client-Sierra",
  "Client-Tango",
  "Client-Uniform",
  "Client-Victor",
  "Client-Whiskey",
  "Client-Xray",
  "Client-Yankee",
  "Client-Zulu",
];
const vehicleNames = [
  "Driver-01",
  "Driver-02",
  "Driver-03",
  "Driver-04",
  "Driver-05",
  "Driver-06",
  "Driver-07",
  "Driver-08",
  "Driver-09",
  "Driver-10",
  "Driver-11",
  "Driver-12",
  "Driver-13",
  "Driver-14",
  "Driver-15",
  "Driver-16",
  "Driver-17",
  "Driver-18",
  "Driver-19",
  "Driver-20",
];

function nextVisitName(visitMap) {
  const n = visitMap.size;
  if (n < visitNames.length) return visitNames[n];
  return "Client-" + String(n + 1).padStart(3, "0");
}

function nextVehicleName(vehicleMap) {
  const n = vehicleMap.size;
  if (n < vehicleNames.length) return vehicleNames[n];
  return "Driver-" + String(n + 1).padStart(2, "0");
}

if (!fs.existsSync(INPUT)) {
  console.error(`Error: Input not found: ${INPUT}`);
  process.exit(1);
}
const raw = fs.readFileSync(INPUT, "utf8");
const lines = raw.split(/\r?\n/).filter((l) => l.trim().length > 0);
const header = lines[0];
const rows = lines.slice(1);

const visitMap = new Map();
const vehicleMap = new Map();

const VISIT_ID_COL = 0;
const VISIT_NAME_COL = 5;
const VEHICLE_ID_COL = 15;
const VEHICLE_SHIFT_ID_COL = 17;

const outLines = [header];

for (const line of rows) {
  const fields = parseCsvLine(line);
  if (fields.length < 18) {
    outLines.push(line);
    continue;
  }
  const origVisit = (fields[VISIT_ID_COL] || "").trim();
  const origVehicle = (fields[VEHICLE_ID_COL] || "").trim();

  if (!visitMap.has(origVisit)) {
    visitMap.set(origVisit, nextVisitName(visitMap));
  }
  if (!vehicleMap.has(origVehicle)) {
    vehicleMap.set(origVehicle, nextVehicleName(vehicleMap));
  }

  fields[VISIT_ID_COL] = visitMap.get(origVisit);
  fields[VISIT_NAME_COL] = visitMap.get(origVisit);
  fields[VEHICLE_ID_COL] = vehicleMap.get(origVehicle);
  fields[VEHICLE_SHIFT_ID_COL] = vehicleMap.get(origVehicle);

  outLines.push(formatCsvRow(fields));
}

const outDir = path.dirname(OUTPUT);
if (!fs.existsSync(outDir)) {
  fs.mkdirSync(outDir, { recursive: true });
}
fs.writeFileSync(OUTPUT, outLines.join("\n") + "\n", "utf8");
console.log("Anonymized " + rows.length + " rows.");
console.log("Visit names: " + visitMap.size + " unique → Client-*");
console.log("Vehicle names: " + vehicleMap.size + " unique → Driver-*");
console.log("Wrote: " + OUTPUT);