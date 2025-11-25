"""E2E tests for error bags - scoped validation errors for multiple forms."""

from playwright.sync_api import Page, expect


def test_error_bags_page_loads(page: Page, fastapi_server: str) -> None:
    """Test that the error bags demo page loads correctly."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Check page loaded with both forms
    expect(page.locator("main h1")).to_contain_text("Error Bags Demo")
    expect(page.locator("text=Login Form")).to_be_visible()
    expect(page.locator("text=Register Form")).to_be_visible()


def test_login_form_error_bag_scoping(page: Page, fastapi_server: str) -> None:
    """Test that login form errors are scoped under 'login' error bag."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Submit empty login form
    page.locator('[data-testid="login-submit"]').click()
    page.wait_for_timeout(500)

    # Should show login errors
    expect(page.locator('[data-testid="login-errors"]')).to_be_visible()
    expect(page.locator("text=Please enter a valid email address")).to_be_visible()
    expect(page.locator("text=Password must be at least 6 characters")).to_be_visible()

    # Register errors should NOT be visible
    expect(page.locator('[data-testid="register-errors"]')).not_to_be_visible()


def test_register_form_error_bag_scoping(page: Page, fastapi_server: str) -> None:
    """Test that register form errors are scoped under 'register' error bag."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Submit empty register form
    page.locator('[data-testid="register-submit"]').click()
    page.wait_for_timeout(500)

    # Should show register errors
    expect(page.locator('[data-testid="register-errors"]')).to_be_visible()
    expect(page.locator("text=Name must be at least 2 characters")).to_be_visible()

    # Login errors should NOT be visible
    expect(page.locator('[data-testid="login-errors"]')).not_to_be_visible()


def test_error_bags_are_independent(page: Page, fastapi_server: str) -> None:
    """Test that submitting one form doesn't affect the other form's errors."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Submit login form with errors
    page.locator('[data-testid="login-submit"]').click()
    page.wait_for_timeout(500)

    # Verify login errors visible, register errors not
    expect(page.locator('[data-testid="login-errors"]')).to_be_visible()
    expect(page.locator('[data-testid="register-errors"]')).not_to_be_visible()

    # Now submit register form
    page.locator('[data-testid="register-submit"]').click()
    page.wait_for_timeout(500)

    # Now register errors should be visible, login errors cleared
    # (because we're re-rendering the page with new errors)
    expect(page.locator('[data-testid="register-errors"]')).to_be_visible()
    expect(page.locator('[data-testid="login-errors"]')).not_to_be_visible()


def test_login_form_validation_passes(page: Page, fastapi_server: str) -> None:
    """Test that valid login form data passes validation."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Fill out valid login form
    page.locator('[data-testid="login-email"]').fill("test@example.com")
    page.locator('[data-testid="login-password"]').fill("password123")

    # Submit
    page.locator('[data-testid="login-submit"]').click()
    page.wait_for_timeout(500)

    # Should not show login errors
    expect(page.locator('[data-testid="login-errors"]')).not_to_be_visible()


def test_register_form_validation_passes(page: Page, fastapi_server: str) -> None:
    """Test that valid register form data passes validation."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Fill out valid register form
    page.locator('[data-testid="register-name"]').fill("John Doe")
    page.locator('[data-testid="register-email"]').fill("john@example.com")
    page.locator('[data-testid="register-password"]').fill("password123")

    # Submit
    page.locator('[data-testid="register-submit"]').click()
    page.wait_for_timeout(500)

    # Should not show register errors
    expect(page.locator('[data-testid="register-errors"]')).not_to_be_visible()


def test_partial_login_validation(page: Page, fastapi_server: str) -> None:
    """Test login form with only email filled shows only password error."""
    page.goto(f"{fastapi_server}/error-bags-demo")

    # Fill only email
    page.locator('[data-testid="login-email"]').fill("test@example.com")

    # Submit
    page.locator('[data-testid="login-submit"]').click()
    page.wait_for_timeout(500)

    # Should show password error but not email error
    expect(page.locator('[data-testid="login-errors"]')).to_be_visible()
    expect(page.locator("text=Password must be at least 6 characters")).to_be_visible()
    # Email error should not be shown (valid email was provided)
    expect(
        page.locator('[data-testid="login-errors"]').locator(
            "text=Please enter a valid email address"
        )
    ).not_to_be_visible()
