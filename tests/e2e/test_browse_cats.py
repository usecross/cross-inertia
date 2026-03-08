"""E2E tests for browsing and favoriting cats."""

import re

from playwright.sync_api import Page, expect


def test_browse_page_loads(page: Page, fastapi_server: str) -> None:
    """Test that the browse page loads correctly."""
    page.goto(f"{fastapi_server}/browse")

    # Check page title
    expect(page).to_have_title("Browse Adoptable Cats - PurrfectHome")

    # Check heading (use more specific selector)
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Check that cats are displayed
    expect(page.locator("text=Showing")).to_be_visible()
    expect(page.locator("text=adorable cats available for adoption")).to_be_visible()

    # Should have cat cards
    cat_cards = page.locator('[data-testid^="view-profile-"]')
    expect(cat_cards).to_have_count(6)


def test_favorite_cat(page: Page, fastapi_server: str) -> None:
    """Test favoriting a cat updates the favorites count."""
    page.goto(f"{fastapi_server}/browse")

    # Initially, favorites count should be 0 (or empty)
    favorites_link = page.locator('[data-testid="favorites-link"]')
    expect(favorites_link).to_be_visible()

    # Click the first favorite button (heart icon)
    page.locator('[data-testid="favorite-1"]').click()

    # Flash message should appear
    expect(page.locator('[data-testid="flash-message"]')).to_contain_text(
        "to your favorites!"
    )

    # Favorites count should update
    expect(page.locator('[data-testid="favorites-badge"]')).to_have_text("1")


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
    nav.locator('[data-testid="favorites-link"]').click()

    # Should navigate to favorites page
    expect(page).to_have_url(f"{fastapi_server}/favorites")


def test_cat_profile_navigation(page: Page, fastapi_server: str) -> None:
    """Test clicking on a cat navigates to profile page."""
    page.goto(f"{fastapi_server}/browse")

    # Click "View Profile" on first cat
    page.locator('[data-testid="view-profile-1"]').click()

    # Should be on a cat profile page (check URL pattern)
    expect(page).to_have_url(re.compile(r".*/cats/1$"))

    # Should have personality section
    expect(page.locator("text=Personality")).to_be_visible()

    # Should have adoption information
    expect(page.locator("text=Adoption Fee")).to_be_visible()


def test_inertia_page_transitions(page: Page, fastapi_server: str) -> None:
    """Test that Inertia.js page transitions work without full reload."""
    page.goto(f"{fastapi_server}/browse")

    # Navigate to a cat profile
    page.locator('[data-testid="view-profile-1"]').click()
    expect(page).to_have_url(re.compile(r".*/cats/1$"))

    # Navigate back to browse
    page.locator('[data-testid="browse-link"]').click(force=True)
    expect(page).to_have_url(f"{fastapi_server}/browse")

    # Check that we're back on browse page
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Performance navigation type should not be 'reload'
    # (This verifies it was an SPA transition, not a full page reload)
    nav_type = page.evaluate(
        "() => performance.getEntriesByType('navigation')[0]?.type"
    )
    assert nav_type != "reload", "Should use SPA navigation, not full page reload"
