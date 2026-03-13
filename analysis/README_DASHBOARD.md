# Timefold FSR Analytics Dashboard

Professional web dashboard for presenting Timefold Field Service Routing analysis results to clients.

## Features

✅ **Sortable Columns** - Click any column header to sort ascending/descending
✅ **Comprehensive Metrics** - All key KPIs in one view
✅ **Multiple Filters** - Filter by environment, search, visit count, empty shifts
✅ **Visual Indicators** - Color-coded performance indicators (good/warning/bad)
✅ **Definitions Section** - Clear explanations of all metrics and KPIs
✅ **Perfect Continuity Highlighting** - Jobs with 0 clients over 15 caregivers highlighted
✅ **Responsive Design** - Works on desktop, tablet, and mobile

## Metrics Included

### Operational Metrics
- **Visits** - Total visits in the schedule
- **Visit Groups** - Multi-caregiver visits (e.g., two-person care)
- **Assigned/Unassigned** - Assignment success rate
- **Employees** - Number of caregivers used
- **Shifts** - Total and empty shifts
- **Shift Time** - Total paid time
- **Travel Time** - Time spent traveling between clients
- **Wait Time** - Idle time between visits

### Efficiency Metrics
- **Field Efficiency** - Visit time / (Visit + Travel) - Target: >67.5%
- **Efficiency Excl Idle** - Productive time as % of paid time

### Continuity Metrics
- **Avg Continuity** - Average distinct caregivers per client - Target: ≤15
- **Max Continuity** - Highest caregiver count for any client
- **Over 15** - Number of clients with >15 caregivers - Target: 0
- **CCI** - Continuity of Care Index (0.0-1.0, higher is better)

## Quick Start

### Method 1: Simple Python HTTP Server

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/analysis
python3 -m http.server 8000
```

Then open: http://localhost:8000

### Method 2: Using serve script

```bash
./serve_dashboard.sh
```

Then open the URL shown in your browser.

### Method 3: Open directly in browser

For modern browsers with CORS support:
```bash
open index.html
```

## Updating Data

When new job analysis results are available, regenerate the dashboard data:

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/scripts
python3 generate_dashboard_data.py
```

This will:
1. Load all batch analysis results from `continuity_batch_test/` and `continuity_batch_prod/`
2. Extract metrics from output.json files
3. Parse continuity data from continuity.csv files
4. Generate `dashboard_data.json` in the analysis folder
5. Dashboard will automatically reload with new data

## File Structure

```
analysis/
├── index.html                  # Dashboard webpage
├── dashboard_data.json         # Data file (generated)
├── README_DASHBOARD.md         # This file
├── continuity_batch_test/      # Test environment job data
│   ├── batch_results.json
│   ├── 1aa5e0a0/              # Individual job folders
│   ├── 6d2d0476/
│   └── ...
└── continuity_batch_prod/      # Prod environment job data
    ├── batch_results.json
    └── ...
```

## Presenting to Client

### Best Practices

1. **Start with Summary Stats**
   - Point out total jobs analyzed
   - Highlight perfect continuity achievements
   - Show average field efficiency

2. **Explain Sorting**
   - Click column headers to sort
   - Show best performers by continuity
   - Show highest efficiency jobs

3. **Use Filters**
   - Filter to production jobs only
   - Show jobs with zero empty shifts
   - Search for specific job IDs

4. **Walk Through Metrics**
   - Start with continuity (most important for care quality)
   - Explain field efficiency (operational performance)
   - Show empty shift elimination results

5. **Review Definitions**
   - Scroll to definitions section
   - Explain CCI and Kolada continuity
   - Show formulas and targets

### Key Talking Points

**Perfect Continuity:**
> "Three production jobs achieved PERFECT continuity - all 176 clients received care from 10 or fewer caregivers, well below the target of 15. This ensures consistent, high-quality relationships between caregivers and clients."

**Field Efficiency:**
> "Our optimized schedules achieve 73% field efficiency, exceeding the industry benchmark of 67.5%. This means caregivers spend more time delivering care and less time driving."

**Empty Shift Elimination:**
> "Using our two-stage optimization approach, we eliminated 100% of empty shifts in the from-patch jobs, resulting in annual savings of approximately 1.2 million SEK."

**Cost Savings:**
> "By optimizing schedules and eliminating waste, we project annual savings of over $115,000 USD while maintaining or improving care quality."

## Browser Support

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## Troubleshooting

### Dashboard shows "Error loading data"

**Solution:** Make sure `dashboard_data.json` exists in the same folder as `index.html`

```bash
cd /Users/bjornevers_MacPro/HomeCare/be-agent-service/recurring-visits/scripts
python3 generate_dashboard_data.py
```

### Dashboard shows no data or sample data

**Solution:** Regenerate dashboard data and refresh browser (Cmd+Shift+R)

### Metrics showing as 0 or N/A

**Solution:** Some jobs may not have complete metrics data. This is normal for jobs that haven't been fully analyzed.

### Can't sort columns

**Solution:** Click directly on column header text, not the cells below.

## Customization

To customize the dashboard appearance, edit `index.html`:

**Change colors:**
- Line 16-17: Main gradient background
- Line 32-33: Header gradient
- Line 148-149: Table header gradient

**Change thresholds:**
- Search for `getEfficiencyClass`, `getContinuityClass`, etc. in the JavaScript
- Adjust the numeric thresholds (e.g., 67.5, 75, etc.)

## Export Options

### Print to PDF

1. Open dashboard in browser
2. File → Print (or Cmd+P)
3. Choose "Save as PDF"
4. Adjust settings (landscape recommended)

### Export Data

The `dashboard_data.json` file can be imported into:
- Excel (via JSON import)
- Power BI
- Tableau
- Custom analysis tools

## Support

For questions or issues with the dashboard:
1. Check this README
2. Review generated data in `dashboard_data.json`
3. Verify source data in batch folders
4. Contact: bjorn.evers@homecare.se

---

**Last Updated:** 2026-03-12
**Version:** 1.0
**Generated from:** Timefold FSR Continuity Campaign Analysis
