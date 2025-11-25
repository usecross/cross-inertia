---
title: Form Handling
description: Handle forms with Inertia.js and Cross-Inertia
---

Inertia provides powerful form handling through its `useForm` hook and `<Form>` component. This guide covers form submissions, file uploads, progress tracking, and multi-step forms.

## Basic Form Submission

### Backend Endpoint

Create a POST endpoint that handles form data:

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from inertia.fastapi import InertiaDep

app = FastAPI()

@app.get("/contacts/create")
async def create_contact_form(inertia: InertiaDep):
    """Show the contact form."""
    return inertia.render("Contacts/Create", {})

@app.post("/contacts")
async def create_contact(inertia: InertiaDep):
    """Handle form submission."""
    form_data = await inertia.request.json()

    # Validate
    errors = {}
    name = form_data.get("name", "")
    email = form_data.get("email", "")
    message = form_data.get("message", "")

    if not name or len(name) < 2:
        errors["name"] = "Name is required"
    if not email or "@" not in email:
        errors["email"] = "Valid email is required"
    if not message or len(message) < 10:
        errors["message"] = "Message must be at least 10 characters"

    if errors:
        return inertia.render("Contacts/Create", {}, errors=errors)

    # Save contact...
    save_contact(name, email, message)

    # Redirect on success
    return RedirectResponse(url="/contacts", status_code=303)
```

### Frontend with useForm

The `useForm` hook provides form state management and submission:

```tsx
import { useForm } from '@inertiajs/react'

export default function CreateContact() {
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    email: '',
    message: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/contacts')
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          type="text"
          value={data.name}
          onChange={e => setData('name', e.target.value)}
        />
        {errors.name && <p className="error">{errors.name}</p>}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={data.email}
          onChange={e => setData('email', e.target.value)}
        />
        {errors.email && <p className="error">{errors.email}</p>}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          value={data.message}
          onChange={e => setData('message', e.target.value)}
        />
        {errors.message && <p className="error">{errors.message}</p>}
      </div>

      <button type="submit" disabled={processing}>
        {processing ? 'Sending...' : 'Send Message'}
      </button>
    </form>
  )
}
```

### Frontend with Form Component

Alternatively, use the `<Form>` component for a more declarative approach:

```tsx
import { Form } from '@inertiajs/react'

export default function CreateContact() {
  return (
    <Form action="/contacts" method="post">
      {({ data, setData, processing, errors }) => (
        <>
          <div>
            <label htmlFor="name">Name</label>
            <input
              id="name"
              type="text"
              value={data.name}
              onChange={e => setData('name', e.target.value)}
            />
            {errors.name && <p className="error">{errors.name}</p>}
          </div>

          {/* ... more fields */}

          <button type="submit" disabled={processing}>
            Send
          </button>
        </>
      )}
    </Form>
  )
}
```

## Form State Properties

The `useForm` hook provides several reactive properties:

| Property | Description |
|----------|-------------|
| `data` | Current form field values |
| `errors` | Validation errors from the server |
| `processing` | `true` while the form is submitting |
| `isDirty` | `true` if data differs from defaults |
| `wasSuccessful` | `true` if the last submission succeeded |
| `recentlySuccessful` | `true` for 2 seconds after success |
| `progress` | Upload progress for file uploads |

## Form Methods

### Submission Methods

```tsx
const { get, post, put, patch, delete: destroy } = useForm({ ... })

// Submit methods
post('/contacts')                    // POST request
put('/contacts/1')                   // PUT request
patch('/contacts/1')                 // PATCH request
destroy('/contacts/1')               // DELETE request
```

### State Management

```tsx
const { reset, clearErrors, setError, transform } = useForm({ ... })

// Reset form to defaults
reset()                              // Reset all fields
reset('name', 'email')               // Reset specific fields

// Clear errors
clearErrors()                        // Clear all errors
clearErrors('name')                  // Clear specific error

// Set errors manually
setError('email', 'This email is taken')

// Transform data before submission
transform(data => ({
  ...data,
  name: data.name.trim(),
}))
```

## File Uploads

Inertia automatically handles file uploads by converting the request to `FormData`.

### Backend

Use FastAPI's `Form` and `UploadFile` for file handling:

```python
from fastapi import Form, UploadFile, File
from fastapi.responses import RedirectResponse
from inertia.fastapi import InertiaDep
import shutil
from pathlib import Path

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/documents/upload")
async def upload_form(inertia: InertiaDep):
    return inertia.render("Documents/Upload", {})

@app.post("/documents")
async def upload_document(
    inertia: InertiaDep,
    title: str = Form(...),
    file: UploadFile = File(...),
):
    errors = {}

    if not title or len(title) < 3:
        errors["title"] = "Title must be at least 3 characters"

    if not file.filename:
        errors["file"] = "Please select a file"
    elif file.size > 10 * 1024 * 1024:  # 10MB limit
        errors["file"] = "File must be less than 10MB"

    if errors:
        return inertia.render("Documents/Upload", {}, errors=errors)

    # Save the file
    file_path = UPLOAD_DIR / file.filename
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save document record...

    return RedirectResponse(url="/documents", status_code=303)
