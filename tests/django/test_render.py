"""Tests for Django Inertia render function."""


class TestBasicRendering:
    """Tests for basic Inertia rendering."""

    def test_initial_page_load_returns_html(self, client, django_inertia_response):
        """Initial page load should return HTML with page data."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get("/test/")
            assert response.status_code == 200
            assert "text/html" in response["Content-Type"]

            content = response.content.decode()
            assert "data-page=" in content
            assert "TestComponent" in content
        finally:
            reset_inertia_response()

    def test_inertia_request_returns_json(self, client, django_inertia_response):
        """Inertia XHR request should return JSON."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get(
                "/test/",
                HTTP_X_INERTIA="true",
            )
            assert response.status_code == 200
            assert response["Content-Type"] == "application/json"
            assert response["X-Inertia"] == "true"
            assert response["Vary"] == "X-Inertia"

            data = response.json()
            assert data["component"] == "TestComponent"
            assert data["props"]["message"] == "Hello, World!"
            assert "url" in data
            assert "version" in data
        finally:
            reset_inertia_response()

    def test_render_with_multiple_props(self, client, django_inertia_response):
        """Should render with multiple props correctly."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get(
                "/multi-props/",
                HTTP_X_INERTIA="true",
            )
            data = response.json()

            assert data["props"]["message"] == "Hello"
            assert data["props"]["user"]["name"] == "John"
            assert data["props"]["count"] == 42
            assert data["props"]["items"] == ["a", "b", "c"]
        finally:
            reset_inertia_response()

    def test_render_with_errors(self, client, django_inertia_response):
        """Should include validation errors in props."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get(
                "/with-errors/",
                HTTP_X_INERTIA="true",
            )
            data = response.json()

            assert "errors" in data["props"]
            assert data["props"]["errors"]["field"] == "This field is required"
        finally:
            reset_inertia_response()


class TestExternalRedirects:
    """Tests for external redirects."""

    def test_external_redirect_returns_409(self, client, django_inertia_response):
        """External redirect should return 409 with location header."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get("/external-redirect/")
            assert response.status_code == 409
            assert response["X-Inertia-Location"] == "https://github.com/login"
        finally:
            reset_inertia_response()


class TestDecorator:
    """Tests for @inertia decorator."""

    def test_inertia_decorator(self, client, django_inertia_response):
        """@inertia decorator should wrap view props."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get(
                "/decorator/",
                HTTP_X_INERTIA="true",
            )
            data = response.json()

            assert data["component"] == "DecoratorTest"
            assert data["props"]["decorated"] is True
            assert data["props"]["message"] == "From decorator"
        finally:
            reset_inertia_response()


class TestClassBasedView:
    """Tests for class-based views with InertiaViewMixin."""

    def test_class_based_view_get(self, client, django_inertia_response):
        """Class-based view GET should work."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.get(
                "/class-view/",
                HTTP_X_INERTIA="true",
            )
            data = response.json()

            assert data["component"] == "ClassViewTest"
            assert data["props"]["class_based"] is True
            assert data["props"]["method"] == "GET"
        finally:
            reset_inertia_response()

    def test_class_based_view_post(self, client, django_inertia_response):
        """Class-based view POST should work with extra props."""
        from inertia.django.shortcuts import reset_inertia_response
        import inertia.django.shortcuts as shortcuts

        shortcuts._inertia_response = django_inertia_response

        try:
            response = client.post(
                "/class-view/",
                HTTP_X_INERTIA="true",
            )
            data = response.json()

            assert data["component"] == "ClassViewTest"
            assert data["props"]["class_based"] is True
            assert data["props"]["method"] == "POST"
        finally:
            reset_inertia_response()
