"""E2E tests for once props and the v3 client behavior around them."""

from playwright.sync_api import Page, expect


def test_once_props_are_remembered_until_explicitly_reloaded(
    page: Page, fastapi_server: str
) -> None:
    """The browser should remember once props, then refresh them when requested."""
    page.goto(f"{fastapi_server}/once-demo")

    expect(page.locator("main h1")).to_contain_text("Once Props Demo")

    initial_offer = page.locator('[data-testid="offer-code"]').inner_text()
    initial_request_count = int(
        page.locator('[data-testid="request-count"]').inner_text()
    )
    initial_once_evaluations = int(
        page.locator('[data-testid="once-evaluations"]').inner_text()
    )

    assert initial_offer.startswith("WELCOME-")
    assert initial_once_evaluations >= 1

    with page.expect_request(
        lambda request: request.url == f"{fastapi_server}/once-demo"
        and request.headers.get("x-inertia") == "true"
        and "request_count" in request.headers.get("x-inertia-partial-data", "")
    ) as diagnostics_request_info:
        page.locator('[data-testid="reload-diagnostics"]').click()

    diagnostics_request = diagnostics_request_info.value
    assert diagnostics_request.headers.get("x-inertia-except-once-props") == (
        "welcome-offer-cache"
    )

    expect(page.locator('[data-testid="request-count"]')).to_have_text(
        str(initial_request_count + 1)
    )
    expect(page.locator('[data-testid="once-evaluations"]')).to_have_text(
        str(initial_once_evaluations)
    )
    expect(page.locator('[data-testid="offer-code"]')).to_have_text(initial_offer)

    with page.expect_request(
        lambda request: request.url == f"{fastapi_server}/once-demo"
        and request.headers.get("x-inertia") == "true"
        and "offer" in request.headers.get("x-inertia-partial-data", "")
    ) as refresh_request_info:
        page.locator('[data-testid="refresh-offer"]').click()

    refresh_request = refresh_request_info.value
    assert refresh_request.headers.get("x-inertia-except-once-props") == (
        "welcome-offer-cache"
    )

    expect(page.locator('[data-testid="request-count"]')).to_have_text(
        str(initial_request_count + 2)
    )
    expect(page.locator('[data-testid="once-evaluations"]')).to_have_text(
        str(initial_once_evaluations + 1)
    )
    expect(page.locator('[data-testid="offer-code"]')).not_to_have_text(initial_offer)
