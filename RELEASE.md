---
release type: minor
---

Add Server-Side Rendering (SSR) support

Enable SSR by passing `ssr_enabled=True` to `InertiaResponse`:

```python
inertia_response = InertiaResponse(
    ssr_enabled=True,
    ssr_url="http://localhost:13714",  # optional, this is the default
)
```

- Add `ssr_enabled` and `ssr_url` parameters to `InertiaResponse`
- SSR server must implement the Inertia SSR protocol (`POST /render`, `GET /health`)
- Graceful fallback to client-side rendering (CSR) when SSR fails or times out
- Template context now includes `ssr_head` and `ssr_body` variables for SSR output
