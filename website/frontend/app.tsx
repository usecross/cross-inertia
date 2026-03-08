import { createInertiaApp } from '@inertiajs/react'
import { DocsPage, ThemeProvider } from '@usecross/docs'
import { createRoot, hydrateRoot } from 'react-dom/client'
import './globals.css'

import Home from './pages/Home'

const pages = {
  Home,
  'docs/DocsPage': DocsPage,
}

createInertiaApp({
  defaults: {
    future: {
      useScriptElementForInitialPage: true,
    },
  },
  title: (title) => (title ? `${title} - Cross-Inertia` : 'Cross-Inertia'),
  resolve: (name) => {
    const page = pages[name as keyof typeof pages]
    if (!page) {
      throw new Error(`Page component "${name}" not found`)
    }
    return page
  },
  setup({ el, App, props }) {
    const appElement = (
      <ThemeProvider>
        <App {...props} />
      </ThemeProvider>
    )

    if (el.hasChildNodes()) {
      hydrateRoot(el, appElement)
      return
    }

    createRoot(el).render(appElement)
  },
})
