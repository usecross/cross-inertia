"""Pytest configuration and fixtures for Django Inertia tests."""

import tempfile
from pathlib import Path

import pytest

# Configure Django settings before any Django imports
import django
from django.conf import settings


def pytest_configure():
    """Configure Django settings for tests."""
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": ":memory:",
                }
            },
            INSTALLED_APPS=[
                "django.contrib.contenttypes",
                "django.contrib.auth",
                "cross_inertia.django",
            ],
            MIDDLEWARE=[
                "cross_inertia.django.InertiaMiddleware",
            ],
            ROOT_URLCONF="tests.django.urls",
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                    "OPTIONS": {
                        "context_processors": [
                            "django.template.context_processors.request",
                        ],
                    },
                },
            ],
            USE_TZ=True,
            SECRET_KEY="test-secret-key",
            CROSS_INERTIA={
                "SHARE": "tests.django.views.share_data",
            },
        )
        django.setup()


@pytest.fixture
def temp_template_dir():
    """Create a temporary templates directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        template_path = Path(tmpdir) / "templates"
        template_path.mkdir()

        # Create a basic app.html template
        (template_path / "app.html").write_text(
            """<!DOCTYPE html>
<html>
<head>
    <title>Test</title>
    {{ vite_tags|safe }}
</head>
<body>
    <script data-page="app" type="application/json">{{ page|safe }}</script>
    <div id="app"></div>
</body>
</html>"""
        )
        yield str(template_path)


@pytest.fixture
def django_inertia_response(temp_template_dir):
    """Create a DjangoInertiaResponse instance for testing."""
    from cross_inertia.django.response import DjangoInertiaResponse

    # Update Django template dirs
    from django.conf import settings

    settings.TEMPLATES[0]["DIRS"] = [temp_template_dir]

    response = DjangoInertiaResponse(
        template_name="app.html",
        vite_dev_url="http://localhost:5173",
        manifest_path="static/build/.vite/manifest.json",
    )
    # Force dev mode for tests (avoids HTTP check to Vite server)
    response._is_dev = True
    return response


@pytest.fixture
def rf():
    """Django request factory."""
    from django.test import RequestFactory

    return RequestFactory()


@pytest.fixture
def client():
    """Django test client."""
    from django.test import Client

    return Client()
