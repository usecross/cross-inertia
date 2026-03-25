---
release type: minor
---

Align with Inertia v3 stable protocol

- Add flash data support via `inertia.flash(key, value)`
- Add `preserveFragment` support via `inertia.preserve_fragment()`
- Add `X-Inertia-Redirect` for hash fragment redirects via `inertia.redirect(url)`
- Add `sharedProps` to page object (exposes shared prop keys for optimistic updates)
- Make `encryptHistory`/`clearHistory` optional in page object (only sent when `true`)
- Remove unused `_is_lazy_prop` backwards compat alias
