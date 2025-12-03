import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface LinksProps {
  content: {
    title: string
    description: string
  }
}

export default function Links({ content }: LinksProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Inertia Links</h2>
      <p>
        Use the <code>Link</code> component for client-side navigation without full page reloads:
      </p>
      <CodeBlock
        code={`import { Link } from '@inertiajs/react'

export default function Navigation() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/users">Users</Link>
    </nav>
  )
}`}
        language="tsx"
      />

      <h2>Link methods</h2>
      <p>
        By default, links use GET requests. You can change this with the <code>method</code> prop:
      </p>
      <CodeBlock
        code={`<Link href="/logout" method="post">
  Logout
</Link>

<Link href="/posts/1" method="delete">
  Delete Post
</Link>`}
        language="tsx"
      />

      <h2>Preserving state</h2>
      <p>
        Use <code>preserveState</code> to maintain component state during navigation:
      </p>
      <CodeBlock
        code={`<Link href="/users?page=2" preserveState>
  Page 2
</Link>`}
        language="tsx"
      />

      <h2>Preserving scroll</h2>
      <p>
        By default, Inertia resets scroll position. Use <code>preserveScroll</code> to prevent this:
      </p>
      <CodeBlock
        code={`<Link href="/users?page=2" preserveScroll>
  Next Page
</Link>`}
        language="tsx"
      />

      <h2>Programmatic navigation</h2>
      <p>
        Use the <code>router</code> for programmatic navigation:
      </p>
      <CodeBlock
        code={`import { router } from '@inertiajs/react'

// GET request
router.visit('/users')

// POST request with data
router.post('/users', {
  name: 'John',
  email: 'john@example.com'
})

// With options
router.visit('/users', {
  method: 'get',
  preserveState: true,
  preserveScroll: true,
  only: ['users'],  // Partial reload
})`}
        language="tsx"
      />

      <h2>External redirects</h2>
      <p>
        For external URLs or non-Inertia pages, use <code>inertia.location()</code> on the server:
      </p>
      <CodeBlock
        code={`@app.get("/oauth/redirect")
async def oauth_redirect(inertia: InertiaDep):
    return inertia.location("https://github.com/login/oauth")`}
        language="python"
      />
    </DocsLayout>
  )
}
