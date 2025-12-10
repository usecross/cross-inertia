---
title: Merge Props & Infinite Scroll
description: Build infinite scroll and load more functionality with merge props
---

Merge props allow you to append new data to existing page props instead of replacing them. This is essential for building infinite scroll, load more buttons, and other pagination patterns that accumulate data.

## The Problem

By default, Inertia replaces all props on navigation:

```tsx
// Page 1: cats = [cat1, cat2, cat3]
// Click "Load More" → Page 2
// Page 2: cats = [cat4, cat5, cat6]  // Previous cats are gone!
```

Users expect "Load More" to add items while keeping existing ones visible.

## The Solution: Merge Props

With merge props, new data is appended to existing arrays:

```tsx
// Page 1: cats = [cat1, cat2, cat3]
// Click "Load More" → Page 2
// Page 2: cats = [cat1, cat2, cat3, cat4, cat5, cat6]  // All cats preserved!
```

## Backend Setup

### Basic Usage

Use the `merge_props` parameter to specify which props should be merged:

```python
@app.get("/browse")
async def browse_items(
    inertia: InertiaDep,
    page: int = Query(1, ge=1),
):
    items = get_items(page=page, per_page=10)

    return inertia.render(
        "Browse",
        {
            "items": items,
            "page": page,
            "has_more": page < total_pages,
        },
        merge_props=["items"],  # Merge items array instead of replacing
    )
```

### Nested Props

For nested data structures, use dot notation:

```python
return inertia.render(
    "Browse",
    {
        "data": {
            "items": paginated_items,
            "metadata": {...}
        },
        "page": page,
    },
    merge_props=["data.items"],  # Merge nested array
)
```

### Preventing Duplicates

Use `match_props_on` to prevent duplicate items when the same page is loaded twice:

```python
return inertia.render(
    "Browse",
    {
        "cats": {
            "data": paginated_cats,
        },
        "page": page,
        "has_more": has_more,
    },
    merge_props=["cats.data"],
    match_props_on=["cats.data.id"],  # Match on ID to prevent duplicates
)
```

### Scroll Configuration

Use `scroll_props` to configure pagination behavior for Inertia's scroll restoration:

```python
@app.get("/browse")
async def browse_cats(
    inertia: InertiaDep,
    page: int = Query(1, ge=1),
):
    paginated = paginate_cats(page=page, per_page=6)

    previous_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < paginated["total_pages"] else None

    return inertia.render(
        "Browse",
        {
            "cats": {
                "data": paginated["cats"],
            },
            "page": page,
            "has_more": page < paginated["total_pages"],
        },
        merge_props=["cats.data"],
        match_props_on=["cats.data.id"],
        scroll_props={
            "cats": {
                "pageName": "page",
                "previousPage": previous_page,
                "nextPage": next_page,
                "currentPage": page,
            }
        },
    )
```

## Frontend Setup

### Load More Button

```tsx
import { router } from '@inertiajs/react'

interface BrowseProps {
  cats: { data: Cat[] }
  page: number
  has_more: boolean
}

export default function Browse({ cats, page, has_more }: BrowseProps) {
  const handleLoadMore = () => {
    router.visit(`/browse?page=${page + 1}`, {
      preserveScroll: true,
      preserveState: true,
      only: ['cats', 'page', 'has_more'],  // Only fetch pagination props
    })
  }

  return (
    <div>
      <div className="grid grid-cols-3 gap-4">
        {cats.data.map((cat) => (
          <CatCard key={cat.id} cat={cat} />
        ))}
      </div>

      {has_more && (
        <button onClick={handleLoadMore}>
          Load More
        </button>
      )}
    </div>
  )
}
```

### Key Frontend Options

- **`preserveScroll: true`** - Keeps the user's scroll position
- **`preserveState: true`** - Preserves component state (form inputs, etc.)
- **`only: [...]`** - Only fetch the props needed for pagination (performance optimization)

## Complete Example

Here's a full implementation from our demo app:

### Backend (FastAPI)

