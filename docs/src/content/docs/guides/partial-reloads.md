---
title: Partial Reloads
description: Optimize performance by loading only the data you need
---

Partial reloads allow you to request a subset of page props, reducing the amount of data transferred and improving performance. This is especially useful for pages with expensive database queries or large datasets.

## The Problem

By default, Inertia reloads all page props on every visit:

```python
@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    return inertia.render("Users/Show", {
        "user": get_user(user_id),              # Fast query
        "posts": get_user_posts(user_id),       # Slow query
        "comments": get_user_comments(user_id), # Slow query
        "stats": calculate_user_stats(user_id)  # Expensive calculation
    })
```

Even if you only need to refresh the `user` data, all props are reloaded - wasting time and bandwidth.

## The Solution: Partial Reloads

Partial reloads let you specify which props to load:

```tsx
import { router } from '@inertiajs/react'

// Only reload 'user' prop
router.reload({ only: ['user'] })

// Reload everything except 'stats'
router.reload({ except: ['stats'] })
```

## Backend Setup

The backend automatically handles partial reload requests. No changes needed!

```python
@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    # All props defined
    return inertia.render("Users/Show", {
        "user": get_user(user_id),
        "posts": get_user_posts(user_id),
        "comments": get_user_comments(user_id),
        "stats": calculate_user_stats(user_id)
    })

# When client requests only=['user'], only get_user() runs
# Other expensive queries are skipped automatically
```

However, for optimal performance, you can use lazy evaluation:

```python
@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    user_id_val = user_id  # Capture for lambda
    
    return inertia.render("Users/Show", {
        "user": get_user(user_id),
        # These only execute when requested
        "posts": lambda: get_user_posts(user_id_val),
        "comments": lambda: get_user_comments(user_id_val),
        "stats": lambda: calculate_user_stats(user_id_val)
    })
```

## Frontend Usage

### Using `router.reload()`

```tsx
import { router } from '@inertiajs/react'
import { User } from './types'

export default function UserProfile({ user, posts, comments }: {
  user: User
  posts: Post[]
  comments: Comment[]
}) {
  const refreshUser = () => {
    // Only reload user data
    router.reload({ only: ['user'] })
  }

  return (
    <div>
      <h1>{user.name}</h1>
      <button onClick={refreshUser}>Refresh Profile</button>
      
      {/* Posts and comments won't be reloaded */}
      <PostList posts={posts} />
      <CommentList comments={comments} />
    </div>
  )
}
```

### Using `router.visit()` with Partial Reloads

```tsx
import { router } from '@inertiajs/react'

// Navigate to user page, only load user and posts
router.visit(`/users/${userId}`, {
  only: ['user', 'posts']
})

// Navigate to user page, load everything except stats
router.visit(`/users/${userId}`, {
  except: ['stats']
})
```

### Using `Link` Component

```tsx
import { Link } from '@inertiajs/react'

export default function UserList({ users }: { users: User[] }) {
  return (
    <div>
      {users.map(user => (
        <Link
          key={user.id}
          href={`/users/${user.id}`}
          only={['user', 'posts']}
        >
          {user.name}
        </Link>
      ))}
    </div>
  )
}
```

## Real-World Examples

### Dashboard with Real-Time Updates

```python
@app.get("/dashboard")
async def dashboard(inertia: InertiaDep):
    user = get_current_user()
    
    return inertia.render("Dashboard", {
        "user": user,
        "notifications": get_notifications(user.id),
        "stats": lambda: calculate_dashboard_stats(user.id),  # Expensive
        "activity": lambda: get_recent_activity(user.id)      # Expensive
    })
```

```tsx
import { router } from '@inertiajs/react'
import { useEffect } from 'react'

export default function Dashboard({ user, notifications, stats, activity }) {
  // Poll for new notifications every 30 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      router.reload({ only: ['notifications'] })
    }, 30000)
    
    return () => clearInterval(interval)
  }, [])

  return (
    <div>
      <h1>Welcome, {user.name}!</h1>
      <NotificationBell notifications={notifications} />
      <Stats data={stats} />
      <ActivityFeed items={activity} />
    </div>
  )
}
```

### Search with Filters

```python
@app.get("/products")
async def search_products(
    inertia: InertiaDep,
    q: str | None = None,
    category: str | None = None,
    page: int = 1
):
    return inertia.render("Products/Search", {
        "products": search_products(q, category, page),
        "categories": get_categories(),  # Static data
        "filters": {"q": q, "category": category}
    })
```

```tsx
import { router } from '@inertiajs/react'

export default function ProductSearch({ products, categories, filters }) {
  const search = (query: string) => {
    router.visit(`/products?q=${query}`, {
      only: ['products', 'filters'],  // Don't reload categories
      preserveState: true,
      preserveScroll: true
    })
  }

  return (
    <div>
      <SearchInput onSearch={search} defaultValue={filters.q} />
      <CategoryList categories={categories} />  {/* Static */}
      <ProductGrid products={products} />
    </div>
  )
}
```

