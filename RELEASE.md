Release type: patch

Simplify Vite configuration

This simplifies the configuration by:
1. Removing auto-detection of Vite entry point from vite.config.ts
2. Removing `vite_cwd` parameter (Vite should always run from project root)

The `vite_entry` now defaults to `"frontend/app.tsx"` which matches the example
project structure. This follows Laravel's vite-plugin pattern where entry points
are explicitly specified rather than auto-detected.

Changes:
- Remove `read_vite_entry_from_config()` function
- Remove `vite_config_path` parameter from `InertiaConfig` and `configure_inertia()`
- Remove `vite_cwd` parameter from `InertiaConfig`, `configure_inertia()`, and `ViteDevServer`
- Change `vite_entry` default from `None` (with auto-detection) to `"frontend/app.tsx"`
