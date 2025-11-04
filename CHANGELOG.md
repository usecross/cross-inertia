

0.3.0 - 2025-11-04
------------------

Add Inertia.js v2 support and scrollProps for infinite scroll

## What's New

- **Inertia.js v2 Support**: Upgraded example to use Inertia.js v2.2.15 with new features
- **scrollProps Support**: Added `scroll_props` parameter to enable infinite scroll prop merging
- **Improved Pagination**: Enhanced Browse example with proper infinite scroll configuration

## Changes

### Core Library

- Add `scroll_props` parameter to `Inertia.render()` and `InertiaResponse.render()` methods
- Include `scrollProps` in page_data when provided for Inertia.js v2 compatibility
- Add `url` parameter to render methods for custom URL handling
- Fix asset version hash to use MD5 for deterministic values

### Example Application

- Upgrade `@inertiajs/react` from v1.x to v2.2.15
- Restructure cats data to use `{ data: [...] }` format for scroll merging
- Add `scrollProps` configuration with pagination metadata (pageName, previousPage, nextPage, currentPage)
- Update `mergeProps` and `matchPropsOn` to use dot notation for nested properties
- Improve toggle favorite functionality to preserve page state and filters
- Update TypeScript types to support both array and wrapped data formats

### Documentation

- Update AGENTS.md to note Inertia.js v2 requirement
- Update example README to indicate v2 usage
- Add dependency documentation for client-side adapters

## Notes

The `scrollProps` infrastructure is now in place for Inertia.js v2 infinite scroll support. The example demonstrates the proper data structure and configuration required by the Inertia.js v2 protocol, including `mergeProps`, `matchPropsOn`, and `scrollProps`.

For full infinite scroll functionality, consider using the `<InfiniteScroll>` component from `@inertiajs/react` in addition to the server-side configuration.
