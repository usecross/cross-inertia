---
release type: minor
---

Add X-Inertia-Reset header support for infinite scroll reset

- Handle X-Inertia-Reset header to clear props before merging
- Filter reset props from mergeProps, prependProps, deepMergeProps
- Support nested prop paths (e.g., reset "cats" excludes "cats.data")
- Include resetProps in response for client-side handling
- Fix URL handling to include query strings in responses
