# Inertia.js + FastAPI Example

A complete example application demonstrating how to use Inertia.js with FastAPI, React, and Vite.

## Features Demonstrated

- ✅ Basic page navigation with Inertia.js
- ✅ FastAPI backend with Inertia adapter
- ✅ React frontend with TypeScript
- ✅ Vite for development and building
- ✅ Bun as package manager
- ✅ **shadcn/ui components** with Tailwind CSS
- ✅ Form handling with validation errors
- ✅ Dynamic routing and parameters
- ✅ Shared layout component
- ✅ Client-side navigation (no full page reloads)
- ✅ Modern, accessible UI components

## Project Structure

```
examples/fastapi/
├── frontend/              # React frontend
│   ├── pages/            # Inertia page components
│   │   ├── Home.tsx
│   │   ├── About.tsx
│   │   ├── Form.tsx
│   │   ├── Error.tsx
│   │   └── Users/
│   │       ├── Index.tsx
│   │       └── Show.tsx
│   ├── components/       # Shared components
│   │   └── Layout.tsx
│   └── app.tsx          # Main entry point
├── templates/            # HTML templates
│   └── app.html         # Root template with {{ vite() }}
├── static/              # Static files
│   └── build/           # Built Vite assets (production)
├── main.py              # FastAPI application
├── package.json         # Frontend dependencies
├── vite.config.ts       # Vite configuration
└── tsconfig.json        # TypeScript configuration
```

## Prerequisites

