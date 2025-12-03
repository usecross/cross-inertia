import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'
import { Link } from '@inertiajs/react'

interface IntroductionProps {
  content: {
    title: string
    description: string
  }
}

export default function Introduction({ content }: IntroductionProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>What is Cross-Inertia?</h2>
      <p>
        Cross-Inertia is an Inertia.js adapter for Python backends. It allows you to build modern
        single-page applications using classic server-side routing and controllers.
      </p>
      <p>
        Instead of building an API and a separate SPA frontend, you can build a monolithic
        application where your Python backend renders React, Vue, or Svelte components directly.
      </p>

      <h2>How it works</h2>
      <p>
        Inertia sits between your server-side framework and your client-side framework. On the
        initial page visit, Inertia returns a full HTML document. Subsequent visits return JSON
        responses that update the page without a full reload.
      </p>
      <CodeBlock
        code={`# Your FastAPI route returns a component name and props
@app.get("/users/{id}")
async def show_user(id: int, inertia: InertiaDep):
    user = await get_user(id)
    return inertia.render("Users/Show", {"user": user})`}
        language="python"
      />
      <p>
        The client-side adapter receives this data and renders the appropriate component with the
        provided props.
      </p>

      <h2>Why use Inertia?</h2>
      <ul>
        <li>
          <strong>No API needed</strong> - Skip building a separate REST or GraphQL API. Your
          controllers return page components directly.
        </li>
        <li>
          <strong>Server-side routing</strong> - Use your familiar Python routing. No client-side
          router needed.
        </li>
        <li>
          <strong>Full SPA experience</strong> - Users get the speed and responsiveness of a
          single-page app without the complexity.
        </li>
        <li>
          <strong>SEO friendly</strong> - With server-side rendering support, your pages are fully
          indexable by search engines.
        </li>
      </ul>

      <h2>Next steps</h2>
      <p>
        Ready to get started? Check out the{' '}
        <Link href="/docs/quick-start" className="text-primary-600 hover:text-primary-700">
          Quick Start guide
        </Link>{' '}
        to build your first Cross-Inertia application.
      </p>
    </DocsLayout>
  )
}
