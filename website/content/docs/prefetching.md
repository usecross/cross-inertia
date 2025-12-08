---
title: Prefetching
description: Improve perceived performance by preloading pages before navigation
---

Prefetching allows the Inertia.js client to load pages in the background before the user navigates to them. This improves perceived performance by reducing the time users wait for pages to load.

## How It Works

When prefetching is enabled on a link, Inertia makes a background request to fetch the page data before the user clicks. The server responds normally, and the client caches the response for instant navigation.

Cross-Inertia automatically detects prefetch requests via the `Purpose: prefetch` header and handles them appropriately.

## Frontend Setup

### Link Prefetching

Use the `prefetch` prop on Link components:

```tsx
import { Link } from '@inertiajs/react'

// Prefetch on hover (default behavior when prefetch is enabled)
<Link href="/users/1" prefetch>
  View User
</Link>

// Prefetch on mount (when component renders)
<Link href="/dashboard" prefetch="mount">
  Dashboard
</Link>

// Prefetch on hover with delay
<Link href="/settings" prefetch="hover">
  Settings
</Link>
```

### Prefetch Triggers

- **`hover`**: Prefetch when the user hovers over the link (most common)
- **`mount`**: Prefetch when the component mounts (for high-priority links)
- **`click`**: Prefetch on mouse down (shortest delay before navigation)

### Cache Configuration

Control how long prefetched data is cached:

```tsx
import { Link } from '@inertiajs/react'

// Cache for 30 seconds
<Link href="/users" prefetch cacheFor="30s">
  Users
</Link>

// Cache for 5 minutes
<Link href="/reports" prefetch cacheFor="5m">
  Reports
</Link>

// Single-use (use once, then refetch)
<Link href="/notifications" prefetch cacheFor={0}>
  Notifications
</Link>
```

### Programmatic Prefetching

Use `router.prefetch()` for more control:

```tsx
import { router } from '@inertiajs/react'

// Prefetch a page
router.prefetch('/users/1')

// Prefetch with options
router.prefetch('/dashboard', {
  method: 'get',
  data: { filter: 'active' },
})

// Prefetch with cache configuration
router.prefetch('/users/1', {}, { cacheFor: '1m' })
```

### Prefetch State Hook

Track prefetch status with `usePrefetch()`:

```tsx
import { usePrefetch } from '@inertiajs/react'

function UserLink({ userId }) {
  const { isPrefetching, isPrefetched } = usePrefetch(`/users/${userId}`)

  return (
    <Link href={`/users/${userId}`} prefetch>
      {isPrefetching && <Spinner />}
      {isPrefetched && <CheckIcon />}
      View User
    </Link>
  )
}
```

## Backend Support

Cross-Inertia automatically handles prefetch requests. No special configuration is required.

### How Detection Works

Prefetch requests include the `Purpose: prefetch` header. Cross-Inertia detects this and:

1. Processes the request normally (returns full page data)
2. Logs prefetch requests distinctly for debugging
3. Supports all features (partial reloads, deferred props, etc.)

### Logging

Prefetch requests are logged separately:

```
→ Prefetch: Users/Show (props: ['user', 'posts'])
→ Inertia XHR: Users/Show (props: ['user', 'posts'])
```

### Combining with Partial Reloads

Prefetch works with partial reloads:

```tsx
// Prefetch only specific props
<Link
  href="/users/1"
  prefetch
  only={['user', 'recentPosts']}
>
  View User
</Link>
```

### Combining with Deferred Props

Prefetch respects deferred props - they're still loaded after the initial render:

```python
@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    return inertia.render("Users/Show", {
        "user": get_user(user_id),
        # These load after render, even on prefetched pages
        "activity": defer(get_activity, user_id),
        "recommendations": defer(get_recommendations, user_id),
    })
```

## Real-World Examples

### Navigation Menu

Prefetch common navigation destinations:

```tsx
import { Link } from '@inertiajs/react'

function Navigation() {
  return (
    <nav>
      <Link href="/dashboard" prefetch="mount">
        Dashboard
      </Link>
      <Link href="/users" prefetch="hover">
        Users
      </Link>
      <Link href="/settings" prefetch="hover">
        Settings
      </Link>
    </nav>
  )
}
```

### List Items

Prefetch detail pages on hover:

```tsx
import { Link } from '@inertiajs/react'

function UserList({ users }) {
  return (
    <ul>
      {users.map(user => (
        <li key={user.id}>
          <Link
            href={`/users/${user.id}`}
            prefetch="hover"
            cacheFor="1m"
          >
            {user.name}
          </Link>
        </li>
      ))}
    </ul>
  )
}
```

### Tabbed Interface

Prefetch tab content:

```tsx
import { Link, usePage } from '@inertiajs/react'

function UserTabs({ userId }) {
  const { url } = usePage()

  return (
    <div className="tabs">
      <Link
        href={`/users/${userId}`}
        prefetch={url !== `/users/${userId}`}
      >
        Profile
      </Link>
      <Link
        href={`/users/${userId}/posts`}
        prefetch={url !== `/users/${userId}/posts`}
      >
        Posts
      </Link>
      <Link
        href={`/users/${userId}/settings`}
        prefetch={url !== `/users/${userId}/settings`}
      >
        Settings
      </Link>
    </div>
  )
}
```

## Cache Management

### Invalidating Cache

Flush specific cached pages:

```tsx
import { router } from '@inertiajs/react'

// Flush specific URL from cache
router.flush('/users/1')

// Flush by cache tags
router.flushByCacheTags('user-1')
```

### Cache Tags

Use cache tags for grouped invalidation:

```tsx
<Link
  href={`/users/${userId}`}
  prefetch
  cacheTags={[`user-${userId}`, 'users']}
>
  View User
</Link>
```

```tsx
// Invalidate all user-related caches
router.flushByCacheTags('users')
```

## Performance Considerations

### When to Prefetch

**Good candidates:**
- Navigation menu items
- List item detail pages
- Next/previous pagination links
- Tabbed interface content

**Avoid prefetching:**
- Pages with constantly changing data
- Heavy pages that are rarely visited
- Protected pages (may prefetch unnecessarily)

### Cache Duration

Choose cache duration based on data freshness needs:

```tsx
// Static content - cache longer
<Link href="/about" prefetch cacheFor="1h">About</Link>

// Dynamic content - cache briefly
<Link href="/notifications" prefetch cacheFor="10s">Notifications</Link>

// Very dynamic - single use
<Link href="/live-feed" prefetch cacheFor={0}>Live Feed</Link>
```

## Best Practices

1. **Start with hover prefetch** - It's the safest default
2. **Use mount sparingly** - Only for high-priority, frequently accessed pages
3. **Set appropriate cache times** - Balance freshness vs performance
4. **Combine with partial reloads** - Prefetch only the data you need
5. **Monitor network usage** - Prefetching increases requests

## Next Steps

- [Partial Reloads](/guides/partial-reloads/) - Combine prefetch with partial data loading
- [Configuration](/guides/configuration/) - Global prefetch settings
