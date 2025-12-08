---
title: Testing
description: Testing Inertia applications with pytest and Playwright
---

Testing Inertia applications involves two types of tests: unit tests for your endpoints and E2E tests for full user flows. This guide covers both approaches with practical examples.

## Unit Testing with pytest

Unit tests verify your endpoints return correct data without spinning up a browser. With Inertia, you'll typically test that your endpoints return the expected props and component.

### Basic Setup

Use FastAPI's `TestClient` to test your endpoints:

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)
```

### Testing Inertia Responses

When testing Inertia endpoints, add the `X-Inertia: true` header to get JSON responses instead of HTML:

```python
def test_browse_cats_returns_cats(client: TestClient):
    """Test that browse endpoint returns cat data."""
    response = client.get(
        "/browse",
        headers={"X-Inertia": "true"},
    )

    assert response.status_code == 200
    data = response.json()

    # Check component name
    assert data["component"] == "Browse"

    # Check props
    assert "cats" in data["props"]
    assert "total" in data["props"]
    assert len(data["props"]["cats"]["data"]) > 0


def test_browse_cats_with_filters(client: TestClient):
    """Test filtering cats by breed."""
    response = client.get(
        "/browse?breed=Persian",
        headers={"X-Inertia": "true"},
    )

    data = response.json()
    cats = data["props"]["cats"]["data"]

    # All returned cats should be Persian
    for cat in cats:
        assert cat["breed"] == "Persian"
```

### Testing Page Object Structure

Every Inertia response includes a page object with `component`, `props`, `url`, and `version`:

```python
def test_page_object_structure(client: TestClient):
    """Test that response has correct Inertia page structure."""
    response = client.get(
        "/browse",
        headers={"X-Inertia": "true"},
    )

    data = response.json()

    # Required fields per Inertia protocol
    assert "component" in data
    assert "props" in data
    assert "url" in data
    assert "version" in data

    # Verify response headers
    assert response.headers.get("X-Inertia") == "true"
    assert response.headers.get("Content-Type") == "application/json"
```

### Testing Validation Errors

Test that validation errors are properly returned in the `errors` prop:

```python
def test_application_form_validation(client: TestClient):
    """Test that invalid form submission returns validation errors."""
    response = client.post(
        "/cats/1/apply",
        headers={"X-Inertia": "true"},
        json={
            "full_name": "",  # Too short
            "email": "invalid",  # Invalid email
            "phone": "123",  # Too short
            "address": "short",  # Too short
            "why_adopt": "I like cats",  # Less than 50 chars
        },
    )

    data = response.json()

    # Inertia always returns 200, errors are in props
    assert response.status_code == 200
    errors = data["props"]["errors"]
    assert "Full name is required" in errors["full_name"]
    assert "valid email" in errors["email"]
    assert "valid phone" in errors["phone"]


def test_application_form_success(client: TestClient):
    """Test successful form submission redirects."""
    response = client.post(
        "/cats/1/apply",
        headers={"X-Inertia": "true"},
        json={
            "full_name": "John Doe",
            "email": "john@example.com",
            "phone": "(555) 123-4567",
            "address": "123 Main Street, Anytown, ST 12345",
            "why_adopt": "I have always loved cats and have a spacious home with a yard. I work from home so I can provide lots of attention.",
        },
        follow_redirects=False,
    )

    # Should redirect on success
    assert response.status_code == 303
    assert response.headers.get("Location") == "/cats/1"
```

### Testing Partial Reloads

Partial reloads let the frontend request specific props. Test that they work correctly:

```python
def test_partial_reload_only_specific_props(client: TestClient):
    """Test that partial reload returns only requested props."""
    response = client.get(
        "/browse",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Data": "cats,total",
            "X-Inertia-Partial-Component": "Browse",
        },
    )

    data = response.json()

    # Should only include requested props
    assert "cats" in data["props"]
    assert "total" in data["props"]
    # Other props should not be included
    assert "filters" not in data["props"]


