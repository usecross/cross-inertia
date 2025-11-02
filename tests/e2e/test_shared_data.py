"""E2E tests for shared data (flash messages, auth, favorites count)."""

from playwright.sync_api import Page, expect


def test_flash_messages_appear_and_dismiss(page: Page, fastapi_server: str) -> None:
    """Test that flash messages appear and can be dismissed."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for page to fully load
    expect(page.locator("main h1")).to_contain_text("Browse")

    # Click favorite button to trigger flash message (use 5th cat to avoid conflicts with other tests)
    favorite_button = page.locator("button").filter(has=page.locator("svg")).nth(4)
    favorite_button.click()

    # Wait for flash message to appear (it comes from server response)
    page.wait_for_timeout(1000)

    # Flash message should be visible - check for any flash message (Added or Removed)
    flash_message_text = page.locator("p.font-medium").first
    expect(flash_message_text).to_be_visible()
    # Verify it contains one of the expected texts
    content = flash_message_text.inner_text()
    assert "favorites" in content.lower(), f"Expected favorites message, got: {content}"

    # Click the close button (X icon) - it's in the parent div
    close_button = (
        page.locator("div.container button").filter(has=page.locator("svg")).first
    )
    close_button.click()

    # Flash message should disappear
    expect(flash_message_text).not_to_be_visible()


def test_flash_messages_auto_dismiss(page: Page, fastapi_server: str) -> None:
    """Test that flash messages auto-dismiss after 5 seconds."""
    page.goto(f"{fastapi_server}/browse")

    # Trigger flash message (use 8th cat to avoid conflicts)
    favorite_button = page.locator("button").filter(has=page.locator("svg")).nth(7)
    favorite_button.click()
    page.wait_for_timeout(1000)

    # Flash message should be visible (check for any flash message)
    flash_message = page.locator("p.font-medium").first
    expect(flash_message).to_be_visible()

    # Wait 5+ seconds
    page.wait_for_timeout(5500)

    # Flash message should have auto-dismissed
    expect(flash_message).not_to_be_visible()


def test_favorites_count_updates_in_real_time(page: Page, fastapi_server: str) -> None:
    """Test that favorites count badge updates without page reload."""
    page.goto(f"{fastapi_server}/browse")

    # Wait for page to fully load
    expect(page.locator("main h1")).to_contain_text("Browse")

    # Get initial favorites count
    favorites_badge = page.locator("nav a[href='/favorites'] span.bg-white")
    initial_visible = favorites_badge.is_visible()
    if initial_visible:
        initial_count = int(favorites_badge.inner_text())
    else:
        initial_count = 0

    # Click a favorite button (use 6th cat to avoid conflicts)
    page.locator("button").filter(has=page.locator("svg")).nth(5).click()
    page.wait_for_timeout(1000)

    # Count badge should be visible and show a count
    expect(favorites_badge).to_be_visible()
    count_after_first = int(favorites_badge.inner_text())
    # Count should have changed from initial
    assert count_after_first != initial_count, (
        "Count should have changed after favoriting"
    )

    # Click another favorite button (10th cat to ensure it's not favorited yet)
    page.locator("button").filter(has=page.locator("svg")).nth(9).click()
    page.wait_for_timeout(1000)

    # Count should have changed again
    count_after_second = int(favorites_badge.inner_text())
    assert count_after_second != count_after_first, (
        "Count should have changed after second favorite"
    )


def test_user_info_appears_in_header(page: Page, fastapi_server: str) -> None:
    """Test that shared user data appears in the header."""
    page.goto(f"{fastapi_server}/browse")

    # User name should be visible
    expect(page.locator("text=John Doe")).to_be_visible()


def test_flash_message_persists_across_redirect(
    page: Page, fastapi_server: str
) -> None:
    """Test that flash messages survive POST -> 303 redirect -> GET cycle."""
    # Submit application form
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Fill and submit form
    page.fill("input[id='full_name']", "Test User")
    page.fill("input[id='email']", "test@example.com")
    page.fill("input[id='phone']", "(555) 111-2222")
    page.fill("input[id='address']", "123 Test St, Test City, TC 12345")
    page.fill("textarea[id='why_adopt']", "I love cats!" * 10)  # 130 characters

    page.locator("button:has-text('Submit Application')").click()
    page.wait_for_timeout(500)

    # Flash message should appear on the cat profile page (after redirect)
    expect(page.locator("text=Application submitted successfully!")).to_be_visible()
    expect(page.locator("text=test@example.com")).to_be_visible()


def test_shared_data_included_in_partial_reloads(
    page: Page, fastapi_server: str
) -> None:
    """Test that shared data is included even in partial reloads."""
    page.goto(f"{fastapi_server}/browse")

    # Get initial favorites count
    favorites_badge = page.locator("nav a[href='/favorites'] span.bg-white")
    initial_visible = favorites_badge.is_visible()
    if initial_visible:
        initial_count = int(favorites_badge.inner_text())
    else:
        initial_count = 0

    # Favorite a cat (this does a partial reload with only: ['cats']) - use 11th cat
    favorite_button = page.locator("button").filter(has=page.locator("svg")).nth(10)
    favorite_button.click()
    page.wait_for_timeout(1000)

    # All shared data should still be present:
    # 1. User name
    expect(page.locator("text=John Doe")).to_be_visible()

    # 2. Favorites count (should have changed)
    new_count = int(favorites_badge.inner_text())
    assert new_count != initial_count, "Favorites count should have changed"

    # 3. Flash message
    flash_message = page.locator("p.font-medium").first
    expect(flash_message).to_be_visible()
