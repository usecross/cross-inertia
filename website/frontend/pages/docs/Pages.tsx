import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface PagesProps {
  content: {
    title: string
    description: string
  }
}

export default function Pages({ content }: PagesProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Rendering pages</h2>
      <p>
        In Cross-Inertia, pages are rendered using the <code>inertia.render()</code> method. This
        method takes a component name and optional props.
      </p>
      <CodeBlock
        code={`from inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "title": "Welcome",
        "user": {"name": "John"}
    })`}
        language="python"
      />

      <h2>Component naming</h2>
      <p>
        Component names map directly to your frontend page components. Use forward slashes to
        organize pages into directories:
      </p>
      <CodeBlock
        code={`# These map to frontend/pages/Users/Index.tsx
inertia.render("Users/Index", {...})

# And frontend/pages/Users/Show.tsx
inertia.render("Users/Show", {...})`}
        language="python"
      />

      <h2>Page props</h2>
      <p>Props passed to the render method are available in your page component:</p>
      <CodeBlock
        code={`// frontend/pages/Users/Show.tsx
interface ShowProps {
  user: {
    id: number
    name: string
    email: string
  }
}

export default function Show({ user }: ShowProps) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}`}
        language="tsx"
      />

      <h2>View data</h2>
      <p>
        You can pass additional data to your template (not included in page props) using the{' '}
        <code>view_data</code> parameter:
      </p>
      <CodeBlock
        code={`@app.get("/products/{id}")
async def show_product(id: int, inertia: InertiaDep):
    product = await get_product(id)
    return inertia.render(
        "Products/Show",
        {"product": product},
        view_data={
            "page_title": product.name,
            "meta_description": product.description[:160]
        }
    )`}
        language="python"
      />

      <h2>Accessing page data</h2>
      <p>On the frontend, you can access the current page data using the <code>usePage</code> hook:</p>
      <CodeBlock
        code={`import { usePage } from '@inertiajs/react'

export default function Layout({ children }) {
  const { url, props } = usePage()

  return (
    <div>
      <nav>Current URL: {url}</nav>
      {children}
    </div>
  )
}`}
        language="tsx"
      />
    </DocsLayout>
  )
}