def test_partial_reload_component_mismatch(client: TestClient):
    """Test that partial reload is ignored if component doesn't match."""
    response = client.get(
        "/browse",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Data": "cats",
            "X-Inertia-Partial-Component": "WrongComponent",
        },
    )

    data = response.json()

    # Should return ALL props when component doesn't match
    assert "cats" in data["props"]
    assert "total" in data["props"]
    assert "filters" in data["props"]
```

### Testing Optional Props

Optional props are only included when explicitly requested:

```python
def test_optional_props_excluded_initially(client: TestClient):
    """Test that optional props are NOT included on initial load."""
    response = client.get(
        "/lazy-demo",
        headers={"X-Inertia": "true"},
    )

    data = response.json()

    # Regular props should be included
    assert data["props"]["message"] is not None
    # Optional prop should NOT be included
    assert "statistics" not in data["props"]


def test_optional_props_included_when_requested(client: TestClient):
    """Test that optional props ARE included when explicitly requested."""
    response = client.get(
        "/lazy-demo",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Component": "LazyDemo",
            "X-Inertia-Partial-Data": "statistics",
        },
    )

    data = response.json()

    # Optional prop should be included and evaluated
    assert "statistics" in data["props"]
    assert "total_cats" in data["props"]["statistics"]
```

### Testing Always Props

Always props are included even during partial reloads:

```python
def test_always_props_included_on_partial_reload(client: TestClient):
    """Test that always props ARE included even when not requested."""
    response = client.get(
        "/lazy-demo",
        headers={
            "X-Inertia": "true",
            "X-Inertia-Partial-Component": "LazyDemo",
            "X-Inertia-Partial-Data": "message",  # Only request message
        },
    )

    data = response.json()

    # Message was requested
    assert data["props"]["message"] is not None
    # Timestamp is always() prop - should be included even though not requested
    assert "timestamp" in data["props"]
```

### Testing External Redirects

Test the `location()` method for external redirects:

```python
def test_external_redirect(client: TestClient):
    """Test that external redirects return correct response."""
    response = client.get(
        "/shelter/Happy%20Paws%20Shelter/directions",
        headers={"X-Inertia": "true"},
        follow_redirects=False,
    )

    # External redirects return 409 with X-Inertia-Location header
    assert response.status_code == 409
    assert "maps.google.com" in response.headers.get("X-Inertia-Location")
```

### Testing Shared Data

Shared data is automatically included in every response:

```python
def test_shared_data_included(client: TestClient):
    """Test that shared data is included in response."""
    response = client.get(
        "/browse",
        headers={"X-Inertia": "true"},
    )

    data = response.json()

    # Shared data should be present
    assert "auth" in data["props"]
    assert "user" in data["props"]["auth"]
    assert "favorites_count" in data["props"]
```

### Testing Initial HTML Responses

For initial page loads (without X-Inertia header), the response is HTML with embedded page data:

```python
import json


def test_initial_page_load_returns_html(client: TestClient):
    """Test that initial page load returns HTML."""
    response = client.get("/browse")

    assert response.status_code == 200
    assert response.headers.get("Content-Type").startswith("text/html")
    assert 'id="app"' in response.text
    assert "data-page=" in response.text


def test_page_data_embedded_in_html(client: TestClient):
    """Test that page object is embedded in HTML."""
    response = client.get("/browse")

    # Extract page data from HTML
    html = response.text
    start = html.find("data-page='") + len("data-page='")
    end = html.find("'", start)
    page_json = html[start:end]
    page_data = json.loads(page_json)

    # Verify structure
    assert page_data["component"] == "Browse"
    assert "cats" in page_data["props"]
```

## E2E Testing with Playwright

E2E tests verify complete user flows in a real browser.

### Basic Setup

Set up pytest fixtures for Playwright:

```python
# tests/e2e/conftest.py
import subprocess
import sys
import time
from pathlib import Path
from typing import Generator

