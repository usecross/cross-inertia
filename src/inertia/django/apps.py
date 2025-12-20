"""Django app configuration for Inertia."""

from django.apps import AppConfig


class InertiaConfig(AppConfig):
    """Django app configuration for inertia.django."""

    name = "inertia.django"
    label = "inertia"
    verbose_name = "Inertia.js"

    def ready(self) -> None:
        """Initialize Inertia when Django starts."""
        # Import to ensure template tags are registered
        pass