```python
from fastapi import FastAPI, Query
from inertia.fastapi import InertiaDep

@app.get("/browse")
async def browse_cats(
    inertia: InertiaDep,
    page: int = Query(1, ge=1),
    breed: str | None = None,
):
    # Apply filters and pagination
    filtered_cats = filter_cats(breed=breed)
    paginated = paginate_cats(filtered_cats, page=page, per_page=6)

    # Calculate pagination info
    previous_page = page - 1 if page > 1 else None
    next_page = page + 1 if page < paginated["total_pages"] else None

    return inertia.render(
        "Browse",
        {
            "title": "Browse Cats",
            "cats": {
                "data": paginated["cats"],
            },
            "total": paginated["total"],
            "page": paginated["page"],
            "has_more": page < paginated["total_pages"],
            "filters": {"breed": breed},
        },
        # Merge props configuration
        merge_props=["cats.data"],
        match_props_on=["cats.data.id"],
        scroll_props={
            "cats": {
                "pageName": "page",
                "previousPage": previous_page,
                "nextPage": next_page,
                "currentPage": page,
            }
        },
    )
```

### Frontend (React)

```tsx
import { router } from '@inertiajs/react'

interface Cat {
  id: number
  name: string
  breed: string
  photo: string
}

interface BrowseProps {
  title: string
  cats: { data: Cat[] }
  total: number
  page: number
  has_more: boolean
  filters: { breed: string | null }
}

export default function Browse({ title, cats, total, page, has_more, filters }: BrowseProps) {
  const handleLoadMore = () => {
    const params = new URLSearchParams()
    params.set('page', (page + 1).toString())
    if (filters.breed) params.set('breed', filters.breed)

    router.visit(`/browse?${params.toString()}`, {
      preserveScroll: true,
      preserveState: true,
      only: ['cats', 'page', 'has_more'],
    })
  }

  return (
    <div>
      <h1>{title}</h1>
      <p>Showing {cats.data.length} of {total} cats</p>

      <div className="grid grid-cols-3 gap-6">
        {cats.data.map((cat) => (
          <div key={cat.id} className="card">
            <img src={cat.photo} alt={cat.name} />
            <h3>{cat.name}</h3>
            <p>{cat.breed}</p>
          </div>
        ))}
      </div>

      {has_more && (
        <div className="text-center mt-8">
          <button
            onClick={handleLoadMore}
            className="btn btn-primary"
          >
            Load More Cats
          </button>
        </div>
      )}
    </div>
  )
}
```

## Resetting Merged Data

When filters change, you typically want to **replace** the data rather than merge it. Use the `reset` option on the frontend to clear existing data before loading new results.

### The Problem

Without reset, changing filters causes new results to be appended to existing data:

```tsx
// User has loaded 12 cats (2 pages)
// User changes breed filter to "Maine Coon"
// Without reset: 12 old cats + 1 Maine Coon = 13 cats shown (wrong!)
// With reset: Just 1 Maine Coon shown (correct!)
```

### Frontend Solution

Use the `reset` option when filters change:

```tsx
const handleFilterChange = (newBreed: string | null) => {
  const params = new URLSearchParams()
  params.set('page', '1')  // Start from page 1
  if (newBreed) params.set('breed', newBreed)

  router.visit(`/browse?${params.toString()}`, {
    preserveScroll: false,  // Scroll to top when filters change
    preserveState: false,
    // Reset cats data when filters change
    // This sends X-Inertia-Reset header to clear existing data
    reset: ['cats'],
    // Request all props needed (reset causes partial reload)
    only: ['cats', 'total', 'page', 'has_more', 'filters'],
  })
}
```

### How It Works

When you use `reset: ['cats']`:

1. The Inertia client sends the `X-Inertia-Reset: cats` header
2. The server excludes `cats` from `mergeProps` (so data replaces instead of merges)
3. The server includes `resetProps: ['cats']` in the response
4. The client clears the local `cats` state before applying new data

### Complete Filter Example