import httpx
import pytest
from playwright.sync_api import Page


@pytest.fixture(scope="session")
def fastapi_server() -> Generator[str, None, None]:
    """Start the FastAPI server for E2E tests."""
    app_dir = Path(__file__).parent.parent.parent / "app"

    process = subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8888",
        ],
        cwd=str(app_dir),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait for server to be ready
    base_url = "http://127.0.0.1:8888"
    for _ in range(30):
        try:
            httpx.get(f"{base_url}/", timeout=0.5)
            break
        except (httpx.ConnectError, httpx.TimeoutException):
            time.sleep(0.1)
    else:
        stdout, stderr = process.communicate(timeout=1)
        raise RuntimeError(
            f"Server failed to start!\nSTDOUT:\n{stdout.decode()}\n\nSTDERR:\n{stderr.decode()}"
        )

    yield base_url

    process.terminate()
    process.wait(timeout=5)


@pytest.fixture
def page(page: Page, fastapi_server: str) -> Page:
    """Configure page with base URL."""
    page.set_default_timeout(10000)
    return page
```

### Testing Page Loads

```python
from playwright.sync_api import Page, expect


def test_browse_page_loads(page: Page, fastapi_server: str) -> None:
    """Test that the browse page loads correctly."""
    page.goto(f"{fastapi_server}/browse")

    # Check page title
    expect(page).to_have_title("Inertia FastAPI Demo")

    # Check heading
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Check that cats are displayed
    cat_cards = page.locator("img[alt]")
    expect(cat_cards).to_have_count(6)  # First page has 6 cats
```

### Testing SPA Navigation

Verify that Inertia handles navigation without full page reloads:

```python
def test_spa_navigation(page: Page, fastapi_server: str) -> None:
    """Test that Inertia.js page transitions work without full reload."""
    page.goto(f"{fastapi_server}/browse")

    # Navigate to a cat profile
    page.locator("text=View Profile").first.click()
    page.wait_for_timeout(300)

    # Check we're on a profile page
    expect(page.locator("text=Personality")).to_be_visible()

    # Navigate back to browse
    page.locator("nav a:has-text('Browse')").click()
    page.wait_for_timeout(300)

    # Check we're back on browse page
    expect(page.locator("main h1")).to_contain_text("Browse Cats")

    # Verify it was an SPA transition, not a full page reload
    nav_type = page.evaluate(
        "() => performance.getEntriesByType('navigation')[0]?.type"
    )
    assert nav_type != "reload", "Should use SPA navigation"
```

### Testing Form Submissions

```python
def test_application_form_validation(page: Page, fastapi_server: str) -> None:
    """Test form submission with validation errors."""
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Submit empty form
    page.locator("button:has-text('Submit')").click()
    page.wait_for_timeout(500)

    # Should show validation errors
    expect(page.locator("text=Full name is required")).to_be_visible()
    expect(page.locator("text=valid email")).to_be_visible()


def test_application_form_success(page: Page, fastapi_server: str) -> None:
    """Test successful form submission."""
    page.goto(f"{fastapi_server}/cats/1/apply")

    # Fill form correctly
    page.fill("input[id='full_name']", "Test User")
    page.fill("input[id='email']", "test@example.com")
    page.fill("input[id='phone']", "(555) 111-2222")
    page.fill("input[id='address']", "123 Test St, Test City, TC 12345")
    page.fill("textarea[id='why_adopt']", "I love cats!" * 10)

    page.locator("button:has-text('Submit')").click()
    page.wait_for_timeout(500)

    # Should show success flash message
    expect(page.locator("text=Application submitted successfully!")).to_be_visible()
```

### Testing Flash Messages

```python
def test_flash_messages_appear(page: Page, fastapi_server: str) -> None:
    """Test that flash messages appear after actions."""
    page.goto(f"{fastapi_server}/browse")

    # Click favorite button
    favorite_button = page.locator("button").filter(has=page.locator("svg")).first
    favorite_button.click()
    page.wait_for_timeout(500)

    # Flash message should be visible
    expect(page.locator("text=favorites")).to_be_visible()


