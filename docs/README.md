# Cross-Inertia Documentation

This directory contains the documentation for Cross-Inertia, built with [Starlight](https://starlight.astro.build/).

## Development

Install dependencies:

```bash
npm install
```

Start the development server:

```bash
npm run dev
```

The docs will be available at `http://localhost:4321`

**Production site**: https://inertia.patrick.wtf

## Building

Build the static site:

```bash
npm run build
```

Preview the build:

```bash
npm run preview
```

## Structure

```
docs/
├── src/
│   └── content/
│       └── docs/
│           ├── index.mdx           # Home page
│           ├── getting-started/    # Installation & Quick Start
│           ├── guides/             # Feature guides
│           ├── reference/          # API reference
│           └── contributing/       # Development guides
├── astro.config.mjs                # Starlight configuration
└── package.json
```

## Adding Content

1. Create a new `.md` or `.mdx` file in `src/content/docs/`
2. Add frontmatter:
   ```yaml
   ---
   title: Page Title
   description: Page description for SEO
   ---
   ```
3. Write your content using Markdown
4. Update `astro.config.mjs` sidebar if needed

## Deployment

The docs can be deployed to any static hosting service:
- GitHub Pages
- Netlify
- Vercel
- Cloudflare Pages

See [Starlight deployment guide](https://starlight.astro.build/guides/deploy/) for details.