```

### Frontend with Progress Tracking

```tsx
import { useForm } from '@inertiajs/react'

export default function UploadDocument() {
  const { data, setData, post, processing, progress, errors } = useForm({
    title: '',
    file: null as File | null,
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/documents', {
      forceFormData: true,  // Force multipart even without files
    })
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label htmlFor="title">Title</label>
        <input
          id="title"
          type="text"
          value={data.title}
          onChange={e => setData('title', e.target.value)}
        />
        {errors.title && <p className="error">{errors.title}</p>}
      </div>

      <div>
        <label htmlFor="file">File</label>
        <input
          id="file"
          type="file"
          onChange={e => setData('file', e.target.files?.[0] || null)}
        />
        {errors.file && <p className="error">{errors.file}</p>}
      </div>

      {/* Progress bar */}
      {progress && (
        <div className="progress-bar">
          <div
            className="progress-fill"
            style={{ width: `${progress.percentage}%` }}
          />
          <span>{progress.percentage}%</span>
        </div>
      )}

      <button type="submit" disabled={processing}>
        {processing ? 'Uploading...' : 'Upload'}
      </button>
    </form>
  )
}
```

### Method Spoofing for PUT/PATCH

Some servers don't support file uploads with PUT/PATCH. Use method spoofing:

```tsx
const { post } = useForm({ ... })

// Spoof PUT request
post('/documents/1', {
  _method: 'put',  // Server interprets as PUT
})
```

On the backend, check for `_method` in form data:

```python
@app.post("/documents/{document_id}")
async def update_document(
    document_id: int,
    inertia: InertiaDep,
    title: str = Form(...),
    file: UploadFile = File(None),
    _method: str = Form(None),
):
    # _method will be "put" if spoofed
    # Handle as update...
    pass
```

## Multi-Step Forms (Wizards)

For complex forms, break them into steps while preserving data.

### Backend

```python
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from inertia.fastapi import InertiaDep

@app.get("/signup")
async def signup_step1(inertia: InertiaDep):
    return inertia.render("Signup/Step1", {"step": 1, "total_steps": 3})

@app.post("/signup/step1")
async def process_step1(inertia: InertiaDep):
    form_data = await inertia.request.json()

    errors = {}
    if not form_data.get("email"):
        errors["email"] = "Email is required"
    if not form_data.get("password"):
        errors["password"] = "Password is required"

    if errors:
        return inertia.render("Signup/Step1", {"step": 1}, errors=errors)

    # Store in session for later steps
    inertia.request.session["signup"] = form_data

    return RedirectResponse(url="/signup/step2", status_code=303)

@app.get("/signup/step2")
async def signup_step2(inertia: InertiaDep):
    # Get data from previous step
    signup_data = inertia.request.session.get("signup", {})

    return inertia.render("Signup/Step2", {
        "step": 2,
        "total_steps": 3,
        "email": signup_data.get("email"),
    })

@app.post("/signup/step2")
async def process_step2(inertia: InertiaDep):
    form_data = await inertia.request.json()

    errors = {}
    if not form_data.get("name"):
        errors["name"] = "Name is required"

    if errors:
        return inertia.render("Signup/Step2", {"step": 2}, errors=errors)

    # Merge with session data
    signup_data = inertia.request.session.get("signup", {})
    signup_data.update(form_data)
    inertia.request.session["signup"] = signup_data

    return RedirectResponse(url="/signup/step3", status_code=303)

@app.post("/signup/complete")
async def complete_signup(inertia: InertiaDep):
    # Get all data and create user
    signup_data = inertia.request.session.pop("signup", {})

    # Create user with all collected data
    user = create_user(**signup_data)

    flash(inertia.request, "Account created successfully!")
    return RedirectResponse(url="/dashboard", status_code=303)
```

### Frontend Wizard Component

```tsx
import { useForm } from '@inertiajs/react'
import { usePage } from '@inertiajs/react'

// Step 1: Account Details
export function Step1() {
  const { data, setData, post, processing, errors } = useForm({
    email: '',
    password: '',
    password_confirmation: '',
  })

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    post('/signup/step1')
  }

  return (
    <form onSubmit={handleSubmit}>
      <h2>Step 1: Account Details</h2>

      <div>
        <label>Email</label>
        <input
          type="email"
          value={data.email}
          onChange={e => setData('email', e.target.value)}
        />
        {errors.email && <p className="error">{errors.email}</p>}
      </div>

      <div>
        <label>Password</label>
        <input
          type="password"
          value={data.password}
          onChange={e => setData('password', e.target.value)}
        />
        {errors.password && <p className="error">{errors.password}</p>}
      </div>

      <button type="submit" disabled={processing}>
        Next Step
      </button>
    </form>
  )
}

