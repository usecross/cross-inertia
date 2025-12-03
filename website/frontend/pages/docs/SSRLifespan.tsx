import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface SSRLifespanProps {
  content: {
    title: string
    description: string
  }
}

export default function SSRLifespan({ content }: SSRLifespanProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 dark:border-amber-800 dark:bg-amber-900/20">
        <p className="text-amber-800 dark:text-amber-200">
          <strong>Experimental Feature:</strong> This feature is experimental and may change in
          future versions.
        </p>
      </div>

      <h2>Automatic SSR server management</h2>
      <p>
        Cross-Inertia can automatically start and stop your SSR server alongside your FastAPI
        application using FastAPI's lifespan feature.
      </p>

      <h2>Quick start</h2>
      <p>
        The simplest way is to use <code>inertia_lifespan</code>:
      </p>
      <CodeBlock
        code={`from fastapi import FastAPI
from inertia.fastapi.experimental import inertia_lifespan

app = FastAPI(lifespan=inertia_lifespan)`}
        language="python"
      />
      <p>This will:</p>
      <ul>
        <li>Start the SSR server when your FastAPI app starts</li>
        <li>Stop the SSR server when your FastAPI app shuts down</li>
        <li>Wait for the SSR server to become healthy before accepting requests</li>
      </ul>

      <h2>Configuration via environment variables</h2>
      <p>Configure the SSR server using environment variables:</p>
      <table className="w-full">
        <thead>
          <tr>
            <th>Variable</th>
            <th>Default</th>
            <th>Description</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><code>INERTIA_SSR_COMMAND</code></td>
            <td><code>bun dist/ssr/ssr.js</code></td>
            <td>Command to start SSR server</td>
          </tr>
          <tr>
            <td><code>INERTIA_SSR_CWD</code></td>
            <td>Current directory</td>
            <td>Working directory</td>
          </tr>
          <tr>
            <td><code>INERTIA_SSR_HEALTH_URL</code></td>
            <td><code>http://127.0.0.1:13714/health</code></td>
            <td>Health check endpoint</td>
          </tr>
          <tr>
            <td><code>INERTIA_SSR_TIMEOUT</code></td>
            <td><code>10</code></td>
            <td>Startup timeout in seconds</td>
          </tr>
        </tbody>
      </table>

      <h2>Composable approach</h2>
      <p>
        For more control, use <code>create_ssr_lifespan</code>:
      </p>
      <CodeBlock
        code={`from contextlib import asynccontextmanager
from fastapi import FastAPI
from inertia.fastapi.experimental import create_ssr_lifespan

@asynccontextmanager
async def lifespan(app):
    # Your startup logic
    print("Starting up...")

    async with create_ssr_lifespan(
        command="bun dist/ssr/ssr.js",
        startup_timeout=15.0,
        env={"NODE_ENV": "production"}
    ) as ssr:
        print(f"SSR running: {ssr.is_running}")
        yield

    # Your shutdown logic
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)`}
        language="python"
      />

      <h2>Error handling</h2>
      <p>
        Handle SSR server startup failures with <code>SSRServerError</code>:
      </p>
      <CodeBlock
        code={`from inertia.fastapi.experimental import create_ssr_lifespan, SSRServerError

@asynccontextmanager
async def lifespan(app):
    try:
        async with create_ssr_lifespan():
            yield
    except SSRServerError as e:
        print(f"SSR failed to start: {e}")
        # Continue without SSR
        yield`}
        language="python"
      />
    </DocsLayout>
  )
}
