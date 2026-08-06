"""Tests for core Inertia protocol implementation."""

from fastapi.testclient import TestClient

from tests.page_html import extract_page_data


class TestInertiaProtocol:
    """Test the core Inertia.js protocol implementation."""

    def test_detects_inertia_request(self, client: TestClient):
        """Test that X-Inertia header is properly detected."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        assert response.status_code == 200
        assert response.headers.get("X-Inertia") == "true"
        assert response.headers.get("Content-Type") == "application/json"

    def test_initial_page_load_returns_html(self, client: TestClient):
        """Test that initial page load returns HTML with embedded page data."""
        response = client.get("/test")
        assert response.status_code == 200
        assert response.headers.get("Content-Type").startswith("text/html")
        assert 'script data-page="app"' in response.text
        assert 'id="app"' in response.text

    def test_vary_header_present(self, client: TestClient):
        """Test that Vary: X-Inertia header is included in responses."""
        # Test JSON response
        response = client.get(
            "/test",
            headers={"X-Inertia": "true"},
        )
        assert response.headers.get("Vary") == "X-Inertia"

        html_response = client.get("/test")
        assert html_response.headers.get("Vary") == "X-Inertia"

    def test_page_object_structure_json(self, client: TestClient):
        """Test that JSON response has correct page object structure."""
        response = client.get(
            "/test",
            headers={
                "X-Inertia": "true",
                "X-Requested-With": "XMLHttpRequest",
            },
        )
        data = response.json()

        # Required fields per spec
        assert "component" in data
        assert "props" in data
        assert "url" in data
        assert "version" in data

        # Check values
        assert data["component"] == "TestComponent"
        assert data["props"]["message"] == "Hello, World!"
        assert data["url"] == "/test"
        assert isinstance(data["version"], str)

    def test_page_object_in_html_script(self, client: TestClient):
        """Test that HTML response includes page object in the JSON script."""
        response = client.get("/test")
        assert response.status_code == 200

        html = response.text
        page_data = extract_page_data(html)

        # Verify structure
        assert page_data["component"] == "TestComponent"
        assert page_data["props"]["message"] == "Hello, World!"
        assert page_data["url"] == "/test"
        assert "version" in page_data

    def test_non_inertia_request_returns_html(self, client: TestClient):
        """Test that requests without X-Inertia header get HTML response."""
        response = client.get("/test")
        assert response.status_code == 200
        assert "text/html" in response.headers.get("Content-Type")
        assert not response.headers.get("X-Inertia")

    def test_custom_status_applies_to_json_and_html(self, client: TestClient):
        json_response = client.get("/forbidden", headers={"X-Inertia": "true"})
        html_response = client.get("/forbidden")

        assert json_response.status_code == 403
        assert json_response.json()["props"]["status"] == 403
        assert html_response.status_code == 403


class TestValidationErrors:
    """Test validation error handling."""

    def test_errors_in_props_json_response(self, client: TestClient):
        """Test that errors are included in props for JSON responses."""
        response = client.get(
            "/with-errors",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        # Inertia always returns 200, errors are communicated via props
        assert response.status_code == 200
        assert "errors" in data["props"]
        assert data["props"]["errors"]["field"] == "This field is required"

    def test_errors_status_code_200(self, client: TestClient):
        """Test that validation errors return 200 status code (Inertia protocol)."""
        response = client.get(
            "/with-errors",
            headers={"X-Inertia": "true"},
        )
        # Per Inertia protocol, errors are communicated via props, not status codes
        assert response.status_code == 200
        # Verify errors are present in props
        data = response.json()
        assert "errors" in data["props"]

    def test_errors_in_html_response(self, client: TestClient):
        """Test that errors are included in HTML page data for initial loads."""
        response = client.get("/with-errors")
        assert response.status_code == 200  # HTML responses still return 200

        page_data = extract_page_data(response.text)

        assert "errors" in page_data["props"]
        assert page_data["props"]["errors"]["field"] == "This field is required"


class TestPageObjectFields:
    """Test the advanced page object fields for infinite scroll and prop merging."""

    def test_merge_props_in_json_response(self, client: TestClient):
        """Test that mergeProps field is included when specified."""
        response = client.get(
            "/test-merge-props",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "mergeProps" in data
        assert data["mergeProps"] == ["items"]

    def test_prepend_props_in_json_response(self, client: TestClient):
        """Test that prependProps field is included when specified."""
        response = client.get(
            "/test-prepend-props",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "prependProps" in data
        assert data["prependProps"] == ["notifications"]

    def test_deep_merge_props_in_json_response(self, client: TestClient):
        """Test that deepMergeProps field is included when specified."""
        response = client.get(
            "/test-deep-merge-props",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "deepMergeProps" in data
        assert data["deepMergeProps"] == ["settings"]

    def test_match_props_on_in_json_response(self, client: TestClient):
        """Test that matchPropsOn field is included when specified."""
        response = client.get(
            "/test-match-props-on",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "matchPropsOn" in data
        assert data["matchPropsOn"] == ["id"]

    def test_multiple_merge_fields_together(self, client: TestClient):
        """Test that multiple merge fields can be used together."""
        response = client.get(
            "/test-all-merge-props",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "mergeProps" in data
        assert "matchPropsOn" in data
        assert data["mergeProps"] == ["items"]
        assert data["matchPropsOn"] == ["id"]

    def test_merge_props_not_included_when_not_specified(self, client: TestClient):
        """Test that merge fields are not included when not specified."""
        response = client.get(
            "/test",
            headers={"X-Inertia": "true"},
        )
        data = response.json()

        assert response.status_code == 200
        assert "mergeProps" not in data
        assert "prependProps" not in data
        assert "deepMergeProps" not in data
        assert "matchPropsOn" not in data
