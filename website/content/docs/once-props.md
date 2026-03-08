---
title: Once Props
description: Remember expensive props across visits and only refresh them when needed.
order: 12
section: Advanced
---

## Overview

`once()` marks props that Inertia can remember on the client and skip re-sending on later visits. This is useful for expensive or rarely-changing data like plans, reference data, and feature flags.

## Basic Usage

Wrap a value or callable with `once()`:

```python
from cross_inertia import once
from cross_inertia.fastapi import InertiaDep

@app.get("/billing")
def billing(inertia: InertiaDep):
    return inertia.render(
        "Billing/Plans",
        {
            "plans": once(load_plans),
            "permissions": once(load_permissions),
        },
    )
```

On the initial visit, the prop is included as normal. On later visits, the Inertia client can tell the server it already has that prop and the server will omit the value while still sending `onceProps` metadata.

## Expiration

Use `until=` to expire remembered props automatically:

```python
from datetime import timedelta

from cross_inertia import once

@app.get("/billing")
def billing(inertia: InertiaDep):
    return inertia.render(
        "Billing/Plans",
        {
            "exchange_rates": once(load_rates, until=timedelta(days=1)),
        },
    )
```

You can pass:

- `timedelta`
- `datetime`
- An integer Unix timestamp in seconds

## Custom Keys

By default, Cross-Inertia uses the prop path as the once key. You can override that with `key=`:

```python
from cross_inertia import once

return inertia.render(
    "Team/Invite",
    {
        "available_roles": once(load_roles, key="roles"),
    },
)
```

Custom keys are helpful when the same logical data appears under different prop names or shared/page boundaries.

## Forced Refresh

Use `fresh=True` when the prop should always be recomputed, even if the client says it already has a remembered value:

```python
from cross_inertia import once

return inertia.render(
    "Billing/Plans",
    {
        "feature_flags": once(load_flags, fresh=request.query_params.get("refresh") == "1"),
    },
)
```

## Shared Data

`once()` works in shared-data hooks too:

```python
from datetime import timedelta

from fastapi import Request
from cross_inertia import once
from cross_inertia.fastapi import inertia_share

@inertia_share
def share_reference_data(request: Request) -> dict:
    return {
        "countries": once(load_countries, key="countries", until=timedelta(days=1)),
        "feature_flags": once(
            load_flags,
            fresh=request.query_params.get("refresh") == "1",
        ),
    }
```

The same pattern works in Django `SHARE` functions.

## Combining With Deferred Props

You can compose `once()` with `defer()`:

```python
from cross_inertia import defer, once

return inertia.render(
    "Billing/Plans",
    {
        "permissions": once(
            defer(load_permissions, group="sidebar"),
            key="permissions",
        ),
    },
)
```

This lets you defer the first load and then avoid re-sending the resolved value on later visits.

## Refreshing From The Client

Refreshing a once prop uses the normal Inertia partial reload flow:

```tsx
import { router } from '@inertiajs/react'

router.reload({ only: ['plans'] })
```

If a once prop is explicitly requested via `only`, Cross-Inertia recomputes it even if the client had previously remembered it.
