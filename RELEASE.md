---
release type: minor
---

This release adds Django and FastAPI lifecycle parity for Vite-backed SSR.

- Use Vite's `/__inertia_ssr` endpoint during development for both adapters
- Align Django middleware startup behavior with the FastAPI lifespan model
- Improve production asset resolution with shared manifest entry and asset URL helpers
