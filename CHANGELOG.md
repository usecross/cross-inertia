

0.6.0 - 2025-11-25
------------------

Add support for deferred props with the new `defer()` function.

Deferred props are excluded from the initial page load and automatically fetched
by the Inertia client after the page renders, improving perceived performance
for expensive computations.

## Usage

```python
from inertia import defer

return inertia.render("Dashboard", {
    "user": get_user(),                    # Loaded immediately
    "analytics": defer(get_analytics),     # Loaded after page renders
})
```

## Grouping for Parallel Loading

Props in the same group load together; different groups load in parallel:

```python
{
    "analytics": defer(get_analytics),                        # default group
    "notifications": defer(get_notifications),                # default group
    "recommendations": defer(get_recommendations, group="sidebar"),  # parallel
}
```

## Arguments Support

Like `functools.partial`, you can pass arguments to the callback:

```python
defer(get_user_stats, user_id, include_history=True)
```
