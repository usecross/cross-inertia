# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Integrated [lia-web](https://github.com/patrick91/lia) for framework abstraction layer
- Added `TODO.md` with comprehensive task tracking and framework support roadmap
- Added `CHANGELOG.md` for tracking changes

### Changed
- Refactored `InertiaResponse` to use `StarletteRequestAdapter` from lia
- Refactored `Inertia` class to accept request adapter alongside raw request
- Updated URL extraction to use adapter's URL property (handles full URL parsing)
- Migrated build system from `uv_build` to `hatchling` for better package structure

### Fixed
- Fixed HTML template escaping issue where JSON in `data-page` attribute was being HTML-escaped
  - Added `| safe` filter to Jinja2 template in test fixtures
- Fixed build system configuration to properly recognize `src/inertia` module structure

### Dependencies
- Added `lia-web>=0.2.3` as a core dependency
- Changed build backend from `uv_build` to `hatchling`

## [0.1.0] - 2024-11

### Added
- Initial implementation of Inertia.js protocol for FastAPI
- Full Inertia.js protocol support (JSON/HTML responses, headers)
- Vite integration with dev/production mode detection
- Auto-detection of Vite entry point from `vite.config.ts/js`
- Template function `{{ vite() }}` for asset loading (Laravel-like)
- Asset versioning for cache busting
- Validation error handling (422 status codes)
- React Fast Refresh support in development
- Type hints throughout codebase
- FastAPI dependency injection via `InertiaDep`
- Comprehensive test suite
- Documentation:
  - README.md with quick start guide
  - ROADMAP.md with feature tracking
  - PACKAGE_STATUS.md with maturity assessment
  - TEMPLATE_FUNCTIONS.md with reference
  - LARAVEL_COMPARISON.md with feature comparison

### Known Limitations
- Asset version mismatch handling not implemented (no 409 Conflict response)
- Partial reloads not implemented
- Shared data middleware not implemented
- Only FastAPI/Starlette supported (lia enables multi-framework in future)

[Unreleased]: https://github.com/patrick91/cross-inertia/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/patrick91/cross-inertia/releases/tag/v0.1.0