// Step 2: Profile Info
export function Step2() {
  const { email } = usePage().props
  const { data, setData, post, processing, errors } = useForm({
    name: '',
    bio: '',
  })

  return (
    <form onSubmit={e => { e.preventDefault(); post('/signup/step2') }}>
      <h2>Step 2: Profile Info</h2>
      <p>Setting up profile for {email}</p>

      <div>
        <label>Name</label>
        <input
          type="text"
          value={data.name}
          onChange={e => setData('name', e.target.value)}
        />
        {errors.name && <p className="error">{errors.name}</p>}
      </div>

      <div>
        <label>Bio</label>
        <textarea
          value={data.bio}
          onChange={e => setData('bio', e.target.value)}
        />
      </div>

      <button type="submit" disabled={processing}>
        Next Step
      </button>
    </form>
  )
}
```

### Progress Indicator

```tsx
interface ProgressProps {
  step: number
  totalSteps: number
}

export function StepProgress({ step, totalSteps }: ProgressProps) {
  return (
    <div className="step-progress">
      {Array.from({ length: totalSteps }, (_, i) => (
        <div
          key={i}
          className={`step ${i + 1 <= step ? 'completed' : ''} ${i + 1 === step ? 'current' : ''}`}
        >
          {i + 1}
        </div>
      ))}
    </div>
  )
}
```

## Preserving Form Data

### Reset on Success

By default, `useForm` doesn't reset after successful submission. Configure this behavior:

```tsx
const form = useForm({ name: '', email: '' })

// Reset all fields on success
form.post('/contacts', {
  resetOnSuccess: true,
})

// Reset specific fields on success
form.post('/contacts', {
  resetOnSuccess: ['email'],  // Only reset email
})
```

### Preserve Scroll Position

Prevent scrolling to top after submission:

```tsx
form.post('/contacts', {
  preserveScroll: true,
})
```

## Form Callbacks

Handle form lifecycle events:

```tsx
const { post } = useForm({ ... })

post('/contacts', {
  onBefore: () => {
    // Called before the request
    return confirm('Are you sure?')  // Return false to cancel
  },
  onStart: () => {
    // Request started
  },
  onProgress: (progress) => {
    // Upload progress (for file uploads)
    console.log(`${progress.percentage}% uploaded`)
  },
  onSuccess: (page) => {
    // Request succeeded
    toast.success('Contact created!')
  },
  onError: (errors) => {
    // Validation errors received
    toast.error('Please fix the errors')
  },
  onFinish: () => {
    // Request completed (success or error)
  },
})
```

## Best Practices

1. **Always validate server-side**: Never trust client-side validation alone
2. **Show loading states**: Use `processing` to disable buttons and show feedback
3. **Display errors inline**: Show errors next to the relevant field
4. **Preserve data on error**: Keep submitted values so users don't re-enter everything
5. **Use proper HTTP methods**: POST for create, PUT/PATCH for update, DELETE for remove
6. **Handle file size limits**: Validate file sizes both client and server-side
7. **Provide progress feedback**: Show upload progress for better UX

## Common Patterns

### Inline Editing

```tsx
import { useForm } from '@inertiajs/react'
import { useState } from 'react'

export function EditableField({ field, value, url }) {
  const [editing, setEditing] = useState(false)
  const { data, setData, patch, processing } = useForm({ [field]: value })

  const save = () => {
    patch(url, {
      onSuccess: () => setEditing(false),
    })
  }

  if (!editing) {
    return (
      <span onClick={() => setEditing(true)} className="editable">
        {value}
      </span>
    )
  }

  return (
    <input
      value={data[field]}
      onChange={e => setData(field, e.target.value)}
      onBlur={save}
      onKeyDown={e => e.key === 'Enter' && save()}
      disabled={processing}
      autoFocus
    />
  )
}
```

### Confirmation Before Submit

```tsx
const { delete: destroy } = useForm({})

const handleDelete = () => {
  destroy(`/contacts/${id}`, {
    onBefore: () => confirm('Delete this contact?'),
  })
}
```

### Auto-save Draft

```tsx
import { useForm } from '@inertiajs/react'
import { useEffect, useRef } from 'react'
import { useDebouncedCallback } from 'use-debounce'

export function AutoSaveForm({ draft }) {
  const { data, setData, patch, isDirty } = useForm({
    title: draft.title,
    content: draft.content,
  })

  const debouncedSave = useDebouncedCallback(() => {
    if (isDirty) {
      patch(`/drafts/${draft.id}`, { preserveScroll: true })
    }
  }, 1000)

  useEffect(() => {
    debouncedSave()
  }, [data])

  return (
    <form>
      <input
        value={data.title}
        onChange={e => setData('title', e.target.value)}
      />
      <textarea
        value={data.content}
        onChange={e => setData('content', e.target.value)}
      />
      {isDirty && <span>Unsaved changes</span>}
    </form>
  )
}
```

## Next Steps

- [Validation Errors](/guides/validation-errors/) - Handle validation in detail
- [Shared Data](/guides/shared-data/) - Flash messages after form submission
- [Partial Reloads](/guides/partial-reloads/) - Optimize form responses
