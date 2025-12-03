import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface MiddlewareApiProps {
  content: {
    title: string
    description: string
  }
}

export default function MiddlewareApi({ content }: MiddlewareApiProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>InertiaMiddleware</h2>
      <p>
        Middleware for sharing data across all Inertia responses.
      </p>
      <CodeBlock
        code={`InertiaMiddleware(
    app,
    share: Callable[[Request], dict] | None = None
)`}
        language="python"
      />

      <h3>Parameters</h3>
      <ul>
        <li><code>app</code> - The ASGI application</li>
        <li><code>share</code> - Function that returns shared data for each request</li>
      </ul>

      <h2>Usage</h2>
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
    }

app.add_middleware(InertiaMiddleware, share=share_data)`}
        language="python"
      />

      <h2>Share function</h2>
      <p>
        The share function receives the current request and should return a dictionary of data to
        share with all pages.
      </p>
      <CodeBlock
        code={`def share_data(request: Request) -> dict:
    # Access request data
    user = request.state.user if hasattr(request.state, 'user') else None

    # Access session (if using session middleware)
    flash = request.session.pop('flash', {}) if 'session' in request.scope else {}

    return {
        "auth": {"user": user},
        "flash": flash,
        "app_name": "My App",
    }`}
        language="python"
      />

      <h2>Prop wrappers</h2>
      <p>
        Use prop wrappers in shared data for lazy evaluation:
      </p>
      <CodeBlock
        code={`from inertia import always, optional, defer

def share_data(request: Request) -> dict:
    return {
        # Always evaluated (even during partial reloads)
        "notifications_count": always(lambda: count_notifications()),

        # Only evaluated when requested
        "detailed_user": optional(lambda: get_detailed_user()),

        # Loaded asynchronously after initial render
        "activity_feed": defer(lambda: get_activity_feed()),
    }`}
        language="python"
      />

      <h2>Middleware order</h2>
      <p>
        Add InertiaMiddleware after other middleware that sets request state:
      </p>
      <CodeBlock
        code={`# Authentication middleware sets request.state.user
app.add_middleware(AuthMiddleware)

# InertiaMiddleware can access request.state.user
app.add_middleware(InertiaMiddleware, share=share_data)`}
        language="python"
      />
    </DocsLayout>
  )
}
