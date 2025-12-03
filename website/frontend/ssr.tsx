import { createInertiaApp } from '@inertiajs/react'
import { renderToString } from 'react-dom/server'

// Import all page components
import Home from './pages/Home'
import DocsIntroduction from './pages/docs/Introduction'
import DocsQuickStart from './pages/docs/QuickStart'
import DocsInstallation from './pages/docs/Installation'
import DocsPages from './pages/docs/Pages'
import DocsSharedData from './pages/docs/SharedData'
import DocsLinks from './pages/docs/Links'
import DocsForms from './pages/docs/Forms'
import DocsSSR from './pages/docs/SSR'
import DocsSSRLifespan from './pages/docs/SSRLifespan'
import DocsDeferredProps from './pages/docs/DeferredProps'
import DocsHistoryEncryption from './pages/docs/HistoryEncryption'
import DocsApiInertia from './pages/docs/api/Inertia'
import DocsApiMiddleware from './pages/docs/api/Middleware'
import DocsApiConfiguration from './pages/docs/api/Configuration'

const pages: Record<string, React.ComponentType<any>> = {
  Home,
  'docs/Introduction': DocsIntroduction,
  'docs/QuickStart': DocsQuickStart,
  'docs/Installation': DocsInstallation,
  'docs/Pages': DocsPages,
  'docs/SharedData': DocsSharedData,
  'docs/Links': DocsLinks,
  'docs/Forms': DocsForms,
  'docs/SSR': DocsSSR,
  'docs/SSRLifespan': DocsSSRLifespan,
  'docs/DeferredProps': DocsDeferredProps,
  'docs/HistoryEncryption': DocsHistoryEncryption,
  'docs/api/Inertia': DocsApiInertia,
  'docs/api/Middleware': DocsApiMiddleware,
  'docs/api/Configuration': DocsApiConfiguration,
}

export default function render(page: any) {
  return createInertiaApp({
    page,
    render: renderToString,
    resolve: (name) => {
      const pageComponent = pages[name]
      if (!pageComponent) {
        throw new Error(`Page component "${name}" not found`)
      }
      return pageComponent
    },
    setup: ({ App, props }) => <App {...props} />,
  })
}
