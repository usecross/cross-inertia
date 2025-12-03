import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'
import { Link } from '@inertiajs/react'

interface SSRProps {
  content: {
    title: string
    description: string
  }
}

export default function SSR({ content }: SSRProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Why use SSR?</h2>
      <p>
        Server-side rendering improves your application's initial page load time and SEO. With SSR,
        the initial HTML is rendered on the server, making the content immediately visible to users
        and search engine crawlers.
      </p>

      <h2>Setting up the SSR server</h2>
      <p>
        Create a <code>ssr.tsx</code> entry point that exports a render function:
      </p>
      <CodeBlock
        code={`// frontend/ssr.tsx
import { createInertiaApp } from '@inertiajs/react'
import { renderToString } from 'react-dom/server'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })

export default function render(page: any) {
  return createInertiaApp({
    page,
    render: renderToString,
    resolve: (name) => pages[\`./pages/\${name}.tsx\`],
    setup: ({ App, props }) => <App {...props} />,
  })
}`}
        language="tsx"
        filename="frontend/ssr.tsx"
      />

      <h2>Building for SSR</h2>
      <p>Add an SSR build script to your <code>package.json</code>:</p>
      <CodeBlock
        code={`{
  "scripts": {
    "build": "vite build",
    "build:ssr": "vite build --ssr frontend/ssr.tsx --outDir dist/ssr"
  }
}`}
        language="json"
      />

      <h2>Running the SSR server</h2>
      <p>Cross-Inertia expects an SSR server running at <code>http://127.0.0.1:13714</code>:</p>
      <CodeBlock
        code={`// ssr-server.js
import { createServer } from 'http'
import render from './dist/ssr/ssr.js'

createServer(async (req, res) => {
  if (req.url === '/health') {
    res.writeHead(200)
    res.end('OK')
    return
  }

  if (req.url === '/render' && req.method === 'POST') {
    let body = ''
    req.on('data', chunk => body += chunk)
    req.on('end', async () => {
      const page = JSON.parse(body)
      const result = await render(page)
      res.writeHead(200, { 'Content-Type': 'application/json' })
      res.end(JSON.stringify(result))
    })
    return
  }

  res.writeHead(404)
  res.end()
}).listen(13714)`}
        language="javascript"
        filename="ssr-server.js"
      />

      <h2>Enabling SSR in Cross-Inertia</h2>
      <p>
        SSR is automatically enabled when the SSR server is running. Cross-Inertia will request
        rendered HTML from the server for initial page loads.
      </p>

      <h2>Automatic SSR server management</h2>
      <p>
        Instead of manually running the SSR server, you can use the experimental{' '}
        <Link href="/docs/ssr-lifespan" className="text-primary-600 hover:text-primary-700">
          SSR Lifespan
        </Link>{' '}
        feature to automatically start and stop the SSR server with your FastAPI app.
      </p>
    </DocsLayout>
  )
}
