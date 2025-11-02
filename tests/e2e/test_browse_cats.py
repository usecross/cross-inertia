"""E2E tests for browsing and favoriting cats."""

from playwright.sync_api import Page, expect


def test_browse_page_loads(page: Page, fastapi_server: str) -> None:
    """Test that the browse page loads correctly."""
    page.goto(f"{fastapi_server}/browse")

    # Check page title
    expect(page).to_have_title("Inertia FastAPI Demo")

    # Check heading (use more specific selector)
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Check that cats are displayed
    expect(page.locator("text=Showing")).to_be_visible()
    expect(page.locator("text=adorable cats available for adoption")).to_be_visible()

    # Should have cat cards
    cat_cards = page.locator("img[alt]")
    expect(cat_cards).to_have_count(12)  # Default page size


def test_favorite_cat(page: Page, fastapi_server: str) -> None:
    """Test favoriting a cat updates the favorites count."""
    page.goto(f"{fastapi_server}/browse")

    # Initially, favorites count should be 0 (or empty)
    favorites_link = page.locator("text=Favorites")
    expect(favorites_link).to_be_visible()

    # Click the first favorite button (heart icon)
    first_favorite_button = page.locator("button").filter(has=page.locator("svg")).first
    first_favorite_button.click()

    # Wait for navigation (Inertia page transition)
    page.wait_for_timeout(500)

    # Flash message should appear
    expect(page.locator("text=to your favorites!")).to_be_visible()

    # Favorites count should update
    expect(page.locator("text=Favorites").locator("text=1")).to_be_visible()


def test_navigation_header(page: Page, fastapi_server: str) -> None:
    """Test that navigation links work."""
    page.goto(f"{fastapi_server}/browse")

    # Check navigation links exist (in nav element)
    nav = page.locator("nav")
    expect(nav.locator("text=PurrfectHome")).to_be_visible()
    expect(nav.locator("text=Browse")).to_be_visible()
    expect(nav.locator("text=Favorites")).to_be_visible()

    # User name should be displayed
    expect(nav.locator("text=John Doe")).to_be_visible()

    # Click favorites link
    nav.locator("text=Favorites").click()
    page.wait_for_timeout(500)

    # Should navigate to favorites page
    expect(page).to_have_url(f"{fastapi_server}/favorites")


def test_cat_profile_navigation(page: Page, fastapi_server: str) -> None:
    """Test clicking on a cat navigates to profile page."""
    page.goto(f"{fastapi_server}/browse")

    # Click "View Profile" on first cat
    first_profile_link = page.locator("text=View Profile").first
    first_profile_link.click()

    # Wait for navigation
    page.wait_for_timeout(500)

    # Should be on a cat profile page (check URL pattern)
    import re

    assert re.match(r".*/cats/\d+$", page.url), (
        f"Expected cat profile URL, got {page.url}"
    )

    # Should have personality section
    expect(page.locator("text=Personality")).to_be_visible()

    # Should have adoption information
    expect(page.locator("text=Adoption Fee")).to_be_visible()


def test_inertia_page_transitions(page: Page, fastapi_server: str) -> None:
    """Test that Inertia.js page transitions work without full reload."""
    page.goto(f"{fastapi_server}/browse")

    # Navigate to a cat profile
    page.locator("text=View Profile").first.click()
    page.wait_for_timeout(300)

    # Navigate back to browse
    nav = page.locator("nav")
    nav.locator("text=Browse").click()
    page.wait_for_timeout(300)

    # Check that we're back on browse page
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Performance navigation type should not be 'reload'
    # (This verifies it was an SPA transition, not a full page reload)
    nav_type = page.evaluate(
        "() => performance.getEntriesByType('navigation')[0]?.type"
    )
    assert nav_type != "reload", "Should use SPA navigation, not full page reload"
