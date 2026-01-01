---
title: Pages
description: Learn how to create and render Inertia pages.
order: 4
section: Core Concepts
---

## Rendering pages

Pages are rendered by specifying a component name and optional props.

### FastAPI

```python
from inertia.fastapi import InertiaDep

@app.get("/")
async def home(inertia: InertiaDep):
    return inertia.render("Home", {
        "title": "Welcome",
        "user": {"name": "John"}
    })
```

### Django

```python
from inertia.django import render

def home(request):
    return render(request, "Home", {
        "title": "Welcome",
        "user": {"name": "John"}
    })

# Or with the decorator
from inertia.django import inertia

@inertia("Home")
def home(request):
    return {
        "title": "Welcome",
        "user": {"name": "John"}
    }
```

## Component naming

Component names map directly to your frontend page components. Use forward slashes to organize pages into directories:

```python
# These map to frontend/pages/Users/Index.tsx
inertia.render("Users/Index", {...})

# And frontend/pages/Users/Show.tsx
inertia.render("Users/Show", {...})
```

## Page props

Props passed to the render method are available in your page component:

```tsx
// frontend/pages/Users/Show.tsx
interface ShowProps {
  user: {
    id: number
    name: string
    email: string
  }
}

export default function Show({ user }: ShowProps) {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>{user.email}</p>
    </div>
  )
}
```

## View data

You can pass additional data to your template (not included in page props) using the `view_data` parameter:

### FastAPI

```python
@app.get("/products/{id}")
async def show_product(id: int, inertia: InertiaDep):
    product = await get_product(id)
    return inertia.render(
        "Products/Show",
        {"product": product},
        view_data={
            "page_title": product.name,
            "meta_description": product.description[:160]
        }
    )
```

### Django

```python
from inertia.django import render

def show_product(request, id):
    product = Product.objects.get(id=id)
    return render(
        request,
        "Products/Show",
        {"product": product},
        view_data={
            "page_title": product.name,
            "meta_description": product.description[:160]
        }
    )
```
