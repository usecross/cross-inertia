import { createInertiaApp, router } from '@inertiajs/react'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './globals.css'

// Import page components
import Home from './pages/Home'
import DocsPage from './pages/docs/DocsPage'

const pages: Record<string, React.ComponentType<any>> = {
  Home,
  'docs/DocsPage': DocsPage,
}

// Disable scroll restoration on initial page load to prevent animated scroll
if (typeof window !== 'undefined') {
  // Disable browser's scroll restoration
  window.history.scrollRestoration = 'manual'
  // Force scroll to top immediately before any rendering
  window.scrollTo(0, 0)
}

createInertiaApp({
  title: (title) => (title ? `${title} - Cross-Inertia` : 'Cross-Inertia'),
  resolve: (name) => {
    const page = pages[name]
    if (!page) {
      throw new Error(`Page component "${name}" not found`)
    }
    return page
  },
  setup({ el, App, props }) {
    if (el.hasChildNodes()) {
      hydrateRoot(el, <App {...props} />)
    } else {
      createRoot(el).render(<App {...props} />)
    }
  },
})
