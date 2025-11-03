"""
FastAPI + Inertia.js Example Application - PurrfectHome

A cat adoption platform demo showcasing Inertia.js features

HISTORY ENCRYPTION EXAMPLES:
----------------------------
This demo doesn't implement authentication, but here are examples of how to use
history encryption in a real application with sensitive data:

# Encrypt sensitive pages (banking, healthcare, admin)
@app.get("/account/transactions")
async def transactions(inertia: InertiaDep):
    inertia.encrypt_history()  # Enable encryption for this page
    return inertia.render("Transactions", {
        "balance": user.balance,
        "transactions": user.get_transactions()
    })

# Clear history on logout
@app.post("/logout")
async def logout(inertia: InertiaDep):
    clear_user_session()
    inertia.clear_history()  # Clear all encrypted history
    return inertia.render("Login", {})

# Method chaining is supported
inertia.encrypt_history().render("AdminPanel", {...})
"""

import sys
import logging
from pathlib import Path

# Add parent package to path for development
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from fastapi import FastAPI, Query, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from inertia.fastapi import InertiaDep, InertiaMiddleware
import mock_data

# Configure logging for this module
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

app = FastAPI(title="PurrfectHome - Cat Adoption Demo")

# Serve static files (built assets in production)
app.mount("/static", StaticFiles(directory="static"), name="static")


# Shared data function for Inertia
def share_data(request: Request) -> dict:
    """
    Shared data that is automatically included in all Inertia responses.
    This data is available in every page component via usePage().props
    """
    # Mock user data - in a real app, this would come from authentication
    user_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john@example.com",
    }

    # Get favorites count dynamically
    favorites_count = len(mock_data.get_favorited_cats())

    # Get flash messages from session (if available)
    # IMPORTANT: Only pop flash on GET requests or non-Inertia requests
    # For POST/PUT/DELETE, the flash should be preserved until the redirect
    flash_data = {}
    try:
        if "session" in request.scope and "flash" in request.session:
            # Check if this is a GET request or a non-Inertia request
            is_get = request.method == "GET"
            is_inertia = request.headers.get("X-Inertia") == "true"

            # Only pop flash on GET requests (after redirects)
            if is_get and is_inertia:
                flash_data = request.session.pop("flash")  # Get and clear
            elif not is_inertia:
                # For non-Inertia requests (initial page load), also pop
                flash_data = request.session.pop("flash", {})
    except (KeyError, AssertionError):
        # Session not available, that's okay
        pass

    return {
        "auth": {
            "user": user_data,
        },
        "favorites_count": favorites_count,
        "flash": flash_data,
    }


# Add middleware (order matters: last added = first executed in FastAPI)
# InertiaMiddleware should be added BEFORE SessionMiddleware so Session runs first
app.add_middleware(InertiaMiddleware, share=share_data)
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-change-in-production")


# Helper function for flash messages
def flash(request: Request, message: str, category: str = "success"):
    """
    Flash a message to be displayed on the next request.

    Args:
        request: The current request
        message: The message to display
        category: Message category (success, error, warning, info)
    """
    request.session["flash"] = {
        "message": message,
        "category": category,
    }


@app.get("/")
async def home(inertia: InertiaDep):
    """Home page - redirects to browse"""
    # For now, redirect to browse page
    # Later we can create a proper home page
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/browse")


@app.get("/browse")
async def browse_cats(
    inertia: InertiaDep,
    page: int = Query(1, ge=1),
    breed: str | None = None,
    age_range: str | None = None,
):
    """Browse cats page with infinite scroll (6 cats per page)"""

    # Apply filters
    filtered_cats = mock_data.filter_cats(breed=breed, age_range=age_range)

    # Apply pagination with 6 cats per page for infinite scroll demo
    paginated = mock_data.paginate_cats(filtered_cats, page=page, per_page=6)

    # Mark favorites
    for cat in paginated["cats"]:
        cat["is_favorited"] = mock_data.is_favorited(cat["id"])

    return inertia.render(
        "Browse",
        {
            "title": "Browse Cats",
            "cats": paginated["cats"],
            "total": paginated["total"],
            "page": paginated["page"],
            "per_page": paginated["per_page"],
            "has_more": page < paginated["total_pages"],
            "filters": {
                "breed": breed,
                "age_range": age_range,
            },
        },
        # Enable infinite scroll: merge cats array and match on ID to prevent duplicates
        merge_props=["cats"],
        match_props_on=["id"],
    )


@app.get("/cats/{cat_id}")
async def show_cat(cat_id: int, inertia: InertiaDep):
    """Show individual cat profile"""
    cat = mock_data.get_cat_by_id(cat_id)

    if not cat:
        return inertia.render(
            "Error",
            {"title": "Not Found", "message": f"Cat {cat_id} not found"},
        )

    # Get shelter info
    shelter = mock_data.get_shelter_by_name(cat["shelter_name"])

    # Get similar cats
    similar_cats = mock_data.get_similar_cats(cat_id, limit=6)

    # Mark favorite status
    cat["is_favorited"] = mock_data.is_favorited(cat_id)
    for similar_cat in similar_cats:
        similar_cat["is_favorited"] = mock_data.is_favorited(similar_cat["id"])

    return inertia.render(
        "CatProfile",
        {
            "title": f"{cat['name']} - Adopt Me!",
            "cat": cat,
            "shelter": shelter,
            "similar_cats": similar_cats,
        },
    )


@app.get("/favorites")
async def favorites(inertia: InertiaDep):
    """Show user's favorite cats"""
    favorited_cats = mock_data.get_favorited_cats()

    # Mark all as favorited
    for cat in favorited_cats:
        cat["is_favorited"] = True

    return inertia.render(
        "Favorites",
        {
            "title": "My Favorites",
            "cats": favorited_cats,
            "total": len(favorited_cats),
        },
    )


