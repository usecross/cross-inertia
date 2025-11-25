

0.7.0 - 2025-11-25
------------------

Add error bags support for scoped validation errors

- Implement `X-Inertia-Error-Bag` header handling to scope validation errors under named keys
- Allow multiple forms on the same page to have independent validation errors
- Add error bags demo page with login and register forms
- Add comprehensive E2E tests for error bags functionality
- Update documentation with error bags usage examples
- Clear Vite pre-bundling cache in justfile to avoid stale exports

## Usage

When multiple forms exist on the same page, use error bags to scope validation errors:

### Frontend

```tsx
const loginForm = useForm({ email: '', password: '' })
const registerForm = useForm({ name: '', email: '', password: '' })

// Submit with error bag
loginForm.post('/login', { errorBag: 'login' })
registerForm.post('/register', { errorBag: 'register' })
```

### Backend

```python
# Errors are automatically scoped when X-Inertia-Error-Bag header is present
if errors:
    return inertia.render("Auth", {}, errors=errors)
    # Returns: { "errors": { "login": { "email": "Invalid" } } }
```
