# Content Management Guide - CAIRE Website

## Overview

The CAIRE website uses a unified content management system that allows you to add new articles, guides, and comparisons without touching any code. All content is managed through markdown files and automatically appears in the appropriate feeds.

## Content Types & Locations

### 1. Articles (Blog Feed)

**Location:** `public/content/articles/`

- Swedish: `public/content/articles/sv/filename.md`
- English: `public/content/articles/en/filename.md`
- **Automatically appears in:** Resources → Blog feed

### 2. Guides

**Location:** `public/content/guides/`

- Swedish: `public/content/guides/sv/filename.md`
- English: `public/content/guides/en/filename.md`
- **Automatically appears in:** Resources → Guides feed

### 3. Comparisons

**Location:** `public/content/comparisons/`

- Swedish: `public/content/comparisons/sv/filename.md`
- English: `public/content/comparisons/en/filename.md`
- **Automatically appears in:** Resources → Comparisons feed

## How to Add New Content

### Step 1: Create the Markdown File

1. Navigate to the appropriate content directory
2. Create a new `.md` file with a descriptive filename (use kebab-case: `my-article-title.md`)
3. Create both Swedish and English versions

### Step 2: Markdown File Structure

Every content file must follow this exact structure:

```markdown
---
title: "Your Article Title"
description: "Brief description for SEO and previews"
keywords: "keyword1, keyword2, keyword3"
category: "articles" | "guides" | "comparisons"
publishDate: "2025-01-25"
author: "Author Name"
readTime: "5 min"
featured: false
---

# Your Article Title

Your content goes here...

## Section Headings

Use proper markdown formatting:

- **Bold text**
- _Italic text_
- [Links](https://example.com)
- Lists and bullet points

### Subsections

More content...
```

### Step 3: Required Frontmatter Fields

| Field         | Required | Description                     | Example                             |
| ------------- | -------- | ------------------------------- | ----------------------------------- |
| `title`       | ✅       | Article title                   | "AI Revolution in Home Care"        |
| `description` | ✅       | SEO description (150-160 chars) | "Discover how AI transforms..."     |
| `keywords`    | ✅       | SEO keywords (comma-separated)  | "AI, home care, scheduling"         |
| `category`    | ✅       | Content type                    | "articles", "guides", "comparisons" |
| `publishDate` | ✅       | Publication date                | "2025-01-25"                        |
| `author`      | ✅       | Author name                     | "CAIRE Team"                        |
| `readTime`    | ✅       | Estimated read time             | "5 min"                             |
| `featured`    | ❌       | Show in featured section        | true/false                          |

### Step 4: File Naming Convention

- Use kebab-case (lowercase with hyphens)
- Be descriptive but concise
- Match between Swedish and English versions

**Examples:**

- `ai-scheduling-revolution.md` (EN) ↔ `ai-schemalaggning-revolution.md` (SV)
- `cost-optimization-guide.md` (EN) ↔ `kostnadsoptimering-guide.md` (SV)

## Content Guidelines

### Writing Style

- **Swedish:** Professional but approachable tone
- **English:** Clear, concise, professional
- Use active voice
- Include practical examples
- Add call-to-actions where appropriate

### SEO Best Practices

1. **Title:** 50-60 characters, include primary keyword
2. **Description:** 150-160 characters, compelling summary
3. **Keywords:** 3-5 relevant keywords, avoid keyword stuffing
4. **Headings:** Use H2, H3 hierarchy properly
5. **Internal Links:** Link to other relevant content when appropriate

### Content Structure

1. **Introduction:** Hook the reader, state the problem/topic
2. **Main Content:** Break into digestible sections with clear headings
3. **Practical Examples:** Include real-world scenarios
4. **Conclusion:** Summarize key points
5. **Call-to-Action:** Guide reader to next steps

## Automatic Features

### What Happens Automatically

- ✅ Content appears in appropriate feed (articles/guides/comparisons)
- ✅ SEO meta tags generated from frontmatter
- ✅ Structured data (JSON-LD) added for search engines
- ✅ Responsive design applied
- ✅ Language switching works automatically
- ✅ Breadcrumb navigation generated
- ✅ Related content suggestions (if implemented)

### What You Don't Need to Do

- ❌ Update any code files
- ❌ Modify navigation menus
- ❌ Add routes or URLs
- ❌ Configure SEO settings
- ❌ Update sitemaps (auto-generated)

## Content Review Process

### Before Publishing

1. **Spell Check:** Use proper Swedish/English spelling
2. **Link Check:** Ensure all links work
3. **Image Check:** Verify all images load (if used)
4. **Preview:** Test in development environment
5. **SEO Check:** Verify title, description, keywords are optimized

### Quality Checklist

- [ ] Frontmatter complete and correct
- [ ] Title is compelling and SEO-friendly
- [ ] Description is under 160 characters
- [ ] Content is well-structured with proper headings
- [ ] No spelling or grammar errors
- [ ] Links work and are relevant
- [ ] Call-to-action is clear
- [ ] Both language versions are consistent

## Examples

### Article Example

```markdown
---
title: "5 Ways AI Improves Home Care Scheduling"
description: "Discover how artificial intelligence revolutionizes home care scheduling with these 5 proven strategies for better efficiency."
keywords: "AI scheduling, home care, efficiency, automation, care coordination"
category: "articles"
publishDate: "2025-01-25"
author: "CAIRE Team"
readTime: "7 min"
featured: true
---

# 5 Ways AI Improves Home Care Scheduling

Home care scheduling has traditionally been a complex puzzle...
```

### Guide Example

```markdown
---
title: "Complete Guide to Home Care Route Optimization"
description: "Step-by-step guide to optimizing home care routes for maximum efficiency and cost savings."
keywords: "route optimization, home care, efficiency, cost savings, planning"
category: "guides"
publishDate: "2025-01-25"
author: "CAIRE Team"
readTime: "12 min"
featured: false
---

# Complete Guide to Home Care Route Optimization

Route optimization is crucial for home care operations...
```

## Troubleshooting

### Common Issues

1. **Content not appearing:** Check frontmatter syntax
2. **Wrong category:** Verify category field matches folder
3. **SEO issues:** Ensure title and description are within character limits
4. **Language switching broken:** Check file naming consistency

### Getting Help

- Check existing content files for reference
- Validate markdown syntax online
- Test in development environment before publishing
- Contact development team for technical issues

---

**Remember:** The beauty of this system is its simplicity. Just create markdown files with proper frontmatter, and everything else happens automatically!