def test_flash_messages_auto_dismiss(page: Page, fastapi_server: str) -> None:
    """Test that flash messages auto-dismiss after timeout."""
    page.goto(f"{fastapi_server}/browse")

    # Trigger flash message
    page.locator("button").filter(has=page.locator("svg")).first.click()
    page.wait_for_timeout(500)

    # Flash should be visible
    flash = page.locator("p.font-medium").first
    expect(flash).to_be_visible()

    # Wait for auto-dismiss (5 seconds)
    page.wait_for_timeout(5500)

    # Flash should be gone
    expect(flash).not_to_be_visible()
```

### Testing Optional Props Loading

```python
def test_optional_props_load_on_demand(page: Page, fastapi_server: str) -> None:
    """Test that optional props load when requested."""
    page.goto(f"{fastapi_server}/lazy-demo")

    # Statistics should not be loaded initially
    expect(page.locator('[data-testid="not-loaded-message"]')).to_be_visible()
    expect(page.locator('[data-testid="statistics-container"]')).not_to_be_visible()

    # Click load button
    page.locator('[data-testid="load-statistics-button"]').click()

    # Statistics should now be visible
    expect(page.locator('[data-testid="statistics-container"]')).to_be_visible()
    expect(page.locator('[data-testid="total-cats"]')).to_be_visible()
```

### Testing Shared Data Updates

```python
def test_favorites_count_updates(page: Page, fastapi_server: str) -> None:
    """Test that favorites count updates without page reload."""
    page.goto(f"{fastapi_server}/browse")

    # Get initial favorites count
    badge = page.locator("nav a[href='/favorites'] span.bg-white")

    # Favorite a cat
    page.locator("button").filter(has=page.locator("svg")).first.click()
    page.wait_for_timeout(500)

    # Count badge should be visible
    expect(badge).to_be_visible()
```

## Running Tests

```bash
# Run unit tests
nox -s tests-3.14

# Run E2E tests (requires frontend build first)
cd examples/fastapi && bun run build
nox -s e2e-3.14

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Best Practices

1. **Test JSON Responses**: Use `X-Inertia: true` header to get JSON for easier assertions
2. **Test Both Success and Error Cases**: Verify validation errors are returned correctly
3. **Test Partial Reloads**: Ensure prop filtering works as expected
4. **Use Test IDs**: Add `data-testid` attributes for reliable E2E selectors
5. **Test SPA Behavior**: Verify navigation doesn't cause full page reloads
6. **Keep E2E Tests Focused**: Test critical user journeys, not every edge case

## Common Pitfalls

### Forgetting the X-Inertia Header

```python
# Bad: Gets HTML response, hard to test
response = client.get("/browse")

# Good: Gets JSON response
response = client.get("/browse", headers={"X-Inertia": "true"})
```

### Not Including Component Header for Partial Reloads

```python
# Bad: Partial data header alone doesn't work
response = client.get(
    "/browse",
    headers={
        "X-Inertia": "true",
        "X-Inertia-Partial-Data": "cats",
    },
)

# Good: Include both headers
response = client.get(
    "/browse",
    headers={
        "X-Inertia": "true",
        "X-Inertia-Partial-Data": "cats",
        "X-Inertia-Partial-Component": "Browse",
    },
)
```

### Flaky E2E Tests

```python
# Bad: Fixed timeout may be too short or too long
page.wait_for_timeout(1000)
expect(page.locator("text=Done")).to_be_visible()

# Good: Wait for specific condition
expect(page.locator("text=Done")).to_be_visible(timeout=5000)
```

## Next Steps

- [Validation Errors](/guides/validation-errors/) - Handle form validation
- [Shared Data](/guides/shared-data/) - Test shared data patterns
- [Partial Reloads](/guides/partial-reloads/) - Optimize data loading
