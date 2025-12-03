import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface SharedDataProps {
  content: {
    title: string
    description: string
  }
}

export default function SharedData({ content }: SharedDataProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>What is shared data?</h2>
      <p>
        Shared data is data that is automatically included in every Inertia response. This is
        useful for data that is needed on every page, such as:
      </p>
      <ul>
        <li>Current user information</li>
        <li>Flash messages</li>
        <li>Navigation data</li>
        <li>Application settings</li>
      </ul>

      <h2>Setting up shared data</h2>
      <p>
        Use the <code>InertiaMiddleware</code> to define shared data:
      </p>
      <CodeBlock
        code={`from fastapi import FastAPI, Request
from inertia.fastapi import InertiaMiddleware

app = FastAPI()

def share_data(request: Request) -> dict:
    return {
        "auth": {
            "user": get_current_user(request)
        },
        "flash": get_flash_messages(request),
        "app_name": "My App"
    }

app.add_middleware(InertiaMiddleware, share=share_data)`}
        language="python"
      />

      <h2>Accessing shared data</h2>
      <p>Shared data is merged with page props. Access it using the <code>usePage</code> hook:</p>
      <CodeBlock
        code={`import { usePage } from '@inertiajs/react'

interface SharedProps {
  auth: {
    user: { name: string } | null
  }
  flash: {
    message?: string
    type?: 'success' | 'error'
  }
}

export default function Layout({ children }) {
  const { auth, flash } = usePage<{ props: SharedProps }>().props

  return (
    <div>
      {auth.user && <span>Hello, {auth.user.name}</span>}
      {flash.message && (
        <div className={\`alert alert-\${flash.type}\`}>
          {flash.message}
        </div>
      )}
      {children}
    </div>
  )
}`}
        language="tsx"
      />

      <h2>Lazy shared data</h2>
      <p>
        You can use <code>always()</code> to ensure data is always evaluated, even during partial
        reloads:
      </p>
      <CodeBlock
        code={`from inertia import always

def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even on partial reloads)
        "notifications_count": always(lambda: get_notifications_count()),
        # Only evaluated on full page loads
        "user": get_current_user(request)
    }`}
        language="python"
      />
    </DocsLayout>
  )
}
