

0.2.0 - 2025-11-03
------------------

Move framework-specific exports to submodules

This release introduces framework-specific import paths to prepare for future Flask and Django support.

**New import style:**
```python
from inertia.fastapi import InertiaDep, InertiaMiddleware
```

**Changes:**
- Add `inertia.fastapi` module with FastAPI-specific exports
- Remove top-level exports from `inertia` package
- Update all examples and documentation to use new import style
- Cleaner namespace for multi-framework support

**Migration Guide:**

Update your imports from:
```python
from inertia import InertiaDep, InertiaMiddleware
```

To:
```python
from inertia.fastapi import InertiaDep, InertiaMiddleware
```

No other code changes are required - just update the import statements.

Closes #10
