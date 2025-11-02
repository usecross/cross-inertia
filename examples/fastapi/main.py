"""
FastAPI + Inertia.js Example Application

A simple demo showing how to use Inertia.js with FastAPI, React, and Vite.
"""

import sys
from pathlib import Path

# Add parent package to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from inertia import InertiaDep

app = FastAPI(title="Inertia FastAPI Demo")

# Serve static files (built assets in production)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def home(inertia: InertiaDep):
    """Home page with welcome message."""
    return inertia.render(
        "Home",
        {
            "title": "Welcome to Inertia.js + FastAPI",
            "message": "This is a demo application showing Inertia.js working with FastAPI, React, and Vite.",
            "features": [
                "FastAPI backend",
                "React frontend with TypeScript",
                "Vite for lightning-fast HMR",
                "Bun as package manager",
                "Full Inertia.js protocol support",
            ],
        },
    )


@app.get("/about")
async def about(inertia: InertiaDep):
    """About page."""
    return inertia.render(
        "About",
        {
            "title": "About This Demo",
            "description": "This demo showcases the cross-inertia adapter for FastAPI.",
            "tech_stack": {
                "Backend": "FastAPI + cross-inertia",
                "Frontend": "React + TypeScript",
                "Build Tool": "Vite",
                "Package Manager": "Bun",
            },
        },
    )


@app.get("/users")
async def users_index(inertia: InertiaDep):
    """List of users."""
    users_data = [
        {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin"},
        {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User"},
        {"id": 3, "name": "Carol White", "email": "carol@example.com", "role": "User"},
        {"id": 4, "name": "David Brown", "email": "david@example.com", "role": "Moderator"},
    ]

    return inertia.render(
        "Users/Index",
        {
            "title": "Users",
            "users": users_data,
        },
    )


@app.get("/users/{user_id}")
async def users_show(user_id: int, inertia: InertiaDep):
    """Show individual user."""
    # In a real app, you'd fetch from database
    users_data = {
        1: {"id": 1, "name": "Alice Johnson", "email": "alice@example.com", "role": "Admin", "joined": "2023-01-15"},
        2: {"id": 2, "name": "Bob Smith", "email": "bob@example.com", "role": "User", "joined": "2023-03-22"},
        3: {"id": 3, "name": "Carol White", "email": "carol@example.com", "role": "User", "joined": "2023-05-10"},
        4: {"id": 4, "name": "David Brown", "email": "david@example.com", "role": "Moderator", "joined": "2023-07-08"},
    }

    user = users_data.get(user_id)
    if not user:
        return inertia.render(
            "Error",
            {"title": "Not Found", "message": f"User {user_id} not found"},
        )

    return inertia.render(
        "Users/Show",
        {
            "title": f"User: {user['name']}",
            "user": user,
        },
    )


@app.get("/form")
async def form_page(inertia: InertiaDep):
    """Example form page."""
    return inertia.render(
        "Form",
        {
            "title": "Example Form",
            "message": "Submit this form to see validation errors.",
        },
    )


@app.post("/form")
async def form_submit(inertia: InertiaDep):
    """Handle form submission with validation."""
    # Simulate validation errors
    errors = {
        "name": "The name field is required.",
        "email": "Please enter a valid email address.",
    }

    # In a real app, you'd validate the actual form data
    return inertia.render(
        "Form",
        {
            "title": "Example Form",
            "message": "There were errors with your submission.",
        },
        errors=errors,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
