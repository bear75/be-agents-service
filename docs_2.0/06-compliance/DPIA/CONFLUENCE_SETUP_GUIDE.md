# Confluence Setup Guide for DPIA Documentation

**Purpose:** Step-by-step guide to create and populate DPIA documentation spaces in Confluence  
**Version:** 1.0  
**Date:** 2025-12-08  
**Target:** Caire team  
**Estimated Time:** 2-3 hours

---

## Overview: Two-Space Structure

We use **two separate Confluence spaces** to maintain clean separation between customer and investor due diligence:

1. **Caire – Customer Due Diligence (Home Care)** - For home care organizations (Attendo, etc.)
2. **Caire – Investor Due Diligence** - For investors

This separation ensures:

- ✅ No cross-audience data leakage
- ✅ Clear permission boundaries
- ✅ Easier access reviews and auditing
- ✅ Different content types per audience

---

## Prerequisites

- [ ] Confluence workspace access (https://caire.atlassian.net/wiki)
- [ ] Admin or Space Admin permissions
- [ ] All DPIA documents translated to English
- [ ] Google Drive backup created (see below)

---

## Step 1: Create Confluence Spaces

### 1.1 Create Space A – Customer Due Diligence

1. Go to https://caire.atlassian.net/wiki
2. Click **"Create"** → **"Space"**
3. Choose **"Team Space"**
4. Fill in:
   - **Name:** `Caire – Customer Due Diligence (Home Care)`
   - **Key:** `CAIRE-CUST-DD`
   - **Description:** `Due diligence documentation for home care organization customers (DPIA, security, operational procedures)`
   - **Visibility:** **Restricted** (only invited users)

### 1.2 Create Space B – Investor Due Diligence

1. Go to https://caire.atlassian.net/wiki
2. Click **"Create"** → **"Space"**
3. Choose **"Team Space"**
4. Fill in:
   - **Name:** `Caire – Investor Due Diligence`
   - **Key:** `CAIRE-INV-DD`
   - **Description:** `Investor data room with DPIA overview, technical documentation, financials, and roadmap`
   - **Visibility:** **Restricted** (only invited users)

### 1.3 Set Permissions

**Space A (Customer DD) Permissions:**

| Role            | Permission  | Users                                                     |
| --------------- | ----------- | --------------------------------------------------------- |
| **Space Admin** | Full access | EirTech CEO, EirTech Tech Lead                            |
| **Can Edit**    | Edit pages  | EirTech team members                                      |
| **Can View**    | View only   | Attendo Verksamhetschef, Attendo DSO, Attendo IT-Säkerhet |

**Space B (Investor DD) Permissions:**

| Role            | Permission  | Users                                   |
| --------------- | ----------- | --------------------------------------- |
| **Space Admin** | Full access | EirTech CEO, EirTech Tech Lead          |
| **Can Edit**    | Edit pages  | EirTech team members                    |
| **Can View**    | View only   | Specific investors (per investor group) |

**How to set:**

1. Go to Space Settings → Permissions
2. Add users/groups with appropriate permissions
3. **Restrict** to only authorized personnel
4. For Customer DD: Each customer subtree should be restricted to that customer + internal team

---

## Step 2: Create Page Structure - Space A (Customer DD)

### 2.1 Homepage Structure

**Space A:** `Caire – Customer Due Diligence (Home Care)`

**Homepage Content:**

```markdown
# Caire – Customer Due Diligence (Home Care)

Welcome to the Caire Customer Due Diligence space. This space contains DPIA documentation, security information, and operational procedures for home care organization customers.

## 📋 Structure

### Home Care Organizations

- [Attendo – DPIA & Due Diligence](Attendo-DPIA-Due-Diligence)
  - Complete DPIA package
  - Security & Architecture
  - Operational Procedures

- [Customer X – DPIA & Due Diligence](Customer-X-DPIA-Due-Diligence)
  - (Future customers)

### General Policies

- Standard security whitepaper
- Standard sub-processor list
- Generic policies reused across customers

## 🔒 Access Control

This space is **RESTRICTED** to:

- EirTech team members
- Authorized customer personnel (per customer)

## 📞 Contact

**Questions about DPIA:**  
Björn Evers (CEO)  
EirTech AB (Org. No. 559522-3800)  
Tändkulevägen 33, 131 58 Nacka, Sweden  
https://www.eirtech.ai/  
bjorn@caire.se  
+46734177166
```

### 2.2 Attendo Section Structure

Create under homepage:

**Page:** `Attendo – DPIA & Due Diligence`

**Child Pages:**

1. **DPIA** (main section)
   - DPIA Documentation – Overview
   - System Description
   - Data Inventory
   - Information Classification
   - DPIA Main Document
   - Risk Analysis
   - DPA Agreement Draft
   - RACI Matrix
   - Contractor Data Access Agreement
   - Internal Data Access Policy

2. **Security & Architecture**
   - (Future: Security whitepaper, architecture diagrams)

3. **Operational Procedures**
   - (Future: Support procedures, incident response)

---

## Step 3: Create Page Structure - Space B (Investor DD)

### 3.1 Homepage Structure

**Space B:** `Caire – Investor Due Diligence`

**Homepage Content:**

```markdown
# Caire – Investor Due Diligence

Welcome to the Caire Investor Data Room. This space contains technical documentation, DPIA overview, financials, roadmap, and investor-specific materials.

## 📋 Structure

### Shared Core Docs

- [Technical Overview](Technical-Overview)
- [DPIA Overview](DPIA-Overview) - Generic, non-customer-specific
- [Security & Compliance Overview](Security-Compliance-Overview)

### Investor Data Rooms

- [Investor A – Data Room](Investor-A-Data-Room)
- [Investor B – Data Room](Investor-B-Data-Room)

## 🔒 Access Control

This space is **RESTRICTED** to:

- EirTech team members
- Authorized investors (per investor group)

## 📞 Contact

**Questions:**  
Björn Evers (CEO)  
EirTech AB (Org. No. 559522-3800)  
bjorn@caire.se
```

### 3.2 Shared Core Docs

Create under homepage:

1. **Technical Overview** - Reuse parts of System Description (generic)
2. **DPIA Overview** - Generic DPIA summary without customer-specific details
3. **Security & Compliance Overview** - High-level security and compliance information

---

## Step 4: Import Markdown to Confluence

### Option A: Manual Copy/Paste (Recommended for First Time)

**For each document:**

1. Open the markdown file (e.g., `01_SYSTEM_DESCRIPTION.md`)
2. Copy all content
3. In Confluence, navigate to the correct space and create new page
4. Click **"Insert"** → **"Markup"** → **"Markdown"**
5. Paste content
6. Click **"Insert"**
7. Review formatting and adjust if needed

**Time per document:** ~5-10 minutes

### Option B: Confluence REST API (Automated)

**Setup script:**

```bash
# Install Python library
pip install atlassian-python-api
```

**Python script example:**

```python
from atlassian import Confluence
import markdown

# Initialize
confluence = Confluence(
    url='https://caire.atlassian.net',
    username='your-email@caire.se',
    password='your-api-token'  # Get from https://id.atlassian.com/manage-profile/security/api-tokens
)

# Convert markdown to Confluence storage format
def markdown_to_confluence(md_content):
    html = markdown.markdown(md_content)
    # Convert to Confluence storage format
    return html

# Upload page
def upload_page(space_key, parent_id, title, content):
    confluence.create_page(
        space=space_key,
        title=title,
        body=markdown_to_confluence(content),
        parent_id=parent_id,
        type='page'
    )

# Usage
with open('01_SYSTEM_DESCRIPTION.md', 'r') as f:
    content = f.read()
    upload_page('CAIRE-CUST-DD', parent_id, 'System Description', content)
```

**Get API Token:**

1. Go to https://id.atlassian.com/manage-profile/security/api-tokens
2. Click **"Create API token"**
3. Copy token (use as password in script)

---

## Step 5: Formatting Tips

### Tables

Confluence supports tables. Markdown tables will convert automatically.

### Code Blocks

Use Confluence's code macro:

```
{code:language=typescript}
// Your code here
{code}
```

### Diagrams

For Mermaid diagrams:

1. Install **"Mermaid for Confluence"** app (if available)
2. Or convert to images and upload
3. Or use Confluence's draw.io integration

### Links

- Internal links: `[Page Name]` or `[Display Text|Page Name]`
- External links: `[Display Text|https://example.com]`

---

## Step 6: Add Table of Contents

On each homepage, add Table of Contents macro:

1. Click **"Insert"** → **"Other macros"**
2. Search for **"Table of Contents"**
3. Insert macro
4. Configure:
   - **Heading levels:** 1-3
   - **Style:** Default

---

## Step 7: Export to PDF (Backup)

### 7.1 Export Individual Pages

1. Open page
2. Click **"..."** (More actions) → **"Export"** → **"PDF"**
3. Save to Google Drive

### 7.2 Export Entire Space

1. Go to Space Settings → **"Content Tools"** → **"Export"**
2. Choose **"PDF"**
3. Download and upload to Google Drive

---

## Step 8: Share with External Parties

### 8.1 Customer Space (Space A)

**Invite Attendo Users:**

1. Go to Space Settings → **"Permissions"**
2. Click **"Add users or groups"**
3. Add Attendo email addresses:
   - [Attendo Verksamhetschef email]
   - [Attendo DSO email]
   - [Attendo IT-Säkerhet email]
4. Set permission: **"Can View"**
5. Restrict to **"Attendo – DPIA & Due Diligence"** section only

**Send Invitation Email:**

```
Subject: Caire DPIA Documentation - Access Granted

Dear [Name],

You have been granted access to the Caire Customer Due Diligence space in Confluence.

Access: https://caire.atlassian.net/wiki/spaces/CAIRE-CUST-DD

This space contains:
- Complete DPIA documentation for Attendo
- Risk analysis
- Data Processing Agreement (draft)
- System architecture and data inventory

Please review the documentation before our DPIA workshop on [DATE].

If you have any questions, please contact:
Björn Evers, EirTech AB (Org. No. 559522-3800)
Tändkulevägen 33, 131 58 Nacka, Sweden
https://www.eirtech.ai/
bjorn@caire.se
+46734177166

Best regards,
EirTech AB Team
```

### 8.2 Investor Space (Space B)

**Invite Investors:**

1. Go to Space Settings → **"Permissions"**
2. Click **"Add users or groups"**
3. Add investor email addresses
4. Set permission: **"Can View"**
5. Optionally restrict to their specific data room section

---

## Step 9: Maintenance

### Regular Updates

**When to update:**

- After DPIA workshop (incorporate feedback)
- When new risks identified
- When security measures change
- Quarterly review
- When onboarding new customers/investors

**How to update:**

1. Update markdown files in repository
2. Copy/paste updated content to Confluence
3. Update version number in document header
4. Add entry to document history

### Version Control

Confluence automatically tracks versions:

- View history: Click **"..."** → **"Page history"**
- Restore previous version if needed

---

## Troubleshooting

### Issue: Markdown not rendering correctly

**Solution:**

- Use Confluence's native formatting instead
- Or use "Markdown" macro explicitly

### Issue: Tables look wrong

**Solution:**

- Recreate table using Confluence's table tool
- Or adjust markdown table formatting

### Issue: Diagrams not showing

**Solution:**

- Convert Mermaid to PNG/SVG
- Upload as image attachment
- Or use Confluence's draw.io integration

### Issue: Can't invite external users

**Solution:**

- Check if they have Atlassian account
- If not, they need to create one (free)
- Or use email sharing (less secure)

---

## Checklist

### Space Setup

- [ ] Space A created: `Caire – Customer Due Diligence (Home Care)` (Key: `CAIRE-CUST-DD`)
- [ ] Space B created: `Caire – Investor Due Diligence` (Key: `CAIRE-INV-DD`)
- [ ] Permissions set for both spaces (restricted)
- [ ] Homepages created with proper structure

### Customer DD Space (Space A)

- [ ] Homepage created
- [ ] "Attendo – DPIA & Due Diligence" section created
- [ ] All DPIA child pages created (11 pages)
- [ ] Content imported from markdown
- [ ] Formatting reviewed and corrected
- [ ] Table of Contents added
- [ ] Attendo users invited with restricted access

### Investor DD Space (Space B)

- [ ] Homepage created
- [ ] "Shared Core Docs" section created
- [ ] Technical Overview page created
- [ ] DPIA Overview page created (generic)
- [ ] Security & Compliance Overview page created
- [ ] Investor data room templates created

### Backup & Sharing

- [ ] PDF exports created for both spaces
- [ ] Google Drive backup uploaded
- [ ] Invitation emails sent to customers/investors

---

## Next Steps

1. ✅ Complete Confluence setup (two spaces)
2. ⏳ Populate Customer DD space with Attendo DPIA
3. ⏳ Create generic DPIA overview in Investor DD space
4. ⏳ Share Customer DD space with Attendo
5. ⏳ Schedule DPIA workshop
6. ⏳ Incorporate feedback
7. ⏳ Finalize DPIA
8. ⏳ Sign DPA

---

**Questions?** Contact Björn Evers (bjorn@caire.se)
