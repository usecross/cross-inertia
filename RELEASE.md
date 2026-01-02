---
release type: minor
---

Rename Python module from `inertia` to `cross_inertia`

**BREAKING CHANGE**: All imports must be updated to use the new module name.

### Migration Guide

Update your imports:

```python
# Before
from inertia import optional, always, defer
from inertia.fastapi import InertiaDep, InertiaMiddleware
from inertia.django import render, inertia

# After
from cross_inertia import optional, always, defer
from cross_inertia.fastapi import InertiaDep, InertiaMiddleware
from cross_inertia.django import render, inertia
```

Update Django settings:

```python
# Before
INSTALLED_APPS = ['inertia.django']
MIDDLEWARE = ['inertia.django.InertiaMiddleware']

# After
INSTALLED_APPS = ['cross_inertia.django']
MIDDLEWARE = ['cross_inertia.django.InertiaMiddleware']
```

This rename aligns the Python module name with the package name (`cross-inertia`) for consistency.
