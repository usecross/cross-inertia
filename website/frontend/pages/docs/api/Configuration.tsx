import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface ConfigurationApiProps {
  content: {
    title: string
    description: string
  }
}

export default function ConfigurationApi({ content }: ConfigurationApiProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>InertiaResponse</h2>
      <p>
        Core configuration class for Inertia responses.
      </p>
      <CodeBlock
        code={`InertiaResponse(
    template_dir: str = "templates",
    vite_dev_url: str = "http://localhost:5173",
    manifest_path: str = "static/build/.vite/manifest.json",
    vite_entry: str | None = None,
    vite_config_path: str = "vite.config.ts",
)`}
        language="python"
      />

      <h3>Parameters</h3>
      <table className="w-full">
        <thead>
          <tr>
            <th>Parameter</th>
            <th>Default</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>template_dir</code></td>
            <td><code>"templates"</code></td>
            <td>Directory containing HTML template</td>
          </tr>
          <tr>
            <td><code>vite_dev_url</code></td>
            <td><code>"http://localhost:5173"</code></td>
            <td>Vite dev server URL</td>
          </tr>
          <tr>
            <td><code>manifest_path</code></td>
            <td><code>"static/build/.vite/manifest.json"</code></td>
            <td>Path to Vite manifest.json</td>
          </tr>
          <tr>
            <td><code>vite_entry</code></td>
            <td><code>None</code> (auto-detected)</td>
            <td>Vite entry point</td>
          </tr>
          <tr>
            <td><code>vite_config_path</code></td>
            <td><code>"vite.config.ts"</code></td>
            <td>Path to vite.config for auto-detection</td>
          </tr>
        </tbody>
      </table>

      <h2>Custom configuration</h2>
      <CodeBlock
        code={`from fastapi import FastAPI, Depends
from inertia.fastapi import InertiaResponse, Inertia

# Custom configuration
inertia_response = InertiaResponse(
    template_dir="my_templates",
    vite_dev_url="http://localhost:5174",
    manifest_path="dist/.vite/manifest.json",
    vite_entry="src/main.tsx"
)

def get_custom_inertia(request: Request):
    return Inertia(request, inertia_response)

@app.get("/")
async def home(inertia: Inertia = Depends(get_custom_inertia)):
    return inertia.render("Home", {})`}
        language="python"
      />

      <h2>Environment detection</h2>
      <p>
        Cross-Inertia automatically detects development vs production mode:
      </p>
      <ul>
        <li><strong>Development:</strong> Uses Vite dev server for hot module replacement</li>
        <li><strong>Production:</strong> Uses built assets from the manifest file</li>
      </ul>
      <p>
        Detection is based on whether the Vite manifest file exists.
      </p>

      <h2>Template functions</h2>
      <p>
        The following functions are available in your Jinja2 templates:
      </p>

      <h3>vite()</h3>
      <p>Include Vite assets (scripts and stylesheets):</p>
      <CodeBlock
        code={`<!-- Default entry point -->
{{ vite() | safe }}

<!-- Custom entry point -->
{{ vite('admin/app.js') | safe }}`}
        language="html"
      />

      <h3>page</h3>
      <p>The current page data as a JSON string:</p>
      <CodeBlock
        code={`<div id="app" data-page='{{ page | safe }}'></div>`}
        language="html"
      />

      <h2>SSR configuration</h2>
      <p>
        SSR is enabled when the SSR server is reachable at <code>http://127.0.0.1:13714</code>.
        Configure the SSR server using environment variables or the experimental lifespan feature.
      </p>
    </DocsLayout>
  )
}
