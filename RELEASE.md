---
release type: minor
---

Add view data support for server-side template variables

- Implement `with_view_data()` method for setting server-side template data
- Add `view_data` parameter to `render()` method
- Add comprehensive test coverage for view data feature
- Update demo app with dynamic page titles and meta descriptions
- Add complete documentation guide for view data usage

This feature enables passing data to the root template (like page titles, meta descriptions, and Open Graph tags) that isn't included in page props, which is essential for SEO and social media sharing.
