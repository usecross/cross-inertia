---
title: History Encryption
description: Encrypt page data stored in browser history.
order: 11
section: Advanced
---

## Overview

Inertia stores page data in the browser's history state. By default, this data is stored in plain text. History encryption allows you to encrypt this data to protect sensitive information.

## Why Use History Encryption?

When users navigate through your app, Inertia stores page props in the browser history. This allows instant back/forward navigation. However, if your pages contain sensitive data (like personal information or access tokens), this data could be exposed to:

- Browser extensions with history access
- Other users with physical access to the device
- Debugging tools

## Enabling Encryption

Enable history encryption in your Inertia client setup:

```tsx
import { createInertiaApp } from '@inertiajs/react'

createInertiaApp({
  // ... other options
  encryptHistory: true,
})
```

## How It Works

1. When navigating to a new page, Inertia encrypts the page props before storing them in history
2. When navigating back/forward, Inertia decrypts the props before rendering
3. The encryption key is unique to each browser session

## Server-Side Configuration

You can also enable encryption from the server side:

```python
from inertia.fastapi import InertiaDep

@app.get("/sensitive-data")
async def sensitive_page(inertia: InertiaDep):
    return inertia.render(
        "SensitiveData",
        {"secret": "confidential-info"},
        encrypt_history=True,
    )
```

## Clearing History

You can programmatically clear encrypted history:

```tsx
import { router } from '@inertiajs/react'

// Clear all encrypted history
router.clearHistory()

// Clear history on logout
async function logout() {
  router.clearHistory()
  router.post('/logout')
}
```

## Performance Considerations

- Encryption adds minimal overhead (typically < 1ms per navigation)
- Large page props may have noticeable encryption time
- Consider using deferred props for large datasets instead of encrypting them

## Browser Support

History encryption requires:
- Web Crypto API (available in all modern browsers)
- History API (standard in all browsers)
