// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	integrations: [
		starlight({
			title: 'Cross-Inertia',
			description: 'Inertia.js adapter for Python web frameworks',
			social: {
				github: 'https://github.com/patrick91/cross-inertia',
			},
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'index' },
						{ label: 'Installation', slug: 'getting-started/installation' },
						{ label: 'Quick Start', slug: 'getting-started/quick-start' },
					],
				},
				{
					label: 'Guides',
					items: [
						{ label: 'Configuration', slug: 'guides/configuration' },
						{ label: 'Validation Errors', slug: 'guides/validation-errors' },
						{ label: 'External Redirects', slug: 'guides/external-redirects' },
						{ label: 'History Encryption', slug: 'guides/history-encryption' },
						{ label: 'Partial Reloads', slug: 'guides/partial-reloads' },
						{ label: 'Shared Data', slug: 'guides/shared-data' },
					],
				},
				{
					label: 'API Reference',
					autogenerate: { directory: 'reference' },
				},
				{
					label: 'Contributing',
					items: [
						{ label: 'Development Setup', slug: 'contributing/development' },
						{ label: 'Running Tests', slug: 'contributing/testing' },
					],
				},
			],
		}),
	],
});
