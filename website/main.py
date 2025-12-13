"""
Cross-Inertia Documentation Website

Built with Cross-Inertia, FastAPI, React, and Bun.
"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia.fastapi import InertiaMiddleware

from cross_docs import CrossDocs

app = FastAPI(title="Cross-Inertia Docs", docs_url=None, redoc_url=None)

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add Inertia middleware
app.add_middleware(InertiaMiddleware)

# Mount docs (includes homepage from config)
docs = CrossDocs()
docs.mount(app)
