---
title: Deferred Props
description: Load slow data after the initial page render.
order: 10
section: Advanced
---

## Overview

Deferred props allow you to load slow or expensive data after the initial page render. This improves perceived performance by showing the page immediately while loading additional data in the background.

## Using Deferred Props

Wrap slow data with the `defer` function:

```python
from inertia import defer
from inertia.fastapi import InertiaDep

@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    return inertia.render("Dashboard", {
        "user": get_current_user(),  # Fast, loaded immediately
        "stats": defer(lambda: get_slow_stats()),  # Loaded after render
        "notifications": defer(lambda: fetch_notifications()),
    })
```

## Client-Side Handling

Use the `Deferred` component from Inertia.js to handle deferred props:

```tsx
import { Deferred } from '@inertiajs/react'

interface DashboardProps {
  user: { name: string }
  stats: { views: number; sales: number } | null
  notifications: Array<{ id: number; message: string }> | null
}

export default function Dashboard({ user, stats, notifications }: DashboardProps) {
  return (
    <div>
      <h1>Welcome, {user.name}</h1>

      <Deferred data="stats" fallback={<div>Loading stats...</div>}>
        <Stats data={stats} />
      </Deferred>

      <Deferred data="notifications" fallback={<div>Loading notifications...</div>}>
        <NotificationList items={notifications} />
      </Deferred>
    </div>
  )
}
```

## Grouping Deferred Props

You can group related deferred props to load them together:

```python
@app.get("/analytics")
async def analytics(inertia: InertiaDep):
    return inertia.render("Analytics", {
        "summary": get_summary(),  # Immediate
        "charts": defer(lambda: get_chart_data(), group="visualizations"),
        "tables": defer(lambda: get_table_data(), group="visualizations"),
        "exports": defer(lambda: get_export_options(), group="tools"),
    })
```

Props in the same group are fetched in a single request.

## Best Practices

1. **Keep critical data immediate**: User info, page title, and essential UI elements should load immediately
2. **Defer secondary content**: Analytics, recommendations, and non-critical features can be deferred
3. **Provide meaningful fallbacks**: Show loading skeletons or spinners while data loads
4. **Group related data**: Reduce request overhead by grouping props that are displayed together
