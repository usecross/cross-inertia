---
release type: patch
---

Always include `errors` in page props, as an empty object when there are no validation errors.

Previously, `errors` was left out when empty. Inertia merges a partial reload into the current page, so a valid submission made with `only` kept the errors from an earlier invalid one and called `onError` instead of `onSuccess`. An `errors` prop set by the app is still kept when there are no validation errors, and is now sent on partial reloads too.
