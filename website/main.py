"""
Cross-Inertia Documentation Website

Built with Cross-Inertia, FastAPI, React, and Bun.
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaMiddleware, InertiaDep

from cross_docs import create_docs_router_from_config, load_config

# Load cross-docs config
docs_config = load_config()

app = FastAPI(title="Cross-Inertia Docs", docs_url=None, redoc_url=None)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add Inertia middleware
app.add_middleware(InertiaMiddleware, share=lambda request: {})

# Add docs router (from cross-docs config)
docs_router = create_docs_router_from_config(docs_config)
app.include_router(docs_router)


# Custom homepage route
@app.get("/")
async def home(request: Request, inertia: InertiaDep):
    return inertia.render(
        "Home",
        {
            "title": "Cross-Inertia",
            "tagline": "Python + Inertia.js",
            "description": "Build modern single-page applications with Django, Flask, and FastAPI. No API required.",
            "installCommand": "uv add cross-inertia",
            "ctaText": "Get Started",
            "ctaHref": "/docs",
            "features": [
                {
                    "title": "No API Needed",
                    "description": "Skip building a separate REST or GraphQL API. Your controllers return page components directly.",
                },
                {
                    "title": "Server-Side Routing",
                    "description": "Use your familiar Python routing. No client-side router needed.",
                },
                {
                    "title": "Full SPA Experience",
                    "description": "Users get the speed and responsiveness of a single-page app without the complexity.",
                },
                {
                    "title": "SEO Friendly",
                    "description": "With server-side rendering support, your pages are fully indexable by search engines.",
                },
            ],
            "logoUrl": "/static/logo.svg",
            "heroLogoUrl": "/static/logo-full.svg",
            "footerLogoUrl": "/static/logo-full.svg",
            "githubUrl": "https://github.com/patrick91/cross-inertia",
            "navLinks": [{"label": "Docs", "href": "/docs"}],
        },
        view_data={"page_title": "Cross-Inertia - Inertia.js for Python"},
    )
