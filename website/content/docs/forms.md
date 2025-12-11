---
title: Forms
description: Handle form submissions with Inertia.
order: 7
section: Core Concepts
---

## Using the useForm hook

The `useForm` hook provides a convenient way to handle form submissions:

```tsx
import { useForm } from '@inertiajs/react'

export default function CreateUser() {
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    email: '',
  })

  function submit(e: React.FormEvent) {
    e.preventDefault()
    post('/users')
  }

  return (
    <form onSubmit={submit}>
      <input
        value={data.name}
        onChange={(e) => setData('name', e.target.value)}
      />
      {errors.name && <span>{errors.name}</span>}

      <input
        value={data.email}
        onChange={(e) => setData('email', e.target.value)}
      />
      {errors.email && <span>{errors.email}</span>}

      <button disabled={processing}>Create User</button>
    </form>
  )
}
```

## Server-side validation

Return validation errors using the `errors` parameter in `render()`:

```python
from pydantic import BaseModel, EmailStr, ValidationError

class CreateUserRequest(BaseModel):
    name: str
    email: EmailStr

@app.post("/users")
async def create_user(request: Request, inertia: InertiaDep):
    form = await request.form()

    try:
        data = CreateUserRequest(**form)
    except ValidationError as e:
        errors = {err["loc"][0]: err["msg"] for err in e.errors()}
        return inertia.render("Users/Create", errors=errors)

    # Create user...
    return RedirectResponse("/users", status_code=303)
```

## File uploads

Use `forceFormData` for file uploads:

```tsx
const { data, setData, post } = useForm({
  name: '',
  avatar: null as File | null,
})

function submit(e: React.FormEvent) {
  e.preventDefault()
  post('/users', { forceFormData: true })
}

return (
  <form onSubmit={submit}>
    <input
      type="file"
      onChange={(e) => setData('avatar', e.target.files?.[0] || null)}
    />
    <button type="submit">Upload</button>
  </form>
)
```
