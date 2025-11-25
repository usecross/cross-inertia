"""E2E tests for infinite scroll / merge props functionality.

The tests verify:
- Initial page shows correct number of cats (6)
- Load More button appears when more cats available
- Clicking Load More adds cats without replacing existing ones (merge props)
- Showing count updates correctly
- Load More disappears when all cats loaded
- Scroll position is preserved
- No duplicate cats appear (matchPropsOn working)
- Partial reload uses correct Inertia headers
"""

from playwright.sync_api import Page, expect


def test_initial_page_shows_first_batch(page: Page, fastapi_server: str) -> None:
    """Test that the browse page initially shows 6 cats (first page)."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for network to be idle (React app loaded)
    page.wait_for_load_state("networkidle")

    # Wait for React to hydrate - the page should have rendered content
    # The Layout component wraps content in a main element
    page.wait_for_selector("main", timeout=15000)

    # Should show "Showing X of Y" text
    expect(page.locator("text=Showing")).to_be_visible()

    # Initial load should show 6 cats (per_page=6 in the backend)
    # Look for View Profile links (they're inside buttons)
    view_profile_links = page.locator("a:has-text('View Profile')")
    expect(view_profile_links).to_have_count(6)


def test_load_more_button_visible_when_more_cats(
    page: Page, fastapi_server: str
) -> None:
    """Test that Load More button is visible when there are more cats."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Load More button should be visible
    load_more_button = page.locator("button:has-text('Load More')")
    expect(load_more_button).to_be_visible()


def test_infinite_scroll_loads_more_cats(page: Page, fastapi_server: str) -> None:
    """Test that clicking Load More adds more cats without replacing existing ones."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Count initial cats
    initial_links = page.locator("a:has-text('View Profile')")
    expect(initial_links).to_have_count(6)

    # Get the first card's link href to verify it's preserved after load more
    first_card_link = page.locator("a:has-text('View Profile')").first
    first_cat_href = first_card_link.get_attribute("href")

    # Click Load More
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()

    # Wait for the new cats to load
    page.wait_for_timeout(1500)

    # Should now have more cats (6 + 6 = 12)
    updated_links = page.locator("a:has-text('View Profile')")
    expect(updated_links).to_have_count(12)

    # First cat should still be there (merge props preserves existing data)
    # Verify by checking the first link href is still the same
    expect(page.locator("a:has-text('View Profile')").first).to_have_attribute(
        "href", first_cat_href
    )


def test_infinite_scroll_updates_showing_count(page: Page, fastapi_server: str) -> None:
    """Test that the 'Showing X of Y' count updates after loading more."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Initial count should show 6
    showing_text = page.locator("text=Showing")
    expect(showing_text).to_contain_text("6")

    # Click Load More
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()
    page.wait_for_timeout(1500)

    # Count should now show 12
    expect(showing_text).to_contain_text("12")


def test_load_more_button_disappears_at_end(page: Page, fastapi_server: str) -> None:
    """Test that Load More button disappears when all cats are loaded."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Keep clicking Load More until it disappears
    max_clicks = 10  # Safety limit
    for _ in range(max_clicks):
        load_more_button = page.locator("button:has-text('Load More')")
        if not load_more_button.is_visible():
            break
        load_more_button.click()
        page.wait_for_timeout(1000)

    # Load More should no longer be visible
    load_more_button = page.locator("button:has-text('Load More')")
    expect(load_more_button).not_to_be_visible()


def test_load_more_does_not_scroll_to_top(page: Page, fastapi_server: str) -> None:
    """Test that clicking Load More doesn't scroll back to the top of the page."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Scroll down to the Load More button area
    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    page.wait_for_timeout(500)

    # Click Load More
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()
    page.wait_for_timeout(1500)

    # Should NOT have scrolled back to top (scrollY should be > 0)
    final_scroll = page.evaluate("window.scrollY")
    assert final_scroll > 0, "Page scrolled back to top after Load More"


def test_merge_props_prevents_duplicates(page: Page, fastapi_server: str) -> None:
    """Test that merge props with matchPropsOn prevents duplicate cats."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Load more cats
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()
    page.wait_for_timeout(1500)

    # Get all cat names (using CardTitle which has class text-xl)
    cat_names = page.locator("h3").all_inner_texts()

    # Check for duplicates
    unique_names = set(cat_names)
    assert len(cat_names) == len(unique_names), f"Found duplicate cats: {cat_names}"


def test_inertia_partial_reload_headers(page: Page, fastapi_server: str) -> None:
    """Test that Load More uses Inertia partial reload (only fetches needed props)."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Set up request interception to check headers
    requests_made = []

    def handle_request(request):
        if "/browse" in request.url and "page=" in request.url:
            requests_made.append(
                {
                    "url": request.url,
                    "headers": request.headers,
                }
            )

    page.on("request", handle_request)

    # Click Load More
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()
    page.wait_for_timeout(1500)

    # Should have made a request with X-Inertia header
    assert len(requests_made) > 0, "No requests intercepted"

    inertia_request = requests_made[-1]
    assert inertia_request["headers"].get("x-inertia") == "true", (
        "Request should have X-Inertia header"
    )


# ============================================================================
# Filter Reset Tests - X-Inertia-Reset header functionality
# ============================================================================


