"""E2E tests for the adoption application form."""

import re

from playwright.sync_api import Page, expect


def test_application_form_validation(page: Page, fastapi_server: str) -> None:
    """Test that form validation works correctly."""
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Check form loaded
    expect(page.locator("main h1")).to_contain_text("Adoption Application")

    # Submit empty form
    page.locator("button:has-text('Submit Application')").click()
    page.wait_for_timeout(500)

    # Should show validation errors (using more specific selectors for error messages)
    expect(
        page.locator("p.text-sm.text-red-500:has-text('Full name is required')")
    ).to_be_visible()
    expect(
        page.locator(
            "p.text-sm.text-red-500:has-text('valid email address is required')"
        )
    ).to_be_visible()
    expect(
        page.locator(
            "p.text-sm.text-red-500:has-text('valid phone number is required')"
        )
    ).to_be_visible()
    expect(
        page.locator("p.text-sm.text-red-500:has-text('complete address is required')")
    ).to_be_visible()
    expect(
        page.locator("p.text-sm.text-red-500:has-text('minimum 50 characters')")
    ).to_be_visible()


def test_application_form_submission(page: Page, fastapi_server: str) -> None:
    """Test successful form submission."""
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Fill out the form
    page.fill("input[id='full_name']", "Jane Smith")
    page.fill("input[id='email']", "jane@example.com")
    page.fill("input[id='phone']", "(555) 987-6543")
    page.fill("input[id='address']", "456 Oak Avenue, Portland, OR 97201")
    page.fill(
        "textarea[id='why_adopt']",
        "I have always loved cats and have experience caring for them. "
        "My home has plenty of space and I work from home, so I can provide "
        "lots of attention and care. I'm looking for a lifelong companion.",
    )

    # Submit the form
    page.locator("button:has-text('Submit Application')").click()

    # Wait for navigation
    page.wait_for_timeout(500)

    # Should redirect to cat profile
    assert re.match(r".*/cats/1$", page.url), (
        f"Expected URL to match /cats/1, got {page.url}"
    )

    # Should show success flash message
    expect(page.locator("text=Application submitted successfully!")).to_be_visible()
    expect(page.locator("text=jane@example.com")).to_be_visible()


def test_form_character_counter(page: Page, fastapi_server: str) -> None:
    """Test that the character counter updates as user types."""
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Initially should show 0 characters (use more specific selector)
    expect(
        page.locator("p.text-sm.text-muted-foreground:has-text('0 characters')")
    ).to_be_visible()

    # Type some text
    why_adopt_field = page.locator("textarea[id='why_adopt']")
    why_adopt_field.fill("This is a test message")

    # Character count should update
    expect(
        page.locator("p.text-sm.text-muted-foreground:has-text('22 characters')")
    ).to_be_visible()


def test_form_cancel_button(page: Page, fastapi_server: str) -> None:
    """Test that cancel button navigates back."""
    # First go to a cat profile
    page.goto(f"{fastapi_server}/cats/1")
    page.wait_for_timeout(300)

    # Click "Apply to Adopt"
    page.locator("text=Apply to Adopt").click()
    page.wait_for_timeout(300)

    # Should be on application form
    expect(page.locator("main h1")).to_contain_text("Adoption Application")

    # Click cancel
    page.locator("button:has-text('Cancel')").click()
    page.wait_for_timeout(300)

    # Should go back to cat profile
    assert re.match(r".*/cats/1$", page.url), (
        f"Expected URL to match /cats/1, got {page.url}"
    )
