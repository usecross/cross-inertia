import { DocsLayout } from '@/components/Layout'
import { CodeBlock } from '@/components/CodeBlock'

interface QuickStartProps {
  content: {
    title: string
    description: string
  }
}

export default function QuickStart({ content }: QuickStartProps) {
  return (
    <DocsLayout title={content.title} description={content.description}>
      <h2>Prerequisites</h2>
      <p>Before you begin, make sure you have:</p>
      <ul>
        <li>Python 3.10 or higher</li>
        <li>Node.js 18+ or Bun</li>
        <li>Basic familiarity with FastAPI and React</li>
      </ul>

      <h2>Step 1: Create your project</h2>
      <p>Create a new directory and set up your Python environment:</p>
      <CodeBlock
        code={`mkdir my-inertia-app
cd my-inertia-app
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate`}
        language="bash"
      />

      <h2>Step 2: Install dependencies</h2>
      <p>Install Cross-Inertia and FastAPI:</p>
      <CodeBlock code={`pip install cross-inertia fastapi uvicorn jinja2`} language="bash" />
      <p>Install the frontend dependencies:</p>
      <CodeBlock
        code={`bun init -y
bun add react react-dom @inertiajs/react
bun add -d vite @vitejs/plugin-react typescript @types/react @types/react-dom`}
        language="bash"
      />

      <h2>Step 3: Create your FastAPI app</h2>
      <p>Create a <code>main.py</code> file:</p>
      <CodeBlock
        code={`from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaDep

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello from Cross-Inertia!"
    })`}
        language="python"
        filename="main.py"
      />

      <h2>Step 4: Create your template</h2>
      <p>Create a <code>templates/app.html</code> file:</p>
      <CodeBlock
        code={`<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Inertia App</title>
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>`}
        language="html"
        filename="templates/app.html"
      />

      <h2>Step 5: Create your React app</h2>
      <p>Create a <code>frontend/app.tsx</code> file:</p>
      <CodeBlock
        code={`import { createInertiaApp } from '@inertiajs/react'
import { createRoot } from 'react-dom/client'

const pages = import.meta.glob('./pages/**/*.tsx', { eager: true })

createInertiaApp({
  resolve: (name) => {
    const page = pages[\`./pages/\${name}.tsx\`]
    if (!page) throw new Error(\`Page \${name} not found\`)
    return page
  },
  setup({ el, App, props }) {
    createRoot(el).render(<App {...props} />)
  },
})`}
        language="tsx"
        filename="frontend/app.tsx"
      />

      <h2>Step 6: Create your first page</h2>
      <p>Create a <code>frontend/pages/Home.tsx</code> file:</p>
      <CodeBlock
        code={`interface HomeProps {
  message: string
}

export default function Home({ message }: HomeProps) {
  return (
    <div>
      <h1>{message}</h1>
      <p>Welcome to your Inertia app!</p>
    </div>
  )
}`}
        language="tsx"
        filename="frontend/pages/Home.tsx"
      />

      <h2>Step 7: Configure Vite</h2>
      <p>Create a <code>vite.config.ts</code> file:</p>
      <CodeBlock
        code={`import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  build: {
    manifest: true,
    outDir: 'static/build',
    rollupOptions: {
      input: 'frontend/app.tsx',
    },
  },
})`}
        language="typescript"
        filename="vite.config.ts"
      />

      <h2>Step 8: Run your app</h2>
      <p>Start both the Vite dev server and FastAPI:</p>
      <CodeBlock
        code={`# Terminal 1: Start Vite
bun run vite

# Terminal 2: Start FastAPI
uvicorn main:app --reload`}
        language="bash"
      />
      <p>
        Visit <code>http://localhost:8000</code> to see your app!
      </p>

      <h2>Next steps</h2>
      <p>
        Now that you have a basic app running, explore more features like shared data, forms, and
        server-side rendering in the documentation.
      </p>
    </DocsLayout>
  )
}
