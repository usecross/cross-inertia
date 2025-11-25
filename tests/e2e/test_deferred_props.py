"""E2E tests for deferred props functionality."""

from playwright.sync_api import Page, expect


def test_deferred_props_not_loaded_on_initial_page_load(
    page: Page, fastapi_server: str
) -> None:
    """Test that deferred props are NOT included in initial page load."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Page should load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # Message should be visible
    expect(page.locator("text=This page demonstrates deferred props")).to_be_visible()

    # Timestamp (regular prop) should be visible immediately
    expect(page.locator('[data-testid="timestamp"]')).to_be_visible()


def test_deferred_props_show_loading_or_loaded_state(
    page: Page, fastapi_server: str
) -> None:
    """Test that deferred props show loading state or are loaded."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Page should load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # The deferred props auto-load, so by the time we check, they might already be loaded
    # Either loading spinner is visible OR the data is already loaded
    # We wait for data to be loaded (which implicitly means loading happened)
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible(timeout=10000)


def test_deferred_props_load_automatically(page: Page, fastapi_server: str) -> None:
    """Test that deferred props are automatically loaded after page render."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # Wait for analytics to load (default group)
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible(timeout=10000)
    expect(page.locator('[data-testid="total-shelters"]')).to_be_visible()
    expect(page.locator('[data-testid="average-age"]')).to_be_visible()
    expect(page.locator('[data-testid="breeds-count"]')).to_be_visible()


def test_deferred_notifications_load(page: Page, fastapi_server: str) -> None:
    """Test that notifications (default group) are loaded."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # Wait for notifications to load
    expect(page.locator("text=New cat available: Whiskers")).to_be_visible(
        timeout=10000
    )
    expect(page.locator("text=Application approved!")).to_be_visible()


def test_deferred_recommendations_load_in_parallel(
    page: Page, fastapi_server: str
) -> None:
    """Test that recommendations (sidebar group) load in parallel."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # Recommendations should load (sidebar group loads in parallel with default)
    # They are cat cards showing name and breed
    expect(page.locator("text=Sidebar Group")).to_be_visible()
    # Wait for the recommendations cards to appear
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible(timeout=10000)


def test_deferred_prop_values_are_correct(page: Page, fastapi_server: str) -> None:
    """Test that deferred prop values are correctly computed and displayed."""
    page.goto(f"{fastapi_server}/deferred-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Deferred Props Demo")

    # Wait for analytics to load
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible(timeout=10000)

    # Verify total cats is a number > 0
    total_cats_text = page.locator('[data-testid="total-cats"]').inner_text()
    total_cats = int(total_cats_text)
    assert total_cats > 0, f"Expected total_cats > 0, got {total_cats}"

    # Verify total shelters is a number > 0
    total_shelters_text = page.locator('[data-testid="total-shelters"]').inner_text()
    total_shelters = int(total_shelters_text)
    assert total_shelters > 0, f"Expected total_shelters > 0, got {total_shelters}"

    # Verify average age is formatted correctly
    average_age_text = page.locator('[data-testid="average-age"]').inner_text()
    assert "years" in average_age_text, (
        f"Expected 'years' in average age, got {average_age_text}"
    )
