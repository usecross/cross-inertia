---
title: Validation Errors
description: Handle form validation errors with Inertia
---

Cross-Inertia provides built-in support for form validation errors following the Inertia.js protocol. When validation fails, errors are automatically returned with a `422 Unprocessable Entity` status.

## Basic Validation

Here's a simple example of form validation:

```python
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/users/create")
async def create_user_form(inertia: InertiaDep):
    return inertia.render("Users/Create", {})

@app.post("/users")
async def create_user(inertia: InertiaDep):
    # Get form data (Inertia sends JSON)
    form_data = await inertia.request.json()
    
    # Validate the data
    errors = {}
    
    name = form_data.get("name", "")
    email = form_data.get("email", "")
    
    if not name or len(name) < 2:
        errors["name"] = "Name must be at least 2 characters"
    
    if not email or "@" not in email:
        errors["email"] = "Please enter a valid email address"
    
    # If there are errors, re-render with validation errors
    if errors:
        return inertia.render("Users/Create", {}, errors=errors)
    
    # Success - create user and redirect
    # ... save to database ...
    return inertia.render("Users/Show", {"user": new_user})
```

## How It Works

When you pass `errors` to `inertia.render()`:

1. Cross-Inertia returns a `422 Unprocessable Entity` status
2. The error bag is included in the response props
3. The Inertia client automatically handles the errors
4. Your frontend receives the errors in the component props

## Frontend Error Display

On the React side, you can access errors from props:

```tsx
import { useForm } from '@inertiajs/react'

export default function CreateUser() {
  const { data, setData, post, errors, processing } = useForm({
    name: '',
    email: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/users')
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Name</label>
        <input
          type="text"
          value={data.name}
          onChange={e => setData('name', e.target.value)}
        />
        {errors.name && <div className="error">{errors.name}</div>}
      </div>

      <div>
        <label>Email</label>
        <input
          type="email"
          value={data.email}
          onChange={e => setData('email', e.target.value)}
        />
        {errors.email && <div className="error">{errors.email}</div>}
      </div>

      <button type="submit" disabled={processing}>
        Create User
      </button>
    </form>
  )
}
```

## Using Pydantic for Validation

You can use Pydantic models for more robust validation:

```python
from pydantic import BaseModel, EmailStr, field_validator
from fastapi import FastAPI
from inertia.fastapi import InertiaDep

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    
    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

@app.post("/users")
async def create_user(inertia: InertiaDep):
    form_data = await inertia.request.json()
    
    try:
        # Validate with Pydantic
        user_data = UserCreate(**form_data)
        
        # Create user...
        return inertia.render("Users/Show", {"user": new_user})
        
    except ValidationError as e:
        # Convert Pydantic errors to Inertia format
        errors = {}
        for error in e.errors():
            field = error['loc'][0]
            errors[field] = error['msg']
        
        return inertia.render("Users/Create", {}, errors=errors)
```

## Complex Validation Example

Here's a real-world example from an adoption application form:

```python
@app.post("/cats/{cat_id}/apply")
async def submit_application(cat_id: int, inertia: InertiaDep):
    form_data = await inertia.request.json()
    
    errors = {}
    
    # Extract form fields
    full_name = str(form_data.get("full_name", ""))
    email = str(form_data.get("email", ""))
    phone = str(form_data.get("phone", ""))
    address = str(form_data.get("address", ""))
    why_adopt = str(form_data.get("why_adopt", ""))
    
    # Validate each field
    if not full_name or len(full_name) < 2:
        errors["full_name"] = "Full name is required (minimum 2 characters)"
    
    if not email or "@" not in email:
        errors["email"] = "A valid email address is required"
    
    if not phone or len(phone) < 10:
        errors["phone"] = "A valid phone number is required"
    
    if not address or len(address) < 10:
        errors["address"] = "A complete address is required"
    
    if not why_adopt or len(why_adopt) < 50:
        errors["why_adopt"] = "Please tell us more (minimum 50 characters)"
    
    # Return errors if validation failed
    if errors:
        cat = get_cat_by_id(cat_id)
        return inertia.render(
            "ApplicationForm",
            {
                "title": f"Apply to Adopt {cat['name']}",
                "cat": cat,
            },
            errors=errors
        )
    
    # Success - process the application
    save_application(form_data)
    
    # Flash success message
    flash(inertia.request, "Application submitted successfully!", "success")
    
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=f"/cats/{cat_id}", status_code=303)
```

## Multiple Error Messages

You can provide multiple error messages per field:

```python
errors = {
    "email": "Please enter a valid email address",
    "password": "Password must be at least 8 characters and contain a number",
}
```

## Nested Field Validation

For nested objects, use dot notation:

```python
errors = {
    "user.name": "Name is required",
    "user.email": "Email is invalid",
    "address.street": "Street address is required",
}
```

Access in frontend:

```tsx
{errors['user.name'] && <div>{errors['user.name']}</div>}
```

## Validation Without Re-rendering

If you want to return validation errors without re-rendering the page (e.g., for AJAX validation):

```python
from fastapi.responses import JSONResponse

@app.post("/validate/email")
async def validate_email(inertia: InertiaDep):
    form_data = await inertia.request.json()
    email = form_data.get("email", "")
    
    if not email or "@" not in email:
        return JSONResponse(
            {"errors": {"email": "Invalid email"}},
            status_code=422
        )
    
    return JSONResponse({"valid": True})
```

## Error Bags (Coming Soon)

Error bags allow you to namespace validation errors for multiple forms on the same page. This feature is planned for a future release.

```python
# Planned API (not yet implemented)
return inertia.render(
    "Users/Edit",
    {},
    errors={"name": "Required"},
    error_bag="createUser"  # Not yet supported
)
```

## Best Practices

1. **Always validate server-side**: Never trust client-side validation alone
2. **Provide clear messages**: Tell users exactly what went wrong and how to fix it
3. **Validate early**: Return errors as soon as validation fails
4. **Preserve form data**: When re-rendering with errors, include the submitted data so users don't have to re-enter everything
5. **Use proper status codes**: Cross-Inertia automatically uses `422` for validation errors

## Next Steps

- [Shared Data](/guides/shared-data/) - Add flash messages for success notifications
- [Partial Reloads](/guides/partial-reloads/) - Optimize form submissions
- [Quick Start](/getting-started/quick-start/) - Build a complete form example
