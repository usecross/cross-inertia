---
release type: patch
---

Make `share` parameter optional in `InertiaMiddleware`

The `share` parameter now defaults to `None`, allowing simpler middleware setup when shared data is not needed:

```python
# Before (required)
app.add_middleware(InertiaMiddleware, share=lambda request: {})

# After (optional)
app.add_middleware(InertiaMiddleware)
```