- Python 3.12+
- [Bun](https://bun.sh) (for package management and faster installs)
  - Or npm/yarn/pnpm if you prefer

## Installation

### 1. Install Python Dependencies

From the **project root**, run:

```bash
# Install all Python dependencies using uv workspace
uv sync
```

This installs the cross-inertia package and all demo dependencies in one command.

### 2. Install Frontend Dependencies

```bash
# Using Bun (recommended - faster)
bun install

# Or using npm
npm install
```

This will install:
- React and TypeScript
- Inertia.js React adapter
- Tailwind CSS
- shadcn/ui component dependencies (Radix UI, etc.)
- Vite and build tools

## Development

You'll need to run both the backend and frontend dev servers.

### Option 1: Using Just (Recommended)

If you have [just](https://github.com/casey/just) installed, run from the **project root**:

```bash
# Install all dependencies
just demo-install

# Start both dev servers
just demo-fastapi
```

See all available commands with `just --list` from the project root.

### Option 2: Quick Start Script

```bash
# Make sure dependencies are installed first (only needed once)
bun install  # or: npm install

# Run the convenience script (starts both servers)
./run-dev.sh
```

This will:
1. Check for frontend dependencies
2. Start Vite dev server on http://localhost:5173
3. Start FastAPI server on http://127.0.0.1:8000

Then visit http://127.0.0.1:8000 in your browser.

### Option 3: Manual Start

If you prefer to run servers separately:

**Terminal 1: Start Vite Dev Server**

```bash
bun run dev
# or: npm run dev
```

This starts Vite on http://localhost:5173 with Hot Module Replacement (HMR).

**Terminal 2: Start FastAPI Server**

Make sure you're in the Python environment where dependencies are installed:

```bash
# Activate the virtual environment first
# The venv location depends on your setup - check with: uv pip show fastapi
# Common locations:
source ../../../.venv/bin/activate  # Parent project venv
# or
source .venv/bin/activate            # Local venv

# Then run the server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload
```

This starts FastAPI on http://127.0.0.1:8000.

**Open the App**

Visit http://127.0.0.1:8000 in your browser.

## How It Works

### Backend (FastAPI)

The FastAPI backend uses the `cross-inertia` adapter:

```python
from fastapi import FastAPI
from inertia import InertiaDep

app = FastAPI()

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render(
        "Home",  # React component name
        {
            "message": "Hello from FastAPI!",
        }
    )
```

### Frontend (React)

The React app uses `@inertiajs/react`:

```tsx
// frontend/pages/Home.tsx
export default function Home({ message }) {
  return (
    <Layout>
      <h1>{message}</h1>
    </Layout>
  )
}
```

### Vite Integration

The `{{ vite() }}` function in `templates/app.html` automatically:
- In development: Loads from Vite dev server with HMR
- In production: Loads built assets from manifest.json

## Production Build

### Using Just (from project root)

```bash
# Build the demo for production
just demo-build
```

### Manual Build

#### 1. Build Frontend Assets

```bash
bun run build
# or: npm run build
```

This creates optimized production assets in `static/build/`.

#### 2. Run Production Server

```bash
# Using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000

# Or using gunicorn (for production)
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The app will automatically detect that Vite dev server is not running and serve built assets instead.

## Available Just Commands

If you have [just](https://github.com/casey/just) installed, run these from the **project root**:

```bash
just                # List all commands
just demo-install   # Install all demo dependencies
just demo-fastapi   # Run the FastAPI demo (both servers)
just demo-build     # Build demo for production
just demo-clean     # Clean demo build artifacts
```

## Example Pages

### Home (`/`)
Welcome page with feature list

### About (`/about`)
Information about the tech stack

### Users List (`/users`)
Table showing list of users with navigation

### User Details (`/users/{id}`)
Detailed view of individual user

### Form Example (`/form`)
Form with validation errors (POST demonstration)

## Key Concepts Demonstrated

### 1. Inertia Navigation

Links use `<Link>` from `@inertiajs/react`:

```tsx
import { Link } from '@inertiajs/react'

<Link href="/about">About</Link>
```

This enables client-side navigation without full page reloads.

### 2. Form Handling

Forms use the `useForm` hook:

```tsx
import { useForm } from '@inertiajs/react'

const { data, setData, post, processing } = useForm({
  name: '',
  email: '',
})

const handleSubmit = (e) => {
  e.preventDefault()
  post('/form')
}
```

### 3. Validation Errors

Errors are passed from backend and available in props:

```python
# Backend
return inertia.render(
    "Form",
    {"message": "Error!"},
    errors={"email": "Invalid email"}
)
```

```tsx
// Frontend
export default function Form({ errors }) {
  return <div>{errors.email}</div>
}
```

### 4. Shared Layouts

Use a shared layout component for consistent navigation:

```tsx
import Layout from '../components/Layout'

export default function MyPage({ title }) {
  return (
    <Layout title={title}>
      <p>Page content here</p>
    </Layout>
  )
}
```

## Customization

### Change Vite Port

Edit `vite.config.ts`:

```ts
export default defineConfig({
  server: {
    port: 3000,  // Change from 5173
  },
})
```

### Change Backend Port

Edit `main.py`:

```python
if __name__ == "__main__":
    uvicorn.run(app, port=3000)  # Change from 8000
```

### Add New Pages

1. Create component in `frontend/pages/`
2. Import in `frontend/app.tsx`
3. Add route in `main.py`

## Troubleshooting

### "Page component not found"

Make sure the component is imported in `frontend/app.tsx`:

```tsx
import MyNewPage from './pages/MyNewPage'

const pages = {
  'MyNewPage': MyNewPage,  // Add here
}
```

### Vite assets not loading

1. Check Vite dev server is running on port 5173
2. Check Vite config has correct `input` path
3. Check console for errors

### FastAPI can't find template

Make sure `templates/app.html` exists and contains:
- `{{ vite() | safe }}`
- `<div id="app" data-page='{{ page | safe }}'></div>`

## UI Components

This example uses [shadcn/ui](https://ui.shadcn.com/) - a collection of beautifully designed, accessible components built with Radix UI and Tailwind CSS.

### Components Included

- **Button** - Multiple variants (default, outline, ghost, etc.)
- **Card** - For content containers
- **Table** - For data tables
- **Input** - Form inputs
- **Label** - Form labels
- **Badge** - For status indicators

### Adding More Components

shadcn/ui components are copied into your project, so you can customize them. To add more components, you can:

1. Copy components from [shadcn/ui documentation](https://ui.shadcn.com/docs/components)
2. Place them in `frontend/components/ui/`
3. Customize as needed

## Learn More

- [Inertia.js v2 Documentation](https://inertiajs.com/) (this example uses Inertia.js v2.0+)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)
- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

## License

This example is part of the cross-inertia project (MIT License).
