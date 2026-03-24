---
release type: patch
---

This release fixes a server-side rendering bug caused by reusing an async SSR HTTP client across closed event loops.

- Create a fresh `httpx.AsyncClient` for each SSR `render()` call
- Create a fresh `httpx.AsyncClient` for each SSR `health_check()` call
- Remove the cached async SSR client to avoid `Event loop is closed` errors on repeated requests
- Add tests covering repeated SSR renders and health checks across separate event loops
- Preserve graceful fallback to CSR when SSR fails
