# Attendo Pilot Data Requirements Excel Template

## Overview

This Excel template (`Attendo_Pilot_Data_Requirements_Template.xlsx`) provides a comprehensive reference for all data fields required for the Attendo pilot, along with anonymized example rows demonstrating different use cases.

## File Structure

The Excel file contains the following sheets:

1. **Field Reference** - Complete list of all 54 fields with:
   - Field name
   - Data type
   - Required level (Yes/Recommended/Optional/Conditional)
   - Description
   - Color coding:
     - 🔴 Red = Required (Yes)
     - 🟠 Orange = Recommended
     - 🔵 Blue = Optional

2. **1_Unplanned_Only** - Example rows for unplanned visits (Option 1: Time Windows format)
3. **2_Unplanned_Flexibility** - Example rows for unplanned visits (Option 2: Original + Flexibility format)
4. **3_Planned_Only** - Example rows for planned visits only
5. **4_Unplanned_Planned** - Example rows showing both unplanned and planned data
6. **5_Planned_Actual** - Example rows showing planned vs actual comparison data

## Usage

### For Data Export

1. Open the Excel template
2. Review the **Field Reference** sheet to understand all available fields
3. Copy the example sheets as a starting point for your data export
4. Replace the anonymized example data with your actual data
5. Save as CSV for import into Caire

### Field Selection

- **Required fields** (marked in red) must be included
- **Recommended fields** (marked in orange) should be included when available
- **Optional fields** (marked in blue) can be included for enhanced optimization
- **Conditional fields** depend on the use case (e.g., time window fields are required for unplanned, but format differs)

### Time Format Options

The system supports two time format options:

**Option 1: Time Windows** (Direct Format)

- Use `visitMinStartTime`, `visitMaxStartTime`, `visitMaxEndTime`
- Best for precise time windows

**Option 2: Original + Flexibility**

- Use `originalStartTime`, `flexibilityMinutes`
- Best when you have a preferred time with flexibility

**Note**: Use either Option 1 or Option 2, not both.

## Regenerating the Template

To regenerate the Excel template:

```bash
node docs_2.0/09-scheduling/pilots/attendo/create_excel_template.js
```

Requires: `exceljs` package (installed as dev dependency)

## Related Documentation

- [DATA_REQUIREMENTS.md](./DATA_REQUIREMENTS.md) - Complete data requirements specification
- [PILOT_PLAN.md](./PILOT_PLAN.md) - Pilot plan and objectives