@app.post("/favorites/{cat_id}/toggle")
async def toggle_favorite(cat_id: int, inertia: InertiaDep):
    """Toggle favorite status for a cat"""
    cat = mock_data.get_cat_by_id(cat_id)
    is_now_favorited = mock_data.toggle_favorite(cat_id)

    # Flash message based on action
    if is_now_favorited:
        flash(inertia.request, f"Added {cat['name']} to your favorites!", "success")
    else:
        flash(inertia.request, f"Removed {cat['name']} from favorites", "info")

    # Redirect back to the referring page (or /browse as fallback)
    from fastapi.responses import RedirectResponse

    referer = inertia.request.headers.get("referer", "/browse")
    # Extract the path from the referer URL
    from urllib.parse import urlparse

    redirect_path = urlparse(referer).path if referer else "/browse"

    return RedirectResponse(url=redirect_path, status_code=303)


@app.post("/favorites/{cat_id}/remove")
async def remove_favorite(cat_id: int, inertia: InertiaDep):
    """Remove a cat from favorites (from favorites page)"""
    cat = mock_data.get_cat_by_id(cat_id)
    mock_data.toggle_favorite(cat_id)

    flash(inertia.request, f"Removed {cat['name']} from favorites", "info")

    # Redirect back to favorites page
    from fastapi.responses import RedirectResponse

    return RedirectResponse(url="/favorites", status_code=303)


@app.get("/shelter/{shelter_name}/directions")
async def get_shelter_directions(shelter_name: str, inertia: InertiaDep):
    """
    External redirect to Google Maps for shelter directions.

    This demonstrates the external redirect feature using inertia.location().
    The client will receive a 409 response with X-Inertia-Location header
    and automatically perform a full page navigation to Google Maps.
    """
    shelter = mock_data.get_shelter_by_name(shelter_name)

    if not shelter:
        return inertia.render(
            "Error",
            {"title": "Not Found", "message": f"Shelter '{shelter_name}' not found"},
        )

    # Construct Google Maps URL with the shelter's address
    # Using + for spaces is more URL-friendly than %20
    address = shelter["address"].replace(" ", "+")
    maps_url = f"https://maps.google.com/?q={address}"

    # Use inertia.location() for external redirect
    # This returns 409 Conflict with X-Inertia-Location header
    return inertia.location(maps_url)


@app.get("/cats/{cat_id}/apply")
async def show_application_form(cat_id: int, inertia: InertiaDep):
    """Show adoption application form"""
    cat = mock_data.get_cat_by_id(cat_id)

    if not cat:
        return inertia.render(
            "Error",
            {"title": "Not Found", "message": f"Cat {cat_id} not found"},
        )

    return inertia.render(
        "ApplicationForm",
        {
            "title": f"Apply to Adopt {cat['name']}",
            "cat": cat,
        },
    )


@app.post("/cats/{cat_id}/apply")
async def submit_application(cat_id: int, inertia: InertiaDep):
    """Handle adoption application submission with validation"""
    from fastapi import Request
    from fastapi.responses import RedirectResponse

    # Get form data (Inertia sends JSON, not form data)
    request: Request = inertia.request
    form_data = await request.json()

    # Validation
    errors = {}

    full_name = str(form_data.get("full_name", ""))
    email = str(form_data.get("email", ""))
    phone = str(form_data.get("phone", ""))
    address = str(form_data.get("address", ""))
    why_adopt = str(form_data.get("why_adopt", ""))

    # Validate required fields
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name is required (minimum 2 characters)"

    if not email or "@" not in email:
        errors["email"] = "A valid email address is required"

    if not phone or len(phone) < 10:
        errors["phone"] = "A valid phone number is required"

    if not address or len(address) < 10:
        errors["address"] = "A complete address is required"

    if not why_adopt or len(why_adopt) < 50:
        errors["why_adopt"] = (
            "Please tell us more about why you want to adopt (minimum 50 characters)"
        )

    # If there are errors, re-render the form with validation errors
    if errors:
        return inertia.render(
            "ApplicationForm",
            {
                "title": f"Apply to Adopt {mock_data.get_cat_by_id(cat_id)['name']}",
                "cat": mock_data.get_cat_by_id(cat_id),
            },
            errors=errors,
        )

    # Success - in a real app, you'd save to database and send confirmation email
    cat = mock_data.get_cat_by_id(cat_id)
    flash(
        inertia.request,
        f"Application submitted successfully! We'll review your application for {cat['name']} and contact you at {email} soon.",
        "success",
    )

    # Redirect back to the cat profile
    return RedirectResponse(url=f"/cats/{cat_id}", status_code=303)


@app.get("/users/{user_id}")
async def users_show(user_id: int, inertia: InertiaDep):
    """Show individual user."""
    # In a real app, you'd fetch from database
    users_data = {
        1: {
            "id": 1,
            "name": "Alice Johnson",
            "email": "alice@example.com",
            "role": "Admin",
            "joined": "2023-01-15",
        },
        2: {
            "id": 2,
            "name": "Bob Smith",
            "email": "bob@example.com",
            "role": "User",
            "joined": "2023-03-22",
        },
        3: {
            "id": 3,
            "name": "Carol White",
            "email": "carol@example.com",
            "role": "User",
            "joined": "2023-05-10",
        },
        4: {
            "id": 4,
            "name": "David Brown",
            "email": "david@example.com",
            "role": "Moderator",
            "joined": "2023-07-08",
        },
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
