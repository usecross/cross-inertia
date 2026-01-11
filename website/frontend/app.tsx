import { createDocsApp, DocsPage } from '@usecross/docs'
import './globals.css'

// Import page components
import Home from './pages/Home'

createDocsApp({
  pages: {
    Home,
    'docs/DocsPage': DocsPage,
  },
  title: (title) => (title ? `${title} - Cross-Inertia` : 'Cross-Inertia'),
})
