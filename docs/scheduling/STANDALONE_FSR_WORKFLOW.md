# Standalone FSR Workflow (No Dashboard DB)

**Datum:** 2026-03-20  
**Syfte:** Komplett workflow för FSR solve utan dashboard-databasen

---

## Snabbstart

### Automatisk workflow (rekommenderat)

```bash
cd be-agent-service

# CSV → FSR JSON → Add shifts → Submit → Analyze
./scripts/compound/reseed-and-solve-fsr.sh \
  /path/to/huddinge-schedule.csv \
  --add-shifts 7 \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode \
  --wait
```

### Manuell workflow

```bash
# 1. Convert CSV to FSR JSON
python3 scripts/conversion/csv_to_fsr.py \
  huddinge-schedule.csv \
  -o input.json \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode

# 2. Add evening shifts
python3 scripts/conversion/add_evening_shifts_to_fsr.py \
  input.json \
  -o input_with_shifts.json \
  --count 7 \
  --start-date 2026-03-02 \
  --end-date 2026-03-15

# 3. Submit to Timefold
python3 scripts/timefold/submit.py solve input_with_shifts.json --wait --save output.json

# 4. Analyze results
python3 scripts/analytics/analyze_supply_demand.py output.json input_with_shifts.json
python3 scripts/analytics/metrics.py output.json
python3 scripts/continuity/report.py output.json
```

---

## Script-referens

### `add_evening_shifts_to_fsr.py`

**Syfte:** Lägger till extra kvällsskift direkt i FSR JSON (ingen databas).

**Användning:**
```bash
python3 scripts/conversion/add_evening_shifts_to_fsr.py input.json -o output.json [options]
```

**Options:**
- `--count <n>` - Antal extra kvällsskift att lägga till (default: 7)
- `--start-date <date>` - Planning start date (YYYY-MM-DD). Auto-detected if not provided
- `--end-date <date>` - Planning end date (YYYY-MM-DD). Auto-detected if not provided

**Exempel:**
```bash
# Lägg till 7 extra kvällsskift
python3 scripts/conversion/add_evening_shifts_to_fsr.py input.json -o output.json --count 7

# Lägg till 10 extra kvällsskift med explicit dates
python3 scripts/conversion/add_evening_shifts_to_fsr.py input.json -o output.json \
  --count 10 \
  --start-date 2026-03-02 \
  --end-date 2026-03-15
```

**Vad skapas:**
- N nya vehicles: `kvall_extra_1` till `kvall_extra_N`
- Shifts för varje dag i planning window (16:00-22:00)
- Totalt: N vehicles × antal dagar = N × 14 = 98 shifts (för 14 dagar)

**Output:**
- Ny FSR JSON med extra vehicles/shifts
- Metadata uppdaterad med `originalVehicleCount`, `addedEveningVehicles`, `totalVehicleCount`

### `reseed-and-solve-fsr.sh`

**Syfte:** Komplett workflow för FSR solve (standalone, ingen databas).

**Användning:**
```bash
./scripts/compound/reseed-and-solve-fsr.sh <csv-path> [options]
```

**Options:**
- `--add-shifts <count>` - Lägg till N extra kvällsskift (default: 7)
- `--start-date <date>` - Planning start date (YYYY-MM-DD, default: 2026-03-02)
- `--end-date <date>` - Planning end date (YYYY-MM-DD, default: 2026-03-15)
- `--no-geocode` - Hoppa över geocoding
- `--wait` - Vänta på att solve är klar

**Exempel:**
```bash
# Komplett workflow med 7 extra kvällsskift
./scripts/compound/reseed-and-solve-fsr.sh \
  /path/to/huddinge-schedule.csv \
  --add-shifts 7 \
  --start-date 2026-03-02 \
  --end-date 2026-03-15 \
  --no-geocode \
  --wait

# Utan extra shifts
./scripts/compound/reseed-and-solve-fsr.sh \
  /path/to/huddinge-schedule.csv \
  --add-shifts 0 \
  --no-geocode
```

**Vad görs:**
1. Konverterar CSV → FSR JSON (`csv_to_fsr.py`)
2. Lägger till extra kvällsskift (`add_evening_shifts_to_fsr.py`)
3. Skickar till Timefold (`submit.py`)
4. Ger instruktioner för analys

---

## Workflow-jämförelse

### Dashboard workflow (beta-appcaire)

```
CSV → Dashboard Upload → DB (Prisma) → Solve → DB (Results)
```

**Fördelar:**
- Data sparas i databasen
- Kan redigeras via dashboard
- Integration med andra features

**Nackdelar:**
- Kräver databas
- Långsammare för research/experiment

### Standalone workflow (be-agent-service)

```
CSV → FSR JSON → Add Shifts → Timefold → Analyze
```

**Fördelar:**
- Ingen databas krävs
- Snabbare för research/experiment
- Enklare att automatisera
- Kan köras i batch

**Nackdelar:**
- Ingen persistent lagring
- Ingen dashboard-integration

---

## Användningsfall

### Research/Experiment

**Använd standalone workflow:**
```bash
# Testa olika antal extra shifts
for count in 0 5 7 10; do
  ./scripts/compound/reseed-and-solve-fsr.sh \
    huddinge-schedule.csv \
    --add-shifts $count \
    --no-geocode
done
```

### Produktion

**Använd dashboard workflow:**
- Upload CSV via dashboard
- Solve via dashboard
- Resultat sparas i databasen

### Batch Processing

**Använd standalone workflow:**
```bash
# Processa flera CSV-filer
for csv in *.csv; do
  ./scripts/compound/reseed-and-solve-fsr.sh "$csv" --add-shifts 7 --wait
done
```

---

## Felsökning

### Problem: Script kan inte hitta planning window

**Lösning:**
- Använd `--start-date` och `--end-date` explicit
- Eller kontrollera att input JSON har shifts med korrekta dates

### Problem: Extra shifts läggs inte till

**Lösning:**
1. Kontrollera att input JSON är korrekt formaterad
2. Verifiera att `--count` är > 0
3. Kontrollera att `--start-date` och `--end-date` är korrekta

### Problem: Solve misslyckas

**Lösning:**
1. Kontrollera att FSR JSON är korrekt formaterad
2. Verifiera att Timefold API key är satt (`TIMEFOLD_API_KEY`)
3. Kontrollera att input inte är för stor (max vehicles/shifts)

---

## Relaterade filer

- `scripts/conversion/csv_to_fsr.py` - CSV → FSR JSON konvertering
- `scripts/conversion/add_evening_shifts_to_fsr.py` - Lägg till kvällsskift i FSR JSON
- `scripts/compound/reseed-and-solve-fsr.sh` - Komplett workflow script
- `scripts/timefold/submit.py` - Submit till Timefold
- `scripts/timefold/fetch.py` - Hämta solution från Timefold
- `scripts/analytics/analyze_supply_demand.py` - Supply/demand analys
- `scripts/analytics/metrics.py` - Metrics calculation
- `scripts/continuity/report.py` - Continuity report
