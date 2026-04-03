"""Tests for Django middleware startup behavior."""

from django.test import override_settings

from cross_inertia.django.conf import inertia_settings
from cross_inertia.django.middleware import InertiaMiddleware


def reset_vite_state() -> None:
    InertiaMiddleware._vite_process = None
    InertiaMiddleware._vite_started = False
    InertiaMiddleware._ssr_process = None
    InertiaMiddleware._ssr_started = False


def test_middleware_starts_vite_by_default_for_runserver_child(monkeypatch):
    reset_vite_state()
    started: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.setenv("RUN_MAIN", "true")
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: None),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: started.append(True)),
    )

    with override_settings(DEBUG=True, CROSS_INERTIA={}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started == [True]


def test_middleware_only_starts_vite_once_per_process(monkeypatch):
    reset_vite_state()
    started: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.setenv("RUN_MAIN", "true")
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: None),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: started.append(True)),
    )

    with override_settings(DEBUG=True, CROSS_INERTIA={}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started == [True]


def test_middleware_skips_standalone_ssr_by_default_for_runserver_child(monkeypatch):
    reset_vite_state()
    started: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.setenv("RUN_MAIN", "true")
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: None),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: started.append(True)),
    )

    with override_settings(DEBUG=True, CROSS_INERTIA={}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started == []


def test_middleware_skips_standalone_ssr_in_dev_mode(monkeypatch):
    """In dev mode Vite handles SSR via /__inertia_ssr."""
    reset_vite_state()
    started: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.setenv("RUN_MAIN", "true")
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: None),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: started.append(True)),
    )

    with override_settings(DEBUG=True, CROSS_INERTIA={"SSR_ENABLED": True}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started == []


def test_middleware_starts_standalone_ssr_outside_dev_mode(monkeypatch):
    reset_vite_state()
    started: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.setenv("RUN_MAIN", "true")
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: None),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: started.append(True)),
    )

    with override_settings(DEBUG=False, CROSS_INERTIA={"SSR_ENABLED": True}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started == [True]


def test_middleware_skips_dev_servers_in_autoreload_parent(monkeypatch):
    reset_vite_state()
    started_vite: list[bool] = []
    started_ssr: list[bool] = []

    monkeypatch.setattr("sys.argv", ["manage.py", "runserver"])
    monkeypatch.delenv("RUN_MAIN", raising=False)
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_vite_dev_server",
        classmethod(lambda cls: started_vite.append(True)),
    )
    monkeypatch.setattr(
        InertiaMiddleware,
        "_start_ssr_server",
        classmethod(lambda cls: started_ssr.append(True)),
    )

    with override_settings(DEBUG=True, CROSS_INERTIA={}):
        inertia_settings.reload()
        InertiaMiddleware(lambda request: None)

    inertia_settings.reload()
    reset_vite_state()
    assert started_vite == []
    assert started_ssr == []


def test_django_settings_fall_back_to_shared_config():
    from cross_inertia import configure_inertia
    from cross_inertia._config import reset_config

    try:
        configure_inertia(vite_port=5199, vite_host="127.0.0.1", ssr_enabled=False)
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            assert inertia_settings.VITE_PORT == 5199
            assert inertia_settings.VITE_HOST == "127.0.0.1"
            assert inertia_settings.SSR_ENABLED is False
    finally:
        reset_config()
        inertia_settings.reload()


def test_django_defaults_used_when_shared_config_not_set():
    """When configure_inertia() was never called, Django's own defaults apply."""
    from cross_inertia._config import reset_config

    reset_config()
    try:
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            assert inertia_settings.VITE_ENTRY == "src/main.tsx"
            assert inertia_settings.VITE_PORT == 5173
    finally:
        reset_config()
        inertia_settings.reload()


def test_shared_config_asset_url_prefix_overrides_static_url():
    """configure_inertia(asset_url_prefix=...) should take priority over STATIC_URL."""
    from cross_inertia import configure_inertia
    from cross_inertia._config import reset_config

    try:
        configure_inertia(asset_url_prefix="/custom-assets")
        with override_settings(CROSS_INERTIA={}, STATIC_URL="/static/"):
            inertia_settings.reload()
            assert inertia_settings.ASSET_URL_PREFIX == "/custom-assets"
    finally:
        reset_config()
        inertia_settings.reload()


def test_asset_url_prefix_derives_from_static_url_without_shared_config():
    """Without configure_inertia(), ASSET_URL_PREFIX derives from STATIC_URL."""
    from cross_inertia._config import reset_config

    reset_config()
    try:
        with override_settings(CROSS_INERTIA={}, STATIC_URL="/assets/"):
            inertia_settings.reload()
            assert inertia_settings.ASSET_URL_PREFIX == "/assets/build"
    finally:
        reset_config()
        inertia_settings.reload()


def test_ssr_cwd_passed_to_ssr_server():
    """SSR_CWD from Django settings should be accessible."""
    from cross_inertia._config import reset_config

    reset_config()
    try:
        with override_settings(CROSS_INERTIA={"SSR_CWD": "/app/frontend"}):
            inertia_settings.reload()
            assert inertia_settings.SSR_CWD == "/app/frontend"
    finally:
        reset_config()
        inertia_settings.reload()


def test_ssr_cwd_falls_back_to_shared_config():
    """SSR_CWD should fall back to shared config when set."""
    from cross_inertia import configure_inertia
    from cross_inertia._config import reset_config

    try:
        configure_inertia(ssr_enabled=True)
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            # InertiaConfig default for ssr_cwd is None
            assert inertia_settings.SSR_CWD is None
    finally:
        reset_config()
        inertia_settings.reload()
