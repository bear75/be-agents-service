# File Structure

## Overview

The project follows a modular structure optimized for scalability and maintainability. Below is the detailed file structure with explanations for each directory.

```
caire/
├── docs/                       # Project documentation
│   ├── analytics.md           # Analytics implementation details
│   ├── file-structure.md      # This file
│   ├── frontend-guidelines.md # Frontend development guidelines
│   └── seo-context.md        # SEO implementation details
│
├── public/                    # Static assets
│   ├── images/               # Image assets
│   │   ├── articles/        # Article images
│   │   ├── features/        # Feature images
│   │   └── icons/          # Icon assets
│   └── fonts/               # Font files
│
├── src/                      # Source code
│   ├── components/          # Reusable components
│   │   ├── ui/             # UI components
│   │   ├── animations/     # Animation components
│   │   ├── layout/         # Layout components
│   │   └── seo/            # SEO components
│   │
│   ├── content/            # Content files
│   │   └── articles/       # Article markdown files
│   │       ├── ai-schemaläggning-revolution.md
│   │       ├── framtidens-hemtjanst-trender.md
│   │       ├── implementeringsguide.md
│   │       └── steg-for-steg-ai-schemaläggning.md
│   │
│   ├── hooks/             # Custom React hooks
│   │   ├── use-seo.ts
│   │   └── usePageTracking.ts
│   │
│   ├── lib/              # Utility libraries
│   │   ├── analytics.ts
│   │   ├── error-tracking.ts
│   │   └── utils.ts
│   │
│   ├── pages/            # Page components
│   │   ├── Resurser/     # Resource pages
│   │   │   ├── index.tsx
│   │   │   ├── ai-schemaläggning-revolution.tsx
│   │   │   ├── framtidens-hemtjanst-trender.tsx
│   │   │   ├── implementeringsguide.tsx
│   │   │   ├── steg-for-steg-ai-schemaläggning.tsx
│   │   │   └── whitepapers.tsx
│   │   ├── Features/     # Feature pages
│   │   ├── About.tsx
│   │   ├── Contact.tsx
│   │   ├── Index.tsx
│   │   └── 404.tsx
│   │
│   ├── styles/          # Global styles
│   │   └── index.css
│   │
│   ├── test/           # Test utilities
│   │   └── test-utils.tsx
│   │
│   ├── types/         # TypeScript type definitions
│   │   └── index.ts
│   │
│   ├── utils/        # Utility functions
│   │   └── markdown-loader.ts
│   │
│   ├── App.tsx      # Main app component
│   └── main.tsx     # Entry point
│
├── .cursorrules     # Cursor AI rules
├── .env            # Environment variables
├── .gitignore     # Git ignore rules
├── index.html     # HTML template
├── package.json   # Dependencies and scripts
├── README.md      # Project readme
├── tsconfig.json  # TypeScript configuration
└── vite.config.ts # Vite configuration
```

## Key Directories

### `/docs`

Contains project documentation including implementation details, guidelines, and specifications.

### `/public`

Static assets that are served directly. Includes images, fonts, and other media files.

### `/src/components`

Reusable React components organized by functionality:

- `ui/`: Shadcn UI components and custom UI elements
- `animations/`: Animation components using Framer Motion
- `layout/`: Layout components like Header, Footer, Container
- `seo/`: SEO-related components including meta tags

### `/src/content`

Markdown content for articles and resources:

- `articles/`: Article content in markdown format
- Each article has its own markdown file with frontmatter

### `/src/pages`

Page components organized by section:

- `Resurser/`: Resource pages including articles and guides
- `Features/`: Feature pages describing product capabilities
- Root-level pages for main sections

### `/src/lib`

Core utilities and services:

- Analytics implementation
- Error tracking
- Utility functions

### `/src/hooks`

Custom React hooks for reusable logic:

- SEO hooks
- Analytics hooks
- Other shared functionality

### `/src/test`

Test utilities and setup:

- Test providers
- Mock implementations
- Helper functions

## File Naming Conventions

- React Components: PascalCase (e.g., `Button.tsx`)
- Utilities: camelCase (e.g., `markdown-loader.ts`)
- Styles: kebab-case (e.g., `button-styles.css`)
- Tests: ComponentName.test.tsx
- Content: kebab-case.md

## Import Structure

- Use absolute imports with `@/` prefix
- Group imports by type (React, components, utilities)
- Keep related imports together
- Use named exports for better tree-shaking

## Best Practices

1. Keep components focused and reusable
2. Use proper TypeScript types
3. Follow consistent naming conventions
4. Maintain proper documentation
5. Keep file structure flat where possible
6. Group related functionality together
7. Use index files for cleaner imports
8. Keep test files close to implementation
