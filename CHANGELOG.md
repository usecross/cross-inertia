

0.4.0 - 2025-11-04
------------------

Add view data support for server-side template variables

- Add `view_data` parameter to `render()` method for passing server-side template data
- Template variables are only included in initial HTML responses, not XHR requests
- Add comprehensive test coverage (5 tests)
- Update demo app with dynamic page titles and SEO meta descriptions
- Add complete documentation guide with examples

This feature enables passing data to the root template (like page titles, meta descriptions, and Open Graph tags) that isn't included in page props, which is essential for SEO and social media sharing. The implementation uses a simple parameter approach that works consistently across all Python frameworks (FastAPI, Django, Flask, etc.).
