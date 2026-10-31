"""E2E tests for validation errors on partial reload submissions."""

from playwright.sync_api import Page, expect


def test_valid_partial_submission_clears_previous_errors(
    page: Page, fastapi_server: str
) -> None:
    page.goto(f"{fastapi_server}/partial-errors-demo")

    page.locator('[data-testid="partial-name"]').fill("A")
    page.locator('[data-testid="partial-submit"]').click()

    expect(page.locator('[data-testid="partial-name-error"]')).to_have_text(
        "Name must be at least 2 characters"
    )
    expect(page.locator('[data-testid="partial-result"]')).to_have_text("error")

    page.locator('[data-testid="partial-name"]').fill("Grace")
    page.locator('[data-testid="partial-submit"]').click()

    expect(page.locator('[data-testid="partial-result"]')).to_have_text("success")
    expect(page.locator('[data-testid="partial-name-error"]')).not_to_be_visible()
    expect(page.locator('[data-testid="saved-name"]')).to_have_text("Grace")
