# Data Integration Documentation

This directory contains all documentation for data integration, seeding, and backup processes in the AppCaire platform.

## Quick Start

- **Need to seed data?** → See [SEEDING_GUIDE.md](./SEEDING_GUIDE.md)
- **Need architecture overview?** → See [COMPLETE_SEED_ARCHITECTURE.md](./COMPLETE_SEED_ARCHITECTURE.md)
- **Need to backup/restore?** → See [../../local/BACKUP_README.md](../../local/BACKUP_README.md)

## Core Documentation

### Architecture & System Design

| Document                                                         | Description                         | When to Use                      |
| ---------------------------------------------------------------- | ----------------------------------- | -------------------------------- |
| [COMPLETE_SEED_ARCHITECTURE.md](./COMPLETE_SEED_ARCHITECTURE.md) | Complete seed system architecture   | Understanding the overall system |
| [DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md)             | Database schema and data structures | Understanding data models        |
| [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md)                   | Seed system design and patterns     | Building new seed scripts        |

### Guides & Procedures

| Document                                               | Description                           | When to Use                             |
| ------------------------------------------------------ | ------------------------------------- | --------------------------------------- |
| [SEEDING_GUIDE.md](./SEEDING_GUIDE.md)                 | **Main guide** - How to seed all data | Daily seeding operations                |
| [DEDUPLICATION_GUIDE.md](./DEDUPLICATION_GUIDE.md)     | Provider deduplication process        | Merging duplicate providers             |
| [EMPLOYEE_DATA.md](./EMPLOYEE_DATA.md)                 | Employee data sources and seeding     | Working with employee data              |
| [SCB_COMPLETE_GUIDE.md](./SCB_COMPLETE_GUIDE.md)       | SCB data integration                  | Working with SCB statistics             |
| [INDIKATOR_INTEGRATION.md](./INDIKATOR_INTEGRATION.md) | Indikator.org survey data             | Quality indicators from Socialstyrelsen |

## Data Sources

### Primary Sources

1. **Jens Nylander** (kommun.jensnylander.com)
   - Financial data, employee counts, presences
   - See: [EMPLOYEE_DATA.md](./EMPLOYEE_DATA.md)

2. **SCB** (Statistics Sweden)
   - National statistics, demographics
   - See: [SCB_COMPLETE_GUIDE.md](./SCB_COMPLETE_GUIDE.md)

3. **Socialstyrelsen**
   - Quality metrics, customer satisfaction
   - Indikator.org survey data
   - See: [INDIKATOR_INTEGRATION.md](./INDIKATOR_INTEGRATION.md)

4. **TIC.io**
   - Financial data enrichment
   - Requires API key

### Data Files Location

All seed data files are stored in:

```
apps/stats-server/src/seed-scripts/seed-data/
```

Marketing data and credentials:

```
docs/docs-seo/04-data-integration/marketing-data/
```

## Seed Scripts Overview

Seed scripts are located in `apps/stats-server/src/seed-scripts/`

### Core Seed Scripts (Run in order)

| Script                             | Purpose                     | Runtime |
| ---------------------------------- | --------------------------- | ------- |
| `01-seed-national-statistics.ts`   | National statistics         | ~1s     |
| `02-seed-municipalities.ts`        | Municipality data           | ~2s     |
| `03-seed-providers-unified.ts`     | Provider base data          | ~5s     |
| `05-seed-provider-satisfaction.ts` | Quality metrics             | ~3s     |
| `06-seed-quality-summaries.ts`     | Quality aggregations        | ~2s     |
| `07-seed-hemtjanstindex.ts`        | Hemtjänstindex rankings     | ~2s     |
| `08-calculate-rankings.ts`         | Calculate provider rankings | ~10s    |

### Data Enrichment Scripts

