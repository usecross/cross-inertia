Release type: patch

Remove auto-detection of Vite entry point from vite.config.ts

This simplifies the configuration by removing the fragile regex-based auto-detection
of the Vite entry point. Instead, `vite_entry` now defaults to `"frontend/app.tsx"`
which matches the example project structure.

This follows the same pattern as Laravel's vite-plugin where entry points are
explicitly specified rather than auto-detected.

Changes:
- Remove `read_vite_entry_from_config()` function
- Remove `vite_config_path` parameter from `InertiaConfig` and `configure_inertia()`
- Change `vite_entry` default from `None` (with auto-detection) to `"frontend/app.tsx"`
