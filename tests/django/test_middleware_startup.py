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
    """When configure_inertia() was never called, the shared defaults apply."""
    from cross_inertia._config import reset_config

    reset_config()
    try:
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            assert inertia_settings.VITE_ENTRY == "frontend/app.tsx"
            assert inertia_settings.VITE_PORT == "auto"
            assert 5173 <= inertia_settings.resolved_vite_port < 5273
    finally:
        reset_config()
        inertia_settings.reload()


def test_django_defaults_mirror_shared_config():
    """Every shared Django setting defaults to the InertiaConfig value."""
    from cross_inertia._config import InertiaConfig
    from cross_inertia.django.conf import DEFAULTS, SHARED_CONFIG_ATTRS

    shared = InertiaConfig()
    for key, attr in SHARED_CONFIG_ATTRS.items():
        assert DEFAULTS[key] == getattr(shared, attr), key


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


def test_vite_base_falls_back_to_shared_config():
    from cross_inertia import configure_inertia
    from cross_inertia._config import reset_config

    try:
        configure_inertia(vite_base="/static/build/")
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            assert inertia_settings.VITE_BASE == "/static/build/"
    finally:
        reset_config()
        inertia_settings.reload()


def test_vite_base_defaults_to_root():
    from cross_inertia._config import reset_config

    reset_config()
    try:
        with override_settings(CROSS_INERTIA={}):
            inertia_settings.reload()
            assert inertia_settings.VITE_BASE == "/"
    finally:
        reset_config()
        inertia_settings.reload()


def test_middleware_passes_vite_base_to_process(monkeypatch):
    """The auto-started Vite process must health-check under VITE_BASE."""
    from cross_inertia.django import middleware as middleware_module

    reset_vite_state()
    created: list[object] = []

    class FakeViteProcess:
        def __init__(self, command, port, startup_timeout, base=None, host=None):
            self.command = command
            self.port = port
            self.startup_timeout = startup_timeout
            self.base = base
            self.host = host
            self.dev_url = f"http://{host}:{port}"
            created.append(self)

        def get_command_with_port(self):
            return f"{self.command} --port {self.port}"

        def start(self):
            return None

    monkeypatch.setattr(middleware_module, "SyncViteProcess", FakeViteProcess)
    monkeypatch.setattr(middleware_module, "is_port_in_use", lambda port: False)
    monkeypatch.setattr(middleware_module.atexit, "register", lambda fn: None)

    with override_settings(
        CROSS_INERTIA={
            "VITE_PORT": 5177,
            "VITE_HOST": "127.0.0.1",
            "VITE_BASE": "/static/build/",
        }
    ):
        inertia_settings.reload()
        InertiaMiddleware._start_vite_dev_server()

    inertia_settings.reload()
    reset_vite_state()
    assert len(created) == 1
    assert created[0].port == 5177
    assert created[0].host == "127.0.0.1"
    assert created[0].base == "/static/build/"