| Script                         | Purpose                      | Source     |
| ------------------------------ | ---------------------------- | ---------- |
| `29-seed-jens-scraped-data.ts` | Jens Nylander data           | JSON files |
| `14-seed-scb-data.ts`          | SCB statistics               | CSV files  |
| `31-seed-corporate-groups.ts`  | Corporate group aggregations | Database   |
| `19-seed-sync-counts.ts`       | Sync aggregations            | Database   |

## Backup & Restore

### Backup Process

```bash
cd local
./backup-seed-data.sh
```

See: [../../local/BACKUP_README.md](../../local/BACKUP_README.md)

### Backup Location

```
local/backups/
├── seed-data-backup-YYYY-MM-DD-HHMMSS.tar.gz  # Data files
└── seed-data-db-backup-YYYY-MM-DD-HHMMSS.sql  # Database dump
```

### Restore Process

```bash
cd local
tar -xzf backups/seed-data-backup-YYYY-MM-DD-HHMMSS.tar.gz -C ../apps/stats-server/src/seed-scripts/seed-data/

# Restore database
psql $DATABASE_URL < backups/seed-data-db-backup-YYYY-MM-DD-HHMMSS.sql
```

## Common Operations

### Full Reseed

```bash
# 1. Reset database
yarn workspace stats-server db:migrate reset

# 2. Run all seed scripts
yarn workspace stats-server db:seed
```

### Update Specific Data

```bash
# Update employee data
yarn workspace stats-server db:seed:29-jens-scraped
yarn workspace stats-server db:seed:31-corporate-groups

# Update quality metrics
yarn workspace stats-server db:seed:05-provider-satisfaction
yarn workspace stats-server db:seed:06-quality-summaries

# Recalculate rankings
yarn workspace stats-server db:seed:08-calculate-rankings
```

### Verify Data

```bash
# Check provider counts
yarn workspace stats-server db:seed:00-verify-database-integrity

# GraphQL query test
curl -X POST http://localhost:4005/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ providers { id name } }"}' | jq '.data.providers | length'
```

## Troubleshooting

### Common Issues

**Issue:** Seed script fails with "duplicate key"

- **Solution:** Run `yarn workspace stats-server db:migrate reset` first

**Issue:** Missing data files

- **Solution:** Restore from backup (see BACKUP_README.md)

**Issue:** Slow performance

- **Solution:** Increase database connection pool size in `.env`

**Issue:** Out of memory

- **Solution:** Process data in batches (see seed script patterns)

## Development

### Adding New Data Sources

1. Create data directory in `seed-data/XX-new-source/`
2. Create seed script `XX-seed-new-source.ts`
3. Follow patterns in [SEED_SYSTEM_GUIDE.md](./SEED_SYSTEM_GUIDE.md)
4. Update this README
5. Test thoroughly
6. Add backup documentation

### Testing Seed Scripts

```bash
# Test single script
yarn workspace stats-server tsx src/seed-scripts/XX-seed-script.ts

# Test with fresh database
yarn workspace stats-server db:migrate reset
yarn workspace stats-server db:seed
```

## Data Quality

### Quality Checks

- Deduplication: [DEDUPLICATION_GUIDE.md](./DEDUPLICATION_GUIDE.md)
- Employee data validation: [EMPLOYEE_DATA.md](./EMPLOYEE_DATA.md)
- Municipality data completeness: [DATA_STRUCTURE_GUIDE.md](./DATA_STRUCTURE_GUIDE.md)

### Monitoring

- Check logs in `apps/stats-server/logs/`
- GraphQL playground: http://localhost:4005/graphql
- Database admin tools (Prisma Studio): `yarn workspace stats-server db:studio`

## Support

For questions or issues:

1. Check relevant guide in this directory
2. Check [SEEDING_GUIDE.md](./SEEDING_GUIDE.md) for common operations
3. Review seed script source code
4. Check backup documentation in `local/BACKUP_README.md`

## Archive

Old documentation and debug files have been archived or removed. For historical reference, see git history.
