---
title: View Data
description: Learn how to pass server-side template data for SEO meta tags and page titles
---

View data allows you to pass additional data to your root template that isn't included in the page props. This is useful for server-side rendering of meta tags, page titles, and other SEO-related data that needs to be in the initial HTML response.

## Why View Data?

When building SEO-friendly applications, you need to set meta tags (like Open Graph tags for social media) and page titles server-side so that:

- Search engine crawlers can see them (they don't always execute JavaScript)
- Social media platforms can properly preview your links
- Users see correct page titles immediately on page load

View data is only available during initial page loads (HTML responses), not in Inertia XHR requests, since these elements are only needed in the initial HTML.

## Usage

Pass view data directly to the `render()` method using the `view_data` parameter:

```python
from inertia.fastapi import InertiaDep

@app.get("/products/{id}")
async def product_page(id: int, inertia: InertiaDep):
    product = get_product(id)
    
    return inertia.render(
        "Product",
        {"product": product},
        view_data={
            "page_title": f"{product.name} - Our Store",
            "meta_description": product.description[:160],
            "og_meta": {
                "title": product.name,
                "description": product.description,
                "image": product.image_url,
            }
        }
    )
```

## Using View Data in Templates

View data variables are available directly in your root template (typically `app.html`):

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% if page_title %}{{ page_title }}{% else %}Default Title{% endif %}</title>
    
    {% if meta_description %}
    <meta name="description" content="{{ meta_description }}">
    {% endif %}
    
    {% if og_meta %}
    <meta property="og:title" content="{{ og_meta.title }}">
    <meta property="og:description" content="{{ og_meta.description }}">
    <meta property="og:image" content="{{ og_meta.image }}">
    {% endif %}
    
    {{ vite() | safe }}
</head>
<body>
    <div id="app" data-page='{{ page | safe }}'></div>
</body>
</html>
```

## Common Use Cases

### Dynamic Page Titles

```python
@app.get("/users/{user_id}")
async def user_profile(user_id: int, inertia: InertiaDep):
    user = get_user(user_id)
    
    return inertia.render(
        "UserProfile",
        {"user": user},
        view_data={
            "page_title": f"{user.name}'s Profile - MySite"
        }
    )
```

### Open Graph Tags for Social Sharing

```python
@app.get("/blog/{post_id}")
async def blog_post(post_id: int, inertia: InertiaDep):
    post = get_blog_post(post_id)
    
    return inertia.render(
        "BlogPost",
        {"post": post},
        view_data={
            "page_title": f"{post.title} - My Blog",
            "og_meta": {
                "title": post.title,
                "description": post.excerpt,
                "image": post.cover_image_url,
                "type": "article",
            }
        }
    )
```

Then in your template:

```html
{% if og_meta %}
<meta property="og:title" content="{{ og_meta.title }}">
<meta property="og:description" content="{{ og_meta.description }}">
<meta property="og:image" content="{{ og_meta.image }}">
<meta property="og:type" content="{{ og_meta.type }}">
{% endif %}
```

### Twitter Card Meta Tags

```python
@app.get("/products/{id}")
async def product_page(id: int, inertia: InertiaDep):
    product = get_product(id)
    
    return inertia.render(
        "Product",
        {"product": product},
        view_data={
            "page_title": f"{product.name} - Shop Now",
            "twitter_card": {
                "card": "summary_large_image",
                "title": product.name,
                "description": product.description,
                "image": product.image_url,
            }
        }
    )
```

Then in your template:

```html
{% if twitter_card %}
<meta name="twitter:card" content="{{ twitter_card.card }}">
<meta name="twitter:title" content="{{ twitter_card.title }}">
<meta name="twitter:description" content="{{ twitter_card.description }}">
<meta name="twitter:image" content="{{ twitter_card.image }}">
{% endif %}
```

## Framework Support

View data works with any Python web framework:

### FastAPI

```python
from inertia.fastapi import InertiaDep

@app.get("/page")
async def page(inertia: InertiaDep):
    return inertia.render(
        "Page",
        {"data": data},
        view_data={"page_title": "Title"}
    )
```

### Django (without dependency injection)

```python
from inertia import inertia

def page_view(request):
    return inertia.render(
        request,
        "Page",
        {"data": data},
        view_data={"page_title": "Title"}
    )
```

## Important Notes

- **View data is not included in page props**: View data is only available in the template, not in your frontend components via `usePage().props`
- **XHR requests don't include view_data**: View data is only rendered during initial page loads (HTML responses), not during Inertia XHR requests
- **Use for server-side only data**: View data is perfect for meta tags, page titles, and other SEO elements that don't need to be reactive in your frontend
- **Simple and explicit**: All view data is passed in one place, making it easy to understand and maintain

## Comparison with Laravel Inertia

This feature is similar to Laravel Inertia's `viewData` feature, but simplified:

```php
// Laravel Inertia
return Inertia::render('Product', $props)
    ->withViewData(['title' => 'Product Page']);
```

```python
# Cross-Inertia
return inertia.render(
    'Product',
    props,
    view_data={'page_title': 'Product Page'}
)
```

The key difference is that Cross-Inertia uses a simple parameter instead of method chaining, making it:
- More explicit and easier to understand
- Works consistently across all Python frameworks
- No hidden state or lifecycle concerns
- All render data in one place

## See Also

- [Shared Data](/guides/shared-data) - For data that should be available in all page props
- [Configuration](/guides/configuration) - Template configuration options
