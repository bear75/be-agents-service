# Demo Data

Anonymized recurring visit data for testing and demos.

## Creating demo-data

Run from `docs_2.0/recurring-visits`:

**1. Anonymize source**

```bash
cd docs_2.0/recurring-visits
python scripts/anonymize_huddinge_to_demo.py <path-to-source-recurring.csv> \
  -o demo-data/source/source.csv
```

**2. Run pipeline**

```bash
python huddinge-package/process_huddinge.py --weeks 2 --output-dir demo-data --source-file source.csv
```

## Anonymization

- **Client IDs** → Client-001, Client-002, ...
- **Client names** → Client-XXX_1
- **Contact names** → Client-XXX
- **Shift/vehicle names** → Driver-01, Driver-02, ...
- **Addresses** → Anonymized Street Client-XXX (postal code and city preserved)

## Structure after creation

```
demo-data/
├── source/
│   └── source.csv
├── expanded/
│   └── demo_2wk_expanded_*.csv
├── solve/
│   └── input_*.json
└── README.md
```