def test_filter_ui_visible(page: Page, fastapi_server: str) -> None:
    """Test that filter dropdowns are visible on the browse page."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Check filter elements are visible
    breed_filter = page.locator("[data-testid='breed-filter']")
    age_filter = page.locator("[data-testid='age-filter']")

    expect(breed_filter).to_be_visible()
    expect(age_filter).to_be_visible()


def test_filter_by_breed_resets_data(page: Page, fastapi_server: str) -> None:
    """Test that selecting a breed filter resets the cats list (not append)."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Load more cats first to have more than initial batch
    load_more_button = page.locator("button:has-text('Load More')")
    load_more_button.click()
    page.wait_for_timeout(1500)

    # Should have 12 cats now (6 + 6)
    cats_before_filter = page.locator("a:has-text('View Profile')").count()
    assert cats_before_filter == 12, f"Expected 12 cats, got {cats_before_filter}"

    # Now select a breed filter
    breed_filter = page.locator("[data-testid='breed-filter']")
    breed_filter.select_option("Maine Coon")

    # Wait for the filter to apply
    page.wait_for_timeout(1500)

    # The count should be reset (not appended) - should show only filtered results
    cats_after_filter = page.locator("a:has-text('View Profile')").count()

    # Key assertion: after filtering, we should NOT have 12+ cats
    # If reset worked, we'll have fewer cats (only Maine Coons)
    assert cats_after_filter < cats_before_filter, (
        f"Filter should reset data, but got {cats_after_filter} cats "
        f"(expected less than {cats_before_filter})"
    )


def test_filter_sends_reset_header(page: Page, fastapi_server: str) -> None:
    """Test that changing filter sends X-Inertia-Reset header."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Set up request interception to check headers
    requests_made = []

    def handle_request(request):
        if "/browse" in request.url and "breed=" in request.url:
            requests_made.append(
                {
                    "url": request.url,
                    "headers": dict(request.headers),
                }
            )

    page.on("request", handle_request)

    # Select a breed filter
    breed_filter = page.locator("[data-testid='breed-filter']")
    breed_filter.select_option("Maine Coon")

    # Wait for the request
    page.wait_for_timeout(1500)

    # Should have made a request with X-Inertia-Reset header
    assert len(requests_made) > 0, "No filter requests intercepted"

    filter_request = requests_made[-1]
    assert filter_request["headers"].get("x-inertia") == "true", (
        "Request should have X-Inertia header"
    )
    assert filter_request["headers"].get("x-inertia-reset") == "cats", (
        f"Request should have X-Inertia-Reset: cats header, got: "
        f"{filter_request['headers'].get('x-inertia-reset')}"
    )


def test_clear_filters_resets_data(page: Page, fastapi_server: str) -> None:
    """Test that clearing filters resets to showing all cats."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Wait for content to load
    page.wait_for_selector("text=Showing")

    # Select a breed filter to reduce results
    breed_filter = page.locator("[data-testid='breed-filter']")
    breed_filter.select_option("Maine Coon")
    page.wait_for_timeout(1500)

    # Clear filters button should appear
    clear_button = page.locator("[data-testid='clear-filters']")
    expect(clear_button).to_be_visible()

    # Click clear filters
    clear_button.click()
    page.wait_for_timeout(1500)

    # Should be back to showing all cats (6 initial)
    cats_count = page.locator("a:has-text('View Profile')").count()
    assert cats_count == 6, f"Expected 6 cats after clearing, got {cats_count}"


def test_filter_then_load_more_works(page: Page, fastapi_server: str) -> None:
    """Test that Load More still works after applying a filter."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Note: With current mock data, some breeds may have < 6 cats
    # so Load More might not appear. Let's use age filter instead
    # which should have more results

    age_filter = page.locator("[data-testid='age-filter']")
    age_filter.select_option("adult")  # Adult cats (3-7 years)
    page.wait_for_timeout(1500)

    initial_count = page.locator("a:has-text('View Profile')").count()

    # If there's a Load More button, click it
    load_more = page.locator("button:has-text('Load More')")
    if load_more.is_visible():
        load_more.click()
        page.wait_for_timeout(1500)

        # Should have more cats now (merged, not replaced)
        new_count = page.locator("a:has-text('View Profile')").count()
        assert new_count > initial_count, (
            f"Load More should add cats, got {new_count} (was {initial_count})"
        )


def test_active_filter_badges_shown(page: Page, fastapi_server: str) -> None:
    """Test that active filter badges are displayed."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Select a breed filter
    breed_filter = page.locator("[data-testid='breed-filter']")
    breed_filter.select_option("Maine Coon")
    page.wait_for_timeout(1500)

    # Should show active filter badge
    badge = page.locator("text=Breed: Maine Coon")
    expect(badge).to_be_visible()


def test_filter_url_updates(page: Page, fastapi_server: str) -> None:
    """Test that the URL updates when filters are applied."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for React to hydrate
    page.wait_for_selector("h1:has-text('Browse Cats')", timeout=10000)

    # Select a breed filter
    breed_filter = page.locator("[data-testid='breed-filter']")
    breed_filter.select_option("Maine Coon")
    page.wait_for_timeout(1500)

    # URL should contain the breed parameter
    assert "breed=Maine" in page.url or "breed=Maine%20Coon" in page.url, (
        f"URL should contain breed filter, got: {page.url}"
    )
