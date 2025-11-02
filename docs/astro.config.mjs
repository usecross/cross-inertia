// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

import cloudflare from '@astrojs/cloudflare';

// https://astro.build/config
export default defineConfig({
  site: 'https://inertia.patrick.wtf',
  integrations: [
      starlight({
          title: 'Cross-Inertia',
          description: 'Inertia.js adapter for Python web frameworks',
          social: [
              {
                  label: 'GitHub',
                  icon: 'github',
                  href: 'https://github.com/patrick91/cross-inertia',
              },
          ],
          sidebar: [
              {
                  label: 'Getting Started',
                  items: [
                      { label: 'Installation', slug: 'getting-started/installation' },
                      { label: 'Quick Start', slug: 'getting-started/quick-start' },
                  ],
              },
              {
                  label: 'Guides',
                  autogenerate: { directory: 'guides' },
              },
              {
                  label: 'API Reference',
                  autogenerate: { directory: 'reference' },
              },
          ],
      }),
	],

  adapter: cloudflare(),
});