### Form Submission with Partial Reload

```python
@app.post("/settings/profile")
async def update_profile(inertia: InertiaDep):
    form_data = await inertia.request.json()
    
    # Update profile
    user = update_user_profile(form_data)
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse("/settings", status_code=303)

@app.get("/settings")
async def settings(inertia: InertiaDep):
    user = get_current_user()
    
    return inertia.render("Settings", {
        "user": user,
        "billing": lambda: get_billing_info(user.id),    # Expensive
        "usage": lambda: calculate_usage_stats(user.id)  # Expensive
    })
```

```tsx
import { useForm } from '@inertiajs/react'

export default function Settings({ user, billing, usage }) {
  const { data, setData, post, processing } = useForm({
    name: user.name,
    email: user.email,
  })

  const submit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/settings/profile', {
      onSuccess: () => {
        // Only reload user data after update
        router.reload({ only: ['user'] })
      }
    })
  }

  return (
    <div>
      <form onSubmit={submit}>
        {/* Profile form */}
      </form>
      
      <BillingInfo data={billing} />  {/* Not reloaded */}
      <UsageStats data={usage} />     {/* Not reloaded */}
    </div>
  )
}
```

## Advanced Patterns

### Nested Partial Reloads

```python
@app.get("/blog/{post_id}")
async def show_post(post_id: int, inertia: InertiaDep):
    return inertia.render("Blog/Show", {
        "post": get_post(post_id),
        "author": lambda: get_author(get_post(post_id).author_id),
        "comments": lambda: get_comments(post_id),
        "related": lambda: get_related_posts(post_id)
    })
```

```tsx
// Load post and author only
router.reload({ only: ['post', 'author'] })

// Load post and comments only
router.reload({ only: ['post', 'comments'] })
```

### Combining with `preserveState`

```tsx
import { router } from '@inertiajs/react'

// Reload data without resetting form state
router.reload({
  only: ['users'],
  preserveState: true,
  preserveScroll: true
})
```

### Optimistic UI Updates

```tsx
import { router } from '@inertiajs/react'

const toggleFavorite = (itemId: number) => {
  // Update UI optimistically
  setFavorited(!favorited)
  
  // Send request in background
  router.post(`/favorites/${itemId}/toggle`, {}, {
    preserveState: true,
    preserveScroll: true,
    only: ['favorites_count'],  // Only reload count
    onError: () => {
      // Revert on error
      setFavorited(favorited)
    }
  })
}
```

## Performance Benefits

### Before Partial Reloads

```python
# Every reload fetches all data
@app.get("/users/{user_id}")
async def show_user(user_id: int):
    return {
        "user": get_user(user_id),           # 10ms
        "posts": get_user_posts(user_id),     # 200ms
        "comments": get_comments(user_id),    # 150ms
        "stats": calculate_stats(user_id)     # 500ms
    }
# Total: 860ms per request
```

### After Partial Reloads

```tsx
// Only reload user data
router.reload({ only: ['user'] })
// Total: 10ms (86x faster!)
```

## Best Practices

1. **Use Lazy Evaluation**: Wrap expensive operations in lambdas
2. **Group Related Data**: Keep related props together for efficient reloads
3. **Minimize Initial Load**: Load heavy data on-demand with partial reloads
4. **Combine with Caching**: Cache expensive queries on the backend
5. **Monitor Performance**: Use `preserveState` and `preserveScroll` for better UX

## Common Pitfalls

### ❌ Don't: Forget to preserve state

```tsx
// Bad: Resets component state
router.reload({ only: ['products'] })
```

```tsx
// Good: Preserves form inputs, scroll position
router.reload({
  only: ['products'],
  preserveState: true,
  preserveScroll: true
})
```

### ❌ Don't: Request props that don't exist

```tsx
// Bad: 'invalid' prop doesn't exist
router.reload({ only: ['invalid'] })
// Result: Error or empty response
```

### ❌ Don't: Overuse partial reloads

```tsx
// Bad: Too many partial reload requests
router.reload({ only: ['user'] })
router.reload({ only: ['posts'] })
router.reload({ only: ['comments'] })

// Good: Reload what you need in one request
router.reload({ only: ['user', 'posts', 'comments'] })
```

## Debugging

Check which props are being requested:

```python
# In your route handler
@app.get("/users/{user_id}")
async def show_user(user_id: int, inertia: InertiaDep):
    # Log partial reload requests
    partial_data = inertia.request.headers.get("X-Inertia-Partial-Data")
    if partial_data:
        print(f"Partial reload requested: {partial_data}")
    
    return inertia.render("Users/Show", {...})
```

## Next Steps

- [Shared Data](/guides/shared-data/) - Combine with shared data for efficiency
- [Configuration](/guides/configuration/) - Set up lazy prop evaluation
- [Validation Errors](/guides/validation-errors/) - Use with form submissions
