"""Tests for history encryption feature."""

from fastapi.testclient import TestClient

from tests.page_html import extract_page_data


class TestHistoryEncryption:
    """Test history encryption functionality."""

    def test_default_no_encryption(self, client: TestClient):
        """Test that encryptHistory and clearHistory are absent when not set."""
        response = client.get(
            "/test",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "encryptHistory" not in data
        assert "clearHistory" not in data

    def test_encrypt_history_enabled(self, client: TestClient):
        """Test that encrypt_history() sets encryptHistory to True."""
        response = client.get("/test-encrypt-history")

        assert response.status_code == 200
        assert 'script data-page="app"' in response.text
        page_data = extract_page_data(response.text)

        assert page_data["encryptHistory"] is True
        assert "clearHistory" not in page_data

    def test_encrypt_history_in_json_response(self, client: TestClient):
        """Test encryptHistory in Inertia JSON response."""
        response = client.get(
            "/test-encrypt-history",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["encryptHistory"] is True
        assert "clearHistory" not in data

    def test_clear_history_enabled(self, client: TestClient):
        """Test that clear_history() sets clearHistory to True."""
        response = client.get(
            "/test-clear-history",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "encryptHistory" not in data
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
        """Test that encrypt_history(False) keeps encryptHistory absent."""
        response = client.get(
            "/test-encrypt-false",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "encryptHistory" not in data

    def test_clear_history_false(self, client: TestClient):
        """Test that clear_history(False) keeps clearHistory absent."""
        response = client.get(
            "/test-clear-false",
            headers={"X-Inertia": "true"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "clearHistory" not in data

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

        # clearHistory should NOT be present when not enabled
        assert "clearHistory" not in data

        # Verify correct values
        assert data["component"] == "TestComponent"
        assert data["encryptHistory"] is True
