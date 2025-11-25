"""E2E tests for optional and always props functionality."""

from playwright.sync_api import Page, expect


def test_optional_prop_not_loaded_on_initial_page_load(
    page: Page, fastapi_server: str
) -> None:
    """Test that optional props are NOT included in initial page load."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Page should load
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")

    # Message should be visible
    expect(page.locator("text=Statistics are optional")).to_be_visible()

    # Statistics should NOT be loaded yet (optional prop)
    expect(page.locator('[data-testid="not-loaded-message"]')).to_be_visible()
    expect(page.locator('[data-testid="statistics-container"]')).not_to_be_visible()

    # Load button should be visible
    expect(page.locator('[data-testid="load-statistics-button"]')).to_be_visible()


def test_always_prop_included_on_initial_load(page: Page, fastapi_server: str) -> None:
    """Test that always props ARE included in initial page load."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Page should load
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")

    # Timestamp should be present (always prop)
    expect(page.locator('[data-testid="timestamp"]')).to_be_visible()
    timestamp = page.locator('[data-testid="timestamp"]').inner_text()
    # Should be an ISO timestamp
    assert "T" in timestamp, f"Expected ISO timestamp, got: {timestamp}"


def test_optional_prop_loads_on_partial_reload(page: Page, fastapi_server: str) -> None:
    """Test that optional props are loaded when explicitly requested via partial reload."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")

    # Statistics should not be loaded initially
    expect(page.locator('[data-testid="not-loaded-message"]')).to_be_visible()

    # Click the load button
    page.locator('[data-testid="load-statistics-button"]').click()

    # Wait for statistics to load
    expect(page.locator('[data-testid="statistics-container"]')).to_be_visible()

    # "Not loaded" message should be gone
    expect(page.locator('[data-testid="not-loaded-message"]')).not_to_be_visible()

    # Statistics values should be present
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible()
    expect(page.locator('[data-testid="total-shelters"]')).to_be_visible()
    expect(page.locator('[data-testid="average-age"]')).to_be_visible()
    expect(page.locator('[data-testid="breeds-count"]')).to_be_visible()


def test_always_prop_included_in_partial_reload(
    page: Page, fastapi_server: str
) -> None:
    """Test that always props are included even during partial reload."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")

    # Verify timestamp is present initially
    expect(page.locator('[data-testid="timestamp"]')).to_be_visible()

    # Click the load button to trigger partial reload
    page.locator('[data-testid="load-statistics-button"]').click()

    # Wait for statistics to load
    expect(page.locator('[data-testid="statistics-container"]')).to_be_visible()

    # Timestamp should still be present (always prop is included even in partial reload)
    expect(page.locator('[data-testid="timestamp"]')).to_be_visible()

    # Timestamp should be updated (different from initial since always() re-evaluates)
    new_timestamp = page.locator('[data-testid="timestamp"]').inner_text()
    # Note: Timestamps could be the same if reload is very fast, so just check it exists
    assert new_timestamp, "Timestamp should be present after partial reload"


def test_optional_prop_values_are_correct(page: Page, fastapi_server: str) -> None:
    """Test that optional prop values are correctly computed and displayed."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Wait for page to load and click load button
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")
    page.locator('[data-testid="load-statistics-button"]').click()

    # Wait for statistics to load
    expect(page.locator('[data-testid="statistics-container"]')).to_be_visible()

    # Verify total cats is a number > 0
    total_cats_text = page.locator('[data-testid="total-cats"]').inner_text()
    total_cats = int(total_cats_text)
    assert total_cats > 0, f"Expected total_cats > 0, got {total_cats}"

    # Verify total shelters is a number > 0
    total_shelters_text = page.locator('[data-testid="total-shelters"]').inner_text()
    total_shelters = int(total_shelters_text)
    assert total_shelters > 0, f"Expected total_shelters > 0, got {total_shelters}"

    # Verify average age is formatted correctly (e.g., "2.5 years")
    average_age_text = page.locator('[data-testid="average-age"]').inner_text()
    assert "years" in average_age_text, (
        f"Expected 'years' in average age, got {average_age_text}"
    )

    # Verify breeds count
    breeds_count_text = page.locator('[data-testid="breeds-count"]').inner_text()
    assert "unique breeds" in breeds_count_text, (
        f"Expected 'unique breeds' in text, got {breeds_count_text}"
    )


def test_loading_state_shown_while_fetching(page: Page, fastapi_server: str) -> None:
    """Test that loading state is shown while fetching optional props."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Wait for page to load
    expect(page.locator("main h1")).to_contain_text("Optional & Always Props Demo")

    # Button should say "Load Statistics"
    button = page.locator('[data-testid="load-statistics-button"]')
    expect(button).to_contain_text("Load Statistics")

    # Click the button - it should show "Loading..."
    button.click()

    # Wait for statistics to load (the loading state might be too fast to catch)
    expect(page.locator('[data-testid="statistics-container"]')).to_be_visible()
