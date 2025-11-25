

0.7.1 - 2025-11-25
------------------

Add prefetch support

- Add `is_prefetch_request()` method to detect prefetch requests via `Purpose: prefetch` header
- Log prefetch requests distinctly from regular Inertia XHR requests for debugging
- Add comprehensive tests for prefetch handling
- Add documentation guide for prefetching
