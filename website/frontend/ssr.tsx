import { createDocsServer } from '@usecross/docs/ssr'
import { DocsPage } from '@usecross/docs'

// Import page components
import Home from './pages/Home'

createDocsServer({
  pages: {
    Home,
    'docs/DocsPage': DocsPage,
  },
  title: (title) => (title ? `${title} - Cross-Inertia` : 'Cross-Inertia'),
})
