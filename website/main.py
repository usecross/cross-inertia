"""
Cross-Inertia Documentation Website

Built with Cross-Inertia, FastAPI, React, and Bun.
"""

import subprocess
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaMiddleware, InertiaDep
import inertia._core

# Auto-detect dev mode: "dev" in argv when running `fastapi dev`
DEBUG = "dev" in sys.argv

# Configure Inertia response (set singleton before it's accessed)
inertia_response = inertia._core.InertiaResponse(
    template_dir="templates",
    manifest_path="static/build/.vite/manifest.json",
    vite_entry="frontend/app.tsx",
    vite_dev_url="http://localhost:5188" if DEBUG else None,
)
inertia._core._inertia_response = inertia_response


@asynccontextmanager
async def lifespan(app: FastAPI):
    vite_process = None

    if DEBUG:
        # Start Vite dev server using pybun
        vite_process = subprocess.Popen(
            [sys.executable, "-m", "pybun", "run", "dev"],
        )
        print("Started Vite dev server")

    yield

    if vite_process:
        vite_process.terminate()
        vite_process.wait()
        print("Stopped Vite dev server")

# Content directory
CONTENT_DIR = Path(__file__).parent / "content"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, content

    frontmatter = {}
    for line in parts[1].strip().split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            frontmatter[key.strip()] = value.strip()

    return frontmatter, parts[2].strip()


def load_markdown(path: str) -> dict:
    """Load and parse a markdown file."""
    file_path = CONTENT_DIR / f"{path}.md"
    if not file_path.exists():
        raise HTTPException(status_code=404, detail=f"Content not found: {path}")

    content = file_path.read_text()
    frontmatter, body = parse_frontmatter(content)

    return {
        "title": frontmatter.get("title", "Untitled"),
        "description": frontmatter.get("description", ""),
        "body": body,
    }


def generate_docs_nav() -> list[dict]:
    """Generate navigation from markdown files in content/docs."""
    docs_dir = CONTENT_DIR / "docs"
    sections: dict[str, list[dict]] = {}

    # Collect all markdown files
    for md_file in docs_dir.rglob("*.md"):
        content = md_file.read_text()
        frontmatter, _ = parse_frontmatter(content)

        title = frontmatter.get("title", md_file.stem)
        section = frontmatter.get("section", "Other")
        order = int(frontmatter.get("order", 99))

        # Build href from file path relative to docs_dir
        rel_path = md_file.relative_to(docs_dir)
        href_parts = list(rel_path.parts)
        href_parts[-1] = href_parts[-1].replace(".md", "")

        # introduction.md -> /docs, others -> /docs/<path>
        if href_parts == ["introduction"]:
            href = "/docs"
        else:
            href = "/docs/" + "/".join(href_parts)

        if section not in sections:
            sections[section] = []

        sections[section].append({"title": title, "href": href, "order": order})

    # Sort items within each section by order
    for section in sections:
        sections[section].sort(key=lambda x: x["order"])
        # Remove order from final output
        for item in sections[section]:
            del item["order"]

    # Define section order
    section_order = ["Getting Started", "Core Concepts", "Advanced", "API Reference"]

    # Build final navigation
    nav = []
    for section_name in section_order:
        if section_name in sections:
            nav.append({"title": section_name, "items": sections[section_name]})

    # Add any remaining sections not in the predefined order
    for section_name, items in sections.items():
        if section_name not in section_order:
            nav.append({"title": section_name, "items": items})

    return nav


# Generate navigation from markdown files
DOCS_NAV = generate_docs_nav()


app = FastAPI(title="Cross-Inertia Docs", lifespan=lifespan)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")


def share_data(request: Request) -> dict:
    """Shared data available on all pages."""
    return {
        "nav": DOCS_NAV,
        "currentPath": str(request.url.path),
    }


app.add_middleware(InertiaMiddleware, share=share_data)


# Routes
@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render(
        "Home",
        {
            "features": [
                {
                    "title": "FastAPI Integration",
                    "description": "First-class support for FastAPI with dependency injection, middleware, and async support.",
                    "icon": "zap",
                },
                {
                    "title": "React & Vue Support",
                    "description": "Works seamlessly with React, Vue, and Svelte through Inertia.js client adapters.",
                    "icon": "layers",
                },
                {
                    "title": "Server-Side Rendering",
                    "description": "Built-in SSR support for improved SEO and faster initial page loads.",
                    "icon": "server",
                },
                {
                    "title": "Type Safety",
                    "description": "Full TypeScript support on the frontend with Python type hints on the backend.",
                    "icon": "shield",
                },
            ],
            "codeExample": '''from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "message": "Hello from Python!"
    })''',
        },
        view_data={"page_title": "Home"},
    )


@app.get("/docs")
async def docs_index(inertia: InertiaDep):
    content = load_markdown("docs/introduction")
    return inertia.render(
        "docs/DocsPage",
        {"content": content},
        view_data={"page_title": content["title"]},
    )


@app.get("/docs/{path:path}")
async def docs_page(path: str, inertia: InertiaDep):
    content = load_markdown(f"docs/{path}")
    return inertia.render(
        "docs/DocsPage",
        {"content": content},
        view_data={"page_title": content["title"]},
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
