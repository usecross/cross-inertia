

0.11.1 - 2025-12-10
-------------------

Fix error handling when Vite manifest is missing in production

- Added `ManifestNotFoundError` exception that is raised when the Vite manifest file is missing in production mode
- Error message now clearly indicates the missing path and suggests running `vite build`
- Previously, missing manifest would silently return empty content, causing pages to load without JavaScript

```python
# The error can be caught if needed:
from inertia import ManifestNotFoundError

try:
    response = inertia.render("Page", props)
except ManifestNotFoundError as e:
    # Handle missing manifest (e.g., show deployment instructions)
    pass
```
