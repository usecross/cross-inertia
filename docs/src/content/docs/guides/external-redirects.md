---
title: External Redirects
description: Redirect to external URLs and non-Inertia pages
---

Sometimes you need to redirect users to external websites or non-Inertia pages (like OAuth providers, payment gateways, or external maps). Cross-Inertia provides the `inertia.location()` method for this.

## Why External Redirects?

Regular Inertia navigation is designed for single-page app transitions within your application. However, for external URLs, you need a full page reload. The `location()` method handles this by:

1. Returning a `409 Conflict` response
2. Setting the `X-Inertia-Location` header
3. Triggering the Inertia client to perform a full page navigation

## Basic Usage

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/auth/github")
async def github_oauth(inertia: InertiaDep):
    """Redirect to GitHub OAuth"""
    oauth_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}"
    return inertia.location(oauth_url)
```

## Common Use Cases

### OAuth Authentication

Redirect users to OAuth providers:

```python
@app.get("/auth/google")
async def google_oauth(inertia: InertiaDep):
    """Redirect to Google OAuth"""
    oauth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&response_type=code"
        "&scope=openid email profile"
    )
    return inertia.location(oauth_url)

@app.get("/auth/github")
async def github_oauth(inertia: InertiaDep):
    """Redirect to GitHub OAuth"""
    oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={REDIRECT_URI}"
        "&scope=user:email"
    )
    return inertia.location(oauth_url)
```

### Payment Gateways

Redirect to external payment providers:

```python
@app.post("/checkout")
async def create_checkout(inertia: InertiaDep):
    """Create Stripe checkout session"""
    form_data = await inertia.request.json()
    
    # Create Stripe checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price': form_data['price_id'],
            'quantity': 1,
        }],
        mode='payment',
        success_url=f'{BASE_URL}/success?session_id={{CHECKOUT_SESSION_ID}}',
        cancel_url=f'{BASE_URL}/cancel',
    )
    
    # Redirect to Stripe
    return inertia.location(session.url)
```

### External Maps

Redirect to mapping services:

```python
@app.get("/shelter/{shelter_id}/directions")
async def get_directions(shelter_id: int, inertia: InertiaDep):
    """Get directions to a shelter"""
    shelter = get_shelter(shelter_id)
    
    # Redirect to Google Maps
    address = shelter["address"].replace(" ", "+")
    maps_url = f"https://maps.google.com/?q={address}"
    
    return inertia.location(maps_url)

@app.get("/venue/{venue_id}/navigate")
async def navigate_to_venue(venue_id: int, inertia: InertiaDep):
    """Navigate to venue using Apple Maps"""
    venue = get_venue(venue_id)
    
    # Redirect to Apple Maps
    apple_maps_url = f"maps://?q={venue['name']}&ll={venue['lat']},{venue['lng']}"
    
    return inertia.location(apple_maps_url)
```

### External Documentation

Link to external documentation or help articles:

```python
@app.get("/help/external/{article_id}")
async def external_help(article_id: str, inertia: InertiaDep):
    """Redirect to external help documentation"""
    help_url = f"https://docs.example.com/articles/{article_id}"
    return inertia.location(help_url)
```

### Download Files

Trigger file downloads from external URLs:

```python
@app.get("/reports/{report_id}/download")
async def download_report(report_id: int, inertia: InertiaDep):
    """Download a generated report"""
    report = get_report(report_id)
    
    # Redirect to S3 or CDN URL
    download_url = generate_presigned_url(report['file_key'])
    return inertia.location(download_url)
```

## Real-World Example

Here's a complete example from a cat adoption platform:

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/cats/{cat_id}")
async def show_cat(cat_id: int, inertia: InertiaDep):
    """Show cat profile with shelter information"""
    cat = get_cat_by_id(cat_id)
    shelter = get_shelter_by_name(cat["shelter_name"])
    
    return inertia.render("CatProfile", {
        "cat": cat,
        "shelter": shelter,
    })

@app.get("/shelter/{shelter_name}/directions")
async def get_shelter_directions(shelter_name: str, inertia: InertiaDep):
    """
    External redirect to Google Maps for shelter directions.
    
    Returns a 409 response with X-Inertia-Location header.
    The Inertia client will automatically navigate to Google Maps.
    """
    shelter = get_shelter_by_name(shelter_name)
    
    if not shelter:
        return inertia.render("Error", {
            "message": f"Shelter '{shelter_name}' not found"
        })
    
    # URL-encode the address
    address = shelter["address"].replace(" ", "+")
    maps_url = f"https://maps.google.com/?q={address}"
    
    return inertia.location(maps_url)
```

Frontend component:

```tsx
export default function CatProfile({ cat, shelter }) {
  return (
    <div>
      <h1>{cat.name}</h1>
      
      <div className="shelter-info">
        <h2>{shelter.name}</h2>
        <p>{shelter.address}</p>
        
        {/* This link will trigger an external redirect */}
        <a href={`/shelter/${shelter.name}/directions`}>
          Get Directions
        </a>
      </div>
    </div>
  )
}
```

## How It Works

When you call `inertia.location(url)`:

1. **Server response**: Returns `409 Conflict` status with:
   - `X-Inertia-Location: <url>` header
   
2. **Client behavior**: The Inertia client:
   - Detects the `409` status
   - Reads the `X-Inertia-Location` header
   - Performs `window.location.href = url` (full page navigation)

## Internal vs External Redirects

### When to use `inertia.location()` (External)

- OAuth providers (GitHub, Google, etc.)
- Payment gateways (Stripe, PayPal, etc.)
- External mapping services
- Third-party documentation
- File downloads from external URLs
- Any URL outside your Inertia app

### When to use regular redirects (Internal)

For navigation within your Inertia app, use FastAPI's `RedirectResponse`:

```python
from fastapi.responses import RedirectResponse

@app.post("/users")
async def create_user(inertia: InertiaDep):
    # Create user...
    
    # Internal redirect (stays in SPA)
    return RedirectResponse(url=f"/users/{user.id}", status_code=303)
```

The Inertia client automatically handles internal redirects without a full page reload.

## Testing External Redirects

When testing, you can verify the redirect:

```python
from fastapi.testclient import TestClient

def test_oauth_redirect():
    client = TestClient(app)
    response = client.get(
        "/auth/github",
        headers={"X-Inertia": "true"}
    )
    
    assert response.status_code == 409
    assert "X-Inertia-Location" in response.headers
    assert "github.com" in response.headers["X-Inertia-Location"]
```

## Security Considerations

1. **Validate URLs**: Only redirect to trusted domains
2. **Use HTTPS**: Always use HTTPS for OAuth and payment redirects
3. **Verify state**: For OAuth, always verify state parameters
4. **Whitelist domains**: Consider whitelisting allowed redirect domains

```python
ALLOWED_DOMAINS = ["github.com", "accounts.google.com", "checkout.stripe.com"]

@app.get("/redirect/{url:path}")
async def safe_redirect(url: str, inertia: InertiaDep):
    from urllib.parse import urlparse
    
    parsed = urlparse(url)
    if parsed.netloc not in ALLOWED_DOMAINS:
        return inertia.render("Error", {
            "message": "Invalid redirect domain"
        })
    
    return inertia.location(url)
```

## Next Steps

- [History Encryption](/guides/history-encryption/) - Secure sensitive OAuth data
- [Validation Errors](/guides/validation-errors/) - Handle payment errors
- [Shared Data](/guides/shared-data/) - Flash messages after OAuth
