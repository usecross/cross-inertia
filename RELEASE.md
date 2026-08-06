---
release type: patch
---

Fix synchronous Django share callbacks under ASGI

- Run synchronous shared-data callbacks in Django's thread-sensitive sync context
- Add regression coverage for database access from shared data
