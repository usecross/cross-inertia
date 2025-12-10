import { createInertiaApp } from '@inertiajs/react'
import createServer from '@inertiajs/react/server'
import ReactDOMServer from 'react-dom/server'
import { DocsPage } from '@usecross/docs'

// Import page components
import Home from './pages/Home'

const pages: Record<string, React.ComponentType<any>> = {
  Home,
  'docs/DocsPage': DocsPage,
}

createServer((page) =>
  createInertiaApp({
    page,
    render: ReactDOMServer.renderToString,
    title: (title) => (title ? `${title} - Cross-Inertia` : 'Cross-Inertia'),
    resolve: (name) => {
      const pageComponent = pages[name]
      if (!pageComponent) {
        throw new Error(`Page component "${name}" not found`)
      }
      return pageComponent
    },
    setup: ({ App, props }) => <App {...props} />,
  })
)
