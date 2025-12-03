import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface InstallationProps {
  content: {
    title: string
    description: string
  }
}

export default function Installation({ content }: InstallationProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Server-side installation</h2>
      <p>Install Cross-Inertia using pip:</p>
      <CodeBlock code={`pip install cross-inertia`} language="bash" />
      <p>Or with uv:</p>
      <CodeBlock code={`uv add cross-inertia`} language="bash" />

      <h2>Client-side installation</h2>
      <p>Install the Inertia.js client adapter for your framework of choice:</p>

      <h3>React</h3>
      <CodeBlock code={`bun add @inertiajs/react react react-dom`} language="bash" />

      <h3>Vue</h3>
      <CodeBlock code={`bun add @inertiajs/vue3 vue`} language="bash" />

      <h3>Svelte</h3>
      <CodeBlock code={`bun add @inertiajs/svelte svelte`} language="bash" />

      <h2>Additional dependencies</h2>
      <p>You'll also need Jinja2 for templating:</p>
      <CodeBlock code={`pip install jinja2`} language="bash" />
      <p>And for server-side rendering support:</p>
      <CodeBlock code={`pip install httpx`} language="bash" />

      <h2>Build tools</h2>
      <p>We recommend using Vite for building your frontend assets:</p>
      <CodeBlock code={`bun add -d vite @vitejs/plugin-react typescript`} language="bash" />

      <h2>Verification</h2>
      <p>You can verify your installation by importing Cross-Inertia:</p>
      <CodeBlock
        code={`from inertia.fastapi import InertiaDep, InertiaMiddleware, InertiaResponse

print("Cross-Inertia installed successfully!")`}
        language="python"
      />
    </DocsLayout>
  )
}
