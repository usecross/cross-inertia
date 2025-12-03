---
title: Links & Navigation
description: Navigate between pages without full page reloads.
order: 6
section: Core Concepts
---

## Inertia Links

Use the `Link` component for client-side navigation without full page reloads:

```tsx
import { Link } from '@inertiajs/react'

export default function Navigation() {
  return (
    <nav>
      <Link href="/">Home</Link>
      <Link href="/about">About</Link>
      <Link href="/users">Users</Link>
    </nav>
  )
}
```

## Link methods

By default, links use GET requests. You can change this with the `method` prop:

```tsx
<Link href="/logout" method="post">
  Logout
</Link>

<Link href="/posts/1" method="delete">
  Delete Post
</Link>
```

## Preserving state

Use `preserveState` to maintain component state during navigation:

```tsx
<Link href="/users?page=2" preserveState>
  Page 2
</Link>
```

## Preserving scroll

By default, Inertia resets scroll position. Use `preserveScroll` to prevent this:

```tsx
<Link href="/users?page=2" preserveScroll>
  Next Page
</Link>
```

## Programmatic navigation

Use the `router` for programmatic navigation:

```tsx
import { router } from '@inertiajs/react'

// GET request
router.visit('/users')

// POST request with data
router.post('/users', {
  name: 'John',
  email: 'john@example.com'
})

// With options
router.visit('/users', {
  method: 'get',
  preserveState: true,
  preserveScroll: true,
  only: ['users'],  // Partial reload
})
```

## External redirects

For external URLs or non-Inertia pages, use `inertia.location()` on the server:

```python
@app.get("/oauth/redirect")
async def oauth_redirect(inertia: InertiaDep):
    return inertia.location("https://github.com/login/oauth")
```
