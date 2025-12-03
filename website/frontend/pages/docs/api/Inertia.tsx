import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface InertiaApiProps {
  content: {
    title: string
    description: string
  }
}

export default function InertiaApi({ content }: InertiaApiProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>InertiaDep</h2>
      <p>
        FastAPI dependency for injecting the Inertia instance into your route handlers:
      </p>
      <CodeBlock
        code={`from inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {})`}
        language="python"
      />

      <h2>inertia.render()</h2>
      <p>Render an Inertia response with the specified component and props.</p>
      <CodeBlock
        code={`def render(
    component: str,
    props: dict[str, Any] | None = None,
    errors: dict[str, str] | None = None,
    merge_props: list[str] | None = None,
    prepend_props: list[str] | None = None,
    deep_merge_props: list[str] | None = None,
    match_props_on: list[str] | None = None,
    scroll_props: dict[str, Any] | None = None,
    url: str | None = None,
    view_data: dict[str, Any] | None = None,
) -> Response`}
        language="python"
      />
      <h3>Parameters</h3>
      <ul>
        <li><code>component</code> - The page component name (e.g., "Home", "Users/Show")</li>
        <li><code>props</code> - Props to pass to the component</li>
        <li><code>errors</code> - Validation errors (triggers 422 status)</li>
        <li><code>merge_props</code> - Props to merge instead of replace</li>
        <li><code>prepend_props</code> - Props to prepend instead of replace</li>
        <li><code>deep_merge_props</code> - Props to deep merge</li>
        <li><code>match_props_on</code> - Keys to match on when merging</li>
        <li><code>scroll_props</code> - Infinite scroll configuration</li>
        <li><code>url</code> - Override the response URL</li>
        <li><code>view_data</code> - Extra template data (not in page props)</li>
      </ul>

      <h2>inertia.location()</h2>
      <p>Perform an external redirect (full page navigation).</p>
      <CodeBlock
        code={`def location(url: str) -> Response`}
        language="python"
      />
      <p>Returns a 409 response with <code>X-Inertia-Location</code> header.</p>
      <CodeBlock
        code={`@app.get("/oauth")
async def oauth(inertia: InertiaDep):
    return inertia.location("https://github.com/login/oauth")`}
        language="python"
      />

      <h2>inertia.encrypt_history()</h2>
      <p>Enable history encryption for the current page.</p>
      <CodeBlock
        code={`def encrypt_history(encrypt: bool = True) -> Inertia`}
        language="python"
      />
      <p>Returns self for method chaining.</p>

      <h2>inertia.clear_history()</h2>
      <p>Clear encrypted history by rotating encryption keys.</p>
      <CodeBlock
        code={`def clear_history(clear: bool = True) -> Inertia`}
        language="python"
      />
      <p>Returns self for method chaining.</p>

      <h2>inertia.back()</h2>
      <p>Redirect back with errors (for form validation).</p>
      <CodeBlock
        code={`def back(errors: dict[str, str] | None = None) -> Response`}
        language="python"
      />
      <CodeBlock
        code={`@app.post("/users")
async def create_user(inertia: InertiaDep):
    if errors:
        return inertia.back(errors=errors)
    # ...`}
        language="python"
      />
    </DocsLayout>
  )
}