```tsx
export default function Browse({ cats, page, has_more, filters }: BrowseProps) {
  // Load more - MERGES data
  const handleLoadMore = () => {
    const params = new URLSearchParams()
    params.set('page', (page + 1).toString())
    if (filters.breed) params.set('breed', filters.breed)

    router.visit(`/browse?${params.toString()}`, {
      preserveScroll: true,
      preserveState: true,
      only: ['cats', 'page', 'has_more'],
    })
  }

  // Filter change - RESETS data
  const handleFilterChange = (breed: string | null) => {
    const params = new URLSearchParams()
    params.set('page', '1')
    if (breed) params.set('breed', breed)

    router.visit(`/browse?${params.toString()}`, {
      preserveScroll: false,
      preserveState: false,
      reset: ['cats'],
      only: ['cats', 'total', 'page', 'has_more', 'filters'],
    })
  }

  return (
    <div>
      {/* Filter dropdown */}
      <select
        value={filters.breed || ''}
        onChange={(e) => handleFilterChange(e.target.value || null)}
      >
        <option value="">All Breeds</option>
        <option value="Maine Coon">Maine Coon</option>
        <option value="Siamese">Siamese</option>
      </select>

      {/* Cat grid */}
      <div className="grid grid-cols-3 gap-4">
        {cats.data.map((cat) => (
          <CatCard key={cat.id} cat={cat} />
        ))}
      </div>

      {/* Load more button */}
      {has_more && (
        <button onClick={handleLoadMore}>Load More</button>
      )}
    </div>
  )
}
```

### Backend: No Changes Needed

The backend automatically handles the reset header. When `X-Inertia-Reset: cats` is received:

- `cats` (and nested paths like `cats.data`) are excluded from `mergeProps`
- The response includes `resetProps: ['cats']` for the client

No backend code changes are required—the existing `merge_props` configuration works automatically with reset.

## Advanced Options

### Prepend Props

Use `prepend_props` to add new items at the beginning instead of the end:

```python
return inertia.render(
    "Feed",
    {"posts": new_posts},
    prepend_props=["posts"],  # New posts appear at the top
)
```

### Deep Merge Props

Use `deep_merge_props` for deeply nested objects that should be merged recursively:

```python
return inertia.render(
    "Dashboard",
    {
        "stats": {
            "daily": {...},
            "weekly": {...},
        }
    },
    deep_merge_props=["stats"],  # Recursively merge nested objects
)
```

## API Reference

### `inertia.render()` Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `merge_props` | `list[str]` | Props to append (arrays are concatenated) |
| `prepend_props` | `list[str]` | Props to prepend (new items first) |
| `deep_merge_props` | `list[str]` | Props to recursively merge (for objects) |
| `match_props_on` | `list[str]` | Fields to match for deduplication |
| `scroll_props` | `dict` | Scroll/pagination configuration |

### Dot Notation

All prop parameters support dot notation for nested paths:

- `"items"` - Top-level array
- `"data.items"` - Nested under `data`
- `"response.data.items"` - Deeply nested

## Best Practices

1. **Always use `match_props_on`** to prevent duplicates when users navigate back and forth
2. **Use `only` on the frontend** to minimize data transfer
3. **Preserve scroll and state** for seamless UX
4. **Include pagination metadata** (`has_more`, `page`) to control UI
5. **Handle filters** - Remember to include filter params when loading more

## Common Pitfalls

### Forgetting `preserveScroll`

```tsx
// Bad: Page jumps to top after load more
router.visit(`/browse?page=${page + 1}`)

// Good: Scroll position preserved
router.visit(`/browse?page=${page + 1}`, {
  preserveScroll: true,
  preserveState: true,
})
```

### Not Using `only`

```tsx
// Bad: Reloads all props including expensive ones
router.visit(`/browse?page=${page + 1}`, {
  preserveScroll: true,
})

// Good: Only loads what's needed
router.visit(`/browse?page=${page + 1}`, {
  preserveScroll: true,
  only: ['cats', 'page', 'has_more'],
})
```

### Forgetting Filters

```tsx
// Bad: Filters lost when loading more
router.visit(`/browse?page=${page + 1}`)

// Good: Preserve filters
const params = new URLSearchParams()
params.set('page', (page + 1).toString())
if (filters.breed) params.set('breed', filters.breed)
router.visit(`/browse?${params.toString()}`, {...})
```

## Next Steps

- [Partial Reloads](/guides/partial-reloads/) - Optimize which props are loaded
- [View Data](/guides/view-data/) - Pass server-side template data
- Try the demo: `just demo-fastapi` to see infinite scroll in action
