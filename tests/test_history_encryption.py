"""Tests for history encryption feature."""

import json

from fastapi.testclient import TestClient


class TestHistoryEncryption:
    """Test history encryption functionality."""

    def test_default_no_encryption(self, client: TestClient):
        """Test that encryptHistory and clearHistory default to False."""
        response = client.get(
            "/test",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is False
        assert data["clearHistory"] is False

    def test_encrypt_history_enabled(self, client: TestClient):
        """Test that encrypt_history() sets encryptHistory to True."""
        response = client.get("/test-encrypt-history")

        assert response.status_code == 200
        # For HTML responses, parse the data-page attribute
        assert "data-page=" in response.text

        # Extract and parse the page data
        import re

        match = re.search(r"data-page='([^']+)'", response.text)
        assert match is not None
        page_data_json = match.group(1).replace("&apos;", "'")
        page_data = json.loads(page_data_json)

        assert page_data["encryptHistory"] is True
        assert page_data["clearHistory"] is False

    def test_encrypt_history_in_json_response(self, client: TestClient):
        """Test encryptHistory in Inertia JSON response."""
        response = client.get(
            "/test-encrypt-history",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is True
        assert data["clearHistory"] is False

    def test_clear_history_enabled(self, client: TestClient):
        """Test that clear_history() sets clearHistory to True."""
        response = client.get(
            "/test-clear-history",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is False
        assert data["clearHistory"] is True

    def test_both_encrypt_and_clear(self, client: TestClient):
        """Test that both flags can be set simultaneously."""
        response = client.get(
            "/test-encrypt-and-clear",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is True
        assert data["clearHistory"] is True

    def test_method_chaining(self, client: TestClient):
        """Test that methods return self for chaining."""
        response = client.get(
            "/test-method-chaining",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is True
        assert data["clearHistory"] is True

    def test_encrypt_history_false(self, client: TestClient):
        """Test that encrypt_history(False) disables encryption."""
        response = client.get(
            "/test-encrypt-false",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is False

    def test_clear_history_false(self, client: TestClient):
        """Test that clear_history(False) doesn't clear history."""
        response = client.get(
            "/test-clear-false",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["clearHistory"] is False

    def test_page_object_structure_with_encryption(self, client: TestClient):
        """Test that encrypted pages maintain proper page object structure."""
        response = client.get(
            "/test-encrypt-history",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()

        # Verify all required page object fields are present
        assert "component" in data
        assert "props" in data
        assert "url" in data
        assert "version" in data
        assert "encryptHistory" in data
        assert "clearHistory" in data

        # Verify correct values
        assert data["component"] == "TestComponent"
        assert data["encryptHistory"] is True
